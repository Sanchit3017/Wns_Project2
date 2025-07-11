from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.driver import Driver
from shared.schemas.user import DriverCreate, DriverUpdate, DriverResponse, DriverWithUser
from shared.utils.http_client import ServiceClient
from shared.config import UserServiceSettings
from typing import List, Optional
import os


settings = UserServiceSettings()
auth_client = ServiceClient(settings.AUTH_SERVICE_URL)


async def create_driver(db: Session, user_id: int, driver_data: DriverCreate) -> DriverResponse:
    """Create driver profile"""
    # Check if driver already exists
    existing_driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile already exists"
        )
    
    db_driver = Driver(
        user_id=user_id,
        name=driver_data.name,
        phone_number=driver_data.phone_number,
        dl_number=driver_data.dl_number,
        vehicle_plate_number=driver_data.vehicle_plate_number,
        service_area=driver_data.service_area
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    
    return DriverResponse(
        id=db_driver.id,
        user_id=db_driver.user_id,
        name=db_driver.name,
        phone_number=db_driver.phone_number,
        dl_number=db_driver.dl_number,
        vehicle_plate_number=db_driver.vehicle_plate_number,
        service_area=db_driver.service_area,
        is_available=db_driver.is_available,
        identity_proof_url=db_driver.identity_proof_url,
        identity_proof_status=db_driver.identity_proof_status,
        created_at=db_driver.created_at,
        updated_at=db_driver.updated_at
    )


def get_driver_profile(db: Session, user_id: int) -> DriverResponse:
    """Get driver profile by user ID"""
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    return DriverResponse(
        id=driver.id,
        user_id=driver.user_id,
        name=driver.name,
        phone_number=driver.phone_number,
        dl_number=driver.dl_number,
        vehicle_plate_number=driver.vehicle_plate_number,
        service_area=driver.service_area,
        is_available=driver.is_available,
        identity_proof_url=driver.identity_proof_url,
        identity_proof_status=driver.identity_proof_status,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )


def update_driver_profile(db: Session, user_id: int, driver_update: DriverUpdate) -> DriverResponse:
    """Update driver profile"""
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Update fields
    for field, value in driver_update.dict(exclude_unset=True).items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    
    return DriverResponse(
        id=driver.id,
        user_id=driver.user_id,
        name=driver.name,
        phone_number=driver.phone_number,
        dl_number=driver.dl_number,
        vehicle_plate_number=driver.vehicle_plate_number,
        service_area=driver.service_area,
        is_available=driver.is_available,
        identity_proof_url=driver.identity_proof_url,
        identity_proof_status=driver.identity_proof_status,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )


async def get_all_drivers(db: Session, auth_token: str) -> List[DriverWithUser]:
    """Get all drivers with user information"""
    drivers = db.query(Driver).all()
    
    result = []
    for driver in drivers:
        # Get user info from auth service
        try:
            user_info = await auth_client.get(
                f"/auth/profile",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            result.append(DriverWithUser(
                id=driver.id,
                user_id=driver.user_id,
                name=driver.name,
                phone_number=driver.phone_number,
                dl_number=driver.dl_number,
                vehicle_plate_number=driver.vehicle_plate_number,
                is_available=driver.is_available,
                email=user_info.get("email", ""),
                is_active=user_info.get("is_active", True),
                created_at=driver.created_at
            ))
        except Exception:
            # If we can't get user info, still include driver data
            result.append(DriverWithUser(
                id=driver.id,
                user_id=driver.user_id,
                name=driver.name,
                phone_number=driver.phone_number,
                dl_number=driver.dl_number,
                vehicle_plate_number=driver.vehicle_plate_number,
                is_available=driver.is_available,
                email="",
                is_active=True,
                created_at=driver.created_at
            ))
    
    return result


def update_availability(db: Session, user_id: int, is_available: bool) -> bool:
    """Update driver availability status"""
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        return False
    
    driver.is_available = is_available
    db.commit()
    return True


def search_drivers_by_location(db: Session, employee_location: str) -> List[dict]:
    """Search for available drivers based on employee location"""
    available_drivers = db.query(Driver).filter(Driver.is_available == True).all()
    
    scored_drivers = []
    for driver in available_drivers:
        if not driver.service_area:
            continue
            
        # Simple scoring based on keyword matching
        score = calculate_location_score(employee_location.lower(), driver.service_area.lower())
        
        scored_drivers.append({
            "driver_id": driver.id,
            "name": driver.name,
            "service_area": driver.service_area,
            "score": score
        })
    
    # Sort by score (lower is better match)
    scored_drivers.sort(key=lambda x: x["score"])
    return scored_drivers


def calculate_location_score(employee_location: str, driver_service_area: str) -> float:
    """Calculate location match score"""
    employee_keywords = set(employee_location.split())
    driver_keywords = set(driver_service_area.split())
    
    if not employee_keywords or not driver_keywords:
        return float('inf')
    
    # Count matching keywords
    matches = len(employee_keywords.intersection(driver_keywords))
    total_keywords = len(employee_keywords.union(driver_keywords))
    
    if matches == 0:
        return float('inf')
    
    # Score: lower is better
    return 1.0 - (matches / total_keywords)


def verify_driver_identity(db: Session, driver_id: int, status: str) -> bool:
    """Update driver identity verification status"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        return False
    
    driver.identity_proof_status = status
    db.commit()
    return True


def upload_identity_proof(db: Session, user_id: int, file_url: str) -> bool:
    """Update driver identity proof URL"""
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        return False
    
    driver.identity_proof_url = file_url
    driver.identity_proof_status = "pending"
    db.commit()
    return True