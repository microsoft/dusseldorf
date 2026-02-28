# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import json
import os
from typing import Optional

import typer

from .api_client import ApiClient
from .config_store import CliConfig, load_config, save_config


app = typer.Typer(help="duSSeldoRF CLI", no_args_is_help=True, add_completion=True)
config_app = typer.Typer(help="Manage local CLI settings")
app.add_typer(config_app, name="config")


def _effective_token(config: CliConfig) -> str:
    env_token = os.getenv("DSSLDRF_AUTH_TOKEN", "").strip()
    return env_token or config.auth_token


def _api_client() -> ApiClient:
    config = load_config()
    token = _effective_token(config)
    if not token:
        raise typer.BadParameter(
            "Missing token. Set DSSLDRF_AUTH_TOKEN or run: dssldrf config set --token <token>"
        )
    return ApiClient(api_url=config.api_url, token=token)


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
    config = load_config()
    safe_output = {
        "api_url": config.api_url,
        "domain": config.domain,
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
    save_config(config)
    typer.echo("Config updated")


@app.command("zone")
def zone_command(
    add: Optional[str] = typer.Option(None, "--add", help="Create zone label"),
    delete: Optional[str] = typer.Option(
        None, "--delete", help="Delete zone (label or fqdn)"
    ),
    list_zones: bool = typer.Option(False, "--list", help="List accessible zones"),
    domain: Optional[str] = typer.Option(
        None, "--domain", help="Domain override for this call"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    selected_actions = sum([bool(add), bool(delete), list_zones])
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
        result = client.post("/zones", payload)
        if json_output:
            typer.echo(json.dumps(result, indent=2))
            return
        created = result[0]["fqdn"] if result else ""
        typer.echo(f"Created zone: {created}")
        return

    if delete:
        fqdn = _resolve_fqdn(delete, active_domain)
        result = client.delete(f"/zones/{fqdn}")
        if json_output:
            typer.echo(json.dumps(result, indent=2))
            return
        typer.echo(f"Deleted zone: {fqdn}")
        return

    params = {"domain": active_domain} if active_domain else None
    result = client.get("/zones", params=params)
    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return
    if not result:
        typer.echo("No zones found")
        return
    for item in result:
        typer.echo(item["fqdn"])


@app.command("req")
def req_command(
    zone: str = typer.Argument(..., help="Zone label or fqdn"),
    limit: int = typer.Option(20, "--limit", min=1, max=1000, help="Max request rows"),
    protocols: Optional[str] = typer.Option(
        None, "--protocols", help="CSV protocol filter"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    config = load_config()
    zone_fqdn = _resolve_fqdn(zone, config.domain)
    params: dict[str, str | int] = {"limit": limit}
    if protocols:
        params["protocols"] = protocols

    client = _api_client()
    result = client.get(f"/requests/{zone_fqdn}", params=params)
    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return
    if not result:
        typer.echo("No requests found")
        return

    for item in result:
        timestamp = item.get("time", "")
        protocol = item.get("protocol", "")
        client_ip = item.get("clientip", "")
        typer.echo(f"{timestamp} {protocol} {client_ip}")


def run() -> None:
    app()


if __name__ == "__main__":
    run()
