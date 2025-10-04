/**
 * Authentication integration tests
 */

const request = require('supertest');
const express = require('express');
const authRoutes = require('../../src/routes/auth.routes');
const { errorHandler } = require('../../src/middleware/errorHandler');

// Mock dependencies
jest.mock('../../src/models/User');
jest.mock('../../src/config/database');

const User = require('../../src/models/User');
const { query } = require('../../src/config/database');

// Create test app
const app = express();
app.use(express.json());
app.use('/api/auth', authRoutes);
app.use(errorHandler);

describe('Authentication API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/auth/register', () => {
    const validRegistration = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'password123',
      firstName: 'Test',
      lastName: 'User',
    };

    it('should register a new user successfully', async () => {
      const mockUser = {
        id: 'user-id',
        email: validRegistration.email,
        username: validRegistration.username,
        first_name: validRegistration.firstName,
        last_name: validRegistration.lastName,
        role: 'member',
      };

      User.findByEmail.mockResolvedValue(null);
      User.findByUsername.mockResolvedValue(null);
      User.create.mockResolvedValue(mockUser);
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .post('/api/auth/register')
        .send(validRegistration)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('user');
      expect(response.body.data).toHaveProperty('accessToken');
      expect(response.body.data).toHaveProperty('refreshToken');
      expect(response.body.data.user.email).toBe(validRegistration.email);
    });

    it('should fail with duplicate email', async () => {
      User.findByEmail.mockResolvedValue({ id: 'existing-user' });

      const response = await request(app)
        .post('/api/auth/register')
        .send(validRegistration)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Email already registered');
    });

    it('should fail with duplicate username', async () => {
      User.findByEmail.mockResolvedValue(null);
      User.findByUsername.mockResolvedValue({ id: 'existing-user' });

      const response = await request(app)
        .post('/api/auth/register')
        .send(validRegistration)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Username already taken');
    });

    it('should fail with invalid email', async () => {
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

    it('should fail with short password', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          password: 'short',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should fail with missing required fields', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'test@example.com',
          // Missing username and password
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should fail with invalid username (special characters)', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          ...validRegistration,
          username: 'test@user#123',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/auth/login', () => {
    const validCredentials = {
      email: 'test@example.com',
      password: 'password123',
    };

    it('should login successfully with valid credentials', async () => {
      const mockUser = {
        id: 'user-id',
        email: validCredentials.email,
        username: 'testuser',
        password_hash: '$2a$10$hashedpassword',
        is_active: true,
        role: 'member',
      };

      User.findByEmail.mockResolvedValue(mockUser);
      User.verifyPassword.mockResolvedValue(true);
      User.updateLastSeen.mockResolvedValue();
      query.mockResolvedValue({ rows: [] });

      const response = await request(app)
        .post('/api/auth/login')
        .send(validCredentials)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('user');
      expect(response.body.data).toHaveProperty('accessToken');
      expect(response.body.data).toHaveProperty('refreshToken');
      expect(User.updateLastSeen).toHaveBeenCalledWith(mockUser.id);
    });

    it('should fail with non-existent email', async () => {
      User.findByEmail.mockResolvedValue(null);

      const response = await request(app)
        .post('/api/auth/login')
        .send(validCredentials)
        .expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Invalid credentials');
    });

    it('should fail with incorrect password', async () => {
      const mockUser = {
        id: 'user-id',
        email: validCredentials.email,
        password_hash: '$2a$10$hashedpassword',
        is_active: true,
      };

      User.findByEmail.mockResolvedValue(mockUser);
      User.verifyPassword.mockResolvedValue(false);

      const response = await request(app)
        .post('/api/auth/login')
        .send(validCredentials)
        .expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Invalid credentials');
    });

    it('should fail with inactive account', async () => {
      const mockUser = {
        id: 'user-id',
        email: validCredentials.email,
        password_hash: '$2a$10$hashedpassword',
        is_active: false,
      };

      User.findByEmail.mockResolvedValue(mockUser);

      const response = await request(app)
        .post('/api/auth/login')
        .send(validCredentials)
        .expect(403);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Account is disabled');
    });

    it('should fail with invalid email format', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'not-an-email',
          password: 'password123',
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });

    it('should fail with missing credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          // Missing password
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/auth/refresh', () => {
    it('should refresh access token with valid refresh token', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
        role: 'member',
      };

      // Mock token verification
      const jwt = require('../../src/utils/jwt');
      jest.spyOn(jwt, 'verifyRefreshToken').mockReturnValue({
        userId: mockUser.id,
      });

      query.mockResolvedValueOnce({
        rows: [{ token: 'valid-refresh-token', user_id: mockUser.id }],
      });
      
      User.findById.mockResolvedValue(mockUser);
      
      query.mockResolvedValueOnce({ rows: [] }); // BEGIN
      query.mockResolvedValueOnce({ rows: [] }); // UPDATE
      query.mockResolvedValueOnce({ rows: [] }); // INSERT
      query.mockResolvedValueOnce({ rows: [] }); // COMMIT

      const response = await request(app)
        .post('/api/auth/refresh')
        .send({
          refreshToken: 'valid-refresh-token',
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('accessToken');
      expect(response.body.data).toHaveProperty('refreshToken');
    });

    it('should fail with missing refresh token', async () => {
      const response = await request(app)
        .post('/api/auth/refresh')
        .send({})
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Refresh token required');
    });

    it('should fail with invalid refresh token', async () => {
      const jwt = require('../../src/utils/jwt');
      jest.spyOn(jwt, 'verifyRefreshToken').mockImplementation(() => {
        throw new Error('Invalid token');
      });

      const response = await request(app)
        .post('/api/auth/refresh')
        .send({
          refreshToken: 'invalid-token',
        })
        .expect(500);

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/auth/me', () => {
    it('should return current user with valid token', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        role: 'member',
      };

      User.findById.mockResolvedValue(mockUser);

      // Generate valid token
      const { generateAccessToken } = require('../../src/utils/jwt');
      const token = generateAccessToken({
        userId: mockUser.id,
        email: mockUser.email,
      });

      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe(mockUser.id);
      expect(response.body.data.email).toBe(mockUser.email);
    });

    it('should fail without token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Access token required');
    });

    it('should fail with invalid token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);

      expect(response.body.success).toBe(false);
    });

    it('should fail with malformed authorization header', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', 'InvalidFormat token')
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/auth/logout', () => {
    it('should logout successfully with valid token', async () => {
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
        .send({
          refreshToken: 'some-refresh-token',
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('Logged out successfully');
      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE refresh_tokens'),
        ['some-refresh-token']
      );
    });

    it('should fail without authentication', async () => {
      const response = await request(app)
        .post('/api/auth/logout')
        .send({
          refreshToken: 'some-token',
        })
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });
});
