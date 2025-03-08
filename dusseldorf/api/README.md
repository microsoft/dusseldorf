# Dusseldorf API

This is the control plane of Dusseldorf, it is a a REST API implemented in Python3 using FastAPI.  

It allows an authenticated user to manage zones, rules and requests.

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
TODO: Get a connection string from Azure.


## Running the API

1. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/api/docs
- UI: http://localhost:8000/ui/

## API Structure

```
src/api/
├── controllers/           # Route handlers
│   ├── authz_controller.py       # Authorization endpoints
│   ├── default_controller.py     # Basic endpoints
│   ├── domains_controller.py     # Domain management
│   ├── payloads_controller.py    # payload generation
│   ├── requests_controller.py    # network requests
│   ├── rules_controller.py       # rules management
│   └── zones_controller.py       # Zone management
├── helpers/              # Utility functions
│   └── dns_helper.py            # DNS validation and utilities
├── models/              # Pydantic models
├── services/            # Business logic
├── ui/                  # Static UI copy
└── main.py             # Application entry point
```

## Authentication

The API uses Entra ID (formerly Azure AD) for authentication. Most endpoints require a valid JWT 
token in the Authorization header:

```
Authorization: Bearer <token>
```

