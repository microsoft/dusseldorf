# Dusseldorf CLI

A simple command line tool for managing Dusseldorf zones and viewing requests. Works on Windows, macOS, Linux, and WSL.

Once installed, you'll have a `dssldrf` command you can run from anywhere.

## What you can do

- `dssldrf login` — Authenticate with EntraID (browser/device code)
- `dssldrf zone` — List all your zones (default)
- `dssldrf zone --add test` or `dssldrf zone -a test` — Create a new zone
- `dssldrf zone --delete test` or `dssldrf zone -d test` — Delete a zone
- `dssldrf req test` — View recent requests for a zone
- `dssldrf config set --api-url <url> --domain <domain>` — Configure settings

> **Tip:** Most commands support short flags: `-a` for `--add`, `-d` for `--delete`, `-l` for `--list`, `-n` for `--limit`, `-h` for `--help`

Full spec: [SPEC.md](SPEC.md)

---

## Installation (Choose One)

### Option 1: Download Pre-Built Binary (Easiest)

**No Python installation needed!**

1. Go to [Releases](../../releases) and download the file for your system:
   - **Linux/WSL**: `dssldrf-linux-amd64`
   - **macOS**: `dssldrf-macos-amd64`
   - **Windows**: `dssldrf-windows-amd64.exe`

2. Make it executable and move it to a system folder:

   **Linux/WSL:**
   ```bash
   chmod +x dssldrf-linux-amd64
   sudo mv dssldrf-linux-amd64 /usr/local/bin/dssldrf
   ```

   **macOS:**
   ```bash
   chmod +x dssldrf-macos-amd64
   sudo mv dssldrf-macos-amd64 /usr/local/bin/dssldrf
   ```

   **Windows PowerShell (run as Administrator):**
   ```powershell
   # Create a tools folder if it doesn't exist
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\bin"
   # Move the file
   Move-Item .\dssldrf-windows-amd64.exe "$env:USERPROFILE\bin\dssldrf.exe"
   # Add to PATH (one-time setup)
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\bin", "User")
   ```

3. Close and reopen your terminal, then test:
   ```bash
   dssldrf --help
   ```

### Option 2: Install with Python

**If you have Python 3.10 or newer installed:**

This installs the `dssldrf` command automatically using a tool called `pipx` (which keeps it isolated from your other Python packages).

1. Open your terminal

2. Navigate to the `cli/` folder in this repository

3. Run these commands:

   **Ubuntu/Debian/WSL (Ubuntu):**
   
   ```bash
   # Install pipx from system package manager
   sudo apt update
   sudo apt install pipx
   pipx ensurepath
   pipx install .
   ```

   **Other Linux/macOS:**
   
   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install pipx
   pipx ensurepath
   pipx install .
   ```

   **Windows PowerShell:**
   
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install pipx
   pipx ensurepath
   pipx install .
   ```

4. Close and reopen your terminal (this is important!)

5. Test that `dssldrf` is now available:
   ```bash
   dssldrf --help
   ```

> **What just happened?** The `pipx install .` command created the `dssldrf` command and put it in a folder that's on your system PATH (usually `~/.local/bin` on Linux/macOS or `%APPDATA%\Python\Scripts` on Windows). That's why you can now type `dssldrf` from any folder.

---

## Setup (First Time)

Before you can use `dssldrf`, you need to configure it and authenticate.

### Option A: Using EntraID Login (Recommended)

This is the easiest way - the CLI handles authentication for you.

**1. Configure EntraID settings:**

You'll need your Dusseldorf app registration details:

```bash
dssldrf config set --api-url https://your-dusseldorf-server/api --domain yourdomain.net --client-id <your-client-id> --tenant-id <your-tenant-id>
```

Replace:
- `https://your-dusseldorf-server/api` with your Dusseldorf API URL
- `yourdomain.net` with your backend domain (e.g., `dssldrf.net`)
- `<your-client-id>` with your EntraID application (client) ID
- `<your-tenant-id>` with your EntraID tenant ID

> **Where to find these IDs:** See \"EntraID App Registration Setup\" section below or the detailed guide: [ENTRAID_SETUP.md](ENTRAID_SETUP.md)

**2. Login:**

```bash
dssldrf login
```

This will:
- Show you a URL and a code
- Open that URL in your browser (or you can copy/paste it)
- Enter the code when prompted
- Sign in with your Microsoft account
- Automatically save your authentication token

**3. Verify it works:**

```bash
dssldrf zone
```

You should see your zones listed (or "No zones found" if you haven't created any yet).

### Option B: Using Manual Token

If you prefer to get tokens manually:

**1. Configure the CLI:**

```bash
dssldrf config set --api-url https://your-dusseldorf-server/api --domain yourdomain.net
```

**2. Get your authentication token:**

You need an EntraID (Azure AD) token. Get it with this command:

**Linux/WSL/macOS:**
```bash
export DSSLDRF_AUTH_TOKEN=$(az account get-access-token --resource <your-app-id> | jq -r .accessToken)
```

**Windows PowerShell:**
```powershell
$env:DSSLDRF_AUTH_TOKEN = (az account get-access-token --resource <your-app-id> | ConvertFrom-Json).accessToken
```

> **Note:** Replace `<your-app-id>` with your Dusseldorf application ID. The token expires after a while, so you may need to run this command again later if you get authentication errors.

---

## EntraID App Registration Setup

To use `dssldrf login`, you need an Azure AD (EntraID) app registration. Here's what you need:

## EntraID App Registration Setup

To use `dssldrf login`, you need an Azure AD (EntraID) app registration. Here's what you need:

### 1. Create App Registration (if you don't have one)

1. Go to [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Name: `Dusseldorf CLI` (or anything you prefer)
4. Supported account types: Choose based on your needs
5. Redirect URI: Leave blank (we're using device code flow)
6. Click **Register**

### 2. Configure as Public Client

1. In your app registration, go to **Authentication**
2. Scroll to **Advanced settings** → **Allow public client flows**
3. Set to **Yes**
4. Click **Save**

### 3. Add API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **APIs my organization uses**
4. Find and select your Dusseldorf API app registration
5. Select the appropriate permissions (typically `user_impersonation` or similar)
6. Click **Add permissions**
7. (Optional) Click **Grant admin consent** if you have admin rights

### 4. Get Your IDs

1. Go to **Overview** in your app registration
2. Copy the **Application (client) ID** — this is your `--client-id`
3. Copy the **Directory (tenant) ID** — this is your `--tenant-id`

### 5. Configure CLI

Now run:

```bash
dssldrf config set --client-id <paste-client-id> --tenant-id <paste-tenant-id>
```

Then you can use `dssldrf login` anytime!

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
# Or short version:
dssldrf zone -a mytest
```

This creates `mytest.yourdomain.net` (using the domain you configured).

### List your zones

See "List zones" above - just run:

```bash
dssldrf zone
```

### View requests for a zone

```bash
dssldrf req mytest --limit 20
# Or short version:
dssldrf req mytest -n 20
```

This shows the last 20 requests received by `mytest.yourdomain.net`.

### Delete a zone

```bash
dssldrf zone --delete mytest
# Or short version:
dssldrf zone -d mytest
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
- On Windows: The installer should have added it automatically, but you may need to restart PowerShell

### Authentication errors

Your token has probably expired. Run the token command again (see Setup step 1 above).

### "Missing token" error

You forgot to set `DSSLDRF_AUTH_TOKEN`. Run the command from Setup step 1.

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


