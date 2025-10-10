# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# the DNS resolver for the dataplane.

import ipaddress
import time
import dnslib
import os 
import sys, logging

from zentralbibliothek.dbclient3 import DatabaseClient
from zentralbibliothek.utils import Utils

from dnslib import RR
from dnslib.server import BaseResolver
from dnsruleengine import get_response

from models.dnsrequest import DnsRequest
from models.dnsresponse import DnsResponse

DEFAULT_TTL:int = 60 * 30
NOERROR:int = 0
NXDOMAIN:int = 3

count = 0 # global counter for requests
logger = logging.getLogger(__name__)

class DusseldorfResolver(BaseResolver):
    """
    A DNS resolver that will lookup if we have a predefined
    "auto response" rule, and log it.

    To resolve a given request, call the resolve method. 
    """
    
    def resolve(self, dnsrecord, handler) -> dnslib.DNSRecord:
        """
        This method resolves an incoming DNS query, passed using `dnsrecord` arg. 
        If the query is for a host not in the Dusseldorf domain, it will just return an NXDomain response. 
        If any rules match this query, the result of the rules will be in the response.
        Otherwise, it will be a default response. 
        """
        global count 
        count += 1

        # qtype_s is always uppercased: "CNAME", "A", ...
        qtype_s:str = str(dnslib.QTYPE[dnsrecord.q.qtype]).upper()
        
        # qname_s is always lowercased: so that "FoO.bAR" -> "foo.bar"
        qname_s:str = str(dnsrecord.q.qname).lower()

        client_ip:str = str(handler.client_address[0])

        reply = dnsrecord.reply()

        COUNT_INTERVAL:int = 1000
        if count % COUNT_INTERVAL == 0: 
            logger.info(f"dns.requests.count: {count}")

        # special cases, version.bind:
        if qname_s == "version.bind.":
            staticResponse:str = "dusseldorf"
            req:DnsRequest = DnsRequest("", "", 'TXT', client_ip, qname_s)
            resp:DnsResponse = req.default_response
            resp._rdata = { "txt": staticResponse }
            answer = self.make_resource_record(resp)
            reply.add_answer(answer)
            return reply

        # not sure if this is to be _optional_, but qname always have a trailing period.
        # Cutting that out for now.
        if qname_s[-1] == '.':
            qname_s = qname_s[:-1]
        
        request_fqdn = qname_s

        db = DatabaseClient.get_instance()

        domains:[] = db.get_domains()
        valid_domain:bool = False
        
        # TODO: make this a method in itself, so we can cache this
        for domain in domains:
            if Utils.fqdn_is_valid(fqdn=request_fqdn, domain=domain):
                valid_domain = True
                break

        if not valid_domain:
            logger.warning(f"Invalid domain: {request_fqdn}")
            reply.header.set_rcode(NXDOMAIN)
            return reply

        zone_fqdn = db.find_zone_for_request(request_fqdn)

        # the DNS request is not for our domain, or a zone isn't found
        # return NXDomain since we are not an open DNS relay.
        if zone_fqdn is None:
            req = DnsRequest(request_fqdn, "", qtype_s, client_ip, request_fqdn)
            resp = req.default_response

            # if we can't make a rr, raise nxdomain and log it.
            if answer := self.make_resource_record(resp):
                reply.add_answer(answer)
                reply.header.set_rcode(NOERROR) 
            else:
                logger.warning(f"could not make RR for {qtype_s}/{request_fqdn}")
                reply.header.set_rcode(NXDOMAIN)
            return reply
        
        # Get the domain from the zone_fqdn
        domain = db.get_domain_from_zone(zone_fqdn)

        # region Reserved Requests
        """
        Handle the requests to a few known named top level domains first, 
        this is dangerous and thus not configurable in DB.
        """
        # TODO: #BYOD
        reserved = [ domain, 
                    f"ns1.{domain}", 
                    f"ns2.{domain}" ]

        if qname_s in reserved:
            req = DnsRequest(request_fqdn, "", qtype_s, client_ip, request_fqdn)
            if resp := DnsResponse.forZone(req):
                answer = self.make_resource_record(resp)
                reply.add_answer(answer)

                # if this is a CAA request, we need to add an additional CAA record
                if qtype_s == "CAA":
                    # hardcoded CAA resp
                    email = "caarecordaware@microsoft.com" 
                    resp = req.default_response
                    resp._rdata = { "flags": 0, "tag": "contactemail", "value": email }                    
                    caa_answer = self.make_resource_record(resp)
                    reply.add_answer(caa_answer)

                    # also iodef
                    resp = req.default_response
                    resp._rdata = { "flags": 0, "tag": "iodef", "value": f"mailto:{email}" }                    
                    iodef_answer = self.make_resource_record(resp)
                    reply.add_answer(iodef_answer)

            else:
                logger.warning(f"could not make RR for zone request {qtype_s}/{request_fqdn}")
                reply.header.set_rcode(NXDOMAIN)
            return reply
        # endregion
        
        # now we know it's a valid request
        # measure perf from now onwards
        start_of_request = time.perf_counter()

        # sent to a valid domain
        req = DnsRequest(req_fqdn    = request_fqdn,
                         zone_fqdn   = zone_fqdn,
                         reqtype     = qtype_s,
                         remote_addr = client_ip,
                         domain      = domain)  # Use the domain here

        # get the response from the rule engine
        response = get_response(req)

        if response is None:
            logger.error(f"no response found for {qtype_s}/{request_fqdn}")
            reply.header.set_rcode(NXDOMAIN)
            return reply

        if answer := self.make_resource_record(response):
            reply.add_answer(answer)
        else:
            logger.warning(f"could not make RR for {qtype_s}/{request_fqdn}")
        
        end_of_request = time.perf_counter()

        start_db_write = time.perf_counter()

        if response is not None:
            db.save_interaction(req, response)

        end_db_write = time.perf_counter()

        request_time:float = round(end_of_request - start_of_request, 6)
        db_write_time:float = round(end_db_write - start_db_write, 6)

        logger.debug("DNSlistener resp: %.3f s, DB write: %.3f s", request_time, db_write_time)
        return reply

    def make_resource_record(self, response:DnsResponse) -> dnslib.RR:
        """
        makeAnswerFromResponse(DnsResponse) -> RR
        Makes a (binary) DNS packet based out the (DnsReponse) response
        Parameters:
            response:DnsResponse -- the DNS response we're sending back. 
        Returns: dnslib.RR record (could be A, MX, SOA...)
        """
        if(response is None):
            logger.warning("make_resource_record() called with response == None")
            return None

        rtype = None
        def _RR(rdata:any, ttl:int = 60) -> RR:
            """Embedded method to return dns.RR type"""
            rname = response.ResponseName
            return RR(rname=rname,
                      rtype=rtype,
                      rclass=1,
                      ttl=ttl,
                      rdata=rdata)

        # fail quickly
        supported_types = list(dnslib.QTYPE.forward.values())
        if response.ResponseType not in supported_types:
            return _RR(dnslib.TXT(""))
        
        # ipv4
        if response.ResponseType == "A":
            ip = response.ResponseData["ip"]
            try:
                data = str(ipaddress.IPv4Address(ip))
            except ipaddress.AddressValueError:
                logger.warning("Invalid IPv4 address: %s", ip)
                data = "0.0.0.0" # ?
            rtype = dnslib.QTYPE.A
            return _RR(dnslib.A(data))

        # ipv6
        if response.ResponseType == "AAAA":
            ip = response.ResponseData["ip"]
            try:
                data = str(ipaddress.IPv6Address(ip))
            except ipaddress.AddressValueError:
                logger.warning("Invalid IPv6 address: %s", ip)
                data = "::"
            rtype = dnslib.QTYPE.AAAA
            return _RR(dnslib.AAAA(data))

        # caa record
        if response.ResponseType == "CAA":
            rtype = dnslib.QTYPE.CAA
            flags = response.ResponseData["flags"]
            tag   = response.ResponseData["tag"]
            value = response.ResponseData["value"]
            return _RR(dnslib.CAA(flags=flags, tag=tag, value=value))

        if response.ResponseType == "CNAME":
            rtype = dnslib.QTYPE.CNAME
            cname = response.ResponseData["cname"]
            return _RR(dnslib.CNAME(cname))

        if response.ResponseType == "MX":
            rtype = dnslib.QTYPE.MX
            name:str = response.ResponseData["name"]
            priority:int = response.ResponseData["priority"]
            return _RR(dnslib.MX(label=name, preference=priority))

        if response.ResponseType == "NS":
            rtype = dnslib.QTYPE.NS
            dns_server:str = response.ResponseData["ns"]
            return _RR(dnslib.NS(dns_server))

        if response.ResponseType == "SOA":
            rtype = dnslib.QTYPE.SOA
            soa = DnsResponse.default_soa_obj()
            mname:str   = soa.get("mname")
            rname:str   = soa.get("rname")
            times:tuple = soa.get("times")
            return _RR(dnslib.SOA(mname, rname, times))

        if response.ResponseType == "TXT":
            rtype = dnslib.QTYPE.TXT
            txt = response.ResponseData["txt"]
            return _RR(dnslib.TXT(txt))

        logger.warning("Unsupported DNS type: %s", response.ResponseType)
        rtype = dnslib.QTYPE.TXT
        return _RR(dnslib.TXT(""))


# if called directly, fail.
if __name__ == '__main__':
    print("[!] Sorry, you can't run this directly")
    sys.exit(-1)
