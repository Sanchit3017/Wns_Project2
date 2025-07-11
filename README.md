# Travel Management System - Microservices Architecture

A comprehensive employee travel management system built with FastAPI microservices architecture. The system manages transportation logistics with role-based access control for administrators, drivers, and employees.

## 🏗️ Architecture Overview

The system has been transformed from a monolithic application into a distributed microservices architecture:

```
┌─────────────────┐
│   API Gateway   │ ← Single entry point (Port 8000)
│   (Port 8000)   │
└─────────┬───────┘
          │
          ├─── Auth Service (Port 8001)      ← Authentication & User Management
          ├─── User Service (Port 8002)      ← Driver & Employee Profiles
          ├─── Trip Service (Port 8003)      ← Trip Management & Scheduling
          └─── Notification Service (Port 8004) ← System Notifications
```

## 🚀 Quick Start

### Running All Services
```bash
# Start all microservices
python run_microservices.py

# Test all services
python test_microservices.py
```

### Docker Deployment
```bash
# Build and start with Docker Compose
docker-compose up --build

# Check service health
curl http://localhost:8000/health
```

## 📋 Service Details

### API Gateway (Port 8000)
- **Purpose**: Central routing and authentication middleware
- **Features**: JWT validation, request proxying, health monitoring
- **Endpoints**: Routes to all downstream services

### Auth Service (Port 8001)
- **Purpose**: User authentication and authorization
- **Database**: `users` table
- **Features**: JWT token generation, user registration, login

### User Service (Port 8002)
- **Purpose**: Profile management for drivers and employees
- **Database**: `drivers`, `employees`, `vehicles` tables
- **Features**: Identity verification, location-based matching, file uploads

### Trip Service (Port 8003)
- **Purpose**: Trip scheduling and management
- **Database**: `trips` table
- **Features**: Trip creation, assignment, status tracking, analytics

### Notification Service (Port 8004)
- **Purpose**: System-wide notifications
- **Database**: `notifications` table
- **Features**: Real-time notifications, bulk messaging, read status

## 🔧 Development

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker (optional)

### Environment Setup
```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email] pydantic-settings httpx

# Set environment variables
export DATABASE_URL="postgresql://postgres:password@localhost:5432/travel_management"
export SECRET_KEY="your-secret-key-here"
```

### Service URLs
- **API Gateway**: http://localhost:8000
- **Auth Service**: http://localhost:8001
- **User Service**: http://localhost:8002
- **Trip Service**: http://localhost:8003
- **Notification Service**: http://localhost:8004

## 📊 Health Monitoring

Check overall system health:
```bash
curl http://localhost:8000/health
```

Individual service health:
```bash
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # User Service
curl http://localhost:8003/health  # Trip Service
curl http://localhost:8004/health  # Notification Service
```

## 🔐 Authentication

The system uses JWT-based authentication with role-based access control:

- **Admin**: Full system access, user management, trip assignment
- **Driver**: Profile management, trip status updates, availability
- **Employee**: Profile viewing, trip history, requests

All requests go through the API Gateway which validates tokens and propagates user context to downstream services.

## 🗄️ Database Architecture

Each microservice maintains its own database for complete isolation:

- **Auth Service**: User accounts and authentication
- **User Service**: Driver/employee profiles and vehicles
- **Trip Service**: Trip scheduling and tracking
- **Notification Service**: System notifications

Cross-service references use service IDs instead of foreign keys to maintain loose coupling.

## 🐳 Docker Support

Individual Dockerfiles for each service with shared dependency management:

```yaml
# docker-compose.yml includes:
- PostgreSQL database
- All 5 microservices
- Network isolation
- Health checks
```

## 📈 Scaling Benefits

The microservices architecture provides:

- **Independent Scaling**: Scale services based on load
- **Fault Isolation**: Service failures don't cascade
- **Technology Flexibility**: Each service can use different tech stacks
- **Team Autonomy**: Different teams can own services
- **Deployment Independence**: Update services separately

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_microservices.py
```

This validates:
- All services are running
- Health checks pass
- API Gateway routing works
- Inter-service communication

## 📝 API Documentation

Each service provides automatic OpenAPI documentation:
- http://localhost:8001/docs (Auth Service)
- http://localhost:8002/docs (User Service)
- http://localhost:8003/docs (Trip Service)
- http://localhost:8004/docs (Notification Service)

## 🛠️ Development Workflow

1. **Start Services**: `python run_microservices.py`
2. **Verify Health**: `python test_microservices.py`
3. **Access Gateway**: http://localhost:8000
4. **Check Logs**: Monitor console output from all services
5. **API Testing**: Use gateway routes or direct service endpoints

## 🔄 Migration from Monolith

This system was successfully migrated from a monolithic FastAPI application to microservices while maintaining:
- All existing functionality
- Database compatibility
- API endpoint structure
- Authentication mechanisms
- User roles and permissions

The migration provides improved scalability, maintainability, and deployment flexibility while preserving the robust travel management capabilities.