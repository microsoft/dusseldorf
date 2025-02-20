# Dusseldorf API v2

A FastAPI-based DNS Management API that provides functionality for managing domains, zones, and DNS records.

## Features

- Domain Management
- Zone Management
- DNS Record Management
- Authorization & Permissions
- Public Zone Access
- Health Monitoring
- Request Processing

## Prerequisites

- Python 3.8+
- MongoDB
- Azure AD (for authentication)

## Installation

### Option 1: Local Installation

1. Clone the repository:
bash
git clone <repository-url>
cd dusseldorf-api

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=dusseldorf

# Azure AD Configuration
AZURE_AD_TENANT_ID=your_tenant_id
AZURE_AD_CLIENT_ID=your_client_id
AZURE_AD_CLIENT_SECRET=your_client_secret

# API Configuration
API_VERSION=2.0.0
ENVIRONMENT=development
```

5. Set up Azure AD application and configure environment variables.

### Option 2: Docker Installation

1. Build the Docker image:
```bash
docker build -t dusseldorf-api .
```

2. Create a docker-compose.yml file:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - MONGODB_DB_NAME=dusseldorf
      - AZURE_AD_TENANT_ID=your_tenant_id
      - AZURE_AD_CLIENT_ID=your_client_id
      - AZURE_AD_CLIENT_SECRET=your_client_secret
      - API_VERSION=2.0.0
      - ENVIRONMENT=production
    depends_on:
      - mongo
    networks:
      - dusseldorf-network

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - dusseldorf-network

networks:
  dusseldorf-network:
    driver: bridge

volumes:
  mongodb_data:
```

3. Start the services:
```bash
docker-compose up -d
```

4. Check the logs:
```bash
docker-compose logs -f api
```

5. Stop the services:
```bash
docker-compose down
```

### Docker Development

For development with hot-reload:

1. Update docker-compose.yml to mount the source code:
```yaml
services:
  api:
    volumes:
      - ./src:/app/src
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Start the development environment:
```bash
docker-compose up -d
```

## Running the API

1. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Structure

```
src/api/
├── controllers/           # Route handlers
│   ├── authz_controller.py       # Authorization endpoints
│   ├── default_controller.py     # Basic endpoints
│   ├── domains_controller.py     # Domain management
│   ├── health_controller.py      # Health checks
│   ├── payloads_controller.py    # DNS payload generation
│   ├── requests_controller.py    # Change requests
│   ├── rules_controller.py       # DNS rules
│   └── zones_controller.py       # Zone management
├── helpers/              # Utility functions
│   └── dns_helper.py            # DNS validation and utilities
├── models/              # Pydantic models
├── services/            # Business logic
└── main.py             # Application entry point
```

## Authentication

The API uses Azure AD for authentication. Most endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Permission Levels

- `READONLY`: Can view resources
- `WRITE`: Can modify resources
- `ASSIGNROLES`: Can manage permissions
- `OWNER`: Full control

## Public Endpoints

- `/` - API information
- `/health` - Basic health check
- `/robots.txt` - Robots file
- `/favicon.ico` - Favicon
- `/public/zones/` - Public zone listing

## Protected Endpoints

All other endpoints require authentication and appropriate permissions.

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
