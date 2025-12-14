from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class WorkerBase(BaseModel):
    name: str
    phone: Optional[str] = None


class WorkerCreate(WorkerBase):
    hourly_rate: Decimal = Decimal("20.00")


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None


class WorkerResponse(WorkerBase):
    id: int
    hourly_rate: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True


class WorkerResponseForWorker(WorkerBase):
    """Response without hourly_rate for non-admin users - actually we show rate but can't edit"""
    id: int
    hourly_rate: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True
