from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List
from datetime import date, timedelta
from decimal import Decimal
from pydantic import BaseModel

from app.database import get_db
from app.models.time_record import TimeRecord
from app.models.worker import Worker
from app.models.property import Property
from app.models.user import User
from app.auth import get_current_admin
from app.services.excel import create_report_excel

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportSummary(BaseModel):
    total_hours: float
    total_cost: float
    records_count: int
    properties_count: int


class DashboardStats(BaseModel):
    today_hours: float
    today_cost: float
    today_records: int
    active_workers: int
    month_hours: float
    month_cost: float
    year_hours: float
    year_cost: float


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get dashboard statistics (admin only)."""
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    # Today's stats
    today_records = db.query(TimeRecord).filter(
        TimeRecord.work_date == today,
        TimeRecord.total_minutes.isnot(None)
    ).all()
    
    today_hours = sum(r.total_minutes or 0 for r in today_records) / 60
    today_cost = sum(float(r.total_cost or 0) for r in today_records)
    
    # Month stats
    month_records = db.query(TimeRecord).filter(
        TimeRecord.work_date >= month_start,
        TimeRecord.total_minutes.isnot(None)
    ).all()
    
    month_hours = sum(r.total_minutes or 0 for r in month_records) / 60
    month_cost = sum(float(r.total_cost or 0) for r in month_records)
    
    # Year stats
    year_records = db.query(TimeRecord).filter(
        TimeRecord.work_date >= year_start,
        TimeRecord.total_minutes.isnot(None)
    ).all()
    
    year_hours = sum(r.total_minutes or 0 for r in year_records) / 60
    year_cost = sum(float(r.total_cost or 0) for r in year_records)
    
    # Active workers
    active_workers = db.query(Worker).filter(Worker.is_active == True).count()
    
    return DashboardStats(
        today_hours=round(today_hours, 2),
        today_cost=round(today_cost, 2),
        today_records=len(today_records),
        active_workers=active_workers,
        month_hours=round(month_hours, 2),
        month_cost=round(month_cost, 2),
        year_hours=round(year_hours, 2),
        year_cost=round(year_cost, 2)
    )


@router.get("/summary", response_model=ReportSummary)
async def get_report_summary(
    start_date: date,
    end_date: date,
    property_id: Optional[int] = None,
    cleanup_type: Optional[str] = None,  # "spring", "fall", or None for all
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get report summary for the given filters (admin only)."""
    query = db.query(TimeRecord).options(
        joinedload(TimeRecord.property)
    ).filter(
        TimeRecord.work_date >= start_date,
        TimeRecord.work_date <= end_date,
        TimeRecord.total_minutes.isnot(None)
    )
    
    if property_id:
        query = query.filter(TimeRecord.property_id == property_id)
    
    records = query.all()
    
    # Filter by cleanup type
    if cleanup_type == "spring":
        records = [r for r in records if r.property.is_spring_cleanup]
    elif cleanup_type == "fall":
        records = [r for r in records if r.property.is_fall_cleanup]
    
    total_hours = sum(r.total_minutes or 0 for r in records) / 60
    total_cost = sum(float(r.total_cost or 0) for r in records)
    properties = set(r.property_id for r in records)
    
    return ReportSummary(
        total_hours=round(total_hours, 2),
        total_cost=round(total_cost, 2),
        records_count=len(records),
        properties_count=len(properties)
    )


@router.get("/preview")
async def preview_report(
    start_date: date,
    end_date: date,
    property_id: Optional[int] = None,
    cleanup_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Preview report data (admin only)."""
    query = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(
        TimeRecord.work_date >= start_date,
        TimeRecord.work_date <= end_date,
        TimeRecord.total_minutes.isnot(None)
    )
    
    if property_id:
        query = query.filter(TimeRecord.property_id == property_id)
    
    records = query.order_by(TimeRecord.work_date.desc()).all()
    
    # Filter by cleanup type
    if cleanup_type == "spring":
        records = [r for r in records if r.property.is_spring_cleanup]
    elif cleanup_type == "fall":
        records = [r for r in records if r.property.is_fall_cleanup]
    
    result = []
    total_hours = 0
    total_cost = 0
    
    for r in records:
        hours = (r.total_minutes or 0) / 60
        cost = float(r.total_cost or 0)
        total_hours += hours
        total_cost += cost
        
        cleanup_type_str = ""
        if r.property.is_spring_cleanup:
            cleanup_type_str = "Spring"
        elif r.property.is_fall_cleanup:
            cleanup_type_str = "Fall"
        
        result.append({
            "id": r.id,
            "date": r.work_date.isoformat(),
            "property": r.property.name,
            "type": cleanup_type_str,
            "workers": [w.name for w in r.workers],
            "hours": round(hours, 2),
            "cost": round(cost, 2)
        })
    
    return {
        "records": result,
        "total_hours": round(total_hours, 2),
        "total_cost": round(total_cost, 2)
    }


@router.get("/export")
async def export_report(
    start_date: date,
    end_date: date,
    property_id: Optional[int] = None,
    cleanup_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Export report to Excel (admin only)."""
    query = db.query(TimeRecord).options(
        joinedload(TimeRecord.workers),
        joinedload(TimeRecord.property)
    ).filter(
        TimeRecord.work_date >= start_date,
        TimeRecord.work_date <= end_date,
        TimeRecord.total_minutes.isnot(None)
    )
    
    property_name = "All Properties"
    if property_id:
        query = query.filter(TimeRecord.property_id == property_id)
        prop = db.query(Property).filter(Property.id == property_id).first()
        if prop:
            property_name = prop.name
    
    records = query.order_by(TimeRecord.work_date.desc()).all()
    
    # Filter by cleanup type
    if cleanup_type == "spring":
        records = [r for r in records if r.property.is_spring_cleanup]
        property_name += " (Spring Cleanup)"
    elif cleanup_type == "fall":
        records = [r for r in records if r.property.is_fall_cleanup]
        property_name += " (Fall Cleanup)"
    
    # Generate Excel
    excel_file = create_report_excel(records, start_date, end_date, property_name)
    
    filename = f"dc_landscaping_report_{start_date}_{end_date}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
