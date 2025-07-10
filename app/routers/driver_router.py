"""
Driver router for profile management and trip operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.driver import (
    get_driver_profile, update_driver_profile, get_assigned_trips,
    get_today_trips, start_trip, complete_trip, update_availability
)
from app.schemas.driver import DriverUpdate, DriverResponse
from app.schemas.trip import TripWithDetails
from app.core.security import get_current_user_id, get_current_user_role
from typing import List

router = APIRouter()
security = HTTPBearer()


def verify_driver_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify that the current user is a driver"""
    role = get_current_user_role(credentials.credentials)
    if role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver access required"
        )
    return get_current_user_id(credentials.credentials)


@router.get("/profile", response_model=DriverResponse)
async def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Get driver profile"""
    return get_driver_profile(db, user_id)


@router.put("/profile", response_model=DriverResponse)
async def update_profile(
    driver_update: DriverUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Update driver profile"""
    return update_driver_profile(db, user_id, driver_update)


@router.get("/trips", response_model=List[TripWithDetails])
async def get_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Get all assigned trips"""
    return get_assigned_trips(db, user_id)


@router.get("/trips/today", response_model=List[TripWithDetails])
async def get_todays_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Get today's trips"""
    return get_today_trips(db, user_id)


@router.post("/trips/{trip_id}/start")
async def start_assigned_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Start a trip"""
    success = start_trip(db, user_id, trip_id)
    return {"message": "Trip started successfully", "success": success}


@router.post("/trips/{trip_id}/complete")
async def complete_assigned_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Complete a trip"""
    success = complete_trip(db, user_id, trip_id)
    return {"message": "Trip completed successfully", "success": success}


@router.post("/availability")
async def update_driver_availability(
    is_available: bool,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Update driver availability status"""
    success = update_availability(db, user_id, is_available)
    return {"message": "Availability updated successfully", "is_available": is_available, "success": success}


@router.get("/dashboard")
async def get_driver_dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Get driver dashboard data"""
    profile = get_driver_profile(db, user_id)
    today_trips = get_today_trips(db, user_id)
    all_trips = get_assigned_trips(db, user_id)
    
    # Calculate statistics
    completed_trips = len([trip for trip in all_trips if trip.status == "completed"])
    in_progress_trips = len([trip for trip in all_trips if trip.status == "in_progress"])
    scheduled_trips = len([trip for trip in all_trips if trip.status == "scheduled"])
    
    return {
        "profile": profile,
        "today_trips": today_trips,
        "stats": {
            "total_trips": len(all_trips),
            "completed_trips": completed_trips,
            "in_progress_trips": in_progress_trips,
            "scheduled_trips": scheduled_trips,
            "today_trips_count": len(today_trips)
        }
    }
