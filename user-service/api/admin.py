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