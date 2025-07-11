from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Driver(Base):

    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,
                     ForeignKey("users.id"),
                     unique=True,
                     nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    dl_number = Column(String, unique=True, nullable=False)
    vehicle_plate_number = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
    identity_proof_url = Column(String, nullable=True)  # PDF or image URL for identity verification
    identity_proof_status = Column(String, default="pending")  # pending, approved, rejected
    service_area = Column(String, nullable=True)  # Area/location where driver operates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="driver_profile")
    trips = relationship("Trip", back_populates="driver")
    vehicles = relationship("Vehicle", back_populates="driver")

    def __repr__(self):
        return f"<Driver(id={self.id}, name='{self.name}', dl_number='{self.dl_number}')>"
