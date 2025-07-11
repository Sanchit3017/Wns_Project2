from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DriverBase(BaseModel):
    
    name: str
    phone_number: str
    dl_number: str
    vehicle_plate_number: str
    service_area: Optional[str] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    
    name: Optional[str] = None
    phone_number: Optional[str] = None
    dl_number: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    is_available: Optional[bool] = None
    service_area: Optional[str] = None


class DriverResponse(DriverBase):
    
    id: int
    user_id: int
    is_available: bool
    identity_proof_url: Optional[str]
    identity_proof_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DriverRegistration(BaseModel):
    
    email: str
    password: str
    name: str
    phone_number: str
    dl_number: str
    vehicle_plate_number: str
    service_area: str


class DriverWithUser(BaseModel):
    
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


class IdentityVerificationUpdate(BaseModel):
    identity_proof_status: str  # approved, rejected, pending


class LocationBasedDriverSearch(BaseModel):
    employee_location: str


class LocationBasedDriverResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    service_area: str
    is_available: bool
    distance_score: float  # Lower score means closer match
    
    class Config:
        from_attributes = True
