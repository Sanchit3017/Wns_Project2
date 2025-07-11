from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


class LeaveRequest(BaseModel):
    
    start_date: datetime
    end_date: datetime
    reason: str


class RescheduleRequest(BaseModel):
    
    trip_id: int
    new_scheduled_time: datetime
    reason: str
