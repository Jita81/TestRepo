/**
 * Rate limiting middleware
 * Limits the number of requests per IP address
 */

const rateLimit = require('express-rate-limit');
const config = require('../config');

/**
 * Rate limiter configuration
 * Limits requests per IP address within the configured window
 */
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.max,
  message: {
    error: {
      message: 'Too many requests, please try again later.',
      retryAfter: 'See Retry-After header'
    }
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  handler: (req, res) => {
    res.status(429).json({
      error: {
        message: 'Too many requests from this IP, please try again later.',
        status: 429,
        retryAfter: res.getHeader('Retry-After')
      }
    });
  }
});

module.exports = limiter;