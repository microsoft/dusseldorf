#!/bin/bash

set -e

echo "We are going to need some information to set up your development environment."
echo "----------------------------------------------------"
echo "We need the client ID and tenant ID of your Azure AD application that you want to use for your developer environment."
read -p "Azure Client ID (example: dc1b6b75-8167-4baf-9e75-d3d1f755de1b): " AZURE_CLIENT_ID
read -p "Azure Tenant ID (example: 72f988bf-86f1-41af-91ab-2d7cd011db47): " AZURE_TENANT_ID
echo "----------------------------------------------------"
echo "Setting up with client ID: $AZURE_CLIENT_ID and tenant ID: $AZURE_TENANT_ID"

mkdir -p env/
mkdir -p env/certs/
echo "Creating certificates..."
openssl req -newkey rsa:2048 -nodes -keyout "env/certs/tls.key" -x509 -days 365 -out "env/certs/tls.crt" -subj "/CN=localhost"
echo "Certificates created successfully."

echo "Making mongo files..."
mkdir -p env/mongo-data/
mkdir -p env/mongo-scripts/
MONGO_PASSWORD=$(openssl rand -hex 12)
cat <<EOF > env/mongo-scripts/init.js
db = db.getSiblingDB("dusseldorf");
db.createUser({
  user: "admin",
  pwd: "$MONGO_PASSWORD",
  roles: [{ role: "readWrite", db: "dusseldorf" }]
});

db.createCollection("domains");
db.createCollection("zones");
db.createCollection("requests");
db.createCollection("rules");

db.domains.createIndex({domain: 1}, { unique: true });
db.zones.createIndex({fqdn: 1}, { unique: true });
db.requests.createIndex({
  "zone": 1,
  "time": 1
});
db.domains.insertOne({"domain": "dusseldorf.local", "public_ips": ["172.18.0.9"], "owner": "dusseldorf"});
EOF

echo "Generating .env file..."
cat <<EOF > .env
# Dusseldorf Environment Variables
API_VERSION=1
ENVIRONMENT=development
AZURE_CLIENT_ID=$AZURE_CLIENT_ID
AZURE_TENANT_ID=$AZURE_TENANT_ID

MONGO_USERNAME=admin
MONGO_PASSWORD=$MONGO_PASSWORD
MONGO_DB_NAME=dusseldorf
MONGODB_DB_NAME=dusseldorf

DSSLDRF_TLS_CRT_FILE=./env/certs/tls.crt
DSSLDRF_TLS_KEY_FILE=./env/certs/tls.key
LSTNER_HTTP_PORT=443
LSTNER_HTTP_INTERFACE=0.0.0.0

LSTNER_DNS_PORT=10053
LSTNER_DNS_INTERFACE=0.0.0.0
LSTNER_DNS_UDP=false
EOF

echo "Generating react .env file..."
cat <<EOF > ui/.env
REACT_APP_CLIENT_ID=$AZURE_CLIENT_ID
REACT_APP_TENANT_ID=$AZURE_TENANT_ID
REACT_APP_API_HOST=http://localhost:8080/api
EOF
echo "Environment setup complete. You can now start running Dusseldorf with docker compose up."