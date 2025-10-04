# 🚀 Quick Start Guide

Get the Task Management System running in 5 minutes!

## Option 1: Docker (Easiest) 🐳

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Navigate to the project:**
```bash
cd task-management-system
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Wait for services to be ready** (about 30 seconds)

4. **Access the application:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:3000
- Health check: http://localhost:3000/health

5. **Create an account:**
- Click "Sign up" on the login page
- Fill in your details
- You're ready to go!

### Stop the application:
```bash
docker-compose down
```

---

## Option 2: Manual Setup 💻

### Prerequisites
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Install PostgreSQL and create database:**
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb task_management

# Ubuntu/Debian
sudo apt install postgresql
sudo -u postgres createdb task_management

# Windows
# Download from postgresql.org
```

2. **Install Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from redis.io or use WSL
```

3. **Set up backend:**
```bash
cd task-management-system/backend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Run database schema
psql -d task_management -f ../database/schema.sql

# Start server
npm run dev
```

Backend will be running at http://localhost:3000

### Frontend Setup

1. **Open a new terminal and set up frontend:**
```bash
cd task-management-system/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be running at http://localhost:3001

---

## First Steps 📝

1. **Register an account**
   - Go to http://localhost:3001
   - Click "Sign up"
   - Create your account

2. **Create a project**
   - Click "New Project"
   - Enter project name
   - Click Create

3. **Add tasks**
   - Open your project
   - Click "New Task"
   - Add task details
   - See real-time updates!

4. **Invite team members** (optional)
   - Open project settings
   - Add members by email
   - Collaborate in real-time

---

## Testing Real-Time Features 🔄

1. **Open two browser windows** side by side
2. **Log in with different accounts** (or same account)
3. **Join the same project**
4. **Create/update tasks in one window**
5. **Watch updates appear instantly** in the other window!

You'll see:
- ✅ New tasks appear immediately
- ✅ Status changes update in real-time
- ✅ Online users shown with green indicators
- ✅ Connection status in the header

---

## Common Issues 🔧

### Backend won't start

**Error: "Database connection failed"**
```bash
# Check if PostgreSQL is running
pg_isready

# Check connection in .env file
cat backend/.env
```

**Error: "Redis connection failed"**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Frontend won't connect

**Error: "Network Error"**
- Check backend is running on port 3000
- Check VITE_API_URL in frontend/.env

### WebSocket won't connect

**Error: "WebSocket connection failed"**
- Check backend logs for errors
- Verify JWT token is valid
- Check CORS settings in backend/.env

---

## Environment Variables 🔐

### Backend (.env)

Minimum required:
```env
PORT=3000
DB_NAME=task_management
DB_USER=postgres
DB_PASSWORD=postgres
REDIS_HOST=localhost
JWT_SECRET=your-secret-key-min-32-characters-long
JWT_REFRESH_SECRET=your-refresh-secret-min-32-characters
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:3000/api
VITE_WS_URL=http://localhost:3000
```

---

## Verify Installation ✅

### Check Backend

```bash
# Health check
curl http://localhost:3000/health

# Should return:
# {"status":"ok","timestamp":"...","uptime":...}
```

### Check Frontend

Open http://localhost:3001 in your browser. You should see the login page.

### Check WebSocket

1. Log in to the application
2. Open browser DevTools (F12)
3. Go to Console tab
4. Look for messages like:
   ```
   WebSocket connected: xyz123
   ```

---

## Running Tests 🧪

### Backend Tests

```bash
cd backend
npm test
```

### Check Test Coverage

```bash
cd backend
npm test -- --coverage
```

---

## Production Deployment 🚀

For production deployment, see:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Complete deployment guide
- Docker: `docker-compose -f docker-compose.prod.yml up -d`
- AWS/Heroku/DigitalOcean instructions included

---

## Next Steps 📚

- Read [README.md](./README.md) for full documentation
- Explore [API.md](./API.md) for API reference
- Check [CONTRIBUTING.md](./CONTRIBUTING.md) to contribute
- Join our community (Discord/Slack link here)

---

## Need Help? 💬

- **Documentation**: See README.md
- **Issues**: Open an issue on GitHub
- **Email**: support@example.com
- **Discord**: Join our server (link)

---

## Quick Commands Reference 📋

```bash
# Docker
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f        # View logs
docker-compose restart        # Restart services

# Backend
npm run dev                   # Start dev server
npm start                     # Start production server
npm test                      # Run tests
npm run migrate              # Run database migrations

# Frontend
npm run dev                   # Start dev server
npm run build                 # Build for production
npm run preview              # Preview production build

# Database
psql -d task_management      # Connect to database
psql -d task_management -f database/schema.sql  # Run schema
```

---

**Happy task managing! 🎉**

If you encounter any issues, please check the [troubleshooting section](./README.md#troubleshooting) in the main README.
