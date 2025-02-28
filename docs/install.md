# **Dusseldorf Deployment Guide**

This guide provides instructions for deploying the Dusseldorf system either locally using Docker Compose or on Azure using Helm charts.

---

## **📌 Prerequisites**

Ensure you have the following installed:

- **Docker Desktop** (for Windows/macOS) or **Docker Engine** (for Linux)
- **Docker Compose**
- **Azure CLI** (`az` command-line tool)
- **OpenSSL** (for generating SSL certificates)
- **Python 3.x** with `pip`
- **jq** (`sudo apt-get install jq` or `brew install jq`)
- **Helm** (`https://helm.sh/docs/intro/install/`)

---

## **🚀 Deployment Options**

### **1️⃣ Local Deployment**

For detailed local deployment instructions, navigate to the `docs/local` directory and refer to the `Readme.md` file.

#### **Step 1: Clone the Repository**
```sh
# Clone the repository and navigate into it
git clone <repo-url>
cd <repo-directory>
```

#### **Step 2: Build and Push Docker Images**

Before deploying locally, you need to build Docker images for each listener and API present in the `src/` directory and push them to your Azure Container Registry (ACR).

```sh
# Build Docker images
docker build -t <acr-name>.azurecr.io/dusseldorf-listener-http:latest src/listener-http
docker build -t <acr-name>.azurecr.io/dusseldorf-listener-https:latest src/listener-https
docker build -t <acr-name>.azurecr.io/dusseldorf-api:latest src/api

# Push Docker images to ACR
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/dusseldorf-listener-http:latest
docker push <acr-name>.azurecr.io/dusseldorf-listener-https:latest
docker push <acr-name>.azurecr.io/dusseldorf-api:latest
```

#### **Step 3: Follow Local Deployment Instructions**

Navigate to the `docs/local` directory and follow the instructions in the `Readme.md` file to complete the local deployment.

---

### **2️⃣ Azure Deployment**

For detailed Azure deployment instructions, navigate to the `docs/azure` directory and refer to the `readme.md` file.

#### **Step 1: Clone the Repository**
```sh
# Clone the repository and navigate into it
git clone <repo-url>
cd <repo-directory>
```

#### **Step 2: Build and Push Docker Images**

Before deploying to Azure, you need to build Docker images for each listener and API present in the `src/` directory and push them to your Azure Container Registry (ACR).

```sh
# Build Docker images
docker build -t <acr-name>.azurecr.io/dusseldorf-listener-http:latest src/listener-http
docker build -t <acr-name>.azurecr.io/dusseldorf-listener-https:latest src/listener-https
docker build -t <acr-name>.azurecr.io/dusseldorf-api:latest src/api

# Push Docker images to ACR
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/dusseldorf-listener-http:latest
docker push <acr-name>.azurecr.io/dusseldorf-listener-https:latest
docker push <acr-name>.azurecr.io/dusseldorf-api:latest
```

#### **Step 3: Follow Azure Deployment Instructions**

Navigate to the `docs/azure` directory and follow the instructions in the `readme.md` file to complete the Azure deployment.

---

## **🛠 Debugging & Troubleshooting**

For common issues and fixes, refer to the `Debugging & Troubleshooting` section in the respective deployment guide (`docs/local/Readme.md` for local deployment and `docs/azure/readme.md` for Azure deployment).

---

## **📖 Additional Commands**

### **Manually Running MongoDB Initialization**
If the database is not initialized correctly, you can run the script manually:
```sh
python3 init_database.py --domain "example.com" --ips "127.0.0.1"
```

### **Logging into Azure ACR (Manually)**
If needed, authenticate manually:
```sh
az login
az acr login --name <ACR_NAME>
```

### **Force Rebuild Containers**
If something is not working correctly:
```sh
docker-compose down -v
./deploy.sh  # or ./deploy.ps1 for Windows
```