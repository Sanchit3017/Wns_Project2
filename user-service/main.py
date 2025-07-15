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
from sqlalchemy.orm import Session
from database import SessionLocal

def seed_employees():
    employees = [
        {"employee_id": "EMP006", "name": "Sanchit Dhale"},
        {"employee_id": "EMP007", "name": "Eshwar Bhore"},
        {"employee_id": "EMP008", "name": "Vinay Dubey"},
        {"employee_id": "EMP009", "name": "Rajeev"},
        {"employee_id": "EMP010", "name": "Aishwarya"},
    ]
    db: Session = SessionLocal()
    try:
        for idx, emp in enumerate(employees):
            # Use negative user_id to avoid conflict with real users
            user_id = -(idx + 1)
            existing = db.query(Employee).filter_by(employee_id=emp["employee_id"]).first()
            if not existing:
                db_emp = Employee(
                    user_id=user_id,
                    name=emp["name"],
                    employee_id=emp["employee_id"],
                    phone_number="",
                    home_location="",
                    commute_schedule=""
                )
                db.add(db_emp)
        db.commit()
    finally:
        db.close()

# Initialize settings
settings = UserServiceSettings()

# Create tables
Base.metadata.create_all(bind=engine)
# Seed initial employees
seed_employees()

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