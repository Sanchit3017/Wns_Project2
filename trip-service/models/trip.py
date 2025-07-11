from sqlalchemy import Column, Integer, String, DateTime, Text
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
    status = Column(String, default="scheduled")
    notes = Column(Text, nullable=True)
    
    # References to other services (no foreign keys in microservices)
    employee_id = Column(Integer, nullable=False)  # Reference to user service
    driver_id = Column(Integer, nullable=True)     # Reference to user service
    vehicle_id = Column(Integer, nullable=True)    # Reference to user service
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Trip(id={self.id}, pickup='{self.pickup_location}', destination='{self.destination}', status='{self.status}')>"