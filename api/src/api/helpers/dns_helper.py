# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

import logging
import random
import re
import string
from re import search
from typing import Optional

logger = logging.getLogger(__name__)

class DnsHelper:
    """Helper class for DNS operations"""

    @staticmethod
    def generate_label(length: int = 12) -> str:
        """
        Generates a random DNS label of specified length
        
        Args:
            length: Length of the label to generate (default: 6)
            
        Returns:
            Random DNS label string
        """
        # First character must be a letter (DNS label rules)
        first = random.choice(string.ascii_lowercase)
        
        # Rest can be letters or numbers
        rest = ''.join(random.choices(
            string.ascii_lowercase + string.digits,
            k=length - 1
        ))
        
        return first + rest

    @staticmethod
    def normalize_domain(domain: Optional[str]) -> Optional[str]:
        """
        Normalizes a domain name by converting to lowercase and removing trailing dot
        
        Args:
            domain: Domain name to normalize
            
        Returns:
            Normalized domain name or None if input is None
        """
        if domain is None:
            return None
            
        # Convert to lowercase and remove trailing dot
        return domain.lower().rstrip('.')

    @staticmethod
    def validate_domain_name(domain: str) -> bool:
        """Validate a domain name according to RFC standards"""
        try:
            # Check length
            if len(domain) > 253:
                return False
            
            # Check format using DNS library
            pattern = re.compile(
                r'^(?:[a-zA-Z0-9]' # First character of the domain
                r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)' # Sub domain + hostname
                r'+[a-zA-Z]{2,6}$' # Top level domain
                )
    
            if not pattern.match(domain):
                return False

            return True
        
            # Additional RFC checks
            #pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
            #if not re.match(pattern, domain):
            #    return False
            
            #return True
        
        except Exception as e:
            logger.debug(f"Domain validation failed for {domain}: {str(e)}")
            return False

    @staticmethod
    def validate_zone_name(zone_name: str, domain: str) -> bool:
        """Validate a zone name within a domain"""
        try:
            if zone_name.startswith('.') or zone_name.endswith('.') or '..' in zone_name:
                return False

            max_length = 253 - (1 + len(domain))
            regex_format = f'^[a-z0-9-.]{{1,{max_length}}}$'
            regex_check = search(regex_format, zone_name)
            if regex_check:
                return True

            return False        
        except Exception as e:
            logger.debug(f"Zone validation failed for {zone_name}: {str(e)}")
            return False
    
    @staticmethod
    def validate_rule_syntax(rule_type: str, content: str) -> bool:
        """Validate DNS rule content based on type"""
        try:
            if rule_type == "A":
                return validate_ipv4(content)
            elif rule_type == "AAAA":
                return validate_ipv6(content)
            elif rule_type == "CNAME":
                return validate_domain_name(content)
            elif rule_type == "MX":
                return validate_mx_record(content)
            elif rule_type == "TXT":
                return validate_txt_record(content)
            elif rule_type == "NS":
                return validate_domain_name(content)
            elif rule_type == "PTR":
                return validate_domain_name(content)
            elif rule_type == "SRV":
                return validate_srv_record(content)
            elif rule_type == "CAA":
                return validate_caa_record(content)
            else:
                return False
                
        except Exception as e:
            logger.debug(f"Rule validation failed: {str(e)}")
            return False
    @staticmethod
    def validate_ipv4(ip: str) -> bool:
        """Validate IPv4 address"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
            
        # Check each octet
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    @staticmethod
    def validate_ipv6(ip: str) -> bool:
        """Validate IPv6 address"""
        try:
            # Use socket to validate IPv6
            import socket
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except:
            return False
    @staticmethod
    def validate_mx_record(content: str) -> bool:
        """Validate MX record format (priority hostname)"""
        try:
            priority, hostname = content.split()
            return (
                priority.isdigit() and
                0 <= int(priority) <= 65535 and
                validate_domain_name(hostname)
            )
        except:
            return False
    @staticmethod
    def validate_txt_record(content: str) -> bool:
        """Validate TXT record content"""
        # Basic validation - could be enhanced based on requirements
        return len(content) <= 255
    @staticmethod
    def validate_srv_record(content: str) -> bool:
        """Validate SRV record format (priority weight port target)"""
        try:
            priority, weight, port, target = content.split()
            return (
                all(x.isdigit() for x in [priority, weight, port]) and
                0 <= int(priority) <= 65535 and
                0 <= int(weight) <= 65535 and
                0 <= int(port) <= 65535 and
                validate_domain_name(target)
            )
        except:
            return False
    @staticmethod
    def validate_caa_record(content: str) -> bool:
        """Validate CAA record format (flag tag value)"""
        try:
            flag, tag, value = content.split()
            return (
                flag.isdigit() and
                0 <= int(flag) <= 255 and
                tag in ['issue', 'issuewild', 'iodef'] and
                len(value) <= 255
            )
        except:
            return False 