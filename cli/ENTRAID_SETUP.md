# Entra ID App Registration Setup for Dusseldorf CLI

This guide helps you set up the Microsoft Entra ID app registration needed for `dssldrf login`.

## What You Need

The Dusseldorf CLI uses **device code flow** for authentication, which requires:
- A Microsoft Entra ID **public client application** (app registration)
- API permissions to access your Dusseldorf API

## Step-by-Step Setup

### 1. Create App Registration

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Fill in the form:
   - **Name**: `Dusseldorf CLI` (or your preferred name)
   - **Supported account types**: 
     - Choose **Accounts in this organizational directory only** (single tenant) if your Dusseldorf instance is for your org only
     - Choose **Accounts in any organizational directory** (multi-tenant) if multiple orgs will use it
   - **Redirect URI**: Leave blank (device code flow doesn't need one)
5. Click **Register**

### 2. Enable Public Client Flow

1. In your new app registration, click **Authentication** (left sidebar)
2. Scroll down to **Advanced settings**
3. Find **Allow public client flows**
4. Toggle it to **Yes**
5. Click **Save** at the top

### 3. Configure API Permissions

You need to grant the CLI app permission to call your Dusseldorf API.

1. Click **API permissions** (left sidebar)
2. Click **+ Add a permission**
3. Select **APIs my organization uses** tab
4. Search for and select your **Dusseldorf API** app registration
5. Select **Delegated permissions**
6. Check the permission scopes your Dusseldorf API exposes (typically `user_impersonation` or similar)
7. Click **Add permissions**
8. **(Optional but recommended)** Click **Grant admin consent for [Your Org]** if you're an admin
   - This allows all users to use the CLI without individual consent prompts

### 4. Get Your Configuration Values

1. Go to the **Overview** page of your app registration
2. Copy these two values:
   - **Application (client) ID** - a GUID like `12345678-1234-1234-1234-123456789abc`
   - **Directory (tenant) ID** - a GUID like `87654321-4321-4321-4321-cba987654321`

### 5. Configure the CLI

Run this command with your values:

```bash
dssldrf config set \
  --api-url https://your-dusseldorf-server/api \
  --domain yourdomain.net \
  --client-id <paste-your-client-id> \
  --tenant-id <paste-your-tenant-id>
```

Example:

```bash
dssldrf config set \
  --api-url https://dusseldorf.contoso.com/api \
  --domain dssldrf.net \
  --client-id 12345678-1234-1234-1234-123456789abc \
  --tenant-id 87654321-4321-4321-4321-cba987654321
```

### 6. Test Login

```bash
dssldrf login
```

You should see:
- A URL (like `https://microsoft.com/devicelogin`)
- A code (like `ABCD-EFGH`)
- Instructions to open the URL and enter the code

Follow the prompts to sign in with your Microsoft account.

Once authentication succeeds, your token is stored locally and you can use all `dssldrf` commands!

## Troubleshooting

### "AADSTS650053: The application is asking for a scope that doesn't exist"

Your Dusseldorf API app registration doesn't expose the right scopes, or you didn't add them in step 3.

**Fix:** 
1. Go to your **Dusseldorf API** app registration (not the CLI app)
2. Check **Expose an API** → ensure there's at least one scope defined
3. Go back to your **CLI app** → **API permissions**
4. Remove and re-add the permission

### "AADSTS7000218: The request body must contain the 'client_assertion' or 'client_secret' parameter"

Your app registration isn't configured as a public client.

**Fix:** Follow step 2 above again and ensure "Allow public client flows" is **Yes**.

### "User consent is required"

The CLI app permission wasn't granted admin consent, so each user must consent individually.

**Fix:**
1. Go to your **CLI app** → **API permissions**
2. Click **Grant admin consent for [Your Org]** (requires admin rights)

OR each user can consent on first login (they'll see a consent screen in the browser).

## Security Notes

- The CLI uses **device code flow**, which is designed for input-constrained devices and CLIs
- No client secret is needed (public client)
- Tokens are stored locally in `~/.dssldrf/config.json` - keep this file secure
- Consider setting `chmod 600 ~/.dssldrf/config.json` on Linux/macOS to restrict access

## Advanced: Using a Different Resource/Scope

By default, the CLI requests the scope `<client_id>/.default`. If your Dusseldorf API uses a different resource identifier:

1. Edit `cli/src/dssldrf_cli/main.py`
2. Find the `login_command()` function
3. Modify the `scopes` line:
   ```python
   scopes = [f"{config.client_id}/.default"]
   # Change to:
   scopes = ["api://<your-api-app-id>/.default"]
   ```

## Need Help?

If you're the Dusseldorf administrator and need to set up the API app registration too, see the main [Dusseldorf installation docs](../docs/install.md).
