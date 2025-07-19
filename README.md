# Appointment Booking System Documentation

## Project Overview

This is a comprehensive appointment booking system that allows patients to book appointments with doctors, manage their profiles, and handles complex business logic. Healthcare providers use this system to manage patient appointments, doctor schedules, and generate reports.

The system follows a microservice architecture with the following components:

- **Backend**: FastAPI (Python)
- **Frontend**: React.js
- **Database**: PostgreSQL
- **Message Broker**: RabbitMQ
- **Task Queue**: Celery
- **Cache**: Redis
- **Containerization**: Docker

## Setup Instructions

## Prerequisite
- **Docker**

- **Node.js (for frontend)** (for manuel installation)
- **Python (backend)** (for manuel installation)

## Installation
**Clone the repository:**
   ```bash
   git clone git@github.com:uzzalpro/appointment-booking-system-backend.git
   ```
**Start the services:**
```
docker compose -f docker-compose-dev.yml up -d --build
```
**Access the application**:
- **Backend:** ```http://127.0.0.1:8000```

## Architecture Diagram
```
┌───────────────────────────────────────────────────────────────────────────────┐
│                               Client (React)                                  │
└───────────────────────┬───────────────────────┬───────────────────────────────┘
                        │                       │
                        ▼                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                               API Gateway (FastAPI)                           │
└───────┬─────────────────────────────────┬─────────────────────────────────────┘
        │                                 │                       
        ▼                                 ▼                        
┌───────────────┐             ┌─────────────────────────┐      
│  User Service │             │ Appointment & Reporting │    
│               │             │       Service           │      
└───────────────┘             └─────────────────────────┘     
        |                                 |                       
        ▼                                 ▼                       
┌───────────────────────────────────────────────────────────────────────────────┐
│                           PostgreSQL Database                                 │
└───────────────────────────────────────────────────────────────────────────────┘
        |
        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           Celery Workers                                      │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                │                    
                                ▼                      
                      ┌─────────────────┐    
                      │ remaider        │  
                      │ Service         │     
                      └─────────────────┘     

```

## SOLID Principles Implementation
 - Each service (user, appointment, reporting) has a single responsibility
 - Controllers, services, and repositories are separated

### Frontend Installation
**Clone the repository:**
   ```bash
   git git@github.com:uzzalpro/appointment-booking-system-frontend.git
   ```
**Set up the frontend:**
```cd frontend
npm install
npm start
```
- **Frontend:** ```http://localhost:3000```

## API Documentation

The API documentation is available via **Swagger UI** at ```http://127.0.0.1:8000/user-auth/api/v1/api-docs``` when the backend is running.

## Authentication
All endpoints (except login/register) require JWT authentication. Include the token in the Authorization header:
```Authorization: Bearer <your_token>```

## Database Schema
```
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mobile VARCHAR(14) UNIQUE NOT NULL CHECK (mobile LIKE '+88%'),
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(10) NOT NULLCHECK (user_type IN ('patient', 'doctor', 'admin')),
    division VARCHAR(50),
    district VARCHAR(50),
    thana VARCHAR(50),
    profile_image VARCHAR(255),
    license_number VARCHAR(50),
    experience_years INTEGER,
    consultation_fee DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    specializations INTEGER REFERENCES doctor_specializations(id)
    status VARCHAR(10) NOT CHECK (user_type IN ('patient', 'doctor', 'admin'))
);
```
## Challenges Faced and Solutions
- **Complex Validation Requirements:**
 - **Challenge**: Multiple validation rules for user registration and appointment booking
 - **Solution**: Implemented Pydantic models with custom validators and database-level constraints

## Background Tasks:
 - **Challenge**: Implementing reliable background tasks for reminders
 - **Solution**: Used Celery Scheduler and Redis for result backend

## Time Slot Management:
 - **Challenge**: Ensuring appointment times don't conflict with doctor availability
 - **Solution**: Implemented comprehensive validation in both API and database

## Microservice Communication:
 - **Challenge**: Coordinating between user, appointment, and reporting services
 - **Solution**: Used shared database for simplicity (could be replaced with API calls in future)


## Monitoring and Maintenance
 - **Logging**: Implemented comprehensive logging for all services
 - **Health Checks**: Added health check endpoints for all services

## Future Improvements
Implement API Gateway for better microservice management
Add rate limiting to prevent abuse
Implement more sophisticated caching strategy
Add WebSocket support for real-time notifications
Implement comprehensive testing at all levels


