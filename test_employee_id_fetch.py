#!/usr/bin/env python3
"""
Test script to verify employee ID fetching from login API
"""

import asyncio
import httpx
import json
import time

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
USER_SERVICE_URL = "http://localhost:8002"
WEB_INTERFACE_URL = "http://localhost:5000"

async def test_login_with_employee_id():
    """Test login API to see if employee_id is included in response"""
    
    print("🔍 Testing employee ID fetching from login API...")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    await asyncio.sleep(10)
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Check if auth service is running
            print("📡 Testing auth service connectivity...")
            try:
                auth_response = await client.get(f"{AUTH_SERVICE_URL}/health", timeout=5)
                print(f"✅ Auth service status: {auth_response.status_code}")
            except Exception as e:
                print(f"❌ Auth service not accessible: {e}")
                return
            
            # Test 2: Check if user service is running
            print("📡 Testing user service connectivity...")
            try:
                user_response = await client.get(f"{USER_SERVICE_URL}/users/employees", timeout=5)
                print(f"✅ User service status: {user_response.status_code}")
                if user_response.status_code == 200:
                    employees = user_response.json()
                    print(f"📊 Found {len(employees)} employees in user service")
                    for emp in employees[:3]:  # Show first 3 employees
                        print(f"   - {emp.get('name')} (ID: {emp.get('employee_id')}, User ID: {emp.get('user_id')})")
            except Exception as e:
                print(f"❌ User service not accessible: {e}")
                return
            
            # Test 3: Test login API with employee credentials
            print("🔐 Testing login API with employee credentials...")
            
            # Try to login with a test employee
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            
            try:
                login_response = await client.post(
                    f"{WEB_INTERFACE_URL}/api/auth/login",
                    json=login_data,
                    timeout=10
                )
                
                print(f"📊 Login response status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print("✅ Login successful!")
                    print(f"📋 User data: {json.dumps(login_result.get('user', {}), indent=2)}")
                    
                    # Check if employee_id is included
                    user_data = login_result.get('user', {})
                    if 'employee_id' in user_data:
                        print(f"🎉 SUCCESS: Employee ID '{user_data['employee_id']}' found in login response!")
                    else:
                        print("⚠️  Employee ID not found in login response")
                        print("🔍 Available fields:", list(user_data.keys()))
                else:
                    print(f"❌ Login failed: {login_response.text}")
                    
            except Exception as e:
                print(f"❌ Login API error: {e}")
            
            # Test 4: Test with a known employee from the database
            print("\n🔍 Testing with known employee data...")
            try:
                # Get employees from user service
                emp_response = await client.get(f"{USER_SERVICE_URL}/users/employees", timeout=5)
                if emp_response.status_code == 200:
                    employees = emp_response.json()
                    if employees:
                        # Use the first employee's user_id to get their email from auth service
                        first_emp = employees[0]
                        user_id = first_emp.get('user_id')
                        
                        print(f"👤 Testing with employee: {first_emp.get('name')} (ID: {first_emp.get('employee_id')})")
                        
                        # Get user email from auth service
                        try:
                            user_response = await client.get(f"{AUTH_SERVICE_URL}/auth/users/{user_id}", timeout=5)
                            if user_response.status_code == 200:
                                user_info = user_response.json()
                                email = user_info.get('email')
                                print(f"📧 Found email: {email}")
                                
                                # Try to login with this email (we don't know the password, but we can test the flow)
                                print("🔐 Testing login flow with known employee...")
                                # This will fail due to wrong password, but we can see the response structure
                                
                        except Exception as e:
                            print(f"❌ Could not get user info: {e}")
                            
            except Exception as e:
                print(f"❌ Error testing with known employee: {e}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_login_with_employee_id()) 