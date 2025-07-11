import os
from typing import Optional
from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    """Base settings for all microservices"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/travel_management")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Service Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Service URLs (for inter-service communication)
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
    TRIP_SERVICE_URL: str = os.getenv("TRIP_SERVICE_URL", "http://localhost:8003")
    NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


class AuthServiceSettings(BaseServiceSettings):
    """Settings specific to auth service"""
    APP_NAME: str = "Auth Service"
    PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8001"))
    DATABASE_URL: str = os.getenv("AUTH_DATABASE_URL", 
                                 os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/auth_service"))


class UserServiceSettings(BaseServiceSettings):
    """Settings specific to user service"""
    APP_NAME: str = "User Service"
    PORT: int = int(os.getenv("USER_SERVICE_PORT", "8002"))
    DATABASE_URL: str = os.getenv("USER_DATABASE_URL", 
                                 os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/user_service"))


class TripServiceSettings(BaseServiceSettings):
    """Settings specific to trip service"""
    APP_NAME: str = "Trip Service"
    PORT: int = int(os.getenv("TRIP_SERVICE_PORT", "8003"))
    DATABASE_URL: str = os.getenv("TRIP_DATABASE_URL", 
                                 os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/trip_service"))


class NotificationServiceSettings(BaseServiceSettings):
    """Settings specific to notification service"""
    APP_NAME: str = "Notification Service"
    PORT: int = int(os.getenv("NOTIFICATION_SERVICE_PORT", "8004"))
    DATABASE_URL: str = os.getenv("NOTIFICATION_DATABASE_URL", 
                                 os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/notification_service"))


class APIGatewaySettings(BaseServiceSettings):
    """Settings specific to API gateway"""
    APP_NAME: str = "API Gateway"
    PORT: int = int(os.getenv("API_GATEWAY_PORT", "8000"))