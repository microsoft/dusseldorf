# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

import time
from fastapi import APIRouter, Response, Depends
from typing import Dict, Any
import logging
from dependencies import get_current_user, get_db, get_log_context

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Default"]
)
    
@router.get("/")
async def root() -> Dict[str, str]:
    """Default endpoint returning API information - public access"""
    return {
        "name": "Dusseldorf API",
        "version": "2.0.1",
        "status": "operational"
    }

@router.get("/ping")
async def pong(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, str|int]:
    """Ping endpoint - authenticated access"""
    preferred_username = current_user["preferred_username"]
    pong:int = int(time.time())
    return {
        "pong":  pong,
        "user":  preferred_username,
        "build": "2026.2.6",
    } 