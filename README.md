# Travel Management - WNS

A comprehensive city-based employee travel management system built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- **Role-based Authentication**: Admin, Driver, and Employee roles with JWT token security
- **Driver Management**: Identity verification with document upload system
- **Location-based Assignment**: Smart driver matching based on proximity to employee locations
- **Trip Management**: Complete trip lifecycle from creation to completion
- **Real-time Notifications**: Automated notifications for trip updates and verification status
- **Fleet Management**: Vehicle tracking and assignment system

## Recent Updates (July 2025)

✅ Driver identity verification with secure document uploads (PDF, JPG, PNG, DOC)  
✅ Location-based driver search with proximity ranking algorithm  
✅ Service area tracking for precise location matching  
✅ Admin verification approval workflow  
✅ Automated notification system for status updates  

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Handling**: Secure document upload system
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## API Endpoints

### Authentication
- `POST /api/auth/register/admin` - Register admin user
- `POST /api/auth/register/driver` - Register driver with service area
- `POST /api/auth/register/employee` - Register employee
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile

### Driver Management
- `GET /api/driver/profile` - Get driver profile
- `PUT /api/driver/profile` - Update driver profile
- `POST /api/driver/upload-identity` - Upload identity documents
- `PUT /api/driver/availability` - Update availability status
- `GET /api/driver/trips` - Get assigned trips
- `GET /api/driver/dashboard` - Driver dashboard data

### Admin Operations
- `GET /api/admin/drivers` - List all drivers
- `GET /api/admin/employees` - List all employees
- `POST /api/admin/drivers/search-by-location` - Location-based driver search
- `PUT /api/admin/drivers/{id}/verify-identity` - Approve/reject driver verification
- `POST /api/admin/trips/{id}/assign` - Assign driver and vehicle to trip
- `GET /api/admin/analytics` - System analytics
- `GET /api/admin/dashboard` - Admin dashboard

### Employee Services
- `GET /api/employee/profile` - Get employee profile
- `PUT /api/employee/profile` - Update employee profile
- `GET /api/employee/trips/upcoming` - Get upcoming trips
- `GET /api/employee/trips/history` - Get trip history
- `POST /api/employee/trips/{id}/reschedule` - Request trip reschedule
- `GET /api/employee/dashboard` - Employee dashboard

### Notifications
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications/bulk` - Send bulk notifications (admin)
- `PUT /api/notifications/{id}/seen` - Mark notification as seen
- `DELETE /api/notifications/{id}` - Delete notification

## Database Schema

The system uses 6 main tables:
- **users**: Base authentication (16 users)
- **drivers**: Driver profiles with verification status (5 drivers)
- **employees**: Employee profiles with location data (5 employees)
- **vehicles**: Fleet management
- **trips**: Trip records and assignments
- **notifications**: System communications

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd travel-management-wns
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and JWT secret
   ```

4. **Initialize database**
   ```bash
   python main.py
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5000 --reload
   ```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_management
SECRET_KEY=your-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Travel Management - WNS
DEBUG=True
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

## File Upload Security

- Supported formats: PDF, JPG, JPEG, PNG, DOC, DOCX
- Maximum file size: 10MB
- Secure storage in `uploads/identity_proofs/`
- Unique filename generation to prevent conflicts

## Location Matching Algorithm

The system uses a proximity-based scoring algorithm to match drivers with employee locations:
1. Extracts location keywords from employee and driver service areas
2. Calculates similarity scores based on keyword matching
3. Ranks drivers by proximity score (lower = better match)
4. Provides ranked results for optimal assignment

## Security Features

- JWT token-based authentication
- Role-based access control
- Password hashing with bcrypt
- Secure file upload validation
- SQL injection prevention with ORM
- CORS configuration for cross-origin requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.