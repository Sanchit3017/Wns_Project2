from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.admin import Admin
from models.driver import Driver
from models.employee import Employee
from models.vehicle import Vehicle
from shared.schemas.user import AdminCreate, AdminUpdate, AdminResponse, AdminWithUser
# HTTP client functionality handled by httpx directly
from shared.config import UserServiceSettings
from typing import List, Optional
import httpx

settings = UserServiceSettings()


async def create_admin(db: Session, user_id: int, admin_data: AdminCreate) -> AdminResponse:
    """Create admin profile"""
    # Check if admin profile already exists
    existing_admin = db.query(Admin).filter(Admin.user_id == user_id).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin profile already exists for this user"
        )
    
    # Check if employee_id is unique
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
    """Get admin profile by user ID"""
    admin = db.query(Admin).filter(Admin.user_id == user_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin profile not found"
        )
    return AdminResponse.from_orm(admin)


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


async def get_all_admins(db: Session) -> List[AdminWithUser]:
    """Get all admin profiles with user details"""
    admins = db.query(Admin).all()
    admin_list = []
    
    async with httpx.AsyncClient() as client:
        for admin in admins:
            try:
                # Get user details from auth service
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/auth/user/{admin.user_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    admin_with_user = AdminWithUser(
                        id=admin.id,
                        user_id=admin.user_id,
                        name=admin.name,
                        employee_id=admin.employee_id,
                        phone_number=admin.phone_number,
                        department=admin.department,
                        access_level=admin.access_level,
                        email=user_data.get("email", "unknown"),
                        is_active=user_data.get("is_active", True),
                        created_at=admin.created_at
                    )
                    admin_list.append(admin_with_user)
            except Exception:
                # If auth service is unavailable, include admin without user details
                admin_with_user = AdminWithUser(
                    id=admin.id,
                    user_id=admin.user_id,
                    name=admin.name,
                    employee_id=admin.employee_id,
                    phone_number=admin.phone_number,
                    department=admin.department,
                    access_level=admin.access_level,
                    email="unavailable",
                    is_active=True,
                    created_at=admin.created_at
                )
                admin_list.append(admin_with_user)
    
    return admin_list


async def get_all_drivers(db: Session) -> List[dict]:
    """Get all drivers with user details"""
    drivers = db.query(Driver).all()
    driver_list = []
    
    async with httpx.AsyncClient() as client:
        for driver in drivers:
            try:
                # Get user details from auth service
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
                # If auth service is unavailable, include driver without user details
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
    """Get all employees with user details"""
    employees = db.query(Employee).all()
    employee_list = []
    
    async with httpx.AsyncClient() as client:
        for employee in employees:
            try:
                # Get user details from auth service
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
                # If auth service is unavailable, include employee without user details
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
    """Assign driver to employee based on location or specific driver ID"""
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
                "destination": "Office",  # Default destination
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
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create trip assignment"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Trip service unavailable: {str(e)}"
            )


async def get_all_trips(db: Session) -> dict:
    """Get all trips from trip service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.TRIP_SERVICE_URL}/trips/admin/all",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch trips"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Trip service unavailable: {str(e)}"
            )


async def toggle_user_status(db: Session, user_id: int, user_type: str, new_status: bool) -> dict:
    """Toggle status of driver or employee"""
    if user_type == "driver":
        user = db.query(Driver).filter(Driver.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        user.is_available = new_status
    elif user_type == "employee":
        # For employees, we'll update the auth service status
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
    
    if user_type == "driver":
        db.commit()
        db.refresh(user)
    
    return {
        "message": f"{user_type.capitalize()} status updated successfully",
        "user_id": user_id,
        "user_type": user_type,
        "new_status": new_status
    }


async def get_admin_dashboard(db: Session) -> dict:
    """Get comprehensive admin dashboard data"""
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


def get_admin_by_id(db: Session, admin_id: int) -> AdminResponse:
    """Get admin by admin ID"""
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return AdminResponse.from_orm(admin)


def get_system_statistics(db: Session) -> dict:
    """Get system-wide statistics for admin dashboard"""
    total_drivers = db.query(Driver).count()
    active_drivers = db.query(Driver).filter(Driver.is_available == True).count()
    total_employees = db.query(Employee).count()
    total_vehicles = db.query(Vehicle).count()
    available_vehicles = db.query(Vehicle).filter(Vehicle.is_available == True).count()
    
    # Driver verification statistics
    pending_verifications = db.query(Driver).filter(Driver.identity_proof_status == "pending").count()
    approved_drivers = db.query(Driver).filter(Driver.identity_proof_status == "approved").count()
    rejected_drivers = db.query(Driver).filter(Driver.identity_proof_status == "rejected").count()
    
    return {
        "drivers": {
            "total": total_drivers,
            "active": active_drivers,
            "inactive": total_drivers - active_drivers,
            "verification_pending": pending_verifications,
            "approved": approved_drivers,
            "rejected": rejected_drivers
        },
        "employees": {
            "total": total_employees
        },
        "vehicles": {
            "total": total_vehicles,
            "available": available_vehicles,
            "in_use": total_vehicles - available_vehicles
        },
        "system": {
            "total_users": total_drivers + total_employees,
            "utilization_rate": round((active_drivers / total_drivers * 100) if total_drivers > 0 else 0, 2)
        }
    }


async def manage_user_status(db: Session, user_id: int, is_active: bool) -> dict:
    """Activate or deactivate a user account via auth service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.AUTH_SERVICE_URL}/auth/users/{user_id}/status",
                json={"is_active": is_active},
                timeout=5.0
            )
            if response.status_code == 200:
                return {"success": True, "message": f"User {'activated' if is_active else 'deactivated'} successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to update user status"
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable"
            )


def update_driver_verification_status(db: Session, driver_id: int, verification_status: str) -> dict:
    """Update driver identity verification status"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if verification_status not in ["approved", "rejected", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification status"
        )
    
    driver.identity_proof_status = verification_status
    db.commit()
    
    return {
        "success": True,
        "message": f"Driver verification status updated to {verification_status}",
        "driver_id": driver_id,
        "status": verification_status
    }


def assign_vehicle_to_driver(db: Session, vehicle_id: int, driver_id: int) -> dict:
    """Assign a vehicle to a driver"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Check if vehicle is already assigned
    if vehicle.driver_id and vehicle.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle is already assigned to another driver"
        )
    
    vehicle.driver_id = driver_id
    db.commit()
    
    return {
        "success": True,
        "message": f"Vehicle {vehicle.plate_number} assigned to driver {driver.name}",
        "vehicle_id": vehicle_id,
        "driver_id": driver_id
    }


def unassign_vehicle_from_driver(db: Session, vehicle_id: int) -> dict:
    """Remove vehicle assignment from driver"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    if not vehicle.driver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle is not assigned to any driver"
        )
    
    vehicle.driver_id = None
    db.commit()
    
    return {
        "success": True,
        "message": f"Vehicle {vehicle.plate_number} unassigned from driver",
        "vehicle_id": vehicle_id
    }