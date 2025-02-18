from dnsresolver import DusseldorfResolver
from models.dnsresponse import DnsResponse
import dnslib

rizz = DusseldorfResolver()
resp = DnsResponse(
    type="A",
    data={"ip": "1.2.3.4"},
    name="test.net",
    ttl=420)

def test_dnsresolver_none():
    a = rizz.make_resource_record(None)
    assert a is None

def test_dnsresolver_valid():
    rr = rizz.make_resource_record(resp)
    assert rr is not None

def test_dnsresolver_type():
    rr = rizz.make_resource_record(resp)
    assert type(rr) == dnslib.RR

def test_dnsresolver_values():
    rr = rizz.make_resource_record(resp)
    assert rr.rname == "test.net" 
    assert rr.rtype == dnslib.QTYPE.A
    assert rr.rclass == 1
