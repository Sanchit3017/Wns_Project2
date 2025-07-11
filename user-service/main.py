import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from shared.config import UserServiceSettings
from shared.database.base import create_database_engine, create_session_factory, Base
from routers.user_router import router as user_router
from models.driver import Driver
from models.employee import Employee
from models.vehicle import Vehicle
import uvicorn

# Initialize settings
settings = UserServiceSettings()

# Create database engine and session factory
engine = create_database_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = create_session_factory(engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="User Service for Travel Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Update the router's get_db dependency
user_router.dependency_overrides = {
    "get_db": get_db
}

# Include routers
app.include_router(user_router, prefix="/users", tags=["Users"])

@app.get("/")
async def root():
    return {"service": "User Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)