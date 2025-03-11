# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import random
import logging
import os

from cachetools.func import ttl_cache
#from zentralbibliothek.config import Config
from zentralbibliothek.models.networkresponse import NetworkResponse
from zentralbibliothek.dbclient3 import DatabaseClient

class DnsResponse(NetworkResponse):
    
    """A DNS response"""
    #_config = Config()

    _rtype: str = ""
    _rdata: dict = {}
    _rname: str = ""
    _ttl: int = 3600

    def __init__(self, **kwargs):
        self._rtype = kwargs.get('type', '')
        self._rdata = kwargs.get('data', {})
        self._rname = kwargs.get('name', '')
        self._ttl = kwargs.get('ttl', 3600)

    @property
    def summary(self):
        """Display the DnsResponse as a string"""
        if self.ResponseType == "AAAA":
            return self.ResponseData["ip"]

        if self.ResponseType == "A":
            return self.ResponseData["ip"]

        if self.ResponseType == "CAA":
            flags = self.ResponseData['flags']
            tag   = self.ResponseData['tag']
            value = self.ResponseData['value']
            return f"{flags} {tag} {value}"

        if self.ResponseType == "CNAME":
            return self.ResponseData["cname"]

        if self.ResponseType == "NS":
            return self.ResponseData["ns"]

        if self.ResponseType == "NXDOMAIN":
            return "NXDOMAIN"

        if self.ResponseType == "MX":
            priority = self.ResponseData['priority']
            mx = self.ResponseData['name']
            return f"{priority} {mx}"

        if self.ResponseType == "SOA":
            mname = self.ResponseData['mname']
            rname   = self.ResponseData['rname']
            return f"{mname} {rname}"

        if self.ResponseType == "TXT":
            return self.ResponseData["txt"]

        return f"{self.ResponseData}"

    def __str__(self):
        return f"DNS {self.ResponseType}/{self.summary}"




    @property
    def json(self):
        return json.dumps(dict({
            'ResponseData': self.ResponseData,
            'ResponseType': self.ResponseType,
            'ResponseName': self.ResponseName, 
            'TTL': self.TTL
        }))
    
    @classmethod
    def forZone(cls, req):
        """
        Makes sure we dont use any rule (for now)
        for a zone-only request. 
        """
        logging.info(f"forZone({req.RequestType}/{req.fqdn})")
        return cls.fromRequest(req)
        
    @classmethod
    @ttl_cache(10, 60) # would never really change imho
    def default_ip(cls):
        hardcoded = random.choice(cls._get_public_ips())
        return hardcoded

    @classmethod
    @ttl_cache(300, 300)
    def default_ipv6(cls):
        hardcoded = random.choice(os.getenv("DSSLDRF_IPV6", "").split(" "))
        return hardcoded

    @classmethod
    @ttl_cache(300, 300)
    def default_cname(cls):
        domain = cls._get_domain()
        return f"cname.{domain}."

    @classmethod
    @ttl_cache(300, 300)
    def default_dns(cls):
        dns_server = random.choice( cls._get_public_ips() )
        return dns_server

    @classmethod
    @ttl_cache(300, 300)
    def default_mx(cls) -> tuple:
        db = DatabaseClient.get_instance()
        domain = db.get_domains()[0]
        return f"mail.{domain}", 10

    @classmethod
    @ttl_cache(300, 300)
    def default_txt(cls) -> str:
        return "txt"

    @classmethod
    @ttl_cache(300, 300)
    def default_caa_obj(cls) -> any:
        return { "flags" : 0, 
                 "tag" : "issue", 
                 "value" : "microsoft.com"}

    @classmethod
    @ttl_cache(300, 300)
    def default_soa_obj(cls) -> any:
        return { "mname": cls.default_dns(),
                 "rname": cls._get_contact().replace("@", "."),
                 "times": (
                        2025022101,  # serial number
                        7200,        # refresh 7200
                        10800,       # retry  10800
                        259200,      # expire 259200
                        3600,        # minimum 3600
                 )}

    @classmethod
    def fromRequest(cls, req):
        """
        Create a DnsResponse object from a DnsRequest object.
        """
        data = {}
        ttl = req._ttl or 3600

        if req._reqtype == "A":
            data = {"ip": cls.default_ip()}
        elif req._reqtype == "AAAA":
            data = {"ip": cls.default_ipv6()}
        elif req._reqtype == "MX":
            name, priority = cls.default_mx()
            data = {"name": name, "priority": priority}
        elif req._reqtype == "NS":
            data = {"ns": cls.default_dns()}
        elif req._reqtype == "CAA":
            data = cls.default_caa_obj()
        elif req._reqtype == "SOA":
            data = cls.default_soa_obj()
        elif req._reqtype == "TXT":
            data = {"txt": cls.default_txt()}
        elif req._reqtype == "CNAME":
            data = {"cname": cls.default_cname()}

        return cls(
            type=req._reqtype,
            name=req._req_fqdn,
            ttl=ttl,
            data=data
        )

    @property
    def ResponseName(self) -> str:
        return self._rname

    @property
    def ResponseData(self) -> dict:
        return self._rdata
        
    @property
    def ResponseType(self) -> str:
        return self._rtype.upper()

    @property
    def TTL(self) -> int:
        return self._ttl
    
    # internal helper methods

    @classmethod
    @ttl_cache(300, 300)
    def _get_public_ips(cls):
        db = DatabaseClient.get_instance()
        if public_ips := db.get_public_ips():
            return public_ips
        hardcoded = ["127.0.0.8", "127.0.0.9"]
        return hardcoded
    
    @classmethod
    @ttl_cache(300, 300)
    def _get_domain(cls):
        db = DatabaseClient.get_instance()
        return db.get_domains()[0]

    @classmethod
    @ttl_cache(300, 300)
    def _get_contact(cls):
        return "info@" + cls._get_domain()