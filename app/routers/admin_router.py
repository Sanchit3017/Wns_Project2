from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.admin import (
    get_all_drivers, get_all_employees, assign_trip_to_driver,
    get_trip_analytics, get_all_trips_with_details, toggle_user_status
)
from app.schemas.driver import (
    DriverWithUser, IdentityVerificationUpdate, LocationBasedDriverSearch, 
    LocationBasedDriverResponse
)
from app.schemas.employee import EmployeeWithUser
from app.schemas.trip import TripWithDetails, TripStatistics, TripAssignment
from app.core.security import get_current_user_role
from typing import List

router = APIRouter()
security = HTTPBearer()


def verify_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
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
    
    return get_all_drivers(db)


@router.get("/employees", response_model=List[EmployeeWithUser])
async def list_all_employees(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    return get_all_employees(db)


@router.post("/trips/{trip_id}/assign")
async def assign_trip(
    trip_id: int,
    assignment: TripAssignment,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    success = assign_trip_to_driver(db, trip_id, assignment.driver_id, assignment.vehicle_id)
    return {"message": "Trip assigned successfully", "success": success}


@router.get("/analytics", response_model=TripStatistics)
async def get_analytics(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    return get_trip_analytics(db)


@router.get("/trips", response_model=List[TripWithDetails])
async def list_all_trips(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    return get_all_trips_with_details(db)


@router.post("/users/{user_id}/toggle-status")
async def toggle_user_active_status(
    user_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    new_status = toggle_user_status(db, user_id)
    return {"message": "User status updated", "is_active": new_status}


@router.get("/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    
    analytics = get_trip_analytics(db)
    recent_trips = get_all_trips_with_details(db)[:10]  
    
    return {
        "analytics": analytics,
        "recent_trips": recent_trips,
        "total_drivers": len(get_all_drivers(db)),
        "total_employees": len(get_all_employees(db))
    }


@router.post("/drivers/search-by-location", response_model=List[LocationBasedDriverResponse])
async def search_drivers_by_location(
    search_request: LocationBasedDriverSearch,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Search for available drivers based on employee location"""
    from app.models.driver import Driver
    from app.models.user import User
    import re
    
    # Get all available drivers with their service areas
    drivers = db.query(Driver).join(User).filter(
        User.is_active == True,
        Driver.is_available == True,
        Driver.service_area.is_not(None)
    ).all()
    
    # Simple location matching algorithm
    employee_location = search_request.employee_location.lower()
    matched_drivers = []
    
    for driver in drivers:
        service_area = driver.service_area.lower()
        
        # Calculate distance score based on string similarity and keyword matching
        distance_score = 1.0  # Default high score (far)
        
        # Exact match (best score)
        if employee_location == service_area:
            distance_score = 0.1
        # Partial match
        elif employee_location in service_area or service_area in employee_location:
            distance_score = 0.3
        # Word matching
        else:
            employee_words = set(re.findall(r'\b\w+\b', employee_location))
            service_words = set(re.findall(r'\b\w+\b', service_area))
            common_words = employee_words.intersection(service_words)
            
            if common_words:
                distance_score = 0.6 - (len(common_words) * 0.1)
            else:
                distance_score = 0.9
        
        matched_drivers.append(LocationBasedDriverResponse(
            id=driver.id,
            name=driver.name,
            phone_number=driver.phone_number,
            service_area=driver.service_area,
            is_available=driver.is_available,
            distance_score=distance_score
        ))
    
    # Sort by distance score (lower is better)
    matched_drivers.sort(key=lambda x: x.distance_score)
    
    return matched_drivers


@router.put("/drivers/{driver_id}/verify-identity")
async def verify_driver_identity(
    driver_id: int,
    verification_update: IdentityVerificationUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_role)
):
    """Update driver identity verification status"""
    from app.models.driver import Driver
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Validate status
    valid_statuses = ["approved", "rejected", "pending"]
    if verification_update.identity_proof_status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    driver.identity_proof_status = verification_update.identity_proof_status
    db.commit()
    
    # Create notification for driver
    from app.api.notification import create_notification
    from app.schemas.notification import NotificationCreate
    
    status_messages = {
        "approved": "Your identity verification has been approved! You can now receive trip assignments.",
        "rejected": "Your identity verification was rejected. Please upload a valid identity document.",
        "pending": "Your identity verification is under review."
    }
    
    notification = NotificationCreate(
        title="Identity Verification Update",
        message=status_messages[verification_update.identity_proof_status],
        recipient_id=driver.user_id
    )
    create_notification(db, notification)
    
    return {
        "message": f"Driver identity verification status updated to {verification_update.identity_proof_status}",
        "driver_id": driver_id,
        "new_status": verification_update.identity_proof_status
    }
