from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import engine
from app.database.base import Base
from app.database.init_db import init_database
from app.routers import (auth_router, admin_router, driver_router,
                         employee_router, trip_router, notification_router)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME,
              description="City-based Employee Travel Management System",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router,
                   prefix="/api/auth",
                   tags=["Authentication"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])
app.include_router(driver_router.router, prefix="/api/driver", tags=["Driver"])
app.include_router(employee_router.router,
                   prefix="/api/employee",
                   tags=["Employee"])
app.include_router(trip_router.router, prefix="/api/trips", tags=["Trips"])
app.include_router(notification_router.router,
                   prefix="/api/notifications",
                   tags=["Notifications"])


@app.on_event("startup")
async def startup_event():

    init_database()


@app.get("/")
async def root():

    return {"message": "Travel Management System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():

    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True) 
"""This is Sanchit"""
