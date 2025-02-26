# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict

from dependencies import get_current_user, get_db

router = APIRouter()

@router.get("/health")
async def health_check(
    db: AsyncIOMotorClient = Depends(get_db)
    # No token check needed - this is a public endpoint
):
    """Basic health check endpoint for the API and MongoDB connection"""
    try:
        # Test MongoDB connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Dict:
    """Detailed health check with system metrics - authenticated users only"""
    try:
        # Get MongoDB stats
        db_stats = await db.command("dbStats")
        
        # Get collection counts
        domains_count = await db.domains.count_documents({})
        zones_count = await db.zones.count_documents({})
        rules_count = await db.rules.count_documents({})
        
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "stats": db_stats,
                "collections": {
                    "domains": domains_count,
                    "zones": zones_count,
                    "rules": rules_count
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        ) 