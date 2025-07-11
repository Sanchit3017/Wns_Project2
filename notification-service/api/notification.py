from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.notification import Notification
from shared.schemas.notification import NotificationCreate, NotificationResponse, BulkNotification
from typing import List

def create_notification(db: Session, notification_data: NotificationCreate) -> NotificationResponse:
    """Create new notification"""
    db_notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        recipient_id=notification_data.recipient_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return NotificationResponse(
        id=db_notification.id,
        title=db_notification.title,
        message=db_notification.message,
        recipient_id=db_notification.recipient_id,
        seen=db_notification.seen,
        created_at=db_notification.created_at
    )

def get_user_notifications(db: Session, user_id: int, include_seen: bool = True) -> List[NotificationResponse]:
    """Get notifications for user"""
    query = db.query(Notification).filter(Notification.recipient_id == user_id)
    
    if not include_seen:
        query = query.filter(Notification.seen == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    return [NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        recipient_id=notification.recipient_id,
        seen=notification.seen,
        created_at=notification.created_at
    ) for notification in notifications]

def mark_notification_as_seen(db: Session, user_id: int, notification_id: int) -> bool:
    """Mark notification as seen"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        return False
    
    notification.seen = True
    db.commit()
    return True

def mark_all_notifications_as_seen(db: Session, user_id: int) -> bool:
    """Mark all notifications as seen for user"""
    db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.seen == False
    ).update({"seen": True})
    db.commit()
    return True

def delete_notification(db: Session, user_id: int, notification_id: int) -> bool:
    """Delete notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        return False
    
    db.delete(notification)
    db.commit()
    return True

def get_unread_count(db: Session, user_id: int) -> int:
    """Get count of unread notifications"""
    return db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.seen == False
    ).count()

def send_bulk_notification(db: Session, bulk_notification: BulkNotification) -> List[NotificationResponse]:
    """Send bulk notifications"""
    notifications = []
    
    for recipient_id in bulk_notification.recipient_ids:
        db_notification = Notification(
            title=bulk_notification.title,
            message=bulk_notification.message,
            recipient_id=recipient_id
        )
        db.add(db_notification)
        notifications.append(db_notification)
    
    db.commit()
    
    # Refresh all notifications to get IDs
    for notification in notifications:
        db.refresh(notification)
    
    return [NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        recipient_id=notification.recipient_id,
        seen=notification.seen,
        created_at=notification.created_at
    ) for notification in notifications]