#!/usr/bin/env python3
"""
Test script to verify microservices are working correctly
"""

import asyncio
import httpx
import json

async def test_microservices():
    """Test microservices functionality"""
    print("Testing Travel Management Microservices")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test API Gateway
        try:
            response = await client.get("http://localhost:8000/")
            print(f"✅ API Gateway: {response.status_code} - {response.json()['service']}")
        except Exception as e:
            print(f"❌ API Gateway: Error - {e}")
        
        # Test Auth Service
        try:
            response = await client.get("http://localhost:8001/health")
            print(f"✅ Auth Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Auth Service: Error - {e}")
        
        # Test User Service
        try:
            response = await client.get("http://localhost:8002/health")
            print(f"✅ User Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ User Service: Error - {e}")
        
        # Test Trip Service
        try:
            response = await client.get("http://localhost:8003/health")
            print(f"✅ Trip Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Trip Service: Error - {e}")
        
        # Test Notification Service
        try:
            response = await client.get("http://localhost:8004/health")
            print(f"✅ Notification Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Notification Service: Error - {e}")
        
        # Test API Gateway Health Check (Service Status)
        try:
            response = await client.get("http://localhost:8000/health")
            print(f"\n🔍 Service Health Check via API Gateway:")
            health_data = response.json()
            for service, status in health_data['services'].items():
                emoji = "✅" if status['status'] == 'healthy' else "❌"
                print(f"  {emoji} {service.capitalize()}: {status['status']}")
        except Exception as e:
            print(f"❌ API Gateway Health Check: Error - {e}")

    print("\n" + "=" * 50)
    print("Microservices test completed!")

if __name__ == "__main__":
    asyncio.run(test_microservices())