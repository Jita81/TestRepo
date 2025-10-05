# E-Commerce Product Browsing and Search System

A full-stack e-commerce product browsing system with advanced search capabilities, real-time filtering, and a modern responsive UI. Built with React, Redux, Node.js, Express, PostgreSQL, Elasticsearch, and Redis.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Node](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen.svg)
![React](https://img.shields.io/badge/react-18.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### Product Browsing
- ✅ Paginated product listing with 20 items per page
- ✅ Infinite scroll for seamless browsing experience
- ✅ Responsive grid layout (1-4 columns based on screen size)
- ✅ Image lazy loading for optimal performance
- ✅ Product availability badges (In Stock, Low Stock, Out of Stock)

### Search & Filtering
- ✅ Full-text search with Elasticsearch
- ✅ Auto-complete suggestions (< 300ms response time)
- ✅ Search term highlighting in results
- ✅ Advanced filters (price range, category, availability)
- ✅ Multiple sorting options (price, name, popularity, newest)
- ✅ Real-time filter updates without page reload

### Navigation
- ✅ Category hierarchy with nested navigation
- ✅ Breadcrumb navigation for easy orientation
- ✅ Category-based product browsing
- ✅ Quick view modal for product details

### Performance
- ✅ Redis caching for frequently accessed data
- ✅ Optimized database queries with indexes
- ✅ API response caching (5-10 minutes)
- ✅ Intersection Observer for infinite scroll
- ✅ Image lazy loading with placeholders

### Developer Experience
- ✅ Comprehensive error handling
- ✅ API rate limiting
- ✅ Request validation with Yup
- ✅ Structured logging with Winston
- ✅ Unit and integration tests
- ✅ Docker support for easy setup

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Frontend Components](#frontend-components)
- [Testing](#testing)
- [Deployment](#deployment)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- **Node.js** >= 16.0.0
- **PostgreSQL** >= 13
- **Redis** >= 6.0
- **Elasticsearch** >= 8.0 (optional but recommended)
- **npm** or **yarn**

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd ecommerce-product-browser
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This will start PostgreSQL, Redis, and Elasticsearch.

3. **Install dependencies**
   ```bash
   # Backend dependencies
   npm install

   # Frontend dependencies
   cd frontend && npm install && cd ..
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations and seed**
   ```bash
   npm run db:seed
   # or
   node backend/src/scripts/seed.js
   ```

6. **Start the application**
   ```bash
   # Development mode (both frontend and backend)
   npm run dev

   # Or start separately:
   # Backend: npm run dev:backend
   # Frontend: npm run dev:frontend
   ```

7. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - Elasticsearch: http://localhost:9200

### Option 2: Manual Setup

1. **Install and start PostgreSQL**
   ```bash
   # Create database
   createdb ecommerce_db
   ```

2. **Install and start Redis**
   ```bash
   redis-server
   ```

3. **Install and start Elasticsearch** (optional)
   ```bash
   # Download and run Elasticsearch 8.x
   # Or skip this step to run without search features
   ```

4. **Follow steps 3-7 from Option 1**

## 📁 Project Structure

```
ecommerce-product-browser/
├── backend/
│   ├── src/
│   │   ├── config/         # Configuration files (DB, Redis, ES)
│   │   ├── controllers/    # Route controllers
│   │   ├── middleware/     # Express middleware
│   │   ├── models/         # Sequelize models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities and helpers
│   │   ├── scripts/        # Database scripts
│   │   └── server.js       # Express app entry point
│   └── tests/              # Backend tests
├── frontend/
│   ├── public/             # Static files
│   └── src/
│       ├── components/     # React components
│       │   ├── common/     # Reusable components
│       │   ├── filters/    # Filter components
│       │   ├── layout/     # Layout components
│       │   ├── products/   # Product components
│       │   └── search/     # Search components
│       ├── pages/          # Page components
│       ├── services/       # API services
│       ├── store/          # Redux store
│       │   └── slices/     # Redux slices
│       ├── App.js          # Main app component
│       └── index.js        # Entry point
├── docker-compose.yml      # Docker services
├── package.json            # Root package.json
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Server
NODE_ENV=development
PORT=3001

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=3600

# Elasticsearch
ELASTICSEARCH_NODE=http://localhost:9200

# API
CORS_ORIGIN=http://localhost:3000
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

## 📚 API Documentation

### Products API

#### Get Products
```http
GET /api/v1/products
```

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 20, max: 100)
- `sort` (string): Sort order (newest, price_asc, price_desc, name_asc, name_desc, popularity)
- `category` (string): Filter by category
- `minPrice` (number): Minimum price filter
- `maxPrice` (number): Maximum price filter
- `search` (string): Search query
- `inStock` (boolean): Show only in-stock items

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Product Name",
      "description": "Product description",
      "price": 99.99,
      "category": "Electronics",
      "categoryPath": ["Electronics", "Laptops"],
      "images": {
        "thumbnail": "url",
        "main": ["url1", "url2"]
      },
      "inventory": {
        "status": "IN_STOCK",
        "quantity": 50
      },
      "metadata": {
        "createdAt": "2024-01-01T00:00:00.000Z",
        "popularity": 100
      }
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "totalPages": 5
  }
}
```

#### Get Product by ID
```http
GET /api/v1/products/:id
```

### Search API

#### Search Products
```http
GET /api/v1/search
```

**Query Parameters:**
- `query` (string, required): Search query
- `limit` (number): Results limit (default: 10)
- `offset` (number): Results offset (default: 0)
- `category` (string): Filter by category

**Response:**
```json
{
  "results": [...],
  "total": 50,
  "took": 15
}
```

#### Get Suggestions
```http
GET /api/v1/search/suggestions?query=laptop
```

**Response:**
```json
{
  "suggestions": [
    "laptop pro",
    "laptop stand",
    "laptop bag"
  ]
}
```

### Categories API

#### Get Categories
```http
GET /api/v1/categories
```

#### Get Category Tree
```http
GET /api/v1/categories/tree
```

#### Get Breadcrumb
```http
GET /api/v1/categories/:id/breadcrumb
```

## 🎨 Frontend Components

### Key Components

#### ProductGrid
Displays products in a responsive grid with infinite scroll.

```jsx
import ProductGrid from './components/products/ProductGrid';

<ProductGrid />
```

#### ProductCard
Individual product card with lazy-loaded images and quick view.

```jsx
import ProductCard from './components/products/ProductCard';

<ProductCard product={product} onQuickView={handleQuickView} />
```

#### SearchBar
Search input with auto-complete suggestions.

```jsx
import SearchBar from './components/search/SearchBar';

<SearchBar />
```

#### FilterPanel
Advanced filtering interface for products.

```jsx
import FilterPanel from './components/filters/FilterPanel';

<FilterPanel categories={categories} onApplyFilters={handleApply} />
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- backend/tests/services/ProductService.test.js

# Watch mode
npm run test:watch
```

### Frontend Tests

```bash
# Run frontend tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## 🚀 Deployment

### Production Build

```bash
# Build frontend
npm run build:frontend

# Start production server
NODE_ENV=production npm start
```

### Environment Configuration

For production, ensure you set:
- `NODE_ENV=production`
- Strong `JWT_SECRET`
- Proper database credentials
- Redis and Elasticsearch endpoints
- CORS origins

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ⚡ Performance Optimization

### Caching Strategy
- **Product listings**: 10 minutes
- **Search results**: 5 minutes
- **Category tree**: 1 hour
- **Individual products**: 1 hour

### Database Optimization
- Indexes on frequently queried fields
- Connection pooling (max 10 connections)
- Optimized query patterns

### Frontend Optimization
- Image lazy loading with Intersection Observer
- Infinite scroll for reduced initial load
- Component code splitting
- Redux for efficient state management

## 🐛 Troubleshooting

### Common Issues

**Issue: Cannot connect to database**
```bash
# Check if PostgreSQL is running
pg_isready

# Check connection settings in .env
```

**Issue: Elasticsearch not available**
The app will run without Elasticsearch, but search features will be limited to basic SQL queries.

**Issue: Redis connection failed**
The app will run without Redis, but performance may be impacted due to lack of caching.

**Issue: Port already in use**
```bash
# Change PORT in .env file
PORT=3002
```

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the [Troubleshooting](#troubleshooting) section
- Review the API documentation

---

**Built with ❤️ using React, Redux, Node.js, Express, PostgreSQL, Elasticsearch, and Redis**