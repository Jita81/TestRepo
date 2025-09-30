# System Architecture

## Overview

The User Profile System follows a layered architecture pattern with clear separation of concerns between the frontend and backend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Components (UI Layer)                         │   │
│  │  - ProfilePage                                       │   │
│  │  - EditProfileModal                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Utilities & Services                                │   │
│  │  - API Client (Axios)                                │   │
│  │  - Validation                                        │   │
│  │  - Sanitization                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │ (JWT Auth)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (FastAPI Routes)                          │   │
│  │  - Authentication endpoints                          │   │
│  │  - Profile management endpoints                     │   │
│  │  - File upload endpoints                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Business Logic (Services)                           │   │
│  │  - UserService                                       │   │
│  │  - ImageService                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Data Access Layer (SQLAlchemy)                      │   │
│  │  - User Model                                        │   │
│  │  - Database Session Management                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Database (SQLite/PostgreSQL)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend Architecture

#### 1. Presentation Layer
- **ProfilePage Component**: Main profile display component
  - Fetches and displays user data
  - Manages edit modal state
  - Handles loading and error states
  
- **EditProfileModal Component**: Profile editing interface
  - Form management with validation
  - Image upload with preview
  - Real-time error feedback

#### 2. Utility Layer
- **API Client**: Centralized HTTP client with interceptors
  - Automatic token injection
  - Error handling and retry logic
  - Response transformation
  
- **Validation**: Client-side form validation
  - Name validation (length, characters)
  - Email validation (format)
  - Image validation (type, size)
  
- **Sanitization**: XSS prevention
  - HTML sanitization with DOMPurify
  - Text escaping for safe display

### Backend Architecture

#### 1. API Layer (FastAPI)
- **Route Handlers**: HTTP request/response handling
  - Request validation using Pydantic
  - Response serialization
  - HTTP status codes
  
- **Middleware**: Cross-cutting concerns
  - CORS configuration
  - Authentication (JWT verification)
  - Error handling

#### 2. Service Layer
- **UserService**: User management business logic
  - User creation and retrieval
  - Profile updates
  - Authorization checks
  
- **ImageService**: Image processing logic
  - File validation
  - Image optimization (resize, compress)
  - Storage management

#### 3. Data Access Layer
- **Models**: SQLAlchemy ORM models
  - User model with relationships
  - Database schema definitions
  
- **Database Session**: Connection management
  - Session lifecycle
  - Transaction handling

#### 4. Security Layer
- **Authentication**: JWT-based auth
  - Token generation
  - Token verification
  - Password hashing
  
- **Authorization**: Access control
  - User ownership verification
  - Permission checks

## Data Flow

### Profile View Flow
```
User Request → ProfilePage Component → API Client → 
Backend Route → UserService → Database → 
Response → API Client → ProfilePage → User Display
```

### Profile Update Flow
```
User Input → EditProfileModal → Validation → 
API Client → Backend Route → Authorization Check → 
UserService → Database Update → 
Response → Success Notification → Profile Reload
```

### Image Upload Flow
```
User Selects Image → Client Validation → Preview Generation → 
Form Submit → API Client → Backend Route → 
ImageService Validation → Image Processing → 
File Storage → Database Update → Response → UI Update
```

## Security Architecture

### Defense in Depth
1. **Input Validation**: Client and server-side validation
2. **Sanitization**: XSS prevention on both ends
3. **Authentication**: JWT tokens with expiration
4. **Authorization**: Resource access control
5. **File Security**: Type and size validation
6. **HTTPS**: Encrypted communication (production)

### Authentication Flow
```
1. User Login → Credentials Sent → Backend Verification
2. JWT Token Generated → Returned to Client
3. Token Stored in LocalStorage
4. Subsequent Requests → Token in Authorization Header
5. Backend Validates Token → Grants/Denies Access
```

## Database Schema

```sql
users
├── id (PRIMARY KEY, UUID)
├── name (VARCHAR, NOT NULL)
├── email (VARCHAR, UNIQUE, NOT NULL)
├── hashed_password (VARCHAR, NOT NULL)
├── profile_picture (VARCHAR, NULL)
├── join_date (DATETIME, NOT NULL)
├── last_updated (DATETIME, NOT NULL)
├── email_notifications (BOOLEAN, DEFAULT TRUE)
├── privacy_level (VARCHAR, DEFAULT 'public')
├── theme (VARCHAR, DEFAULT 'light')
└── is_active (BOOLEAN, DEFAULT TRUE)
```

### Indexes
- `email` (unique index for fast lookups)
- `id` (primary key, auto-indexed)

## Scalability Considerations

### Current Implementation
- Single server deployment
- SQLite database (development)
- Local file storage

### Production Recommendations
1. **Database**: PostgreSQL with connection pooling
2. **File Storage**: AWS S3 or similar cloud storage
3. **Caching**: Redis for session management
4. **Load Balancing**: Multiple backend instances
5. **CDN**: Static asset delivery
6. **Database Replication**: Read replicas for scaling

## Performance Optimizations

### Frontend
- Component lazy loading
- Image optimization
- Debounced form validation
- Optimistic UI updates
- React.memo for expensive components

### Backend
- Database indexing
- Connection pooling
- Async I/O with FastAPI
- Image compression
- Response caching headers

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Validation, sanitization utilities
- **Component Tests**: React components with Testing Library
- **Integration Tests**: API client interactions

### Backend Testing
- **Unit Tests**: Services, utilities
- **Integration Tests**: API endpoints
- **Database Tests**: Model operations

### E2E Testing (Recommended)
- User registration and login
- Profile viewing and editing
- Image upload
- Error handling scenarios

## Deployment Architecture

### Development
```
Frontend (Vite Dev Server:5173) → Backend (Uvicorn:8000)
```

### Production
```
Users → CDN → Frontend (Static Files) → 
API Gateway → Load Balancer → 
Backend Instances → Database Cluster
```

## Monitoring & Logging

### Recommended Tools
- **Application Monitoring**: Sentry, Datadog
- **Logging**: ELK Stack, CloudWatch
- **Performance**: New Relic, Prometheus
- **Uptime**: Pingdom, UptimeRobot

## Future Enhancements

1. **Real-time Updates**: WebSocket for live profile updates
2. **Social Features**: Follow system, activity feed
3. **Advanced Analytics**: User behavior tracking
4. **Microservices**: Separate services for auth, profiles, media
5. **GraphQL**: Alternative to REST API
6. **Mobile Apps**: React Native implementation