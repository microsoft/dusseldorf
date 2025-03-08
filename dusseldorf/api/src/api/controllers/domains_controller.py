# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import logging

from models.domain import Domain, DomainCreate
from dependencies import get_current_user, get_db
from helpers.dns_helper import DnsHelper
from services.permissions import PermissionService

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