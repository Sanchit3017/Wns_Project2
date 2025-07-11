from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from shared.database.base import Base

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    pickup_location = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, cancelled
    notes = Column(Text, nullable=True)
    
    # References to other services (using IDs instead of foreign keys)
    employee_id = Column(Integer, nullable=False)
    driver_id = Column(Integer, nullable=True)
    vehicle_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Trip(id={self.id}, pickup_location='{self.pickup_location}', destination='{self.destination}', status='{self.status}')>"