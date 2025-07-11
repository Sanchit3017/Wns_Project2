#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import threading
from pathlib import Path

# Add current directory to Python path for shared imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def run_service(service_name, service_dir, port):
    """Run a microservice in a separate process"""
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir)
    
    print(f"Starting {service_name} on port {port}...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=service_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[{service_name}] {line.strip()}")
        
    except Exception as e:
        print(f"Error running {service_name}: {e}")

def main():
    """Main function to start all microservices"""
    services = [
        ("Auth Service", "auth-service", 8001),
        ("User Service", "user-service", 8002),
        ("Trip Service", "trip-service", 8003),
        ("Notification Service", "notification-service", 8004),
        ("API Gateway", "api-gateway", 8000),
    ]
    
    threads = []
    
    print("Starting Travel Management Microservices...")
    print("=" * 50)
    
    for service_name, service_dir, port in services:
        service_path = current_dir / service_dir
        if service_path.exists():
            thread = threading.Thread(
                target=run_service,
                args=(service_name, service_path, port),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(2) 
        else:
            print(f"Warning: {service_dir} directory not found")
    
    print("\nAll services started. Press Ctrl+C to stop.")
    print("=" * 50)
    print("Service URLs:")
    print("  Auth Service:         http://localhost:8001")
    print("  User Service:         http://localhost:8002")
    print("  Trip Service:         http://localhost:8003")
    print("  Notification Service: http://localhost:8004")
    print("  API Gateway:          http://localhost:8000")
    print("=" * 50)
    
    try:
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down microservices...")

if __name__ == "__main__":
    main()