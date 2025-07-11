
#!/usr/bin/env python3
"""
Comprehensive test data creation script for the Travel Management System
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
USER_SERVICE_URL = "http://localhost:8002"
TRIP_SERVICE_URL = "http://localhost:8003"

async def create_test_user_and_employee():
    """Create test user and employee data"""
    print("📝 Creating test user and employee...")
    
    # Test user data
    user_data = {
        "email": "employee@test.com",
        "password": "testpass123",
        "role": "employee"
    }
    
    employee_data = {
        "name": "Test Employee",
        "employee_id": "EMP001", 
        "phone_number": "+1234567890",
        "department": "Engineering",
        "location": "Bellandur, Bangalore"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Create auth user
            print("🔐 Creating auth user...")
            auth_response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=user_data)
            
            if auth_response.status_code == 201:
                auth_data = auth_response.json()
                user_id = auth_data["user"]["id"]
                token = auth_data["access_token"]
                print(f"✅ Auth user created with ID: {user_id}")
                
                # Create employee profile
                print("👤 Creating employee profile...")
                headers = {"Authorization": f"Bearer {token}"}
                emp_response = await client.post(
                    f"{USER_SERVICE_URL}/api/users/employee/profile", 
                    json=employee_data,
                    headers=headers
                )
                
                if emp_response.status_code == 201:
                    emp_data = emp_response.json()
                    print(f"✅ Employee created with ID: {emp_data['id']}")
                    return user_id, emp_data['id'], token
                else:
                    print(f"❌ Employee creation failed: {emp_response.status_code} - {emp_response.text}")
            else:
                print(f"❌ Auth user creation failed: {auth_response.status_code} - {auth_response.text}")
                
        except Exception as e:
            print(f"❌ Error creating test user/employee: {e}")
    
    return None, None, None

async def create_test_driver():
    """Create test driver"""
    print("🚗 Creating test driver...")
    
    # Test driver user
    driver_user_data = {
        "email": "driver@test.com",
        "password": "testpass123",
        "role": "driver"
    }
    
    driver_data = {
        "name": "Test Driver",
        "phone_number": "+1234567891",
        "dl_number": "DL123456789",
        "vehicle_plate_number": "KA01AB1234",
        "service_area": "Bellandur, Electronic City, Koramangala"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Create driver auth user
            auth_response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=driver_user_data)
            
            if auth_response.status_code == 201:
                auth_data = auth_response.json()
                driver_user_id = auth_data["user"]["id"]
                driver_token = auth_data["access_token"]
                print(f"✅ Driver auth user created with ID: {driver_user_id}")
                
                # Create driver profile
                headers = {"Authorization": f"Bearer {driver_token}"}
                driver_response = await client.post(
                    f"{USER_SERVICE_URL}/api/users/driver/profile",
                    json=driver_data,
                    headers=headers
                )
                
                if driver_response.status_code == 201:
                    driver_profile = driver_response.json()
                    print(f"✅ Driver created with ID: {driver_profile['id']}")
                    return driver_user_id, driver_profile['id'], driver_token
                else:
                    print(f"❌ Driver creation failed: {driver_response.status_code} - {driver_response.text}")
            else:
                print(f"❌ Driver auth creation failed: {auth_response.status_code} - {auth_response.text}")
                
        except Exception as e:
            print(f"❌ Error creating test driver: {e}")
    
    return None, None, None

async def create_admin_user():
    """Create admin user"""
    print("👑 Creating admin user...")
    
    admin_data = {
        "email": "admin@test.com",
        "password": "adminpass123",
        "role": "admin"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=admin_data)
            
            if auth_response.status_code == 201:
                auth_data = auth_response.json()
                admin_user_id = auth_data["user"]["id"]
                admin_token = auth_data["access_token"]
                print(f"✅ Admin user created with ID: {admin_user_id}")
                return admin_user_id, admin_token
            else:
                print(f"❌ Admin creation failed: {auth_response.status_code} - {auth_response.text}")
                
        except Exception as e:
            print(f"❌ Error creating admin: {e}")
    
    return None, None

async def create_test_trip(employee_id, driver_id, admin_token):
    """Create test trip without vehicle constraints"""
    print("🚌 Creating test trip...")
    
    # Calculate future date
    future_date = datetime.now() + timedelta(hours=24)
    
    trip_data = {
        "pickup_location": "Bellandur",
        "destination": "WNS Global Services",
        "scheduled_time": future_date.isoformat() + "Z",
        "employee_id": employee_id,
        "driver_id": driver_id,
        "notes": "Test trip created by script"
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
        "x-user-id": "1",
        "x-user-role": "admin",
        "x-user-email": "admin@test.com"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            trip_response = await client.post(
                f"{TRIP_SERVICE_URL}/api/trips",
                json=trip_data,
                headers=headers
            )
            
            if trip_response.status_code == 201:
                trip_data = trip_response.json()
                print(f"✅ Trip created with ID: {trip_data['id']}")
                return trip_data['id']
            else:
                print(f"❌ Trip creation failed: {trip_response.status_code} - {trip_response.text}")
                
        except Exception as e:
            print(f"❌ Error creating trip: {e}")
    
    return None

async def main():
    """Main test data creation function"""
    print("=" * 60)
    print("🚀 Creating Comprehensive Test Data")
    print("=" * 60)
    
    # Create admin user
    admin_user_id, admin_token = await create_admin_user()
    if not admin_token:
        print("❌ Cannot proceed without admin user")
        return
    
    # Create employee
    user_id, employee_id, employee_token = await create_test_user_and_employee()
    if not employee_id:
        print("❌ Cannot proceed without employee")
        return
    
    # Create driver
    driver_user_id, driver_id, driver_token = await create_test_driver()
    if not driver_id:
        print("❌ Cannot proceed without driver")
        return
    
    # Create trip
    trip_id = await create_test_trip(employee_id, driver_id, admin_token)
    
    print("\n" + "=" * 60)
    print("📋 TEST DATA SUMMARY")
    print("=" * 60)
    print(f"👑 Admin User ID: {admin_user_id}")
    print(f"👤 Employee ID: {employee_id} (User ID: {user_id})")
    print(f"🚗 Driver ID: {driver_id} (User ID: {driver_user_id})")
    print(f"🚌 Trip ID: {trip_id}")
    print("\n✅ Test data creation completed!")
    
    print("\n📋 READY-TO-USE TRIP CREATION API:")
    print("Endpoint: POST /api/trips")
    print("Headers:")
    print(f'  Authorization: Bearer {admin_token}')
    print('  Content-Type: application/json')
    print('  x-user-id: 1')
    print('  x-user-role: admin')
    print('  x-user-email: admin@test.com')
    print("\nRequest Body:")
    print(f'''{{
  "pickup_location": "Koramangala",
  "destination": "Electronic City", 
  "scheduled_time": "{(datetime.now() + timedelta(hours=2)).isoformat()}Z",
  "employee_id": {employee_id},
  "driver_id": {driver_id},
  "notes": "Another test trip"
}}''')

if __name__ == "__main__":
    asyncio.run(main())
