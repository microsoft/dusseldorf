# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

import logging
import os
import yaml
import pytomlpp

class Config():
    """
    This class represents the global config object.
    This is a singleton. 
    """
    _instance = None
    _cfg = None
    _values:dict = {
        "connstr": "",
        "domains": []
    }

    _readonly_keys = []

    appInsightsConnString = ""

    # general keys
    db_min_conn:int = 2
    db_max_conn:int = 20

    # connecting string
    connstr:str = os.environ.get("DSSLDRF_CONNSTR", "")

    # space separated list of domains from env, or use default
    domains = os.environ.get("DSSLDRF_DOMAINS", "").split(" ")

    ipv4_addresses = os.environ.get("DSSLDRF_IPV4", "127.0.0.1 127.0.0.2").split(" ")
    ipv6_addresses = os.environ.get("DSSLDRF_IPV6", "").split(" ")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set(cls, key, value, readonly=False):
        """
        Set a config value. 
        """
        if key in cls._values:
            logging.info(f"Overwriting config value for {key}")
            if key in cls._readonly_keys:
                raise ValueError(f"{key} is readonly")
            else:
                if readonly:
                    cls._readonly_keys.append(key)

        cls._values[key] = value
    
    @classmethod
    def get(cls, key):
        """
        Utility for when you only need to quickly grab one value.
        """
        return cls._values.get(key)

    @classmethod
    def load_config(cls, filename:str=""):
        if os.path.exists(filename) is False:
            raise ValueError(f"Config file {filename} does not exist")
        try:
            cls._values = pytomlpp.load(filename, mode="rt") # rt = text mode
        except Exception as e:
            raise ValueError(f"Error reading config file: {e}")

    @DeprecationWarning
    def _load(cls):
        # setup logging if we have app insights enabled
        pass
        