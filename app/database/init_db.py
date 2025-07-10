"""
Database initialization with sample data
"""
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.user import User
from app.models.driver import Driver
from app.models.employee import Employee
from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.notification import Notification
from app.core.security import get_password_hash
from datetime import datetime, timedelta


def init_database():
    """Initialize database with sample data"""
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            return
        
        # Create Admin user
        admin_user = User(
            email="admin@travel.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        
        # Create Driver users
        driver1_user = User(
            email="driver1@travel.com",
            hashed_password=get_password_hash("driver123"),
            role="driver",
            is_active=True
        )
        db.add(driver1_user)
        db.flush()
        
        driver2_user = User(
            email="driver2@travel.com",
            hashed_password=get_password_hash("driver123"),
            role="driver",
            is_active=True
        )
        db.add(driver2_user)
        db.flush()
        
        # Create Employee users
        employee1_user = User(
            email="employee1@travel.com",
            hashed_password=get_password_hash("emp123"),
            role="employee",
            is_active=True
        )
        db.add(employee1_user)
        db.flush()
        
        employee2_user = User(
            email="employee2@travel.com",
            hashed_password=get_password_hash("emp123"),
            role="employee",
            is_active=True
        )
        db.add(employee2_user)
        db.flush()
        
        employee3_user = User(
            email="employee3@travel.com",
            hashed_password=get_password_hash("emp123"),
            role="employee",
            is_active=True
        )
        db.add(employee3_user)
        db.flush()
        
        # Create Driver profiles
        driver1 = Driver(
            user_id=driver1_user.id,
            name="John Driver",
            phone_number="+1234567890",
            dl_number="DL123456789",
            vehicle_plate_number="ABC123"
        )
        db.add(driver1)
        
        driver2 = Driver(
            user_id=driver2_user.id,
            name="Jane Driver",
            phone_number="+1234567891",
            dl_number="DL987654321",
            vehicle_plate_number="XYZ789"
        )
        db.add(driver2)
        
        # Create Employee profiles
        employee1 = Employee(
            user_id=employee1_user.id,
            name="Alice Employee",
            employee_id="EMP001",
            phone_number="+1234567892",
            home_location="Downtown Area",
            commute_schedule="9:00 AM - 6:00 PM"
        )
        db.add(employee1)
        
        employee2 = Employee(
            user_id=employee2_user.id,
            name="Bob Employee",
            employee_id="EMP002",
            phone_number="+1234567893",
            home_location="Uptown Area",
            commute_schedule="8:30 AM - 5:30 PM"
        )
        db.add(employee2)
        
        employee3 = Employee(
            user_id=employee3_user.id,
            name="Charlie Employee",
            employee_id="EMP003",
            phone_number="+1234567894",
            home_location="Suburb Area",
            commute_schedule="10:00 AM - 7:00 PM"
        )
        db.add(employee3)
        
        # Create Vehicles
        vehicle1 = Vehicle(
            plate_number="ABC123",
            vehicle_type="Sedan",
            capacity=4,
            driver_id=driver1.id
        )
        db.add(vehicle1)
        
        vehicle2 = Vehicle(
            plate_number="XYZ789",
            vehicle_type="SUV",
            capacity=6,
            driver_id=driver2.id
        )
        db.add(vehicle2)
        
        db.flush()
        
        # Create Sample Trips
        trip1 = Trip(
            pickup_location="Downtown Office",
            destination="Airport",
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            employee_id=employee1.id,
            driver_id=driver1.id,
            vehicle_id=vehicle1.id
        )
        db.add(trip1)
        
        trip2 = Trip(
            pickup_location="Hotel Plaza",
            destination="Conference Center",
            scheduled_time=datetime.utcnow() + timedelta(hours=4),
            status="scheduled",
            employee_id=employee2.id,
            driver_id=driver2.id,
            vehicle_id=vehicle2.id
        )
        db.add(trip2)
        
        trip3 = Trip(
            pickup_location="Train Station",
            destination="Office Complex",
            scheduled_time=datetime.utcnow() - timedelta(hours=1),
            status="completed",
            employee_id=employee3.id,
            driver_id=driver1.id,
            vehicle_id=vehicle1.id,
            actual_start_time=datetime.utcnow() - timedelta(hours=1, minutes=30),
            actual_end_time=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add(trip3)
        
        db.flush()
        
        # Create Sample Notifications
        notifications = [
            Notification(
                title="Trip Assignment",
                message="You have been assigned a new trip to Airport",
                recipient_id=driver1_user.id,
                seen=False
            ),
            Notification(
                title="Trip Reminder",
                message="Your trip to Conference Center is scheduled in 4 hours",
                recipient_id=employee2_user.id,
                seen=False
            ),
            Notification(
                title="Trip Completed",
                message="Your trip to Office Complex has been completed",
                recipient_id=employee3_user.id,
                seen=True
            ),
            Notification(
                title="System Update",
                message="Travel management system has been updated",
                recipient_id=admin_user.id,
                seen=False
            ),
            Notification(
                title="New Driver Registration",
                message="A new driver has registered in the system",
                recipient_id=admin_user.id,
                seen=False
            )
        ]
        
        for notification in notifications:
            db.add(notification)
        
        # Commit all changes
        db.commit()
        print("Database initialized with sample data successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
