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
