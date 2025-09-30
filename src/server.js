/**
 * Server entry point
 * Starts the Express server
 */

const app = require('./app');
const config = require('./config');

const PORT = config.port;

// Start server
const server = app.listen(PORT, () => {
  console.log(`🚀 Greeting API server running on port ${PORT}`);
  console.log(`📝 Environment: ${config.env}`);
  console.log(`🌍 Health check: http://localhost:${PORT}/health`);
  console.log(`👋 Greeting endpoint: http://localhost:${PORT}/api/greeting`);
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
  console.log(`\n${signal} received. Starting graceful shutdown...`);
  
  server.close(() => {
    console.log('Server closed. Exiting process.');
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  gracefulShutdown('UNCAUGHT_EXCEPTION');
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  gracefulShutdown('UNHANDLED_REJECTION');
});

module.exports = server;