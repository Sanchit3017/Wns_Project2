from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from api.driver import (
    get_driver_profile, update_driver_profile, get_all_drivers,
    update_availability, search_drivers_by_location, verify_driver_identity,
    upload_identity_proof, create_driver
)
from api.employee import (
    get_employee_profile, update_employee_profile,
    get_employee_by_id, create_employee, get_employee_by_employee_id
)
from api.admin import (
    create_admin, get_admin_profile, update_admin_profile,
    get_all_drivers, get_all_employees, assign_driver_to_employee,
    get_all_trips, toggle_user_status, get_admin_dashboard
)
from shared.schemas.user import (
    DriverResponse, DriverUpdate, DriverWithUser, EmployeeResponse, 
    EmployeeUpdate, EmployeeWithUser, LocationBasedDriverSearch,
    IdentityVerificationUpdate, DriverCreate, EmployeeCreate,
    AdminResponse, AdminUpdate, AdminWithUser, AdminCreate,
    UserStatusUpdate, SystemStatistics
)
from typing import List, Optional
import os

router = APIRouter()
security = HTTPBearer()


# Import database dependency from database module
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from database import get_database_session as get_db


def get_user_context(x_user_id: Optional[str] = Header(None), 
                    x_user_role: Optional[str] = Header(None)):
    """Extract user context from headers (set by API Gateway)"""
    if not x_user_id or not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User context headers missing"
        )
    return {"user_id": int(x_user_id), "role": x_user_role}


# Driver endpoints
@router.post("/drivers", response_model=DriverResponse)
async def create_driver_profile(
    driver_data: DriverCreate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Create driver profile"""
    return await create_driver(db, user_context["user_id"], driver_data)


@router.get("/drivers/profile", response_model=DriverResponse)
async def get_driver_profile_endpoint(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get driver profile"""
    return get_driver_profile(db, user_context["user_id"])


@router.put("/drivers/profile", response_model=DriverResponse)
async def update_driver_profile_endpoint(
    driver_update: DriverUpdate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update driver profile"""
    return update_driver_profile(db, user_context["user_id"], driver_update)


@router.get("/drivers", response_model=List[DriverWithUser])
async def list_all_drivers(
    user_context: dict = Depends(get_user_context),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all drivers (admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_all_drivers(db, credentials.credentials)


@router.put("/drivers/availability")
async def update_driver_availability(
    is_available: bool,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update driver availability"""
    success = update_availability(db, user_context["user_id"], is_available)
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Availability updated successfully"}


@router.post("/drivers/search-by-location")
async def search_drivers_by_location_endpoint(
    search_request: LocationBasedDriverSearch,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Search drivers by location (admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return search_drivers_by_location(db, search_request.employee_location)


@router.put("/drivers/{driver_id}/verify-identity")
async def verify_driver_identity_endpoint(
    driver_id: int,
    verification_update: IdentityVerificationUpdate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Verify driver identity (admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = verify_driver_identity(db, driver_id, verification_update.identity_proof_status)
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Identity verification status updated"}


@router.post("/drivers/upload-identity")
async def upload_identity_proof_endpoint(
    file: UploadFile = File(...),
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Upload identity proof document"""
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PDF, JPG, PNG allowed."
        )
    
    # Save file
    upload_dir = "uploads/identity_proofs"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{user_context['user_id']}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update driver record
    success = upload_identity_proof(db, user_context["user_id"], file_path)
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {"message": "Identity proof uploaded successfully", "file_path": file_path}


# Employee endpoints
@router.post("/employees", response_model=EmployeeResponse)
async def create_employee_profile(
    employee_data: EmployeeCreate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Create employee profile"""
    return await create_employee(db, user_context["user_id"], employee_data)


@router.get("/employees/profile", response_model=EmployeeResponse)
async def get_employee_profile_endpoint(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get employee profile"""
    return get_employee_profile(db, user_context["user_id"])


@router.put("/employees/profile", response_model=EmployeeResponse)
async def update_employee_profile_endpoint(
    employee_update: EmployeeUpdate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update employee profile"""
    return update_employee_profile(db, user_context["user_id"], employee_update)


@router.get("/employees", response_model=List[dict])
async def list_all_employees(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get all employees (admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_all_employees(db)


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id_endpoint(
    employee_id: int,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get employee by ID (internal use)"""
    return get_employee_by_id(db, employee_id)


@router.get("/employees/by-employee-id/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_employee_id_endpoint(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get employee by employee_id (string, e.g., EMP006)"""
    return get_employee_by_employee_id(db, employee_id)


# ===== ADMIN ENDPOINTS =====

@router.post("/admins", response_model=AdminResponse)
async def create_admin_profile(
    admin_data: AdminCreate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Create admin profile"""
    return await create_admin(db, user_context["user_id"], admin_data)


@router.get("/admins/profile", response_model=AdminResponse)
async def get_admin_profile_endpoint(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get admin profile"""
    return get_admin_profile(db, user_context["user_id"])


@router.put("/admins/profile", response_model=AdminResponse)
async def update_admin_profile_endpoint(
    admin_update: AdminUpdate,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update admin profile"""
    return update_admin_profile(db, user_context["user_id"], admin_update)





# ===== COMPREHENSIVE ADMIN MANAGEMENT ENDPOINTS =====

@router.get("/admin/drivers", response_model=List[dict])
async def admin_list_all_drivers(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Get all drivers with user details"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_all_drivers(db)


@router.get("/admin/employees", response_model=List[dict])
async def admin_list_all_employees(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Get all employees with user details"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_all_employees(db)


@router.post("/admin/assign-driver")
async def admin_assign_driver_to_employee(
    employee_id: int,
    driver_id: Optional[int] = None,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Assign driver to employee based on location or specific driver ID"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await assign_driver_to_employee(db, employee_id, driver_id)


@router.get("/admin/trips")
async def admin_get_all_trips(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Get all trips from trip service"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_all_trips(db)


@router.put("/admin/users/{user_id}/toggle-status")
async def admin_toggle_user_status(
    user_id: int,
    user_type: str,
    new_status: bool,
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Toggle status of driver or employee"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await toggle_user_status(db, user_id, user_type, new_status)


@router.get("/admin/dashboard")
async def admin_get_dashboard(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Get comprehensive admin dashboard data"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_admin_dashboard(db)


@router.get("/admin/statistics")
async def admin_get_statistics(
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Admin: Get system statistics (alias for dashboard)"""
    if user_context["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return await get_admin_dashboard(db)


