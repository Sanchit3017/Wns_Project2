from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    message: str


class NotificationCreate(NotificationBase):
    recipient_id: int


class NotificationUpdate(BaseModel):
    seen: bool


class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    seen: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationWithRecipient(BaseModel):
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
    title: str
    message: str
    recipient_role: Optional[str] = None
    recipient_ids: Optional[list[int]] = None