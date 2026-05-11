# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Dusseldorf API Client

This module provides a typed client for interacting with the Dusseldorf REST API.
"""

import httpx
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# ============================================================================
# Models
# ============================================================================

class Zone(BaseModel):
    """Represents a Dusseldorf zone"""
    fqdn: str
    domain: str


class RuleComponent(BaseModel):
    """Represents a component of a rule (predicate or result)"""
    componentid: Optional[str] = None
    ispredicate: bool
    actionname: str
    actionvalue: str


class Rule(BaseModel):
    """Represents a Dusseldorf rule"""
    ruleid: Optional[str] = None
    zone: str
    name: str
    networkprotocol: str
    priority: int
    rulecomponents: list[RuleComponent] = []


class Request(BaseModel):
    """Represents a captured network request"""
    zone: str
    time: int
    fqdn: str
    protocol: str
    clientip: str
    request: dict
    response: dict
    reqsummary: str
    respsummary: str

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.time)


# ============================================================================
# API Client
# ============================================================================

class DusseldorfClient:
    """
    Client for the Dusseldorf OAST API.
    
    This client wraps the Dusseldorf REST API and provides typed methods
    for zone, rule, and request management.
    """

    def __init__(self, base_url: str, token: str):
        """
        Initialize the Dusseldorf client.
        
        Args:
            base_url: The base URL of the Dusseldorf API (e.g., https://dusseldorf.security.azure)
            token: Bearer token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.token = token
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    # ========================================================================
    # Zone Management
    # ========================================================================

    async def list_zones(self, domain: Optional[str] = None) -> list[Zone]:
        """
        List all zones accessible to the current user.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of Zone objects
        """
        params = {}
        if domain:
            params["domain"] = domain
            
        response = await self._client.get(f"{self.api_url}/zones", params=params)
        response.raise_for_status()
        return [Zone(**z) for z in response.json()]

    async def get_zone(self, fqdn: str) -> Zone:
        """
        Get details of a specific zone.
        
        Args:
            fqdn: Fully qualified domain name of the zone
            
        Returns:
            Zone object
        """
        response = await self._client.get(f"{self.api_url}/zones/{fqdn}")
        response.raise_for_status()
        return Zone(**response.json())

    async def create_zone(
        self, 
        zone_name: Optional[str] = None, 
        domain: Optional[str] = None,
        num: int = 1
    ) -> list[Zone]:
        """
        Create one or more zones.
        
        Args:
            zone_name: Optional specific zone name (if not provided, random name is generated)
            domain: Optional domain to create the zone in
            num: Number of zones to create (only used if zone_name is not provided)
            
        Returns:
            List of created Zone objects
        """
        payload = {"num": num}
        if zone_name:
            payload["zone"] = zone_name
            payload["num"] = 1
        if domain:
            payload["domain"] = domain
            
        response = await self._client.post(f"{self.api_url}/zones", json=payload)
        response.raise_for_status()
        return [Zone(**z) for z in response.json()]

    async def delete_zone(self, fqdn: str) -> dict:
        """
        Delete a zone.
        
        Args:
            fqdn: Fully qualified domain name of the zone
            
        Returns:
            Status response
        """
        response = await self._client.delete(f"{self.api_url}/zones/{fqdn}")
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # Rule Management
    # ========================================================================

    async def list_rules(self, zone: Optional[str] = None) -> list[Rule]:
        """
        List rules, optionally filtered by zone.
        
        Args:
            zone: Optional zone to filter by
            
        Returns:
            List of Rule objects
        """
        if zone:
            response = await self._client.get(f"{self.api_url}/rules/{zone}")
        else:
            response = await self._client.get(f"{self.api_url}/rules")
        
        # 404 means no rules found, return empty list
        if response.status_code == 404:
            return []
            
        response.raise_for_status()
        return [Rule(**r) for r in response.json()]

    async def get_rule(self, zone: str, rule_id: str) -> Rule:
        """
        Get a specific rule.
        
        Args:
            zone: Zone the rule belongs to
            rule_id: UUID of the rule
            
        Returns:
            Rule object
        """
        response = await self._client.get(f"{self.api_url}/rules/{zone}/{rule_id}")
        response.raise_for_status()
        return Rule(**response.json())

    async def create_rule(
        self,
        zone: str,
        name: str,
        network_protocol: str,
        priority: int = 100
    ) -> Rule:
        """
        Create a new rule.
        
        Args:
            zone: Zone to create the rule for
            name: Name of the rule
            network_protocol: Protocol (DNS, HTTP, HTTPS)
            priority: Rule priority (1-1000, lower = higher priority)
            
        Returns:
            Created Rule object
        """
        payload = {
            "zone": zone,
            "name": name,
            "networkprotocol": network_protocol.lower(),
            "priority": priority
        }
        response = await self._client.post(f"{self.api_url}/rules", json=payload)
        response.raise_for_status()
        return Rule(**response.json())

    async def delete_rule(self, zone: str, rule_id: str) -> dict:
        """
        Delete a rule.
        
        Args:
            zone: Zone the rule belongs to
            rule_id: UUID of the rule
            
        Returns:
            Status response
        """
        response = await self._client.delete(f"{self.api_url}/rules/{zone}/{rule_id}")
        response.raise_for_status()
        return response.json()

    async def add_rule_component(
        self,
        zone: str,
        rule_id: str,
        is_predicate: bool,
        action_name: str,
        action_value: str
    ) -> RuleComponent:
        """
        Add a component (predicate or result) to a rule.
        
        Predicates (conditions):
            - dns.type: Match DNS record type (A, AAAA, CNAME, TXT, etc.)
            - http.method: Match HTTP method (GET, POST, etc.)
            - http.tls: Match TLS status (true/false)
            - http.path: Match URL path
            - http.header: Match specific header
            - http.headers.keys: Match header keys
            - http.headers.values: Match header values
            - http.headers.regexes: Match headers with regex
            - http.body: Match request body
            
        Results (actions):
            - dns.data: Set DNS response data
            - dns.type: Set DNS response type
            - http.code: Set HTTP status code
            - http.header: Add single header
            - http.headers: Set multiple headers (JSON)
            - http.body: Set response body
            - http.passthru: Proxy to another URL
            
        Args:
            zone: Zone the rule belongs to
            rule_id: UUID of the rule
            is_predicate: True for predicate (condition), False for result (action)
            action_name: Name of the action
            action_value: Value for the action
            
        Returns:
            Created RuleComponent object
        """
        payload = {
            "ispredicate": is_predicate,
            "actionname": action_name,
            "actionvalue": action_value
        }
        response = await self._client.post(
            f"{self.api_url}/rules/{zone}/{rule_id}/components",
            json=payload
        )
        response.raise_for_status()
        return RuleComponent(**response.json())

    async def delete_rule_component(
        self,
        zone: str,
        rule_id: str,
        component_id: str
    ) -> dict:
        """
        Delete a rule component.
        
        Args:
            zone: Zone the rule belongs to
            rule_id: UUID of the rule
            component_id: UUID of the component
            
        Returns:
            Status response
        """
        response = await self._client.delete(
            f"{self.api_url}/rules/{zone}/{rule_id}/components/{component_id}"
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # Request Viewing
    # ========================================================================

    async def get_requests(
        self,
        zone: str,
        protocols: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Request]:
        """
        Get captured requests for a zone.
        
        Args:
            zone: Zone to get requests for
            protocols: Optional list of protocols to filter (DNS, HTTP, HTTPS)
            skip: Number of requests to skip (for pagination)
            limit: Maximum number of requests to return
            
        Returns:
            List of Request objects
        """
        params = {"skip": skip, "limit": limit}
        if protocols:
            params["protocols"] = ",".join(protocols)
            
        response = await self._client.get(
            f"{self.api_url}/requests/{zone}",
            params=params
        )
        response.raise_for_status()
        return [Request(**r) for r in response.json()]

    async def get_request(self, zone: str, timestamp: int) -> Request:
        """
        Get a specific request by timestamp.
        
        Args:
            zone: Zone the request was made to
            timestamp: Unix timestamp of the request
            
        Returns:
            Request object
        """
        response = await self._client.get(
            f"{self.api_url}/requests/{zone}/{timestamp}"
        )
        response.raise_for_status()
        return Request(**response.json())

    # ========================================================================
    # Utility Methods
    # ========================================================================

    async def ping(self) -> dict:
        """
        Ping the API to check connectivity and authentication.
        
        Returns:
            Ping response with user info and build version
        """
        response = await self._client.get(f"{self.api_url}/ping")
        response.raise_for_status()
        return response.json()
