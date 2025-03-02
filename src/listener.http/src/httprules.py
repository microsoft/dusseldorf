# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import ipaddress
import json
import logging
import random
import re
import socket
import uuid
import requests

from urllib.parse import ParseResult, urlparse
from zentralbibliothek.ruleengine import RuleEngine, Predicate, Result
from models.httprequest import HttpRequest
from models.httpresponse import HttpResponse
from zentralbibliothek.utils import Utils

logger = logging.getLogger("listener.http")

def _is_dangerous_host(cls, url:str) -> bool:
    """
    Helper function that returns if a URL is dangerous.
    """
    # need to convince @liks and @sukrkash to port 
    # antissrf to python3 :) 
    bad_networks = [
        ipaddress.IPv4Network("127.0.0.0/8"),       # loopback (news letter!)
        ipaddress.IPv4Network("10.0.0.0/8"),        # rfc 1928
        ipaddress.IPv4Network("192.168.0.0/16"),    # rfc 1918
        ipaddress.IPv4Network("172.16.0.0/12"),     # rfc 1918
        ipaddress.IPv4Network("169.254.0.0/16"),    # rfc 3927
        ipaddress.IPv4Network("168.63.129.16/32"),  # Azure Gateway
        ipaddress.IPv6Network("::1/128"),           # IPv6 loopback
        ipaddress.IPv6Network("fc00::/7"),          # site-local
        ipaddress.IPv6Network("fe80::/10"),         # link-local
    ]

    try:
        # Resolve all IP addresses 
        ip_addresses = socket.getaddrinfo(url, None)

        for ip_info in ip_addresses:
            ip = ipaddress.ip_address(ip_info[4][0])
            if any(ip in network for network in bad_networks):
                return True
            
        return false
    except:
        logger.error(f"Could not resolve host: {url}: {str(ex)}") 
        return True # default, assume it's bad

#region predicates

class HttpTlsPredicate(Predicate):
    """
    Check if the HTTP protocol had TLS enabled
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        # If we're not requiring anything, then we should let all requests satisfy the predicate.
        if not parameter: return True
        return request.tls

class HttpMethodPredicate(Predicate):
    """
    Check if the HTTP method of the request is one of the expected ones in the parameter. 
    Parameter should be a comma-delimited list of HTTP methods.
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        # If we're not requiring anything, then we should let all requests satisfy the predicate.
        if not parameter:  return True
        methods = parameter.split(',')
        return request.method.lower() in [m.lower() for m in methods]

class HttpPathPredicate(Predicate):
    """
    Check if the path of the request matches the provided regular expression.
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True
        
        if type(request) != HttpRequest: 
            return False
        return bool(re.search(parameter, request.path))
    
class HttpBodyPredicate(Predicate):
    """
    Check if the body of the request matches the provided regular expression.
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):    
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True
        
        if type(request) != HttpRequest: 
            return False
        return bool(re.search(parameter, request.body))

class HttpHeaderPredicate(Predicate):
    """
    Check if the provided (case insensitive) HTTP header is present.
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        
        # If we're not requiring anything, then we should let all requests satisfy the predicate.
        if not parameter: return True

        # We're going to do a case-insensitive comparison here, 
        # so we'll just convert everything to lowercase.
        return parameter.lower() in [k.lower() for k in request.headers.keys()]

class HttpHeaderKeysPredicate(Predicate):
    """
    Check if ALL of the provided keys are present in the headers of the request.
    Parameter: comma-delimited list of header keys. 
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True

        required_keys = [k.lower() for k in parameter.split(',') if k != '']
        actual_keys = [k.lower() for k in request.headers.keys() if k != '']

        if len(required_keys) > len(actual_keys):
            return False
        
        return all(rk in actual_keys for rk in required_keys)

class HttpHeaderValuesPredicate(Predicate):
    """
    Check if ALL of the provided key/value pairs are present in the headers of the request.
    Parameter: JSON blob. 
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True
        
        required_hdrs = json.loads(parameter)
        for rk,rv in required_hdrs.items():
            if rk not in request.headers.keys():
                return False
            if request.headers[rk] != rv:
                return False
        return True

class HttpHeaderValueRegexesPredicate(Predicate):
    """
    For each `key/value` pair in the parameter, check if `request.headers[key]` matches the `value` regex.
    Parameter: JSON blob. 
    """
    @classmethod
    def satisfied_by(cls, request:HttpRequest, parameter:str):
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True
        required_hdrs = json.loads(parameter)
        for rk,rv_regex in required_hdrs.items():
            if rk not in request.headers.keys():
                return False
            if not bool(re.search(rv_regex, request.headers[rk])):
                return False
        return True

#endregion

#region results
class SetHttpResponseCodeResult(Result):
    """
    Sets the status code of the HTTP response.
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:HttpResponse = result_data['response']
        response.status_code = int(parameter)
        result_data['response'] = response
        return result_data

class SetHttpResponseBodyResult(Result):
    """
    Sets the body of the HTTP response.
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:HttpResponse = result_data['response']
        response.body = parameter
        result_data['response'] = response
        return result_data

class SetHttpResponseSingleHeaderResult(Result):
    """
    Sets a single header of the HTTP response
    Parameter: a single string for the desired header in the format "name:value"
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:HttpResponse = result_data['response']
        # split parameter first instance of ":", set that as header name, rest as value
        (header_name, header_value) = parameter.split(":", 1)
        header_value = header_value.strip()
        # TODO replace variables in header value
        response.headers[header_name] = header_value
        result_data['response'] = response
        return result_data

class SetHttpResponseMultipleHeadersResult(Result):
    """
    Sets the headers of the HTTP response
    Parameter: a JSON blob of the desired headers.
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:HttpResponse = result_data['response']
        response.headers = json.loads(parameter)
        result_data['response'] = response
        return result_data
    
class SetVariableResult(Result):
    """
    Sets a variable in all str values in result_data dict. 
    Parameter: a string in the format "replace_from:replace_with"
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        current_zone = result_data['zone']
        (rename_from, replace_with) = parameter.split(":", 1)

        if rename_from.strip() == "": # fail quickly
            return result_data

        if replace_with == "uuid()":
            replace_with = str(uuid.uuid4())
        elif replace_with == "zone()":
            replace_with = current_zone
        elif replace_with == "newzone()":
            # make a new zone in the DB, and set replace_with to that
            # currently just let it make a random zone (empty prefix)
            # TODO: maybe lazy load this for perf?
            try:
                logger.info(f"making newzone() for {current_zone}")
                # pgclient = PostgresClient.get_instance()
                # new_prefix:str = "" 
                # new_zone:str = DbClient2.create_zone(
                    # zone_prefix=new_prefix, 
                    # parent_zone=current_zone
                # )
                # replace_with = new_zone
            except:
                # log that we failed to make a new zone
                logger.error(f"Failed on newzone() for: {current_zone}")
                replace_with = ""

        if isinstance(result_data['response'], HttpResponse):
            # in HTTP, change everything in the body and header values
            result_data['response'].body = result_data['response'].body.replace(rename_from, replace_with)
            for key in result_data['response'].headers:
                if rename_from in result_data['response'].headers[key]:
                    result_data['response'].headers[key] = result_data['response'].headers[key].replace(rename_from, replace_with)

        return result_data

class GetHTTPPassthruResult(Result):
    """
    Sends the payloads to an external server and returns the response.
    Parameter: a URL as a string
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        # parse parameter as a URL
        target:ParseResult = urlparse(parameter) 

        # check for valid URL's
        if _is_dangerous_host(target.netloc) == True:
            logger.error(f"Dangerous URL for http.passthru: {parameter}")
            return result_data

        if target.scheme not in ["http", "https"]:
            target.scheme = "http"

        current_zone = result_data['zone']

        # request made out of original request
        orig_req:HttpRequest = result_data['request'] 

        # make new haeders 
        headers = {}
        for key in orig_req.headers:
            # TODO: 
            # - skip dangerous header names?
            # - add xff for ssrf protection?
            # - replace variables in headers?
            # - add x-dssldrf header with orig zone?
            headers[key] = orig_req.headers[key]
        
        # override host header
        headers['host'] = target.netloc

        method:str = orig_req.method.upper()

        url = f"{target.scheme}://{target.netloc}"
        
        if orig_req.path: url += orig_req.path

        try:
            logger.info(f"http.passthru for {target.netloc}{orig_req.path}")
            resp:requests.Response = requests.request(
                method, 
                url, 
                headers = headers, 
                data = orig_req.body, 
                allow_redirects = False,
                verify = True,     # configurable?
                timeout = 2000      # configurable?
            )

            logger.info(f"http.passthru for {target.netloc}{orig_req.path} gave {resp.status_code} ({len(resp.text)} bytes)")

            # set response data
            result_data['response'].status_code = resp.status_code
            result_data['response'].headers = dict(resp.headers)
            result_data['response'].body = resp.text or None
        except Exception as ex:
            logger.error(f"Invalid response from for http.passthru: {orig_req.method}")
            logger.exception(ex)
        return result_data

class GetHTTPPassthru2Result(Result):
    """
    Rewrites a request and sends to an external server and then replaces
    all from_this_* to a to_this_* snippet in the the response's
    headers and body.

    Parameter: JSON blob with following:
        {
            url: "https://forward.to.this.host", // a URL as a string
            skip_tls_check: false,               // setting to true is INSECURE!
            timeout_in_ms: 2000,                 // time out in milliseconds,
            skip_xff: false,                     // skip populating a XFF header
            subs: {
                "from_this_1": "to_this_1",
                "from_this_2": "to_this_2",
                ...
                "from_this_N": "to_this_N"
            }
        }
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:dict):
        MAX_TIMEOUT:int     = 10000
        DEFAULT_TIMEOUT:int = 2000

        # extract values
        url:str = parameter['url']
        subs:dict = parameter.get('subs', {})
        tls_verify:bool = not parameter.get('skip_tls_check', False) # negate the parameter
        timeout:int = parameter.get("timeout_in_ms", DEFAULT_TIMEOUT)
        skip_xff:bool = parameter.get("skip_xff", False)

        if timeout > MAX_TIMEOUT: 
            timeout = DEFAULT_TIMEOUT

        target:ParseResult = urlparse(url) 

        # check for valid URL's
        if _is_dangerous_host(target.netloc) == True:
            logger.error(f"Dangerous URL for http.passthru2: {parameter}")
            return result_data

        if target.scheme not in ["http", "https"]:
            target.scheme = "http"

        # request made out of original request
        orig_req:HttpRequest = result_data['request'] 

        # make new haeders and body
        headers = orig_req.headers
        http_body:str = orig_req.body

        # rewrite all values according to the sub dict
        for change_from,change_to in subs.items():
            # go through all headers' values
            for hdr in headers:
                if change_from in headers[hdr]:
                    headers[hdr] = headers[hdr].replace(change_from, change_to)
                    logger.debug(f"http.passthru2: replaced {change_from} in http header: {hdr}")

            # replace in body too
            if change_from in http_body:
                http_body = http_body.replace(change_from, change_to)
                logger.debug(f"http.passthru2: replaced {change_from} in http body")

        # by default, we add a XFF header if there's none
        _xff:str = "X-Forwarded-For"
        if skip_xff is False and _xff not in headers.keys():
            headers[_xff] = orig_req.remote_addr

        # override host header
        headers['host'] = target.netloc

        method:str = orig_req.method.upper()

        url = f"{target.scheme}://{target.netloc}"
        
        if orig_req.path: 
            url += orig_req.path

        try:
            logger.info(f"http.passthru2 for {target.netloc}{orig_req.path}")
            resp:requests.Response = requests.request(
                method, 
                url, 
                headers = headers, 
                data = orig_req.body, 
                allow_redirects = False,
                verify = tls_verify, 
                timeout = timeout
            )

            logger.info(f"http.passthru2 for {target.netloc}{orig_req.path} gave {resp.status_code} ({len(resp.text)} bytes)")

            # set response data
            result_data['response'].status_code = resp.status_code
            result_data['response'].headers = dict(resp.headers)
            result_data['response'].body = resp.text or None
        except Exception as ex:
            logger.error(f"Invalid response from for http.passthru: {orig_req.method}")
            logger.exception(ex)
        return result_data

    
class WeightedRandomSelectionResultWrapper(Result):
    """
    A result wrapper that randomly chooses from a probability distribution of results.
    Each result has an weighted probability that it will be chosen.
    If all weights are equal, this is just a purely random selection. 
   
    Parameter: A JSON blob following this example:
    {
        "results": [
            {
                "type": "http.code",
                "parameter": "200"
            },
            {
                "type": "http.code",
                "parameter": "500"
            }
        ],
        "weights": [0.9, 0.1]
    }
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        rule_id = Utils.dig(result_data, [ 'metadata', 'rule_id']) 
        component_id = Utils.dig(result_data, ['metadata', 'component_id']) 
        
        # This should never happen because the ruleengine provides both IDs. Better safe than sorry, though.
        if not rule_id or not component_id:
            return result_data

        # TODO: if they are not guids, fail? 

        parameter = json.loads(parameter)

        # TODO: make weights optional and default to [ 1, 1, 1 ... ] for N elements.

        if ('results' not in parameter.keys()) or ('weights' not in parameter.keys()):
            return result_data
        
        if len(parameter['results']) != len(parameter['weights']):
            return result_data
        
        if len(parameter['results']) == 0:
            return result_data
        
        if not all([0 <= x <= 1 for x in parameter['weights']]):
            return result_data
        
        sampled_result = random.choices(parameter['results'], weights=parameter['weights'], k=1)[0]

        result_type = [] # RESULT_CLASS_MAPPINGS.get(sampled_result.get('type', None), None)
        result_parameter = sampled_result.get('parameter', None)

        if result_type is not None and result_parameter is not None:
            result_data = result_type.execute(result_data, result_parameter)
        return result_data
#endregion

def get_response(request:HttpRequest) -> HttpResponse:
    """Gets a HTTP response from the RuleEngine"""

    predicate_mappings:dict = {
        'http.tls': HttpTlsPredicate,
        'http.method': HttpMethodPredicate,
        'http.path': HttpPathPredicate,
        'http.body': HttpBodyPredicate,
        'http.header': HttpHeaderPredicate,
        'http.headers.keys': HttpHeaderKeysPredicate,
        'http.headers.values': HttpHeaderValuesPredicate,
        'http.headers.regexes': HttpHeaderValueRegexesPredicate,
    }

    result_mappings = {
        'http.code': SetHttpResponseCodeResult,
        'http.body': SetHttpResponseBodyResult,
        'http.header': SetHttpResponseSingleHeaderResult,
        'http.headers': SetHttpResponseMultipleHeadersResult,
        'http.passthru': GetHTTPPassthruResult,
        'http.passthru2': GetHTTPPassthru2Result, # -preview
        'var': SetVariableResult,
        'random': WeightedRandomSelectionResultWrapper,
    }

    logger.debug(f"get_respomse({request.method} {request.path})")

    return RuleEngine.get_response_from_request(
        request, 
        predicate_mappings, 
        result_mappings
    )
