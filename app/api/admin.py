"""
Admin API endpoints for user management and analytics
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.driver import Driver
from app.models.employee import Employee
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.schemas.driver import DriverWithUser
from app.schemas.employee import EmployeeWithUser
from app.schemas.trip import TripWithDetails, TripStatistics
from typing import List


def get_all_drivers(db: Session) -> List[DriverWithUser]:
    """Get all drivers with user information"""
    drivers = db.query(Driver).join(User).all()
    result = []
    for driver in drivers:
        result.append(DriverWithUser(
            id=driver.id,
            user_id=driver.user_id,
            name=driver.name,
            phone_number=driver.phone_number,
            dl_number=driver.dl_number,
            vehicle_plate_number=driver.vehicle_plate_number,
            is_available=driver.is_available,
            email=driver.user.email,
            is_active=driver.user.is_active,
            created_at=driver.created_at
        ))
    return result


def get_all_employees(db: Session) -> List[EmployeeWithUser]:
    """Get all employees with user information"""
    employees = db.query(Employee).join(User).all()
    result = []
    for employee in employees:
        result.append(EmployeeWithUser(
            id=employee.id,
            user_id=employee.user_id,
            name=employee.name,
            employee_id=employee.employee_id,
            phone_number=employee.phone_number,
            home_location=employee.home_location,
            commute_schedule=employee.commute_schedule,
            email=employee.user.email,
            is_active=employee.user.is_active,
            created_at=employee.created_at
        ))
    return result


def assign_trip_to_driver(db: Session, trip_id: int, driver_id: int, vehicle_id: int) -> bool:
    """Assign a trip to a driver and vehicle"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    trip.driver_id = driver_id
    trip.vehicle_id = vehicle_id
    db.commit()
    return True


def get_trip_analytics(db: Session) -> TripStatistics:
    """Get trip analytics and statistics"""
    total_trips = db.query(Trip).count()
    completed_trips = db.query(Trip).filter(Trip.status == "completed").count()
    in_progress_trips = db.query(Trip).filter(Trip.status == "in_progress").count()
    scheduled_trips = db.query(Trip).filter(Trip.status == "scheduled").count()
    cancelled_trips = db.query(Trip).filter(Trip.status == "cancelled").count()
    
    completion_rate = (completed_trips / total_trips * 100) if total_trips > 0 else 0
    
    # Calculate delay percentage (trips that started late)
    delayed_trips = db.query(Trip).filter(
        Trip.actual_start_time > Trip.scheduled_time,
        Trip.status.in_(["completed", "in_progress"])
    ).count()
    total_started_trips = completed_trips + in_progress_trips
    delay_percentage = (delayed_trips / total_started_trips * 100) if total_started_trips > 0 else 0
    
    return TripStatistics(
        total_trips=total_trips,
        completed_trips=completed_trips,
        in_progress_trips=in_progress_trips,
        scheduled_trips=scheduled_trips,
        cancelled_trips=cancelled_trips,
        completion_rate=round(completion_rate, 2),
        delay_percentage=round(delay_percentage, 2)
    )


def get_all_trips_with_details(db: Session) -> List[TripWithDetails]:
    """Get all trips with detailed information"""
    trips = db.query(Trip).join(Employee).outerjoin(Driver).outerjoin(Vehicle).all()
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
            driver_name=trip.driver.name if trip.driver else None,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def toggle_user_status(db: Session, user_id: int) -> bool:
    """Toggle user active status"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    return user.is_active
