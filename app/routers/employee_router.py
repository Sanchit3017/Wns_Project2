from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.employee import (
    get_employee_profile, update_employee_profile, get_upcoming_trips,
    get_past_trips, request_trip_reschedule, get_trip_history, get_current_trip
)
from app.schemas.employee import EmployeeUpdate, EmployeeResponse, RescheduleRequest
from app.schemas.trip import TripWithDetails
from app.core.security import get_current_user_id, get_current_user_role
from typing import List

router = APIRouter()
security = HTTPBearer()


def verify_employee_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    role = get_current_user_role(credentials.credentials)
    if role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )
    return get_current_user_id(credentials.credentials)


@router.get("/profile", response_model=EmployeeResponse)
async def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return get_employee_profile(db, user_id)


@router.put("/profile", response_model=EmployeeResponse)
async def update_profile(
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return update_employee_profile(db, user_id, employee_update)


@router.get("/trips/upcoming", response_model=List[TripWithDetails])
async def get_upcoming_employee_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return get_upcoming_trips(db, user_id)


@router.get("/trips/past", response_model=List[TripWithDetails])
async def get_past_employee_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return get_past_trips(db, user_id)


@router.get("/trips/history", response_model=List[TripWithDetails])
async def get_employee_trip_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return get_trip_history(db, user_id, limit)


@router.get("/trips/current", response_model=TripWithDetails)
async def get_current_ongoing_trip(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    return get_current_trip(db, user_id)


@router.post("/trips/{trip_id}/reschedule")
async def request_reschedule(
    trip_id: int,
    reschedule_request: RescheduleRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    success = request_trip_reschedule(
        db, user_id, trip_id, 
        reschedule_request.new_scheduled_time, 
        reschedule_request.reason
    )
    return {"message": "Reschedule request submitted successfully", "success": success}


@router.get("/dashboard")
async def get_employee_dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_employee_role)
):
    
    profile = get_employee_profile(db, user_id)
    upcoming_trips = get_upcoming_trips(db, user_id)
    past_trips = get_past_trips(db, user_id)
    
    
    current_trip = None
    try:
        current_trip = get_current_trip(db, user_id)
    except HTTPException:
        
        pass
    
    
    completed_trips = len([trip for trip in past_trips if trip.status == "completed"])
    cancelled_trips = len([trip for trip in past_trips if trip.status == "cancelled"])
    scheduled_trips = len([trip for trip in upcoming_trips if trip.status == "scheduled"])
    
    return {
        "profile": profile,
        "current_trip": current_trip,
        "upcoming_trips": upcoming_trips[:5],  
        "stats": {
            "total_trips": len(past_trips) + len(upcoming_trips),
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "scheduled_trips": scheduled_trips,
            "upcoming_trips_count": len(upcoming_trips),
            "has_ongoing_trip": current_trip is not None
        }
    }
