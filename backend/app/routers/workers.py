from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.worker import Worker
from app.models.user import User, UserRole
from app.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse
from app.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("", response_model=List[WorkerResponse])
async def get_workers(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all workers."""
    query = db.query(Worker)
    if not include_inactive:
        query = query.filter(Worker.is_active == True)
    return query.order_by(Worker.name).all()


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def create_worker(
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new worker. Both admin and worker users can create workers."""
    # If not admin, set default rate
    if current_user.role != UserRole.ADMIN:
        worker_data.hourly_rate = 20.00
    
    worker = Worker(
        name=worker_data.name,
        phone=worker_data.phone,
        hourly_rate=worker_data.hourly_rate,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a worker. Only admin can change hourly_rate."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    update_data = worker_data.model_dump(exclude_unset=True)
    
    # Only admin can update hourly_rate
    if current_user.role != UserRole.ADMIN and "hourly_rate" in update_data:
        del update_data["hourly_rate"]
    
    for field, value in update_data.items():
        setattr(worker, field, value)
    
    db.commit()
    db.refresh(worker)
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a worker (admin only). Actually just deactivates."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker.is_active = False
    db.commit()
    return None
