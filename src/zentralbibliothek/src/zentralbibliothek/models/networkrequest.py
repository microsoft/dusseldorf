# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

from abc import ABC, abstractmethod
import ipaddress
from attr import dataclass

@dataclass(slots=True)
class NetworkRequest(ABC):
    """
    This is the abstract base class that all requests (HTTP, DNS, ...) inherit from. 
    Child classes MUST implement the json() function.
    """    
    zone_fqdn:str
    req_fqdn:str
    remote_addr:ipaddress
    protocol:str

    def __init__(self, req_fqdn:str, zone_fqdn:str, protocol:str, remote_addr:str):
        '''Constructor. Call this in your child classes, like `super().__init__(...)`.

        :param req_fqdn: The FQDN that this request came in to.
        :type req_fqdn: str
        :param zone_fqdn: The FQDN of the zone this request falls under.
        :type zone_fqdn: str
        :param protocol: The network protocol that this request uses (e.g. HTTP)
        :type protocol: str
        :param remote_addr: The IP address that the request originated from.
        :type remote_addr: str
        '''
        self.req_fqdn = req_fqdn
        self.zone_fqdn = zone_fqdn
        self.protocol = protocol
        self.remote_addr = remote_addr

    def __str__(self):
        return f"{self.protocol} request from {self.remote_addr} to {self.req_fqdn}"
    
    @property
    def NetworkProtocol(self):
        '''Return the network protocol that this request uses (e.g. http)'''
        return self.protocol.lower()
    
    @property
    def RequestFqdn(self) -> str:
        '''Return the full, lowercase FQDN that this request came in to.'''
        return self.req_fqdn.lower()
    
    @property
    def ZoneFqdn(self) -> str:
        '''Return the lowercase FQDN of the zone of this request.
        '''
        return self.zone_fqdn.lower()
    
    @property
    def RemoteAddress(self) -> str:
        '''Return the IP address that the request originated from.'''
        return self.remote_addr

    @property
    @abstractmethod
    def json(self):
        '''Implement this in your child classes to return a JSON blob of useful details
        about the request.
        '''
        pass

    @property
    @abstractmethod
    def default_response(self):
        '''Return an object of the class that inherits from NetworkResponse and should be used to
        create the response to your request class, with default values.
        '''
        pass

    @property
    @abstractmethod
    def summary(self):
        '''Return a short string describing this request, e.g. "HTTP GET microsoft.com"
        '''
        pass