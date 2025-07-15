from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.employee import Employee
from shared.schemas.user import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeWithUser
from shared.utils.http_client import ServiceClient
from shared.config import UserServiceSettings
from typing import List


settings = UserServiceSettings()
auth_client = ServiceClient(settings.AUTH_SERVICE_URL)


async def create_employee(db: Session, user_id: int, employee_data: EmployeeCreate) -> EmployeeResponse:
    """Create employee profile"""
    # Check if employee already exists
    existing_employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists"
        )

    # Auto-generate employee_id if not provided
    if not employee_data.employee_id:
        # Get the highest current employee_id in the format EMP###
        last_employee = db.query(Employee).filter(Employee.employee_id.like("EMP%")) \
            .order_by(Employee.employee_id.desc()).first()
        if last_employee and last_employee.employee_id[3:].isdigit():
            next_num = int(last_employee.employee_id[3:]) + 1
        else:
            next_num = 1
        new_employee_id = f"EMP{next_num:03d}"
    else:
        new_employee_id = employee_data.employee_id

    db_employee = Employee(
        user_id=user_id,
        name=employee_data.name,
        employee_id=new_employee_id,
        phone_number=employee_data.phone_number,
        home_location=employee_data.home_location,
        commute_schedule=employee_data.commute_schedule
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return EmployeeResponse(
        id=db_employee.id,
        user_id=db_employee.user_id,
        name=db_employee.name,
        employee_id=db_employee.employee_id,
        phone_number=db_employee.phone_number,
        home_location=db_employee.home_location,
        commute_schedule=db_employee.commute_schedule,
        created_at=db_employee.created_at,
        updated_at=db_employee.updated_at
    )


def get_employee_profile(db: Session, user_id: int) -> EmployeeResponse:
    """Get employee profile by user ID"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    return EmployeeResponse(
        id=employee.id,
        user_id=employee.user_id,
        name=employee.name,
        employee_id=employee.employee_id,
        phone_number=employee.phone_number,
        home_location=employee.home_location,
        commute_schedule=employee.commute_schedule,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


def update_employee_profile(db: Session, user_id: int, employee_update: EmployeeUpdate) -> EmployeeResponse:
    """Update employee profile"""
    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Update fields
    for field, value in employee_update.dict(exclude_unset=True).items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse(
        id=employee.id,
        user_id=employee.user_id,
        name=employee.name,
        employee_id=employee.employee_id,
        phone_number=employee.phone_number,
        home_location=employee.home_location,
        commute_schedule=employee.commute_schedule,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


async def get_all_employees(db: Session, auth_token: str) -> List[EmployeeWithUser]:
    """Get all employees with user information"""
    employees = db.query(Employee).all()
    
    result = []
    for employee in employees:
        # Get user info from auth service
        try:
            user_info = await auth_client.get(
                f"/auth/profile",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            result.append(EmployeeWithUser(
                id=employee.id,
                user_id=employee.user_id,
                name=employee.name,
                employee_id=employee.employee_id,
                phone_number=employee.phone_number,
                home_location=employee.home_location,
                commute_schedule=employee.commute_schedule,
                email=user_info.get("email", ""),
                is_active=user_info.get("is_active", True),
                created_at=employee.created_at
            ))
        except Exception:
            # If we can't get user info, still include employee data
            result.append(EmployeeWithUser(
                id=employee.id,
                user_id=employee.user_id,
                name=employee.name,
                employee_id=employee.employee_id,
                phone_number=employee.phone_number,
                home_location=employee.home_location,
                commute_schedule=employee.commute_schedule,
                email="",
                is_active=True,
                created_at=employee.created_at
            ))
    
    return result


def get_employee_by_id(db: Session, employee_id: int) -> EmployeeResponse:
    """Get employee by internal ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return EmployeeResponse(
        id=employee.id,
        user_id=employee.user_id,
        name=employee.name,
        employee_id=employee.employee_id,
        phone_number=employee.phone_number,
        home_location=employee.home_location,
        commute_schedule=employee.commute_schedule,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


def get_employee_by_employee_id(db: Session, employee_id_str: str) -> EmployeeResponse:
    """Get employee by employee_id (string, e.g., EMP006)"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id_str).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return EmployeeResponse(
        id=employee.id,
        user_id=employee.user_id,
        name=employee.name,
        employee_id=employee.employee_id,
        phone_number=employee.phone_number,
        home_location=employee.home_location,
        commute_schedule=employee.commute_schedule,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )