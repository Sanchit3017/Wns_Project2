from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.trip import Trip
from app.models.employee import Employee
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.schemas.trip import TripCreate, TripUpdate, TripResponse, TripWithDetails, TripAssignment
from datetime import datetime, date
from typing import List


def create_trip(db: Session, trip_data: TripCreate) -> TripResponse:
    
    employee = db.query(Employee).filter(Employee.id == trip_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    
    if trip_data.driver_id:
        driver = db.query(Driver).filter(Driver.id == trip_data.driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
    
    
    if trip_data.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == trip_data.vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
    
    trip = Trip(
        pickup_location=trip_data.pickup_location,
        destination=trip_data.destination,
        scheduled_time=trip_data.scheduled_time,
        employee_id=trip_data.employee_id,
        driver_id=trip_data.driver_id,
        vehicle_id=trip_data.vehicle_id,
        notes=trip_data.notes,
        status="scheduled"
    )
    
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return TripResponse.from_orm(trip)


def get_trip_by_id(db: Session, trip_id: int) -> TripWithDetails:
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
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
        employee_name=trip.employee.name,
        employee_id=trip.employee.employee_id,
        driver_name=trip.driver.name if trip.driver else None,
        vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
        vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
        created_at=trip.created_at
    )


def update_trip(db: Session, trip_id: int, trip_update: TripUpdate) -> TripResponse:
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    update_data = trip_update.dict(exclude_unset=True)
    
    
    if "driver_id" in update_data and update_data["driver_id"]:
        driver = db.query(Driver).filter(Driver.id == update_data["driver_id"]).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
    
    
    if "vehicle_id" in update_data and update_data["vehicle_id"]:
        vehicle = db.query(Vehicle).filter(Vehicle.id == update_data["vehicle_id"]).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
    
    for field, value in update_data.items():
        setattr(trip, field, value)
    
    db.commit()
    db.refresh(trip)
    return TripResponse.from_orm(trip)


def assign_trip(db: Session, trip_id: int, assignment: TripAssignment) -> TripResponse:
    """Assign driver and vehicle to a trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    
    driver = db.query(Driver).filter(Driver.id == assignment.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == assignment.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    trip.driver_id = assignment.driver_id
    trip.vehicle_id = assignment.vehicle_id
    db.commit()
    db.refresh(trip)
    return TripResponse.from_orm(trip)


def get_today_trips(db: Session) -> List[TripWithDetails]:
    
    today = date.today()
    trips = db.query(Trip).filter(
        func.date(Trip.scheduled_time) == today
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
            employee_name=trip.employee.name,
            employee_id=trip.employee.employee_id,
            driver_name=trip.driver.name if trip.driver else None,
            vehicle_plate_number=trip.vehicle.plate_number if trip.vehicle else None,
            vehicle_type=trip.vehicle.vehicle_type if trip.vehicle else None,
            created_at=trip.created_at
        ))
    return result


def delete_trip(db: Session, trip_id: int) -> bool:
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    if trip.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete trip that is in progress"
        )
    
    db.delete(trip)
    db.commit()
    return True


def reschedule_trip(db: Session, trip_id: int, new_time: datetime) -> TripResponse:
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    if trip.status not in ["scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reschedule scheduled trips"
        )
    
    trip.scheduled_time = new_time
    db.commit()
    db.refresh(trip)
    return TripResponse.from_orm(trip)


def get_trips_by_status(db: Session, status: str) -> List[TripWithDetails]:
    
    valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    trips = db.query(Trip).filter(Trip.status == status).order_by(Trip.scheduled_time).all()
    
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
