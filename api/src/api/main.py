# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .controllers.default_controller import router as default_router
from .controllers.authz_controller import router as authz_router
# from .controllers.domains_controller import router as domains_router
# from .controllers.health_controller import router as health_router
from .controllers.requests_controller import router as requests_router
from .controllers.rules_controller import router as rules_router
from .controllers.zones_controller import router as zones_router

# SSL
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/app/cert.pem', keyfile='/app/key.pem')

app = FastAPI(
    title="Dusseldorf API",
    description="Dusseldorf Management API",
    
    version="2025.3.2",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(authz_router)
# app.include_router(domains_router) # soft delete :)
app.include_router(requests_router)
app.include_router(rules_router)
app.include_router(zones_router)
app.include_router(default_router)
# app.include_router(health_router)