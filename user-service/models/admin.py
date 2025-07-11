from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from shared.database.base import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)  # Reference to auth service user
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    department = Column(String, nullable=False)
    access_level = Column(String, default="admin")  # admin, super_admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Admin(id={self.id}, name='{self.name}', employee_id='{self.employee_id}', department='{self.department}')>"