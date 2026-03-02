# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
import logging

from models.auth import AuthzPermission, Permission, PermissionRequest
from services.permissions import PermissionService
from dependencies import get_current_user, get_db, get_log_context

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
    current_user: Dict[str, Any] = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    correlation_id = current_user.get("correlation_id", "unknown")
    can_assign_roles: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        current_user["preferred_username"],
        Permission.ASSIGNROLES,
        correlation_id
    )

    if not can_assign_roles:
        logger.warning(
            "authz_list_access_denied",
            extra=get_log_context(current_user, zone=zone, operation="get_authz_list")
        )
        raise HTTPException(status_code=403, detail="Unauthorized")

    authz_list = await db.zones.find_one({"fqdn": zone}, {"_id": 0, "authz": 1})
    if not authz_list:
        logger.info(
            "authz_list_not_found",
            extra=get_log_context(current_user, zone=zone, operation="get_authz_list")
        )
        raise HTTPException(status_code=400, detail="Zone permissions not found")
 
    logger.info(
        "authz_list_retrieved",
        extra=get_log_context(
            current_user,
            zone=zone,
            operation="get_authz_list",
            count=len(authz_list.get("authz", []))
        )
    )
    return [AuthzPermission(**authz) for authz in authz_list["authz"]]



# GET /authz/{zone}/{user}
# gets the permission for a given user on a given zone
@router.get("/{zone}/{user}", response_model=AuthzPermission)
async def get_authz_permission(
    zone: str,
    user: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    # Users can view their own permissions or need ASSIGNROLES to view others

    correlation_id = current_user.get("correlation_id", "unknown")
    can_assign_roles: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        current_user["preferred_username"],
        Permission.ASSIGNROLES,
        correlation_id
    )

    if user != current_user["preferred_username"] and can_assign_roles is False:
        logger.warning(
            "authz_user_access_denied",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="get_authz_user",
                target_user=user
            )
        )
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    user_auth = await db.zones.find_one(
        {"fqdn": zone, "authz.alias": user},
        {"_id": 0, "authz": {"$elemMatch": {"alias": user}}}
    )
    if user_auth:
        logger.info(
            "authz_user_retrieved",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="get_authz_user",
                target_user=user
            )
        )
        return AuthzPermission(**user_auth["authz"][0])

    logger.info(
        "authz_user_not_found",
        extra=get_log_context(
            current_user,
            zone=zone,
            operation="get_authz_user",
            target_user=user
        )
    )
    raise HTTPException(status_code=400, detail="User not found")



# POST /authz/{zone}
# grants a permission to a user on a given zone
@router.post("/{zone}")
async def grant_permission(
    zone: str,
    perm_req: PermissionRequest,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    correlation_id = current_user.get("correlation_id", "unknown")

    # Validate permission data
    if not perm_req.permission in permission_map_text.values():
        logger.warning(
            "invalid_permission_request",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="grant_permission",
                target_user=perm_req.alias,
                requested_permission=perm_req.permission
            )
        )
        raise HTTPException(status_code=400, detail="Invalid permission")

    user_id = current_user["preferred_username"]

    # Must be able to assign roles
    can_assign_roles: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        user_id,
        Permission.ASSIGNROLES,
        correlation_id
    )
    
    if not can_assign_roles:
        logger.warning(
            "grant_permission_denied",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="grant_permission",
                target_user=perm_req.alias
            )
        )
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
    is_owner: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        user_id,
        Permission.OWNER,
        correlation_id
    )
    
    if is_owner is False and permission_to_give == Permission.OWNER:
        logger.warning(
            "grant_owner_denied",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="grant_permission",
                target_user=perm_req.alias,
                requested_permission="owner"
            )
        )
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
            logger.exception(
                "grant_permission_update_failed",
                extra=get_log_context(
                    current_user,
                    zone=zone,
                    operation="grant_permission",
                    target_user=perm_req.alias
                )
            )
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
            logger.exception(
                "grant_permission_insert_failed",
                extra=get_log_context(
                    current_user,
                    zone=zone,
                    operation="grant_permission",
                    target_user=perm_req.alias
                )
            )
            raise HTTPException(status_code=400, detail="Failed to update permissions")

    logger.info(
        "permission_granted",
        extra=get_log_context(
            current_user,
            zone=zone,
            operation="grant_permission",
            target_user=perm_req.alias,
            permission=int(permission_to_give)
        )
    )
    return {"status": "success"}



# DELETE /authz/{zone}/{user}
# revokes a permission from a user on a given zone
@router.delete("/{zone}/{user}")
async def remove_permission(
    zone: str,
    user: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    user_id = current_user["preferred_username"]
    correlation_id = current_user.get("correlation_id", "unknown")

    # First, current_user must have correct role to remove any permissions
    can_remove_users: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        user_id,
        Permission.ASSIGNROLES,
        correlation_id
    )
    
    if not can_remove_users:
        logger.warning(
            "revoke_permission_denied",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="revoke_permission",
                target_user=user
            )
        )
        raise HTTPException(status_code=403, detail="Unauthorized")

    current_permission = await db.zones.find_one(
        {"fqdn": zone, "authz.alias": user}, 
        {"_id": 0, "authz": {"$elemMatch": {"alias": user}}})
    if not current_permission:
        logger.warning(
            "revoke_permission_not_found",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="revoke_permission",
                target_user=user
            )
        )
        raise HTTPException(status_code=404, detail="Permission not found")

    permission_to_remove:int = current_permission["authz"][0]["authzlevel"]

    # Only owners can remove owner permissions
    current_user_is_owner: bool = await permission_service.has_at_least_permissions_on_zone(
        zone,
        user_id,
        Permission.OWNER,
        correlation_id
    )
    
    if permission_to_remove == Permission.OWNER and current_user_is_owner is False:
        logger.warning(
            "revoke_owner_denied",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="revoke_permission",
                target_user=user
            )
        )
        raise HTTPException(status_code=403, detail="Only owners can remove owner permissions")

    if not await db.zones.update_one({"fqdn": zone}, {"$pull": {"authz": {"alias": user}}}):
        logger.exception(
            "revoke_permission_failed",
            extra=get_log_context(
                current_user,
                zone=zone,
                operation="revoke_permission",
                target_user=user
            )
        )
        raise HTTPException(status_code=400, detail="Failed to revoke permissions")

    logger.info(
        "permission_revoked",
        extra=get_log_context(
            current_user,
            zone=zone,
            operation="revoke_permission",
            target_user=user
        )
    )

    return {"status": "success"} 