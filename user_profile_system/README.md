# User Profile System

A production-ready full-stack user profile management system with React/TypeScript frontend and FastAPI backend.

## Features

✅ **User Profile Management**
- View user profile information (name, email, profile picture, join date)
- Edit profile with real-time validation
- Upload and manage profile pictures
- Customizable user settings (notifications, privacy, theme)

✅ **Security**
- JWT-based authentication
- Password hashing with bcrypt
- Input sanitization to prevent XSS attacks
- Authorization checks for profile editing
- Secure file upload with type and size validation

✅ **User Experience**
- Beautiful, modern UI with gradient backgrounds
- Modal-based editing interface
- Real-time form validation
- Success/error notifications
- Responsive design for all screen sizes
- Optimistic updates for better UX
- Image preview before upload

✅ **Production-Ready**
- Comprehensive test coverage (unit, integration, E2E)
- Type-safe with TypeScript
- Error handling and retry logic
- Network failure handling
- Session timeout management
- Accessibility compliant (ARIA labels, keyboard navigation)

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLAlchemy (SQLite for development)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Passlib with bcrypt
- **Image Processing:** Pillow
- **Input Sanitization:** Bleach
- **Testing:** pytest, httpx

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Form Management:** React Hook Form
- **HTTP Client:** Axios
- **Sanitization:** DOMPurify
- **Notifications:** React Toastify
- **Testing:** Vitest, React Testing Library

## Project Structure

```
user_profile_system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── user_profile.py    # API endpoints
│   │   ├── core/
│   │   │   ├── config.py              # Configuration
│   │   │   └── security.py            # Security utilities
│   │   ├── db/
│   │   │   └── database.py            # Database setup
│   │   ├── models/
│   │   │   └── user.py                # Database models
│   │   ├── schemas/
│   │   │   └── user.py                # Pydantic schemas
│   │   ├── services/
│   │   │   ├── user_service.py        # Business logic
│   │   │   └── image_service.py       # Image handling
│   │   └── main.py                    # FastAPI app
│   ├── tests/                         # Backend tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfilePage.tsx        # Main profile page
│   │   │   ├── ProfilePage.css
│   │   │   ├── EditProfileModal.tsx   # Edit modal
│   │   │   └── EditProfileModal.css
│   │   ├── types/
│   │   │   └── user.ts                # TypeScript types
│   │   ├── utils/
│   │   │   ├── api.ts                 # API client
│   │   │   ├── validation.ts          # Form validation
│   │   │   └── sanitize.ts            # Input sanitization
│   │   ├── tests/                     # Frontend tests
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd user_profile_system/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
```env
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///./user_profile.db
```

6. Initialize the database:
```bash
python -c "from app.db.database import init_db; init_db()"
```

7. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
- API documentation: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd user_profile_system/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

For test coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test
```

For coverage report:
```bash
npm run test:coverage
```

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login user

### Profile Management
- `GET /api/users/me/profile` - Get current user's profile
- `GET /api/users/{user_id}/profile` - Get user profile by ID
- `PUT /api/users/{user_id}/profile` - Update user profile
- `PATCH /api/users/{user_id}/profile/picture` - Upload profile picture

### Health
- `GET /health` - Health check endpoint

## Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Get Profile

```bash
curl -X GET "http://localhost:8000/api/users/me/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Update Profile

```bash
curl -X PUT "http://localhost:8000/api/users/{user_id}/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com"
  }'
```

## Security Features

### Input Validation
- Name: 2-50 characters, alphanumeric with spaces, hyphens, underscores
- Email: Valid email format
- Password: Minimum 8 characters, must contain uppercase, lowercase, and digit
- Images: JPG, PNG, GIF only, max 5MB

### Input Sanitization
- All text inputs are sanitized using Bleach (backend) and DOMPurify (frontend)
- HTML tags are stripped or whitelisted
- XSS prevention through proper escaping

### Authentication & Authorization
- JWT-based authentication with configurable expiration
- Password hashing using bcrypt
- Authorization checks ensure users can only edit their own profiles

### File Upload Security
- File type validation (MIME type checking)
- File size limits (5MB)
- Image processing and optimization
- Secure file storage

## Error Handling

The system handles various edge cases:

- **Network Failures:** Retry mechanisms with user feedback
- **Concurrent Edits:** Optimistic updates with backend validation
- **Large Files:** Size validation before upload
- **Session Timeouts:** Automatic redirect to login
- **Missing Images:** Fallback to placeholder
- **Invalid Input:** Real-time validation with clear error messages

## Accessibility

- ARIA labels for all interactive elements
- Keyboard navigation support
- Screen reader friendly
- Error messages announced to assistive technologies
- High contrast for readability
- Focus indicators for keyboard users

## Performance Optimizations

- Image optimization (resize, compress)
- Lazy loading of components
- Debounced form validation
- Optimistic UI updates
- Efficient re-rendering with React
- Database indexing on frequently queried fields

## Deployment

### Backend Deployment

1. Set environment variables in production
2. Use a production database (PostgreSQL recommended)
3. Set `SECRET_KEY` to a strong random value
4. Configure CORS `ALLOWED_ORIGINS` for your frontend domain
5. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment

1. Build the production bundle:
```bash
npm run build
```

2. Deploy the `dist/` folder to your hosting service
3. Configure environment variables for production API URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run all tests to ensure they pass
5. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.