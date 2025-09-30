# Quick Start Guide

Get your Todo List application up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Node.js 14+ installed (`node --version`)
- [ ] PostgreSQL 12+ installed (`psql --version`)
- [ ] Git installed (optional)

## Installation Steps

### 1. Install Dependencies

```bash
npm install
```

**Expected output:** Dependencies installed successfully

### 2. Set Up Database

```bash
# Start PostgreSQL (if not running)
# On macOS with Homebrew:
brew services start postgresql

# On Linux:
sudo systemctl start postgresql

# On Windows:
# Start PostgreSQL from Services or pgAdmin

# Create database
psql -U postgres -c "CREATE DATABASE todolist;"
```

### 3. Configure Environment

The `.env` file is already created with default settings. For custom configuration:

```bash
# Edit .env file
nano .env
```

**Default settings work for most local setups!**

### 4. Run Database Migrations

```bash
npm run db:migrate
```

**Expected output:** ✓ Database migrations completed successfully

### 5. Start the Application

```bash
npm start
```

**Expected output:**
```
╔═══════════════════════════════════════╗
║   Todo List API Server Running        ║
╠═══════════════════════════════════════╣
║   Port:        3000                   ║
║   Environment: development            ║
║   Time:        [current time]         ║
╚═══════════════════════════════════════╝
```

### 6. Open Your Browser

Navigate to: **http://localhost:3000**

🎉 **You're all set!**

## Quick Test

1. Add a todo: Type "My first todo" and click Add
2. Mark as complete: Click the checkbox
3. Delete: Click the trash icon
4. Refresh page: Your todos persist!

## Troubleshooting

### Port 3000 is already in use

```bash
# Change port in .env
PORT=3001
```

### Database connection error

```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check credentials in .env match your PostgreSQL setup
```

### Dependencies not installing

```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [API Documentation](README.md#api-documentation)
- Run tests: `npm test`

## Need Help?

- Check existing issues on GitHub
- Review the [Contributing Guide](CONTRIBUTING.md)
- Open a new issue with the "question" label

---

**Happy coding! 🚀**