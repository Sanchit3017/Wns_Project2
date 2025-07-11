from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from shared.database.base import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Reference to auth service user
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    dl_number = Column(String, unique=True, nullable=False)
    vehicle_plate_number = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
    identity_proof_url = Column(String, nullable=True)
    identity_proof_status = Column(String, default="pending")
    service_area = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Driver(id={self.id}, name='{self.name}', dl_number='{self.dl_number}')>"