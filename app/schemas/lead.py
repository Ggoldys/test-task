import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    source: str = Field(..., max_length=50)
    comment: str | None = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    source: str
    comment: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorDetail(BaseModel):
    code: str
    message: str
    correlation_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
