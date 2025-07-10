from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Notification(Base):
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seen = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
    recipient = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title='{self.title}', recipient_id={self.recipient_id}, seen={self.seen})>"
