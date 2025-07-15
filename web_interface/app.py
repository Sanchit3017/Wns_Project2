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

# Get service URLs from environment or default to service names
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
TRIP_SERVICE_URL = os.getenv("TRIP_SERVICE_URL", "http://trip-service:8003")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")

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

# Authentication models
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str

# Authentication template routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

# Authentication API routes
@app.post("/api/auth/login")
async def login_api(login_data: LoginRequest):
    """Login API - proxy to auth service with enhanced employee info"""
    auth_url = f"{AUTH_SERVICE_URL}/auth/login"
    try:
        print(f"Attempting to connect to auth service at: {auth_url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_url,
                json={"email": login_data.email, "password": login_data.password},
                timeout=10.0
            )
            
            print(f"Auth service response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                
                # If user is an employee, fetch employee details from user service
                if auth_data.get("user", {}).get("role") == "employee":
                    try:
                        # Search for employee by email in user service
                        emp_response = await client.get(
                            f"{USER_SERVICE_URL}/users/employees",
                            timeout=5.0
                        )
                        if emp_response.status_code == 200:
                            employees_data = emp_response.json()
                            
                            # Find employee by email (we need to get user info first)
                            user_response = await client.get(
                                f"{AUTH_SERVICE_URL}/auth/users/{auth_data['user']['id']}",
                                timeout=5.0
                            )
                            if user_response.status_code == 200:
                                user_info = user_response.json()
                                user_email = user_info.get("email")
                                
                                # Find matching employee
                                for emp in employees_data:
                                    # We need to match by user_id since employee table has user_id
                                    if emp.get("user_id") == auth_data["user"]["id"]:
                                        # Add employee info to user data
                                        auth_data["user"]["employee_id"] = emp.get("employee_id")
                                        auth_data["user"]["employee_name"] = emp.get("name")
                                        auth_data["user"]["phone_number"] = emp.get("phone_number")
                                        auth_data["user"]["home_location"] = emp.get("home_location")
                                        break
                    except Exception as e:
                        print(f"Error fetching employee details: {e}")
                        # Continue without employee details if there's an error
                
                return auth_data
            else:
                error_data = response.json()
                print(f"Auth service error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Authentication failed")
                )
    except httpx.TimeoutException:
        print(f"Timeout connecting to auth service at {auth_url}")
        raise HTTPException(status_code=503, detail="Authentication service timeout")
    except httpx.RequestError as e:
        print(f"Request error connecting to auth service: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=503, detail="Authentication service error")

@app.post("/api/auth/register")
async def register_api(signup_data: SignupRequest):
    """Register API - proxy to auth service"""
    auth_url = f"{AUTH_SERVICE_URL}/auth/register"
    try:
        print(f"Attempting to register at auth service: {auth_url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_url,
                json={
                    "email": signup_data.email, 
                    "password": signup_data.password,
                    "role": signup_data.role
                },
                timeout=10.0
            )
            
            print(f"Auth service register response status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                print(f"Auth service register error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Registration failed")
                )
    except httpx.TimeoutException:
        print(f"Timeout connecting to auth service at {auth_url}")
        raise HTTPException(status_code=503, detail="Authentication service timeout")
    except httpx.RequestError as e:
        print(f"Request error connecting to auth service: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=503, detail="Authentication service error")

@app.get("/api/debug/auth-service")
async def debug_auth_service():
    """Debug endpoint to test auth service connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/health", timeout=5.0)
            return {
                "status": "connected",
                "auth_service_url": AUTH_SERVICE_URL,
                "auth_service_status": response.status_code,
                "auth_service_response": response.json()
            }
    except httpx.RequestError as e:
        return {
            "status": "connection_error",
            "auth_service_url": AUTH_SERVICE_URL,
            "error": str(e),
            "message": "Cannot connect to auth service"
        }
    except Exception as e:
        return {
            "status": "error",
            "auth_service_url": AUTH_SERVICE_URL,
            "error": str(e)
        }

@app.post("/api/auth/logout")
async def logout_api():
    """Logout API"""
    return {"message": "Successfully logged out"}

# Role-based dashboard routes
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard with comprehensive management features"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request
    })

@app.get("/driver/dashboard", response_class=HTMLResponse) 
async def driver_dashboard(request: Request):
    """Driver dashboard - placeholder"""
    return templates.TemplateResponse("base.html", {
        "request": request,
        "title": "Driver Dashboard",
        "message": "Driver Dashboard - Coming Soon!"
    })

@app.get("/employee/dashboard", response_class=HTMLResponse)
async def employee_dashboard(request: Request):
    """Employee dashboard"""
    return templates.TemplateResponse("employee_dashboard.html", {
        "request": request
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})

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
                    f"{API_GATEWAY_URL}/api/trips/trips",
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

@app.get("/trips/history", response_class=HTMLResponse)
async def trips_history_page(request: Request):
    """Trip history page"""
    return templates.TemplateResponse("trips_history.html", {
        "request": request
    })

@app.get("/trips/{trip_id}", response_class=HTMLResponse)
async def trip_details_page(request: Request, trip_id: int):
    """Trip details page"""
    return templates.TemplateResponse("trip_details.html", {
        "request": request,
        "trip_id": trip_id,
        "office": WNS_OFFICE
    })

@app.get("/api/trips/history")
async def get_trips_history(
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    status: Optional[str] = None
):
    """API endpoint to fetch trip history based on user role and filters"""
    print("=== DEBUG: get_trips_history function called! ===")
    print(f"Trips history called with role={role}, user_id={user_id}, status={status}")
    trips = generate_sample_trip_data(role, user_id, status)
    analytics = {
        "total_trips": len(trips),
        "completed_trips": len([t for t in trips if t.get("status") == "completed"]),
        "pending_trips": len([t for t in trips if t.get("status") in ["pending", "scheduled"]]),
        "cancelled_trips": len([t for t in trips if t.get("status") == "cancelled"]),
        "in_progress_trips": len([t for t in trips if t.get("status") == "in_progress"])
    } if role == "admin" else None
    
    result = {"trips": trips, "role": role or "employee"}
    if analytics:
        result["analytics"] = analytics
    
    return result

def generate_sample_trip_data(role=None, user_id=None, status=None):
    """Generate sample trip data for demonstration"""
    from datetime import datetime, timedelta
    import random
    
    sample_trips = [
        {
            "id": 1,
            "pickup_location": "Electronic City",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() - timedelta(days=2)).isoformat(),
            "actual_start_time": (datetime.now() - timedelta(days=2, hours=-1)).isoformat(),
            "actual_end_time": (datetime.now() - timedelta(days=2, hours=-2)).isoformat(),
            "status": "completed",
            "employee_id": 1,
            "driver_id": 1,
            "employee_name": "John Employee",
            "driver_name": "Ravi Kumar",
            "notes": "Regular office commute"
        },
        {
            "id": 2,
            "pickup_location": "Koramangala",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "actual_start_time": (datetime.now() - timedelta(days=1, hours=-1)).isoformat(),
            "status": "in_progress",
            "employee_id": 2,
            "driver_id": 2,
            "employee_name": "Jane Smith",
            "driver_name": "Suresh Reddy",
            "notes": "Airport pickup requested"
        },
        {
            "id": 3,
            "pickup_location": "HSR Layout",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "status": "scheduled",
            "employee_id": 3,
            "driver_id": 3,
            "employee_name": "Mike Johnson",
            "driver_name": "Amit Sharma",
            "notes": "Client meeting - urgent"
        },
        {
            "id": 4,
            "pickup_location": "Bellandur",
            "destination": "Kempegowda International Airport",
            "scheduled_time": (datetime.now() - timedelta(days=3)).isoformat(),
            "status": "cancelled",
            "employee_id": 4,
            "driver_id": None,
            "employee_name": "Sarah Wilson",
            "driver_name": None,
            "notes": "Trip cancelled due to flight delay"
        },
        {
            "id": 5,
            "pickup_location": "Marathahalli",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "scheduled",
            "employee_id": 5,
            "driver_id": 1,
            "employee_name": "David Brown",
            "driver_name": "Ravi Kumar",
            "notes": "Early morning pickup requested"
        }
    ]
    
    # Filter by status if specified
    if status and status != "all":
        sample_trips = [trip for trip in sample_trips if trip["status"] == status]
    
    # Filter by user if not admin
    if role != "admin" and user_id:
        if role == "driver":
            sample_trips = [trip for trip in sample_trips if trip.get("driver_id") == user_id]
        else:  # employee
            sample_trips = [trip for trip in sample_trips if trip.get("employee_id") == user_id]
    
    return sample_trips

@app.get("/api/trips/{trip_id}")
async def get_trip_details(trip_id: int, request: Request):
    """API endpoint to fetch detailed trip information"""
    try:
        # Get user context from headers (set by frontend)
        user_id = request.headers.get("x-user-id", "1")
        user_role = request.headers.get("x-user-role", "employee")
        user_email = request.headers.get("x-user-email", "user@travel.com")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "x-user-id": user_id,
                "x-user-role": user_role,
                "x-user-email": user_email
            }
            
            # Fetch trip details from trip service
            response = await client.get(
                f"{API_GATEWAY_URL}/api/trips/trips/{trip_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                trip_data = response.json()
                return trip_data
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Trip not found")
            else:
                # Return sample data if service unavailable
                return {
                    "id": trip_id,
                    "pickup_location": "Electronic City",
                    "destination": "WNS Vuram, Whitefield",
                    "scheduled_time": "2024-01-15T09:00:00",
                    "status": "in_progress",
                    "employee_name": "John Doe",
                    "employee_id": "EMP001",
                    "driver_name": "Ravi Kumar",
                    "driver_contact": "+91 9876543210",
                    "vehicle_plate_number": "KA 01 AB 1234",
                    "vehicle_type": "Sedan",
                    "notes": "Please call before arrival",
                    "created_at": "2024-01-15T08:30:00",
                    "actual_start_time": "2024-01-15T09:05:00"
                }
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching trip details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

@app.get("/api/admin/dashboard/kpis")
async def get_admin_kpis():
    """Get KPI data for admin dashboard"""
    try:
        # Try to get real data from services
        async with httpx.AsyncClient() as client:
            try:
                # Get trip data
                trips_response = await client.get(f"{API_GATEWAY_URL}/api/trips", timeout=5)
                active_trips = 0
                if trips_response.status_code == 200:
                    trips_data = trips_response.json()
                    active_trips = len([t for t in trips_data if t.get('status') == 'active'])
                
                # Get user data
                users_response = await client.get(f"{USER_SERVICE_URL}/api/users/count", timeout=5)
                total_users = 0
                if users_response.status_code == 200:
                    users_data = users_response.json()
                    total_users = users_data.get('total', 0)
                
                return {
                    "active_trips": active_trips,
                    "total_users": total_users,
                    "available_drivers": 8,  # Default value
                    "coverage_zones": 12
                }
            except:
                # Return default values if services are unavailable
                return {
                    "active_trips": 5,
                    "total_users": 150,
                    "available_drivers": 8,
                    "coverage_zones": 12
                }
    except Exception as e:
        return {
            "error": f"KPI service error: {str(e)}",
            "active_trips": 0,
            "total_users": 0,
            "available_drivers": 0,
            "coverage_zones": 12
        }

@app.get("/api/admin/trips/recent")
async def get_recent_trips():
    """Get recent trips for admin dashboard"""
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_GATEWAY_URL}/api/trips?limit=10", timeout=5)
                if response.status_code == 200:
                    trips = response.json()
                    return trips
                else:
                    # Return sample data if service unavailable
                    return [
                        {
                            "id": 1,
                            "employee_name": "John Doe",
                            "pickup_location": "Whitefield",
                            "status": "completed"
                        },
                        {
                            "id": 2,
                            "employee_name": "Jane Smith",
                            "pickup_location": "Marathahalli",
                            "status": "in-progress"
                        }
                    ]
            except:
                # Return sample data if service unavailable
                return [
                    {
                        "id": 1,
                        "employee_name": "John Doe",
                        "pickup_location": "Whitefield",
                        "status": "completed"
                    },
                    {
                        "id": 2,
                        "employee_name": "Jane Smith",
                        "pickup_location": "Marathahalli",
                        "status": "in-progress"
                    }
                ]
    except Exception as e:
        return []

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

@app.get("/api/employees/search")
async def search_employees(q: str = ""):
    """Search employees by name or employee ID"""
    try:
        if len(q) < 2:  # Minimum 2 characters for search
            return {"employees": []}
        
        # Try to get employees from user service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/users/employees", timeout=5)
                if response.status_code == 200:
                    employees_data = response.json()
                    
                    # Filter employees based on search query
                    filtered_employees = []
                    q_lower = q.lower()
                    
                    for emp in employees_data:
                        name_match = q_lower in emp.get('name', '').lower()
                        id_match = q in str(emp.get('employee_id', ''))
                        
                        if name_match or id_match:
                            filtered_employees.append({
                                "id": emp.get('id'),
                                "name": emp.get('name'),
                                "employee_id": emp.get('employee_id'),
                                "phone_number": emp.get('phone_number'),
                                "home_location": emp.get('home_location')
                            })
                    
                    return {"employees": filtered_employees[:10]}  # Limit to 10 results
                    
            except Exception as e:
                print(f"Error searching employees: {e}")
        
        # Fallback data for testing
        fallback_employees = [
            {"id": 1, "name": "John Employee", "employee_id": "EMP001", "phone_number": "+91-9876543210", "home_location": "Bellandur"},
            {"id": 2, "name": "Jane Smith", "employee_id": "EMP002", "phone_number": "+91-9876543211", "home_location": "Whitefield"},
            {"id": 3, "name": "Mike Johnson", "employee_id": "EMP003", "phone_number": "+91-9876543212", "home_location": "Electronic City"},
            {"id": 4, "name": "Sarah Wilson", "employee_id": "EMP004", "phone_number": "+91-9876543213", "home_location": "Koramangala"},
            {"id": 5, "name": "David Brown", "employee_id": "EMP005", "phone_number": "+91-9876543214", "home_location": "Indiranagar"}
        ]
        
        # Filter fallback data
        q_lower = q.lower()
        filtered = [
            emp for emp in fallback_employees 
            if q_lower in emp['name'].lower() or q in emp['employee_id']
        ]
        
        return {"employees": filtered[:10]}
        
    except Exception as e:
        return {"error": str(e), "employees": []}

@app.get("/api/employees/{employee_id}")
async def get_employee_by_id(employee_id: str):
    """Get employee details by employee ID"""
    try:
        # Try to get employee from user service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/users/employees", timeout=5)
                if response.status_code == 200:
                    employees_data = response.json()
                    
                    # Find employee by employee_id
                    for emp in employees_data:
                        if str(emp.get('employee_id')) == str(employee_id):
                            return {
                                "employee": {
                                    "id": emp.get('id'),
                                    "name": emp.get('name'),
                                    "employee_id": emp.get('employee_id'),
                                    "phone_number": emp.get('phone_number'),
                                    "home_location": emp.get('home_location')
                                }
                            }
                    
                    return {"error": "Employee not found", "employee": None}
                    
            except Exception as e:
                print(f"Error fetching employee: {e}")
        
        # Fallback data for testing
        fallback_employees = {
            "EMP001": {"id": 1, "name": "John Employee", "employee_id": "EMP001", "phone_number": "+91-9876543210", "home_location": "Bellandur"},
            "EMP002": {"id": 2, "name": "Jane Smith", "employee_id": "EMP002", "phone_number": "+91-9876543211", "home_location": "Whitefield"},
            "EMP003": {"id": 3, "name": "Mike Johnson", "employee_id": "EMP003", "phone_number": "+91-9876543212", "home_location": "Electronic City"},
            "EMP004": {"id": 4, "name": "Sarah Wilson", "employee_id": "EMP004", "phone_number": "+91-9876543213", "home_location": "Koramangala"},
            "EMP005": {"id": 5, "name": "David Brown", "employee_id": "EMP005", "phone_number": "+91-9876543214", "home_location": "Indiranagar"}
        }
        
        if employee_id in fallback_employees:
            return {"employee": fallback_employees[employee_id]}
        else:
            return {"error": "Employee not found", "employee": None}
        
    except Exception as e:
        return {"error": str(e), "employee": None}

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