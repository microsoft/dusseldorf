from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for API endpoints"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    status_code: int = 200

class AuditableModel(BaseModel):
    """Base model with audit fields"""
    created_at: datetime
    created_by: str
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Pagination wrapper for list responses"""
    items: list
    total: int
    page: int
    size: int
    pages: int 