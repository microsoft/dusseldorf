# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
import random
import os
import string
import time
from pymongo import MongoClient, errors
from cachetools.func import ttl_cache
# from .config import Config
from .models.networkrequest import NetworkRequest
from .models.networkresponse import NetworkResponse
from azure.monitor.opentelemetry import configure_azure_monitor

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(
        logger_name="dssldrf.mongodbclient",  # Set the namespace for the logger in which you would like to collect telemetry for if you are collecting logging telemetry. This is imperative so you do not collect logging telemetry from the SDK itself.
    )

logger = logging.getLogger('dssldrf.mongodbclient')

class DatabaseClient:
    """
    This class handles all communication with the MongoDB database.
    It's a singleton - call get_instance() instead of making a new instance yourself. 
    """
    _instance = None
    _client = None
    _db = None

    def __init__(self) -> None:
        raise RuntimeError("This is a singleton class. Don't instantiate it, call get_instance instead.")
    
    @classmethod
    def get_instance(cls):
        """
        Call this method to get a MongoDBClient object to read from. 

        Returns:
            MongoDBClient: the singleton instance of this class.
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        """
        Internal method. Connects to the database.
        """
        connstr:str = os.environ.get("DSSLDRF_CONNSTR")
        dbname:str = os.environ.get("DSSLDRF_DBNAME", None)
        if not connstr:
            raise RuntimeError("Environment variable DSSLDRF_CONNSTR is not set or is empty")
        self._client = MongoClient(connstr)
        self._db = self._client.get_database(dbname)

    def test_connectivity(self) -> bool:
        """
        Test connectivity to the database, Returns true if succeeded, false if not. 
        """
        try:
            self._client.admin.command('ping')
            return True
        except errors.ConnectionFailure as ex:
            logger.warning(f"MongoDB connection failed: {ex}")
            return False
    
    @ttl_cache(maxsize=2, ttl=30)
    def guarantee_connectivity(self):
        """
        Test if the DB is connected. 
        If not, try once to reconnect. 
        If that doesn't work, raise a RuntimeError.
        Returns: None
        """
        if not self.test_connectivity():
            logger.warning('Database connection down, attempting to reconnect...')
            try:
                self._setup() 
            except Exception as ex:
                logger.critical(f'Unable to connect to database: {ex}')
                raise RuntimeError('Unable to connect to database')

    @ttl_cache(maxsize=256, ttl=5) 
    def domain_exists(self, domain_fqdn:str) -> bool:
        """
        Indicator method to tell if a domain exists in the database. 
        
        Arguments:
            domain_fqdn:str
                The FQDN of the domain to check.
        Returns:
            bool
        """
        self.guarantee_connectivity()
        try:
            count = self._db.domains.count_documents({"domain": domain_fqdn})
            return count > 0
        except Exception as ex:
            logger.critical(f"Unable to check if domain exists in database: {ex}")
            return False

    @ttl_cache(maxsize=256, ttl=5)
    def zone_exists(self, zone_fqdn:str) -> bool:
        """
        Indicator method to tell if a zone exists in the database.
        If a zone exists, it is guaranteed that its domain also exists (because of the strong 
        foreign key relationship in the database).

        Arguments:
            zone_fqdn:str
                The FQDN of the zone to check.
        Returns:
            bool
        """
        if zone_fqdn == "":
            return False
        
        self.guarantee_connectivity()
        try:
            count = self._db.zones.count_documents({"fqdn": zone_fqdn})
            return count > 0
        except Exception as ex:
            logger.critical(f"Unable to check if zone exists in database: {ex}")
            return False

    def save_interaction(self, req:NetworkRequest, resp:NetworkResponse) -> str:
        """
        Log a request (and its response) in the database.

        Arguments:
            req:NetworkRequest
                The request. What else would it be? 
            resp:NetworkResponse
                The response.
        Returns:
            str: The timestamp that the db assigned to this request.
        """
        self.guarantee_connectivity()
        try:
            result = self._db.requests.insert_one({
                "zone": req.zone_fqdn,
                "fqdn": req.req_fqdn,
                "protocol": req.protocol,
                "clientip": req.remote_addr,
                "request": req.json,
                "response": resp.json,
                "reqsummary": req.summary,
                "respsummary": resp.summary,
                "time": int(time.time())
            })
            return str(result.inserted_id)
        except Exception as ex:
            logger.critical(f"Unable to save request/response to database: {ex}")
            return ''

    @ttl_cache(maxsize=64, ttl=1)
    def get_rules(self, zone_fqdn:str):
        """
        Get all the rules for the given zone FQDN, as a list of dictionaries. 
        
        Arguments:
            zone_fqdn:str
                The FQDN of the zone to check.
        Returns:
            list[dict]
        """
        self.guarantee_connectivity()
        try:
            rules = list(self._db.rules.find({"zone": zone_fqdn}).limit(1000))
            return rules
        except Exception as ex:
            logger.critical(f"Unable to get rules from database: {ex}")
            return []

    @ttl_cache(maxsize=256, ttl=30)
    def find_zone_for_request(self, request_fqdn):
        """
        Find the Zone FQDN for a given request's FQDN e.g. if a zone exists with FQDN `sahil.ssrf.ms` 
        and a request comes in on `hello.sahil.ssrf.ms`, this can help you find the zone.
        If this returns an fqdn, that means the zone, and therefore the domain, are guaranteed to exist. 

        Arguments: 
            zone_fqdn:str
                The FQDN of the zone to check.
        Returns:
            str: the fqdn of the zone.
            None: when no zone is found.
        """
        self.guarantee_connectivity()
        try:
            request_fqdn = request_fqdn.lower()
            # first try a direct match
            zone = self._db.zones.find_one({"fqdn": request_fqdn})
            if zone:
                return zone["fqdn"]

            # else, iterate through all zones and check if request_fqdn ends with zone fqdn
            zones = self._db.zones.find({}, {"_id": 0, "fqdn": 1})
            for zone_it in zones:
                if request_fqdn.endswith("." + zone_it["fqdn"].lower()):
                    return zone_it["fqdn"]

            # if we're here, we couldn't find a zone
            logger.debug(f"No zone found for fqdn: {request_fqdn}")
            return None
        
        except Exception as ex:
            logger.critical(f"Unable to find zone for request: {ex}")
            return None

    @ttl_cache(maxsize=256, ttl=1)
    def get_aggregated_rule_predicates_for_zone(self, network_protocol:str, zone_fqdn:str):
        """
        Returns a list of tuples with three elements each: rule id, list of action names, and list of corresponding action values. 

        Example: 
        >>> get_aggregated_rule_predicates_for_zone('myzone.dssldrf.net')
        <<< [
        <<<     ('rule-id-1', ['http.method', 'http.version'], ['GET,PUT', '1.1']),
        <<<     ('rule-id-2', ['http.body'], ['.*'])
        <<< ]
        """
        self.guarantee_connectivity()
        try:
            rules = self._db.rules.find({"networkprotocol": network_protocol, "zone": zone_fqdn})
            result = []
            for rule in rules:
                predicates = [(comp["actionname"], comp["actionvalue"]) for comp in rule["rulecomponents"] if comp["ispredicate"]]
                if predicates:
                    action_names, action_values = zip(*predicates)
                    result.append((rule["ruleid"], list(action_names), list(action_values)))
            return result
        except Exception as ex:
            logger.critical(f"Unable to get rule preds from database: {ex}")
            return []

    @ttl_cache(maxsize=256, ttl=1)
    def get_aggregated_rule_results(self, rule_id:str):
        """
        Returns a tuple describing all the results of a given rule. 

        Sample output: ('rule-id-here', ['action_name_1', ...], ['action_value_1', ...])
        """
        self.guarantee_connectivity()
        try:
            rule = self._db.rules.find_one({"ruleid": rule_id})
            if not rule:
                return (rule_id, [], [], [])
            results = [(comp["componentid"], comp["actionname"], comp["actionvalue"]) for comp in rule["rulecomponents"] if not comp["ispredicate"]]
            if results:
                component_ids, action_names, action_values = zip(*results)
                return (rule_id, list(component_ids), list(action_names), list(action_values))
            return (rule_id, [], [], [])
        except Exception as ex:
            logger.critical(f"Unable to get rule results from database: {ex}")
            return (rule_id, [], [], [])


    @ttl_cache(maxsize=256, ttl=30)
    def get_domain_from_zone(self, zone_fqdn:str):
        """
        Get the domain FQDN from a zone FQDN. 
        """
        if zone_fqdn == "":
            raise ValueError("zone_fqdn cannot be empty")
                
        self.guarantee_connectivity()
        try:
            zone = self._db.zones.find_one({"fqdn": zone_fqdn})
            return zone["domain"] if zone else ""
        except Exception as ex:
            logger.critical(f"Unable to get domain from zone: {ex}")
            return ""


    @ttl_cache(maxsize=256, ttl=30)
    def get_domains(self) -> list:
        """
        Get all the domains in the database. 
        """
        self.guarantee_connectivity()
        try:
            domains = self._db.domains.find()
            return [domain["domain"] for domain in domains]
        except Exception as ex:
            logger.critical(f"Unable to get domains from database: {ex}")
            return []


    def get_public_ips(self, domain:str="") -> list:
        """
        Get all the public IPs in the database. 
        """
        self.guarantee_connectivity()
        rec = None
        try:
            if domain != "":
                rec = self._db.domains.find_one({"domain": domain})
            else :
                rec = self._db.domains.find_one()
            
            if rec:
                return rec["public_ips"]

        except Exception as ex:
            logger.critical(f"Unable to get public IPs from database: {ex}")
        return []   


    @PendingDeprecationWarning
    def create_zone(self, zone_prefix:str = "", parent_zone:str = "") -> str:
        """
        Makes a new zone in the database.

        Parameters: 
            zone_prefix: if empty we make a random one
            parent_zone: a FQDN of a zone to link this new zone to.
        """
        if parent_zone == "":
            raise ValueError("parent zone cannot be empty")
        
        domain = self.get_domain_from_zone(parent_zone)

        if zone_prefix == "":
            size:int = 12
            chars = string.ascii_lowercase + string.digits
            while zone_prefix == "" or zone_prefix[0] in string.digits:
                zone_prefix = ''.join(random.choices(chars, k=size))

        new_zone = f"{zone_prefix}.{domain}"

        self.guarantee_connectivity()
        try:
            self._db.zones.insert_one({"fqdn": new_zone, "domain": domain, "parent_zone": parent_zone})
            self._db.zones.insert_many([
                {"fqdn": new_zone, "authz.alias": authz["alias"], "authz.authzlevel": authz["authzlevel"]}
                for authz in self._db.zones.find({"fqdn": parent_zone})
            ])
            return new_zone
        except Exception as ex:
            logger.critical(f"Failed to create zone: {ex}")
            return ""

    def update_rule_component(self, rule_id:str, component_id:str, new_parameter:str):
        """Updates a rule component with a new parameter.
        Args:
            rule_id (str): The GUID ID of the rule
            component_id (str): The GUID ID of the component
            new_parameter (str): The new parameter as a string
        """
        self.guarantee_connectivity()
        try:
           result = self._db.rules.update_one(
                {"ruleid": rule_id, "rulecomponents.componentid": component_id},
                {"$set": {"rulecomponents.actionvalue": new_parameter}}
            )
           if result.matched_count == 0:
               logger.warning(f"No matching rule component found for rule_id: {rule_id} and component_id: {component_id}")
        except Exception as ex:
            logger.critical(f"Update rule component failed with exception: {ex}")


    # ------- these are only used for testing, but they are public methods so they can be tested. ----

    def create_domain(self, domain:str) -> str:
        """
        Makes a new domain in the database.
        """
        self.guarantee_connectivity()
        try:
            self._db.domains.insert_one({"domain": domain})
            return domain
        except Exception as ex:
            logger.critical(f"Failed to create domain: {ex}")
            return ""

    def delete_domain(self, domain:str):
        """
        Deletes a domain from the database.
        """
        self.guarantee_connectivity()
        try:
            return self._db.domains.delete_one({"domain": domain})
        except Exception as ex:
            logger.critical(f"Failed to delete domain: {ex}")


