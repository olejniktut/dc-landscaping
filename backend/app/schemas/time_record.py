from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time
from decimal import Decimal

from app.schemas.worker import WorkerResponse
from app.schemas.property import PropertyResponse


class TimeRecordBase(BaseModel):
    property_id: int
    work_date: date
    start_time: time
    end_time: Optional[time] = None
    break_minutes: int = 0
    is_manual_entry: bool = False
    notes: Optional[str] = None


class TimeRecordCreate(TimeRecordBase):
    worker_ids: List[int]


class TimeRecordUpdate(BaseModel):
    property_id: Optional[int] = None
    work_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: Optional[int] = None
    notes: Optional[str] = None
    worker_ids: Optional[List[int]] = None


class TimeRecordResponse(TimeRecordBase):
    id: int
    total_minutes: Optional[int] = None
    total_cost: Optional[Decimal] = None
    workers: List[WorkerResponse] = []
    property: Optional[PropertyResponse] = None
    
    class Config:
        from_attributes = True


class TimeRecordWithDetails(TimeRecordResponse):
    """Extended response with property details."""
    pass


# For starting/stopping timer
class TimerStart(BaseModel):
    property_id: int
    worker_ids: List[int]


class TimerStop(BaseModel):
    time_record_id: int
    end_time: Optional[time] = None
    break_minutes: int = 0
    worker_ids: Optional[List[int]] = None
