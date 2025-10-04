/**
 * User model unit tests
 */

const User = require('../../../src/models/User');
const bcrypt = require('bcryptjs');

// Mock the database
jest.mock('../../../src/config/database', () => ({
  query: jest.fn(),
  transaction: jest.fn(),
}));

const { query } = require('../../../src/config/database');

describe('User Model', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('should create a new user with hashed password', async () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
        firstName: 'Test',
        lastName: 'User',
        role: 'member',
      };

      const mockUser = {
        id: 'user-id',
        email: userData.email,
        username: userData.username,
        first_name: userData.firstName,
        last_name: userData.lastName,
        role: userData.role,
      };

      query.mockResolvedValue({ rows: [mockUser] });

      const result = await User.create(userData);

      expect(query).toHaveBeenCalledTimes(1);
      expect(query.mock.calls[0][0]).toContain('INSERT INTO users');
      
      // Check that password was hashed (not plain text)
      const hashedPassword = query.mock.calls[0][1][2];
      expect(hashedPassword).not.toBe(userData.password);
      expect(hashedPassword.length).toBeGreaterThan(20);

      expect(result).toEqual(mockUser);
    });

    it('should use default role if not provided', async () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
      };

      query.mockResolvedValue({ rows: [{ ...userData, role: 'member' }] });

      await User.create(userData);

      const callArgs = query.mock.calls[0][1];
      expect(callArgs[5]).toBe('member'); // role parameter
    });
  });

  describe('findById', () => {
    it('should find user by ID', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
        username: 'testuser',
      };

      query.mockResolvedValue({ rows: [mockUser] });

      const result = await User.findById('user-id');

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('SELECT'),
        ['user-id']
      );
      expect(result).toEqual(mockUser);
    });

    it('should throw error if user not found', async () => {
      query.mockResolvedValue({ rows: [] });

      await expect(User.findById('non-existent-id')).rejects.toThrow('User not found');
    });
  });

  describe('findByEmail', () => {
    it('should find user by email', async () => {
      const mockUser = {
        id: 'user-id',
        email: 'test@example.com',
      };

      query.mockResolvedValue({ rows: [mockUser] });

      const result = await User.findByEmail('test@example.com');

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('WHERE email = $1'),
        ['test@example.com']
      );
      expect(result).toEqual(mockUser);
    });

    it('should return null if user not found', async () => {
      query.mockResolvedValue({ rows: [] });

      const result = await User.findByEmail('nonexistent@example.com');

      expect(result).toBeNull();
    });
  });

  describe('findByUsername', () => {
    it('should find user by username', async () => {
      const mockUser = {
        id: 'user-id',
        username: 'testuser',
      };

      query.mockResolvedValue({ rows: [mockUser] });

      const result = await User.findByUsername('testuser');

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('WHERE username = $1'),
        ['testuser']
      );
      expect(result).toEqual(mockUser);
    });
  });

  describe('verifyPassword', () => {
    it('should return true for correct password', async () => {
      const password = 'password123';
      const hash = await bcrypt.hash(password, 10);

      const result = await User.verifyPassword(password, hash);

      expect(result).toBe(true);
    });

    it('should return false for incorrect password', async () => {
      const password = 'password123';
      const hash = await bcrypt.hash(password, 10);

      const result = await User.verifyPassword('wrongpassword', hash);

      expect(result).toBe(false);
    });

    it('should handle empty password', async () => {
      const hash = await bcrypt.hash('password', 10);

      const result = await User.verifyPassword('', hash);

      expect(result).toBe(false);
    });
  });

  describe('updateLastSeen', () => {
    it('should update user last seen timestamp', async () => {
      query.mockResolvedValue({ rows: [] });

      await User.updateLastSeen('user-id');

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE users SET last_seen_at'),
        ['user-id']
      );
    });
  });

  describe('update', () => {
    it('should update allowed fields', async () => {
      const updates = {
        first_name: 'Updated',
        last_name: 'Name',
        avatar_url: 'http://example.com/avatar.jpg',
      };

      const mockUpdatedUser = {
        id: 'user-id',
        ...updates,
      };

      query.mockResolvedValue({ rows: [mockUpdatedUser] });

      const result = await User.update('user-id', updates);

      expect(query).toHaveBeenCalledTimes(1);
      expect(query.mock.calls[0][0]).toContain('UPDATE users');
      expect(result).toEqual(mockUpdatedUser);
    });

    it('should ignore non-allowed fields', async () => {
      const updates = {
        first_name: 'Updated',
        email: 'hacker@example.com', // Should be ignored
        role: 'admin', // Should be ignored
      };

      query.mockResolvedValue({ rows: [{ id: 'user-id' }] });

      await User.update('user-id', updates);

      const sqlQuery = query.mock.calls[0][0];
      expect(sqlQuery).toContain('first_name');
      // Check that email is not in the SET clause (it's fine if in RETURNING)
      expect(sqlQuery).toMatch(/SET.*first_name/);
      expect(sqlQuery).not.toMatch(/SET.*email/);
      expect(sqlQuery).not.toMatch(/SET.*role/);
    });

    it('should throw error if no valid fields to update', async () => {
      const updates = {
        email: 'hacker@example.com',
      };

      await expect(User.update('user-id', updates)).rejects.toThrow('No valid fields to update');
    });
  });

  describe('isProjectMember', () => {
    it('should return true if user is project member', async () => {
      query.mockResolvedValue({ rows: [{ exists: true }] });

      const result = await User.isProjectMember('user-id', 'project-id');

      expect(result).toBe(true);
      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('project_members'),
        ['user-id', 'project-id']
      );
    });

    it('should return false if user is not project member', async () => {
      query.mockResolvedValue({ rows: [] });

      const result = await User.isProjectMember('user-id', 'project-id');

      expect(result).toBe(false);
    });
  });

  describe('getByProject', () => {
    it('should get all users in a project', async () => {
      const mockUsers = [
        { id: 'user1', username: 'user1' },
        { id: 'user2', username: 'user2' },
      ];

      query.mockResolvedValue({ rows: mockUsers });

      const result = await User.getByProject('project-id');

      expect(query).toHaveBeenCalledWith(
        expect.stringContaining('JOIN project_members'),
        ['project-id']
      );
      expect(result).toEqual(mockUsers);
    });
  });

  describe('getAll', () => {
    it('should get all users with pagination', async () => {
      const mockUsers = [
        { id: 'user1' },
        { id: 'user2' },
      ];

      query
        .mockResolvedValueOnce({ rows: mockUsers })
        .mockResolvedValueOnce({ rows: [{ count: '10' }] });

      const result = await User.getAll(50, 0);

      expect(result).toHaveProperty('users', mockUsers);
      expect(result).toHaveProperty('total', 10);
    });

    it('should apply limit and offset', async () => {
      query
        .mockResolvedValueOnce({ rows: [] })
        .mockResolvedValueOnce({ rows: [{ count: '0' }] });

      await User.getAll(25, 50);

      expect(query.mock.calls[0][1]).toEqual([25, 50]);
    });
  });
});
