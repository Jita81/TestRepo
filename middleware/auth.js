const jwt = require('jsonwebtoken');
const logger = require('./logger');

/**
 * Authentication middleware to verify JWT tokens
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({
      success: false,
      error: { message: 'Access token required' }
    });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret', (err, user) => {
    if (err) {
      logger.warn('Invalid token attempt', {
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        error: err.message
      });
      
      return res.status(403).json({
        success: false,
        error: { message: 'Invalid or expired token' }
      });
    }

    req.user = user;
    next();
  });
};

/**
 * Authorization middleware to check user roles
 * @param {Array} roles - Required roles
 * @returns {Function} Middleware function
 */
const authorizeRoles = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: { message: 'Authentication required' }
      });
    }

    if (!roles.includes(req.user.role)) {
      logger.warn('Unauthorized access attempt', {
        userId: req.user.id,
        requiredRoles: roles,
        userRole: req.user.role,
        ip: req.ip
      });

      return res.status(403).json({
        success: false,
        error: { message: 'Insufficient permissions' }
      });
    }

    next();
  };
};

/**
 * Optional authentication middleware
 * Sets req.user if token is valid, but doesn't reject if no token
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const optionalAuth = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return next();
  }

  jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret', (err, user) => {
    if (!err) {
      req.user = user;
    }
    next();
  });
};

module.exports = {
  authenticateToken,
  authorizeRoles,
  optionalAuth
};