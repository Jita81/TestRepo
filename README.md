# Todo List Application

A full-stack, production-ready todo list application with comprehensive CRUD operations, persistent storage, and a beautiful responsive UI.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Node](https://img.shields.io/badge/node-%3E%3D14.0.0-brightgreen)
![PostgreSQL](https://img.shields.io/badge/postgresql-%3E%3D12.0-blue)

## 📋 Features

- ✅ **Create** new todo items with descriptions
- ✅ **Mark** todos as complete/incomplete
- ✅ **Delete** individual or all completed todos
- ✅ **Persistent storage** with PostgreSQL database
- ✅ **Real-time updates** with optimistic UI
- ✅ **Responsive design** that works on all devices
- ✅ **Filter todos** by all/active/completed
- ✅ **Character counter** with validation
- ✅ **Offline detection** and error handling
- ✅ **RESTful API** with comprehensive error handling
- ✅ **Rate limiting** for API protection
- ✅ **Input sanitization** to prevent XSS attacks
- ✅ **Accessible** UI with ARIA attributes
- ✅ **Comprehensive tests** for backend and frontend

## 🏗️ Architecture

```
todo-list-app/
├── backend/
│   ├── config/
│   │   └── database.js          # PostgreSQL connection pool
│   ├── controllers/
│   │   └── todoController.js    # Request handlers
│   ├── database/
│   │   ├── schema.sql           # Database schema
│   │   └── migrate.js           # Migration script
│   ├── middleware/
│   │   ├── errorHandler.js      # Global error handling
│   │   └── validators.js        # Input validation
│   ├── models/
│   │   └── Todo.js              # Todo data model
│   ├── routes/
│   │   └── todos.js             # API routes
│   └── server.js                # Express server setup
├── frontend/
│   ├── scripts/
│   │   ├── api.js               # API service layer
│   │   ├── app.js               # Main application logic
│   │   └── utils.js             # Utility functions
│   ├── styles/
│   │   └── main.css             # Responsive styles
│   └── index.html               # Main HTML page
├── tests/
│   ├── todo.test.js             # Backend API tests
│   └── frontend.test.html       # Frontend tests
├── .env.example                 # Environment variables template
├── package.json                 # Dependencies and scripts
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** >= 14.0.0
- **PostgreSQL** >= 12.0
- **npm** or **yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo-list-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Configure your `.env` file**
   ```env
   PORT=3000
   NODE_ENV=development
   
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=todolist
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   ```

5. **Create the database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE todolist;
   
   # Exit psql
   \q
   ```

6. **Run database migrations**
   ```bash
   npm run db:migrate
   ```

7. **Start the server**
   ```bash
   # Development mode (with auto-reload)
   npm run dev
   
   # Production mode
   npm start
   ```

8. **Open your browser**
   ```
   http://localhost:3000
   ```

## 📚 API Documentation

### Base URL
```
http://localhost:3000/api
```

### Endpoints

#### Get All Todos
```http
GET /api/todos
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "description": "Sample todo",
      "completed": false,
      "created_at": "2025-09-30T12:00:00.000Z",
      "updated_at": "2025-09-30T12:00:00.000Z"
    }
  ],
  "count": 1
}
```

#### Get Single Todo
```http
GET /api/todos/:id
```

#### Create Todo
```http
POST /api/todos
Content-Type: application/json

{
  "description": "New todo item"
}
```

#### Update Todo
```http
PUT /api/todos/:id
Content-Type: application/json

{
  "description": "Updated description",
  "completed": true
}
```

#### Delete Todo
```http
DELETE /api/todos/:id
```

#### Delete All Completed
```http
DELETE /api/todos/completed/all
```

### Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message"
}
```

**Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `503` - Service Unavailable (database error)

## 🧪 Testing

### Run Backend Tests
```bash
npm test
```

### Run Frontend Tests
Open `tests/frontend.test.html` in your browser.

### Test Coverage
```bash
npm test -- --coverage
```

## 🔒 Security Features

- **Input Validation**: All inputs are validated and sanitized
- **XSS Protection**: HTML escaping prevents script injection
- **Rate Limiting**: API requests are limited to prevent abuse
- **SQL Injection Prevention**: Parameterized queries used throughout
- **CORS Configuration**: Controlled cross-origin access
- **Error Handling**: Sensitive information hidden in production

## 🎨 Design Features

### Responsive Design
- Mobile-first approach
- Breakpoints at 768px and 480px
- Touch-friendly interface

### Accessibility
- ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- Focus indicators
- Reduced motion support

### User Experience
- Optimistic UI updates
- Loading states
- Error messages
- Character counter
- Confirmation dialogs
- Empty states

## 📊 Database Schema

```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    description VARCHAR(500) NOT NULL CHECK (length(description) > 0),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
CREATE INDEX idx_todos_completed ON todos(completed);
```

## 🛠️ Development

### Project Structure
- **backend/**: Server-side code
  - **config/**: Configuration files
  - **controllers/**: Business logic
  - **database/**: Schema and migrations
  - **middleware/**: Express middleware
  - **models/**: Data models
  - **routes/**: API routes

- **frontend/**: Client-side code
  - **scripts/**: JavaScript modules
  - **styles/**: CSS files

### Code Quality
- Modular architecture
- Clean separation of concerns
- Comprehensive error handling
- Input validation at all layers
- Consistent naming conventions
- Well-documented code

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `NODE_ENV` | Environment | development |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | todolist |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | - |
| `CORS_ORIGIN` | CORS allowed origin | * |
| `API_RATE_LIMIT_WINDOW_MS` | Rate limit window | 900000 |
| `API_RATE_LIMIT_MAX_REQUESTS` | Max requests per window | 100 |

## 🚢 Deployment

### Production Checklist

1. **Environment Setup**
   - [ ] Set `NODE_ENV=production`
   - [ ] Configure production database
   - [ ] Set secure CORS origin
   - [ ] Update rate limit settings

2. **Security**
   - [ ] Use strong database password
   - [ ] Enable SSL/TLS
   - [ ] Configure firewall rules
   - [ ] Set up monitoring

3. **Database**
   - [ ] Run migrations
   - [ ] Set up backups
   - [ ] Configure connection pooling

4. **Server**
   - [ ] Use process manager (PM2)
   - [ ] Set up reverse proxy (nginx)
   - [ ] Enable HTTPS
   - [ ] Configure logging

### Deployment Platforms

#### Heroku
```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set NODE_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run npm run db:migrate
```

#### Docker
```bash
# Build image
docker build -t todo-app .

# Run container
docker run -p 3000:3000 --env-file .env todo-app
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with Express.js and PostgreSQL
- Styled with modern CSS
- Icons from Feather Icons
- Tested with Jest and Supertest

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the test files for examples

---

**Happy Todo-ing! 🎉**