"""
Driver schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DriverBase(BaseModel):
    """Base driver schema"""
    name: str
    phone_number: str
    dl_number: str
    vehicle_plate_number: str


class DriverCreate(DriverBase):
    """Driver creation schema"""
    pass


class DriverUpdate(BaseModel):
    """Driver update schema"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    dl_number: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    is_available: Optional[bool] = None


class DriverResponse(DriverBase):
    """Driver response schema"""
    id: int
    user_id: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DriverRegistration(BaseModel):
    """Driver registration schema including user creation"""
    email: str
    password: str
    name: str
    phone_number: str
    dl_number: str
    vehicle_plate_number: str


class DriverWithUser(BaseModel):
    """Driver with user information"""
    id: int
    user_id: int
    name: str
    phone_number: str
    dl_number: str
    vehicle_plate_number: str
    is_available: bool
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
