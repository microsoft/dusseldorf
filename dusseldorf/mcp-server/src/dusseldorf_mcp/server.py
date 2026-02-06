# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Dusseldorf MCP Server

This MCP server provides tools for interacting with a Dusseldorf OAST platform,
enabling automated out-of-band security testing workflows.

Supports two transport modes:
- stdio: For local VS Code / Copilot integration (default)
- SSE: For remote server deployment
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Optional
from datetime import datetime
from contextvars import ContextVar

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from .client import DusseldorfClient, Zone, Rule, Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dusseldorf-mcp")


# ============================================================================
# Server Configuration
# ============================================================================

# Configuration via environment variables:
#   DUSSELDORF_API_URL   - Base URL of the Dusseldorf API (required)
#   DUSSELDORF_CLIENT_ID - Azure AD client ID for token acquisition (required for auto-auth in stdio mode)
#   DUSSELDORF_TOKEN     - Bearer token (optional, overrides automatic token acquisition)
#
# SSE mode additional configuration:
#   ENVIRONMENT          - Set to "development" to disable TLS
#   MCP_SSE_PORT         - Port for SSE server (default: 8080)
#   API_TLS_CRT_FILE     - TLS certificate file (required in production)
#   API_TLS_KEY_FILE     - TLS key file (required in production)
#
# Example (stdio mode):
#   export DUSSELDORF_API_URL="https://dusseldorf.example.com"
#   export DUSSELDORF_CLIENT_ID="your-azure-ad-client-id"
#
# Example (SSE mode):
#   export DUSSELDORF_API_URL="https://dusseldorf.example.com"
#   export MCP_SSE_PORT=8080
#   export API_TLS_CRT_FILE="/path/to/cert.pem"
#   export API_TLS_KEY_FILE="/path/to/key.pem"

DUSSELDORF_API_URL = os.environ.get("DUSSELDORF_API_URL", "")
DUSSELDORF_CLIENT_ID = os.environ.get("DUSSELDORF_CLIENT_ID", "")
DUSSELDORF_TOKEN = os.environ.get("DUSSELDORF_TOKEN", "")

# SSE mode configuration
MCP_SSE_PORT = int(os.environ.get("MCP_SSE_PORT", "8080"))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
API_TLS_CRT_FILE = os.environ.get("API_TLS_CRT_FILE", "")
API_TLS_KEY_FILE = os.environ.get("API_TLS_KEY_FILE", "")

# Create the MCP server
server = Server("dusseldorf-mcp")

# Context variable for per-request token (used in SSE mode)
_request_token: ContextVar[Optional[str]] = ContextVar("request_token", default=None)

# Token cache for stdio mode
_cached_token: str | None = None
_token_expires: datetime | None = None


# ============================================================================
# Helper Functions
# ============================================================================

def get_token() -> str:
    """Get a valid token for the current request.
    
    In SSE mode: Returns the token from the request context (passed by client).
    In stdio mode: Returns token from env var or Azure CLI credentials.
    """
    global _cached_token, _token_expires
    
    # Check for per-request token (SSE mode)
    request_token = _request_token.get()
    if request_token:
        return request_token
    
    # If token is provided via environment, use it
    if DUSSELDORF_TOKEN:
        return DUSSELDORF_TOKEN
    
    # Check if cached token is still valid (with 5 min buffer)
    if _cached_token and _token_expires and datetime.now() < _token_expires:
        return _cached_token
    
    # Validate configuration
    if not DUSSELDORF_CLIENT_ID:
        raise ValueError(
            "DUSSELDORF_CLIENT_ID environment variable is not set. "
            "Please set it to your Azure AD application client ID, "
            "or provide DUSSELDORF_TOKEN directly."
        )
    
    # Get a new token using Azure Identity
    try:
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential()
        # Get token for the Dusseldorf app
        token = credential.get_token(f"{DUSSELDORF_CLIENT_ID}/.default")
        _cached_token = token.token
        # Token expires_on is a Unix timestamp
        from datetime import timedelta
        _token_expires = datetime.fromtimestamp(token.expires_on) - timedelta(minutes=5)
        return _cached_token
    except Exception as e:
        raise ValueError(
            f"Failed to get token using Azure CLI. Please run 'az login' first. Error: {e}"
        )


def get_client() -> DusseldorfClient:
    """Get a configured Dusseldorf client"""
    if not DUSSELDORF_API_URL:
        raise ValueError(
            "DUSSELDORF_API_URL environment variable is not set. "
            "Please set it to your Dusseldorf API URL (e.g., https://dusseldorf.example.com)."
        )
    token = get_token()
    return DusseldorfClient(DUSSELDORF_API_URL, token)


def format_zone(zone: Zone) -> str:
    """Format a zone for display"""
    return f"• {zone.fqdn} (domain: {zone.domain})"


def format_rule(rule: Rule) -> str:
    """Format a rule for display"""
    components = []
    for comp in rule.rulecomponents:
        comp_type = "PREDICATE" if comp.ispredicate else "RESULT"
        components.append(f"    - [{comp_type}] {comp.actionname} = {comp.actionvalue}")
    
    comp_str = "\n".join(components) if components else "    (no components)"
    return f"""• Rule: {rule.name}
  ID: {rule.ruleid}
  Zone: {rule.zone}
  Protocol: {rule.networkprotocol}
  Priority: {rule.priority}
  Components:
{comp_str}"""


def format_request(req: Request) -> str:
    """Format a request for display"""
    timestamp = datetime.fromtimestamp(req.time).strftime("%Y-%m-%d %H:%M:%S")
    return f"""• [{req.protocol}] {timestamp}
  FQDN: {req.fqdn}
  Client IP: {req.clientip}
  Request: {req.reqsummary}
  Response: {req.respsummary}"""


# ============================================================================
# Tool Definitions
# ============================================================================

TOOLS = [
    # Zone Management
    Tool(
        name="dusseldorf_list_zones",
        description="List all Dusseldorf zones accessible to the current user. Returns zone FQDNs and their parent domains.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Optional domain filter to list zones only from a specific domain"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="dusseldorf_create_zone",
        description="""Create a new Dusseldorf zone for OAST testing. 
        
A zone is a subdomain that Dusseldorf monitors for incoming requests (DNS, HTTP, HTTPS).
When testing for SSRF or other OOB vulnerabilities, create a zone and use its FQDN as the callback URL.

If no zone_name is provided, a random 12-character name is generated.""",
        inputSchema={
            "type": "object",
            "properties": {
                "zone_name": {
                    "type": "string",
                    "description": "Optional specific zone name (e.g., 'mytest'). If not provided, a random name is generated."
                },
                "domain": {
                    "type": "string",
                    "description": "Optional domain to create the zone in. Uses the default public domain if not specified."
                }
            },
            "required": []
        }
    ),
    Tool(
        name="dusseldorf_delete_zone",
        description="Delete a Dusseldorf zone. The zone must have no rules attached. All captured requests for this zone will also be deleted.",
        inputSchema={
            "type": "object",
            "properties": {
                "fqdn": {
                    "type": "string",
                    "description": "Fully qualified domain name of the zone to delete (e.g., 'mytest.dusseldorf.example.com')"
                }
            },
            "required": ["fqdn"]
        }
    ),
    
    # Rule Management
    Tool(
        name="dusseldorf_list_rules",
        description="List all rules for a specific zone or all accessible zones.",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Optional zone FQDN to filter rules. If not provided, lists rules from all accessible zones."
                }
            },
            "required": []
        }
    ),
    Tool(
        name="dusseldorf_create_rule",
        description="""Create a new rule for a zone. Rules control how Dusseldorf responds to incoming requests.

After creating a rule, add components using dusseldorf_add_rule_component:
- Predicates (conditions): Define when the rule matches
- Results (actions): Define what response to send""",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN to create the rule for"
                },
                "name": {
                    "type": "string",
                    "description": "Human-readable name for the rule"
                },
                "protocol": {
                    "type": "string",
                    "enum": ["DNS", "HTTP", "HTTPS"],
                    "description": "Network protocol this rule applies to"
                },
                "priority": {
                    "type": "integer",
                    "description": "Rule priority (1-1000, lower = higher priority). Default is 100.",
                    "default": 100
                }
            },
            "required": ["zone", "name", "protocol"]
        }
    ),
    Tool(
        name="dusseldorf_add_rule_component",
        description="""Add a predicate (condition) or result (action) to a rule.

PREDICATES (is_predicate=true) - Conditions that must match:
• dns.type: Match DNS record type (A, AAAA, CNAME, TXT, MX, etc.)
• http.method: Match HTTP method (GET, POST, PUT, DELETE, etc.)
• http.tls: Match TLS status ("true" or "false")
• http.path: Match URL path (e.g., "/api/callback")
• http.header: Match specific header value
• http.body: Match request body content

RESULTS (is_predicate=false) - Response actions:
• dns.type: Set DNS response record type
• dns.data: Set DNS response data (IP address, domain, etc.)
• http.code: Set HTTP status code (e.g., "200", "404", "500")
• http.header: Add a response header (format: "Header-Name: value")
• http.headers: Set multiple headers as JSON object
• http.body: Set response body content
• http.passthru: Proxy request to another URL""",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN the rule belongs to"
                },
                "rule_id": {
                    "type": "string",
                    "description": "UUID of the rule to add the component to"
                },
                "is_predicate": {
                    "type": "boolean",
                    "description": "True for predicate (condition), False for result (action)"
                },
                "action_name": {
                    "type": "string",
                    "description": "Name of the action (see tool description for valid values)"
                },
                "action_value": {
                    "type": "string",
                    "description": "Value for the action"
                }
            },
            "required": ["zone", "rule_id", "is_predicate", "action_name", "action_value"]
        }
    ),
    Tool(
        name="dusseldorf_delete_rule",
        description="Delete a rule from a zone.",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN the rule belongs to"
                },
                "rule_id": {
                    "type": "string",
                    "description": "UUID of the rule to delete"
                }
            },
            "required": ["zone", "rule_id"]
        }
    ),
    
    # Request Viewing
    Tool(
        name="dusseldorf_get_requests",
        description="""Get captured requests for a zone. Use this to check if an SSRF or other OOB vulnerability was triggered.

Returns the most recent requests first, including:
- Protocol (DNS, HTTP, HTTPS)
- Timestamp
- Client IP (the IP that made the request)
- Request summary (what was requested)
- Response summary (what Dusseldorf returned)""",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN to get requests for"
                },
                "protocols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of protocols to filter (DNS, HTTP, HTTPS)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of requests to return (default 20, max 100)",
                    "default": 20
                }
            },
            "required": ["zone"]
        }
    ),
    Tool(
        name="dusseldorf_get_request_details",
        description="Get full details of a specific captured request, including complete request and response data.",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN the request was made to"
                },
                "timestamp": {
                    "type": "integer",
                    "description": "Unix timestamp of the request"
                }
            },
            "required": ["zone", "timestamp"]
        }
    ),
    
    # Payload Generation
    Tool(
        name="dusseldorf_generate_payload",
        description="""Generate callback URLs and payloads for OAST testing.

Returns ready-to-use payloads for:
- HTTP/HTTPS callback URLs
- DNS resolution payloads
- Common SSRF test payloads
- XXE payloads with external entity references""",
        inputSchema={
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone FQDN to generate payloads for"
                },
                "payload_type": {
                    "type": "string",
                    "enum": ["url", "dns", "ssrf", "xxe", "all"],
                    "description": "Type of payload to generate",
                    "default": "all"
                },
                "identifier": {
                    "type": "string",
                    "description": "Optional unique identifier to include in the payload for tracking (e.g., 'test1', 'param-vuln')"
                }
            },
            "required": ["zone"]
        }
    ),
    
    # HTTP Trigger
    Tool(
        name="dusseldorf_trigger_http",
        description="""Make an HTTP request to trigger potential SSRF/OOB vulnerabilities.

Use this to send requests to target applications that may be vulnerable.
The request can include custom headers, body, and method.

NOTE: This makes actual HTTP requests. Use responsibly and only against authorized targets.""",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target URL to send the request to"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "description": "HTTP method to use",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "Optional headers to include in the request"
                },
                "body": {
                    "type": "string",
                    "description": "Optional request body"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds (default 10)",
                    "default": 10
                },
                "follow_redirects": {
                    "type": "boolean",
                    "description": "Whether to follow redirects (default true)",
                    "default": True
                },
                "verify_ssl": {
                    "type": "boolean",
                    "description": "Whether to verify SSL certificates (default true)",
                    "default": True
                }
            },
            "required": ["url"]
        }
    ),
    
    # Connectivity Check
    Tool(
        name="dusseldorf_ping",
        description="Check connectivity to the Dusseldorf API and verify authentication. Returns the current user and build version.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
]


# ============================================================================
# Tool Handlers
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools"""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        result = await _handle_tool(name, arguments)
        return CallToolResult(content=[TextContent(type="text", text=result)])
    except Exception as e:
        error_msg = f"Error: {type(e).__name__}: {str(e)}"
        return CallToolResult(content=[TextContent(type="text", text=error_msg)], isError=True)


async def _handle_tool(name: str, arguments: dict) -> str:
    """Route tool calls to appropriate handlers"""
    
    # Zone Management
    if name == "dusseldorf_list_zones":
        return await handle_list_zones(arguments)
    elif name == "dusseldorf_create_zone":
        return await handle_create_zone(arguments)
    elif name == "dusseldorf_delete_zone":
        return await handle_delete_zone(arguments)
    
    # Rule Management
    elif name == "dusseldorf_list_rules":
        return await handle_list_rules(arguments)
    elif name == "dusseldorf_create_rule":
        return await handle_create_rule(arguments)
    elif name == "dusseldorf_add_rule_component":
        return await handle_add_rule_component(arguments)
    elif name == "dusseldorf_delete_rule":
        return await handle_delete_rule(arguments)
    
    # Request Viewing
    elif name == "dusseldorf_get_requests":
        return await handle_get_requests(arguments)
    elif name == "dusseldorf_get_request_details":
        return await handle_get_request_details(arguments)
    
    # Payload Generation
    elif name == "dusseldorf_generate_payload":
        return await handle_generate_payload(arguments)
    
    # HTTP Trigger
    elif name == "dusseldorf_trigger_http":
        return await handle_trigger_http(arguments)
    
    # Connectivity
    elif name == "dusseldorf_ping":
        return await handle_ping(arguments)
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# ============================================================================
# Handler Implementations
# ============================================================================

async def handle_list_zones(arguments: dict) -> str:
    """Handle dusseldorf_list_zones"""
    client = get_client()
    try:
        zones = await client.list_zones(domain=arguments.get("domain"))
        if not zones:
            return "No zones found."
        
        result = f"Found {len(zones)} zone(s):\n\n"
        result += "\n".join(format_zone(z) for z in zones)
        return result
    finally:
        await client.close()


async def handle_create_zone(arguments: dict) -> str:
    """Handle dusseldorf_create_zone"""
    client = get_client()
    try:
        zones = await client.create_zone(
            zone_name=arguments.get("zone_name"),
            domain=arguments.get("domain")
        )
        
        if len(zones) == 1:
            zone = zones[0]
            return f"""✓ Zone created successfully!

FQDN: {zone.fqdn}
Domain: {zone.domain}

Callback URLs:
• HTTP:  http://{zone.fqdn}/
• HTTPS: https://{zone.fqdn}/
• DNS:   Any DNS query to *.{zone.fqdn} or {zone.fqdn}

Use dusseldorf_get_requests to check for incoming connections."""
        else:
            result = f"✓ Created {len(zones)} zone(s):\n\n"
            result += "\n".join(format_zone(z) for z in zones)
            return result
    finally:
        await client.close()


async def handle_delete_zone(arguments: dict) -> str:
    """Handle dusseldorf_delete_zone"""
    client = get_client()
    try:
        await client.delete_zone(arguments["fqdn"])
        return f"✓ Zone '{arguments['fqdn']}' deleted successfully."
    finally:
        await client.close()


async def handle_list_rules(arguments: dict) -> str:
    """Handle dusseldorf_list_rules"""
    client = get_client()
    try:
        rules = await client.list_rules(zone=arguments.get("zone"))
        if not rules:
            return "No rules found."
        
        result = f"Found {len(rules)} rule(s):\n\n"
        result += "\n\n".join(format_rule(r) for r in rules)
        return result
    finally:
        await client.close()


async def handle_create_rule(arguments: dict) -> str:
    """Handle dusseldorf_create_rule"""
    client = get_client()
    try:
        rule = await client.create_rule(
            zone=arguments["zone"],
            name=arguments["name"],
            network_protocol=arguments["protocol"],
            priority=arguments.get("priority", 100)
        )
        
        return f"""✓ Rule created successfully!

{format_rule(rule)}

Next steps:
1. Add predicates (conditions) with dusseldorf_add_rule_component (is_predicate=true)
2. Add results (actions) with dusseldorf_add_rule_component (is_predicate=false)"""
    finally:
        await client.close()


async def handle_add_rule_component(arguments: dict) -> str:
    """Handle dusseldorf_add_rule_component"""
    client = get_client()
    try:
        component = await client.add_rule_component(
            zone=arguments["zone"],
            rule_id=arguments["rule_id"],
            is_predicate=arguments["is_predicate"],
            action_name=arguments["action_name"],
            action_value=arguments["action_value"]
        )
        
        comp_type = "Predicate" if component.ispredicate else "Result"
        return f"""✓ {comp_type} added successfully!

Component ID: {component.componentid}
Action: {component.actionname} = {component.actionvalue}"""
    finally:
        await client.close()


async def handle_delete_rule(arguments: dict) -> str:
    """Handle dusseldorf_delete_rule"""
    client = get_client()
    try:
        await client.delete_rule(arguments["zone"], arguments["rule_id"])
        return f"✓ Rule '{arguments['rule_id']}' deleted from zone '{arguments['zone']}'."
    finally:
        await client.close()


async def handle_get_requests(arguments: dict) -> str:
    """Handle dusseldorf_get_requests"""
    client = get_client()
    try:
        requests = await client.get_requests(
            zone=arguments["zone"],
            protocols=arguments.get("protocols"),
            limit=min(arguments.get("limit", 20), 100)
        )
        
        if not requests:
            return f"No requests captured for zone '{arguments['zone']}' yet.\n\nWaiting for incoming connections..."
        
        result = f"Found {len(requests)} request(s) for zone '{arguments['zone']}':\n\n"
        result += "\n\n".join(format_request(r) for r in requests)
        return result
    finally:
        await client.close()


async def handle_get_request_details(arguments: dict) -> str:
    """Handle dusseldorf_get_request_details"""
    client = get_client()
    try:
        req = await client.get_request(arguments["zone"], arguments["timestamp"])
        
        timestamp = datetime.fromtimestamp(req.time).strftime("%Y-%m-%d %H:%M:%S")
        return f"""Request Details:

Zone: {req.zone}
FQDN: {req.fqdn}
Protocol: {req.protocol}
Time: {timestamp} (Unix: {req.time})
Client IP: {req.clientip}

Request Data:
{json.dumps(req.request, indent=2)}

Response Data:
{json.dumps(req.response, indent=2)}"""
    finally:
        await client.close()


async def handle_generate_payload(arguments: dict) -> str:
    """Handle dusseldorf_generate_payload"""
    zone = arguments["zone"]
    payload_type = arguments.get("payload_type", "all")
    identifier = arguments.get("identifier", "")
    
    # Build subdomain with optional identifier
    if identifier:
        subdomain = f"{identifier}.{zone}"
    else:
        subdomain = zone
    
    payloads = {}
    
    if payload_type in ("url", "all"):
        payloads["HTTP/HTTPS URLs"] = [
            f"http://{subdomain}/",
            f"https://{subdomain}/",
            f"http://{subdomain}/callback",
            f"https://{subdomain}/api/webhook",
        ]
    
    if payload_type in ("dns", "all"):
        payloads["DNS Payloads"] = [
            subdomain,
            f"dns.{subdomain}",
            f"resolve.{subdomain}",
        ]
    
    if payload_type in ("ssrf", "all"):
        payloads["SSRF Test Payloads"] = [
            f"http://{subdomain}/",
            f"https://{subdomain}/",
            f"///{subdomain}/",
            f"http://{subdomain}:80/",
            f"http://{subdomain}:443/",
            f"http://{subdomain}#",
            f"http://{subdomain}?",
            f"http://foo@{subdomain}/",
            f"http://{subdomain}%00.example.com/",
            f"http://{subdomain}%2f%2f",
        ]
    
    if payload_type in ("xxe", "all"):
        payloads["XXE Payloads"] = [
            f'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://{subdomain}/xxe">]>',
            f'<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://{subdomain}/xxe.dtd"> %xxe;]>',
            f'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "https://{subdomain}/xxe">]>',
        ]
    
    # Format output
    result = f"Generated payloads for zone: {zone}\n"
    if identifier:
        result += f"Identifier: {identifier}\n"
    result += "\n"
    
    for category, items in payloads.items():
        result += f"=== {category} ===\n"
        for item in items:
            result += f"  {item}\n"
        result += "\n"
    
    result += "Use dusseldorf_get_requests to check for incoming connections."
    return result


async def handle_trigger_http(arguments: dict) -> str:
    """Handle dusseldorf_trigger_http"""
    import httpx
    
    url = arguments["url"]
    method = arguments.get("method", "GET")
    headers = arguments.get("headers", {})
    body = arguments.get("body")
    timeout = arguments.get("timeout", 10)
    follow_redirects = arguments.get("follow_redirects", True)
    verify_ssl = arguments.get("verify_ssl", True)
    
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=verify_ssl
        ) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            
            # Format response headers
            resp_headers = "\n".join(f"  {k}: {v}" for k, v in response.headers.items())
            
            # Truncate body if too long
            body_text = response.text
            if len(body_text) > 2000:
                body_text = body_text[:2000] + f"\n... (truncated, {len(response.text)} total chars)"
            
            return f"""HTTP Request sent successfully!

Request:
  {method} {url}
  Headers: {json.dumps(headers) if headers else "(none)"}
  Body: {body[:200] + '...' if body and len(body) > 200 else body or "(none)"}

Response:
  Status: {response.status_code} {response.reason_phrase}
  Headers:
{resp_headers}

  Body:
{body_text}"""
            
    except httpx.TimeoutException:
        return f"Request timed out after {timeout} seconds."
    except httpx.ConnectError as e:
        return f"Connection error: {str(e)}"
    except Exception as e:
        return f"Request failed: {type(e).__name__}: {str(e)}"


async def handle_ping(arguments: dict) -> str:
    """Handle dusseldorf_ping"""
    client = get_client()
    try:
        result = await client.ping()
        return f"""✓ Connected to Dusseldorf API

API URL: {DUSSELDORF_API_URL}
User: {result.get('user', 'unknown')}
Build: {result.get('build', 'unknown')}
Timestamp: {result.get('pong', 'unknown')}"""
    finally:
        await client.close()


# ============================================================================
# Main Entry Points
# ============================================================================

def main():
    """Main entry point for stdio mode (default)"""
    asyncio.run(run_server_stdio())


def main_sse():
    """Main entry point for SSE mode"""
    run_server_sse()


async def run_server_stdio():
    """Run the MCP server in stdio mode (for VS Code / Copilot)"""
    logger.info("Starting Dusseldorf MCP server in stdio mode")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run_server_sse():
    """Run the MCP server in SSE mode (for remote deployment)"""
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import JSONResponse
    from mcp.server.sse import SseServerTransport
    
    # Validate configuration
    if not DUSSELDORF_API_URL:
        logger.error("DUSSELDORF_API_URL environment variable is not set")
        sys.exit(1)
    
    if ENVIRONMENT != "development":
        if not API_TLS_CRT_FILE:
            logger.error("API_TLS_CRT_FILE not found in environment variables")
            sys.exit(1)
        if not API_TLS_KEY_FILE:
            logger.error("API_TLS_KEY_FILE not found in environment variables")
            sys.exit(1)
    
    # Create SSE transport
    sse_transport = SseServerTransport("/messages")
    
    async def handle_sse(request):
        """Handle SSE connection requests"""
        # Extract Bearer token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or invalid Authorization header. Expected: Bearer <token>"},
                status_code=401
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Set the token in context for this connection
        token_ctx = _request_token.set(token)
        
        try:
            async with sse_transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    server.create_initialization_options()
                )
        finally:
            _request_token.reset(token_ctx)
    
    async def handle_messages(request):
        """Handle POST messages for SSE transport"""
        # Extract Bearer token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or invalid Authorization header. Expected: Bearer <token>"},
                status_code=401
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Set the token in context for this request
        token_ctx = _request_token.set(token)
        
        try:
            return await sse_transport.handle_post_message(request.scope, request.receive, request._send)
        finally:
            _request_token.reset(token_ctx)
    
    async def health_check(request):
        """Health check endpoint"""
        return JSONResponse({"status": "healthy", "service": "dusseldorf-mcp"})
    
    # Create Starlette app
    app = Starlette(
        debug=(ENVIRONMENT == "development"),
        routes=[
            Route("/health", endpoint=health_check, methods=["GET"]),
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )
    
    # Run with uvicorn
    logger.info(f"Starting Dusseldorf MCP server in SSE mode on port {MCP_SSE_PORT}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Dusseldorf API URL: {DUSSELDORF_API_URL}")
    
    if ENVIRONMENT == "development":
        logger.info("TLS disabled (development mode)")
        uvicorn.run(app, host="0.0.0.0", port=MCP_SSE_PORT)
    else:
        logger.info(f"TLS enabled with cert: {API_TLS_CRT_FILE}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=MCP_SSE_PORT,
            ssl_keyfile=API_TLS_KEY_FILE,
            ssl_certfile=API_TLS_CRT_FILE
        )


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dusseldorf MCP Server")
    parser.add_argument(
        "--sse", 
        action="store_true", 
        help="Run in SSE mode for remote deployment (default: stdio mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"Port for SSE server (default: {MCP_SSE_PORT}, set via MCP_SSE_PORT env var)"
    )
    args = parser.parse_args()
    
    if args.port:
        MCP_SSE_PORT = args.port
    
    if args.sse:
        main_sse()
    else:
        main()
