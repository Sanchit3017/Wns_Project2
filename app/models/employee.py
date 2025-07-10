"""
Employee model for employee-specific information
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Employee(Base):
    """Employee profile model"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    home_location = Column(String, nullable=False)
    commute_schedule = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="employee_profile")
    trips = relationship("Trip", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', employee_id='{self.employee_id}')>"
