#!/usr/bin/env python3
"""
Comprehensive test script to demonstrate all microservices APIs working together.
Tests authentication, user management, trip management, and notifications.
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class MicroservicesAPITest:
    def __init__(self):
        self.base_url = "http://localhost:8000"  # API Gateway
        self.auth_token = None
        self.user_data = None
        self.trip_id = None
        self.notification_id = None
        
    async def test_auth_service(self):
        """Test authentication service endpoints"""
        print("\n🔐 Testing Auth Service...")
        
        # Test user registration
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "employee"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/auth/register", json=user_data)
            if response.status_code == 200:
                print("✅ User registration successful")
                self.user_data = response.json()
            else:
                print(f"❌ User registration failed: {response.status_code}")
                return False
            
            # Test user login
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = await client.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ User login successful")
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                return True
            else:
                print(f"❌ User login failed: {response.status_code}")
                return False
    
    async def test_user_service(self):
        """Test user service endpoints"""
        if not self.auth_token:
            print("❌ No auth token available for user service test")
            return False
            
        print("\n👥 Testing User Service...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test creating employee profile
            employee_data = {
                "phone": "+1234567890",
                "home_address": "123 Main St, City, State",
                "emergency_contact": "+0987654321"
            }
            
            response = await client.post(f"{self.base_url}/users/employees", json=employee_data, headers=headers)
            if response.status_code == 200:
                print("✅ Employee profile created successfully")
                return True
            else:
                print(f"❌ Employee profile creation failed: {response.status_code}")
                return False
    
    async def test_trip_service(self):
        """Test trip service endpoints"""
        if not self.auth_token:
            print("❌ No auth token available for trip service test")
            return False
            
        print("\n🚗 Testing Trip Service...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test creating a trip
            trip_data = {
                "pickup_location": "Home",
                "destination": "Office",
                "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "notes": "Regular commute trip"
            }
            
            response = await client.post(f"{self.base_url}/trips", json=trip_data, headers=headers)
            if response.status_code == 200:
                print("✅ Trip created successfully")
                trip_response = response.json()
                self.trip_id = trip_response["id"]
                
                # Test getting trip details
                response = await client.get(f"{self.base_url}/trips/{self.trip_id}", headers=headers)
                if response.status_code == 200:
                    print("✅ Trip details retrieved successfully")
                    return True
                else:
                    print(f"❌ Trip details retrieval failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Trip creation failed: {response.status_code}")
                return False
    
    async def test_notification_service(self):
        """Test notification service endpoints"""
        if not self.auth_token:
            print("❌ No auth token available for notification service test")
            return False
            
        print("\n🔔 Testing Notification Service...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test getting notifications (should be empty initially)
            response = await client.get(f"{self.base_url}/notifications", headers=headers)
            if response.status_code == 200:
                print("✅ Notifications retrieved successfully")
                notifications = response.json()
                print(f"   Found {len(notifications)} notifications")
                
                # Test getting unread count
                response = await client.get(f"{self.base_url}/notifications/unread-count", headers=headers)
                if response.status_code == 200:
                    print("✅ Unread count retrieved successfully")
                    count_data = response.json()
                    print(f"   Unread notifications: {count_data.get('unread_count', 0)}")
                    return True
                else:
                    print(f"❌ Unread count retrieval failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Notifications retrieval failed: {response.status_code}")
                return False
    
    async def test_api_gateway(self):
        """Test API Gateway health and routing"""
        print("\n🌐 Testing API Gateway...")
        
        async with httpx.AsyncClient() as client:
            # Test gateway health
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API Gateway health check passed")
                health_data = response.json()
                print(f"   Gateway status: {health_data.get('status', 'unknown')}")
                
                # Test root endpoint
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    print("✅ API Gateway root endpoint working")
                    return True
                else:
                    print(f"❌ API Gateway root endpoint failed: {response.status_code}")
                    return False
            else:
                print(f"❌ API Gateway health check failed: {response.status_code}")
                return False
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive Microservices API Tests")
        print("=" * 60)
        
        test_results = {}
        
        # Test API Gateway first
        test_results['gateway'] = await self.test_api_gateway()
        
        # Test Auth Service
        test_results['auth'] = await self.test_auth_service()
        
        # Test User Service (requires auth)
        if test_results['auth']:
            test_results['user'] = await self.test_user_service()
        else:
            test_results['user'] = False
            
        # Test Trip Service (requires auth)
        if test_results['auth']:
            test_results['trip'] = await self.test_trip_service()
        else:
            test_results['trip'] = False
            
        # Test Notification Service (requires auth)
        if test_results['auth']:
            test_results['notification'] = await self.test_notification_service()
        else:
            test_results['notification'] = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        print("=" * 60)
        
        for service, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {service.upper()} Service: {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        
        print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All microservices are working perfectly!")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed_tests == total_tests

async def main():
    """Main test function"""
    tester = MicroservicesAPITest()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✨ Microservices architecture is fully functional!")
        print("   All services are communicating properly through the API Gateway.")
        print("   Authentication, user management, trips, and notifications are working.")
    else:
        print("\n💡 Some services may need attention. Check individual test results above.")

if __name__ == "__main__":
    asyncio.run(main())