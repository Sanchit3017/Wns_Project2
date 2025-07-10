"""
Employee API endpoints for profile management and trip viewing
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.employee import Employee
from app.models.trip import Trip
from app.models.user import User
from app.schemas.employee import EmployeeUpdate, EmployeeResponse
from app.schemas.trip import TripWithDetails
from datetime import datetime, date
from typing import List


def get_employee_profile(db: Session, user_id: int) -> EmployeeResponse:
    """Get employee profile by user ID"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return EmployeeResponse.from_orm(employee)


def update_employee_profile(db: Session, user_id: int, employee_update: EmployeeUpdate) -> EmployeeResponse:
    """Update employee profile"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    update_data = employee_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    return EmployeeResponse.from_orm(employee)


def get_upcoming_trips(db: Session, user_id: int) -> List[TripWithDetails]:
    """Get upcoming trips for the employee"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    now = datetime.utcnow()
    trips = db.query(Trip).filter(
        and_(
            Trip.employee_id == employee.id,
            Trip.scheduled_time > now,
            Trip.status.in_(["scheduled", "in_progress"])
        )
    ).order_by(Trip.scheduled_time).all()
    
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
            employee_name=employee.name,
            employee_id=employee.employee_id,
            driver_name=trip.driver.name if trip.driver else None,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def get_past_trips(db: Session, user_id: int) -> List[TripWithDetails]:
    """Get past trips for the employee"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    trips = db.query(Trip).filter(
        and_(
            Trip.employee_id == employee.id,
            Trip.status.in_(["completed", "cancelled"])
        )
    ).order_by(Trip.scheduled_time.desc()).all()
    
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
            employee_name=employee.name,
            employee_id=employee.employee_id,
            driver_name=trip.driver.name if trip.driver else None,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def get_current_trip(db: Session, user_id: int) -> TripWithDetails:
    """Get current ongoing trip for the employee"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    trip = db.query(Trip).filter(
        and_(
            Trip.employee_id == employee.id,
            Trip.status == "in_progress"
        )
    ).first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ongoing trip found"
        )
    
    return TripWithDetails(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_name=employee.name,
        employee_id=employee.employee_id,
        driver_name=trip.driver.name if trip.driver else None,
        vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
        vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
        created_at=trip.created_at
    )


def request_trip_reschedule(db: Session, user_id: int, trip_id: int, new_time: datetime, reason: str) -> bool:
    """Request trip reschedule (creates a notification for admin)"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    trip = db.query(Trip).filter(
        and_(Trip.id == trip_id, Trip.employee_id == employee.id)
    ).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    if trip.status not in ["scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reschedule trip in current status"
        )
    
    # Add reschedule note to trip
    reschedule_note = f"Reschedule requested by {employee.name} for {new_time}. Reason: {reason}"
    if trip.notes:
        trip.notes += f"\n{reschedule_note}"
    else:
        trip.notes = reschedule_note
    
    db.commit()
    return True


def get_trip_history(db: Session, user_id: int, limit: int = 50) -> List[TripWithDetails]:
    """Get complete trip history for the employee"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    trips = db.query(Trip).filter(
        Trip.employee_id == employee.id
    ).order_by(Trip.created_at.desc()).limit(limit).all()
    
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
            employee_name=employee.name,
            employee_id=employee.employee_id,
            driver_name=trip.driver.name if trip.driver else None,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result
