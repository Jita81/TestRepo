/**
 * Express application setup
 * Configures middleware and routes
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const greetingRoutes = require('./routes/greeting');
const rateLimiter = require('./middleware/rateLimiter');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

const app = express();

// Security middleware - sets various HTTP headers
app.use(helmet());

// CORS middleware - enable CORS for all origins
app.use(cors({
  origin: '*', // In production, configure specific origins
  methods: ['GET'],
  allowedHeaders: ['Content-Type'],
  exposedHeaders: ['RateLimit-Limit', 'RateLimit-Remaining', 'RateLimit-Reset']
}));

// Body parser middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting middleware
app.use(rateLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API routes
app.use('/api/greeting', greetingRoutes);

// 404 handler - must be after all routes
app.use(notFoundHandler);

// Error handling middleware - must be last
app.use(errorHandler);

module.exports = app;