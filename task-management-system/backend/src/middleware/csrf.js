/**
 * CSRF protection middleware
 * Implements double-submit cookie pattern
 */

const crypto = require('crypto');
const logger = require('../utils/logger');

const CSRF_TOKEN_LENGTH = 32;
const CSRF_COOKIE_NAME = 'csrf-token';
const CSRF_HEADER_NAME = 'x-csrf-token';

/**
 * Generate CSRF token
 * @returns {string} CSRF token
 */
function generateCsrfToken() {
  return crypto.randomBytes(CSRF_TOKEN_LENGTH).toString('hex');
}

/**
 * CSRF protection middleware
 * Validates CSRF token for state-changing requests
 */
function csrfProtection(req, res, next) {
  // Skip CSRF for safe methods
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  if (safeMethods.includes(req.method)) {
    return next();
  }

  // Skip CSRF for WebSocket upgrade requests
  if (req.headers.upgrade === 'websocket') {
    return next();
  }

  // Get token from header and cookie
  const headerToken = req.headers[CSRF_HEADER_NAME];
  const cookieToken = req.cookies?.[CSRF_COOKIE_NAME];

  // Validate tokens exist
  if (!headerToken || !cookieToken) {
    logger.warn('CSRF token missing', {
      method: req.method,
      path: req.path,
      ip: req.ip,
    });

    return res.status(403).json({
      success: false,
      error: 'CSRF token missing',
      code: 'CSRF_TOKEN_MISSING',
    });
  }

  // Validate tokens match
  if (headerToken !== cookieToken) {
    logger.warn('CSRF token mismatch', {
      method: req.method,
      path: req.path,
      ip: req.ip,
    });

    return res.status(403).json({
      success: false,
      error: 'CSRF token invalid',
      code: 'CSRF_TOKEN_INVALID',
    });
  }

  next();
}

/**
 * Generate and set CSRF token
 * Should be called on login or when token is missing
 */
function setCsrfToken(req, res, next) {
  const token = generateCsrfToken();

  // Set cookie with security options
  res.cookie(CSRF_COOKIE_NAME, token, {
    httpOnly: false, // Must be readable by JavaScript for header
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  });

  // Also send in response body for initial setup
  res.locals.csrfToken = token;

  next();
}

/**
 * Get CSRF token endpoint
 * Returns current CSRF token
 */
function getCsrfToken(req, res) {
  const token = req.cookies?.[CSRF_COOKIE_NAME] || generateCsrfToken();

  // Set cookie if not present
  if (!req.cookies?.[CSRF_COOKIE_NAME]) {
    res.cookie(CSRF_COOKIE_NAME, token, {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000,
    });
  }

  res.json({
    success: true,
    csrfToken: token,
  });
}

module.exports = {
  csrfProtection,
  setCsrfToken,
  getCsrfToken,
  generateCsrfToken,
};
