"""
Notification router for system communications
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.notification import (
    create_notification, get_user_notifications, mark_notification_as_seen,
    mark_all_notifications_as_seen, get_all_notifications_with_recipients,
    send_bulk_notification, delete_notification, get_unread_count
)
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationWithRecipient,
    BulkNotification
)
from app.core.security import get_current_user_id, get_current_user_role
from typing import List

router = APIRouter()
security = HTTPBearer()


def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user ID and role"""
    user_id = get_current_user_id(credentials.credentials)
    role = get_current_user_role(credentials.credentials)
    return {"user_id": user_id, "role": role}


def verify_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify that the current user is an admin"""
    role = get_current_user_role(credentials.credentials)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return get_current_user_id(credentials.credentials)


@router.post("/", response_model=NotificationResponse)
async def create_new_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    _: int = Depends(verify_admin_role)
):
    """Create a new notification (Admin only)"""
    return create_notification(db, notification_data)


@router.post("/bulk", response_model=List[NotificationResponse])
async def send_bulk_notifications(
    bulk_notification: BulkNotification,
    db: Session = Depends(get_db),
    _: int = Depends(verify_admin_role)
):
    """Send bulk notifications (Admin only)"""
    return send_bulk_notification(db, bulk_notification)


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    include_seen: bool = True,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_info)
):
    """Get notifications for current user"""
    return get_user_notifications(db, user_info["user_id"], include_seen)


@router.get("/all", response_model=List[NotificationWithRecipient])
async def get_all_notifications(
    db: Session = Depends(get_db),
    _: int = Depends(verify_admin_role)
):
    """Get all notifications with recipient information (Admin only)"""
    return get_all_notifications_with_recipients(db)


@router.get("/unread-count")
async def get_unread_notifications_count(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_info)
):
    """Get count of unread notifications"""
    count = get_unread_count(db, user_info["user_id"])
    return {"unread_count": count}


@router.post("/{notification_id}/mark-seen")
async def mark_notification_seen(
    notification_id: int,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_info)
):
    """Mark a notification as seen"""
    success = mark_notification_as_seen(db, user_info["user_id"], notification_id)
    return {"message": "Notification marked as seen", "success": success}


@router.post("/mark-all-seen")
async def mark_all_notifications_seen(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_info)
):
    """Mark all notifications as seen"""
    success = mark_all_notifications_as_seen(db, user_info["user_id"])
    return {"message": "All notifications marked as seen", "success": success}


@router.delete("/{notification_id}")
async def delete_user_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_info)
):
    """Delete a notification"""
    success = delete_notification(db, user_info["user_id"], notification_id)
    return {"message": "Notification deleted successfully", "success": success}
