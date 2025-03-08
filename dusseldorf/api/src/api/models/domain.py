# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from pydantic import BaseModel

class DomainBase(BaseModel):
    domain: str
    owner: str
    users: list

class DomainCreate(BaseModel):
    domain: str
    users: list

class Domain(DomainBase):
    pass
