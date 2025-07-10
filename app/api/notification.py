from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationWithRecipient, BulkNotification
from typing import List


def create_notification(db: Session, notification_data: NotificationCreate) -> NotificationResponse:
    
    recipient = db.query(User).filter(User.id == notification_data.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        recipient_id=notification_data.recipient_id
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return NotificationResponse.from_orm(notification)


def get_user_notifications(db: Session, user_id: int, include_seen: bool = True) -> List[NotificationResponse]:
    
    query = db.query(Notification).filter(Notification.recipient_id == user_id)
    
    if not include_seen:
        query = query.filter(Notification.seen == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    return [NotificationResponse.from_orm(notification) for notification in notifications]


def mark_notification_as_seen(db: Session, user_id: int, notification_id: int) -> bool:
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.seen = True
    db.commit()
    return True


def mark_all_notifications_as_seen(db: Session, user_id: int) -> bool:
    
    db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.seen == False
    ).update({"seen": True})
    
    db.commit()
    return True


def get_all_notifications_with_recipients(db: Session) -> List[NotificationWithRecipient]:
    
    notifications = db.query(Notification).join(User).order_by(Notification.created_at.desc()).all()
    
    result = []
    for notification in notifications:
        result.append(NotificationWithRecipient(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            recipient_id=notification.recipient_id,
            recipient_email=notification.recipient.email,
            seen=notification.seen,
            created_at=notification.created_at
        ))
    return result


def send_bulk_notification(db: Session, bulk_notification: BulkNotification) -> List[NotificationResponse]:
    
    recipient_ids = []
    
    if bulk_notification.recipient_role:
        
        users = db.query(User).filter(User.role == bulk_notification.recipient_role).all()
        recipient_ids = [user.id for user in users]
    elif bulk_notification.recipient_ids:
        
        recipient_ids = bulk_notification.recipient_ids
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either recipient_role or recipient_ids must be provided"
        )
    
    created_notifications = []
    for recipient_id in recipient_ids:
        notification = Notification(
            title=bulk_notification.title,
            message=bulk_notification.message,
            recipient_id=recipient_id
        )
        db.add(notification)
        created_notifications.append(notification)
    
    db.commit()
    
    
    for notification in created_notifications:
        db.refresh(notification)
    
    return [NotificationResponse.from_orm(notification) for notification in created_notifications]


def delete_notification(db: Session, user_id: int, notification_id: int) -> bool:
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    return True


def get_unread_count(db: Session, user_id: int) -> int:
    
    count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.seen == False
    ).count()
    return count
