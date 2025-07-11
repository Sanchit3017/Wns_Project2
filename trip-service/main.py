import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import TripServiceSettings
from models.trip import Trip
from routers.trip_router import router as trip_router
import uvicorn

# Initialize settings
settings = TripServiceSettings()

# Database setup is handled in database.py
from database import engine
from shared.database.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Trip Service for Travel Management System",
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

# Include routers
app.include_router(trip_router, prefix="/api", tags=["trips"])

@app.get("/")
async def root():
    return {"service": "Trip Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)