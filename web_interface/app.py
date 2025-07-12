#!/usr/bin/env python3
"""
Interactive Web Interface for WNS Bangalore Transport Management
Enhanced with real-time tracking, zone visualization, and client presentation features
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import httpx
import json
from datetime import datetime, timedelta
import asyncio

# Import our enhanced features
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_features import BangaloreTransportEnhancer, RealTimeTracker, get_dashboard_data, BANGALORE_ZONES, WNS_OFFICE

app = FastAPI(title="WNS Bangalore Transport Management", version="2.0.0")

# Templates and static files
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize enhanced features
enhancer = BangaloreTransportEnhancer()
tracker = RealTimeTracker()

# Pydantic models
class TripRequest(BaseModel):
    pickup_location: str
    destination: str = "WNS Vuram, Whitefield"
    employee_id: int
    scheduled_time: str
    notes: Optional[str] = None

class TrackingUpdate(BaseModel):
    trip_id: int
    location: Dict[str, float]
    status: str
    eta_minutes: int

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard with enhanced Bangalore transport features"""
    dashboard_data = get_dashboard_data()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "dashboard_data": dashboard_data,
        "zones": BANGALORE_ZONES,
        "office": WNS_OFFICE
    })

@app.get("/api/zones")
async def get_zones():
    """Get Bangalore transport zones"""
    return {
        "zones": BANGALORE_ZONES,
        "office_location": WNS_OFFICE,
        "total_coverage": sum(len(data["areas"]) for data in BANGALORE_ZONES.values() if "areas" in data)
    }

@app.post("/api/trips/enhanced")
async def create_enhanced_trip(trip_request: TripRequest):
    """Create trip with enhanced Bangalore-specific features"""
    trip_data = trip_request.dict()
    
    try:
        # Use our enhanced trip creation
        enhanced_trip = await enhancer.create_enhanced_trip(trip_data)
        
        # Also try to create in the actual system
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "http://localhost:8000/api/trips/trips",
                    json=trip_data,
                    headers={
                        "x-user-id": "1",
                        "x-user-role": "admin", 
                        "x-user-email": "admin@travel.com"
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    actual_trip = response.json()
                    enhanced_trip["system_trip_id"] = actual_trip.get("id")
            except:
                enhanced_trip["system_integration"] = "offline_mode"
        
        return enhanced_trip
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create enhanced trip: {str(e)}")

@app.get("/api/trips/{trip_id}/tracking")
async def get_trip_tracking(trip_id: int):
    """Get real-time tracking for a trip"""
    tracking_data = await tracker.get_live_updates(trip_id)
    return tracking_data

@app.post("/api/trips/{trip_id}/start-tracking")
async def start_trip_tracking(trip_id: int):
    """Start real-time tracking for a trip"""
    tracking_data = await tracker.start_trip_tracking(trip_id)
    return tracking_data

@app.get("/api/drivers/optimal")
async def get_optimal_drivers(location: str, shift_time: str = "09:00"):
    """Get optimal driver assignment for a location"""
    assignment = await enhancer.get_optimal_driver_assignment(location, shift_time)
    return assignment

@app.get("/api/eta/calculate")
async def calculate_eta(pickup_location: str, shift_time: str = "09:00"):
    """Calculate ETA for pickup"""
    # Mock coordinates for demo
    pickup_coords = {"lat": 12.9716, "lng": 77.5946}
    eta_info = enhancer.calculate_eta(pickup_location, pickup_coords, shift_time)
    return eta_info

@app.get("/zones", response_class=HTMLResponse)
async def zones_page(request: Request):
    """Interactive zones visualization page"""
    return templates.TemplateResponse("zones.html", {
        "request": request,
        "zones": BANGALORE_ZONES,
        "office": WNS_OFFICE
    })

@app.get("/tracking", response_class=HTMLResponse)
async def tracking_page(request: Request):
    """Real-time tracking page"""
    return templates.TemplateResponse("tracking.html", {
        "request": request,
        "office": WNS_OFFICE
    })

@app.get("/trips/create", response_class=HTMLResponse)
async def create_trip_page(request: Request):
    """Enhanced trip creation page"""
    return templates.TemplateResponse("create_trip.html", {
        "request": request,
        "zones": BANGALORE_ZONES,
        "office": WNS_OFFICE
    })

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    # Mock some real-time data for demonstration
    current_time = datetime.now()
    
    stats = {
        "active_trips": 12,
        "available_drivers": 8,
        "zones_covered": len([z for z in BANGALORE_ZONES.keys() if z != "Non_Hiring"]),
        "average_eta": "25 minutes",
        "traffic_status": enhancer.get_traffic_description(enhancer.get_traffic_factor(current_time.hour)),
        "last_updated": current_time.isoformat(),
        "zone_activity": {
            "East": {"trips": 5, "drivers": 3},
            "West": {"trips": 3, "drivers": 2}, 
            "North": {"trips": 2, "drivers": 1},
            "South": {"trips": 2, "drivers": 2},
            "Central": {"trips": 0, "drivers": 0}
        }
    }
    
    return stats

@app.get("/api/policy/bangalore")
async def get_bangalore_policy():
    """Get Bangalore-specific transport policy details"""
    from enhanced_features import BANGALORE_TRANSPORT_TIMINGS, TRAVEL_TIME_MATRIX
    
    return {
        "location": "Bangalore",
        "office": WNS_OFFICE,
        "transport_timings": BANGALORE_TRANSPORT_TIMINGS,
        "travel_time_matrix": TRAVEL_TIME_MATRIX,
        "zones": BANGALORE_ZONES,
        "policy_highlights": [
            "Sociable hours: 06:30 - 20:30 for all employees",
            "15 minutes buffer before login time",
            "20 minutes buffer after logout time", 
            "Zone-based driver assignment",
            "Traffic-aware ETA calculations",
            "Coverage up to 30km from Whitefield office"
        ]
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{trip_id}")
async def websocket_endpoint(websocket, trip_id: int):
    """WebSocket for real-time trip updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send live updates every 5 seconds
            tracking_data = await tracker.get_live_updates(trip_id)
            await websocket.send_json(tracking_data)
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)