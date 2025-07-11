import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from shared.config import AuthServiceSettings
from shared.database.base import create_database_engine, create_session_factory, Base
from routers.auth_router import router as auth_router
from models.user import User
import uvicorn

# Initialize settings
settings = AuthServiceSettings()

# Create database engine and session factory
engine = create_database_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = create_session_factory(engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Authentication Service for Travel Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers (with dependency override)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Override the get_db dependency after including the router
from routers.auth_router import get_db as router_get_db
app.dependency_overrides[router_get_db] = get_db

@app.get("/")
async def root():
    return {"service": "Auth Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)