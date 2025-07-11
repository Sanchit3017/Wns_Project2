from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.admin import Admin
from models.driver import Driver
from models.employee import Employee
from models.vehicle import Vehicle
from shared.schemas.user import AdminCreate, AdminUpdate, AdminResponse, AdminWithUser
from shared.config import UserServiceSettings
from typing import List, Optional
import httpx

settings = UserServiceSettings()


# =============================================================================
# ADMIN MANAGEMENT FUNCTIONS (Top Priority)
# =============================================================================

async def create_admin(db: Session, user_id: int, admin_data: AdminCreate) -> AdminResponse:
    """Create admin profile"""
    existing_admin = db.query(Admin).filter(Admin.user_id == user_id).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin profile already exists for this user"
        )
    
    existing_employee_id = db.query(Admin).filter(Admin.employee_id == admin_data.employee_id).first()
    if existing_employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    
    admin = Admin(
        user_id=user_id,
        name=admin_data.name,
        employee_id=admin_data.employee_id,
        phone_number=admin_data.phone_number,
        department=admin_data.department,
        access_level=admin_data.access_level or "admin"
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return AdminResponse.from_orm(admin)


def get_admin_profile(db: Session, user_id: int) -> AdminResponse:
    
    admin = db.query(Admin).filter(Admin.user_id == user_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin profile not found"
        )
    return AdminResponse.from_orm(admin)


async def get_all_drivers(db: Session) -> List[dict]:
    
    drivers = db.query(Driver).all()
    driver_list = []
    
    async with httpx.AsyncClient() as client:
        for driver in drivers:
            try:
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/auth/user/{driver.user_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    driver_with_user = {
                        "id": driver.id,
                        "user_id": driver.user_id,
                        "name": driver.name,
                        "phone_number": driver.phone_number,
                        "dl_number": driver.dl_number,
                        "vehicle_plate_number": driver.vehicle_plate_number,
                        "is_available": driver.is_available,
                        "identity_proof_status": driver.identity_proof_status,
                        "service_area": driver.service_area,
                        "email": user_data.get("email", "unknown"),
                        "is_active": user_data.get("is_active", True),
                        "created_at": driver.created_at
                    }
                    driver_list.append(driver_with_user)
            except Exception:
                driver_with_user = {
                    "id": driver.id,
                    "user_id": driver.user_id,
                    "name": driver.name,
                    "phone_number": driver.phone_number,
                    "dl_number": driver.dl_number,
                    "vehicle_plate_number": driver.vehicle_plate_number,
                    "is_available": driver.is_available,
                    "identity_proof_status": driver.identity_proof_status,
                    "service_area": driver.service_area,
                    "email": "unavailable",
                    "is_active": True,
                    "created_at": driver.created_at
                }
                driver_list.append(driver_with_user)
    return driver_list


async def get_all_employees(db: Session) -> List[dict]:
  
    employees = db.query(Employee).all()
    employee_list = []
    
    async with httpx.AsyncClient() as client:
        for employee in employees:
            try:
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/auth/user/{employee.user_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    employee_with_user = {
                        "id": employee.id,
                        "user_id": employee.user_id,
                        "name": employee.name,
                        "employee_id": employee.employee_id,
                        "phone_number": employee.phone_number,
                        "home_location": employee.home_location,
                        "commute_schedule": employee.commute_schedule,
                        "email": user_data.get("email", "unknown"),
                        "is_active": user_data.get("is_active", True),
                        "created_at": employee.created_at
                    }
                    employee_list.append(employee_with_user)
            except Exception:
                employee_with_user = {
                    "id": employee.id,
                    "user_id": employee.user_id,
                    "name": employee.name,
                    "employee_id": employee.employee_id,
                    "phone_number": employee.phone_number,
                    "home_location": employee.home_location,
                    "commute_schedule": employee.commute_schedule,
                    "email": "unavailable",
                    "is_active": True,
                    "created_at": employee.created_at
                }
                employee_list.append(employee_with_user)
    return employee_list


async def assign_driver_to_employee(db: Session, employee_id: int, driver_id: Optional[int] = None) -> dict:
    """Admin function: Assign driver to employee based on location or specific driver ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if driver_id:
        # Assign specific driver
        driver = db.query(Driver).filter(Driver.id == driver_id, Driver.is_available == True).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found or not available"
            )
    else:
        # Find available driver in the same service area as employee's home location
        driver = db.query(Driver).filter(
            Driver.is_available == True,
            Driver.service_area.ilike(f"%{employee.home_location}%")
        ).first()
        
        if not driver:
            # If no driver in same area, get any available driver
            driver = db.query(Driver).filter(Driver.is_available == True).first()
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No available drivers found"
                )
    
    # Create trip assignment through trip service
    async with httpx.AsyncClient() as client:
        try:
            trip_data = {
                "employee_id": employee.user_id,
                "driver_id": driver.user_id,
                "pickup_location": employee.home_location,
                "destination": "Office",
                "trip_type": "pickup",
                "scheduled_time": employee.commute_schedule
            }
            
            response = await client.post(
                f"{settings.TRIP_SERVICE_URL}/trips/admin/assign",
                json=trip_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                trip_info = response.json()
                return {
                    "message": "Driver assigned successfully",
                    "employee": {
                        "id": employee.id,
                        "name": employee.name,
                        "location": employee.home_location
                    },
                    "driver": {
                        "id": driver.id,
                        "name": driver.name,
                        "vehicle": driver.vehicle_plate_number,
                        "service_area": driver.service_area
                    },
                    "trip_id": trip_info.get("id"),
                    "assignment_reason": "location_based" if not driver_id else "manual"
                }
            else:
                # Fallback: Return assignment info even if trip creation fails
                return {
                    "message": "Driver assigned (trip service unavailable)",
                    "employee": {"id": employee.id, "name": employee.name, "location": employee.home_location},
                    "driver": {"id": driver.id, "name": driver.name, "vehicle": driver.vehicle_plate_number},
                    "assignment_reason": "location_based" if not driver_id else "manual"
                }
        except Exception:
            # Fallback: Return assignment info
            return {
                "message": "Driver assigned (trip service unavailable)",
                "employee": {"id": employee.id, "name": employee.name, "location": employee.home_location},
                "driver": {"id": driver.id, "name": driver.name, "vehicle": driver.vehicle_plate_number},
                "assignment_reason": "location_based" if not driver_id else "manual"
            }


async def get_all_trips(db: Session) -> dict:
    """Admin function: Get all trips from trip service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.TRIP_SERVICE_URL}/trips/admin/all",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"trips": [], "message": "Trip service unavailable"}
        except Exception:
            return {"trips": [], "message": "Trip service unavailable"}


async def toggle_user_status(db: Session, user_id: int, user_type: str, new_status: bool) -> dict:
    """Admin function: Toggle status of driver or employee"""
    if user_type == "driver":
        user = db.query(Driver).filter(Driver.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        user.is_available = new_status
        db.commit()
        db.refresh(user)
    elif user_type == "employee":
        # For employees, update auth service status
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{settings.AUTH_SERVICE_URL}/auth/user/{user_id}/status",
                    json={"is_active": new_status},
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update user status"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Auth service unavailable: {str(e)}"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type. Must be 'driver' or 'employee'"
        )
    
    return {
        "message": f"{user_type.capitalize()} status updated successfully",
        "user_id": user_id,
        "user_type": user_type,
        "new_status": new_status
    }


async def get_admin_dashboard(db: Session) -> dict:
    """Admin function: Get comprehensive admin dashboard data"""
    # Get basic statistics
    driver_stats = {
        "total": db.query(Driver).count(),
        "available": db.query(Driver).filter(Driver.is_available == True).count(),
        "verified": db.query(Driver).filter(Driver.identity_proof_status == "approved").count(),
        "pending_verification": db.query(Driver).filter(Driver.identity_proof_status == "pending").count()
    }
    
    employee_stats = {
        "total": db.query(Employee).count()
    }
    
    admin_stats = {
        "total": db.query(Admin).count()
    }
    
    vehicle_stats = {
        "total": db.query(Vehicle).count(),
        "available": db.query(Vehicle).filter(Vehicle.is_available == True).count()
    }
    
    # Get recent drivers and employees
    recent_drivers = db.query(Driver).order_by(Driver.created_at.desc()).limit(5).all()
    recent_employees = db.query(Employee).order_by(Employee.created_at.desc()).limit(5).all()
    
    # Get trip statistics from trip service
    trip_stats = {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.TRIP_SERVICE_URL}/trips/admin/statistics",
                timeout=5.0
            )
            if response.status_code == 200:
                trip_stats = response.json()
        except Exception:
            trip_stats = {"total": 0, "completed": 0, "pending": 0, "in_progress": 0}
    
    return {
        "statistics": {
            "drivers": driver_stats,
            "employees": employee_stats,
            "admins": admin_stats,
            "vehicles": vehicle_stats,
            "trips": trip_stats
        },
        "recent_activity": {
            "recent_drivers": [
                {
                    "id": driver.id,
                    "name": driver.name,
                    "status": driver.identity_proof_status,
                    "created_at": driver.created_at
                } for driver in recent_drivers
            ],
            "recent_employees": [
                {
                    "id": employee.id,
                    "name": employee.name,
                    "location": employee.home_location,
                    "created_at": employee.created_at
                } for employee in recent_employees
            ]
        },
        "alerts": {
            "pending_verifications": driver_stats["pending_verification"],
            "unavailable_drivers": driver_stats["total"] - driver_stats["available"],
            "system_health": "operational"
        }
    }


def update_admin_profile(db: Session, user_id: int, admin_update: AdminUpdate) -> AdminResponse:
    """Update admin profile"""
    admin = db.query(Admin).filter(Admin.user_id == user_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin profile not found"
        )
    
    update_data = admin_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(admin, field, value)
    
    db.commit()
    db.refresh(admin)
    return AdminResponse.from_orm(admin)


def get_system_statistics(db: Session) -> dict:
    """Get system statistics - alias for get_admin_dashboard"""
    import asyncio
    return asyncio.create_task(get_admin_dashboard(db))


def manage_user_status(db: Session, user_id: int, user_type: str, status_data: dict) -> dict:
    """Manage user status - alias for toggle_user_status"""
    import asyncio
    return asyncio.create_task(toggle_user_status(db, user_id, user_type, status_data.get("is_active", True)))


def update_driver_verification_status(db: Session, driver_id: int, status: str) -> dict:
    """Update driver verification status"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.identity_proof_status = status
    db.commit()
    db.refresh(driver)
    
    return {
        "message": "Driver verification status updated",
        "driver_id": driver_id,
        "new_status": status
    }


def assign_vehicle_to_driver(db: Session, driver_id: int, vehicle_id: int) -> dict:
    """Assign vehicle to driver"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    vehicle.driver_id = driver.user_id
    vehicle.is_available = False
    driver.vehicle_plate_number = vehicle.plate_number
    
    db.commit()
    return {"message": "Vehicle assigned to driver successfully"}


def unassign_vehicle_from_driver(db: Session, driver_id: int) -> dict:
    """Unassign vehicle from driver"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    
    vehicle = db.query(Vehicle).filter(Vehicle.driver_id == driver.user_id).first()
    if vehicle:
        vehicle.driver_id = None
        vehicle.is_available = True
    
    driver.vehicle_plate_number = "UNASSIGNED"
    db.commit()
    return {"message": "Vehicle unassigned from driver successfully"}