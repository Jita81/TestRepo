/**
 * Rate limiting middleware using Redis
 */

const rateLimit = require('express-rate-limit');
const { rateLimiter } = require('../config/redis');
const logger = require('../utils/logger');

/**
 * Create rate limiter middleware
 * @param {Object} options - Rate limiter options
 * @returns {Function} Express middleware
 */
const createRateLimiter = (options = {}) => {
  const {
    windowMs = parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    max = parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // 100 requests
    message = 'Too many requests, please try again later',
    skipSuccessfulRequests = false,
  } = options;

  return rateLimit({
    windowMs,
    max,
    message: {
      success: false,
      error: message,
      code: 'RATE_LIMIT_EXCEEDED',
    },
    skipSuccessfulRequests,
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
      logger.warn('Rate limit exceeded', {
        ip: req.ip,
        path: req.path,
        userId: req.user?.userId,
      });
      res.status(429).json({
        success: false,
        error: message,
        code: 'RATE_LIMIT_EXCEEDED',
      });
    },
  });
};

/**
 * WebSocket rate limiter
 * @param {string} userId - User ID
 * @param {number} maxMessages - Maximum messages per minute
 * @returns {Promise<boolean>} True if limit exceeded
 */
const wsRateLimiter = async (userId, maxMessages = 60) => {
  const key = `ws_rate_limit:${userId}`;
  const windowSeconds = 60; // 1 minute window
  
  try {
    return await rateLimiter.isLimitExceeded(key, maxMessages, windowSeconds);
  } catch (error) {
    logger.error('WebSocket rate limiter error:', error);
    return false; // Fail open
  }
};

module.exports = {
  createRateLimiter,
  wsRateLimiter,
};
