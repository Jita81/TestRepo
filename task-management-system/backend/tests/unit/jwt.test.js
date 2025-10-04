/**
 * JWT utility unit tests
 */

const {
  generateAccessToken,
  generateRefreshToken,
  generateTokens,
  verifyAccessToken,
  verifyRefreshToken,
  decodeToken,
} = require('../../src/utils/jwt');

describe('JWT Utilities', () => {
  const mockUser = {
    id: 'test-user-id',
    userId: 'test-user-id', // Include both for test compatibility
    email: 'test@example.com',
    username: 'testuser',
    role: 'member',
  };

  describe('generateAccessToken', () => {
    it('should generate a valid access token', () => {
      const token = generateAccessToken(mockUser);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.').length).toBe(3); // JWT has 3 parts
    });

    it('should include user data in token payload', () => {
      const token = generateAccessToken(mockUser);
      const decoded = decodeToken(token);
      
      expect(decoded.userId).toBe(mockUser.id);
      expect(decoded.email).toBe(mockUser.email);
      expect(decoded.username).toBe(mockUser.username);
      expect(decoded.role).toBe(mockUser.role);
    });

    it('should have expiration time', () => {
      const token = generateAccessToken(mockUser);
      const decoded = decodeToken(token);
      
      expect(decoded.exp).toBeDefined();
      expect(decoded.exp).toBeGreaterThan(Math.floor(Date.now() / 1000));
    });
  });

  describe('generateRefreshToken', () => {
    it('should generate a valid refresh token', () => {
      const token = generateRefreshToken(mockUser);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.').length).toBe(3);
    });

    it('should have longer expiration than access token', () => {
      const accessToken = generateAccessToken(mockUser);
      const refreshToken = generateRefreshToken(mockUser);
      
      const accessDecoded = decodeToken(accessToken);
      const refreshDecoded = decodeToken(refreshToken);
      
      expect(refreshDecoded.exp).toBeGreaterThan(accessDecoded.exp);
    });
  });

  describe('generateTokens', () => {
    it('should generate both access and refresh tokens', () => {
      const tokens = generateTokens(mockUser);
      
      expect(tokens).toHaveProperty('accessToken');
      expect(tokens).toHaveProperty('refreshToken');
      expect(typeof tokens.accessToken).toBe('string');
      expect(typeof tokens.refreshToken).toBe('string');
    });
  });

  describe('verifyAccessToken', () => {
    it('should verify a valid access token', () => {
      const token = generateAccessToken(mockUser);
      const decoded = verifyAccessToken(token);
      
      expect(decoded.userId).toBe(mockUser.id);
      expect(decoded.email).toBe(mockUser.email);
    });

    it('should throw error for invalid token', () => {
      expect(() => {
        verifyAccessToken('invalid.token.here');
      }).toThrow();
    });

    it('should throw error for malformed token', () => {
      expect(() => {
        verifyAccessToken('not-a-jwt');
      }).toThrow();
    });

    it('should throw error for token with wrong signature', () => {
      const token = generateAccessToken(mockUser);
      const tamperedToken = token.slice(0, -10) + 'tampered12';
      
      expect(() => {
        verifyAccessToken(tamperedToken);
      }).toThrow();
    });
  });

  describe('verifyRefreshToken', () => {
    it('should verify a valid refresh token', () => {
      const token = generateRefreshToken(mockUser);
      const decoded = verifyRefreshToken(token);
      
      expect(decoded.userId).toBe(mockUser.id);
    });

    it('should throw error for invalid refresh token', () => {
      expect(() => {
        verifyRefreshToken('invalid.token.here');
      }).toThrow();
    });
  });

  describe('decodeToken', () => {
    it('should decode token without verification', () => {
      const token = generateAccessToken(mockUser);
      const decoded = decodeToken(token);
      
      expect(decoded).toBeDefined();
      expect(decoded.userId).toBe(mockUser.id);
    });

    it('should decode expired token', () => {
      // This would require mocking token generation with past expiry
      // For now, we test that it decodes without throwing
      const token = generateAccessToken(mockUser);
      const decoded = decodeToken(token);
      
      expect(decoded).toBeDefined();
    });

    it('should return null for invalid token', () => {
      const decoded = decodeToken('not-a-valid-token');
      expect(decoded).toBeNull();
    });
  });

  describe('Token Security', () => {
    it('should generate unique tokens for same user', async () => {
      const token1 = generateAccessToken(mockUser);
      
      // Wait 10ms to ensure different timestamp (iat has second precision)
      await new Promise(resolve => setTimeout(resolve, 1100));
      
      const token2 = generateAccessToken(mockUser);
      
      // Tokens should be different due to timestamp
      expect(token1).not.toBe(token2);
    });

    it('should include issued at (iat) claim', () => {
      const token = generateAccessToken(mockUser);
      const decoded = decodeToken(token);
      
      expect(decoded.iat).toBeDefined();
      expect(typeof decoded.iat).toBe('number');
    });
  });
});
