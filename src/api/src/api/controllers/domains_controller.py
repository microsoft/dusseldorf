# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import logging

from ..models.domain import Domain, DomainCreate
from ..dependencies import get_current_user, get_db
from ..helpers.dns_helper import DnsHelper
from ..services.permissions import PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/domains",
    tags=["Domains"]
)

# GET /domains
@router.get("", response_model=List[str])
async def get_all_domains(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)  
):
    """Get all domains with optional pagination"""
    query = {
        "$or": [
            {
                "users": {
                    "$in": [current_user["preferred_username"]]
                    }
            },
            {
                "owner": current_user["preferred_username"]
            },
            {
                "owner": "dusseldorf"
            }
        ]
    }

    all_domains = await db.domains.find(query).skip(skip).limit(limit).to_list(None)

    return [dom['domain'] for dom in all_domains]
    


# GET /domains/{fqdn}
@router.get("/{fqdn}", response_model=Domain)
async def get_domain(
    fqdn: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Get a specific domain, given its fqdn"""

    query = {
        "$or": [
            {
                "domain": fqdn,
                "owner": "dusseldorf"
            },
            {
                "domain": fqdn,
                "users": {
                    "$in": [current_user["preferred_username"]]
                    }
            },
            {
                "domain": fqdn,
                "owner": current_user["preferred_username"]
            }
            
        ]
    }

    # Validate domain permissions
    if not permission_service.validate_user_domain(current_user["preferred_username"], fqdn):
        logger.warning(f"User {current_user['preferred_username']} attempted to view domain {fqdn}")

    domain = await db.domains.find_one(query)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return Domain(**domain)

# POST /domains
# Creates a new domain (with optional users)
@router.post("", response_model=Domain)
async def create_domain(
    req: DomainCreate,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new domain"""
    # Validate domain name
    if not DnsHelper.validate_domain_name(req.domain):
        raise HTTPException(status_code=400, detail="Invalid domain name")

    # Check existing and confirm domain isn't part of larger domain
    domains = await db.domains.find({}).to_list(None)
    for domain in domains:
        normalize_fqdn = req.domain.lower()
        normalize_domain = domain["domain"].lower()
        if normalize_fqdn.endswith("." + normalize_domain) or normalize_fqdn == normalize_domain:
            raise HTTPException(status_code=400, detail="Invalid domain name")

    new_domain = req.model_dump()
    new_domain["owner"] = current_user["preferred_username"]
    new_domain["users"] = req.users if req.users else []
    new_domain["users"].append(current_user["preferred_username"])
    
    result = await db.domains.insert_one(new_domain)
    if not result.inserted_id:
        raise HTTPException(status_code=400, detail="Create domain failed")
    
    new_domain["_id"] = result.inserted_id
    logger.warning(f"User {current_user['preferred_username']} created domain {req.domain}")
    return Domain(**new_domain)


# PUT /domains/{fqdn}
# Add a user to a domain
@router.put("/{fqdn}", response_model=Domain)
async def update_domain(
    fqdn: str,
    user: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Update an existing domain"""
    if not await permission_service.validate_domain_owner(fqdn, current_user["preferred_username"]):
        logger.warning(f"User {current_user['preferred_username']} attempted to add user {user} to domain {fqdn}")
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await db.domains.update_one(
        {"domain": fqdn},
        {"$push": {"users": user} }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found")
        
    updated = await db.domains.find_one({"domain": fqdn})
    logger.warning(f"User {current_user['preferred_username']} added user {user} to domain {fqdn}")
    return Domain(**updated)

@router.delete("/{fqdn}")
async def delete_domain(
    fqdn: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):   
    """Delete a domain"""
    if not await permission_service.validate_domain_owner(fqdn, current_user["preferred_username"]):
        logger.warning(f"User {current_user['preferred_username']} attempted to delete domain {fqdn}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check for existing zones using this domain
    if await db.zones.find_one({"domain": fqdn}):
        raise HTTPException(status_code=400, detail="Cannot delete domain with existing zones")
    
    result = await db.domains.delete_one({"domain": fqdn})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    logger.warning(f"User {current_user['preferred_username']} deleted domain {fqdn}")
    return {"status": "success"} 