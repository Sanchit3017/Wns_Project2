"""
Utility functions for notification management
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from typing import List, Optional


def send_notification_to_user(
    db: Session,
    user_id: int,
    title: str,
    message: str
) -> Notification:
    """Send a notification to a specific user"""
    notification = Notification(
        title=title,
        message=message,
        recipient_id=user_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def send_notification_to_role(
    db: Session,
    role: str,
    title: str,
    message: str
) -> List[Notification]:
    """Send notifications to all users with a specific role"""
    users = db.query(User).filter(User.role == role, User.is_active == True).all()
    notifications = []
    
    for user in users:
        notification = Notification(
            title=title,
            message=message,
            recipient_id=user.id
        )
        db.add(notification)
        notifications.append(notification)
    
    db.commit()
    
    for notification in notifications:
        db.refresh(notification)
    
    return notifications


def send_trip_assignment_notification(
    db: Session,
    driver_id: int,
    trip_details: dict
) -> Notification:
    """Send trip assignment notification to driver"""
    title = "New Trip Assignment"
    message = (
        f"You have been assigned a new trip from {trip_details['pickup_location']} "
        f"to {trip_details['destination']} scheduled for {trip_details['scheduled_time']}"
    )
    
    # Get driver's user_id
    from app.models.driver import Driver
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if driver:
        return send_notification_to_user(db, driver.user_id, title, message)
    return None


def send_trip_reminder_notification(
    db: Session,
    employee_id: int,
    trip_details: dict
) -> Notification:
    """Send trip reminder notification to employee"""
    title = "Trip Reminder"
    message = (
        f"Your trip to {trip_details['destination']} is scheduled for "
        f"{trip_details['scheduled_time']}. Please be ready at the pickup location."
    )
    
    # Get employee's user_id
    from app.models.employee import Employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        return send_notification_to_user(db, employee.user_id, title, message)
    return None


def send_trip_completion_notification(
    db: Session,
    employee_id: int,
    trip_details: dict
) -> Notification:
    """Send trip completion notification to employee"""
    title = "Trip Completed"
    message = (
        f"Your trip to {trip_details['destination']} has been completed successfully. "
        f"Thank you for using our travel service."
    )
    
    # Get employee's user_id
    from app.models.employee import Employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        return send_notification_to_user(db, employee.user_id, title, message)
    return None


def send_trip_reschedule_notification(
    db: Session,
    user_ids: List[int],
    trip_details: dict
) -> List[Notification]:
    """Send trip reschedule notification to multiple users"""
    title = "Trip Rescheduled"
    message = (
        f"Trip from {trip_details['pickup_location']} to {trip_details['destination']} "
        f"has been rescheduled to {trip_details['new_scheduled_time']}"
    )
    
    notifications = []
    for user_id in user_ids:
        notification = send_notification_to_user(db, user_id, title, message)
        notifications.append(notification)
    
    return notifications


def send_system_notification(
    db: Session,
    title: str,
    message: str,
    target_role: Optional[str] = None
) -> List[Notification]:
    """Send system-wide notifications"""
    if target_role:
        return send_notification_to_role(db, target_role, title, message)
    else:
        # Send to all active users
        users = db.query(User).filter(User.is_active == True).all()
        notifications = []
        
        for user in users:
            notification = Notification(
                title=title,
                message=message,
                recipient_id=user.id
            )
            db.add(notification)
            notifications.append(notification)
        
        db.commit()
        
        for notification in notifications:
            db.refresh(notification)
        
        return notifications


def cleanup_old_notifications(db: Session, days_old: int = 30) -> int:
    """Clean up notifications older than specified days"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    deleted_count = db.query(Notification).filter(
        Notification.created_at < cutoff_date,
        Notification.seen == True
    ).delete()
    
    db.commit()
    return deleted_count
