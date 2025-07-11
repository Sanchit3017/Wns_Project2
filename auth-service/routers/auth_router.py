from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from api.auth import login_user, validate_token_and_get_user, create_user
from shared.schemas.auth import UserLogin, Token, UserResponse, UserCreate, ServiceUserContext
from shared.database.base import get_db_session

router = APIRouter()
security = HTTPBearer()


def get_db():
    """Get database session"""
    # This will be configured in main.py
    yield None


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    return login_user(db, user_credentials.email, user_credentials.password)


@router.post("/validate", response_model=ServiceUserContext)
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate JWT token - used by API Gateway and other services"""
    user = validate_token_and_get_user(db, credentials.credentials)
    return ServiceUserContext(
        user_id=user.id,
        role=user.role,
        email=user.email
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user - internal service use only"""
    user = create_user(db, user_data)
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    return validate_token_and_get_user(db, credentials.credentials)


@router.post("/logout")
async def logout():
    """Logout endpoint - JWT tokens are stateless so just return success"""
    return {"message": "Successfully logged out"}