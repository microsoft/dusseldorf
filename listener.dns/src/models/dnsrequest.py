# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

import json
from .dnsresponse import DnsResponse
from zentralbibliothek.models.networkrequest import NetworkRequest


class DnsRequest(NetworkRequest):
    """
    A class that represents a DnsRequest, so we can save it in storage.
    """
    _zone:str
    """Soon: FQDN""" # TODO: #BYOD
    _domain:str
    _reqtype:str
    """Textual repesentaion of DNS request"""
    _remote_addr:str
    _ttl:int
    _req_fqdn:str

    def __init__(self, req_fqdn:str, zone_fqdn:str, reqtype:str, remote_addr:str, domain:str, ttl:int = 60):
        """Default constructor

        Args:
            reqtype (str): DNS request type, always uppercase
            remote_addr (str): remote address
            zone (str): the current session's zone
            domain (str): the domain
            ttl (int, optional): optional time to live. Defaults to 60.
        """
        super().__init__(req_fqdn=req_fqdn, zone_fqdn=zone_fqdn, protocol='DNS', remote_addr=remote_addr)
        self._reqtype:str = reqtype.upper()
        self._remote_addr = remote_addr
        self._zone = zone_fqdn
        self._domain = domain
        self._ttl = ttl
        self._req_fqdn = req_fqdn
   
    def __str__(self):
        return f"DNS {self._reqtype} {self._req_fqdn}"

    @property
    def summary(self):
        return f"{self._reqtype}/{self._req_fqdn}"

    @property
    def isSupported(self) -> bool:
        """Check if this request is supported, need to hold parity with dnslistener."""
        supported_list = [
            "A",
            "AAAA",
            #"CAA",
            "CNAME",
            #"MX", 
            "NS",
            #"PTR", 
            "SOA", 
            #"TXT"
        ]
        return self.RequestType in supported_list

    @property
    def RequestType(self):
        """The request type.

        Returns:
            str: DNS request type, upper cased
        """
        return self._reqtype.upper()

    @property
    def fqdn(self):
        """The fully qualified domain name.

        Returns:
            str: Freshly Qualified Domain Name :)
        """
        return self._req_fqdn
    
    @property
    def json(self):
        return json.dumps({
            'request_type': self._reqtype,
            'ttl': self._ttl
        })
    
    @property
    def default_response(self):
        data:dict= {}
        ttl:int = 60 * 60
        
        # default values 
        if self._reqtype == "A":
            data= { "ip": DnsResponse.default_ip() }
        elif self._reqtype == "AAAA":
            data = { "ip": DnsResponse.default_ipv6() } 
        elif self._reqtype == "MX":
            name, priority = DnsResponse.default_mx()
            data= { "name": name, "priority": priority }
        elif self._reqtype == "NS":
            data= { "ns": DnsResponse.default_dns() }
        elif self._reqtype == "CAA":
            data = DnsResponse.default_caa_obj()
        elif self._reqtype == "SOA":
            data= DnsResponse.default_soa_obj()
        elif self._reqtype == "TXT":
            data= {"txt": DnsResponse.default_txt() }
        elif self._reqtype == "CNAME":
            data= { "cname": DnsResponse.default_cname() }
            
        return DnsResponse(
            type = self.RequestType,
            name = self.fqdn,
            ttl  = self._ttl or ttl,
            data = data
        )