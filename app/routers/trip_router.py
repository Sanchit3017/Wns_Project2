from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.trip import (
    create_trip, get_trip_by_id, update_trip, assign_trip,
    get_today_trips, delete_trip, reschedule_trip, get_trips_by_status
)
from app.schemas.trip import TripCreate, TripUpdate, TripResponse, TripWithDetails, TripAssignment
from app.core.security import get_current_user_role
from datetime import datetime
from typing import List

router = APIRouter()
security = HTTPBearer()


def verify_admin_or_employee_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    role = get_current_user_role(credentials.credentials)
    if role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Employee access required"
        )
    return role


def verify_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    role = get_current_user_role(credentials.credentials)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return role


@router.post("/", response_model=TripResponse)
async def create_new_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    return create_trip(db, trip_data)


@router.get("/{trip_id}", response_model=TripWithDetails)
async def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_or_employee_role)
):
    
    return get_trip_by_id(db, trip_id)


@router.put("/{trip_id}", response_model=TripResponse)
async def update_existing_trip(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    return update_trip(db, trip_id, trip_update)


@router.post("/{trip_id}/assign")
async def assign_trip_to_driver(
    trip_id: int,
    assignment: TripAssignment,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    trip = assign_trip(db, trip_id, assignment)
    return {"message": "Trip assigned successfully", "trip": trip}


@router.delete("/{trip_id}")
async def delete_existing_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    success = delete_trip(db, trip_id)
    return {"message": "Trip deleted successfully", "success": success}


@router.post("/{trip_id}/reschedule")
async def reschedule_existing_trip(
    trip_id: int,
    new_time: datetime,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    trip = reschedule_trip(db, trip_id, new_time)
    return {"message": "Trip rescheduled successfully", "trip": trip}


@router.get("/", response_model=List[TripWithDetails])
async def list_trips(
    status: str = None,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_or_employee_role)
):
    
    if status:
        return get_trips_by_status(db, status)
    else:
        return get_today_trips(db)


@router.get("/today/all", response_model=List[TripWithDetails])
async def get_all_today_trips(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_or_employee_role)
):
   
    return get_today_trips(db)


@router.get("/status/{status}", response_model=List[TripWithDetails])
async def get_trips_with_status(
    status: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_or_employee_role)
):
    
    return get_trips_by_status(db, status)
