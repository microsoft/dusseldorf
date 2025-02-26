# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

import time
from fastapi import APIRouter, Response, Depends
from typing import Dict
from ..dependencies import get_current_user, get_db

router = APIRouter()

@router.get("/")
async def root() -> Dict[str, str]:
    """Default endpoint returning API information - public access"""
    return {
        "name": "Dusseldorf API",
        "version": "2.0.0",
        "status": "operational"
    }

@router.get("/robots.txt")
async def robots() -> Response:
    return Response(
        content="User-agent: *\nDisallow: /",
        media_type="text/plain"
    )

@router.get("/favicon.ico")
async def favicon() -> Response:
    """Favicon endpoint - public access"""
    return Response(status_code=204)

@router.get("/ping")
async def pong(
    current_user: str = Depends(get_current_user),
) -> Dict[str, str|int]:
    """Ping endpoint - authenticated access"""
    preferred_username = current_user["preferred_username"]
    pong:int = int(time.time())
    return {
        "pong":  pong,
        "user":  preferred_username,
        "build": "2025.3.2",
    } 