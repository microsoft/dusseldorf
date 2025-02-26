# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is the DNS rule engine for the dataplane.

import json
from zentralbibliothek.ruleengine import RuleEngine, Result, Predicate

from models.dnsrequest import DnsRequest
from models.dnsresponse import DnsResponse

#region predicates
class DnsRequestTypePredicate(Predicate):
    """
    Check if the DNS request type of the request is one of the expected ones in the parameter. 
    Parameter should be a comma-delimited list of DNS request types.
    """
    @classmethod
    def satisfied_by(cls, request:DnsRequest, parameter:str):
        if not parameter: # If we're not requiring anything, then we should let all requests satisfy the predicate.
            return True
        reqtypes = parameter.split(',')
        return request.RequestType.lower() in [rt.lower() for rt in reqtypes]
#endregion

#region results
class SetDnsResponseDataResult(Result):
    """
    Sets the response data of the DNS response.    
    Parameter: a json blob of the data you wish to respond with.
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:DnsResponse = result_data['response']
        response._rdata = json.loads(parameter)
        result_data['response'] = response
        return result_data

class SetDnsResponseAnswerTypeResult(Result):    
    """
    Sets the Answer Type (SOA, CNAME, etc) of the DNS response
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:DnsResponse = result_data['response']
        response._rtype = parameter
        result_data['response'] = response
        return result_data

class SetDnsResponseTTLResult(Result):
    """
    Sets the TTL of the DNS response
    """
    @classmethod
    def execute(cls, result_data:dict, parameter:str):
        response:DnsResponse = result_data['response']
        response._ttl = int(parameter)
        result_data['response'] = response
        return result_data
#endregion
    
# this method is called from the handler.  It maps the
# "keys" in the DB to the classes defined above.
def get_response(request: DnsRequest) -> DnsResponse:
    predicate_mappings:dict = {
        'dns.type': DnsRequestTypePredicate
    }
    result_mappings:dict = {
        'dns.data': SetDnsResponseDataResult,
        'dns.ttl':  SetDnsResponseTTLResult, 
        'dns.type': SetDnsResponseAnswerTypeResult, 
    }

    return RuleEngine.get_response_from_request(
            request,
            predicate_mappings,
            result_mappings
    )