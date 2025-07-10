"""
Admin router for user management and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.admin import (
    get_all_drivers, get_all_employees, assign_trip_to_driver,
    get_trip_analytics, get_all_trips_with_details, toggle_user_status
)
from app.schemas.driver import DriverWithUser
from app.schemas.employee import EmployeeWithUser
from app.schemas.trip import TripWithDetails, TripStatistics, TripAssignment
from app.core.security import get_current_user_role
from typing import List

router = APIRouter()
security = HTTPBearer()


def verify_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify that the current user is an admin"""
    role = get_current_user_role(credentials.credentials)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return role


@router.get("/drivers", response_model=List[DriverWithUser])
async def list_all_drivers(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Get list of all drivers with user information"""
    return get_all_drivers(db)


@router.get("/employees", response_model=List[EmployeeWithUser])
async def list_all_employees(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Get list of all employees with user information"""
    return get_all_employees(db)


@router.post("/trips/{trip_id}/assign")
async def assign_trip(
    trip_id: int,
    assignment: TripAssignment,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Assign a trip to a driver and vehicle"""
    success = assign_trip_to_driver(db, trip_id, assignment.driver_id, assignment.vehicle_id)
    return {"message": "Trip assigned successfully", "success": success}


@router.get("/analytics", response_model=TripStatistics)
async def get_analytics(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Get trip analytics and statistics"""
    return get_trip_analytics(db)


@router.get("/trips", response_model=List[TripWithDetails])
async def list_all_trips(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Get list of all trips with detailed information"""
    return get_all_trips_with_details(db)


@router.post("/users/{user_id}/toggle-status")
async def toggle_user_active_status(
    user_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Toggle user active status"""
    new_status = toggle_user_status(db, user_id)
    return {"message": "User status updated", "is_active": new_status}


@router.get("/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Get admin dashboard data"""
    analytics = get_trip_analytics(db)
    recent_trips = get_all_trips_with_details(db)[:10]  # Last 10 trips
    
    return {
        "analytics": analytics,
        "recent_trips": recent_trips,
        "total_drivers": len(get_all_drivers(db)),
        "total_employees": len(get_all_employees(db))
    }
