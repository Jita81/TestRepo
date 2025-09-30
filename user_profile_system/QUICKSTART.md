# Quick Start Guide

Get the User Profile System up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git

## Option 1: Manual Setup (Recommended for Development)

### Step 1: Clone and Navigate
```bash
cd user_profile_system
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the backend server
python run.py
```

Backend will be running at: http://localhost:8000
API docs: http://localhost:8000/api/docs

### Step 3: Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run the frontend
npm run dev
```

Frontend will be running at: http://localhost:5173

## Option 2: Docker Setup (Recommended for Production)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## First Steps

### 1. Register a User

**Via UI:**
1. Open http://localhost:5173
2. You'll need to implement a registration page, or use the API directly

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from the response.

### 2. View Profile

```bash
# Replace YOUR_TOKEN with the token from registration
curl -X GET "http://localhost:8000/api/users/me/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Update Profile

```bash
curl -X PUT "http://localhost:8000/api/users/{USER_ID}/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com"
  }'
```

### 4. Upload Profile Picture

```bash
curl -X PATCH "http://localhost:8000/api/users/{USER_ID}/profile/picture" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

## Testing the Application

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Issues
```bash
# Delete and recreate database
cd backend
rm user_profile.db
python run.py  # Will create new database
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### CORS Errors
Make sure backend `.env` has:
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
3. Review [SECURITY.md](SECURITY.md) for security features
4. See [TESTING.md](TESTING.md) for testing guidelines

## Development Workflow

1. **Make Changes**: Edit code in `backend/` or `frontend/`
2. **Auto-Reload**: Both servers support hot reload
3. **Test**: Run tests after changes
4. **Commit**: Commit with clear messages

## Production Deployment

See the main README.md for production deployment instructions.

## Getting Help

- Check the documentation in the repo
- Review API docs at http://localhost:8000/api/docs
- Check existing tests for usage examples

## Quick Commands Reference

```bash
# Backend
cd backend
source venv/bin/activate  # Activate venv
python run.py              # Run server
pytest tests/              # Run tests
uvicorn app.main:app --reload  # Alternative run

# Frontend
cd frontend
npm run dev                # Run dev server
npm run build              # Build for production
npm run test               # Run tests
npm run lint               # Lint code

# Docker
docker-compose up          # Start all services
docker-compose down        # Stop all services
docker-compose logs -f     # View logs
```

Enjoy building with the User Profile System! 🚀