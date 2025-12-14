from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, datetime, time

from app.database import get_db
from app.models.time_record import TimeRecord
from app.models.worker import Worker
from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.time_record import (
    TimeRecordCreate, TimeRecordUpdate, TimeRecordResponse,
    TimerStart, TimerStop
)
from app.auth import get_current_user

router = APIRouter(prefix="/time-records", tags=["Time Records"])


@router.get("", response_model=List[TimeRecordResponse])
async def get_time_records(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    property_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get time records with optional filters."""
    query = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    )
    
    if start_date:
        query = query.filter(TimeRecord.work_date >= start_date)
    if end_date:
        query = query.filter(TimeRecord.work_date <= end_date)
    if property_id:
        query = query.filter(TimeRecord.property_id == property_id)
    if worker_id:
        query = query.filter(TimeRecord.workers.any(Worker.id == worker_id))
    
    return query.order_by(TimeRecord.work_date.desc(), TimeRecord.start_time.desc()).all()


@router.get("/today", response_model=List[TimeRecordResponse])
async def get_today_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's time records."""
    today = date.today()
    return db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(
        TimeRecord.work_date == today
    ).order_by(TimeRecord.start_time.desc()).all()


@router.get("/{record_id}", response_model=TimeRecordResponse)
async def get_time_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific time record."""
    record = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(TimeRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    return record


@router.post("", response_model=TimeRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_time_record(
    record_data: TimeRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new time record (manual entry)."""
    # Verify property exists
    property = db.query(Property).filter(Property.id == record_data.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get workers
    workers = db.query(Worker).filter(Worker.id.in_(record_data.worker_ids)).all()
    if len(workers) != len(record_data.worker_ids):
        raise HTTPException(status_code=404, detail="One or more workers not found")
    
    # Create record
    record = TimeRecord(
        property_id=record_data.property_id,
        work_date=record_data.work_date,
        start_time=record_data.start_time,
        end_time=record_data.end_time,
        break_minutes=record_data.break_minutes,
        is_manual_entry=True,
        notes=record_data.notes,
    )
    record.workers = workers
    
    # Calculate totals if end_time is provided
    if record.end_time:
        record.calculate_totals(workers)
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(TimeRecord.id == record.id).first()


@router.post("/start", response_model=TimeRecordResponse, status_code=status.HTTP_201_CREATED)
async def start_timer(
    timer_data: TimerStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new timer."""
    # Verify property exists
    property = db.query(Property).filter(Property.id == timer_data.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get workers
    workers = db.query(Worker).filter(Worker.id.in_(timer_data.worker_ids)).all()
    if len(workers) != len(timer_data.worker_ids):
        raise HTTPException(status_code=404, detail="One or more workers not found")
    
    # Create record with current time
    now = datetime.now()
    record = TimeRecord(
        property_id=timer_data.property_id,
        work_date=now.date(),
        start_time=now.time(),
        is_manual_entry=False,
    )
    record.workers = workers
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(TimeRecord.id == record.id).first()


@router.post("/stop", response_model=TimeRecordResponse)
async def stop_timer(
    timer_data: TimerStop,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop an active timer."""
    record = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(TimeRecord.id == timer_data.time_record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    if record.end_time:
        raise HTTPException(status_code=400, detail="Timer already stopped")
    
    # Update end time
    record.end_time = timer_data.end_time or datetime.now().time()
    record.break_minutes = timer_data.break_minutes
    
    # Update workers if provided
    if timer_data.worker_ids:
        workers = db.query(Worker).filter(Worker.id.in_(timer_data.worker_ids)).all()
        record.workers = workers
    
    # Calculate totals
    record.calculate_totals(record.workers)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.put("/{record_id}", response_model=TimeRecordResponse)
async def update_time_record(
    record_id: int,
    record_data: TimeRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a time record. Worker can only edit today's records."""
    record = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(TimeRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    # Check permissions - worker can only edit today's records
    if current_user.role != UserRole.ADMIN:
        if record.work_date != date.today():
            raise HTTPException(
                status_code=403, 
                detail="You can only edit today's records"
            )
    
    # Update fields
    update_data = record_data.model_dump(exclude_unset=True)
    
    # Handle worker_ids separately
    worker_ids = update_data.pop("worker_ids", None)
    if worker_ids is not None:
        workers = db.query(Worker).filter(Worker.id.in_(worker_ids)).all()
        record.workers = workers
    
    for field, value in update_data.items():
        setattr(record, field, value)
    
    # Recalculate totals
    if record.end_time:
        record.calculate_totals(record.workers)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a time record. Worker can only delete today's records."""
    record = db.query(TimeRecord).filter(TimeRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if record.work_date != date.today():
            raise HTTPException(
                status_code=403,
                detail="You can only delete today's records"
            )
    
    db.delete(record)
    db.commit()
    return None
