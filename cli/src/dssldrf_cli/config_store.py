# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Project duSSeldoRF CLI

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path


CONFIG_DIR: Path = Path.home() / ".dssldrf"
CONFIG_FILE: Path = CONFIG_DIR / "config.json"


@dataclass
class CliConfig:
    api_url: str = "https://localhost:10443/api"
    domain: str = ""
    auth_token: str = ""


def load_config() -> CliConfig:
    if not CONFIG_FILE.exists():
        return CliConfig()

    try:
        raw_data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return CliConfig()

    return CliConfig(
        api_url=str(raw_data.get("api_url", CliConfig.api_url)).rstrip("/"),
        domain=str(raw_data.get("domain", "")).strip().lower(),
        auth_token=str(raw_data.get("auth_token", "")).strip(),
    )


def save_config(config: CliConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(asdict(config), indent=2, sort_keys=True),
        encoding="utf-8",
    )
