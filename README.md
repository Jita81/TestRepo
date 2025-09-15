# Node.js Web Application Starter 🚀

A complete, production-ready Node.js web application starter template with Express.js, authentication, modern UI, and comprehensive API endpoints.

## ✨ Features

### Backend
- **Express.js** server with comprehensive middleware
- **JWT Authentication** with registration, login, and role-based authorization
- **RESTful API** with full CRUD operations
- **Security** with Helmet, CORS, and rate limiting
- **Error Handling** with centralized error management
- **Logging** with custom logger and file output
- **Validation** using express-validator
- **Environment Configuration** with dotenv

### Frontend
- **Modern HTML5** with semantic structure
- **CSS3** with custom properties and responsive design
- **Vanilla JavaScript** with ES6+ features
- **SPA Navigation** with dynamic content loading
- **Authentication UI** with login/register modals
- **Toast Notifications** for user feedback
- **Loading States** and error handling
- **Mobile Responsive** design

### Security Features
- JWT token-based authentication
- Password hashing with bcryptjs
- Rate limiting to prevent abuse
- CORS configuration
- Helmet for security headers
- Input validation and sanitization
- XSS protection

## 📁 Project Structure

```
nodejs-web-starter/
├── middleware/              # Custom middleware
│   ├── auth.js             # Authentication middleware
│   ├── errorHandler.js     # Global error handler
│   └── logger.js           # Logging utility
├── routes/                 # API routes
│   ├── api.js             # Main API endpoints
│   └── auth.js            # Authentication routes
├── public/                # Frontend assets
│   ├── css/
│   │   └── styles.css     # Main stylesheet
│   ├── js/
│   │   ├── app.js         # Main application logic
│   │   ├── auth.js        # Authentication handling
│   │   └── api.js         # API communication
│   └── index.html         # Main HTML file
├── logs/                  # Application logs (auto-created)
├── server.js             # Main server file
├── package.json          # Dependencies and scripts
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16.0.0 or higher)
- **npm** (v8.0.0 or higher)

### Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration.

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser** and visit `http://localhost:3000`

### Production Deployment

1. **Set environment to production**:
   ```bash
   export NODE_ENV=production
   ```

2. **Start the server**:
   ```bash
   npm start
   ```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment (development/production) | `development` |
| `PORT` | Server port | `3000` |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `JWT_EXPIRES_IN` | Token expiration time | `24h` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

### Default Users

The application comes with two default users for testing:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | `admin` |
| `user` | `admin123` | `user` |

**⚠️ Important**: Change these default passwords in production!

## 📚 API Documentation

### Authentication Endpoints

#### POST `/auth/register`
Register a new user.

**Request Body:**
```json
{
  "username": "string (3-30 chars)",
  "email": "string (valid email)",
  "password": "string (min 6 chars, must contain uppercase, lowercase, number)"
}
```

#### POST `/auth/login`
Login with username and password.

#### GET `/auth/profile`
Get current user profile (requires authentication).

#### PUT `/auth/profile`
Update user profile (requires authentication).

#### POST `/auth/logout`
Logout user (client-side token removal).

### Items API

#### GET `/api/items`
Get all items with pagination and search.

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 10)
- `search` (string): Search query

#### POST `/api/items`
Create new item (requires authentication).

#### PUT `/api/items/:id`
Update item (requires authentication).

#### DELETE `/api/items/:id`
Delete item (requires authentication and admin/moderator role).

### Statistics API

#### GET `/api/stats`
Get application statistics (requires authentication).

### Health Check

#### GET `/health`
Server health check endpoint.

## 🎨 Frontend Usage

### Navigation

The application uses single-page navigation with the following sections:

- **Home**: Welcome page with feature overview
- **Dashboard**: Statistics and overview (requires authentication)
- **Items**: Items management with CRUD operations
- **Profile**: User profile management (requires authentication)

### Authentication Flow

1. Users can register or login using the modals
2. JWT tokens are stored in localStorage
3. Authenticated users see additional navigation options
4. Tokens are automatically included in API requests
5. Token expiration is handled automatically

## 🛠️ Development

### Available Scripts

- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests (Jest)
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues

## 🔒 Security Best Practices

### Implemented Security Measures

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Using bcryptjs with salt rounds
- **Rate Limiting**: Prevents brute force attacks
- **CORS Protection**: Configured for specific origins
- **Helmet**: Security headers for common vulnerabilities
- **Input Validation**: Server-side validation for all inputs
- **XSS Protection**: HTML escaping in frontend

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Node.js and modern web technologies**