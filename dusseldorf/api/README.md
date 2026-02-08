# Dusseldorf API

This is the control plane (CP) of Dusseldorf, it is implemented as a REST API in Python3 using FastAPI.  

It allows an authenticated user to manage their zones, rules and requests.  Unauthenticated users can
only perform a /ping to see if the server is up  and responding (it holds the current timestamp).

## Prerequisites

- Python 3.8+
- MongoDB
- Entra ID (for authentication)

## Installation

### Option 1: Local Installation

1. Create and activate a virtual environment for Python:

```bash
python3 -m venv venv
source venv/bin/activate 
```

Then, install the dependencies:

```bash
python3 -m pip install -r requirements.txt
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

## Logging and Observability

The CP provides comprehensive logging and auditing capabilities for operational visibility and security:

- **Correlation ID Middleware**: Every request receives a unique correlation ID for end-to-end tracing
- **Structured Logging**: Consistent log context with user, zone, operations, and custom fields
- **Permission Audit Trail**: All permission checks and denials are logged for security compliance
- **Request Tracing**: Integration with Azure Application Insights for advanced monitoring

For detailed information on logging configuration, usage patterns, and integration with monitoring tools, see [OBSERVABILITY.md](OBSERVABILITY.md).

## Authentication

The API uses Entra ID (formerly Azure AD) for authentication. Most endpoints require a valid JWT 
token in the Authorization header:

```
Authorization: Bearer <token>
```

