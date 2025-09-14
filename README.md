# EventlyChahat - Async Event Management System

## Overview

EventlyChahat is a high-performance, asynchronous event management and booking platform built with FastAPI. It provides a comprehensive solution for managing events, user registrations, seat bookings, and analytics with enterprise-grade features including caching, waitlist management, and real-time analytics.

## Key Features

- **🎫 Event Management**: Create, update, and manage events with capacity control
- **👥 User Authentication**: JWT-based authentication with role-based access (Admin/User)
- **💺 Seat Booking System**: Seat level booking and cancellation 
- **⏳ Waitlist Management**: Redis's sortedSet used for waitlist system for fully booked events
- **🚪 API Gateway and  Rate Limiting**: Nginx-based API gateway with intelligent request routing and load balancing  Advanced rate limiting (15 req/s per IP) with leaky bucket algorithm for DDoS protection
- **⚡ Caching Performance Optimized**: Redis caching for improved response times
- **📊 Analytics Dashboard**: Comprehensive analytics with booking trends and capacity utilization
- **🔄 Async Architecture**: Fully asynchronous for high concurrency
- **🐳 Docker Ready and Docker Swarm**: Complete containerization with Docker Compose and Horizontal scaling with docker swarm for backend service .   

## Architecture & Design Decisions

### Major Design Decisions

#### 1. **Asynchronous Architecture**
- **Decision**: Use proper locking to avoid double booking and race conditions 
- **Reference**: I stumbled upon a great video by Hussein Nasser ( My fav. tech youtuber for backend ) : https://www.youtube.com/watch?v=I8IlO0hCSgY , this exact video solves our exact problem using pessimistic locking . 
- **Trade-offs**: 
  - ✅ Pessimistic locking for booking to avoid double booking and race conditions . 
- **Reasoning**: Double booking is a very critical issue and this should be explicitly handled . 

#### 1. **Asynchronous Architecture**
- **Decision**: Built entirely on FastAPI with async/await patterns
- **Trade-offs**: 
  - ✅ Excellent for I/O bound operations (database queries, cache operations)
  - ✅ Better resource utilization and scalability
  - ❌ Slightly more complex database operations due to lack of support for features for async db engine , we are not able to SQLAlchemy's inert features like lazy loading and we have to eager load the values .   
- **Reasoning**: Event booking systems are heavily I/O bound, making async architecture ideal for handling multiple concurrent bookings . 

#### 2. **PostgreSQL + Redis Hybrid Storage**
- **Decision**: PostgreSQL for persistent data, Redis for caching and waitlist
- **Trade-offs**:
  - ✅ ACID compliance for critical booking data
  - ✅ Fast read operations with Redis caching
  - ✅ Built-in waitlist with Redis with sorted sets
  - ❌ Additional complexity managing cache invalidation to maintain strong consistency , we need to delete cache with relevant keys like event:<event_id>* prefix and event:booking:<event_id>* when we use put , post , delete .  
- **Reasoning**: Combines reliability of SQL with performance of in-memory caching

#### 3. **Microservice-Ready Architecture**
- **Decision**: Modular structure with clear separation of concerns
- **Components**:
  - **API Layer**: Clean REST endpoints with versioning (`/api/v1/`)
  - **CRUD Layer**: Database operations abstraction
  - **Core Services**: Configuration, Redis, authentication
  - **Models**: SQLAlchemy ORM models
  - **Schemas**: Pydantic models for validation
- **Trade-offs**:
  - ✅ Easy to scale individual components
  - ✅ Clear separation of concerns

#### 4. **JWT Authentication Strategy**
- **Decision**: Stateless JWT tokens with role-based access control
- **Implementation**: 
  - Admin-only endpoints for event management and analytics
  - User endpoints for bookings and personal data

#### 5. **API Gateway & Rate Limiting Implementation**
- **Decision**: Nginx as a Reverse Proxy with built-in rate limiting using leaky bucket algorithm
- **Implementation**:
  - **Rate Limiting**: 15 requests/second per IP address with burst capacity of 10 requests
  - **Leaky Bucket Algorithm**: Processes 1 request immediately, queues up to 10 requests with no delay, then applies rate limiting
- **Trade-offs**:
  - ✅ DDoS protection and abuse prevention
  - ✅ Better system stability under high load
  - ✅ Cost-effective compared to cloud-based API gateways
  - ❌ Single point of failure if not properly configured for high availability
  - ❌ Limited advanced features compared to dedicated API gateway solutions
- **Reasoning**: Nginx provides rate limiting with minimal overhead, perfect for protecting the booking system from abuse while maintaining high performance

### Scalability Approach

#### 1. **Horizontal Scaling Ready**
- **Load Balancing**: We use docker compose's replication feature to horizontally scale , so docker compose inherently uses docker swarm to scale the services and distribute the load between the services 
- **Stateless Design**: No server-side sessions, allows us to scale it further with k8s 

#### 2. **Caching Strategy**
- **Caching**: Redis central cache store for quickly resolving get calls  
- **Cache Invalidation**: Strategic cache invalidation on data mutations 

#### 3. **Database Optimization**
- **Indexing Strategy**: Strategic indexes on frequently queried columns
- **Query Optimization**: Efficient relationship loading with SQLAlchemy ( Since , we couldnt lazy load due to lack of support in Async version )

### Creative Features & Optimizations

#### 1. **Intelligent Waitlist System**
- **Redis Sorted Sets**: Priority-based waitlist using timestamps
- **Automatic Promotion**: Users automatically notified when seats become available
- **TTL-based Cleanup**: Automatic waitlist entry expiration based on event start_time

#### 2. **Analytics**
- **Capacity Utilization**: Venue and event performance analytics
- **User Behavior Analytics**: Individual user booking patterns

#### 3. **Smart Caching**
- **Read through cache**: Implemented the caching 
- **Dynamic Cache Keys**: namespace based cache key generation

#### 3. **Waitlist implementation with Redis**
- **Implemented waitlist using redis**: Utilized sortedSet data structure as priority queue to implement waitlist 
- **Namespace based cache keys**: push to waitlist by dynamically creating cache key for each event's waitlist

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 
- **Cache**: Redis 
- **API Gateway**: Nginx with rate limiting 
- **Authentication**: JWT 
- **ORM**: SQLAlchemy (async)
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (reverse proxy & load balancer)
- **Admin Interface**: Adminer

## Project Structure

```
EventlyChahat/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── v1/                 # API version 1 routes
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User management endpoints
│   │       ├── events.py       # Event management endpoints
│   │       ├── seats.py        # Seat booking endpoints
│   │       ├── bookings.py     # Booking management endpoints
│   │       ├── analytics.py    # Analytics and reporting endpoints
│   │       ├── waitlist.py     # Waitlist management endpoints
│   │       └── deps.py         # Dependency injection functions
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   └── redis.py            # Redis connection and utilities
│   ├── crud/                   # Database operations layer
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── booking.py
│   │   ├── seat.py
│   │   └── analytics.py
│   ├── db/
│   │   └── session.py          # Database session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── booking.py
│   │   └── seat.py
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── booking.py
│   │   ├── seat.py
│   │   └── analytics.py
│   └── helper/
│       ├── helper.py           # Utility functions
│       └── notification.py     # Notification services
├── docker-compose.yml          # Multi-service orchestration
├── Dockerfile                  # Application container definition
├── nginx.conf                  # Nginx configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EventlyChahat
```

### 2. Environment Setup

Create a `.env` file in the root directory  , for now all of these values are already hardcoded for quick testing :


```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=evently
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/evently

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis Configuration
REDIS_HOST=cache
REDIS_PORT=6379

# Email Configuration (Optional)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain
```

### 3. Start the Application

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Verify Installation

- **API Documentation**: http://127.0.0.1/docs (Swagger UI)
- **Database Admin**: http://127.0.0.1:8080 (Adminer)
  - Server: `db`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `evently`

## API Documentation

### Base URL
```
http://127.0.0.1/api/v1

```

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword",
  "is_admin": false
}
```

#### Login
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

### Events Management

#### Create Event (Admin Only)
```http
POST /api/v1/events/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Tech Conference 2024",
  "venue": "Convention Center",
  "description": "Annual technology conference",
  "start_time": "2024-06-15T09:00:00Z",
  "end_time": "2024-06-15T18:00:00Z",
  "capacity": 100
}
```

#### List Events
```http
GET /api/v1/events/?name=tech&venue=center&limit=10&offset=0
```

#### Get Event Details
```http
GET /api/v1/events/{event_id}
```

#### Update Event (Admin Only)
```http
PUT /api/v1/events/{event_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Event Name",
  "capacity": 150
}
```

#### Delete Event (Admin Only)
```http
DELETE /api/v1/events/{event_id}
Authorization: Bearer <token>
```

### Seat Management

#### List Available Seats
```http
GET /api/v1/events/{event_id}/seats
```

#### Book a Seat
```http
POST /api/v1/events/{event_id}/book/{seat_number}
Authorization: Bearer <token>
```

### Booking Management

#### Get User Bookings
```http
GET /api/v1/bookings/
Authorization: Bearer <token>
```

#### Cancel Booking
```http
DELETE /api/v1/bookings/cancel/{booking_id}
Authorization: Bearer <token>
```

### Waitlist Management

#### Join Waitlist
```http
POST /api/v1/waitlist/{event_id}
Authorization: Bearer <token>
```

### Analytics (Admin Only)

#### Analytics Overview
```http
GET /api/v1/analytics/overview
Authorization: Bearer <admin-token>
```

#### Popular Events
```http
GET /api/v1/analytics/popular-events?limit=5
Authorization: Bearer <admin-token>
```

#### Booking Trends
```http
GET /api/v1/analytics/booking-trends?days=30
Authorization: Bearer <admin-token>
```

#### User Statistics
```http
GET /api/v1/analytics/my-stats
Authorization: Bearer <token>
```

#### Venue Analytics
```http
GET /api/v1/analytics/venue-analytics
Authorization: Bearer <admin-token>
```

### Route Structure Overview

```
/api/v1/
├── auth/
│   ├── POST /register          # User registration
│   └── POST /token             # User login
├── users/
│   └── [User management endpoints]
├── events/
│   ├── POST /                  # Create event (admin)
│   ├── GET /                   # List events
│   ├── GET /{id}               # Get event details
│   ├── PUT /{id}               # Update event (admin)
│   ├── DELETE /{id}            # Delete event (admin)
│   └── GET /bookings/{id}      # Get event bookings
├── events/{id}/
│   ├── GET /seats              # List seats
│   └── POST /book/{seat_num}   # Book seat
├── bookings/
│   ├── GET /                   # Get user bookings
│   └── DELETE /cancel/{id}     # Cancel booking
├── waitlist/
│   └── POST /{event_id}        # Join waitlist
└── analytics/
    ├── GET /overview           # Analytics overview (admin)
    ├── GET /popular-events     # Popular events (admin)
    ├── GET /capacity-utilization # Capacity report (admin)
    ├── GET /booking-trends     # Booking trends (admin)
    ├── GET /user-stats/{id}    # User stats (admin)
    ├── GET /my-stats           # Current user stats
    ├── GET /venue-analytics    # Venue analytics (admin)
    └── GET /summary            # Quick summary (admin)
```

## Database Schema and ER Diagram 
<img width="796" height="727" alt="eg" src="https://github.com/user-attachments/assets/39669fea-c157-4898-a6b9-66e267cd8387" />

### Core Entities

#### Users
- `id` (Primary Key)
- `email` (Unique)
- `full_name`
- `hashed_password`
- `is_admin` (Boolean)
- `created_at`

#### Events
- `id` (Primary Key)
- `name`
- `venue`
- `description`
- `start_time`
- `end_time`
- `capacity`
- `created_by` (Foreign Key → Users)
- `created_at`

#### Seats
- `id` (Primary Key)
- `seat_number`
- `event_id` (Foreign Key → Events)
- `status` (AVAILABLE/BOOKED)
- `extradata` (JSON)
- `created_at`

#### Bookings
- `id` (Primary Key)
- `user_id` (Foreign Key → Users)
- `event_id` (Foreign Key → Events)
- `seat_id` (Foreign Key → Seats)
- `status` (PENDING/BOOKED/CANCELLED)
- `created_at`

### Relationships
- Users → Events (One-to-Many) - Creator relationship
- Users → Bookings (One-to-Many) - User bookings
- Events → Seats (One-to-Many) - Event seats
- Events → Bookings (One-to-Many) - Event bookings
- Seats → Bookings (One-to-One) - Seat booking

## Development

### Local Development Setup

1. **Python Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**:
```bash
# Start only database and Redis
docker-compose up db cache -d

# Update DATABASE_URL in .env for local development
# THESE VALUES ARE ALREADY HARDCODED FOR QUICK TESTING
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/evently
REDIS_HOST=localhost
```

3. **Run Application**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment

### Environment Variables for Production

```env
# DONT SET ENV VARIABLES , DEFAULT VALUES ARE ALREADY SET FOR QUICK TESTING
# Security
JWT_SECRET=<strong-random-secret>
DATABASE_URL=<production-database-url>

# Performance
REDIS_HOST=<redis-host>
REDIS_PORT=6379

# Email
# THIS SERVICE IS STILL IN DEVELOPMENT
MAILGUN_API_KEY=<production-mailgun-key>
MAILGUN_DOMAIN=<production-domain>
```

### Docker Production Build

```bash
# Run with compose
docker-compose up --build
```

### Performance Tuning

1. **Database**:
   - Enable connection pooling
   - Optimize PostgreSQL settings
   - Set up read replicas for analytics

2. **Caching**:
   - Configure Redis persistence
   - Set up Redis clustering
   - Implement cache warming strategies

3. **Application**:
   - Configure Gunicorn/Uvicorn workers
   - Enable HTTP/2
   - Set up monitoring and logging

## Monitoring & Observability

### Health Checks

```http
GET /health
```

### Metrics Endpoints

- Application metrics available at `/metrics` (when configured)
- Redis metrics through Redis CLI
- PostgreSQL metrics through standard monitoring tools

### Logging

- Structured JSON logging
- Request/response logging
- Error tracking and alerting

## API Rate Limiting & Security

### Rate Limiting Implementation

EventlyChahat implements robust rate limiting at the API Gateway level using Nginx:

- **Rate Limit**: 15 requests per second per IP address
- **Burst Capacity**: Up to 10 additional requests can be queued without delay
- **Algorithm**: Leaky bucket implementation for smooth traffic handling
- **Scope**: Applied globally to all API endpoints
- **Memory Usage**: 10MB zone allocation for tracking IP addresses

**How it works:**
1. Each IP can make 15 requests/second continuously
2. Burst requests (up to 10) are processed immediately when rate limit allows
3. Excess requests beyond burst capacity are rejected with HTTP 429
4. Rate limiting resets automatically as time progresses

**Example Response Headers:**
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 15
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1694696400
```

### Security Features

- **API Gateway Protection**: Nginx-based rate limiting and request filtering
- JWT token authentication
- Password hashing with bcrypt
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration
- Input validation with Pydantic

### Recommended Production Security

- **Enhanced Rate Limiting**: Consider different limits for authenticated vs anonymous users
- Add API key authentication for admin endpoints
- Enable HTTPS/TLS
- Set up database SSL
- Configure firewall rules
- Implement request logging and monitoring
- Add DDoS protection at infrastructure level

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

<!-- ## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code examples in this README -->

---

**EventlyChahat** - Built with ❤️ using FastAPI.
