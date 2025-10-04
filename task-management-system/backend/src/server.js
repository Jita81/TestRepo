/**
 * Main server file - Express + Socket.io server with real-time features
 */

require('dotenv').config();
require('express-async-errors'); // Automatically handle async errors
const express = require('express');
const http = require('http');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const logger = require('./utils/logger');
const { initRedis, closeRedis } = require('./config/redis');
const { close: closeDb } = require('./config/database');
const { initSocketServer } = require('./socket/socketServer');
const { errorHandler, notFound } = require('./middleware/errorHandler');
const { createRateLimiter } = require('./middleware/rateLimiter');

// Import routes
const authRoutes = require('./routes/auth.routes');
const projectRoutes = require('./routes/projects.routes');
const taskRoutes = require('./routes/tasks.routes');
const commentRoutes = require('./routes/comments.routes');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

// Create Express app
const app = express();
const httpServer = http.createServer(app);

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for WebSocket
  crossOriginEmbedderPolicy: false,
}));

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3001',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression middleware
app.use(compression());

// Request logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('user-agent'),
    userId: req.user?.userId,
  });
  next();
});

// Rate limiting for API routes
const apiRateLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests from this IP, please try again later',
});

app.use('/api', apiRateLimiter);

// Stricter rate limiting for auth routes
const authRateLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // 10 requests per window
  message: 'Too many authentication attempts, please try again later',
  skipSuccessfulRequests: true,
});

app.use('/api/auth/login', authRateLimiter);
app.use('/api/auth/register', authRateLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
  });
});

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/tasks', taskRoutes);
app.use('/api/comments', commentRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'Task Management API',
    version: '1.0.0',
    description: 'RESTful API with real-time WebSocket updates',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      projects: '/api/projects',
      tasks: '/api/tasks',
      comments: '/api/comments',
    },
  });
});

// 404 handler
app.use(notFound);

// Error handler (must be last)
app.use(errorHandler);

/**
 * Initialize server and connections
 */
const startServer = async () => {
  try {
    // Initialize Redis
    logger.info('Initializing Redis...');
    await initRedis();

    // Initialize Socket.io
    logger.info('Initializing Socket.io...');
    const io = initSocketServer(httpServer);

    // Store io instance globally for use in routes if needed
    app.set('io', io);

    // Start HTTP server
    httpServer.listen(PORT, HOST, () => {
      logger.info(`Server started successfully!`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
      logger.info(`HTTP Server: http://${HOST}:${PORT}`);
      logger.info(`WebSocket Server: ws://${HOST}:${PORT}`);
      logger.info(`API Docs: http://${HOST}:${PORT}/`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

/**
 * Graceful shutdown
 */
const shutdown = async (signal) => {
  logger.info(`${signal} received, shutting down gracefully...`);

  // Close HTTP server
  httpServer.close(async () => {
    logger.info('HTTP server closed');

    try {
      // Close Redis connections
      await closeRedis();

      // Close database connections
      await closeDb();

      logger.info('All connections closed');
      process.exit(0);
    } catch (error) {
      logger.error('Error during shutdown:', error);
      process.exit(1);
    }
  });

  // Force shutdown after 30 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
};

// Handle shutdown signals
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  shutdown('UNCAUGHT_EXCEPTION');
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  shutdown('UNHANDLED_REJECTION');
});

// Start the server
startServer();

module.exports = app;
