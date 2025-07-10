"""
Trip schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TripBase(BaseModel):
    """Base trip schema"""
    pickup_location: str
    destination: str
    scheduled_time: datetime


class TripCreate(TripBase):
    """Trip creation schema"""
    employee_id: int
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    notes: Optional[str] = None


class TripUpdate(BaseModel):
    """Trip update schema"""
    pickup_location: Optional[str] = None
    destination: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class TripResponse(TripBase):
    """Trip response schema"""
    id: int
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    status: str
    notes: Optional[str]
    employee_id: int
    driver_id: Optional[int]
    vehicle_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TripAssignment(BaseModel):
    """Trip assignment schema"""
    driver_id: int
    vehicle_id: int


class TripStatusUpdate(BaseModel):
    """Trip status update schema"""
    status: str  # scheduled, in_progress, completed, cancelled


class TripWithDetails(BaseModel):
    """Trip with employee, driver, and vehicle details"""
    id: int
    pickup_location: str
    destination: str
    scheduled_time: datetime
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    status: str
    notes: Optional[str]
    employee_name: str
    employee_id: str
    driver_name: Optional[str]
    vehicle_plate_number: Optional[str]
    vehicle_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TripStatistics(BaseModel):
    """Trip statistics schema"""
    total_trips: int
    completed_trips: int
    in_progress_trips: int
    scheduled_trips: int
    cancelled_trips: int
    completion_rate: float
    delay_percentage: float
