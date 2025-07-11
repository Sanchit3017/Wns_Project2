
#!/usr/bin/env python3
"""
Script to create test employees and drivers for testing trip creation
"""

import requests
import json
from datetime import datetime

# Service URLs (adjust if different)
AUTH_SERVICE_URL = "http://localhost:8001/api"
USER_SERVICE_URL = "http://localhost:8002/api"
TRIP_SERVICE_URL = "http://localhost:8003/api"

def create_test_employee():
    """Create a test employee"""
    print("📝 Creating test employee...")
    
    # Create auth user first
    auth_data = {
        "email": "testemployee@company.com",
        "password": "employee123",
        "role": "employee"
    }
    
    try:
        # Register user in auth service
        auth_response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            json=auth_data,
            headers={"Content-Type": "application/json"}
        )
        
        if auth_response.status_code == 201:
            auth_result = auth_response.json()
            user_id = auth_result["user"]["id"]
            print(f"✅ Auth user created with ID: {user_id}")
            
            # Create employee profile
            employee_data = {
                "name": "John Employee",
                "employee_id": "EMP001",
                "phone_number": "+91-9876543210",
                "home_location": "Bellandur, Bangalore",
                "commute_schedule": "9:00 AM - 6:00 PM"
            }
            
            # Headers for user service
            headers = {
                "Content-Type": "application/json",
                "x-user-id": str(user_id),
                "x-user-role": "employee",
                "x-user-email": auth_data["email"]
            }
            
            employee_response = requests.post(
                f"{USER_SERVICE_URL}/users/employees",
                json=employee_data,
                headers=headers
            )
            
            if employee_response.status_code in [200, 201]:
                employee_result = employee_response.json()
                print(f"✅ Employee created with ID: {employee_result['id']}")
                return {
                    "user_id": user_id,
                    "employee_id": employee_result['id'],
                    "auth_data": auth_data
                }
            else:
                print(f"❌ Employee creation failed: {employee_response.status_code}")
                print(f"Response: {employee_response.text}")
                
        else:
            print(f"❌ Auth user creation failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to services. Make sure they are running.")
        
    return None

def create_test_driver():
    """Create a test driver"""
    print("🚗 Creating test driver...")
    
    # Create auth user first
    auth_data = {
        "email": "testdriver@company.com", 
        "password": "driver123",
        "role": "driver"
    }
    
    try:
        # Register user in auth service
        auth_response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            json=auth_data,
            headers={"Content-Type": "application/json"}
        )
        
        if auth_response.status_code == 201:
            auth_result = auth_response.json()
            user_id = auth_result["user"]["id"]
            print(f"✅ Auth user created with ID: {user_id}")
            
            # Create driver profile
            driver_data = {
                "name": "Mike Driver",
                "phone_number": "+91-9876543211",
                "dl_number": "KA05-DL-123456",
                "vehicle_plate_number": "KA05-AB-1234",
                "service_area": "Bellandur, Electronic City, Koramangala"
            }
            
            # Headers for user service
            headers = {
                "Content-Type": "application/json",
                "x-user-id": str(user_id),
                "x-user-role": "driver", 
                "x-user-email": auth_data["email"]
            }
            
            driver_response = requests.post(
                f"{USER_SERVICE_URL}/users/drivers",
                json=driver_data,
                headers=headers
            )
            
            if driver_response.status_code in [200, 201]:
                driver_result = driver_response.json()
                print(f"✅ Driver created with ID: {driver_result['id']}")
                return {
                    "user_id": user_id,
                    "driver_id": driver_result['id'],
                    "auth_data": auth_data
                }
            else:
                print(f"❌ Driver creation failed: {driver_response.status_code}")
                print(f"Response: {driver_response.text}")
                
        else:
            print(f"❌ Auth user creation failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to services. Make sure they are running.")
        
    return None

def test_trip_creation(employee_data, driver_data):
    """Test creating a trip with the created employee and driver"""
    print("🎯 Testing trip creation...")
    
    # Login as admin first
    admin_login = {
        "email": "admin@travel.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=admin_login,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            # Create trip with actual IDs
            trip_data = {
                "pickup_location": "Bellandur",
                "destination": "Electronic City",
                "scheduled_time": "2025-07-12T09:30:00.000Z",
                "employee_id": employee_data["employee_id"],
                "driver_id": driver_data["driver_id"],
                "notes": "Test trip with valid employee and driver IDs"
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-user-id": "1",
                "x-user-role": "admin",
                "x-user-email": "admin@travel.com"
            }
            
            trip_response = requests.post(
                f"{TRIP_SERVICE_URL}/trips",
                json=trip_data,
                headers=headers
            )
            
            if trip_response.status_code in [200, 201]:
                trip_result = trip_response.json()
                print(f"✅ Trip created successfully!")
                print(f"   Trip ID: {trip_result['id']}")
                print(f"   Employee ID: {trip_result['employee_id']}")
                print(f"   Driver ID: {trip_result['driver_id']}")
                return trip_result
            else:
                print(f"❌ Trip creation failed: {trip_response.status_code}")
                print(f"Response: {trip_response.text}")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to services.")
        
    return None

def main():
    """Main function"""
    print("🚀 Creating Test Data for Trip Management System")
    print("=" * 60)
    
    # Create test employee
    employee_data = create_test_employee()
    if not employee_data:
        print("❌ Failed to create test employee")
        return
    
    print()
    
    # Create test driver
    driver_data = create_test_driver()
    if not driver_data:
        print("❌ Failed to create test driver")
        return
        
    print()
    
    # Test trip creation
    trip_result = test_trip_creation(employee_data, driver_data)
    
    if trip_result:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! All test data created successfully!")
        print("=" * 60)
        print("\n📋 SUMMARY:")
        print(f"Employee ID: {employee_data['employee_id']} (User ID: {employee_data['user_id']})")
        print(f"Driver ID: {driver_data['driver_id']} (User ID: {driver_data['user_id']})")
        print(f"Trip ID: {trip_result['id']}")
        
        print("\n🎯 USE THESE IDs FOR FUTURE TRIP CREATION:")
        print(json.dumps({
            "pickup_location": "Your Location",
            "destination": "Your Destination", 
            "scheduled_time": "2025-07-12T10:00:00.000Z",
            "employee_id": employee_data['employee_id'],
            "driver_id": driver_data['driver_id'],
            "notes": "Your trip notes"
        }, indent=2))
        
    else:
        print("\n❌ Failed to create complete test data")

if __name__ == "__main__":
    main()
