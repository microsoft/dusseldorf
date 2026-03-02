# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF CLI

# This module allows users to manage zones and view requests, configure settings.
# Config is stored locally in a JSON file, and the CLI supports both direct token
# input and through calling the az CLI.

# For any help: aka.ms/dusseldorf or open an issue in the GitHub repo.

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from typing import Optional

import typer

from .api_client import ApiClient
from .config_store import CliConfig, load_config, save_config


app = typer.Typer(help="Dusseldorf CLI", no_args_is_help=True, add_completion=False)
config_app = typer.Typer(help="Manage local CLI settings")
app.add_typer(config_app, name="config")


def _effective_token(config: CliConfig) -> str:
    env_token = os.getenv("DSSLDRF_AUTH_TOKEN", "").strip()
    return env_token or config.auth_token


def _config_exists() -> bool:
    return os.path.exists(os.path.expanduser("~/.dssldrf/config.json"))


def _require_config() -> None:
    if not _config_exists():
        raise typer.BadParameter("No config found. Run: dssldrf init")


def _api_client() -> ApiClient:
    _require_config()
    config = load_config()
    token = _effective_token(config)
    if not token:
        raise typer.BadParameter(
            "Missing token. Set DSSLDRF_AUTH_TOKEN or run: dssldrf login"
        )
    return ApiClient(api_url=config.api_url, token=token)


def _handle_api_error(error: RuntimeError) -> None:
    message = str(error)
    if message.startswith("API 401"):
        typer.echo(
            "Authentication failed (401). Run: dssldrf login to refresh your token.",
            err=True,
        )
    else:
        typer.echo(message, err=True)
    raise typer.Exit(1)


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _prompt_required(label: str, default_value: str) -> str:
    value = typer.prompt(label, default=default_value or "")
    if not value.strip():
        raise typer.BadParameter(f"Missing value for {label}.")
    return value.strip()


def _install_completion() -> None:
    try:
        from typer.main import install_completion
    except Exception:
        return

    try:
        install_completion(app)
    except Exception:
        return


def _format_timestamp(timestamp: str | int, human: bool) -> str:
    """Format timestamp as Unix or human-readable."""
    if not human or not timestamp:
        return str(timestamp)
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%m:%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(timestamp)


def _format_request_summary(item: dict, human: bool) -> None:
    """Display summary info for a request (used with --details)."""
    timestamp = item.get("time", "")
    protocol = item.get("protocol", "")
    client_ip = item.get("clientip", "")
    formatted_time = _format_timestamp(timestamp, human)

    # Basic info
    typer.echo(f"{formatted_time} {protocol} {client_ip}")

    # Request object
    request_data = item.get("request", {})
    if isinstance(request_data, dict):
        if protocol.upper() == "HTTP":
            method = request_data.get("method", "")
            path = request_data.get("path", "")
            if method or path:
                typer.echo(f"  → {method} {path}")
            headers = request_data.get("headers", {})
            if headers:
                for key, val in list(headers.items())[:3]:  # Show first 3 headers
                    typer.echo(f"    {key}: {val}")
                if len(headers) > 3:
                    typer.echo(f"    ... and {len(headers) - 3} more headers")
            body = request_data.get("body", "")
            if body:
                preview = str(body)[:100]
                suffix = " ..." if len(str(body)) > 100 else ""
                typer.echo(f"    Body: {preview}{suffix}")

    # Response object
    response_data = item.get("response", {})
    if isinstance(response_data, dict):
        if protocol.upper() == "HTTP":
            status = response_data.get("status", "")
            if status:
                typer.echo(f"  ← {status}")


def _format_request_detail(item: dict, human: bool) -> None:
    """Display full details for a single request."""
    timestamp = item.get("time", "")
    protocol = item.get("protocol", "").upper()
    client_ip = item.get("clientip", "")
    zone = item.get("zone", "")
    fqdn = item.get("fqdn", "")
    formatted_time = _format_timestamp(timestamp, human)

    typer.echo(f"\n{'='*60}")
    typer.echo(f"Request: {formatted_time}")
    typer.echo(f"Zone: {zone or fqdn}")
    typer.echo(f"Protocol: {protocol}")
    typer.echo(f"Client IP: {client_ip}")
    typer.echo(f"{'='*60}\n")

    # Request details
    request_data = item.get("request", {})
    if isinstance(request_data, dict):
        typer.echo("REQUEST:")
        if protocol == "HTTP":
            method = request_data.get("method", "N/A")
            path = request_data.get("path", "N/A")
            tls = request_data.get("tls", False)
            typer.echo(f"  Method: {method}")
            typer.echo(f"  Path: {path}")
            if tls:
                typer.echo(f"  TLS: Yes")
            headers = request_data.get("headers", {})
            if headers:
                typer.echo(f"  Headers:")
                for key, val in headers.items():
                    typer.echo(f"    {key}: {val}")
            body = request_data.get("body", "")
            if body:
                typer.echo(f"  Body: {body}")
        elif protocol == "DNS":
            query = request_data.get("query", "N/A")
            qtype = request_data.get("type", "N/A")
            typer.echo(f"  Query: {query}")
            typer.echo(f"  Type: {qtype}")

    # Response details
    response_data = item.get("response", {})
    if isinstance(response_data, dict) and response_data:
        typer.echo("\nRESPONSE:")
        if protocol == "HTTP":
            status = response_data.get("status", "N/A")
            typer.echo(f"  Status: {status}")
            headers = response_data.get("headers", {})
            if headers:
                typer.echo(f"  Headers:")
                for key, val in headers.items():
                    typer.echo(f"    {key}: {val}")
            body = response_data.get("body", "")
            if body:
                typer.echo(f"  Body: {body}")
        elif protocol == "DNS":
            data = response_data.get("data", [])
            if isinstance(data, list):
                for answer in data:
                    typer.echo(f"  {answer}")
            else:
                typer.echo(f"  Data: {data}")
    typer.echo(f"\n{'='*60}\n")


def _resolve_fqdn(zone: str, domain: str) -> str:
    normalized_zone = zone.strip().lower()
    if "." in normalized_zone:
        return normalized_zone

    normalized_domain = domain.strip().lower()
    if not normalized_domain:
        raise typer.BadParameter(
            "Zone label provided but no default domain configured. Use: dssldrf config set --domain <domain>"
        )
    return f"{normalized_zone}.{normalized_domain}"


@config_app.command("show")
def config_show() -> None:
    _require_config()
    config = load_config()
    safe_output = {
        "api_url": config.api_url,
        "domain": config.domain,
        "client_id": config.client_id if config.client_id else "",
        "auth_token": "***" if _effective_token(config) else "",
    }
    typer.echo(json.dumps(safe_output, indent=2))


@config_app.command("set")
def config_set(
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="Dusseldorf API base URL"
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", help="Default backend domain"
    ),
    token: Optional[str] = typer.Option(None, "--token", help="Auth token"),
    clear_token: bool = typer.Option(
        False, "--clear-token", help="Remove stored token"
    ),
    client_id: Optional[str] = typer.Option(
        None, "--client-id", help="Azure application client ID"
    ),
) -> None:
    config = load_config()
    if api_url is not None:
        config.api_url = api_url.strip().rstrip("/")
    if domain is not None:
        config.domain = domain.strip().lower()
    if token is not None:
        config.auth_token = token.strip()
    if clear_token:
        config.auth_token = ""
    if client_id is not None:
        config.client_id = client_id.strip()
    save_config(config)
    typer.echo("Config updated")


@app.command("init")
def init_command() -> None:
    """Initialize CLI config using env var defaults."""
    if _config_exists():
        typer.echo("Existing config found. Values will be updated if changed.")

    current = load_config()
    default_api_url = (
        _first_env(
            "DSSLDRF_API_URL",
            "REACT_APP_API_HOST",
            "DUSSLEDORF_API_URL",
        )
        or current.api_url
    )
    default_domain = (
        _first_env(
            "DSSLDRF_DOMAIN",
            "REACT_APP_DOMAIN",
        )
        or current.domain
    )
    default_client_id = (
        _first_env(
            "DSSLDRF_CLIENT_ID",
            "AZURE_CLIENT_ID",
            "REACT_APP_CLIENT_ID",
        )
        or current.client_id
    )

    api_url = _prompt_required("Dusseldorf API URL", default_api_url)
    domain = typer.prompt(
        "Default domain (optional)",
        default=default_domain or "",
        show_default=bool(default_domain),
    ).strip()
    client_id = typer.prompt(
        "Azure App Client ID (for login)",
        default=default_client_id or "",
        show_default=bool(default_client_id),
    ).strip()

    current.api_url = api_url.rstrip("/")
    current.domain = domain.lower()
    current.client_id = client_id
    save_config(current)
    typer.echo("Config initialized")
    typer.echo("Next step: run dssldrf login")
    _install_completion()


@app.command("zone")
def zone_command(
    add: Optional[str] = typer.Option(None, "--add", "-a", help="Create zone label"),
    delete: Optional[str] = typer.Option(
        None, "--delete", "-d", help="Delete zone (label or fqdn)"
    ),
    list_zones: bool = typer.Option(
        False, "--list", "-l", help="List accessible zones"
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", help="Domain override for this call"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    _require_config()
    selected_actions = sum([bool(add), bool(delete), list_zones])
    # If no action specified, default to list
    if selected_actions == 0:
        list_zones = True
        selected_actions = 1
    if selected_actions != 1:
        raise typer.BadParameter(
            "Choose exactly one action: --add OR --delete OR --list"
        )

    config = load_config()
    active_domain = (domain or config.domain).strip().lower()
    client = _api_client()

    if add:
        zone_label = add.strip().lower()
        if "." in zone_label:
            raise typer.BadParameter(
                "--add expects a zone label without dots, example: --add test"
            )
        payload = {"zone": zone_label, "domain": active_domain, "num": 1}
        try:
            result = client.post("/zones", payload)
        except RuntimeError as exc:
            _handle_api_error(exc)
        if json_output:
            typer.echo(json.dumps(result, indent=2))
            return
        created = result[0]["fqdn"] if result else ""
        typer.echo(f"Created zone: {created}")
        return

    if delete:
        fqdn = _resolve_fqdn(delete, active_domain)
        try:
            result = client.delete(f"/zones/{fqdn}")
        except RuntimeError as exc:
            _handle_api_error(exc)
        if json_output:
            typer.echo(json.dumps(result, indent=2))
            return
        typer.echo(f"Deleted zone: {fqdn}")
        return

    params = {"domain": active_domain} if active_domain else None
    try:
        result = client.get("/zones", params=params)
    except RuntimeError as exc:
        _handle_api_error(exc)
    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return
    if not result:
        typer.echo("No zones found")
        return
    for item in result:
        typer.echo(item["fqdn"])


@app.command("login")
def login_command() -> None:
    """Fetch fresh auth token using az CLI and store it in config."""
    _require_config()
    config = load_config()

    if not config.client_id:
        raise typer.BadParameter(
            "Missing client_id. Run: dssldrf config set --client-id <id>"
        )

    # Run: az account get-access-token --resource <client_id>
    typer.echo(f"Fetching token for resource {config.client_id}...")
    try:
        result = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource",
                config.client_id,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        token_data = json.loads(result.stdout)
        token = token_data.get("accessToken")
        if not token:
            typer.echo("Error: No access token in response")
            raise typer.Exit(1)
        config.auth_token = token
        save_config(config)
        typer.echo("Auth token fetched successfully")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error running az CLI: {e.stderr}", err=True)
        typer.echo("Make sure you're logged in: az login")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Error: Could not parse token response", err=True)
        raise typer.Exit(1)


@app.command("req")
def req_command(
    zone: str = typer.Argument(..., help="Zone label or fqdn"),
    limit: int = typer.Option(
        20, "--limit", "-n", min=1, max=1000, help="Max request rows"
    ),
    skip: int = typer.Option(0, "--skip", "-s", min=0, help="Skip first N requests"),
    protocols: Optional[str] = typer.Option(
        None, "--protocols", "-p", help="CSV protocol filter"
    ),
    human: bool = typer.Option(
        False,
        "--human",
        help="Show timestamps in human-readable format (MM:DD hh:mm:ss)",
    ),
    details: bool = typer.Option(
        False,
        "--details",
        help="Show summary details (headers, body preview, etc.)",
    ),
    show_id: Optional[str] = typer.Option(
        None,
        "--id",
        help="Show full details of a specific request by ID (timestamp or _id)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    _require_config()
    config = load_config()
    zone_fqdn = _resolve_fqdn(zone, config.domain)
    params: dict[str, str | int] = {"limit": limit, "skip": skip}
    if protocols:
        params["protocols"] = protocols

    client = _api_client()
    try:
        result = client.get(f"/requests/{zone_fqdn}", params=params)
    except RuntimeError as exc:
        _handle_api_error(exc)

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return

    if not result:
        typer.echo("No requests found")
        return

    # Show full details of a specific request
    if show_id:
        found = None
        for item in result:
            item_id = item.get("_id", "")
            item_time = str(item.get("time", ""))
            if item_id == show_id or item_time == show_id:
                found = item
                break
        if found:
            _format_request_detail(found, human)
        else:
            typer.echo(f"Request not found with ID/timestamp: {show_id}", err=True)
            raise typer.Exit(1)
        return

    # List with optional summary details
    for item in result:
        if details:
            _format_request_summary(item, human)
            typer.echo()  # Blank line between requests
        else:
            # Compact view (original behavior)
            timestamp = item.get("time", "")
            protocol = item.get("protocol", "")
            client_ip = item.get("clientip", "")
            formatted_time = _format_timestamp(timestamp, human)
            typer.echo(f"{formatted_time} {protocol} {client_ip}")


def run() -> None:
    app()


if __name__ == "__main__":
    run()
