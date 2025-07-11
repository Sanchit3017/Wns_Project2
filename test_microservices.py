#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test_microservices():
    
    print("Testing Travel Management Microservices")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        try:
            response = await client.get("http://localhost:8000/")
            print(f"✅ API Gateway: {response.status_code} - {response.json()['service']}")
        except Exception as e:
            print(f"❌ API Gateway: Error - {e}")
        
        
        try:
            response = await client.get("http://localhost:8001/health")
            print(f"✅ Auth Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Auth Service: Error - {e}")
        
        
        try:
            response = await client.get("http://localhost:8002/health")
            print(f"✅ User Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ User Service: Error - {e}")
        
        
        try:
            response = await client.get("http://localhost:8003/health")
            print(f"✅ Trip Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Trip Service: Error - {e}")
        
        
        try:
            response = await client.get("http://localhost:8004/health")
            print(f"✅ Notification Service: {response.status_code} - {response.json()['status']}")
        except Exception as e:
            print(f"❌ Notification Service: Error - {e}")
        
        
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