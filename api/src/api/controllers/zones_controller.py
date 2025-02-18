# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
import logging

from ..models.zone import Zone, ZoneCreate
from ..models.auth import Permission
from ..dependencies import get_current_user, get_db
from ..helpers.dns_helper import DnsHelper
from ..services.permissions import PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/zones",
    tags=["Zones"]
)

MAX_ZONES = 100
LABEL_LENGTH = 12

# GET /zones
# gets all zones that user has some sort of permission on
@router.get("", response_model=List[Zone])
async def get_zones(
    domain: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Get all zones with optional domain filter"""
    query = {}
    if domain:
        query["domain"] = domain

    query["authz.alias"] = current_user["preferred_username"]
    user_accessible_zones = await db.zones.find(query).skip(skip).limit(limit).to_list(None)
    if not user_accessible_zones:
        return [] # no zones found for this user

    # Confirm user has at least RO perms on this zone
    confirmed_zones = []
    for zone_check in user_accessible_zones:
        if await permission_service.has_at_least_permissions_on_zone(zone_check["fqdn"], current_user["preferred_username"], Permission.READONLY):
            confirmed_zones.append(zone_check)

    return [Zone(**zone) for zone in confirmed_zones]

# GET /zones/{fqdn}
# gets specific data about zone 
@router.get("/{fqdn}", response_model=Zone)
async def get_zone(
    fqdn: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Get a specific zone by ID"""
    # see if the zone exists
    fqdn = fqdn.lower()

    zone_result = await db.zones.find_one({"fqdn": fqdn})
    if not zone_result:
        raise HTTPException(status_code=404, detail="Zone not found")

    # zone exists, check if user has any permissions on it 
    can_read:bool =  await permission_service.has_at_least_permissions_on_zone(
                                fqdn, 
                                current_user["preferred_username"], 
                                Permission.READONLY)
    
    if not can_read:
        logger.warning(f"User {current_user['preferred_username']} attempted to access zone {fqdn}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # zone exists, and we have permissions
    return Zone(**zone_result)


# POST /zones
# creates a new zone, or more than one (if num is specified)
@router.post("", response_model=List[Zone])
async def create_zone(
    req: ZoneCreate,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    # Set initial domain to "public" fqdn
    query_result = await db.domains.find_one({"owner": "dusseldorf"})
    domain = query_result["domain"]

    user_id:str = current_user["preferred_username"]

    # request has speficied a domain name, see if we're allowed to create zones in it
    if req.domain:
        if not await permission_service.validate_user_domain(user_id, req.domain):
            logger.warning(f"403: User {user_id} attempted to create zone({req.zone}) on domain({req.domain})")
            raise HTTPException(status_code=403, detail="Unauthorized")
        domain = req.domain

    # Validate the zone name
    if req.zone:
        req.zone = req.zone.lower()
        if not DnsHelper.validate_zone_name(req.zone, domain):
            logger.warning(f"400: Invalid zone: {req.zone} for domain {domain}")
            raise HTTPException(status_code=400, detail="Invalid zone name")
        new_zone_fqdn = f"{req.zone}.{domain}".lower()

        # Check existing and confirm not part of larger zone
        all_zones = await db.zones.find({}).to_list(None)
        for existing_zone in all_zones:
            lower_zone = existing_zone["fqdn"].lower()
            if new_zone_fqdn.endswith("." + lower_zone) or new_zone_fqdn == lower_zone:
                logger.warning(f"403: User {user_id} attempted to create zone({req.zone}), which is a subdomain of {existing_zone['fqdn']}")
                raise HTTPException(status_code=403, detail="Zone name not allowed")

        zone_request_dict = {
            "fqdn": new_zone_fqdn,
            "domain": domain,
            "expiry": None,
            "authz": [
                {
                    "alias": user_id,
                    "authzlevel": Permission.OWNER
                }
            ]
        }
        result = await db.zones.insert_one(zone_request_dict)
        if result.inserted_id:
            logger.info(f"User {user_id} created zone({new_zone_fqdn})")
            logger.error(result)
            return [Zone(**zone_request_dict)]

    if req.num > 0 and req.num <= MAX_ZONES:
        insert_results = []
        for i in range(req.num):
            zone_name = DnsHelper.generate_label(LABEL_LENGTH)
            new_zone_name = f"{zone_name}.{domain}"
            while True:
                # Confirm generated zone name doesn't already exist
                validation_filter = {
                    "fqdn": new_zone_name
                }
                if not await db.zones.find_one(validation_filter):
                    break
                new_zone_name = f"{DnsHelper.generate_label(LABEL_LENGTH)}.{domain}"
            
            zone_request_dict = {
                "fqdn": new_zone_name,
                "domain": domain,
                "expiry": None,
                "authz": [
                    {
                        "alias": current_user["preferred_username"],
                        "authzlevel": Permission.OWNER
                    }
                ]
            }
            result = await db.zones.insert_one(zone_request_dict)
            if result.inserted_id:
                logger.warning(f"User {current_user['preferred_username']} created domain {domain} zone {new_zone_name}")
                insert_results.append(zone_request_dict)

        return[Zone(**result) for result in insert_results]

    # if we're here, we failed to create a zone
    logger.exception("Failed to create zone")
    raise HTTPException(status_code=400, detail="Failed to add zone")


# DELETE /zones/{fqdn}
# deletes a zone
@router.delete("/{fqdn}")
async def delete_zone(
    fqdn: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    is_owner = await permission_service.has_at_least_permissions_on_zone(fqdn, current_user["preferred_username"], Permission.OWNER)
    if not is_owner:
        logger.warning(f"User {current_user['preferred_username']} attempted to delete zone {fqdn}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check for existing rules
    if await db.rules.find_one({"zone": fqdn}):
        raise HTTPException(status_code=400, detail="Cannot delete zone with existing rules")
    
    result = await db.zones.delete_one({"fqdn": fqdn})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    logger.warning(f"User {current_user['preferred_username']} deleted zone {fqdn}")
    return {"status": "success"}