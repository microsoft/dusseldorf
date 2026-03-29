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
import yaml
from click.core import Context
from typer.core import TyperGroup

from .api_client import ApiClient
from .config_store import CliConfig, load_config, save_config
from .rule_builder import (
    ALLOWED_PREDICATES,
    ALLOWED_RESULTS,
    component,
    ensure_json_text,
    infer_protocol,
    next_available_priority,
    parse_action_assignment,
    preview_rule,
    short_rule_name,
)
from .rule_service import create_rule_with_components


class _RuleGroup(TyperGroup):
    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        remaining = super().parse_args(ctx, args)
        if ctx._protected_args:
            candidate = ctx._protected_args[0]
            if self.get_command(ctx, candidate) is None:
                ctx.args = [*ctx._protected_args, *ctx.args]
                ctx._protected_args = []
                return ctx.args
        return remaining


app = typer.Typer(help="Dusseldorf CLI", no_args_is_help=True, add_completion=False)
config_app = typer.Typer(help="Manage local CLI settings")
rule_app = typer.Typer(
    help="Create and manage rules",
    cls=_RuleGroup,
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": False},
)
app.add_typer(config_app, name="config")
app.add_typer(rule_app, name="rule")


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
    protocol = str(item.get("protocol", "")).lower()
    client_ip = item.get("clientip", "")
    zone = item.get("zone", "")
    fqdn = item.get("fqdn", "")
    formatted_time = _format_timestamp(timestamp, human)

    typer.echo(f"id: {formatted_time}")
    typer.echo(f"zone: {zone or fqdn}")
    typer.echo(f"protocol: {protocol}")
    typer.echo(f"client ip: {client_ip}")
    typer.echo()

    # Request details
    request_data = item.get("request", {})
    if isinstance(request_data, dict):
        typer.echo("request:")
        if protocol == "http":
            method = request_data.get("method", "N/A")
            path = request_data.get("path", "N/A")
            tls = request_data.get("tls", False)
            typer.echo(f"  method: {method}")
            typer.echo(f"  path: {path}")
            if tls:
                typer.echo("  tls: yes")
            headers = request_data.get("headers", {})
            if headers:
                typer.echo("  headers:")
                for key, val in headers.items():
                    typer.echo(f"    {key}: {val}")
            body = request_data.get("body", "")
            if body:
                typer.echo(f"  body: {body}")
        elif protocol == "dns":
            query = request_data.get("query", "N/A")
            qtype = request_data.get("type", "N/A")
            typer.echo(f"  query: {query}")
            typer.echo(f"  type: {qtype}")

    # Response details
    response_data = item.get("response", {})
    if isinstance(response_data, dict) and response_data:
        typer.echo("\nresponse:")
        if protocol == "http":
            status = response_data.get("status", response_data.get("code", "N/A"))
            typer.echo(f"  status: {status}")
            headers = response_data.get("headers", {})
            if headers:
                typer.echo("  headers:")
                for key, val in headers.items():
                    typer.echo(f"    {key}: {val}")
            body = response_data.get("body", "")
            if body:
                typer.echo(f"  body: {body}")
        elif protocol == "dns":
            data = response_data.get("data", [])
            if isinstance(data, list):
                for answer in data:
                    typer.echo(f"  {answer}")
            else:
                typer.echo(f"  data: {data}")
    typer.echo(f"\n{'='*60}\n")


def _resolve_request_matches(items: list[dict], selector: str) -> list[dict]:
    normalized_selector = selector.strip()

    # Exact request IDs should win over timestamp matching.
    for item in items:
        if str(item.get("_id", "")) == normalized_selector:
            return [item]

    timestamp_matches = [
        item for item in items if str(item.get("time", "")) == normalized_selector
    ]
    if not timestamp_matches:
        raise typer.BadParameter(
            f"Request not found with ID/timestamp: {normalized_selector}"
        )
    return timestamp_matches


def _merge_protocol_filters(
    protocols: Optional[str],
    http_only: bool,
    dns_only: bool,
) -> Optional[str]:
    if http_only or dns_only:
        selected_protocols: list[str] = []
        if http_only:
            selected_protocols.append("HTTP")
        if dns_only:
            selected_protocols.append("DNS")
        return ",".join(selected_protocols)

    return protocols


def _format_rule_entry(rule: dict) -> str:
    protocol = str(rule.get("networkprotocol", "")).lower() or "unknown"
    priority = rule.get("priority", "?")
    name = str(rule.get("name", "")).strip() or "unnamed"
    rule_id = rule.get("ruleid", "")
    component_count = len(rule.get("rulecomponents", []))
    return (
        f"  [{protocol}] priority {priority} {name} "
        f"({rule_id}, {component_count} components)"
    )


def _render_rule_listing(rules: list[dict], selected_zone: Optional[str] = None) -> None:
    if not rules:
        if selected_zone:
            typer.echo(f"No rules found for zone: {selected_zone}")
        else:
            typer.echo("No rules found")
        return

    grouped_rules: dict[str, list[dict]] = {}
    for rule in rules:
        zone = str(rule.get("zone", "")).strip() or "unknown"
        grouped_rules.setdefault(zone, []).append(rule)

    for index, zone in enumerate(sorted(grouped_rules)):
        if index:
            typer.echo()
        typer.echo(f"zone: {zone}")
        zone_rules = sorted(
            grouped_rules[zone],
            key=lambda item: (
                int(item.get("priority", 0)) if str(item.get("priority", "")).isdigit() else 0,
                str(item.get("networkprotocol", "")),
                str(item.get("name", "")),
            ),
        )
        for rule in zone_rules:
            typer.echo(_format_rule_entry(rule))


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


def _prompt_json_map(label: str) -> str:
    typer.echo(f"Enter {label} entries as key=value. Leave blank to finish.")
    items: dict[str, str] = {}
    while True:
        line = typer.prompt("entry", default="", show_default=False).strip()
        if not line:
            break
        if "=" not in line:
            typer.echo("Expected key=value", err=True)
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            typer.echo("Key cannot be empty", err=True)
            continue
        items[key] = value.strip()
    return json.dumps(items)


def _normalize_bool_string(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return "true"
    if lowered in {"false", "0", "no", "n"}:
        return "false"
    raise typer.BadParameter("Expected boolean value: true|false")


def _build_rule_components(
    method: Optional[str],
    tls: Optional[bool],
    path: Optional[str],
    body_regex: Optional[str],
    header: list[str],
    header_keys: list[str],
    header_values_json: Optional[str],
    header_regexes_json: Optional[str],
    dns_types: list[str],
    response_code: Optional[int],
    response_body: Optional[str],
    response_header: list[str],
    response_headers_json: Optional[str],
    dns_data_json: Optional[str],
    passthru_url: Optional[str],
    var_rewrite: list[str],
    extra_predicate: list[str],
    extra_result: list[str],
    interactive_values: bool,
) -> tuple[list[dict], list[dict], list[str]]:
    predicates: list[dict] = []
    results: list[dict] = []
    action_names: list[str] = []

    if method:
        action_names.append("http.method")
        predicates.append(component("http.method", method.strip().upper(), True))

    if tls is not None:
        action_names.append("http.tls")
        predicates.append(component("http.tls", "true" if tls else "false", True))

    if path:
        action_names.append("http.path")
        predicates.append(component("http.path", path, True))

    if body_regex:
        action_names.append("http.body")
        predicates.append(component("http.body", body_regex, True))

    for item in header:
        action_names.append("http.header")
        predicates.append(component("http.header", item.strip(), True))

    if header_keys:
        action_names.append("http.headers.keys")
        predicates.append(component("http.headers.keys", ",".join(header_keys), True))

    if interactive_values and not header_values_json:
        if typer.confirm("Build http.headers.values JSON interactively?", default=False):
            header_values_json = _prompt_json_map("http.headers.values")

    if interactive_values and not header_regexes_json:
        if typer.confirm("Build http.headers.regexes JSON interactively?", default=False):
            header_regexes_json = _prompt_json_map("http.headers.regexes")

    if header_values_json:
        action_names.append("http.headers.values")
        predicates.append(
            component(
                "http.headers.values",
                ensure_json_text(header_values_json, "--header-values-json"),
                True,
            )
        )

    if header_regexes_json:
        action_names.append("http.headers.regexes")
        predicates.append(
            component(
                "http.headers.regexes",
                ensure_json_text(header_regexes_json, "--header-regexes-json"),
                True,
            )
        )

    if dns_types:
        action_names.append("dns.type")
        predicates.append(component("dns.type", ",".join(dns_types), True))

    if response_code is not None:
        action_names.append("http.code")
        results.append(component("http.code", str(response_code), False))

    if response_body is not None:
        action_names.append("http.body")
        results.append(component("http.body", response_body, False))

    for item in response_header:
        if ":" not in item:
            raise typer.BadParameter("--response-header expects name:value")
        action_names.append("http.header")
        results.append(component("http.header", item, False))

    if interactive_values and not response_headers_json:
        if typer.confirm("Build http.headers JSON interactively?", default=False):
            response_headers_json = _prompt_json_map("http.headers")

    if response_headers_json:
        action_names.append("http.headers")
        results.append(
            component(
                "http.headers",
                ensure_json_text(response_headers_json, "--response-headers-json"),
                False,
            )
        )

    if interactive_values and not dns_data_json:
        if typer.confirm("Provide dns.data JSON now?", default=False):
            dns_data_json = typer.prompt("dns.data JSON", default="{}").strip()

    if dns_data_json:
        action_names.append("dns.data")
        results.append(
            component("dns.data", ensure_json_text(dns_data_json, "--dns-data-json"), False)
        )

    if passthru_url:
        action_names.append("http.passthru")
        results.append(component("http.passthru", passthru_url.strip(), False))

    for value in var_rewrite:
        action_names.append("var")
        results.append(component("var", value, False))

    for assignment in extra_predicate:
        action_name, action_value = parse_action_assignment(assignment)
        action_names.append(action_name)
        if action_name == "http.tls":
            action_value = _normalize_bool_string(action_value)
        predicates.append(component(action_name, action_value, True))

    for assignment in extra_result:
        action_name, action_value = parse_action_assignment(assignment)
        action_names.append(action_name)
        results.append(component(action_name, action_value, False))

    if not results:
        raise typer.BadParameter("At least one result action is required")

    return predicates, results, action_names


def _yaml_components(items: list, is_predicate: bool) -> list[dict]:
    built: list[dict] = []
    for item in items:
        if isinstance(item, str):
            action_name, action_value = parse_action_assignment(item)
        elif isinstance(item, dict):
            action_name = str(item.get("action", "")).strip().lower()
            if not action_name:
                raise ValueError("YAML component object must include action")
            if "value" not in item:
                raise ValueError(f"YAML component {action_name} must include value")
            raw_value = item["value"]
            if isinstance(raw_value, (dict, list)):
                action_value = json.dumps(raw_value)
            elif isinstance(raw_value, bool):
                # Normalize YAML booleans to lowercase strings to match CLI conventions.
                action_value = "true" if raw_value else "false"
            else:
                action_value = str(raw_value)
        else:
            raise ValueError("YAML component entries must be strings or objects")

        built.append(component(action_name, action_value, is_predicate))
    return built


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
    request_ref: Optional[str] = typer.Argument(
        None,
        help="Optional request ID or timestamp; timestamps return all requests captured at that instant",
    ),
    limit: int = typer.Option(
        20, "--limit", "-n", min=1, max=1000, help="Max request rows"
    ),
    skip: int = typer.Option(0, "--skip", "-s", min=0, help="Skip first N requests"),
    protocols: Optional[str] = typer.Option(
        None, "--protocols", "-p", help="CSV protocol filter"
    ),
    http_only: bool = typer.Option(
        False,
        "--http",
        help="Only include HTTP requests",
    ),
    dns_only: bool = typer.Option(
        False,
        "--dns",
        help="Only include DNS requests",
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
        help="Show full details for a request ID or all requests at a timestamp",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    _require_config()
    if request_ref and show_id:
        raise typer.BadParameter("Provide a request selector either positionally or with --id, not both")

    config = load_config()
    zone_fqdn = _resolve_fqdn(zone, config.domain)
    params: dict[str, str | int] = {"limit": limit, "skip": skip}
    effective_protocols = _merge_protocol_filters(protocols, http_only, dns_only)
    if effective_protocols:
        params["protocols"] = effective_protocols

    client = _api_client()
    try:
        result = client.get(f"/requests/{zone_fqdn}", params=params)
    except RuntimeError as exc:
        _handle_api_error(exc)

    if not result:
        typer.echo("No requests found")
        return

    resolved_selector = show_id or request_ref
    if resolved_selector:
        selected_requests = _resolve_request_matches(result, resolved_selector)
        if json_output:
            typer.echo(json.dumps(selected_requests, indent=2))
            return
        for item in selected_requests:
            _format_request_detail(item, human)
        return

    if json_output:
        typer.echo(json.dumps(result, indent=2))
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


@rule_app.command("list-actions")
def rule_list_actions() -> None:
    typer.echo("Supported predicates:")
    for action_name in sorted(ALLOWED_PREDICATES):
        typer.echo(f"  - {action_name}")
    typer.echo("\nSupported results:")
    for action_name in sorted(ALLOWED_RESULTS):
        typer.echo(f"  - {action_name}")


@rule_app.callback()
def rule_command(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    if len(ctx.args) > 1:
        raise typer.BadParameter("Provide at most one zone: dssldrf rule [zone]")

    zone = ctx.args[0] if ctx.args else None

    _require_config()
    config = load_config()
    client = _api_client()

    try:
        if zone:
            zone_fqdn = _resolve_fqdn(zone, config.domain)
            result = client.list_rules(zone_fqdn)
            if json_output:
                typer.echo(json.dumps(result, indent=2))
                return
            _render_rule_listing(result, zone_fqdn)
            return

        result = client.list_all_rules()
    except RuntimeError as exc:
        _handle_api_error(exc)
        return

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return
    _render_rule_listing(result)


@rule_app.command("create")
def rule_create_command(
    zone: str = typer.Option(..., "--zone", help="Zone label or fqdn"),
    protocol: Optional[str] = typer.Option(None, "--protocol", help="HTTP or DNS"),
    name: Optional[str] = typer.Option(None, "--name", help="Rule name"),
    priority: Optional[int] = typer.Option(
        None, "--priority", min=1, max=1000, help="Rule priority (1..1000)"
    ),
    method: Optional[str] = typer.Option(
        None,
        "--http-req-method",
        help="HTTP request method predicate",
    ),
    tls: Optional[bool] = typer.Option(
        None,
        "--http-req-tls",
        help="HTTP request TLS predicate",
    ),
    path: Optional[str] = typer.Option(
        None,
        "--http-req-path-regex",
        help="HTTP request path regex predicate",
    ),
    body_regex: Optional[str] = typer.Option(
        None,
        "--http-req-body",
        "--http-req-body-regex",
        help="HTTP request body regex predicate",
    ),
    header: list[str] = typer.Option(
        [],
        "--http-req-header",
        help="HTTP request header present predicate",
    ),
    header_keys: list[str] = typer.Option(
        [],
        "--http-req-header-key",
        help="Required HTTP request header key",
    ),
    header_values_json: Optional[str] = typer.Option(
        None,
        "--http-req-header-values-json",
        help="JSON object for http.headers.values predicate",
    ),
    header_regexes_json: Optional[str] = typer.Option(
        None,
        "--http-req-header-regexes-json",
        help="JSON object for http.headers.regexes predicate",
    ),
    dns_types: list[str] = typer.Option(
        [],
        "--dns-req-type",
        help="DNS request type",
    ),
    response_code: Optional[int] = typer.Option(
        None,
        "--http-resp-code",
        help="HTTP response status code result",
    ),
    response_body: Optional[str] = typer.Option(
        None,
        "--http-resp-body",
        help="HTTP response body result",
    ),
    response_header: list[str] = typer.Option(
        [],
        "--http-resp-header",
        help="HTTP response header result in name:value format",
    ),
    response_headers_json: Optional[str] = typer.Option(
        None,
        "--http-resp-headers-json",
        help="JSON object for http.headers result",
    ),
    passthru_url: Optional[str] = typer.Option(
        None,
        "--http-resp-passthru-url",
        help="http.passthru target URL",
    ),
    dns_data_json: Optional[str] = typer.Option(
        None,
        "--dns-resp-data-json",
        help="JSON value for dns.data result",
    ),
    var_rewrite: list[str] = typer.Option([], "--var", help="var rewrite result, format from:to"),
    predicate: list[str] = typer.Option([], "--predicate", help="Extra predicate action=value"),
    result: list[str] = typer.Option([], "--result", help="Extra result action=value"),
    interactive_values: bool = typer.Option(
        False,
        "--interactive-values",
        help="Prompt for JSON-valued fields when omitted",
    ),
    preview: bool = typer.Option(False, "--preview", help="Show resolved rule before apply"),
    confirm: bool = typer.Option(False, "--confirm", help="Apply without interactive confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Print API response as JSON"),
) -> None:
    _require_config()
    config = load_config()
    zone_fqdn = _resolve_fqdn(zone, config.domain)
    client = _api_client()

    try:
        predicates, results, action_names = _build_rule_components(
            method=method,
            tls=tls,
            path=path,
            body_regex=body_regex,
            header=header,
            header_keys=header_keys,
            header_values_json=header_values_json,
            header_regexes_json=header_regexes_json,
            dns_types=dns_types,
            response_code=response_code,
            response_body=response_body,
            response_header=response_header,
            response_headers_json=response_headers_json,
            dns_data_json=dns_data_json,
            passthru_url=passthru_url,
            var_rewrite=var_rewrite,
            extra_predicate=predicate,
            extra_result=result,
            interactive_values=interactive_values,
        )

        resolved_protocol = infer_protocol(action_names, protocol)
    except ValueError as exc:
        raise typer.BadParameter(str(exc))

    try:
        existing_rules = client.list_rules(zone_fqdn)
        resolved_priority = priority or next_available_priority(existing_rules, resolved_protocol)
    except RuntimeError as exc:
        _handle_api_error(exc)
        return
    except ValueError as exc:
        raise typer.BadParameter(str(exc))

    auto_hint = method or (dns_types[0] if dns_types else "rule")
    resolved_name = (name or "").strip() or short_rule_name(resolved_protocol, auto_hint)

    preview_text = preview_rule(
        zone=zone_fqdn,
        protocol=resolved_protocol,
        name=resolved_name,
        priority=resolved_priority,
        predicates=predicates,
        results=results,
    )
    typer.echo(preview_text)

    if preview and not confirm:
        return

    if not confirm:
        if not typer.confirm("Apply this rule?", default=True):
            typer.echo("Cancelled")
            return

    try:
        result_data = create_rule_with_components(
            client=client,
            zone=zone_fqdn,
            protocol=resolved_protocol,
            name=resolved_name,
            priority=resolved_priority,
            predicates=predicates,
            results=results,
        )
    except RuntimeError as exc:
        _handle_api_error(exc)
        return

    if json_output:
        typer.echo(json.dumps(result_data, indent=2))
        return

    created_rule = result_data.get("rule", {})
    typer.echo(
        f"Created rule {created_rule.get('ruleid', '')} with {result_data.get('components_created', 0)} components"
    )


@rule_app.command("apply")
def rule_apply_command(
    file: str = typer.Option(..., "--file", "-f", help="YAML file with one or more rules"),
    confirm: bool = typer.Option(False, "--confirm", help="Apply without interactive confirmation"),
    continue_on_error: bool = typer.Option(
        False,
        "--continue-on-error",
        help="Keep applying subsequent rules after an error",
    ),
    preview: bool = typer.Option(False, "--preview", help="Preview rules and exit"),
    json_output: bool = typer.Option(False, "--json", help="Print full result JSON"),
) -> None:
    _require_config()
    config = load_config()
    client = _api_client()

    try:
        with open(file, "r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
    except OSError as exc:
        raise typer.BadParameter(f"Could not read file: {exc}")
    except yaml.YAMLError as exc:
        raise typer.BadParameter(f"Invalid YAML: {exc}")

    raw_rules = payload.get("rules") if isinstance(payload, dict) else None
    if not isinstance(raw_rules, list) or not raw_rules:
        raise typer.BadParameter("YAML must contain a non-empty 'rules' list")

    outcomes: list[dict] = []

    for index, raw_rule in enumerate(raw_rules, start=1):
        if not isinstance(raw_rule, dict):
            message = f"rules[{index}] must be an object"
            outcomes.append({"index": index, "status": "error", "error": message})
            if not continue_on_error:
                break
            continue

        try:
            zone_value = str(raw_rule.get("zone", "")).strip()
            if not zone_value:
                raise ValueError("Missing zone")
            zone_fqdn = _resolve_fqdn(zone_value, config.domain)

            predicates = _yaml_components(raw_rule.get("predicates", []), True)
            results = _yaml_components(raw_rule.get("results", []), False)
            if not results:
                raise ValueError("Each rule must include at least one result")

            action_names = [c["actionname"] for c in predicates + results]
            resolved_protocol = infer_protocol(action_names, raw_rule.get("protocol"))
            existing_rules = client.list_rules(zone_fqdn)

            parsed_priority = raw_rule.get("priority")
            if parsed_priority is None:
                resolved_priority = next_available_priority(existing_rules, resolved_protocol)
            else:
                resolved_priority = int(parsed_priority)
                if resolved_priority < 1 or resolved_priority > 1000:
                    raise ValueError("priority must be in range 1..1000")

            name_hint = raw_rule.get("name_hint")
            if not name_hint and predicates:
                name_hint = predicates[0]["actionname"].split(".")[-1]
            resolved_name = str(raw_rule.get("name", "")).strip() or short_rule_name(
                resolved_protocol,
                str(name_hint or "rule"),
            )

            typer.echo(
                preview_rule(
                    zone=zone_fqdn,
                    protocol=resolved_protocol,
                    name=resolved_name,
                    priority=resolved_priority,
                    predicates=predicates,
                    results=results,
                )
            )

            if preview:
                outcomes.append({"index": index, "status": "preview"})
                continue

            if not confirm:
                if not typer.confirm(f"Apply rule {index}?", default=True):
                    outcomes.append({"index": index, "status": "skipped"})
                    continue

            created = create_rule_with_components(
                client=client,
                zone=zone_fqdn,
                protocol=resolved_protocol,
                name=resolved_name,
                priority=resolved_priority,
                predicates=predicates,
                results=results,
            )
            outcomes.append(
                {
                    "index": index,
                    "status": "created",
                    "ruleid": created.get("rule", {}).get("ruleid"),
                    "components_created": created.get("components_created", 0),
                }
            )
        except (RuntimeError, ValueError) as exc:
            outcomes.append({"index": index, "status": "error", "error": str(exc)})
            if not continue_on_error:
                break

    if json_output:
        typer.echo(json.dumps(outcomes, indent=2))
        return

    for outcome in outcomes:
        status = outcome.get("status")
        if status == "created":
            typer.echo(
                f"Rule {outcome['index']} created: {outcome.get('ruleid', '')} ({outcome.get('components_created', 0)} components)"
            )
        elif status == "preview":
            typer.echo(f"Rule {outcome['index']} previewed")
        elif status == "skipped":
            typer.echo(f"Rule {outcome['index']} skipped")
        else:
            typer.echo(f"Rule {outcome['index']} failed: {outcome.get('error', '')}", err=True)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
