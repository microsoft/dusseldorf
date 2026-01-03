# Dusseldorf MCP Server

An MCP (Model Context Protocol) server that enables AI assistants to interact with a [Dusseldorf](https://aka.ms/dusseldorf) OAST (Out-of-Band Application Security Testing) platform.

## Overview

This MCP server allows AI assistants like GitHub Copilot to:

- **Create and manage zones** - Set up callback endpoints for OAST testing
- **Configure custom responses** - Define rules for DNS/HTTP responses
- **Monitor captured requests** - Check if vulnerabilities were triggered
- **Generate payloads** - Create ready-to-use SSRF, XXE, and other test payloads
- **Trigger HTTP requests** - Send requests to test for vulnerabilities

## Installation

### Prerequisites

- Python 3.10 or higher
- Access to a Dusseldorf instance
- A valid authentication token

### Install from source

```bash
cd mcp-server
pip install -e .
```

### Install dependencies only

```bash
pip install mcp httpx pydantic azure-identity
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DUSSELDORF_API_URL` | Base URL of the Dusseldorf API | Yes |
| `DUSSELDORF_CLIENT_ID` | Azure AD application client ID for automatic token acquisition | Yes (unless using `DUSSELDORF_TOKEN`) |
| `DUSSELDORF_TOKEN` | Bearer token for authentication (overrides automatic token) | No |

### Option 1: Automatic Token Acquisition (Recommended)

The MCP server can automatically acquire tokens using your Azure CLI credentials:

```bash
# Set the required environment variables
export DUSSELDORF_API_URL="https://your-dusseldorf-instance.example.com"
export DUSSELDORF_CLIENT_ID="your-azure-ad-app-client-id"

# Ensure you're logged in to Azure CLI
az login
```

### Option 2: Manual Token

If you prefer to manage tokens manually:

```bash
export DUSSELDORF_API_URL="https://your-dusseldorf-instance.example.com"
export DUSSELDORF_TOKEN=$(az account get-access-token --resource=<client-id> --query accessToken -o tsv)
```

## VS Code / Copilot Integration

Add the following to your `.vscode/mcp.json`:

```json
{
  "servers": {
    "dusseldorf": {
      "type": "stdio",
      "command": "${workspaceFolder}/mcp-server/.venv/Scripts/python.exe",
      "args": ["-m", "dusseldorf_mcp.server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/mcp-server/src",
        "DUSSELDORF_API_URL": "${env:DUSSELDORF_API_URL}",
        "DUSSELDORF_CLIENT_ID": "${env:DUSSELDORF_CLIENT_ID}",
        "DUSSELDORF_TOKEN": "${env:DUSSELDORF_TOKEN}"
      }
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcp": {
    "servers": {
      "dusseldorf": {
        "command": "dusseldorf-mcp",
        "env": {
          "DUSSELDORF_API_URL": "https://dusseldorf.security.azure",
          "DUSSELDORF_TOKEN": "your-token-here"
        }
      }
    }
  }
}
```

## Available Tools

### Zone Management

| Tool | Description |
|------|-------------|
| `dusseldorf_list_zones` | List all accessible zones |
| `dusseldorf_create_zone` | Create a new zone for testing |
| `dusseldorf_delete_zone` | Delete a zone |

### Rule Management

| Tool | Description |
|------|-------------|
| `dusseldorf_list_rules` | List rules for a zone |
| `dusseldorf_create_rule` | Create a new rule |
| `dusseldorf_add_rule_component` | Add a predicate or result to a rule |
| `dusseldorf_delete_rule` | Delete a rule |

### Request Monitoring

| Tool | Description |
|------|-------------|
| `dusseldorf_get_requests` | Get captured requests for a zone |
| `dusseldorf_get_request_details` | Get full details of a specific request |

### Payload Generation & Testing

| Tool | Description |
|------|-------------|
| `dusseldorf_generate_payload` | Generate SSRF/XXE/DNS test payloads |
| `dusseldorf_trigger_http` | Make HTTP requests to trigger vulnerabilities |

### Utility

| Tool | Description |
|------|-------------|
| `dusseldorf_ping` | Check API connectivity and authentication |

## Example Workflow: SSRF Testing

Here's how an AI assistant might use these tools to test for SSRF:

1. **Create a zone** for callback monitoring:
   ```
   dusseldorf_create_zone()
   → Creates zone: abc123xyz.dusseldorf.example.com
   ```

2. **Generate payloads** for the zone:
   ```
   dusseldorf_generate_payload(zone="abc123xyz.dusseldorf.example.com", payload_type="ssrf")
   → Returns various SSRF test URLs
   ```

3. **Configure a custom response** (optional):
   ```
   dusseldorf_create_rule(zone="...", name="Custom 200", protocol="HTTP")
   dusseldorf_add_rule_component(zone="...", rule_id="...", is_predicate=false, action_name="http.code", action_value="200")
   ```

4. **Trigger the vulnerability**:
   ```
   dusseldorf_trigger_http(url="https://target.com/api?url=http://abc123xyz.dusseldorf.example.com/")
   ```

5. **Check for callbacks**:
   ```
   dusseldorf_get_requests(zone="abc123xyz.dusseldorf.example.com")
   → Shows if the target made a request to our zone
   ```

6. **Cleanup**:
   ```
   dusseldorf_delete_zone(fqdn="abc123xyz.dusseldorf.example.com")
   ```

## Rule Components Reference

### Predicates (Conditions)

| Action Name | Description | Example Value |
|-------------|-------------|---------------|
| `dns.type` | Match DNS record type | `A`, `AAAA`, `TXT` |
| `http.method` | Match HTTP method | `GET`, `POST` |
| `http.tls` | Match TLS status | `true`, `false` |
| `http.path` | Match URL path | `/api/callback` |
| `http.header` | Match header value | `User-Agent: curl` |
| `http.body` | Match request body | `{"key": "value"}` |

### Results (Actions)

| Action Name | Description | Example Value |
|-------------|-------------|---------------|
| `dns.type` | Set DNS response type | `A`, `TXT` |
| `dns.data` | Set DNS response data | `127.0.0.1` |
| `http.code` | Set HTTP status code | `200`, `404` |
| `http.header` | Add response header | `X-Custom: value` |
| `http.headers` | Set multiple headers | `{"X-A": "1", "X-B": "2"}` |
| `http.body` | Set response body | `{"status": "ok"}` |
| `http.passthru` | Proxy to another URL | `https://example.com` |

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Running the Server Directly

```bash
export DUSSELDORF_TOKEN="your-token"
python -m dusseldorf_mcp.server
```

## License

MIT License - Copyright (c) Microsoft Corporation
