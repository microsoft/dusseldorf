# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from enum import IntEnum
from fastapi import Depends
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from models.auth import AuthzPermission, Permission
from dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)

class PermissionService:
    def __init__(self, db: AsyncIOMotorClient = Depends(get_db)):
        self.db = db

    async def has_at_least_permissions_on_zone(
        self,
        zone: str,
        user_id: str,
        min_permission: IntEnum = Permission.READONLY
    ) -> bool:
        """Check if user has at least the specified permission level on zone"""
        logger.error(f"has_at_least_permissions_on_zone({zone}, {user_id}, {min_permission})")

        perm_check = await self.db.zones.find_one(
            {"fqdn": zone, "authz.alias": user_id},
            {"_id": 0, "authz": {"$elemMatch": {"alias": user_id, "authzlevel": { "$gte": min_permission }}}}
        )
        return len(perm_check)

    async def get_user_zones(self, user_id: str) -> List[str]:
        """Get all zones where user has any permission"""
        cursor = self.db.authz.find({"user_id": user_id})
        zones = []
        async for doc in cursor:
            zones.append(doc["zone"])
        return zones

    async def validate_user_domain(self, user: str, domain: str) -> bool:
        query = {
            "$or": [
                {
                    "domain": domain,
                    "users": {
                        "$in": [user]
                    }
                },
                {
                    "domain": domain,
                    "owner": user
                },
                {
                    "domain": domain,
                    "owner": "dusseldorf"
                }
            ]
        }

        if await self.db.domains.find_one(query):
            return True
        return False

    async def validate_domain_owner(self, domain: str, owner: str) -> bool:
        if await self.db.domains.find_one({"domain": domain, "owner": owner}):
            return True
        return False