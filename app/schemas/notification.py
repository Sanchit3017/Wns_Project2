"""
Notification schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str
    message: str


class NotificationCreate(NotificationBase):
    """Notification creation schema"""
    recipient_id: int


class NotificationUpdate(BaseModel):
    """Notification update schema"""
    seen: bool


class NotificationResponse(NotificationBase):
    """Notification response schema"""
    id: int
    recipient_id: int
    seen: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationWithRecipient(BaseModel):
    """Notification with recipient information"""
    id: int
    title: str
    message: str
    recipient_id: int
    recipient_email: str
    seen: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkNotification(BaseModel):
    """Bulk notification schema"""
    title: str
    message: str
    recipient_role: Optional[str] = None  # Send to all users of specific role
    recipient_ids: Optional[list[int]] = None  # Send to specific users
