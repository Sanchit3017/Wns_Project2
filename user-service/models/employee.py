from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from shared.database.base import Base


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Reference to auth service user
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    home_location = Column(String, nullable=False)
    commute_schedule = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', employee_id='{self.employee_id}')>"