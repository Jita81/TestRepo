/**
 * Enhanced authentication integration tests
 */

const request = require('supertest');
const express = require('express');
const cookieParser = require('cookie-parser');
const authRoutes = require('../../src/routes/auth.enhanced.routes');
const { errorHandler } = require('../../src/middleware/errorHandler');

// Mock dependencies
jest.mock('../../src/models/User');
jest.mock('../../src/config/database');
jest.mock('../../src/services/email.service');

const User = require('../../src/models/User');
const { query } = require('../../src/config/database');
const emailService = require('../../src/services/email.service');

// Create test app
const app = express();
app.use(express.json());
app.use(cookieParser());
app.use('/api/auth', authRoutes);
app.use(errorHandler);

describe('Enhanced Authentication API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/auth/register', () => {
    const validRegistration = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'SecurePass123!',
      firstName: 'Test',
      lastName: 'User',
    };

    it('should register user with email verification', async () => {
      const mockUser = {
        id: 'user-id',
        email: validRegistration.email,
        username: validRegistration.username,
        first_name: validRegistration.firstName,
        last_name: validRegistration.lastName,
        role: 'member',
        is_verified: false,
      };

      User.findByEmail.mockResolvedValue(null);
      User.findByUsername.mockResolvedValue(null);
      User.create.mockResolvedValue(mockUser);
      emailService.sendVerificationEmail.mockResolvedValue(true);

      const response = await request(app)
        .post('/api/auth/register')
        .send(validRegistration)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('verify your account');
      expect(response.body.data.user.isVerified).toBe(false);
      expect(emailService.sendVerificationEmail).toHaveBeenCalled();
    });

    it('should reject weak password', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          password: 'weak',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('8 characters');
    });

    it('should reject password without uppercase', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          password: 'nouppercasepass123!',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('uppercase');
    });

    it('should reject password without number', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          password: 'NoNumberPass!',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('number');
    });

    it('should reject invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          email: 'invalid-email',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('email');
    });

    it('should reject short username', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          username: 'ab',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('3 characters');
    });

    it('should continue registration even if email fails', async () => {
      User.findByEmail.mockResolvedValue(null);
      User.findByUsername.mockResolvedValue(null);
      User.create.mockResolvedValue({ id: 'user-id', email: validRegistration.email });
      emailService.sendVerificationEmail.mockRejectedValue(new Error('Email service down'));

      const response = await request(app)
        .post('/api/auth/register')
        .send(validRegistration)
        .expect(201);

      expect(response.body.success).toBe(true);
    });
  });

  describe('GET /api/auth/verify-email/:token', () => {
    it('should verify email with valid token', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
        verification_token_expires: new Date(Date.now() + 1000000),
      };

      query.mockResolvedValueOnce({ rows: [mockUser] }); // Find user
      query.mockResolvedValueOnce({ rows: [] }); // Update user
      emailService.sendWelcomeEmail.mockResolvedValue(true);

      const response = await request(app)
        .get('/api/auth/verify-email/valid-token')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('verified successfully');
      expect(emailService.sendWelcomeEmail).toHaveBeenCalled();
    });

    it('should reject invalid token', async () => {
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .get('/api/auth/verify-email/invalid-token')
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Invalid or expired');
    });

    it('should reject expired token', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        verification_token_expires: new Date(Date.now() - 1000),
      };

      query.mockResolvedValue({ rows: [mockUser] });

      const response = await request(app)
        .get('/api/auth/verify-email/expired-token')
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('expired');
    });
  });

  describe('POST /api/auth/resend-verification', () => {
    it('should resend verification email', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
      };

      query.mockResolvedValueOnce({ rows: [mockUser] }); // Find user
      query.mockResolvedValueOnce({ rows: [] }); // Update token
      emailService.sendVerificationEmail.mockResolvedValue(true);

      const response = await request(app)
        .post('/api/auth/resend-verification')
        .send({ email: 'test@example.com' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(emailService.sendVerificationEmail).toHaveBeenCalled();
    });

    it('should not reveal if email does not exist', async () => {
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .post('/api/auth/resend-verification')
        .send({ email: 'nonexistent@example.com' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(emailService.sendVerificationEmail).not.toHaveBeenCalled();
    });

    it('should require email', async () => {
      const response = await request(app)
        .post('/api/auth/resend-verification')
        .send({})
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/auth/login', () => {
    it('should login verified user and set cookies', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
        password_hash: '$2a$10$hashedpassword',
        is_active: true,
        is_verified: true,
        role: 'member',
        failed_login_attempts: 0,
        locked_until: null,
      };

      User.findByEmail.mockResolvedValue(mockUser);
      User.verifyPassword.mockResolvedValue(true);
      User.updateLastSeen.mockResolvedValue();
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
          rememberMe: true,
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('accessToken');
      expect(response.body.data).toHaveProperty('csrfToken');
      expect(response.headers['set-cookie']).toBeDefined();
    });

    it('should reject unverified user', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        is_active: true,
        is_verified: false,
      };

      User.findByEmail.mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
        })
        .expect(403);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('verify your email');
    });

    it('should reject locked account', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        is_active: true,
        is_verified: true,
        locked_until: new Date(Date.now() + 10000),
      };

      User.findByEmail.mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123!',
        })
        .expect(403);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('locked');
    });

    it('should increment failed login attempts', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        password_hash: '$2a$10$hashedpassword',
        is_active: true,
        is_verified: true,
        failed_login_attempts: 2,
      };

      User.findByEmail.mockResolvedValue(mockUser);
      User.verifyPassword.mockResolvedValue(false);
      query.mockResolvedValue({ rows: [] });

      await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'WrongPassword',
        })
        .expect(401);

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('failed_login_attempts'),
        expect.any(Array)
      );
    });
  });

  describe('POST /api/auth/forgot-password', () => {
    it('should send password reset email', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
      };

      User.findByEmail.mockResolvedValue(mockUser);
      query.mockResolvedValue({ rows: [] });
      emailService.sendPasswordResetEmail.mockResolvedValue(true);

      const response = await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'test@example.com' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(emailService.sendPasswordResetEmail).toHaveBeenCalled();
    });

    it('should not reveal if email does not exist', async () => {
      User.findByEmail.mockResolvedValue(null);

      const response = await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'nonexistent@example.com' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(emailService.sendPasswordResetEmail).not.toHaveBeenCalled();
    });

    it('should validate email format', async () => {
      const response = await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'invalid-email' })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/auth/reset-password', () => {
    it('should reset password with valid token', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
      };

      query.mockResolvedValueOnce({ rows: [mockUser] }); // Find user
      query.mockResolvedValueOnce({ rows: [] }); // Update password
      query.mockResolvedValueOnce({ rows: [] }); // Revoke tokens
      emailService.sendPasswordChangedEmail.mockResolvedValue(true);

      const response = await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'valid-reset-token',
          password: 'NewSecurePass123!',
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('reset successfully');
      expect(emailService.sendPasswordChangedEmail).toHaveBeenCalled();
    });

    it('should reject invalid token', async () => {
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'invalid-token',
          password: 'NewSecurePass123!',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Invalid or expired');
    });

    it('should reject weak new password', async () => {
      const response = await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'valid-token',
          password: 'weak',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      // Should reject due to validation
      expect(response.body.error).toBeDefined();
    });

    it('should revoke all refresh tokens after reset', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
      };

      query.mockResolvedValueOnce({ rows: [mockUser] });
      query.mockResolvedValueOnce({ rows: [] });
      query.mockResolvedValueOnce({ rows: [] });
      emailService.sendPasswordChangedEmail.mockResolvedValue(true);

      await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'valid-token',
          password: 'NewSecurePass123!',
        })
        .expect(200);

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('refresh_tokens'),
        expect.arrayContaining([mockUser.id])
      );
    });
  });

  describe('POST /api/auth/refresh', () => {
    it('should require refresh token', async () => {
      const response = await request(app)
        .post('/api/auth/refresh')
        .send({})
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Refresh token required');
    });

    it('should reject invalid refresh token', async () => {
      const jwt = require('../../src/utils/jwt');
      jest.spyOn(jwt, 'verifyRefreshToken').mockImplementation(() => {
        const error = new Error('Invalid token');
        error.name = 'JsonWebTokenError';
        throw error;
      });

      const response = await request(app)
        .post('/api/auth/refresh')
        .send({ refreshToken: 'invalid-token' });

      expect(response.body.success).toBe(false);
      expect([401, 500]).toContain(response.statusCode);
    });
  });

  describe('POST /api/auth/logout', () => {
    it('should logout and clear cookies', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
      };

      query.mockResolvedValue({ rows: [] });

      const { generateAccessToken } = require('../../src/utils/jwt');
      const token = generateAccessToken({
        userId: mockUser.id,
        email: mockUser.email,
      });

      const response = await request(app)
        .post('/api/auth/logout')
        .set('Authorization', `Bearer ${token}`)
        .set('Cookie', ['refreshToken=refresh-token'])
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.headers['set-cookie']).toBeDefined();
    });
  });
});
