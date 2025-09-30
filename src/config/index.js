/**
 * Application configuration
 * Loads environment variables and provides default values
 */

require('dotenv').config();

const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  env: process.env.NODE_ENV || 'development',
  rateLimit: {
    windowMs: (parseInt(process.env.RATE_LIMIT_WINDOW, 10) || 15) * 60 * 1000,
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS, 10) || 100
  }
};

module.exports = config;