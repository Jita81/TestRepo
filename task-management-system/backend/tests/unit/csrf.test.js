/**
 * CSRF protection unit tests
 */

const { generateCsrfToken } = require('../../src/middleware/csrf');

describe('CSRF Protection', () => {
  describe('generateCsrfToken', () => {
    it('should generate a token', () => {
      const token = generateCsrfToken();
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
    });

    it('should generate token of correct length', () => {
      const token = generateCsrfToken();
      expect(token.length).toBe(64); // 32 bytes = 64 hex chars
    });

    it('should generate unique tokens', () => {
      const token1 = generateCsrfToken();
      const token2 = generateCsrfToken();
      expect(token1).not.toBe(token2);
    });

    it('should generate hexadecimal tokens', () => {
      const token = generateCsrfToken();
      expect(/^[0-9a-f]+$/.test(token)).toBe(true);
    });

    it('should generate cryptographically random tokens', () => {
      const tokens = new Set();
      for (let i = 0; i < 100; i++) {
        tokens.add(generateCsrfToken());
      }
      // All tokens should be unique
      expect(tokens.size).toBe(100);
    });
  });
});
