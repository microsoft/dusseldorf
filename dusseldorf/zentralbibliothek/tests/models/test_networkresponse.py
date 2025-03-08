# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest
from zentralbibliothek.models.networkresponse import NetworkResponse

def test_networkresponse_successful():
    '''
    This test makes sure that we can write a child class outside of zentralbibliothek
    that can be parented to the abstract networkresponse class in zentralbibliothek.
    '''
    class TestNetworkResponse(NetworkResponse):
        def __init__(self, response, zone, metadata, request):
            super().__init__()

        def json(self):
            return '{"something": "here"}'
        
        def summary(self):
            return "summary"
    
    test_response = TestNetworkResponse("response", "zone", "metadata", "request")
    assert test_response.json() == '{"something": "here"}'
    assert test_response.summary() == "summary"

def test_networkresponse_missingmethods():
    '''
    This test does not implement the abstract methods in the child class, and so should fail.
    '''
    class TestNetworkResponse(NetworkResponse):
        def __init__(self, response, zone, metadata, request):
            super().__init__(response=response, zone=zone, metadata=metadata, request=request)
    
    with pytest.raises(TypeError):
        test_response = TestNetworkResponse("response", "zone", "metadata", "request")