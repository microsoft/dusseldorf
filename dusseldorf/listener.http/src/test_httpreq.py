# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest
from models.httprequest import HttpRequest

def _get_http_request():
    return HttpRequest(
        req_fqdn='test.dusseldorf.local',
        zone_fqdn='dusseldorf.local',
        remote_addr='127.0.0.1',
        method='GET',
        path='/test',
        version='1.1',
        headers={'Content-Type': 'application/json'},
        body='{"key": "value"}',
        tls=False
    )


def test_http_request_mehtod():
    req = _get_http_request()
    assert req.method == 'GET'

def test_http_request_path():
    req = _get_http_request()
    assert req.path == '/test'

def test_http_request_version():
    req = _get_http_request()
    assert req.version == '1.1'

def test_http_request_headers():    
    req = _get_http_request()
    assert req.headers == {'Content-Type': 'application/json'}
    assert req.body == '{"key": "value"}'
    assert req.tls is False

def test_http_request_default_response_as_json():
    req = _get_http_request()
    assert req.json == '{"method": "GET", "path": "/test", "version": "1.1", "headers": {"Content-Type": "application/json"}, "body": "{\\"key\\": \\"value\\"}", "tls": false}'

def test_http_request_default():    
    req = _get_http_request()
    # Test the default_response property
    assert req.default_response.status_code == 200
    assert req.default_response.headers == {}
    assert req.default_response.body == ''

def test_http_request_summary():    
    req = _get_http_request()
    # Test the summary property
    assert req.summary == 'GET /test'

def test_http_request_str():    
    req = _get_http_request()
    # Test the __str__ method
    assert str(req) == 'HTTP GET test.dusseldorf.local/test'