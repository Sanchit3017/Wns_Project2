"""Database configuration for Trip Service"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from shared.config import TripServiceSettings
from shared.database.base import create_database_engine, create_session_factory, Base


settings = TripServiceSettings()


engine = create_database_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = create_session_factory(engine)

def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)