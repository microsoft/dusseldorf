# Stop execution on errors
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment..."

# Function to show help menu
function Show-Help {
    Write-Host "Usage: .\deploy.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -CertPath <path>      Provide custom SSL certificate directory"
    Write-Host "  -Override             Force overwrite existing SSL certificates"
    Write-Host "  -Help                 Show this help menu"
    exit 0
}

# Default values
$CERT_DIR = "$HOME\dusseldorf\certs"
$OVERRIDE = $false
$CUSTOM_CRT_FILE = ""
$CUSTOM_KEY_FILE = ""

# Parse command-line arguments
param (
    [string]$CertPath,
    [switch]$Override,
    [switch]$Help
)

if ($Help) { Show-Help }

if ($CertPath) { $CERT_DIR = $CertPath }
if ($Override) { $OVERRIDE = $true }

Write-Host "🔎 Using certificate directory: $CERT_DIR"

# Load .env file properly, ignoring comments and empty lines
if (Test-Path ".env") {
    Get-Content .env | Where-Object {$_ -match '^[^#]+'} | ForEach-Object {
        if ($_ -match "^(.*?)=(.*)$") {
            Set-Content -Path env:\$matches[1] -Value $matches[2]
        }
    }
} else {
    Write-Host "❌ ERROR: .env file not found! Exiting."
    exit 1
}

# Ensure required environment variables are set
$requiredVars = @("DSSLDRF_DOMAIN", "DSSLDRF_IPV4", "AZURE_CLIENT_ID", "AZURE_TENANT_ID", "ACR_NAME", "MONGODB_DB_NAME")
foreach ($var in $requiredVars) {
    if (-not (Get-Content env:\$var)) {
        Write-Host "❌ ERROR: $var is not set in the .env file"
        exit 1
    }
}

# Generate a random MongoDB username and password if not set
if (-not $env:MONGO_USERNAME) {
    $MONGO_USERNAME = "admin"
    Write-Host "Generated MongoDB username."
} else {
    $MONGO_USERNAME = $env:MONGO_USERNAME
}

if (-not $env:MONGO_PASSWORD) {
    $MONGO_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 12 | ForEach-Object {[char]$_})
    Write-Host "Generated MongoDB password."
} else {
    $MONGO_PASSWORD = $env:MONGO_PASSWORD
}

# Certificate paths
$DSSLDRF_TLS_CRT_FILE = "$CERT_DIR\tls.crt"
$DSSLDRF_TLS_KEY_FILE = "$CERT_DIR\tls.key"

# Handle existing certificate files
if (Test-Path $DSSLDRF_TLS_CRT_FILE -or Test-Path $DSSLDRF_TLS_KEY_FILE) {
    Write-Host "⚠️ SSL certificates already exist."

    if ($OVERRIDE) {
        $confirm = Read-Host "⚠️ This will overwrite existing certificates. Are you sure? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Overwrite canceled. Exiting."
            exit 1
        }
        Write-Host "🗑️ Removing existing certificates..."
        Remove-Item -Force $DSSLDRF_TLS_CRT_FILE, $DSSLDRF_TLS_KEY_FILE -ErrorAction Ignore
    } else {
        Write-Host "✅ Using existing certificates."
    }
}

# Ensure OpenSSL is installed
if (-not (Get-Command openssl -ErrorAction SilentlyContinue)) {
    Write-Host "🔍 OpenSSL not found. Installing via winget..."
    winget install --id OpenSSL.OpenSSL -e --source winget
}

# Generate SSL certificates if missing
if (!(Test-Path $DSSLDRF_TLS_CRT_FILE) -or !(Test-Path $DSSLDRF_TLS_KEY_FILE)) {
    Write-Host "🔑 Generating new SSL certificates..."
    openssl req -newkey rsa:2048 -nodes -keyout $DSSLDRF_TLS_KEY_FILE -x509 -days 365 -out $DSSLDRF_TLS_CRT_FILE -subj "/CN=localhost"
}

# Check if already logged into Azure ACR
if ($env:ACR_NAME) {
    Write-Host "🔎 Checking Azure ACR login status..."
    if (az acr show --name $env:ACR_NAME --query "loginServer" -o none 2>$null) {
        Write-Host "✅ Already logged into ACR: $env:ACR_NAME"
    } else {
        Write-Host "🔐 Logging into Azure..."
        az login --use-device-code
        az acr login --name $env:ACR_NAME
    }
}

# Pull the latest Docker images
Write-Host "📦 Pulling latest Docker images..."
docker-compose pull

# Start the services with environment variables passed at runtime
Write-Host "🚀 Starting services..."
$env:DSSLDRF_TLS_CRT_FILE = $DSSLDRF_TLS_CRT_FILE
$env:DSSLDRF_TLS_KEY_FILE = $DSSLDRF_TLS_KEY_FILE
$env:MONGO_USERNAME = $MONGO_USERNAME
$env:MONGO_PASSWORD = $MONGO_PASSWORD

docker-compose up -d

# Run database initialization
Write-Host "🗄️ Initializing MongoDB..."
Write-Host "Ensuring dependencies are installed..."
python -m pip install motor
python init_database.py --domain $env:DSSLDRF_DOMAIN --ips $env:DSSLDRF_IPV4

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Database initialization failed!"
    exit 1
} else {
    Write-Host "✅ Database initialized successfully!"
}

Write-Host "🎉 Deployment completed successfully!"
