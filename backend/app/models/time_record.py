from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey, Table, Numeric
from sqlalchemy.orm import relationship
from datetime import date, time

from app.database import Base


# Association table for many-to-many relationship between TimeRecord and Worker
time_record_workers = Table(
    "time_record_workers",
    Base.metadata,
    Column("time_record_id", Integer, ForeignKey("time_records.id", ondelete="CASCADE"), primary_key=True),
    Column("worker_id", Integer, ForeignKey("workers.id", ondelete="CASCADE"), primary_key=True),
)


class TimeRecord(Base):
    __tablename__ = "time_records"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    work_date = Column(Date, nullable=False, default=date.today)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    break_minutes = Column(Integer, default=0)
    is_manual_entry = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    
    # Calculated fields stored for reporting
    total_minutes = Column(Integer, nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Relationships
    property = relationship("Property", back_populates="time_records")
    workers = relationship(
        "Worker",
        secondary=time_record_workers,
        back_populates="time_records"
    )
    
    def calculate_totals(self, workers_list):
        """Calculate total minutes and cost based on workers."""
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            work_minutes = end_minutes - start_minutes - (self.break_minutes or 0)
            self.total_minutes = max(0, work_minutes)
            
            # Calculate cost based on each worker's rate
            total_cost = 0
            hours = self.total_minutes / 60
            for worker in workers_list:
                total_cost += float(worker.hourly_rate) * hours
            self.total_cost = total_cost
