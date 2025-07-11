from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from api.trip import (
    create_trip, get_trip_by_id, get_trip_with_details, update_trip,
    start_trip, complete_trip, get_trips_by_status, get_trips_by_employee,
    get_trips_by_driver, get_trip_analytics, delete_trip
)
from shared.schemas.trip import TripCreate, TripUpdate, TripResponse, TripWithDetails, TripStatistics
from database import get_database_session
from typing import List, Optional

router = APIRouter()

def get_db():
    """Get database session"""
    return next(get_database_session())

def get_user_context(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None)
):
    """Get user context from headers (set by API Gateway)"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User context not found"
        )
    return {
        "user_id": int(x_user_id),
        "role": x_user_role,
        "email": x_user_email
    }

@router.post("/trips", response_model=TripResponse)
async def create_new_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Create a new trip (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create trips"
        )
    return await create_trip(db, trip_data)

@router.get("/trips/{trip_id}", response_model=TripWithDetails)
async def get_trip_details(
    trip_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context),
    authorization: Optional[str] = Header(None)
):
    """Get trip details with related information"""
    return await get_trip_with_details(db, trip_id, authorization or "")

@router.put("/trips/{trip_id}", response_model=TripResponse)
def update_trip_details(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Update trip details (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update trips"
        )
    return update_trip(db, trip_id, trip_update)

@router.delete("/trips/{trip_id}")
def delete_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Delete trip (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete trips"
        )
    
    success = delete_trip(db, trip_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    return {"message": "Trip deleted successfully"}

@router.post("/trips/{trip_id}/start")
def start_trip_by_driver(
    trip_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Start trip (Driver only)"""
    if user_context["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can start trips"
        )
    
    success = start_trip(db, trip_id, user_context["user_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or not assigned to you"
        )
    return {"message": "Trip started successfully"}

@router.post("/trips/{trip_id}/complete")
def complete_trip_by_driver(
    trip_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Complete trip (Driver only)"""
    if user_context["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can complete trips"
        )
    
    success = complete_trip(db, trip_id, user_context["user_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or not assigned to you"
        )
    return {"message": "Trip completed successfully"}

@router.get("/trips/status/{status}", response_model=List[TripResponse])
def get_trips_by_status_filter(
    status: str,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get trips by status (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view trips by status"
        )
    return get_trips_by_status(db, status)

@router.get("/trips/employee/{employee_id}", response_model=List[TripResponse])
def get_employee_trips(
    employee_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get trips for specific employee"""
    # Allow employees to see their own trips, admins can see all
    if user_context["role"] == "employee" and user_context["user_id"] != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own trips"
        )
    return get_trips_by_employee(db, employee_id)

@router.get("/trips/driver/{driver_id}", response_model=List[TripResponse])
def get_driver_trips(
    driver_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get trips for specific driver"""
    # Allow drivers to see their own trips, admins can see all
    if user_context["role"] == "driver" and user_context["user_id"] != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own trips"
        )
    return get_trips_by_driver(db, driver_id)

@router.get("/trips/analytics", response_model=TripStatistics)
def get_trip_analytics_data(
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get trip analytics (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view analytics"
        )
    return get_trip_analytics(db)