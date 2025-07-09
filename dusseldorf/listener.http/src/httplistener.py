# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import http.server
import base64
import logging
import sys
import ssl
import time
import re

from httprules import get_response
from models.httprequest import HttpRequest
from models.httpresponse import HttpResponse
from zentralbibliothek.utils import Utils
from zentralbibliothek.dbclient3 import DatabaseClient

from cachetools.func import ttl_cache

_timeout = 5
sessionsCache = []

logger = logging.getLogger("listener.http")

class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    This object handles a given Http request and defines the response.
    """
    MAX_CONTENT_LENGTH = 1024 * 1024 * 10 # 10MB
    ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
    PATH_PATTERN = re.compile(r"^/") # re.compile(r"^/([a-zA-Z0-9-_]+)(/([a-zA-Z0-9-_]+))?(/([a-zA-Z0-9-_]+))?/?$")

    def validate_request(self):
        """
        Validates the request, returns True if valid, False if not.
        """
        if self.command not in self.ALLOWED_METHODS:
            logger.warning("Invalid method %s", self.command)
            return False, 405

        # Validate path
        if not self.PATH_PATTERN.match(self.path):
            logger.warning("Invalid path %s", self.path)
            return False, 400

        # Validate content length
        content_length = int(self.headers.get("content-length", 0))
        if content_length > self.MAX_CONTENT_LENGTH:
            logger.warning("Content length %d exceeds maximum %d", content_length, self.MAX_CONTENT_LENGTH)
            return False, 413

        return True, None

    def setup(self):
        http.server.SimpleHTTPRequestHandler.setup(self)
        self.server_version= "dusseldorf"
        self.sys_version = "v1"
        self.request.settimeout(_timeout)

    #region HTTP Methods
    def do_HEAD(self):
        """Handles an HEAD request"""
        return self.handle_request()
    def do_OPTIONS(self):
        """Handles an OPTIONS request, usually cors preflights"""
        return self.handle_request()
    def do_GET(self):
        """Handles a GET request"""
        return self.handle_request()
    def do_PATCH(self):
        """Handles a PATCH request"""
        return self.handle_request()
    def do_POST(self):
        """Handles a POST request"""
        return self.handle_request()
    def do_PUT(self):
        """Handles a PUT request"""
        return self.handle_request()
    def do_DELETE(self):
        """Handles a DELETE request"""
        return self.handle_request()
    #endregion

    def log_message(self, fmt, *args):
        """intercept built in logger and suppress it, it's quite noisy."""
        return


    @ttl_cache(maxsize=1024, ttl=300)
    def is_valid_domain(self, domains:str, fqdn:str) -> bool:
        for domain in domains.split(","):
            if Utils.fqdn_is_valid(fqdn=fqdn, domain=domain):
                return True 
        return False


    def handle_request(self):        
        """
        This looks up if we have a matching rule for the current
        request. And if we do, then let's see what to send back.
        """
        is_valid, status_code = self.validate_request()
        if not is_valid:
            self.send_error(status_code)
            return

        start_of_req = time.perf_counter()
        logger.debug("handling_request(%s %s)", self.command, self.path)       
      
        req_fqdn = self.headers.get("host", "")

        db_client = DatabaseClient.get_instance()

        done_get_db = time.perf_counter()

        domains = ",".join(db_client.get_domains())
        if not self.is_valid_domain(fqdn=req_fqdn, domains=domains):
            self.sendHttpResponse(HttpResponse.Empty())
            return
        
        done_dom_check = time.perf_counter()

        # Check if the zone exists
        zone_fqdn = db_client.find_zone_for_request(req_fqdn)
        if not zone_fqdn:
            logger.info("zone not found for request %s", req_fqdn)
            self.sendHttpResponse(HttpResponse.Empty())
            return
       
        done_zone_check = time.perf_counter()

        req_body_bytes:bytes = None
        req_body:str = None
        req_body_b64:str = None

        try:
            content_len:int = int(self.headers.get("content-length", 0))
            if(content_len > 0):
                req_body_bytes = self.rfile.read(content_len)
        except Exception as e:
            logger.error("Error reading body content")
            logger.exception(e)
            content_len = 0
            req_body_bytes = None

        if req_body_bytes is not None:
            # if we have a body, let's decode it.
            try:
                req_body = req_body_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # if we can't decode it, let's base64 encode it
                req_body_b64 = base64.b64encode(req_body_bytes).decode('utf-8')

        done_body_read = time.perf_counter()

        # we're good now, handle the http request, make a response
        req = HttpRequest( req_fqdn = req_fqdn,
                           zone_fqdn = zone_fqdn,
                           remote_addr = self.client_address[0],
                           method = self.command,
                           path = self.path,
                           headers = {h:v for h,v in self.headers.items()}, # self.headers is not a dict so we need to make it one.
                           version = self.request_version,
                           body = req_body,
                           body_b64 = req_body_b64,
                           tls = isinstance(self.connection, ssl.SSLSocket))

        # gets the response from the rule engine, and check if empty.
        if response := get_response(req):
            self.sendHttpResponse(response)
        else:
            logger.warning("get_response() returned None, it's supposed to return a default response")
            self.sendHttpResponse(HttpResponse.Empty())

        done_send_resp = time.perf_counter()
        
        db_client.save_interaction(req, response)

        done_db_write = time.perf_counter()

        stop_total_req = time.perf_counter()

        get_db:float = round(done_get_db - start_of_req, 6)
        dom_check:float = round(done_dom_check - done_get_db, 6)
        zone_check:float = round(done_zone_check - done_dom_check, 6)
        body_read:float = round(done_body_read - done_zone_check, 6)
        send_resp:float = round(done_send_resp - done_body_read, 6)
        db_write_time:float = round(done_db_write - done_send_resp, 6)
        request_time:float = round(stop_total_req - start_of_req, 6)
        
        

        logger.debug("request %.3fs, get_db: %.3fs, dom_check: %.3fs, zone_check: %.3fs, body_read: %.3fs, send_resp: %.3fs, db_write: %.3fs", request_time, get_db, dom_check, zone_check, body_read, send_resp, db_write_time)

        # logger.debug("response %.3fs, db %.3fs, total: %.3fs, needle: %.3f", request_time, db_write_time, total_req, total_req2)
        return 


    def sendHttpResponse(self, http_response:HttpResponse=None):
        """
        Sends an HTTPResponse onto "the wire"
        """
        if http_response is None:
            logger.warning('sendHttpResponse() used with None, setting default reply')
            http_response = HttpResponse.Empty()
        
        # ensure the status code is valid,
        # may change that for future HTTP fuzzing, but let's stick to 100-600 for now.
        if http_response.status_code > 99 and http_response.status_code < 600:
            self.send_response(http_response.status_code)
        else:
            logger.warning("Invalid status code %d, setting to default", http_response.status_code)
            self.send_response(HttpResponse.Empty().status_code)

        # skip sending this header
        skip = [ "content-length" ]
        for hdr in http_response.headers.keys():
            if hdr.lower() not in skip:  # Convert current header to lowercase for comparison
                self.send_header(hdr, http_response.headers.get(hdr))

        # always send content-length
        content_len = int(http_response.headers.get("content-length", len(http_response.body)))
        self.send_header("content-length", content_len)
        self.end_headers()

        if (len(http_response.body) > 0):
            self.wfile.write(http_response.body.encode('utf-8', 'ignore'))

        return
            

# if called directly, fail. 
if __name__ == '__main__':
  print("[!] Sorry, you can't run this directly")
  sys.exit(1)
