# Dusseldorf CLI Specification

This spec documents the functionality of a dusseldorf command line interface (cli) client tool
to interact with a Dusseldorf API.

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
- CLI framework: Typer (Click-based) - provides automatic `-h` short flag support
- HTTP client: httpx
- Token fetching: Shell out to `az account get-access-token` (Azure CLI)
- Packaging: Python package with console entrypoint `dssldrf`
- Optional binary packaging: PyInstaller or Nuitka (per-OS build)

Rationale: Python3 + Typer is a small codebase, cross-platform, supports shell completion, and is easy to ship as both script and binary. Using `az` CLI avoids complexity of MSAL and works around policy restrictions on device code flow.

## CLI Command Contract (MVP)

### 1) Config

- `dssldrf config set --api-url <url> [--domain <domain>] [--token <token>] [--client-id <id>]`
- `dssldrf config show`

Stores configuration in `~/.dssldrf/config.json`.

Fields:
- `api_url`: Dusseldorf API base URL (example `https://frontend/api`)
- `domain`: default backend domain (example `dssldrf.net`)
- `auth_token`: optional local token (env var preferred)
- `client_id`: Azure AD application ID (for `dssldrf login` to fetch tokens via az CLI)

### 2) Zone management

- `dssldrf zone` (no flags) - Lists all accessible zones (default behavior)
- `dssldrf zone --add <label> [-a] [--domain <domain>]`
  - Example: `dssldrf zone --add test` or `dssldrf zone -a test`
  - Calls `POST /zones` with `{ "zone": "test", "domain": "dssldrf.net", "num": 1 }`
- `dssldrf zone --list [-l] [--domain <domain>]`
  - Calls `GET /zones`
- `dssldrf zone --delete <label|fqdn> [-d] [--domain <domain>]`
  - Calls `DELETE /zones/{fqdn}`

### 3) Requests

- `dssldrf req <label|fqdn> [--limit <n> / -n] [--skip <n> / -s] [--protocols <csv> / -p] [--human] [--details] [--id <request-id>]`
  - Example: `dssldrf req test` or `dssldrf req test -n 50 -s 10 --details`
  - Resolves to `test.dssldrf.net` if default domain is set.
  - Calls `GET /requests/{zone}?limit=<n>&skip=<n>&protocols=<csv>`
  - `--limit` - Max requests to return (default 20, max 1000)
  - `--skip` - Skip first N requests (useful for pagination)
  - `--protocols` - CSV filter by protocol (e.g., `HTTP`, `DNS`, `HTTP,DNS`)
  - `--human` - Format timestamp as MM:DD hh:mm:ss instead of Unix timestamp
  - `--details` - Show summary view: includes method/path, first 3 headers, response status and body preview (truncated to 100 chars)
  - `--id <request-id>` - Show full details of a specific request; accepts either Unix timestamp or MongoDB `_id`; displays complete REQUEST and RESPONSE sections with all headers and full body

**View modes:**
- *Compact* (default): Shows timestamp, protocol, client IP per row
- *Summary* (`--details`): Each request includes method/path, sample headers, response status
- *Full* (`--id <request-id>`): Complete REQUEST/RESPONSE details for one request

**Example workflows:**
```bash
# List recent requests
dssldrf req test

# See request details (headers, body preview)
dssldrf req test --details

# Inspect a specific request in detail
dssldrf req test --id 1738034859

# With human-readable timestamps
dssldrf req test --details --human
dssldrf req test --id 1738034859 --human

# Paginate through requests
dssldrf req test -n 20 -s 20  # Get requests 20-40

# Filter by protocol
dssldrf req test --protocols HTTP
```

### 4) Authentication

- `dssldrf login`
  - Shells out to `az account get-access-token --resource <client-id>`
  - Requires Azure CLI (`az`) to be installed and user logged in
  - Stores token in config after successful fetch
  - Requires `client_id` configured first via `dssldrf config set --client-id <id>`

### 5) Output

- Default: human-readable lines.
- `--json` option for machine-readable output.
- All commands support `-h` short flag for help.

## Authentication Model

**Priority order:**
1. Environment variable `DSSLDRF_AUTH_TOKEN`
2. Stored token in config file (from `dssldrf login` or manual `config set --token`)

**Authentication methods:**
- **Azure CLI Token Fetch** (recommended): `dssldrf login`
  - Requires `az` CLI installed and user logged in (`az login`)
  - Calls `az account get-access-token --resource <client-id>`
  - Uses same app registration as web UI
  - Token stored after successful fetch
- **Manual token**: `export DSSLDRF_AUTH_TOKEN=<token>` or `dssldrf config set --token <token>`

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

## Initial Framework Files

- `cli/pyproject.toml`
- `cli/src/dssldrf_cli/main.py`
- `cli/src/dssldrf_cli/config_store.py`
- `cli/src/dssldrf_cli/api_client.py`

## Next Iteration Candidates

- Rule CRUD commands
- Rich formatting (`table`) and filter presets
- Auto-discover domain from `/domains` when not configured
- Token refresh handling (MSAL cache)
