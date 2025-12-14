from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    hourly_rate = Column(Numeric(10, 2), default=20.00, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship to time records through association table
    time_records = relationship(
        "TimeRecord",
        secondary="time_record_workers",
        back_populates="workers"
    )
