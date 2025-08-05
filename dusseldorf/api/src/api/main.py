# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

import os
import uvicorn

# Azure Monitor OpenTelemetry
from azure.monitor.opentelemetry import configure_azure_monitor
if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from controllers.default_controller import router as default_router
from controllers.authz_controller import router as authz_router
from controllers.domains_controller import router as domains_router
# from controllers.health_controller import router as health_router
from controllers.requests_controller import router as requests_router
from controllers.rules_controller import router as rules_router
from controllers.zones_controller import router as zones_router

if os.environ.get("ENVIRONMENT") != "development":
    if not os.environ.get("API_TLS_CRT_FILE"):
        raise Exception("API_TLS_CRT_FILE not found in environment variables")
    if not os.environ.get("API_TLS_KEY_FILE"):
        raise Exception("API_TLS_KEY_FILE not found in environment variables")

dusseldorf = FastAPI()

@dusseldorf.get("/")
async def ui_redirect():
    # Redirect to /ui
    return RedirectResponse(url="/ui", status_code=302)

app = FastAPI(
    title="Dusseldorf API",
    description="Dusseldorf Management API",
    
    version="2025.3.2",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1
    },
    root_path="/api",
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
app.include_router(domains_router)
app.include_router(requests_router)
app.include_router(rules_router)
app.include_router(zones_router)
app.include_router(default_router)
# app.include_router(health_router)

dusseldorf.mount("/api", app)
dusseldorf.mount("/ui", StaticFiles(directory="./ui", html=True), name="ui")

if os.environ.get("ENVIRONMENT") == "development":
    uvicorn.run(dusseldorf, host="0.0.0.0", port=int(os.environ.get("API_PORT", 10443)))
else:
    uvicorn.run(dusseldorf, host="0.0.0.0", port=int(os.environ.get("API_PORT", 10443)), ssl_keyfile=os.environ.get("API_TLS_KEY_FILE"), ssl_certfile=os.environ.get("API_TLS_CRT_FILE"))
