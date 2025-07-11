from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserProfile(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Service-to-service authentication schemas
class ServiceAuthRequest(BaseModel):
    token: str


class ServiceUserContext(BaseModel):
    user_id: int
    role: str
    email: str