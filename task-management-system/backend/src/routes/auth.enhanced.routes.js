/**
 * Enhanced authentication routes with email verification and password reset
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const crypto = require('crypto');
const User = require('../models/User');
const { query } = require('../config/database');
const { generateTokens, verifyAccessToken, verifyRefreshToken } = require('../utils/jwt');
const { authenticateToken } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');
const { validateRegistrationData, validatePassword } = require('../utils/validation');
const { 
  sendVerificationEmail, 
  sendPasswordResetEmail,
  sendWelcomeEmail,
  sendPasswordChangedEmail 
} = require('../services/email.service');
const { setCsrfToken } = require('../middleware/csrf');
const logger = require('../utils/logger');

// Rate limiting tracking
const loginAttempts = new Map();

// Validation schemas
const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  username: Joi.string().alphanum().min(3).max(30).required(),
  password: Joi.string().min(8).required(),
  firstName: Joi.string().min(1).max(100).optional(),
  lastName: Joi.string().min(1).max(100).optional(),
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required(),
  rememberMe: Joi.boolean().optional(),
});

const resetPasswordRequestSchema = Joi.object({
  email: Joi.string().email().required(),
});

const resetPasswordSchema = Joi.object({
  token: Joi.string().required(),
  password: Joi.string().min(8).required(),
});

/**
 * Check rate limiting for login attempts
 * @param {string} email - User email
 * @returns {boolean} Is rate limited
 */
function isRateLimited(email) {
  const attempts = loginAttempts.get(email) || { count: 0, resetAt: Date.now() + 15 * 60 * 1000 };
  
  // Reset if window expired
  if (Date.now() > attempts.resetAt) {
    loginAttempts.delete(email);
    return false;
  }
  
  return attempts.count >= 5;
}

/**
 * Record login attempt
 * @param {string} email - User email
 */
function recordLoginAttempt(email) {
  const attempts = loginAttempts.get(email) || { count: 0, resetAt: Date.now() + 15 * 60 * 1000 };
  attempts.count++;
  loginAttempts.set(email, attempts);
}

/**
 * @route   POST /api/auth/register
 * @desc    Register a new user with email verification
 * @access  Public
 */
router.post('/register', async (req, res, next) => {
  try {
    // Validate input with enhanced validation
    const validation = validateRegistrationData(req.body);
    if (!validation.isValid) {
      throw new AppError(
        Object.values(validation.errors).join(', '),
        400,
        'VALIDATION_ERROR'
      );
    }

    const { email, username, password, firstName, lastName } = req.body;

    // Check if user already exists
    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      throw new AppError('Email already registered', 400, 'EMAIL_EXISTS');
    }

    const existingUsername = await User.findByUsername(username);
    if (existingUsername) {
      throw new AppError('Username already taken', 400, 'USERNAME_EXISTS');
    }

    // Generate verification token
    const verificationToken = crypto.randomBytes(32).toString('hex');
    const verificationExpires = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

    // Create user (not verified yet)
    const user = await User.create({
      email,
      username,
      password,
      firstName,
      lastName,
      verificationToken,
      verificationExpires,
    });

    // Send verification email
    try {
      await sendVerificationEmail(email, verificationToken);
    } catch (emailError) {
      logger.error('Failed to send verification email', emailError);
      // Don't fail registration if email fails
    }

    logger.info(`User registered: ${user.id}`, { email, username });

    res.status(201).json({
      success: true,
      message: 'Registration successful. Please check your email to verify your account.',
      data: {
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          isVerified: false,
        },
        passwordStrength: validation.passwordStrength,
      },
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/auth/verify-email/:token
 * @desc    Verify email address
 * @access  Public
 */
router.get('/verify-email/:token', async (req, res, next) => {
  try {
    const { token } = req.params;

    // Find user with valid verification token
    const result = await query(
      `SELECT id, email, username, verification_token_expires 
       FROM users 
       WHERE verification_token = $1 AND is_verified = false`,
      [token]
    );

    if (result.rows.length === 0) {
      throw new AppError('Invalid or expired verification token', 400, 'INVALID_TOKEN');
    }

    const user = result.rows[0];

    // Check if token expired
    if (new Date() > new Date(user.verification_token_expires)) {
      throw new AppError('Verification token has expired', 400, 'TOKEN_EXPIRED');
    }

    // Verify user
    await query(
      `UPDATE users 
       SET is_verified = true, 
           verification_token = NULL, 
           verification_token_expires = NULL,
           is_active = true
       WHERE id = $1`,
      [user.id]
    );

    // Send welcome email
    try {
      await sendWelcomeEmail(user.email, user.username);
    } catch (emailError) {
      logger.error('Failed to send welcome email', emailError);
    }

    logger.info(`Email verified: ${user.id}`);

    res.json({
      success: true,
      message: 'Email verified successfully. You can now log in.',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/resend-verification
 * @desc    Resend verification email
 * @access  Public
 */
router.post('/resend-verification', async (req, res, next) => {
  try {
    const { email } = req.body;

    if (!email) {
      throw new AppError('Email is required', 400, 'VALIDATION_ERROR');
    }

    // Find unverified user
    const result = await query(
      'SELECT id, email, username FROM users WHERE email = $1 AND is_verified = false',
      [email]
    );

    if (result.rows.length === 0) {
      // Don't reveal if email exists
      return res.json({
        success: true,
        message: 'If an unverified account exists, a verification email has been sent.',
      });
    }

    const user = result.rows[0];

    // Generate new verification token
    const verificationToken = crypto.randomBytes(32).toString('hex');
    const verificationExpires = new Date(Date.now() + 24 * 60 * 60 * 1000);

    await query(
      `UPDATE users 
       SET verification_token = $1, verification_token_expires = $2 
       WHERE id = $3`,
      [verificationToken, verificationExpires, user.id]
    );

    // Send verification email
    await sendVerificationEmail(email, verificationToken);

    res.json({
      success: true,
      message: 'Verification email sent.',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/login
 * @desc    Login user with enhanced security
 * @access  Public
 */
router.post('/login', setCsrfToken, async (req, res, next) => {
  try {
    // Validate input
    const { error, value } = loginSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const { email, password, rememberMe = false } = value;

    // Check rate limiting
    if (isRateLimited(email)) {
      throw new AppError(
        'Too many login attempts. Please try again in 15 minutes.',
        429,
        'RATE_LIMIT_EXCEEDED'
      );
    }

    // Find user
    const user = await User.findByEmail(email);
    if (!user) {
      recordLoginAttempt(email);
      throw new AppError('Invalid credentials', 401, 'INVALID_CREDENTIALS');
    }

    // Check if account is locked
    if (user.locked_until && new Date() < new Date(user.locked_until)) {
      throw new AppError('Account is temporarily locked. Please try again later.', 403, 'ACCOUNT_LOCKED');
    }

    // Check if user is active
    if (!user.is_active) {
      throw new AppError('Account is disabled', 403, 'ACCOUNT_DISABLED');
    }

    // Check if email is verified
    if (!user.is_verified) {
      throw new AppError(
        'Please verify your email address before logging in. Check your inbox for the verification link.',
        403,
        'EMAIL_NOT_VERIFIED'
      );
    }

    // Verify password
    const isValidPassword = await User.verifyPassword(password, user.password_hash);
    if (!isValidPassword) {
      recordLoginAttempt(email);
      
      // Increment failed attempts
      await query(
        'UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = $1',
        [user.id]
      );

      // Lock account after 5 failed attempts
      if (user.failed_login_attempts >= 4) {
        await query(
          'UPDATE users SET locked_until = NOW() + INTERVAL \'1 hour\' WHERE id = $1',
          [user.id]
        );
      }

      throw new AppError('Invalid credentials', 401, 'INVALID_CREDENTIALS');
    }

    // Reset failed attempts and clear lock
    await query(
      'UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = $1',
      [user.id]
    );

    // Clear rate limiting
    loginAttempts.delete(email);

    // Generate tokens with extended expiry if remember me
    const tokenExpiry = rememberMe ? '30d' : '7d';
    const { accessToken, refreshToken } = generateTokens(user);

    // Store refresh token in HTTP-only cookie
    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: rememberMe ? 30 * 24 * 60 * 60 * 1000 : 7 * 24 * 60 * 60 * 1000,
    });

    // Store refresh token in database
    await query(
      'INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES ($1, $2, NOW() + INTERVAL $3)',
      [user.id, refreshToken, tokenExpiry]
    );

    // Update last seen
    await User.updateLastSeen(user.id);

    logger.info(`User logged in: ${user.id}`, { rememberMe });

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role,
          avatarUrl: user.avatar_url,
          isVerified: user.is_verified,
        },
        accessToken,
        // Don't send refreshToken in body (it's in HTTP-only cookie)
        csrfToken: res.locals.csrfToken,
      },
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/forgot-password
 * @desc    Request password reset email
 * @access  Public
 */
router.post('/forgot-password', async (req, res, next) => {
  try {
    const { error, value } = resetPasswordRequestSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const { email } = value;

    // Find user
    const user = await User.findByEmail(email);

    // Always return success (don't reveal if email exists)
    if (!user) {
      return res.json({
        success: true,
        message: 'If an account exists, a password reset email has been sent.',
      });
    }

    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetExpires = new Date(Date.now() + 60 * 60 * 1000); // 1 hour

    // Store reset token
    await query(
      `UPDATE users 
       SET reset_password_token = $1, reset_password_expires = $2 
       WHERE id = $3`,
      [resetToken, resetExpires, user.id]
    );

    // Send reset email
    await sendPasswordResetEmail(email, resetToken);

    logger.info(`Password reset requested: ${user.id}`);

    res.json({
      success: true,
      message: 'If an account exists, a password reset email has been sent.',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/reset-password
 * @desc    Reset password with token
 * @access  Public
 */
router.post('/reset-password', async (req, res, next) => {
  try {
    const { error, value } = resetPasswordSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400, 'VALIDATION_ERROR');
    }

    const { token, password } = value;

    // Validate password strength
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      throw new AppError(
        passwordValidation.errors.join(', '),
        400,
        'WEAK_PASSWORD'
      );
    }

    // Find user with valid reset token
    const result = await query(
      `SELECT id, email FROM users 
       WHERE reset_password_token = $1 
         AND reset_password_expires > NOW()`,
      [token]
    );

    if (result.rows.length === 0) {
      throw new AppError('Invalid or expired reset token', 400, 'INVALID_TOKEN');
    }

    const user = result.rows[0];

    // Hash new password
    const bcrypt = require('bcryptjs');
    const passwordHash = await bcrypt.hash(password, 10);

    // Update password and clear reset token
    await query(
      `UPDATE users 
       SET password_hash = $1, 
           reset_password_token = NULL, 
           reset_password_expires = NULL,
           failed_login_attempts = 0,
           locked_until = NULL
       WHERE id = $2`,
      [passwordHash, user.id]
    );

    // Revoke all existing refresh tokens for security
    await query(
      'UPDATE refresh_tokens SET revoked_at = NOW() WHERE user_id = $1',
      [user.id]
    );

    // Send confirmation email
    try {
      await sendPasswordChangedEmail(user.email);
    } catch (emailError) {
      logger.error('Failed to send password changed email', emailError);
    }

    logger.info(`Password reset: ${user.id}`);

    res.json({
      success: true,
      message: 'Password reset successfully. Please log in with your new password.',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/refresh
 * @desc    Refresh access token using HTTP-only cookie
 * @access  Public
 */
router.post('/refresh', async (req, res, next) => {
  try {
    // Get refresh token from cookie or body
    const refreshToken = req.cookies?.refreshToken || req.body.refreshToken;

    if (!refreshToken) {
      throw new AppError('Refresh token required', 400, 'TOKEN_REQUIRED');
    }

    // Verify refresh token
    const decoded = verifyRefreshToken(refreshToken);

    // Check if token exists and is not revoked
    const result = await query(
      'SELECT * FROM refresh_tokens WHERE token = $1 AND user_id = $2 AND revoked_at IS NULL AND expires_at > NOW()',
      [refreshToken, decoded.userId]
    );

    if (result.rows.length === 0) {
      throw new AppError('Invalid refresh token', 401, 'INVALID_TOKEN');
    }

    // Get user
    const user = await User.findById(decoded.userId);

    // Generate new tokens
    const tokens = generateTokens(user);

    // Store new refresh token and revoke old one
    await query('BEGIN');
    await query('UPDATE refresh_tokens SET revoked_at = NOW() WHERE token = $1', [refreshToken]);
    await query(
      'INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES ($1, $2, NOW() + INTERVAL \'7 days\')',
      [user.id, tokens.refreshToken]
    );
    await query('COMMIT');

    // Update cookie
    res.cookie('refreshToken', tokens.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    res.json({
      success: true,
      data: {
        accessToken: tokens.accessToken,
      },
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   POST /api/auth/logout
 * @desc    Logout user and clear tokens
 * @access  Private
 */
router.post('/logout', authenticateToken, async (req, res, next) => {
  try {
    const refreshToken = req.cookies?.refreshToken || req.body.refreshToken;

    if (refreshToken) {
      await query('UPDATE refresh_tokens SET revoked_at = NOW() WHERE token = $1', [refreshToken]);
    }

    // Clear cookie
    res.clearCookie('refreshToken');
    res.clearCookie('csrf-token');

    logger.info(`User logged out: ${req.user.userId}`);

    res.json({
      success: true,
      message: 'Logged out successfully',
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route   GET /api/auth/me
 * @desc    Get current user
 * @access  Private
 */
router.get('/me', authenticateToken, async (req, res, next) => {
  try {
    const user = await User.findById(req.user.userId);

    res.json({
      success: true,
      data: {
        id: user.id,
        email: user.email,
        username: user.username,
        firstName: user.first_name,
        lastName: user.last_name,
        role: user.role,
        avatarUrl: user.avatar_url,
        isVerified: user.is_verified,
        lastSeenAt: user.last_seen_at,
        createdAt: user.created_at,
      },
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
