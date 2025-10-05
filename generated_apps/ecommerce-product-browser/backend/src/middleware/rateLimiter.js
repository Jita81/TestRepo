const rateLimit = require('express-rate-limit');
const { RateLimitError } = require('./errorHandler');

/**
 * Rate limiter for general API endpoints
 */
const apiLimiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS, 10) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS, 10) || 100,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res, next) => {
    next(new RateLimitError('Too many requests from this IP, please try again later'));
  },
  skip: (req) => process.env.NODE_ENV === 'test',
});

/**
 * Stricter rate limiter for search endpoints
 */
const searchLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res, next) => {
    next(new RateLimitError('Too many search requests, please slow down'));
  },
  skip: (req) => process.env.NODE_ENV === 'test',
});

module.exports = {
  apiLimiter,
  searchLimiter,
};