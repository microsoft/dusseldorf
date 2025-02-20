# Use MCR Azure Linux Python image
FROM mcr.microsoft.com/azurelinux/base/python:3

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies
RUN tdnf -y update && tdnf -y install build-essential curl ca-certificates

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# 2025-02-06 TEMPORARY SELF-SIGNED CERT
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 356 -subj "/CN=DSSLDRK"
CMD ["uvicorn", "src.api.main:app", "--ssl-keyfile", "/app/key.pem", "--ssl-certfile", "/app/cert.pem", "--host", "0.0.0.0", "--port", "443"]

# Run the application
#CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "443"] 