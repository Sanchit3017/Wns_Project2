"""
Vehicle schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    """Base vehicle schema"""
    plate_number: str
    vehicle_type: str
    capacity: int


class VehicleCreate(VehicleBase):
    """Vehicle creation schema"""
    driver_id: Optional[int] = None


class VehicleUpdate(BaseModel):
    """Vehicle update schema"""
    vehicle_type: Optional[str] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None
    driver_id: Optional[int] = None


class VehicleResponse(VehicleBase):
    """Vehicle response schema"""
    id: int
    is_available: bool
    driver_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VehicleWithDriver(BaseModel):
    """Vehicle with driver information"""
    id: int
    plate_number: str
    vehicle_type: str
    capacity: int
    is_available: bool
    driver_id: Optional[int]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
