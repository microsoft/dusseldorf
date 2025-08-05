# **Dusseldorf Local Deployment Guide**

> [!WARNING]
> These local deployment instructions are not actively maintained and do not reflect the current structure of
> the repository. It is recommended that you instead follow the devenv setup instructions from the `dusseldorf/`
> directory [here](https://github.com/microsoft/dusseldorf/tree/main/dusseldorf).

This guide provides instructions for deploying the Dusseldorf system locally using Docker Compose.

---

## **📌 Prerequisites**
Ensure you have the following installed:

- **Docker Desktop** (for Windows/macOS) or **Docker Engine** (for Linux)
- **Docker Compose**
- **Azure CLI** (`az` command-line tool)
- **OpenSSL** (for generating SSL certificates)
- **Python 3.x** with `pip`

For Windows users, **PowerShell 7+** is recommended.

---

## **🚀 Deployment Instructions**

### **1️⃣ Clone the Repository**
```sh
# Clone the repository and navigate into it
git clone <repo-url>
cd <repo-directory>
```

### **2️⃣ Generate Credentials & Certificates**

This step ensures that MongoDB credentials and SSL certificates are set up.

#### **Linux/macOS**:
```sh
./generate_credentials.sh --override  # Use --override to force regen
```

#### **Windows (PowerShell)**:
```powershell
./generate_credentials.ps1 -Override  # Use -Override to force regen
```

By default, certificates are generated in:
- **Linux/macOS:** `$HOME/dusseldorf/certs`
- **Windows:** `$HOME\dusseldorf\certs`

To specify a custom path:
```sh
./generate_credentials.sh --crt /custom/path/cert.crt --key /custom/path/key.key
```
```powershell
./generate_credentials.ps1 -CertPath "C:\custom\certs"
```

---

### **3️⃣ Deploy Services**

This will start all required services using Docker Compose.

#### **Linux/macOS**:
```sh
./deploy.sh
```

#### **Windows (PowerShell)**:
```powershell
./deploy.ps1
```

This will:
✅ Check if required environment variables are set.
✅ Generate missing MongoDB credentials if needed.
✅ Generate SSL certificates if missing.
✅ Authenticate with Azure ACR if needed.
✅ Pull the latest Docker images.
✅ Start all services using `docker-compose`.
✅ Run database initialization.

To specify a custom SSL certificate path:
```sh
./deploy.sh --crt /custom/path/cert.crt --key /custom/path/key.key
```
```powershell
./deploy.ps1 -CertPath "C:\custom\certs"
```

---

### **4️⃣ Verify Running Containers**
Check if all containers are running:
```sh
docker ps
```

To check logs for a specific service:
```sh
docker logs -f listener-http
```

To restart a container:
```sh
docker restart listener-http
```

To stop and remove all running services:
```sh
docker-compose down
```

To rebuild and restart services:
```sh
docker-compose build
./deploy.sh  # or ./deploy.ps1 for Windows
```

---

## **🛠 Debugging & Troubleshooting**

### **Common Issues & Fixes**

**1️⃣ Issue:** `command not found: az`
- ✅ **Fix:** Install Azure CLI from [here](https://aka.ms/installazurecli).

**2️⃣ Issue:** `MongoDB authentication error`
- ✅ **Fix:** Ensure `MONGO_USERNAME` and `MONGO_PASSWORD` are correctly set in `.env`.

**3️⃣ Issue:** `invalid mount config for type "bind"`
- ✅ **Fix:** Ensure **absolute paths** are used for SSL certificates in `.env`.

**4️⃣ Issue:** `Azure login prompts repeatedly`
- ✅ **Fix:** Run `az acr show --name <ACR_NAME>` to check if already logged in.

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

