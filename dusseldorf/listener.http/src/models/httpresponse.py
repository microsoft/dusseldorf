# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
from zentralbibliothek.models.networkresponse import NetworkResponse

class HttpResponse(NetworkResponse):
    """
        A class representing a Http Response
    """

    status_code:int
    """The response code as a number"""

    headers:dict
    """A `dict` of HTTP response headers"""

    body:str
    """A string representing the body"""

    # @property
    @classmethod
    def Empty(cls):
        """Static empty reply (200, no headers nor body)"""
        return HttpResponse(status_code=200, headers={}, body='')

    def __init__(self, **kwargs):
        """
        Kwargs:
            status_code:int HTTP response code
            headers:dict HTTP response headers
            body:str HTTP response body
        """
        self.status_code = kwargs.get('status_code', 200)
        self.headers = kwargs.get('headers', {})
        self.body = kwargs.get('body', '')

    @property
    def json(self):
        """
        Returns a blob-like (dict) representation of the HttpResponse.
        """
        return json.dumps(dict({
            'code': self.status_code, 
            'headers': self.headers, 
            'body': self.body
        }))
    
    def __str__(self):
        return f"HTTP {self.status_code}"

    @property
    def summary(self):
        return str(self)