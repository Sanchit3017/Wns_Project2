"""
Authentication router for user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.auth import register_user, login_user, get_current_user
from app.schemas.auth import UserLogin, Token, UserProfile
from app.schemas.driver import DriverRegistration
from app.schemas.employee import EmployeeRegistration
from app.core.security import get_current_user_id

router = APIRouter()
security = HTTPBearer()


@router.post("/register/admin", response_model=Token)
async def register_admin(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Register a new admin user"""
    user_data = {"email": email, "password": password}
    return register_user(db, "admin", user_data)


@router.post("/register/driver", response_model=Token)
async def register_driver(
    driver_data: DriverRegistration,
    db: Session = Depends(get_db)
):
    """Register a new driver"""
    user_data = driver_data.dict()
    return register_user(db, "driver", user_data)


@router.post("/register/employee", response_model=Token)
async def register_employee(
    employee_data: EmployeeRegistration,
    db: Session = Depends(get_db)
):
    """Register a new employee"""
    user_data = employee_data.dict()
    return register_user(db, "employee", user_data)


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user with email and password"""
    return login_user(db, user_credentials.email, user_credentials.password)


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    user_id = get_current_user_id(credentials.credentials)
    user = get_current_user(db, user_id)
    return UserProfile.from_orm(user)


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
