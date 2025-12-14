from pydantic import BaseModel
from typing import Optional


class PropertyBase(BaseModel):
    name: str
    address: Optional[str] = None
    is_spring_cleanup: bool = False
    is_fall_cleanup: bool = False


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    is_spring_cleanup: Optional[bool] = None
    is_fall_cleanup: Optional[bool] = None
    is_active: Optional[bool] = None


class PropertyResponse(PropertyBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
