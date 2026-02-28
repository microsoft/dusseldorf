# Dusseldorf CLI Specification (MVP)

## Goals

- Keep the CLI minimal and easy to install.
- Support Linux, macOS, and Windows.
- Talk directly to Dusseldorf API with a Bearer token.
- Prioritize zone setup and request inspection workflows.
- Expose command name `dssldrf` so it runs from any folder.

## Non-goals (MVP)

- No interactive login flow.
- No advanced rule management yet.
- No daemon/background process.

## Technology Choice

- Language: Python 3.10+
- CLI framework: Typer (Click-based)
- HTTP client: httpx
- Packaging: Python package with console entrypoint `dssldrf`
- Optional binary packaging: PyInstaller or Nuitka (per-OS build)

Rationale: Python + Typer is a small codebase, cross-platform, supports shell completion, and is easy to ship as both script and binary.

## CLI Command Contract (MVP)

### 1) Config

- `dssldrf config set --api-url <url> [--domain <domain>] [--token <token>] [--clear-token]`
- `dssldrf config show`

Stores configuration in `~/.dssldrf/config.json`.

Fields:
- `api_url`: Dusseldorf API base URL (example `https://frontend/api`)
- `domain`: default backend domain (example `dssldrf.net`)
- `auth_token`: optional local token (env var preferred)

### 2) Zone management

- `dssldrf zone --add <label> [--domain <domain>]`
  - Example: `dssldrf zone --add test`
  - Calls `POST /zones` with `{ "zone": "test", "domain": "dssldrf.net", "num": 1 }`
- `dssldrf zone --list [--domain <domain>]`
  - Calls `GET /zones`
- `dssldrf zone --delete <label|fqdn> [--domain <domain>]`
  - Calls `DELETE /zones/{fqdn}`

### 3) Requests

- `dssldrf req <label|fqdn> [--limit <n>] [--protocols <csv>]`
  - Example: `dssldrf req test`
  - Resolves to `test.dssldrf.net` if default domain is set.
  - Calls `GET /requests/{zone}?limit=<n>&protocols=<csv>`

### 4) Output

- Default: human-readable lines.
- `--json` option for machine-readable output.

## Authentication Model (MVP)

Priority order:
1. Environment variable `DSSLDRF_AUTH_TOKEN`
2. Stored token in config file

API auth header:
- `Authorization: Bearer <token>`

## Error Handling (MVP)

- Missing token: fail with clear remediation message.
- API error: print status + `detail` from API JSON if available.
- Invalid command usage: fail fast with argument help.

## Completion (Tab)

Typer completion is enabled. Users install shell completion once:

- Bash/Zsh/Fish/Powershell supported via Typer completion install command.
- UX target: `dssldrf zo<TAB>` expands or suggests `zone`.

## Cross-platform Distribution

### Script/package mode (recommended first)

- Install with `pipx install .` (or `pip install .`)
- `dssldrf` command is placed in user scripts folder that should be on `PATH`

### Binary mode

- Build one binary per OS/arch (Linux, macOS, Windows).
- Publish binaries via GitHub Releases.
- Users download binary and place it in a folder on `PATH`.

**CI workflows**:
- `.github/workflows/cli-binaries.yml` - builds on PR/push to `cli/`
- `.github/workflows/cli-release.yml` - builds and attaches to GitHub Releases on tag creation

**Release assets**:
- `dssldrf-linux-amd64`
- `dssldorf-macos-amd64`
- `dssldrf-windows-amd64.exe`

## Initial Framework Files

- `cli/pyproject.toml`
- `cli/src/dssldrf_cli/main.py`
- `cli/src/dssldrf_cli/config_store.py`
- `cli/src/dssldrf_cli/api_client.py`

## Next Iteration Candidates

- Device-code login command for Entra ID.
- Rule CRUD commands.
- Rich formatting (`table`) and filter presets.
- Auto-discover domain from `/domains` when not configured.
