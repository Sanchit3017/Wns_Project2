from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Driver schemas
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


# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    employee_id: str
    phone_number: str
    home_location: str
    commute_schedule: str


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    home_location: Optional[str] = None
    commute_schedule: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmployeeRegistration(BaseModel):
    email: str
    password: str
    name: str
    employee_id: str
    phone_number: str
    home_location: str
    commute_schedule: str


class EmployeeWithUser(BaseModel):
    id: int
    user_id: int
    name: str
    employee_id: str
    phone_number: str
    home_location: str
    commute_schedule: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Vehicle schemas
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


# Search and verification schemas
class IdentityVerificationUpdate(BaseModel):
    identity_proof_status: str  # approved, rejected, pending


class LocationBasedDriverSearch(BaseModel):
    employee_location: str


class RescheduleRequest(BaseModel):
    trip_id: int
    new_scheduled_time: datetime
    reason: str


# Admin schemas
class AdminBase(BaseModel):
    name: str
    employee_id: str
    phone_number: str
    department: str


class AdminCreate(AdminBase):
    access_level: Optional[str] = "admin"


class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    access_level: Optional[str] = None


class AdminResponse(AdminBase):
    id: int
    user_id: int
    access_level: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AdminRegistration(BaseModel):
    email: str
    password: str
    name: str
    employee_id: str
    phone_number: str
    department: str
    access_level: Optional[str] = "admin"


class AdminWithUser(BaseModel):
    id: int
    user_id: int
    name: str
    employee_id: str
    phone_number: str
    department: str
    access_level: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Admin action schemas
class UserStatusUpdate(BaseModel):
    is_active: bool





class SystemStatistics(BaseModel):
    drivers: dict
    employees: dict
    vehicles: dict
    system: dict