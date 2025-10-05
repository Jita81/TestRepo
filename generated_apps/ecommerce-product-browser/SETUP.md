# Setup Guide

This guide will walk you through setting up the E-Commerce Product Browser application from scratch.

## Prerequisites Installation

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Install Elasticsearch (optional)
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full
brew services start elasticsearch-full
```

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Elasticsearch (optional)
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt update
sudo apt install elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

### Windows

1. **Node.js**: Download and install from https://nodejs.org/
2. **PostgreSQL**: Download from https://www.postgresql.org/download/windows/
3. **Redis**: Download from https://redis.io/download or use WSL2
4. **Elasticsearch**: Download from https://www.elastic.co/downloads/elasticsearch

## Step-by-Step Setup

### 1. Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce_db;

# Create user (optional)
CREATE USER ecommerce_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;

# Exit
\q
```

### 2. Project Setup

```bash
# Navigate to project directory
cd ecommerce-product-browser

# Install backend dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Copy environment file
cp .env.example .env
```

### 3. Configure Environment

Edit `.env` file with your configuration:

```env
# Update these values based on your setup
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379

ELASTICSEARCH_NODE=http://localhost:9200
```

### 4. Seed Database

```bash
# Run seed script
node backend/src/scripts/seed.js

# You should see output like:
# INFO: Database initialized successfully
# INFO: Created category: Electronics
# INFO: Created product: Premium Wireless Headphones
# ...
# INFO: Database seeding completed: 15 products, 10 categories
```

### 5. Start Application

```bash
# Option 1: Start both frontend and backend together
npm run dev

# Option 2: Start separately
# Terminal 1 (Backend)
npm run dev:backend

# Terminal 2 (Frontend)
npm run dev:frontend
```

### 6. Verify Installation

1. **Backend Health Check**
   ```bash
   curl http://localhost:3001/health
   # Should return: {"status":"ok","timestamp":"..."}
   ```

2. **Check Products API**
   ```bash
   curl http://localhost:3001/api/v1/products?limit=5
   # Should return JSON with products
   ```

3. **Open Frontend**
   - Navigate to http://localhost:3000
   - You should see the product listing page

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Seed database
npm run db:seed

# Start application
npm run dev
```

## Testing the Setup

### Test Search Functionality

1. Open http://localhost:3000
2. Type "laptop" in the search bar
3. You should see autocomplete suggestions
4. Press Enter to see search results

### Test Filtering

1. Select a category from the sidebar
2. Adjust the price range
3. Toggle "In Stock Only"
4. Products should update accordingly

### Test Sorting

1. Use the "Sort By" dropdown
2. Try different sorting options
3. Products should reorder accordingly

### Test Infinite Scroll

1. Scroll to the bottom of the page
2. More products should load automatically
3. Continue scrolling to load all products

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready

# Check PostgreSQL logs
# macOS: /usr/local/var/log/postgresql@15.log
# Linux: /var/log/postgresql/postgresql-15-main.log

# Restart PostgreSQL
# macOS: brew services restart postgresql@15
# Linux: sudo systemctl restart postgresql
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check Redis logs
# macOS: /usr/local/var/log/redis.log
# Linux: /var/log/redis/redis-server.log

# Restart Redis
# macOS: brew services restart redis
# Linux: sudo systemctl restart redis-server
```

### Elasticsearch Issues

```bash
# Check if Elasticsearch is running
curl http://localhost:9200
# Should return cluster information

# Check Elasticsearch logs
# macOS: /usr/local/var/log/elasticsearch.log
# Linux: /var/log/elasticsearch/

# Restart Elasticsearch
# macOS: brew services restart elasticsearch-full
# Linux: sudo systemctl restart elasticsearch
```

### Port Conflicts

If ports 3000, 3001, 5432, 6379, or 9200 are already in use:

```bash
# Find process using a port (macOS/Linux)
lsof -i :3001

# Kill the process
kill -9 <PID>

# Or change the port in .env
PORT=3002
```

### Module Not Found Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules frontend/node_modules
npm install
cd frontend && npm install && cd ..
```

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Frontend: Changes to React files auto-refresh
- Backend: Nodemon restarts server on changes

### Debugging

```bash
# Backend debugging
NODE_ENV=development npm run dev:backend

# Frontend debugging
# Open Chrome DevTools (F12) in browser
# Use React Developer Tools extension
```

### Database Management

```bash
# Connect to database
psql -U postgres -d ecommerce_db

# List tables
\dt

# View products
SELECT id, name, price, category FROM products LIMIT 10;

# View categories
SELECT id, name, slug, level FROM categories;
```

### Clear Cache

```bash
# Connect to Redis
redis-cli

# Clear all cache
FLUSHALL

# Exit
exit
```

## Next Steps

1. **Customize Products**: Edit `backend/src/utils/seedData.js` to add your own products
2. **Add Authentication**: Implement user authentication for admin features
3. **Add Shopping Cart**: Implement cart functionality
4. **Deploy**: Follow deployment guide in README.md
5. **Configure CDN**: Set up image CDN for production

## Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review [API Documentation](#api-documentation) for endpoint details
- Check logs in `logs/app.log` for backend issues
- Use browser console for frontend debugging

## Maintenance

### Update Dependencies

```bash
# Check outdated packages
npm outdated

# Update all packages
npm update

# Update frontend packages
cd frontend && npm update && cd ..
```

### Backup Database

```bash
# Create backup
pg_dump -U postgres ecommerce_db > backup.sql

# Restore backup
psql -U postgres ecommerce_db < backup.sql
```

### Monitor Performance

```bash
# Check Redis memory
redis-cli INFO memory

# Check Elasticsearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Check database connections
psql -U postgres -d ecommerce_db -c "SELECT count(*) FROM pg_stat_activity;"
```

---

**Setup complete! Start building your e-commerce platform! 🚀**