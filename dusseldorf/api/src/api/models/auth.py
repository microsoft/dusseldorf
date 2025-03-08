# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from enum import IntEnum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Permission(IntEnum):
    NOPERMISSION = -999
    READONLY = 0
    READWRITE = 10
    ASSIGNROLES = 20
    OWNER = 999


class AuthzBase(BaseModel):
    alias: EmailStr
    authzlevel: int #IntEnum?

class AuthzPermission(AuthzBase):
    pass

class PermissionRequest(BaseModel):
    alias: EmailStr
    permission: str
    # permission: Permission

class PermissionCreate(BaseModel):
    zone: str
    user: str
    permission: Permission

class PermissionUpdate(BaseModel):
    permission: Permission 

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 