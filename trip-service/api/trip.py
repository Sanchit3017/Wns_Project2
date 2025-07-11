from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.trip import Trip
from shared.schemas.trip import TripCreate, TripUpdate, TripResponse, TripWithDetails, TripStatistics
from shared.utils.http_client import ServiceClient
from shared.config import TripServiceSettings
from typing import List, Optional
from datetime import datetime


settings = TripServiceSettings()
user_service = ServiceClient(settings.USER_SERVICE_URL)


async def create_trip(db: Session, trip_data: TripCreate) -> TripResponse:
    """Create new trip"""
    db_trip = Trip(
        pickup_location=trip_data.pickup_location,
        destination=trip_data.destination,
        scheduled_time=trip_data.scheduled_time,
        employee_id=trip_data.employee_id,
        driver_id=trip_data.driver_id,
        vehicle_id=None,  # Vehicle will be assigned later by admin
        notes=trip_data.notes
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    
    return TripResponse(
        id=db_trip.id,
        pickup_location=db_trip.pickup_location,
        destination=db_trip.destination,
        scheduled_time=db_trip.scheduled_time,
        actual_start_time=db_trip.actual_start_time,
        actual_end_time=db_trip.actual_end_time,
        status=db_trip.status,
        notes=db_trip.notes,
        employee_id=db_trip.employee_id,
        driver_id=db_trip.driver_id,
        vehicle_id=db_trip.vehicle_id,
        created_at=db_trip.created_at,
        updated_at=db_trip.updated_at
    )


def get_trip_by_id(db: Session, trip_id: int) -> TripResponse:
    """Get trip by ID"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    return TripResponse(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_id=trip.employee_id,
        driver_id=trip.driver_id,
        vehicle_id=trip.vehicle_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    )


async def get_trip_with_details(db: Session, trip_id: int, auth_token: str) -> TripWithDetails:
    """Get trip with detailed information from other services"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Get employee details
    employee_data = {}
    try:
        employee_response = await user_service.get(
            f"/users/employees/{trip.employee_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        employee_data = employee_response
    except Exception:
        pass
    
    # Get driver details
    driver_data = {}
    if trip.driver_id:
        try:
            driver_response = await user_service.get(
                f"/users/drivers/{trip.driver_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            driver_data = driver_response
        except Exception:
            pass
    
    return TripWithDetails(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_name=employee_data.get("name", "Unknown"),
        employee_id=employee_data.get("employee_id", "Unknown"),
        driver_name=driver_data.get("name"),
        vehicle_plate_number=None,  # Would need vehicle service
        vehicle_type=None,
        created_at=trip.created_at
    )


def update_trip(db: Session, trip_id: int, trip_update: TripUpdate) -> TripResponse:
    """Update trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Update fields
    for field, value in trip_update.dict(exclude_unset=True).items():
        setattr(trip, field, value)
    
    db.commit()
    db.refresh(trip)
    
    return TripResponse(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_id=trip.employee_id,
        driver_id=trip.driver_id,
        vehicle_id=trip.vehicle_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    )


def start_trip(db: Session, trip_id: int, driver_user_id: int) -> bool:
    """Start trip (driver only)"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return False
    
    # Verify driver is assigned to this trip
    # Would need to check with user service for driver mapping
    
    trip.status = "in_progress"
    trip.actual_start_time = datetime.utcnow()
    db.commit()
    return True


def complete_trip(db: Session, trip_id: int, driver_user_id: int) -> bool:
    """Complete trip (driver only)"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return False
    
    trip.status = "completed"
    trip.actual_end_time = datetime.utcnow()
    db.commit()
    return True


def get_trips_by_status(db: Session, status: str) -> List[TripResponse]:
    """Get trips by status"""
    trips = db.query(Trip).filter(Trip.status == status).all()
    
    return [TripResponse(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_id=trip.employee_id,
        driver_id=trip.driver_id,
        vehicle_id=trip.vehicle_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    ) for trip in trips]


def get_trips_by_employee(db: Session, employee_id: int) -> List[TripResponse]:
    """Get trips for specific employee"""
    trips = db.query(Trip).filter(Trip.employee_id == employee_id).all()
    
    return [TripResponse(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_id=trip.employee_id,
        driver_id=trip.driver_id,
        vehicle_id=trip.vehicle_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    ) for trip in trips]


def get_trips_by_driver(db: Session, driver_id: int) -> List[TripResponse]:
    """Get trips for specific driver"""
    trips = db.query(Trip).filter(Trip.driver_id == driver_id).all()
    
    return [TripResponse(
        id=trip.id,
        pickup_location=trip.pickup_location,
        destination=trip.destination,
        scheduled_time=trip.scheduled_time,
        actual_start_time=trip.actual_start_time,
        actual_end_time=trip.actual_end_time,
        status=trip.status,
        notes=trip.notes,
        employee_id=trip.employee_id,
        driver_id=trip.driver_id,
        vehicle_id=trip.vehicle_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    ) for trip in trips]


def get_trip_analytics(db: Session) -> TripStatistics:
    """Get trip analytics"""
    total_trips = db.query(Trip).count()
    completed_trips = db.query(Trip).filter(Trip.status == "completed").count()
    pending_trips = db.query(Trip).filter(Trip.status == "scheduled").count()
    in_progress_trips = db.query(Trip).filter(Trip.status == "in_progress").count()
    cancelled_trips = db.query(Trip).filter(Trip.status == "cancelled").count()
    
    completion_rate = (completed_trips / total_trips * 100) if total_trips > 0 else 0
    
    return TripStatistics(
        total_trips=total_trips,
        completed_trips=completed_trips,
        pending_trips=pending_trips,
        in_progress_trips=in_progress_trips,
        cancelled_trips=cancelled_trips,
        completion_rate=round(completion_rate, 2)
    )


def delete_trip(db: Session, trip_id: int) -> bool:
    """Delete trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return False
    
    db.delete(trip)
    db.commit()
    return True