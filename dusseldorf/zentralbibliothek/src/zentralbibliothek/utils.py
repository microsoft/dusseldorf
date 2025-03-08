# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

import asyncio
from datetime import datetime, timezone
import dateutil.parser as dateparse
import math
import operator
import re
import random
import string
from colorama import Fore
from functools import reduce
from cachetools.func import ttl_cache

import idna

class Utils:
    @classmethod
    def banner(cls):
        """
        Prints the ASCII art at the launch of the program.
        """
        print(f"             {Fore.RED}(   (                   (   (     ")
        print(f"    (        )\\ ))\\ )     (  (       )\\ ))\\ )  ")
        print(f"    )\\ )   ( ({Fore.LIGHTRED_EX}()/(()/(  {Fore.RED}( )\\ )\\ )   ({Fore.LIGHTRED_EX}()/(()/{Fore.RED}(")
        print(f"   ({Fore.LIGHTRED_EX}()/( ))\\ /(_))(_)) {Fore.RED}){Fore.LIGHTRED_EX})((_|()/( (  /{Fore.YELLOW}(_){Fore.LIGHTRED_EX})(_){Fore.RED})")
        print(f"{Fore.LIGHTRED_EX}    ({Fore.YELLOW}(_))((_|_))(_))  /( (_) ((_)))\\(_))(_)){Fore.LIGHTRED_EX}_|")
        print(f"{Fore.YELLOW}    _| {Fore.LIGHTYELLOW_EX}(_))(/ __/ __|(_))| | _| |((_) _ \\ {Fore.YELLOW} _|")
        print(f"{Fore.LIGHTYELLOW_EX}  / _` {Fore.LIGHTWHITE_EX}| || \\__ \\__ \\/ -_) / _` / _ \\   / __{Fore.LIGHTYELLOW_EX}|")
        print(f"{Fore.LIGHTWHITE_EX}  \\__,_|\\_,_|___/___/\\___|_\\__,_\\___/_|_\\_|")
        print(f"       {Fore.WHITE}microsoft security | aka.ms/dusseldorf")
        print(Fore.RESET)
        print("duSSeldoRF is a flexible out-of-band auto responder to help in SSRF, RFI, XXE,... research.")
        # AttackerEndpoint as a Service AEaaS :)
        print("", flush=True)  

    @classmethod
    def get_subdomain(cls, length=20, keyspace="abcdef1234567890"):
        """
        An over engineered random string creator :)
        """
        if len(keyspace) == 0:
            return "" 
        tot_keyspace = keyspace * math.floor((length/len(keyspace)) + 1) 
        return ''.join(random.sample(tot_keyspace, length))

    @classmethod
    def generate_randomized_inverted_timestamp(cls, suffix_len:int=6) -> str:
        """
        A method that gets an inverted timestamp (t0 = 01/01/2050) with 
        a random hex string appended to the end to prevent collisions. 

        Args:
            k:int
                The length of the random string suffix.
        Returns:
            string
        """
        far_away = datetime(2050,1,1).replace(tzinfo=timezone.utc)
        inverted_timestamp = str( (far_away - datetime.now(timezone.utc)).total_seconds() ).replace(".", "")
        random_suffix = ''.join(random.choices(string.hexdigits, k=suffix_len))
        return f"{inverted_timestamp}{random_suffix}".lower()

    @classmethod    
    def timeformat(cls, ts):
        """
        Consistent timeformats, pet peeve of mine.
        """
        try: 
            return dateparse.parse(ts).strftime("%b %d %Y %H:%M:%S")
        except: 
            # date parsing failed, default is "" or timenow?
            return ""
    
    @classmethod
    def dig(cls, obj:dict, keys:list, default=None):
        # inspired by me missing ruby: https://apidock.com/ruby/Hash/dig
        # implementation from https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
        """
        'Digs' through the dict-like object to find a nested value.
        E.g. for an object dic_obj={a: {b:c}, {d:{e:f}}}
        dig(yaml_obj, 'a.d.e') -> f
        dig(yaml_obj, 'a.wrong.hello') -> None
        """
        try:
            return reduce(operator.getitem, keys, obj)
        except (KeyError, IndexError):
            return default

    @classmethod
    # inspired by the work from
    # https://techoverflow.net/2020/10/01/how-to-fix-python-asyncio-runtimeerror-there-is-no-current-event-loop-in-thread/
    def get_eventloop(cls):
        """
        Utility function to avoid errors related to fetching the event loop for async threaded tasks. 
        """
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    @classmethod
    def fqdn_is_valid(cls, domain:str, fqdn:str) -> bool:      
        # if invalid, fail quickly.      
        if fqdn is None or fqdn=='' or cls.valid_dns_label(fqdn) == False:
            return False 
       
        # if this is a vald top level domain
        # or if under one of valid domains
        return fqdn == domain or fqdn.endswith("." + domain)
    
    
    @classmethod
    @ttl_cache(maxsize= 100, ttl= 300)
    def valid_dns_label(cls, fqdn:str, strict:bool = True) -> bool:
        """
        Validates whether this is a valid DNS label.  
        Valid means: 
            - less than 255 chars
            - containing N chunks
            - each chunk is less than 64 characters
            - chunks are seperated by a period (".") character

        Args:
            fqdn (str): domain name
            strict (bool): whether we should be forgiving on bad DNS labels

        Returns:
            bool: whether this is valid
        """
        if len(fqdn) == 0 or len(fqdn) > 255: return False
        ascii_domain:str = fqdn.lower()
        if strict:
            try:
                ascii_domain = idna.encode(fqdn).decode('utf-8')
            except idna.core.IDNAError:
                return False
            
        pattern:str = '^([a-z0-9-]{0,61}[a-z0-9])?$' if strict == True else '^[a-z0-9-][^.\\s]{1,63}$'
        allowed = re.compile(pattern, re.IGNORECASE)
        return all(allowed.match(x) for x in ascii_domain.split("."))