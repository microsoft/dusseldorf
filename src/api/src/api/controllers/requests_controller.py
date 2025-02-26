# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
import logging

from models.auth import Permission
from models.request import Request
from dependencies import get_current_user, get_db
from services.permissions import PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/requests",
    tags=["Requests"]
)

# GET /requests/{zone}
# gets all requests for a given zone, optionally filtered, paginated
@router.get("/{zone}", response_model=List[Request])
async def get_requests(
    zone: str,
    protocols: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Get requests for a zone"""
    can_read:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        current_user["preferred_username"], 
        Permission.READONLY)
    
    if not can_read:
        logger.warning(f"User {current_user['preferred_username']} attempted to access zone {zone} requests")
        raise HTTPException(status_code=403, detail="Unauthorized")

    query = { "zone": zone }
    
    if protocols:
        conv_protocols = [protocol.upper() for protocol in protocols.split(",")]
        query["protocol"] = {"$in": conv_protocols}

    requests = await db.requests.find(query).sort({"_id": -1, "time": -1}).skip(skip).limit(limit).to_list(None)
    if not requests:
        logger.debug(f"No requests found for zone {zone}")
        return [] # raise HTTPException(status_code=404, detail="Requests not found")

    return [Request(**request) for request in requests]


# GET /requests/{zone}/{timestamp}
# gets a specific request by zone and timestamp
@router.get('/{zone}/{timestamp}', response_model=Request)
async def get_request(
    zone: str, 
    timestamp: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    can_read:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        current_user["preferred_username"], 
        Permission.READONLY)
    
    if not can_read:
        logger.warning(f"User {current_user['preferred_username']} attempted to access zone {zone} timestamp {timestamp} request")
        raise HTTPException(status_code=403, detail="Unauthorized")

    results = await db.requests.find_one({"zone": zone, "time": int(timestamp)})
    if not results:
        raise HTTPException(status_code=404, detail="Request not found")

    return Request(**results)