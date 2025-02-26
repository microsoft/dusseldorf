# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import logging

from ..models.auth import AuthzPermission, Permission, PermissionRequest
from ..services.permissions import PermissionService
from ..dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/authz",
    tags=["Authorization"]
)

permission_map_text = {
    Permission.READONLY: "readonly",
    Permission.READWRITE: "readwrite",
    Permission.ASSIGNROLES: "assignroles",
    Permission.OWNER: "owner"
}

# GET /authz/{zone}
# gets all permissions for a given zone
@router.get("/{zone}", response_model=List[AuthzPermission])
async def get_permissions_for_zone(
    zone: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    can_assign_roles:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        current_user["preferred_username"], 
        Permission.ASSIGNROLES)

    if not can_assign_roles:
        logger.warning(f"User {current_user['preferred_username']} attempted to access permissions for zone {zone}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    authz_list = await db.zones.find_one({"fqdn": zone}, {"_id": 0, "authz": 1})
    if not authz_list:
        raise HTTPException(status_code=400, detail="Zone permissions not found")
    
    return [AuthzPermission(**authz) for authz in authz_list["authz"]]



# GET /authz/{zone}/{user}
# gets the permission for a given user on a given zone
@router.get("/{zone}/{user}", response_model=AuthzPermission)
async def get_authz_permission(
    zone: str,
    user: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    # Users can view their own permissions or need ASSIGNROLES to view others

    can_assign_roles:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        current_user["preferred_username"], 
        Permission.ASSIGNROLES)

    if user != current_user["preferred_username"] and can_assign_roles == False:
        logger.warning(f"User {current_user['preferred_username']} attempted to access permissions for user {user}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    user_auth = await db.zones.find_one(
        {"fqdn": zone, "authz.alias": user},
        {"_id": 0, "authz": {"$elemMatch": {"alias": user}}}
    )
    if user_auth:
        return AuthzPermission(**user_auth["authz"][0])

    raise HTTPException(status_code=400, detail="User not found")



# POST /authz/{zone}
# grants a permission to a user on a given zone
@router.post("/{zone}")
async def grant_permission(
    zone: str,
    perm_req: PermissionRequest,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    logger.critical(f"grant_permission({zone}, {perm_req})")

    # Validate permission data
    if not perm_req.permission in permission_map_text.values():
        raise HTTPException(status_code=400, detail="Invalid permission")

    user_id = current_user["preferred_username"]

    # Must be able to assign roles
    can_assign_roles:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        user_id, 
        Permission.ASSIGNROLES)
    
    if not can_assign_roles:
        logger.warning(f"User {user_id} attempted to grant permissions to {perm_req.alias} on zone {zone} without proper permissions")
        raise HTTPException(status_code=403, detail="Unauthorized")

    permission_to_give:Permission = Permission.READONLY
    
    # perm_req string to Permission enum
    if perm_req.permission == "owner":
        permission_to_give = Permission.OWNER
    elif perm_req.permission in ("read-write", "readwrite", "rw"):
        permission_to_give = Permission.READWRITE
    elif perm_req.permission in ("read-only", "readonly", "ro"):
        permission_to_give = Permission.READONLY
    elif perm_req.permission in ("assignroles"):
        permission_to_give = Permission.ASSIGNROLES
    

    # Only owners can give owner permissions
    is_owner:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        user_id, 
        Permission.OWNER)
    
    if is_owner == False and permission_to_give == Permission.OWNER:
        logger.warning(f"Non-owner {user_id} attempted to grant owner permission to {perm_req.alias} on zone {zone}")
        raise HTTPException(status_code=403, detail="Only owners can grant owner permissions")

    # all good, set the permission
    query = {
        "fqdn": zone,
        "authz.alias": perm_req.alias
        }
    if await db.zones.find_one(query):
        # we found one, so we need to update the permission for this user
        update_action = {
            "$set": {
                "authz.$.authzlevel": permission_to_give
                }
            }
        if not await db.zones.update_one(query, update_action):
            logger.exception(f"Failed to update permissions on {zone}")
            raise HTTPException(status_code=400, detail="Failed to update permissions")
    else:
        # didn't find the user in the authz table, adding them
        push_action = {
            "$push": {
                "authz": {
                    "alias": perm_req.alias,
                    "authzlevel": permission_to_give
                    }
                }
            }

        if not await db.zones.update_one({"fqdn": zone}, push_action):
            raise HTTPException(status_code=400, detail="Failed to update permissions")

    logger.info(f"User {user_id} granted permission {permission_to_give} to user {perm_req.alias} on zone {zone}")
    return {"status": "success"}



# DELETE /authz/{zone}/{user}
# revokes a permission from a user on a given zone
@router.delete("/{zone}/{user}")
async def remove_permission(
    zone: str,
    user: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    user_id = current_user["preferred_username"]

    # First, current_user must have correct role to remove any permissions
    can_remove_users:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        user_id, 
        Permission.ASSIGNROLES)
    
    if not can_remove_users:
        logger.warning(f"User {user_id} attempted to remove user {user} permissions without ASSIGNROLES")
        raise HTTPException(status_code=403, detail="Unauthorized")

    current_permission = await db.zones.find_one(
        {"fqdn": zone, "authz.alias": user}, 
        {"_id": 0, "authz": {"$elemMatch": {"alias": user}}})
    if not current_permission:
        logger.warning(f"User {user_id} attempted to remove user {user} permissions that do not exist")
        raise HTTPException(status_code=404, detail="Permission not found")

    permission_to_remove:int = current_permission["authz"][0]["authzlevel"]

    # Only owners can remove owner permissions
    current_user_is_owner:bool = await permission_service.has_at_least_permissions_on_zone(
        zone, 
        user_id, 
        Permission.OWNER)
    
    if permission_to_remove == Permission.OWNER and current_user_is_owner == False:
        logger.warning(f"Non-owner {user_id} attempted to remove user {user} owner permission")
        raise HTTPException(status_code=403, detail="Only owners can remove owner permissions")

    if not await db.zones.update_one({"fqdn": zone}, {"$pull": {"authz": {"alias": user}}}):
        logger.exception(f"Failed to revoke permissions for {user} on {zone} by {user_id}")
        raise HTTPException(status_code=400, detail="Failed to revoke permissions")

    logger.warning(f"User {user_id} removed user {user} permissions")

    return {"status": "success"} 