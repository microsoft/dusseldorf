# Dusseldorf CLI

Simple cross-platform command line client for Dusseldorf.

The command name is `dssldrf` and focuses on simple zone setup + request lookup.

## What this supports now (MVP)

- `dssldrf zone --add <label>`
- `dssldrf zone --list`
- `dssldrf zone --delete <label|fqdn>`
- `dssldrf req <label|fqdn>`
- `dssldrf config set/show`

Spec document: [SPEC.md](SPEC.md)

## Prerequisites

- Python 3.10+
- Network access to Dusseldorf API endpoint
- Valid API Bearer token (`DSSLDRF_AUTH_TOKEN`)

## Install from this repo

From the `cli/` folder:

```bash
python -m pip install --upgrade pip
python -m pip install pipx
pipx ensurepath
pipx install .
```

After install, `dssldrf` should be available globally from any terminal session.

## PATH notes by OS

If `dssldrf` is not found, add your Python scripts directory to `PATH`.

### Linux

Common paths:

- `~/.local/bin`
- `~/.local/pipx/venvs/...` (managed by pipx)

Example:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### macOS

Common paths:

- `~/.local/bin`
- `~/Library/Python/<version>/bin`

Example (zsh):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows (PowerShell)

Common path:

- `%USERPROFILE%\AppData\Roaming\Python\Python3x\Scripts`

Example:

```powershell
[Environment]::SetEnvironmentVariable(
	"Path",
	$env:Path + ";$env:APPDATA\Python\Python312\Scripts",
	"User"
)
```

Close and reopen terminal after PATH updates.

## Configure

Set API URL and default domain:

```bash
dssldrf config set --api-url https://frontend/api --domain dssldrf.net
```

Set token (recommended through env var):

```bash
export DSSLDRF_AUTH_TOKEN="<token>"
```

Windows PowerShell:

```powershell
$env:DSSLDRF_AUTH_TOKEN = "<token>"
```

Show current config:

```bash
dssldrf config show
```

## Usage examples

Create zone `test.dssldrf.net`:

```bash
dssldrf zone --add test
```

List your zones:

```bash
dssldrf zone --list
```

Show latest requests for `test.dssldrf.net`:

```bash
dssldrf req test --limit 20
```

Delete zone:

```bash
dssldrf zone --delete test
```

## Tab completion

Typer completion is built-in.

Install completion for your shell:

```bash
dssldrf --install-completion
```

After restarting shell, commands like `dssldrf zo<TAB>` should expand/suggest `zone`.

If needed, inspect generated completion script:

```bash
dssldrf --show-completion
```

## Local development

From `cli/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
dssldrf --help
```

## Optional: binary distribution

This framework is package-first. If you also need native binaries:

- build one binary per OS/arch (Linux/macOS/Windows)
- publish binaries in releases
- users place binary folder on `PATH`

Tools to use in CI: `pyinstaller` or `nuitka`.

### Downloading pre-built binaries

**From GitHub Releases** (recommended):

1. Go to [Releases](../../releases)
2. Download the binary for your OS:
   - `dssldrf-linux-amd64` (Linux)
   - `dssldrf-macos-amd64` (macOS)
   - `dssldrf-windows-amd64.exe` (Windows)
3. Place it in a folder on `PATH`:
   - Linux/macOS: `/usr/local/bin` or `~/.local/bin`
   - Windows: `%USERPROFILE%\bin` or another folder on `PATH`
4. Linux/macOS only: make executable with `chmod +x dssldrf-*`

After this, `dssldrf --help` should work from any terminal folder.

**From CI artifacts** (development builds):

This repo includes `.github/workflows/cli-binaries.yml` that builds on every PR/push to `cli/`:

- Artifacts: `dssldrf-Linux`, `dssldrf-macOS`, `dssldrf-Windows`
- Access via **Actions** tab in GitHub
- Manually trigger via **Build CLI Binaries** workflow

### Creating a new release

To publish new binaries:

1. Create and push a new tag: `git tag v0.2.0 && git push origin v0.2.0`
2. Create a GitHub Release for that tag
3. The `cli-release.yml` workflow runs automatically and attaches binaries to the release

This CLI talks to the API directly using your EntraID token

