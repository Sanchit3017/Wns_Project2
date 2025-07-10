# Travel Management - WNS

## Overview

This is a city-based employee travel management system built with FastAPI, SQLAlchemy, and PostgreSQL. The system manages transportation for employees with role-based access control for admins, drivers, and employees. It handles trip scheduling, driver assignments, vehicle management, and real-time notifications.

## Recent Changes (July 10, 2025)

✓ Updated application name to "Travel Management - WNS"
✓ Added ongoing trip tracking functionality to employee API
✓ Added `/api/employee/trips/current` endpoint to get current ongoing trip
✓ Enhanced employee dashboard to include current trip tracking
✓ Configured application to run on port 5000 for Replit deployment
✓ Fixed Pydantic configuration to ignore extra environment variables
✓ Successfully deployed with PostgreSQL database integration

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **SQLAlchemy**: ORM for database operations with declarative models
- **PostgreSQL**: Primary relational database for data persistence
- **Pydantic**: Data validation and serialization using Python type hints

### Authentication & Authorization
- **JWT tokens**: Stateless authentication with role-based access control
- **bcrypt**: Password hashing for secure storage
- **Role-based permissions**: Three distinct user roles (admin, driver, employee)

### Database Design
The system uses a relational database with the following core entities:
- Users (base authentication table)
- Employees (employee-specific profile data)
- Drivers (driver-specific profile data)
- Vehicles (fleet management)
- Trips (travel requests and assignments)
- Notifications (system communications)

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

### User Registration & Authentication
1. User registers with role-specific information
2. System creates base User record and role-specific profile
3. JWT token issued for authenticated sessions
4. Role-based access enforced on subsequent requests

### Trip Management Workflow
1. Admin creates trips for employees
2. Admin assigns drivers and vehicles to trips
3. Driver receives trip notifications
4. Driver updates trip status (start/complete)
5. System tracks trip history and analytics

### Notification System
1. System generates notifications for trip updates
2. Role-based notification targeting
3. Mark as read/unread functionality
4. Bulk notification capabilities for admins

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

### Environment Configuration
- Environment-based configuration using Pydantic settings
- Database URL configuration for different environments
- JWT secret key management
- Debug mode toggles

### Database Management
- SQLAlchemy engine with connection pooling
- Automatic table creation on startup
- Sample data initialization for development
- Migration-ready architecture

### CORS Configuration
- Configured for cross-origin requests
- Supports all origins in development (should be restricted in production)
- Credential support enabled

### Production Considerations
- Connection pooling with pre-ping health checks
- Connection recycling for long-running applications
- Configurable token expiration times
- Environment-specific debug logging

The system is designed to be modular and scalable, with clear separation of concerns between authentication, business logic, and data access layers. The architecture supports easy extension for additional features like real-time location tracking, advanced analytics, or mobile application integration.