# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

#!/bin/bash

set -e  # Exit on error
set -o pipefail  # Catch pipeline failures

# Colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# File paths
ARM_TEMPLATE="ARM/dusseldorf-template.json"
ARM_PARAMETERS="ARM/dusseldorf-parameter.json"
VALUES_TEMPLATE="kubernetes/values-template.yaml"
GENERATED_VALUES_FILE="kubernetes/values.yaml"

# Flags
VERBOSE=false
SKIP_ENTRA_APP=false

# Function to check for required dependencies
check_dependency() {
    local cmd="$1"

    if ! command -v "$cmd" &>/dev/null; then
        echo -e "${RED}Error: '$cmd' is not installed.${NC}"
        echo -e "${YELLOW}Please install '$cmd' manually and re-run the script.${NC}"
        exit 1
    else
        echo -e "${GREEN}'$cmd' is installed.${NC}"
    fi
}

# Call the dependency check function before proceeding
echo -e "${YELLOW}Checking required dependencies...${NC}"
check_dependency "az"
check_dependency "jq"
check_dependency "envsubst"

# Help Menu
function show_help {
    echo -e "${GREEN}Usage:${NC} ./create_dusseldorf_resources.sh -p <prefix> -r <region> -g <resource-group> -s <subscription> -d <domain-name> [--tenant-id <tenant_id>] [--app-id <app_id>]"
    echo ""
    echo -e "${GREEN}Required parameters:${NC}"
    echo "  -p  Prefix for naming Azure resources (e.g., myproject)"
    echo "  -r  Azure region (e.g., eastus, westeurope)"
    echo "  -g  Azure Resource Group name"
    echo "  -s  Azure Subscription ID"
    echo "  -d  Domain Name for deployment (e.g., myproject.example.com)"
    echo ""
    echo -e "${YELLOW}Optional parameters:${NC}"
    echo "  --tenant-id <tenant_id>  Use an existing Azure Tenant ID instead of creating a new one"
    echo "  --app-id <app_id>  Use an existing Entra App ID instead of creating a new one"
    echo "  --acr-name <acr_name>  Use an existing Azure Container Registry name to pull images from"
    echo "  --deployment-name <deployment_name>  Specify a custom name for the ARM deployment"
    echo "  --verbose  Enable detailed logs"
    echo ""
    echo -e "${YELLOW}Example:${NC}"
    echo "  ./deploy-azure.sh -p myproject -r eastus -g my-resource-group -s 1234-abcd-5678 -d myproject.example.com"
    echo "  ./deploy-azure.sh -p myproject -r eastus -g my-resource-group -s 1234-abcd-5678 -d myproject.example.com --tenant-id <tenant_id> --app-id <app_id>"
    exit 0
}

# Default values
TAG="dusseldorf-default"
ACR_NAME=""
DEPLOYMENT_NAME="dusseldorf-deployment"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p) PREFIX="$2"; shift 2 ;;
        -r) REGION="$2"; shift 2 ;;
        -g) RESOURCE_GROUP="$2"; shift 2 ;;
        -s) SUBSCRIPTION_ID="$2"; shift 2 ;;
        -d) DOMAIN_NAME="$2"; shift 2 ;;
        --tenant-id) AZURE_TENANT_ID="$2"; shift 2 ;;
        --app-id) APP_ID="$2"; shift 2 ;;
        --acr-name) ACR_NAME="$2"; shift 2 ;;
        --deployment-name) DEPLOYMENT_NAME="$2"; shift 2 ;;
        --verbose) VERBOSE=true; shift ;;
        -h|--help) show_help ;;
        *) echo -e "${RED}Invalid option:${NC} $1"; show_help ;;
    esac
done

# Check required parameters for deployment
if [ -z "$PREFIX" ] || [ -z "$REGION" ] || [ -z "$RESOURCE_GROUP" ] || [ -z "$SUBSCRIPTION_ID" ] || [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}Error: Missing required parameters.${NC}"
    show_help
fi

# Enable verbose mode for Azure CLI
if $VERBOSE; then
    echo -e "${YELLOW}Verbose mode enabled.${NC}"
    set -x  # Enable script debugging
    az config set logging.enable=True
fi

# Ensure the resource group exists before proceeding
echo -e "${YELLOW}Ensuring resource group '$RESOURCE_GROUP' exists...${NC}"
if ! az group exists --name "$RESOURCE_GROUP"; then
    az group create --name "$RESOURCE_GROUP" --location "$REGION" --tags "project=$TAG"
    echo -e "${GREEN}Resource group '$RESOURCE_GROUP' created successfully.${NC}"
else
    echo -e "${GREEN}Resource group '$RESOURCE_GROUP' already exists.${NC}"
fi

# Check if the subnet already exists
SUBNET_NAME="$PREFIX-dusseldorf-vnet/aks-subnet"
EXISTING_SUBNET=$(az network vnet subnet show --resource-group "$RESOURCE_GROUP" --vnet-name "$PREFIX-dusseldorf-vnet" --name "aks-subnet" --query "id" -o tsv 2>/dev/null || echo "not_found")

if [[ "$EXISTING_SUBNET" != "not_found" ]]; then
    echo -e "${GREEN}Subnet '$SUBNET_NAME' already exists. Skipping creation.${NC}"
    SKIP_SUBNET_CREATION="true"
else
    echo -e "${YELLOW}Subnet '$SUBNET_NAME' does not exist. It will be created.${NC}"
    SKIP_SUBNET_CREATION="false"
fi

# Pass SKIP_SUBNET_CREATION as a parameter to the ARM template
# Deploy ARM template
echo -e "${YELLOW}Deploying Azure resources from ARM templates...${NC}"
az deployment group create \
    --mode "Incremental" \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$ARM_TEMPLATE" \
    --parameters "@$ARM_PARAMETERS" resourceGroup="$RESOURCE_GROUP" region="$REGION" skipSubnetCreation="$SKIP_SUBNET_CREATION" prefix="$PREFIX"

# Check if the deployment exists
EXISTING_DEPLOYMENT=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$DEPLOYMENT_NAME" --query "id" -o tsv 2>/dev/null || echo "not_found")

if [[ "$EXISTING_DEPLOYMENT" == "not_found" ]]; then
    echo -e "${RED}Error: Deployment '$DEPLOYMENT_NAME' not found. Ensure the deployment has been executed successfully.${NC}"
    exit 1
fi

# Fetch deployed resource details
echo -e "${YELLOW}Fetching deployed resource details...${NC}"
DEPLOYMENT_OUTPUT=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$DEPLOYMENT_NAME" --query "properties.outputs" -o json)

# Extract values using jq (handles missing values gracefully)
AKS_IP=$(az network public-ip show --name "$PREFIX-dusseldorf-publicip" --resource-group "$RESOURCE_GROUP" --query "ipAddress" -o tsv)
API_IP=$(az network public-ip show --name "$PREFIX-dusseldorf-api-ip" --resource-group "$RESOURCE_GROUP" --query "ipAddress" -o tsv)
AKS_IP_2=$(az network public-ip show --name "$PREFIX-dusseldorf-publicip2" --resource-group "$RESOURCE_GROUP" --query "ipAddress" -o tsv)
COSMOSDB_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.cosmosDBName.value // empty')
KEYVAULT_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.keyVaultName.value // empty')
AKS_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.aksName.value // empty')
ACR_NAME=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.acrName.value // empty')

# Fetch CosmosDB MongoDB-compatible connection string
echo -e "${YELLOW}Fetching CosmosDB MongoDB connection string...${NC}"
RAW_CONNSTR=$(az cosmosdb keys list --name "$COSMOSDB_NAME" --resource-group "$RESOURCE_GROUP" --type connection-strings --query "connectionStrings[?contains(description, 'MongoDB')].connectionString | [0]" -o tsv)

# Ensure the connection string is in the correct format
if [[ -z "$RAW_CONNSTR" ]]; then
    echo -e "${RED}Error: Could not retrieve a valid MongoDB-compatible connection string from CosmosDB.${NC}"
    exit 1
fi

export DSSLDRF_CONNSTR="$RAW_CONNSTR"
echo -e "${GREEN}✅ CosmosDB connection string retrieved successfully.${NC}"


# Ensure values exist before proceeding
if [[ -z "$AKS_IP" || -z "$COSMOSDB_NAME" || -z "$KEYVAULT_NAME" || -z "$AKS_NAME" || -z "$API_IP" || -z "$DSSLDRF_CONNSTR" ]]; then
    echo -e "${RED}Error: Some resource details could not be retrieved.${NC}"
    echo -e "${YELLOW}Listing all resources in '$RESOURCE_GROUP'...${NC}"
    az resource list --resource-group "$RESOURCE_GROUP" --output table
    exit 1
fi

echo -e "${GREEN}Deployed resource details retrieved successfully.${NC}"

# Display resource details to user
echo -e "${YELLOW}\n📌 Deployment Summary:${NC}"
echo "-------------------------------------------------------------"
printf "%-25s | %-40s\n" "Resource" "Value"
echo "-------------------------------------------------------------"
printf "%-25s | %-40s\n" "AKS Public IP" "$AKS_IP"
printf "%-25s | %-40s\n" "AKS Public IP 2" "$AKS_IP_2"
printf "%-25s | %-40s\n" "API Public IP" "$API_IP"
printf "%-25s | %-40s\n" "CosmosDB Name" "$COSMOSDB_NAME"
printf "%-25s | %-40s\n" "Key Vault Name" "$KEYVAULT_NAME"
printf "%-25s | %-40s\n" "AKS Name" "$AKS_NAME"
printf "%-25s | %-40s\n" "CosmosDB ConnStr" "$DSSLDRF_CONNSTR"
printf "%-25s | %-40s\n" "ACR Name" "$ACR_NAME"
echo "-------------------------------------------------------------"
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}Next step: Run the Helm deployment script.${NC}"


# Ensure the AKV name is set
if [[ -z "$KEYVAULT_NAME" ]]; then
    echo -e "${RED}Error: Key Vault name is not set.${NC}"
    exit 1
fi

# Assign "Certificate User" and "Secrets User" roles to AKS identity
AKS_MI_ID=$(az aks show --name "$PREFIX-dusseldorf-aks" --resource-group "$RESOURCE_GROUP" --query "identityProfile.kubeletidentity.clientId" -o tsv)

# Attach acr
echo -e "${YELLOW}Attaching ACR to AKS...${NC}"
az aks update --name "$PREFIX-dusseldorf-aks" --resource-group "$RESOURCE_GROUP" --attach-acr "$ACR_NAME"

echo -e "${YELLOW}Assigning Key Vault roles to AKS...${NC}"
az role assignment create --assignee "$AKS_MI_ID" --role "Certificate User" --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME"
az role assignment create --assignee "$AKS_MI_ID" --role "Secrets User" --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME"

echo -e "${GREEN}✅ AKS now has 'Certificate User' and 'Secrets User' roles in Key Vault.${NC}"

# Store CosmosDB connection string in AKV as 'msrv-connstr-jz'
echo -e "${YELLOW}Storing CosmosDB connection string in Key Vault...${NC}"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "msrv-connstr-jz" --value "$DSSLDRF_CONNSTR"

echo -e "${GREEN}✅ CosmosDB connection string stored in Key Vault as 'msrv-connstr-jz'.${NC}"


# Ensure the correct PyMongo version is installed
PYMONGO_VERSION=$(python3 -c "import pymongo; print(pymongo.version)" 2>/dev/null || echo "not_installed")

if [[ "$PYMONGO_VERSION" == "not_installed" || "$PYMONGO_VERSION" < "3.11" ]]; then
    echo -e "${RED}Error: PyMongo version is incompatible. Required: 3.11+.${NC}"
    echo -e "${YELLOW}Please run:${NC}"
    echo -e "${GREEN}pip install --upgrade 'pymongo>=3.11' motor${NC}"
    exit 1
fi


# Function to check Python dependencies
check_python_dependency() {
    local package="$1"

    if ! python3 -c "import $package" &>/dev/null; then
        echo -e "${RED}Error: Python package '$package' is not installed.${NC}"
        echo -e "${YELLOW}Please install it manually using:${NC}"
        echo -e "${GREEN}pip install $package${NC}"
        exit 1
    else
        echo -e "${GREEN}Python package '$package' is installed.${NC}"
    fi
}

# Ensure Python is installed
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: Python3 is not installed.${NC}"
    echo -e "${YELLOW}Please install Python3 before running this script.${NC}"
    exit 1
fi

# Ensure required Python dependencies are installed
echo -e "${YELLOW}Checking required Python dependencies...${NC}"
check_python_dependency "motor"
check_python_dependency "asyncio"

# Proceed with database initialization
echo -e "${YELLOW}Initializing CosmosDB with required tables...${NC}"
python3 init_database.py --domain "$DOMAIN_NAME" --ips "$AKS_IP"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Error: Failed to initialize the database.${NC}"
    exit 1
fi
echo -e "${GREEN}CosmosDB initialization completed successfully.${NC}"



# If user did not provide --tenant-id and --app-id, create a new Entra ID App
if [[ -z "$AZURE_TENANT_ID" || -z "$APP_ID" ]]; then
    echo -e "${YELLOW}Creating Entra ID App Registration...${NC}"
    APP_ID=$(az ad app create --display-name "$PREFIX-dusseldorf-app" --query "appId" -o tsv)
    AZURE_TENANT_ID=$(az ad app show --id "$APP_ID" --query "appOwnerTenantId" -o tsv)
    echo -e "${GREEN}Entra ID App created with Application ID: $APP_ID and Tenant ID: $AZURE_TENANT_ID${NC}"
else
    echo -e "${GREEN}Using provided Tenant ID: $AZURE_TENANT_ID and App ID: $APP_ID${NC}"
fi

# Generate values.yaml using envsubst
echo -e "${YELLOW}Generating Helm values.yaml file...${NC}"
export AZURE_TENANT_ID APP_ID AKS_IP API_IP COSMOSDB_NAME KEYVAULT_NAME ACR_NAME

cat <<EOF | envsubst > "$GENERATED_VALUES_FILE"
# Values for development environment

global:
  tenantID: "$AZURE_TENANT_ID"
  identityName: "" # Enter AKS Managed Identity
  identityClientIdAPI: "$APP_ID"
  identityTenantIdAPI: "$AZURE_TENANT_ID"
  dusseldorfDomain: "$DOMAIN_NAME"
  dusseldorfIPV4list: "$AKS_IP"
  dusseldorfIPV6list: ""
  dusseldorfMaxConnections: 100
  dusseldorfLogLevel: "debug"
  acrName: "$ACR_NAME"
  loadBalancerIP: "$AKS_IP"
  loadBalancerIPApi: "$API_IP"
  loadBalancerIP2: "$AKS_IP_2" # Enter second load balancer IP

listeners:
  listenerDNS:
    name: dns-listener
    port: 10053
    image: dusseldorf-listener-dns
    acrRepo: "$ACR_NAME/dusseldorf-listener-dns:latest"

  listenerHTTP:
    name: http-listener
    image: dusseldorf-listener-http
    acrRepo: "$ACR_NAME/dusseldorf-listener-http:latest"
    port: 10080

  listenerHTTPS:
    name: https-listener
    image: dusseldorf-listener-https
    acrRepo: "$ACR_NAME/dusseldorf-listener-http:latest"
    port: 10443
    certPath: "/mnt/secrets-store"
    keyVaultCertSecretName: "{keyVaultCertSecretName}"  

api:
  name: dusseldorf-api
  image: dusseldorf-api
  acrRepo: "$ACR_NAME/dusseldorf-api:latest"
  port: 443
  targetPort: 10443
  certPath: "/mnt/secrets-store"
  AZURE_API_TENANT_ID: "$AZURE_TENANT_ID"
  AZURE_API_CLIENT_ID: "$APP_ID"

secrets:
  keyVaultName: "$KEYVAULT_NAME"
  certSecretName: "dssldrf-test-cert"
  keyVaultSecretName: "dssldrf-connstr-cosmosdb"
  apiCertName: "dssldrf-test-cert"
EOF

echo -e "${GREEN}values.yaml file generated successfully.${NC}"
