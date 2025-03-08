# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest
from zentralbibliothek.models.networkrequest import NetworkRequest

def test_networkrequest_successful():
    '''
    This test makes sure that we can write a child class outside of zentralbibliothek
    that can be parented to the abstract networkrequest class in zentralbibliothek.
    '''
    class TestNetworkRequest(NetworkRequest):
        def __init__(self, req_fqdn, zone_fqdn, protocol, remote_addr):
            super().__init__(req_fqdn=req_fqdn, zone_fqdn=zone_fqdn, protocol=protocol, remote_addr=remote_addr)

        def json(self):
            return '{"something": "here"}'
        
        def default_response(self):
            return "default response"
        
        def summary(self):
            return "summary"
    
    test_request = TestNetworkRequest("req_fqdn", "zone_fqdn", "protocol", "remote_addr")
    assert test_request.RequestFqdn == "req_fqdn"
    assert test_request.summary() == "summary"
    assert str(test_request) == "protocol request from remote_addr to req_fqdn"

def test_networkrequest_missingmethods():
    '''
    This test does not implement the abstract methods in the child class, and so should fail.
    '''
    class TestNetworkRequest(NetworkRequest):
        def __init__(self, req_fqdn, zone_fqdn, protocol, remote_addr):
            super().__init__(req_fqdn, zone_fqdn, protocol, remote_addr)
    
    with pytest.raises(TypeError):
        test_request = TestNetworkRequest("req_fqdn", "zone_fqdn", "protocol", "remote_addr")