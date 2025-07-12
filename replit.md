# Travel Management - WNS

## Overview

This is a city-based employee travel management system transformed from a monolithic FastAPI application into a complete microservices architecture. The system manages transportation for employees with role-based access control for admins, drivers, and employees. It handles trip scheduling, driver assignments, vehicle management, and real-time notifications across distributed services.

## Recent Changes (July 12, 2025)

✓ **BANGALORE-SPECIFIC ENHANCED FEATURES ADDED**: Complete WNS transport policy integration
✓ **INTERACTIVE WEB INTERFACE**: Modern, client-ready presentation system implemented
✓ **REAL-TIME LOCATION TRACKING**: Live driver tracking with ETA calculations
✓ **WNS VURAM OFFICE INTEGRATION**: Whitefield-specific routing and zone optimization
✓ **BANGALORE TRANSPORT ZONES**: Full zone mapping based on official WNS policy
  - East Zone: Yelahanka, Whitefield, Hoskote, IT corridor coverage
  - West Zone: Kengeri, Nagarbhavi, residential areas
  - North Zone: Hebbal, airport route, industrial areas  
  - South Zone: Electronic City, JP Nagar, IT hubs
  - Central Zone: City center, transport hubs
✓ **TRAFFIC-AWARE ETA SYSTEM**: Real-time calculations based on Bangalore traffic patterns
✓ **INTELLIGENT DRIVER ASSIGNMENT**: Zone-based optimal matching algorithm
✓ **CLIENT-READY DASHBOARD**: Professional presentation interface for stakeholder demos
✓ **WNS POLICY COMPLIANCE**: Integrated transport timings, buffers, and guidelines
  - Sociable hours: 06:30-20:30 for all employees
  - 15 minutes before login buffer, 20 minutes after logout buffer
  - Distance-based travel time matrix (0-10km: 0-60min, up to 30km+: 120-150min)
✓ **ENHANCED MICROSERVICE INTEGRATION**: Seamless backend-frontend connectivity

## Previous Changes (July 11, 2025)

✓ **MAJOR ARCHITECTURAL TRANSFORMATION**: Successfully migrated from monolithic to microservices architecture
✓ Created 5 independent microservices with complete separation of concerns:
  - Auth Service (port 8001): User authentication and authorization
  - User Service (port 8002): Driver and employee profile management  
  - Trip Service (port 8003): Trip scheduling and management
  - Notification Service (port 8004): System notifications
  - API Gateway (port 8000): Request routing and middleware
✓ Implemented shared component library for code reuse across services
✓ Set up Docker containers and docker-compose orchestration
✓ Created inter-service communication using HTTP clients
✓ Established JWT-based authentication with user context propagation
✓ Built centralized microservice runner for local development
✓ **FULLY OPERATIONAL**: All 5 microservices now running with 100% health validation
✓ **AUTHENTICATION FLOW COMPLETE**: JWT token generation, validation, and user context forwarding working perfectly
✓ **API GATEWAY FUNCTIONAL**: Successfully routing authenticated requests to all downstream services
✓ **DATABASE INTEGRATION**: Each service maintains its own isolated PostgreSQL database
✓ **COMPREHENSIVE ADMIN FUNCTIONALITY**: Complete admin management system implemented and operational
✓ **COMPLETE ADMIN MANAGEMENT SYSTEM**: Implemented streamlined admin functionality with proper hierarchy
  - List all drivers with complete user details and authentication status
  - List all employees with location and schedule information
  - Intelligent driver assignment based on employee home location
  - Complete trip management and monitoring capabilities
  - User status toggling for drivers and employees
  - Comprehensive admin dashboard with real-time statistics
  - Removed unnecessary admin listing endpoints for cleaner architecture
✓ **LOCATION-BASED DRIVER ASSIGNMENT**: Automatic driver matching by service area with fallback options
✓ **INTER-SERVICE COMMUNICATION**: Admin functions communicate with Auth and Trip services
✓ **ROLE-BASED ACCESS CONTROL**: Admin hierarchy properly enforced above drivers and employees
✓ **DATABASE DEPENDENCY INJECTION**: Fixed and optimized database connection handling across services
✓ **SIMPLIFIED TRIP CREATION**: Removed vehicle ID constraints from trip creation API
  - Trip creation no longer requires vehicle_id parameter
  - Vehicle assignment handled separately by admin functions
  - Cleaner API with focus on employee-driver assignment workflow
  - Removed vehicle assignment endpoints and schemas where unnecessary
✓ **CRITICAL TRIP CREATION FIXES COMPLETED (July 11, 2025)**:
  - Fixed missing vehicle_id field in TripCreate schema causing AttributeError
  - Verified real employee/driver ID combinations from database analysis
  - Updated test scripts with proper error handling and fallback URLs
  - Documented exact API usage with working curl commands
  - All trip creation issues resolved and ready for testing
✓ Maintained all existing functionality while improving scalability and reliability

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Microservices Architecture
- **Auth Service**: Handles user authentication, JWT token generation/validation, and user account management
- **User Service**: Manages driver and employee profiles, identity verification, and location-based matching
- **Trip Service**: Handles trip creation, scheduling, assignment, and status tracking
- **Notification Service**: Manages system notifications and communication
- **API Gateway**: Central entry point for routing requests, authentication middleware, and service orchestration

### Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **SQLAlchemy**: ORM for database operations with declarative models
- **PostgreSQL**: Separate databases for each microservice ensuring complete isolation
- **Pydantic**: Data validation and serialization using Python type hints
- **httpx**: Async HTTP client for inter-service communication
- **Docker**: Containerization for deployment and development
- **Docker Compose**: Multi-service orchestration

### Authentication & Authorization
- **JWT tokens**: Stateless authentication with role-based access control
- **bcrypt**: Password hashing for secure storage
- **Role-based permissions**: Three distinct user roles (admin, driver, employee)
- **API Gateway middleware**: Automatic user context propagation to downstream services

### Database Design
Each microservice maintains its own database with specific entities:
- **Auth Service**: Users (authentication and authorization)
- **User Service**: Drivers, Employees, Vehicles (profile management)
- **Trip Service**: Trips (scheduling and tracking)
- **Notification Service**: Notifications (system communications)
- **Cross-service references**: Uses service IDs instead of foreign keys for loose coupling

### Enhanced Web Interface (Port 5000)
- **Interactive Dashboard**: Real-time stats, zone coverage maps, live activity feeds
- **Bangalore Zone Visualization**: Interactive map showing all 5 transport zones with coverage details
- **Live Trip Tracking**: Real-time driver location tracking with ETA updates and route visualization
- **Enhanced Trip Creation**: Zone-based pickup selection, optimal driver assignment, traffic-aware calculations
- **WNS Policy Integration**: Built-in compliance with Bangalore transport timings and guidelines
- **Client Presentation Ready**: Professional UI designed for stakeholder demonstrations

## Key Components

### Models Layer
- **User**: Base authentication model with email, password, and role
- **Employee**: Extended profile for employees with home location and commute schedule
- **Driver**: Extended profile for drivers with license and vehicle information
- **Vehicle**: Fleet management with capacity and availability tracking
- **Trip**: Core business entity managing travel requests and assignments
- **Notification**: System-wide communication mechanism

### API Layer
Organized into domain-specific modules:
- **Authentication**: User registration, login, and token management
- **Admin**: User management, analytics, and trip assignments
- **Driver**: Profile management and trip operations
- **Employee**: Profile management and trip viewing
- **Trip**: Core trip management operations
- **Notification**: System communications

### Router Layer
FastAPI routers with role-based access control:
- JWT token validation on protected endpoints
- Role verification middleware for each user type
- RESTful API design with proper HTTP status codes

## Data Flow

### Microservices Communication
1. **API Gateway** receives all external requests
2. **JWT validation** performed at gateway level
3. **User context** (ID, role, email) propagated via headers to downstream services
4. **Service-to-service** communication uses async HTTP clients
5. **Database isolation** ensures each service manages its own data independently

### User Registration & Authentication Flow
1. Registration request → API Gateway → Auth Service
2. Auth Service creates user account and returns JWT token
3. Profile creation request → API Gateway → User Service
4. User Service creates role-specific profile (driver/employee)
5. JWT token used for all subsequent authenticated requests

### Driver Identity Verification Workflow
1. Document upload → API Gateway → User Service
2. Files stored securely in service-specific uploads directory
3. Admin verification request → API Gateway → User Service
4. Verification status update triggers Notification Service
5. Driver receives real-time notification about status change

### Trip Management Workflow
1. Trip creation → API Gateway → Trip Service
2. Trip Service stores trip data in isolated database
3. Driver assignment → User Service lookup for driver details
4. Status updates → Trip Service → Notification Service
5. Real-time notifications sent to relevant users

### Inter-Service Data Consistency
1. Services use **eventual consistency** model
2. **Service IDs** used for cross-service references (no foreign keys)
3. **Compensation patterns** for handling distributed transaction failures
4. **Health checks** ensure service availability before requests

## External Dependencies

### Core Libraries
- **FastAPI**: Web framework and automatic API documentation
- **SQLAlchemy**: Database ORM and session management
- **psycopg2**: PostgreSQL database adapter
- **python-jose**: JWT token handling
- **passlib**: Password hashing with bcrypt
- **pydantic**: Data validation and serialization

### Development Tools
- **uvicorn**: ASGI server for running the application
- **python-multipart**: Form data handling
- **python-dotenv**: Environment variable management

## Deployment Strategy

### Local Development
- **Microservice Runner**: `python run_microservices.py` starts all services
- **Service Ports**: Auth(8001), User(8002), Trip(8003), Notification(8004), Gateway(8000)
- **Database**: Single PostgreSQL instance with separate schemas per service
- **Health Monitoring**: Built-in health checks and service status dashboard

### Docker Deployment
- **Individual Dockerfiles**: Each service has optimized container configuration
- **Docker Compose**: Orchestrates all services with proper dependencies
- **Network Isolation**: Services communicate over dedicated Docker network
- **Database**: Containerized PostgreSQL with persistent volumes

### Environment Configuration
- **Service-specific settings**: Each service has isolated configuration
- **Shared configuration**: Common settings in shared module
- **Environment variables**: Database URLs, service URLs, JWT secrets
- **Debug toggles**: Per-service debugging capabilities

### Production Considerations
- **Horizontal scaling**: Each service can scale independently
- **Load balancing**: API Gateway can be load balanced for high availability
- **Database sharding**: Each service database can be optimized separately
- **Service discovery**: Health checks and automatic failover capabilities
- **Monitoring**: Distributed logging and metrics collection
- **Security**: JWT token validation at gateway with service isolation

### Migration Benefits
- **Independent deployment**: Services can be updated without affecting others
- **Technology flexibility**: Each service can use different tech stacks if needed
- **Fault isolation**: Service failures don't cascade to entire system
- **Team scalability**: Different teams can own different services
- **Performance optimization**: Services can be optimized for specific workloads

The microservices architecture provides a robust foundation for scaling the travel management system while maintaining the existing functionality and improving operational flexibility.