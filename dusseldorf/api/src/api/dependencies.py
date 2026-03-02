# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import Depends, HTTPException, status, Header, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.errors import ConfigurationError, ConnectionFailure
from typing import Optional, Dict, Any
import logging

from services.azure_ad import AzureADService
from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

logger = logging.getLogger(__name__)

async def get_current_user(
    request: Request,
    authorization: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> Dict[Any, Any]:
    """Get current user from token"""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    if not authorization:
        logger.warning(
            "auth_failed_no_token",
            extra={"correlation_id": correlation_id}
        )
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    try:
        # Check scheme
        if authorization.scheme.lower() != "bearer":
            logger.warning(
                "auth_failed_invalid_scheme",
                extra={"scheme": authorization.scheme, "correlation_id": correlation_id}
            )
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # Get the credentials provided
        token = authorization.credentials
        azure_ad = AzureADService()
        user = await azure_ad.validate_token(token)
        if not user:
            logger.warning(
                "auth_failed_invalid_token",
                extra={"correlation_id": correlation_id}
            )
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Add correlation_id to user context for downstream logging
        user["correlation_id"] = correlation_id
        
        logger.info(
            "auth_success",
            extra={
                "user": user.get("preferred_username"),
                "correlation_id": correlation_id
            }
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "auth_exception",
            extra={"error": str(e), "correlation_id": correlation_id},
            exc_info=True
        )
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

def get_log_context(
    current_user: dict,
    zone: Optional[str] = None,
    operation: Optional[str] = None,
    **extra_fields
) -> Dict[str, Any]:
    """
    Build structured logging context dict with correlation ID, user, zone, and operation.
    
    Usage:
        logger.info(
            "zone_created",
            extra=get_log_context(current_user, zone="example.com", operation="create_zone")
        )
    """
    context = {
        "correlation_id": current_user.get("correlation_id", "unknown"),
        "user": current_user.get("preferred_username", "unknown"),
        "user_id": current_user.get("id", "unknown"),
    }
    
    if zone:
        context["zone"] = zone
    
    if operation:
        context["operation"] = operation
    
    # Merge any extra fields
    context.update(extra_fields)
    
    return context
