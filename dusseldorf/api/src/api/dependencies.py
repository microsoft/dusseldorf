# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import Depends, HTTPException, status, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.errors import ConfigurationError, ConnectionFailure
from typing import Optional

from services.azure_ad import AzureADService
from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> str:
    """Get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    try:
        # Check scheme
        if authorization.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # Get the credentials provided
        token = authorization.credentials
        azure_ad = AzureADService()
        user = await azure_ad.validate_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_db() -> AsyncIOMotorClient:
    """Get database connection"""
    settings = get_settings()
    try:
        client = AsyncIOMotorClient(settings.DSSLDRF_CONNSTR, uuidRepresentation='standard')
        db = client.get_default_database()
        yield db
    except ConfigurationError as ce:
        print(f"ConfigurationError: {str(ce)}")
        raise HTTPException(status_code=500, detail="DB - Something is misconfigured")
    except ConnectionFailure as cf:
        print(f"ConnectionFailure: {str(cf)}")
        raise HTTPException(status_code=500, detail="DB - Connection failed")
    finally:
        pass
