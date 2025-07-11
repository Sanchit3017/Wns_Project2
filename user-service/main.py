import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import UserServiceSettings
from routers.user_router import router as user_router
from models.driver import Driver
from models.employee import Employee
from models.vehicle import Vehicle
from models.admin import Admin
from database import engine, Base
import uvicorn

# Initialize settings
settings = UserServiceSettings()

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