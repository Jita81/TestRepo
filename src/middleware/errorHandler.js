/**
 * Global error handling middleware
 * Catches and formats errors for consistent API responses
 */

const config = require('../config');

/**
 * Error handler middleware
 * Catches all errors and returns a consistent error response
 * 
 * @param {Error} err - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const errorHandler = (err, req, res, next) => {
  // Default error status and message
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  // Log error in development
  if (config.env === 'development') {
    console.error('Error:', {
      message: err.message,
      stack: err.stack,
      url: req.url,
      method: req.method
    });
  }

  // Don't expose internal errors in production
  const errorResponse = {
    error: {
      message: status === 500 && config.env === 'production' 
        ? 'Internal Server Error' 
        : message,
      status,
      timestamp: new Date().toISOString()
    }
  };

  // Add stack trace only in development
  if (config.env === 'development' && err.stack) {
    errorResponse.error.stack = err.stack;
  }

  res.status(status).json(errorResponse);
};

/**
 * 404 Not Found handler
 */
const notFoundHandler = (req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found',
      status: 404,
      path: req.url
    }
  });
};

module.exports = {
  errorHandler,
  notFoundHandler
};