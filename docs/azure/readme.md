# Düsseldorf Deployment Guide (Azure + Local Helm Charts)

This guide provides step-by-step instructions to deploy Düsseldorf on **Azure**, initialize **CosmosDB**, and deploy Helm charts using **local Helm files**.

---

## Prerequisites

Ensure you have the following installed before proceeding:

- **Azure CLI** (`az`)
- **jq** (`sudo apt-get install jq` or `brew install jq`)
- **Python 3** (`python3 --version`)
- **Pip Dependencies** (`pip install motor pymongo`)
- **Helm** (`https://helm.sh/docs/intro/install/`)

---

## Deployment Steps

### 1. **Run the Azure Deployment Script**

```bash
./deploy-azure.sh -p <prefix> -r <region> -g <resource-group> -s <subscription-id> -d <domain-name> --acr-name <acr-name>
```

**Example:**

```bash
./deploy-azure.sh -p myproject -r eastus -g my-resource-group -s 1234-abcd-5678 -d myproject.example.com --acr-name mycustomacr.azurecr.io
```

**This will:**

- Deploy an **AKS Cluster with Azure RBAC**.
- Assign **public IPs for AKS and API**.
- Set up **CosmosDB with MongoDB API**.
- Store **CosmosDB connection string in Key Vault (`msrv-connstr-jz`)**.
- Assign **"Certificate User" and "Secrets User" roles to AKV for AKS**.
- Generate a **values.yaml file** for Helm deployment.

---

### 2. **Initialize CosmosDB (If Needed Manually)**

If the deployment script does not run this automatically, run the following:

```bash
export DSSLDRF_CONNSTR=$(az keyvault secret show --name "msrv-connstr-jz" --vault-name "<keyvault-name>" --query value -o tsv)

python3 init_database.py --domain "<domain-name>" --ips "<AKS-IP>,<API-IP>"
```

---

### 3. **Run Helm Commands to Deploy the Application (Using Local Charts)**

Ensure your values file is populated as required prior to running this command

```bash
# Navigate to the directory containing local Helm charts
cd /path/to/local/helm/charts

# Deploy the application using local Helm charts
helm upgrade --install dusseldorf ./dusseldorf-chart -f kubernetes/values.yaml
```

---

## **Managing the Deployment**

### **Upgrade Deployment**

```bash
helm upgrade dusseldorf ./dusseldorf-chart -f kubernetes/values.yaml
```

### **Check Deployment Status**

```bash
helm list
kubectl get pods -n default
```

### **Uninstall the Application**

```bash
helm uninstall dusseldorf
```

---

## **Debugging Issues**

If you encounter any errors:

1️⃣ **Check Deployment Logs**

```bash
kubectl logs -l app=dusseldorf
```

2️⃣ **Check Helm Release Status**

```bash
helm status dusseldorf
```

3️⃣ **Verify Key Vault Secrets**

```bash
az keyvault secret show --name "<conn-str-name>" --vault-name "<keyvault-name>"
```

4️⃣ **Check CosmosDB Connection**

```bash
python3 init_database.py --domain "<domain-name>" --ips "<AKS-IP>,<API-IP>"
```
