const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const { authenticateToken } = require('../middleware/auth');
const logger = require('../middleware/logger');

const router = express.Router();

// In-memory user store (replace with database in production)
let users = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    password: '$2a$10$8K1p/a0dURXAm7ZisDo/ZOr6GUzVrJ2uKW7XCsVUJ3E5qZVqQXqKu', // password: admin123
    role: 'admin',
    createdAt: new Date()
  },
  {
    id: 2,
    username: 'user',
    email: 'user@example.com',
    password: '$2a$10$8K1p/a0dURXAm7ZisDo/ZOr6GUzVrJ2uKW7XCsVUJ3E5qZVqQXqKu', // password: admin123
    role: 'user',
    createdAt: new Date()
  }
];
let nextUserId = 3;

/**
 * Validation middleware for user registration
 */
const validateRegistration = [
  body('username')
    .isLength({ min: 3, max: 30 })
    .withMessage('Username must be between 3 and 30 characters')
    .matches(/^[a-zA-Z0-9_]+$/)
    .withMessage('Username can only contain letters, numbers, and underscores'),
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one lowercase letter, one uppercase letter, and one number')
];

/**
 * Validation middleware for user login
 */
const validateLogin = [
  body('username')
    .notEmpty()
    .withMessage('Username is required'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

/**
 * Handle validation errors
 */
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Validation failed',
        details: errors.array()
      }
    });
  }
  next();
};

/**
 * Generate JWT token
 * @param {Object} user - User object
 * @returns {string} JWT token
 */
const generateToken = (user) => {
  return jwt.sign(
    { 
      id: user.id, 
      username: user.username, 
      email: user.email, 
      role: user.role 
    },
    process.env.JWT_SECRET || 'fallback-secret',
    { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
  );
};

// POST /auth/register - Register new user
router.post('/register', 
  validateRegistration,
  handleValidationErrors,
  async (req, res) => {
    try {
      const { username, email, password } = req.body;

      // Check if user already exists
      const existingUser = users.find(user => 
        user.username === username || user.email === email
      );

      if (existingUser) {
        return res.status(409).json({
          success: false,
          error: { message: 'Username or email already exists' }
        });
      }

      // Hash password
      const saltRounds = 10;
      const hashedPassword = await bcrypt.hash(password, saltRounds);

      // Create new user
      const newUser = {
        id: nextUserId++,
        username,
        email,
        password: hashedPassword,
        role: 'user', // default role
        createdAt: new Date()
      };

      users.push(newUser);

      // Generate token
      const token = generateToken(newUser);

      // Remove password from response
      const { password: _, ...userResponse } = newUser;

      logger.info('User registered', { 
        userId: newUser.id,
        username: newUser.username,
        email: newUser.email 
      });

      res.status(201).json({
        success: true,
        data: {
          user: userResponse,
          token
        }
      });
    } catch (error) {
      logger.error('Registration error', { error: error.message });
      res.status(500).json({
        success: false,
        error: { message: 'Registration failed' }
      });
    }
  }
);

// POST /auth/login - Login user
router.post('/login',
  validateLogin,
  handleValidationErrors,
  async (req, res) => {
    try {
      const { username, password } = req.body;

      // Find user
      const user = users.find(user => user.username === username);

      if (!user) {
        logger.warn('Login attempt with invalid username', { 
          username,
          ip: req.ip 
        });
        return res.status(401).json({
          success: false,
          error: { message: 'Invalid credentials' }
        });
      }

      // Check password
      const isPasswordValid = await bcrypt.compare(password, user.password);

      if (!isPasswordValid) {
        logger.warn('Login attempt with invalid password', { 
          userId: user.id,
          username: user.username,
          ip: req.ip 
        });
        return res.status(401).json({
          success: false,
          error: { message: 'Invalid credentials' }
        });
      }

      // Generate token
      const token = generateToken(user);

      // Remove password from response
      const { password: _, ...userResponse } = user;

      logger.info('User logged in', { 
        userId: user.id,
        username: user.username 
      });

      res.json({
        success: true,
        data: {
          user: userResponse,
          token
        }
      });
    } catch (error) {
      logger.error('Login error', { error: error.message });
      res.status(500).json({
        success: false,
        error: { message: 'Login failed' }
      });
    }
  }
);

// GET /auth/profile - Get current user profile
router.get('/profile', authenticateToken, (req, res) => {
  try {
    const user = users.find(user => user.id === req.user.id);

    if (!user) {
      return res.status(404).json({
        success: false,
        error: { message: 'User not found' }
      });
    }

    // Remove password from response
    const { password: _, ...userResponse } = user;

    res.json({
      success: true,
      data: { user: userResponse }
    });
  } catch (error) {
    logger.error('Profile retrieval error', { 
      userId: req.user?.id,
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: { message: 'Failed to retrieve profile' }
    });
  }
});

// PUT /auth/profile - Update user profile
router.put('/profile',
  authenticateToken,
  [
    body('email')
      .optional()
      .isEmail()
      .withMessage('Please provide a valid email address')
      .normalizeEmail(),
    body('username')
      .optional()
      .isLength({ min: 3, max: 30 })
      .withMessage('Username must be between 3 and 30 characters')
      .matches(/^[a-zA-Z0-9_]+$/)
      .withMessage('Username can only contain letters, numbers, and underscores')
  ],
  handleValidationErrors,
  (req, res) => {
    try {
      const { email, username } = req.body;
      const userIndex = users.findIndex(user => user.id === req.user.id);

      if (userIndex === -1) {
        return res.status(404).json({
          success: false,
          error: { message: 'User not found' }
        });
      }

      // Check for existing username/email (excluding current user)
      if (username || email) {
        const existingUser = users.find(user => 
          user.id !== req.user.id && 
          (user.username === username || user.email === email)
        );

        if (existingUser) {
          return res.status(409).json({
            success: false,
            error: { message: 'Username or email already exists' }
          });
        }
      }

      // Update user
      if (email) users[userIndex].email = email;
      if (username) users[userIndex].username = username;
      users[userIndex].updatedAt = new Date();

      // Remove password from response
      const { password: _, ...userResponse } = users[userIndex];

      logger.info('Profile updated', { 
        userId: req.user.id,
        changes: { email, username }
      });

      res.json({
        success: true,
        data: { user: userResponse }
      });
    } catch (error) {
      logger.error('Profile update error', { 
        userId: req.user?.id,
        error: error.message 
      });
      res.status(500).json({
        success: false,
        error: { message: 'Failed to update profile' }
      });
    }
  }
);

// POST /auth/change-password - Change user password
router.post('/change-password',
  authenticateToken,
  [
    body('currentPassword')
      .notEmpty()
      .withMessage('Current password is required'),
    body('newPassword')
      .isLength({ min: 6 })
      .withMessage('New password must be at least 6 characters long')
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
      .withMessage('New password must contain at least one lowercase letter, one uppercase letter, and one number')
  ],
  handleValidationErrors,
  async (req, res) => {
    try {
      const { currentPassword, newPassword } = req.body;
      const userIndex = users.findIndex(user => user.id === req.user.id);

      if (userIndex === -1) {
        return res.status(404).json({
          success: false,
          error: { message: 'User not found' }
        });
      }

      // Verify current password
      const isCurrentPasswordValid = await bcrypt.compare(currentPassword, users[userIndex].password);

      if (!isCurrentPasswordValid) {
        logger.warn('Invalid current password in change password attempt', { 
          userId: req.user.id 
        });
        return res.status(401).json({
          success: false,
          error: { message: 'Current password is incorrect' }
        });
      }

      // Hash new password
      const saltRounds = 10;
      const hashedNewPassword = await bcrypt.hash(newPassword, saltRounds);

      // Update password
      users[userIndex].password = hashedNewPassword;
      users[userIndex].updatedAt = new Date();

      logger.info('Password changed', { userId: req.user.id });

      res.json({
        success: true,
        data: { message: 'Password changed successfully' }
      });
    } catch (error) {
      logger.error('Change password error', { 
        userId: req.user?.id,
        error: error.message 
      });
      res.status(500).json({
        success: false,
        error: { message: 'Failed to change password' }
      });
    }
  }
);

// POST /auth/logout - Logout user (client-side token removal)
router.post('/logout', authenticateToken, (req, res) => {
  logger.info('User logged out', { userId: req.user.id });
  
  res.json({
    success: true,
    data: { message: 'Logged out successfully' }
  });
});

module.exports = router;