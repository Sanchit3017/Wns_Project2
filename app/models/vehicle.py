"""
Vehicle model for fleet management
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Vehicle(Base):
    """Vehicle model for fleet management"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    vehicle_type = Column(String, nullable=False)  # sedan, suv, van, etc.
    capacity = Column(Integer, nullable=False)
    is_available = Column(String, default=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    driver = relationship("Driver", back_populates="vehicles")
    trips = relationship("Trip", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, plate_number='{self.plate_number}', type='{self.vehicle_type}')>"
