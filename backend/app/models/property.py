from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    is_spring_cleanup = Column(Boolean, default=False)
    is_fall_cleanup = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship to time records
    time_records = relationship("TimeRecord", back_populates="property")
