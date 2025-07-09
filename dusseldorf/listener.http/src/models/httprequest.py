# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
from models.httpresponse import HttpResponse

from zentralbibliothek.models.networkrequest import NetworkRequest

class HttpRequest(NetworkRequest):
    """
        A class representing a Http Request
    """
    method:str
    """The HTTP method used"""

    path:str
    """The path being requested"""

    version:str 
    """The HTTP version (0.9, 1.0, 1.1 or 2)"""

    headers:dict
    """A `dict` of HTTP request headers"""

    body:str 
    """A string representing the body"""

    body_b64:str
    """A string representing a base64 encoded body, if the body is binary or not UTF-8 encoded"""

    tls:bool
    """Whether this request was done over a TLS protected connection"""

    def __init__(self, req_fqdn:str, zone_fqdn:str, remote_addr:str, **kwargs):
        super().__init__(req_fqdn=req_fqdn, zone_fqdn=zone_fqdn, protocol='HTTP', remote_addr=remote_addr)
        
        self.req_fqdn = req_fqdn
        self.zone_fqdn = zone_fqdn
        self.remote_addr = remote_addr
        
        allowed_keys = [ "method", "path", "version", "headers", "body", "body_b64", "tls"]
        for key in allowed_keys:
            self.__setattr__(key, kwargs.get(key))

    @property
    def json(self):
        """Returns a JSON alike representation of the HTTP Request"""
        return json.dumps(dict({
            'method': self.method,
            'path': self.path,
            'version': self.version,
            'headers': self.headers,
            'body': self.body,
            'body_b64': self.body_b64,
            'tls': self.tls,
        }))

    @property
    def default_response(self):
        return HttpResponse(status_code=200, headers={}, body='')

    @property
    def summary(self):
        maxpath:str  = (self.path[:20] + '..') if len(self.path) > 20 else self.path
        return f"{self.method} {maxpath}"
   
    def __str__(self):
        return f"{'HTTPS' if self.tls else 'HTTP'} {self.method} {self.req_fqdn}{self.path}"
    