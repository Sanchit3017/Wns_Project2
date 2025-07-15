#!/usr/bin/env python3
"""
Simple script to create sample trip data for testing trip history
"""
import requests
import json
from datetime import datetime, timedelta

# Service URLs
API_GATEWAY_URL = "http://localhost:8000"
TRIP_SERVICE_URL = "http://localhost:8003"

def create_sample_trips():
    """Create sample trips using the trip service API"""
    print("🚗 Creating Sample Trip Data")
    print("=" * 50)
    
    # Sample trip data
    sample_trips = [
        {
            "pickup_location": "Electronic City",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() - timedelta(days=2)).isoformat() + "Z",
            "employee_id": 1,
            "driver_id": 1,
            "notes": "Regular office commute"
        },
        {
            "pickup_location": "Koramangala",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() - timedelta(days=1)).isoformat() + "Z",
            "employee_id": 2,
            "driver_id": 2,
            "notes": "Airport pickup requested"
        },
        {
            "pickup_location": "HSR Layout",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat() + "Z",
            "employee_id": 3,
            "driver_id": 3,
            "notes": "Client meeting - urgent"
        },
        {
            "pickup_location": "Bellandur",
            "destination": "Kempegowda International Airport",
            "scheduled_time": (datetime.now() - timedelta(days=3)).isoformat() + "Z",
            "employee_id": 4,
            "notes": "Airport transfer"
        },
        {
            "pickup_location": "Marathahalli",
            "destination": "WNS Global Services, Whitefield",
            "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat() + "Z",
            "employee_id": 5,
            "driver_id": 1,
            "notes": "Early morning pickup requested"
        }
    ]
    
    # Headers for authentication
    headers = {
        "Content-Type": "application/json",
        "x-user-id": "1",
        "x-user-role": "admin",
        "x-user-email": "admin@travel.com"
    }
    
    created_trips = []
    
    for i, trip_data in enumerate(sample_trips, 1):
        print(f"\nCreating Trip {i}: {trip_data['pickup_location']} → {trip_data['destination']}")
        
        try:
            # Try API Gateway first
            try:
                response = requests.post(
                    f"{API_GATEWAY_URL}/api/trips/trips",
                    json=trip_data,
                    headers=headers,
                    timeout=5
                )
                print(f"  Gateway response: {response.status_code}")
            except requests.exceptions.ConnectionError:
                # Fall back to direct service
                response = requests.post(
                    f"{TRIP_SERVICE_URL}/trips",
                    json=trip_data,
                    headers=headers,
                    timeout=5
                )
                print(f"  Direct service response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                trip_result = response.json()
                created_trips.append(trip_result)
                print(f"  ✅ Success! Trip ID: {trip_result.get('id')}")
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print(f"\n📊 Summary: Created {len(created_trips)} trips successfully")
    return created_trips

if __name__ == "__main__":
    trips = create_sample_trips()
    
    if trips:
        print("\n✅ Trip creation completed!")
        print("You can now view the trips at: http://localhost:5001/trips/history")
    else:
        print("\n❌ No trips were created. Check if services are running.") 