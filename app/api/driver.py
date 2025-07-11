from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.user import User
from app.schemas.driver import DriverUpdate, DriverResponse
from app.schemas.trip import TripWithDetails
from datetime import datetime, date
from typing import List


def get_driver_profile(db: Session, user_id: int) -> DriverResponse:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    return DriverResponse.from_orm(driver)


def update_driver_profile(db: Session, user_id: int, driver_update: DriverUpdate) -> DriverResponse:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    update_data = driver_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    return DriverResponse.from_orm(driver)


def get_assigned_trips(db: Session, user_id: int) -> List[TripWithDetails]:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    trips = db.query(Trip).filter(Trip.driver_id == driver.id).all()
    result = []
    for trip in trips:
        result.append(TripWithDetails(
            id=trip.id,
            pickup_location=trip.pickup_location,
            destination=trip.destination,
            scheduled_time=trip.scheduled_time,
            actual_start_time=trip.actual_start_time,
            actual_end_time=trip.actual_end_time,
            status=trip.status,
            notes=trip.notes,
            employee_name=trip.employee.name,
            employee_id=trip.employee.employee_id,
            driver_name=driver.name,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def get_today_trips(db: Session, user_id: int) -> List[TripWithDetails]:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    today = date.today()
    trips = db.query(Trip).filter(
        and_(
            Trip.driver_id == driver.id,
            func.date(Trip.scheduled_time) == today
        )
    ).all()
    
    result = []
    for trip in trips:
        result.append(TripWithDetails(
            id=trip.id,
            pickup_location=trip.pickup_location,
            destination=trip.destination,
            scheduled_time=trip.scheduled_time,
            actual_start_time=trip.actual_start_time,
            actual_end_time=trip.actual_end_time,
            status=trip.status,
            notes=trip.notes,
            employee_name=trip.employee.name,
            employee_id=trip.employee.employee_id,
            driver_name=driver.name,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def start_trip(db: Session, user_id: int, trip_id: int) -> bool:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    trip = db.query(Trip).filter(
        and_(Trip.id == trip_id, Trip.driver_id == driver.id)
    ).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or not assigned to this driver"
        )
    
    if trip.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip cannot be started in current status"
        )
    
    trip.status = "in_progress"
    trip.actual_start_time = datetime.utcnow()
    db.commit()
    return True


def complete_trip(db: Session, user_id: int, trip_id: int) -> bool:
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    trip = db.query(Trip).filter(
        and_(Trip.id == trip_id, Trip.driver_id == driver.id)
    ).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or not assigned to this driver"
        )
    
    if trip.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip must be in progress to be completed"
        )
    
    trip.status = "completed"
    trip.actual_end_time = datetime.utcnow()
    db.commit()
    return True


def update_availability(db: Session, user_id: int, is_available: bool) -> bool:
    """Update driver availability status"""
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    driver.is_available = is_available
    db.commit()
    return True


def search_drivers_by_location(db: Session, employee_location: str) -> List[dict]:
    """Search for available drivers based on employee location"""
    from app.models.user import User
    import re
    
    # Get all available drivers with their service areas
    drivers = db.query(Driver).join(User).filter(
        User.is_active == True,
        Driver.is_available == True,
        Driver.service_area.is_not(None)
    ).all()
    
    # Simple location matching algorithm
    employee_location = employee_location.lower()
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
        
        matched_drivers.append({
            "id": driver.id,
            "name": driver.name,
            "phone_number": driver.phone_number,
            "service_area": driver.service_area,
            "is_available": driver.is_available,
            "distance_score": distance_score
        })
    
    # Sort by distance score (lower is better)
    matched_drivers.sort(key=lambda x: x["distance_score"])
    
    return matched_drivers
