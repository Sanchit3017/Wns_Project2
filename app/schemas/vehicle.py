from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    plate_number: str
    vehicle_type: str
    capacity: int


class VehicleCreate(VehicleBase):
 
    driver_id: Optional[int] = None


class VehicleUpdate(BaseModel):
    
    vehicle_type: Optional[str] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None
    driver_id: Optional[int] = None


class VehicleResponse(VehicleBase):
    
    id: int
    is_available: bool
    driver_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VehicleWithDriver(BaseModel):
    
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
