from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.driver import Driver
from app.models.employee import Employee
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.schemas.driver import DriverRegistration
from app.schemas.employee import EmployeeRegistration
from app.core.security import verify_password, get_password_hash, create_access_token


def authenticate_user(db: Session, email: str, password: str) -> User:
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    return user


def register_user(db: Session, role: str, user_data: dict) -> Token:
    
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
        role=role,
        is_active=True
    )
    db.add(user)
    db.flush()
    
    
    if role == "driver":
        driver = Driver(
            user_id=user.id,
            name=user_data["name"],
            phone_number=user_data["phone_number"],
            dl_number=user_data["dl_number"],
            vehicle_plate_number=user_data["vehicle_plate_number"],
            service_area=user_data.get("service_area")
        )
        db.add(driver)
    elif role == "employee":
        employee = Employee(
            user_id=user.id,
            name=user_data["name"],
            employee_id=user_data["employee_id"],
            phone_number=user_data["phone_number"],
            home_location=user_data["home_location"],
            commute_schedule=user_data["commute_schedule"]
        )
        db.add(employee)
    
    db.commit()
    
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


def login_user(db: Session, email: str, password: str) -> Token:
    
    user = authenticate_user(db, email, password)
    
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


def get_current_user(db: Session, user_id: int) -> User:
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    return user
