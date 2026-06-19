# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from enum import IntEnum
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime
from pydantic import AfterValidator, BaseModel, EmailStr, TypeAdapter, ValidationError


_email_validator = TypeAdapter(EmailStr)


def _validate_alias(value: str) -> str:
    """An authz principal is a user's email or a service identity's GUID (OID/appId)."""
    try:
        _email_validator.validate_python(value)
    except ValidationError:
        try:
            UUID(value)
        except ValueError:
            raise ValueError("alias must be an email address or a GUID")
    return value


# Accepts a human (email) or a managed identity / service principal (GUID).
EmailOrGuid = Annotated[str, AfterValidator(_validate_alias)]

class Permission(IntEnum):
    NOPERMISSION = -999
    READONLY = 0
    READWRITE = 10
    ASSIGNROLES = 20
    OWNER = 999


class AuthzBase(BaseModel):
    alias: EmailOrGuid
    authzlevel: int #IntEnum?

class AuthzPermission(AuthzBase):
    pass

class PermissionRequest(BaseModel):
    alias: EmailOrGuid
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