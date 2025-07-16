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
        {"employee_id": "EMP001", "name": "Aarav Sharma", "phone_number": "9876543201", "home_location": "Whitefield", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP002", "name": "Priya Patel", "phone_number": "9876543202", "home_location": "Koramangala", "commute_schedule": "8:30 AM - 5:30 PM"},
        {"employee_id": "EMP003", "name": "Rahul Verma", "phone_number": "9876543203", "home_location": "Indiranagar", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP004", "name": "Anjali Singh", "phone_number": "9876543204", "home_location": "JP Nagar", "commute_schedule": "8:00 AM - 5:00 PM"},
        {"employee_id": "EMP005", "name": "Vikram Kumar", "phone_number": "9876543205", "home_location": "Marathahalli", "commute_schedule": "9:30 AM - 6:30 PM"},
        {"employee_id": "EMP006", "name": "Sanchit Dhale", "phone_number": "9876543206", "home_location": "Electronic City", "commute_schedule": "8:00 AM - 5:00 PM"},
        {"employee_id": "EMP007", "name": "Eshwar Bhore", "phone_number": "9876543207", "home_location": "Bellandur", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP008", "name": "Vinay Dubey", "phone_number": "9876543208", "home_location": "HSR Layout", "commute_schedule": "8:30 AM - 5:30 PM"},
        {"employee_id": "EMP009", "name": "Rajeev", "phone_number": "9876543209", "home_location": "Bannerghatta", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP010", "name": "Aishwarya", "phone_number": "9876543210", "home_location": "Sarjapur", "commute_schedule": "8:00 AM - 5:00 PM"},
        {"employee_id": "EMP011", "name": "Neha Gupta", "phone_number": "9876543211", "home_location": "Domlur", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP012", "name": "Arjun Reddy", "phone_number": "9876543212", "home_location": "Bommanahalli", "commute_schedule": "8:30 AM - 5:30 PM"},
        {"employee_id": "EMP013", "name": "Kavya Iyer", "phone_number": "9876543213", "home_location": "Hebbal", "commute_schedule": "9:00 AM - 6:00 PM"},
        {"employee_id": "EMP014", "name": "Siddharth Malhotra", "phone_number": "9876543214", "home_location": "Yelahanka", "commute_schedule": "8:00 AM - 5:00 PM"},
        {"employee_id": "EMP015", "name": "Zara Khan", "phone_number": "9876543215", "home_location": "Malleswaram", "commute_schedule": "9:30 AM - 6:30 PM"},
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
                    phone_number=emp["phone_number"],
                    home_location=emp["home_location"],
                    commute_schedule=emp["commute_schedule"]
                )
                db.add(db_emp)
        db.commit()
    finally:
        db.close()

def seed_drivers():
    drivers = [
        {"user_id": -101, "name": "Ravi Kumar", "phone_number": "9876543210", "dl_number": "DL1001", "vehicle_plate_number": "KA01AB1234", "service_area": "Whitefield", "is_available": True},
        {"user_id": -102, "name": "Sunil Sharma", "phone_number": "9876543211", "dl_number": "DL1002", "vehicle_plate_number": "KA01AB5678", "service_area": "Koramangala", "is_available": True},
        {"user_id": -103, "name": "Priya Singh", "phone_number": "9876543212", "dl_number": "DL1003", "vehicle_plate_number": "KA01AB9101", "service_area": "Indiranagar", "is_available": False},
        {"user_id": -104, "name": "Amit Patel", "phone_number": "9876543213", "dl_number": "DL1004", "vehicle_plate_number": "KA01AB1122", "service_area": "JP Nagar", "is_available": True},
        {"user_id": -105, "name": "Meena Joshi", "phone_number": "9876543214", "dl_number": "DL1005", "vehicle_plate_number": "KA01AB3344", "service_area": "Marathahalli", "is_available": True},
        {"user_id": -106, "name": "Rajesh Kumar", "phone_number": "9876543215", "dl_number": "DL1006", "vehicle_plate_number": "KA01AB5566", "service_area": "Electronic City", "is_available": True},
        {"user_id": -107, "name": "Lakshmi Devi", "phone_number": "9876543216", "dl_number": "DL1007", "vehicle_plate_number": "KA01AB7788", "service_area": "Bellandur", "is_available": False},
        {"user_id": -108, "name": "Suresh Reddy", "phone_number": "9876543217", "dl_number": "DL1008", "vehicle_plate_number": "KA01AB9900", "service_area": "HSR Layout", "is_available": True},
        {"user_id": -109, "name": "Geeta Sharma", "phone_number": "9876543218", "dl_number": "DL1009", "vehicle_plate_number": "KA01AB1122", "service_area": "Bannerghatta", "is_available": True},
        {"user_id": -110, "name": "Mohan Das", "phone_number": "9876543219", "dl_number": "DL1010", "vehicle_plate_number": "KA01AB3344", "service_area": "Sarjapur", "is_available": True},
        {"user_id": -111, "name": "Anita Verma", "phone_number": "9876543220", "dl_number": "DL1011", "vehicle_plate_number": "KA01AB5566", "service_area": "Domlur", "is_available": False},
        {"user_id": -112, "name": "Prakash Singh", "phone_number": "9876543221", "dl_number": "DL1012", "vehicle_plate_number": "KA01AB7788", "service_area": "Bommanahalli", "is_available": True},
        {"user_id": -113, "name": "Rekha Patel", "phone_number": "9876543222", "dl_number": "DL1013", "vehicle_plate_number": "KA01AB9900", "service_area": "Hebbal", "is_available": True},
        {"user_id": -114, "name": "Vijay Kumar", "phone_number": "9876543223", "dl_number": "DL1014", "vehicle_plate_number": "KA01AB1122", "service_area": "Yelahanka", "is_available": True},
        {"user_id": -115, "name": "Sunita Iyer", "phone_number": "9876543224", "dl_number": "DL1015", "vehicle_plate_number": "KA01AB3344", "service_area": "Malleswaram", "is_available": False},
    ]
    db: Session = SessionLocal()
    try:
        for drv in drivers:
            existing = db.query(Driver).filter_by(dl_number=drv["dl_number"]).first()
            if not existing:
                db_drv = Driver(
                    user_id=drv["user_id"],
                    name=drv["name"],
                    phone_number=drv["phone_number"],
                    dl_number=drv["dl_number"],
                    vehicle_plate_number=drv["vehicle_plate_number"],
                    is_available=drv["is_available"],
                    service_area=drv["service_area"]
                )
                db.add(db_drv)
        db.commit()
    finally:
        db.close()

# Initialize settings
settings = UserServiceSettings()

# Create tables
Base.metadata.create_all(bind=engine)
# Seed initial employees
seed_employees()
# Seed initial drivers
seed_drivers()

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