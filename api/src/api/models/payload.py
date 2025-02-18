from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PayloadStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PayloadBase(BaseModel):
    zone_id: str
    content: Dict[str, Any]
    type: str
    priority: int = 0

class PayloadCreate(PayloadBase):
    pass

class PayloadUpdate(BaseModel):
    status: PayloadStatus
    error_message: Optional[str] = None

class Payload(PayloadBase):
    id: str = Field(alias="_id")
    status: PayloadStatus
    error_message: Optional[str] = None
    created_at: datetime
    created_by: str
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None

    class Config:
        allow_population_by_field_name = True 