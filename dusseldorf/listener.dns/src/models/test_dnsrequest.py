# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest

from models.dnsresponse import DnsResponse

from .dnsrequest import DnsRequest

req = DnsRequest(
    req_fqdn="sub.zone.test.net", 
    zone_fqdn="zone.test.net", 
    reqtype="a", 
    domain="test.net",
    remote_addr="1.2.3.4")

def test_dnsrequest():
    assert req.req_fqdn == "sub.zone.test.net"
    assert req.zone_fqdn == "zone.test.net"
    assert req.remote_addr == "1.2.3.4"

def test_dnsrequest_upper_type():
    assert req.RequestType == "A" # must be upper

def test_dnsrequest_supported():
    assert req.isSupported == True

def test_dnsrequest_json():
    json = req.json
    assert json == '{"request_type": "A", "ttl": 60}'

def test_dnsrequest_default_SOA_response():
    req2 = req
    req2._reqtype = "SOA"
    resp = req2.default_response
    assert "rname" in resp.ResponseData.keys()
    
def test_dnsrequest_default_SOA_response():
    req2 = req
    req2._reqtype = "MX"
    resp = req2.default_response
    assert "priority" in resp.ResponseData.keys()

def test_dnsrequest_default_SOA_response2():
    # default values
    contact = DnsResponse._get_contact()
    req2 = req
    req2._reqtype = "SOA"
    resp = req2.default_response
    assert resp.ResponseData.get("rname") == contact.replace("@", ".")

def test_dnsrequest_default_cname_response():
    dom = DnsResponse._get_domain()
    req2 = req
    req2._reqtype = "CNAME"
    resp = req2.default_response
    assert resp.ResponseData.get("cname") == f"cname.{dom}."


    