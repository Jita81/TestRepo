/**
 * Global error handling middleware
 * Catches and formats errors for consistent API responses
 */
function errorHandler(err, req, res, next) {
  // Log error for debugging
  console.error('Error:', {
    message: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    url: req.url,
    method: req.method,
    timestamp: new Date().toISOString()
  });

  // Default error response
  let statusCode = 500;
  let errorResponse = {
    success: false,
    error: 'Internal Server Error',
    message: 'Something went wrong on the server'
  };

  // Handle specific error types
  if (err.message.includes('Database error')) {
    statusCode = 503;
    errorResponse.error = 'Database Error';
    errorResponse.message = 'Database service temporarily unavailable';
  } else if (err.message.includes('Validation')) {
    statusCode = 400;
    errorResponse.error = 'Validation Error';
    errorResponse.message = err.message;
  } else if (err.message.includes('not found')) {
    statusCode = 404;
    errorResponse.error = 'Not Found';
    errorResponse.message = err.message;
  } else if (err.name === 'ValidationError') {
    statusCode = 400;
    errorResponse.error = 'Validation Error';
    errorResponse.message = err.message;
  }

  // Include stack trace in development
  if (process.env.NODE_ENV === 'development') {
    errorResponse.stack = err.stack;
  }

  res.status(statusCode).json(errorResponse);
}

/**
 * 404 Not Found handler
 */
function notFoundHandler(req, res) {
  res.status(404).json({
    success: false,
    error: 'Not Found',
    message: `Route ${req.method} ${req.url} not found`
  });
}

module.exports = {
  errorHandler,
  notFoundHandler
};