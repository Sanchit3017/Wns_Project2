from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()

def create_database_engine(database_url: str, echo: bool = False):
    """Create database engine with proper configuration"""
    engine = create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        pool_recycle=300,
        poolclass=StaticPool if "sqlite" in database_url else None
    )
    return engine

def create_session_factory(engine):
    """Create session factory for database operations"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session(session_factory):
    """Database dependency for FastAPI"""
    db = session_factory()
    try:
        yield db
    finally:
        db.close()