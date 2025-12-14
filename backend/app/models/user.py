from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    WORKER = "worker"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.WORKER, nullable=False)
    is_active = Column(Boolean, default=True)
