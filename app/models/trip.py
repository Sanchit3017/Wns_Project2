from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


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
    
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
    employee = relationship("Employee", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
    
    def __repr__(self):
        return f"<Trip(id={self.id}, pickup='{self.pickup_location}', destination='{self.destination}', status='{self.status}')>"
