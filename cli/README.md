# Dusseldorf: Command Line Interface

A simple command line tool for managing your Dusseldorf zones, viewing requests and adding and editing rules. This works on Windows/wsl2, macOS, Linux.

Once installed, you'll have a `dssldrf` command you can run from anywhere.

## Examples:

- `dssldrf zone` - List all your zones (default)
- `dssldrf zone --add foo` or `dssldrf zone -a foo` - Create a new zone
- `dssldrf req foo` - View recent requests for a zone
- `dssldrf rule` - List rules across all your accessible zones
- `dssldrf rule foo` - List rules for one zone
- `dssldrf rule apply -f mock_api.yaml` - Apply one or more rules from YAML

The full spec can be found here: [SPEC.md](SPEC.md)

---

## Installation

The instlalation has two main parts:

1. Install `pipx` and basic prerequisites.
2. Download the repo and install the CLI from `cli/`.

### 1. Install `pipx` and prerequisites

**on Ubuntu/Debian/WSL:**

```bash
sudo apt update
sudo apt install -y git python3 python3-pip pipx
python3 -m pipx ensurepath
```

**Other Linux/macOS:**

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pipx
python3 -m pipx ensurepath
```

### 2. Install dusseldorf CLI

These commands can be copied and pasted in your terminal:

```bash
git clone https://github.com/microsoft/dusseldorf.git
cd dusseldorf/cli
python3 -m pipx install .
dssldrf --help
```


If `dssldrf` is not found immediately after installation, close and reopen your terminal once and run:

```bash
dssldrf --help
```

`pipx` installs the CLI in an isolated environment and places the `dssldrf` command on your PATH.

---

## Setup (First Time)

Before you can use `dssldrf`, you need to configure it and set up authentication.

### 1. Configure the API endpoint and domain:

```bash
dssldrf config set --api-url https://your-dusseldorf-server/api --domain yourdomain.net
```

Replace:
- `https://your-dusseldorf-server/api` with your Dusseldorf API URL (control plane)
- `yourdomain.net` with your backend domain (data plane)

### 2. Set up authentication

Dusseldorf CLI uses EntraID Bearer token authentication. You can provide a token in two ways:

#### Option A: Environment Variable (Recommended)

Set the `DSSLDRF_AUTH_TOKEN` environment variable with your token:

**Linux/WSL/macOS:**
```bash
export DSSLDRF_AUTH_TOKEN=<your-bearer-token>
dssldrf zone
```

#### Option A.2: Using `dssldrf login` (Easiest with Azure CLI)

If you have Azure CLI (`az`) installed and are logged in, you can fetch tokens automatically:

**1. Configure your app ID:**

```bash
dssldrf config set --client-id <your-app-client-id>
```

Replace `<your-app-client-id>` with your Dusseldorf app registration's client ID. This is the same ID your web UI uses.

**2. Login:**

```bash
dssldrf login
```

This runs `az account get-access-token --resource <client-id>` and saves the token to your config. The token is fetched automatically using your existing Azure CLI login.

**3. Verify:**

```bash
dssldrf zone
```

> **Requirements:** You must have Azure CLI installed (`az`) and be logged in. If you're not logged in, run `az login` first.

#### Option B: Store in Config (Less Secure)

Alternatively, store the token in your local config file:

```bash
dssldrf config set --token <your-bearer-token>
```

**Warning:** This stores your token in plain text at `~/.dssldrf/config.json`. The environment variable approach (Option A) is more secure.

### 3. Verify it works:

```bash
dssldrf zone
```

You should see your zones listed (or "No zones found" if you haven't created any yet).

---

---



## Common Tasks

### List zones

Just type:

```bash
dssldrf zone
```

Or explicitly:

```bash
dssldrf zone --list
# Or short version:
dssldrf zone -l
```

### Create a new zone

```bash
dssldrf zone --add mytest
```

This creates `mytest.yourdomain.net` (using the domain you configured).

### List your zones

See "List zones" above - just run:

```bash
dssldrf zone
```

> **Tip:** Most commands support short flags: `-a` for `--add`, `-d` for `--delete`, `-l` for `--list`, `-n` for `--limit`, `-s` for `--skip`, `-p` for `--protocols`, `-h` for `--help`



### View requests for a zone

#### Compact list (default)

```bash
dssldrf req mytest --limit 20
```

Shows timestamp, protocol, and client IP for each request (e.g., `1738034859 HTTP 174.181.87.109`)

#### Summary view (with headers and body preview)

```bash
dssldrf req mytest --details
```

Shows method/path, first 3 headers, response status code, and a preview of the request body (truncated to 100 chars). Useful for quickly inspecting what was in a request.

#### Full details for a request or timestamp group

```bash
dssldrf req mytest --id 1738034859
```

Shows complete REQUEST and RESPONSE sections with all headers, full body, HTTP method, path, TLS flag, etc. You can pass either a timestamp (Unix) or MongoDB `_id`.

When you pass a timestamp, the CLI shows every request captured at that exact timestamp. This is useful when DNS and HTTP requests land in the same second.

```bash
dssldrf req mytest 1738034859
dssldrf req mytest --id 1738034859 --json
```

With `--json`, selector-based output is always an array. A timestamp returns all matching requests; an exact `_id` returns a one-element array.

#### Human-readable timestamps

```bash
dssldrf req mytest --human
# Shows timestamps as MM:DD hh:mm:ss instead of Unix timestamps

dssldrf req mytest --details --human
dssldrf req mytest --id 1738034859 --human
dssldrf req mytest 1738034859 --human
```

Works with all view modes.

#### Pagination

```bash
dssldrf req mytest --limit 20 --skip 10
# Or short version:
dssldrf req mytest -n 20 -s 10
```

#### Filter by protocol

```bash
dssldrf req mytest --protocols HTTP,DNS
dssldrf req mytest --protocols HTTP  # HTTP only
dssldrf req mytest --http
dssldrf req mytest --dns
dssldrf req mytest 1738034859 --http --json
```

This shows the last 20 requests received by `mytest.yourdomain.net`.

`--http` and `--dns` are convenience filters. If either is present, only those protocol families are requested and shown.

### Delete a zone

```bash
dssldrf zone --delete mytest
# Or short version:
dssldrf zone -d mytest
```

### List rules

```bash
dssldrf rule
```

Lists rules across all accessible zones, grouped by zone.

To narrow that down to one zone:

```bash
dssldrf rule mytest
```

If you want machine-readable output, put the group option before the zone selector:

```bash
dssldrf rule --json
dssldrf rule --json mytest
```

### Create a rule from CLI flags

Block POST requests that contain Authorization header and return a fixed response:

```bash
dssldrf rule create \
  --zone mytest \
  --http-req-method POST \
  --http-req-header Authorization \
  --http-resp-code 403 \
  --http-resp-body "blocked by policy"
```

Useful options:

- `--preview` shows the resolved rule and exits.
- `--confirm` applies without interactive prompt.
- `--predicate action=value` and `--result action=value` let you use all API-supported actions.
- `--interactive-values` helps build JSON-valued actions interactively.

### Apply rules from YAML

```bash
dssldrf rule apply -f rules.yaml
```

Example YAML:

```yaml
rules:
  - zone: mytest
    protocol: HTTP
    predicates:
      - action: http.method
        value: POST
      - action: http.header
        value: Authorization
    results:
      - action: http.code
        value: "403"
      - action: http.body
        value: blocked by policy
```

List all currently supported predicate/result names:

```bash
dssldrf rule list-actions
```

---

## Tab Completion (Optional)

You can enable tab completion so `dssldrf zo<TAB>` expands to `dssldrf zone`:

```bash
dssldrf --install-completion
```

Then restart your terminal.

---

## Troubleshooting

### "dssldrf: command not found"

The `dssldrf` command is not in your system PATH.

**For binary installation:**
- Make sure you moved the file to `/usr/local/bin` (Linux/macOS/WSL) or a folder that's on your PATH
- Try running `echo $PATH` to see which folders are checked for commands

**For Python installation:**
- Close and reopen your terminal (PATH updates don't apply to currently open terminals)
- Run `pipx ensurepath` again and follow any instructions it prints
- On Linux/WSL: Add this line to your `~/.bashrc` file:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```
  Then run `source ~/.bashrc`
- On macOS: Add the same line to `~/.zshrc` instead

### Authentication errors

Your token may have expired or be invalid. Make sure you're using a valid bearer token by setting `DSSLDRF_AUTH_TOKEN` environment variable or storing it with `dssldrf config set --token`.

### "Missing token" error

You need to set `DSSLDRF_AUTH_TOKEN` or store a token in config.

Quick fix:
```bash
export DSSLDRF_AUTH_TOKEN=<your-bearer-token>
```

Or save it to config:
```bash
dssldrf config set --token <your-bearer-token>
```

### "externally-managed-environment" error (Ubuntu/Debian/WSL)

Modern Ubuntu/Debian systems prevent installing Python packages globally to protect the system.

**Solution:** Install `pipx` using the system package manager instead:

```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
pipx install .
```

Then close and reopen your terminal.

---

## Advanced Options

### Store token in config (not recommended)

Instead of using the environment variable, you can store your token in the config file:

```bash
dssldrf config set --token <your-token>
```

**Warning:** This stores your token in plain text at `~/.dssldrf/config.json`. The environment variable approach is safer.

### Output raw JSON

Add `--json` to any command:

```bash
dssldrf zone --list --json
dssldrf req mytest --json
```

---

## For Developers

### Local development

From `cli/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
dssldrf --help
```

### Building binaries yourself

This repo uses PyInstaller via GitHub Actions to build binaries.

**From CI artifacts** (development builds):

- Workflow: `.github/workflows/cli-binaries.yml` builds on every PR/push to `cli/`
- Artifacts: `dssldrf-Linux`, `dssldrf-macOS`, `dssldrf-Windows`
- Access via **Actions** tab in GitHub
- Manually trigger via **Build CLI Binaries** workflow

### Creating a new release

To publish new binaries:

1. Create and push a new tag: `git tag v0.2.0 && git push origin v0.2.0`
2. Create a GitHub Release for that tag
3. The `cli-release.yml` workflow runs automatically and attaches binaries to the release

This CLI talks to the API directly using your EntraID token


