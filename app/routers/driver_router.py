from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
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
    
    return get_driver_profile(db, user_id)


@router.put("/profile", response_model=DriverResponse)
async def update_profile(
    driver_update: DriverUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    return update_driver_profile(db, user_id, driver_update)


@router.get("/trips", response_model=List[TripWithDetails])
async def get_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    return get_assigned_trips(db, user_id)


@router.get("/trips/today", response_model=List[TripWithDetails])
async def get_todays_trips(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    return get_today_trips(db, user_id)


@router.post("/trips/{trip_id}/start")
async def start_assigned_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    success = start_trip(db, user_id, trip_id)
    return {"message": "Trip started successfully", "success": success}


@router.post("/trips/{trip_id}/complete")
async def complete_assigned_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    success = complete_trip(db, user_id, trip_id)
    return {"message": "Trip completed successfully", "success": success}


@router.post("/availability")
async def update_driver_availability(
    is_available: bool,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    success = update_availability(db, user_id, is_available)
    return {"message": "Availability updated successfully", "is_available": is_available, "success": success}


@router.post("/upload-identity")
async def upload_identity_proof(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    """Upload identity proof document for verification"""
    # Validate file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: PDF, JPG, PNG, DOC, DOCX"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/identity_proofs"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"driver_{user_id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update driver record with file path
        from app.models.driver import Driver
        driver = db.query(Driver).filter(Driver.user_id == user_id).first()
        if driver:
            driver.identity_proof_url = file_path
            driver.identity_proof_status = "pending"
            db.commit()
            
        return {
            "message": "Identity proof uploaded successfully",
            "filename": filename,
            "status": "pending_verification"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/dashboard")
async def get_driver_dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_driver_role)
):
    
    profile = get_driver_profile(db, user_id)
    today_trips = get_today_trips(db, user_id)
    all_trips = get_assigned_trips(db, user_id)
    
    
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
