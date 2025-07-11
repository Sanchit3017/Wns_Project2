from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from api.notification import (
    create_notification, get_user_notifications, mark_notification_as_seen,
    mark_all_notifications_as_seen, send_bulk_notification, delete_notification,
    get_unread_count
)
from shared.schemas.notification import NotificationCreate, NotificationResponse, BulkNotification
from shared.database.base import get_db_session
from typing import List, Optional

router = APIRouter()

def get_db():
    """Get database session"""
    return next(get_db_session())

def get_user_context(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None)
):
    """Get user context from headers (set by API Gateway)"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User context not found"
        )
    return {
        "user_id": int(x_user_id),
        "role": x_user_role,
        "email": x_user_email
    }

@router.post("/notifications", response_model=NotificationResponse)
def create_new_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Create a new notification (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create notifications"
        )
    return create_notification(db, notification_data)

@router.get("/notifications", response_model=List[NotificationResponse])
def get_my_notifications(
    include_seen: bool = True,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get notifications for current user"""
    return get_user_notifications(db, user_context["user_id"], include_seen)

@router.get("/notifications/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Get count of unread notifications for current user"""
    count = get_unread_count(db, user_context["user_id"])
    return {"unread_count": count}

@router.put("/notifications/{notification_id}/seen")
def mark_notification_seen(
    notification_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Mark a notification as seen"""
    success = mark_notification_as_seen(db, user_context["user_id"], notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as seen"}

@router.put("/notifications/mark-all-seen")
def mark_all_notifications_seen(
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Mark all notifications as seen for current user"""
    success = mark_all_notifications_as_seen(db, user_context["user_id"])
    return {"message": f"All notifications marked as seen", "success": success}

@router.delete("/notifications/{notification_id}")
def delete_notification_by_id(
    notification_id: int,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Delete a notification"""
    success = delete_notification(db, user_context["user_id"], notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification deleted successfully"}

@router.post("/notifications/bulk", response_model=List[NotificationResponse])
def send_bulk_notifications(
    bulk_notification: BulkNotification,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_user_context)
):
    """Send bulk notifications (Admin only)"""
    if user_context["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can send bulk notifications"
        )
    return send_bulk_notification(db, bulk_notification)