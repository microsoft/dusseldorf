# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.auth import AuthzBase

class ZoneBase(BaseModel):
    fqdn: str
    domain: str
    expiry: datetime | None
    authz: List[AuthzBase]

class ZoneCreate(BaseModel):
    domain: Optional[str] = ""
    num:    Optional[int] = 1
    zone:   Optional[str] = ""

class Zone(BaseModel):
    fqdn: str
    domain: str

class ZoneRecord(BaseModel):
    name: str
    type: str
    content: str
    ttl: int
    priority: Optional[int] = None 