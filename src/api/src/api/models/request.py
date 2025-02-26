# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from pydantic import BaseModel, Json
from typing import Any

class Request(BaseModel):
    zone: str
    time: int
    fqdn: str
    protocol: str
    clientip: str
    request: Json[Any]
    response: Json[Any]
    reqsummary: str
    respsummary: str