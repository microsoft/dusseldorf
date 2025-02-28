#!/bin/bash

set -e  # Exit on any error

# Function to show help menu
function show_help {
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --crt <path>        Provide custom SSL certificate file"
    echo "  --key <path>        Provide custom SSL key file"
    echo "  --override          Force overwrite existing SSL certificates"
    echo "  --domain <domain>  Specify the domain for Let's Encrypt certificates"
    echo "  --email <email>    Specify the email for Let's Encrypt registration"
    echo "  --use-letsencrypt  Use Let's Encrypt for TLS certificates"
    echo "  --help              Show this help menu"
    exit 0
}

# Default values
CERT_DIR="/$HOME/dusseldorf/certs"
OVERRIDE=false
CUSTOM_CRT_FILE=""
CUSTOM_KEY_FILE=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --crt)
            CUSTOM_CRT_FILE="$2"
            shift 2
            ;;
        --key)
            CUSTOM_KEY_FILE="$2"
            shift 2
            ;;
        --override)
            OVERRIDE=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "❌ ERROR: Unknown option $1"
            show_help
            ;;
    esac
done

echo "🚀 Starting deployment..."

# Load .env file properly, ignoring comments and empty lines
if [ -f .env ]; then
    set -o allexport
    source <(grep -E -v '^(#|$)' .env)
    set +o allexport
else
    echo "❌ ERROR: .env file not found! Exiting."
    exit 1
fi

# Ensure required environment variables are set
REQUIRED_VARS=("DSSLDRF_DOMAIN" "DSSLDRF_IPV4" "AZURE_CLIENT_ID" "AZURE_TENANT_ID" "ACR_NAME" "MONGODB_DB_NAME")
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "❌ ERROR: $VAR is not set in the .env file"
        exit 1
    fi
done

# Generate a random MongoDB username and password if not set
if [ -z "$MONGO_USERNAME" ]; then
    MONGO_USERNAME="admin"
    echo "Generated MongoDB username."
fi

if [ -z "$MONGO_PASSWORD" ]; then
    MONGO_PASSWORD=$(openssl rand -hex 12)
    echo "Generated MongoDB password."
fi

# Handle certificate paths
if [ -n "$CUSTOM_CRT_FILE" ] && [ -n "$CUSTOM_KEY_FILE" ]; then
    echo "📄 Using provided certificate files:"
    echo "   🔹 CRT: $CUSTOM_CRT_FILE"
    echo "   🔹 KEY: $CUSTOM_KEY_FILE"
    DSSLDRF_TLS_CRT_FILE="$CUSTOM_CRT_FILE"
    DSSLDRF_TLS_KEY_FILE="$CUSTOM_KEY_FILE"
else
    echo "🔎 Checking SSL certificates in $CERT_DIR..."
    
    if [ -d "$CERT_DIR" ] && [ "$(ls -A $CERT_DIR 2>/dev/null)" ]; then
        echo "⚠️ SSL certificate directory already exists."
        if [ "$OVERRIDE" = true ]; then
            read -p "⚠️ This will overwrite existing certificates. Are you sure? (y/N): " CONFIRM
            if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
                echo "❌ Overwrite canceled. Exiting."
                exit 1
            fi
            echo "🗑️ Removing existing certificates..."
            rm -rf "$CERT_DIR"
        else
            echo "✅ Using existing certificates."
        fi
    fi

    mkdir -p "$CERT_DIR"
    DSSLDRF_TLS_CRT_FILE="$CERT_DIR/tls.crt"
    DSSLDRF_TLS_KEY_FILE="$CERT_DIR/tls.key"

    if [ ! -f "$DSSLDRF_TLS_CRT_FILE" ] || [ ! -f "$DSSLDRF_TLS_KEY_FILE" ]; then
        echo "🔑 Generating new SSL certificates in $CERT_DIR..."
        openssl req -newkey rsa:2048 -nodes -keyout "$DSSLDRF_TLS_KEY_FILE" -x509 -days 365 -out "$DSSLDRF_TLS_CRT_FILE" -subj "/CN=localhost"
    fi
fi

# Check if already logged into Azure ACR
if [ -n "$ACR_NAME" ]; then
    echo "🔎 Checking Azure ACR login status..."
    if az acr show --name "$ACR_NAME" --query "loginServer" -o none 2>/dev/null; then
        echo "✅ Already logged into ACR: $ACR_NAME"
    else
        echo "🔐 Logging into Azure..."
        az login --use-device-code
        az acr login --name "$ACR_NAME"
    fi
fi

# Pull the latest Docker images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Start the services with environment variables passed at runtime
echo "🚀 Starting services..."
DSSLDRF_TLS_CRT_FILE="$DSSLDRF_TLS_CRT_FILE" \
DSSLDRF_TLS_KEY_FILE="$DSSLDRF_TLS_KEY_FILE" \
MONGO_USERNAME="$MONGO_USERNAME" \
MONGO_PASSWORD="$MONGO_PASSWORD" \
docker-compose up -d

# Run database initialization
echo "🗄️ Initializing MongoDB..."
echo "Ensuring dependencies are installed..."
python3 -m pip install motor 
python3 init_database.py --domain "$DSSLDRF_DOMAIN" --ips "$DSSLDRF_IPV4"

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Database initialization failed!"
    exit 1
else
    echo "✅ Database initialized successfully!"
fi

echo "🎉 Deployment completed successfully!"
