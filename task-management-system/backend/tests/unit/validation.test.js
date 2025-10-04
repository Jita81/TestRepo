/**
 * Validation utilities unit tests
 */

const {
  validatePassword,
  calculatePasswordStrength,
  validateEmail,
  validateUsername,
  sanitizeInput,
  validateRegistrationData,
} = require('../../src/utils/validation');

describe('Validation Utilities', () => {
  describe('validatePassword', () => {
    it('should accept valid strong password', () => {
      const result = validatePassword('SecurePass123!');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject password shorter than 8 characters', () => {
      const result = validatePassword('Short1!');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters long');
    });

    it('should reject password without uppercase', () => {
      const result = validatePassword('lowercase123!');
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('uppercase'))).toBe(true);
    });

    it('should reject password without number', () => {
      const result = validatePassword('NoNumber!');
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('number'))).toBe(true);
    });

    it('should warn about missing special character', () => {
      const result = validatePassword('Password123');
      expect(result.errors.some(e => e.includes('special character'))).toBe(true);
    });

    it('should reject common weak passwords', () => {
      const commonPasswords = ['password', 'password123'];
      commonPasswords.forEach(pwd => {
        const result = validatePassword(pwd);
        expect(result.isValid).toBe(false);
      });
    });

    it('should include password strength in result', () => {
      const result = validatePassword('VeryStr0ng!Pass');
      expect(result.strength).toHaveProperty('score');
      expect(result.strength).toHaveProperty('level');
    });

    it('should handle empty password', () => {
      const result = validatePassword('');
      expect(result.isValid).toBe(false);
    });

    it('should handle null password', () => {
      const result = validatePassword(null);
      expect(result.isValid).toBe(false);
    });
  });

  describe('calculatePasswordStrength', () => {
    it('should rate short password as weak', () => {
      const strength = calculatePasswordStrength('pass');
      expect(strength.level).toBe('weak');
      expect(strength.score).toBeLessThan(4);
    });

    it('should rate medium password correctly', () => {
      const strength = calculatePasswordStrength('Password1');
      expect(['weak', 'medium']).toContain(strength.level);
    });

    it('should rate strong password correctly', () => {
      const strength = calculatePasswordStrength('SecurePass123!');
      expect(['strong', 'very-strong']).toContain(strength.level);
      expect(strength.score).toBeGreaterThanOrEqual(6);
    });

    it('should rate very strong password correctly', () => {
      const strength = calculatePasswordStrength('C0mpl3x!P@ssw0rd#2024');
      expect(strength.level).toBe('very-strong');
      expect(strength.score).toBeGreaterThanOrEqual(8);
    });

    it('should handle empty password', () => {
      const strength = calculatePasswordStrength('');
      expect(strength.score).toBe(0);
      expect(strength.level).toBe('weak');
    });

    it('should reward length', () => {
      const short = calculatePasswordStrength('Pass1!');
      const long = calculatePasswordStrength('VeryLongPassword1!');
      expect(long.score).toBeGreaterThan(short.score);
    });

    it('should reward character variety', () => {
      const simple = calculatePasswordStrength('password');
      const complex = calculatePasswordStrength('P@ssw0rd!');
      expect(complex.score).toBeGreaterThan(simple.score);
    });
  });

  describe('validateEmail', () => {
    it('should accept valid email addresses', () => {
      const validEmails = [
        'user@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_name@example-domain.com',
      ];

      validEmails.forEach(email => {
        expect(validateEmail(email)).toBe(true);
      });
    });

    it('should reject invalid email formats', () => {
      const invalidEmails = [
        'invalid',
        '@example.com',
        'user@',
        'user @example.com',
      ];

      invalidEmails.forEach(email => {
        expect(validateEmail(email)).toBe(false);
      });
    });

    it('should reject empty email', () => {
      expect(validateEmail('')).toBe(false);
      expect(validateEmail(null)).toBe(false);
      expect(validateEmail(undefined)).toBe(false);
    });

    it('should reject too long emails', () => {
      const longEmail = 'a'.repeat(250) + '@example.com';
      expect(validateEmail(longEmail)).toBe(false);
    });

    it('should reject too long local part', () => {
      const longLocal = 'a'.repeat(65) + '@example.com';
      expect(validateEmail(longLocal)).toBe(false);
    });

    it('should accept emails with numbers', () => {
      expect(validateEmail('user123@example.com')).toBe(true);
    });

    it('should accept emails with special characters', () => {
      expect(validateEmail('user.name+tag@example.com')).toBe(true);
    });
  });

  describe('validateUsername', () => {
    it('should accept valid usernames', () => {
      const validUsernames = ['user123', 'john_doe', 'alice-smith', 'user_name_123'];
      
      validUsernames.forEach(username => {
        const result = validateUsername(username);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject username shorter than 3 characters', () => {
      const result = validateUsername('ab');
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('at least 3'))).toBe(true);
    });

    it('should reject username longer than 30 characters', () => {
      const result = validateUsername('a'.repeat(31));
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('30 characters'))).toBe(true);
    });

    it('should reject username with special characters', () => {
      const result = validateUsername('user@name');
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('letters, numbers'))).toBe(true);
    });

    it('should reject username starting with number', () => {
      const result = validateUsername('123user');
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('cannot start with a number'))).toBe(true);
    });

    it('should reject reserved usernames', () => {
      const reserved = ['admin', 'root', 'system', 'api'];
      
      reserved.forEach(username => {
        const result = validateUsername(username);
        expect(result.isValid).toBe(false);
        expect(result.errors.some(e => e.includes('reserved'))).toBe(true);
      });
    });

    it('should accept underscores and hyphens', () => {
      expect(validateUsername('user_name').isValid).toBe(true);
      expect(validateUsername('user-name').isValid).toBe(true);
    });

    it('should handle empty username', () => {
      const result = validateUsername('');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Username is required');
    });

    it('should handle null username', () => {
      const result = validateUsername(null);
      expect(result.isValid).toBe(false);
    });
  });

  describe('sanitizeInput', () => {
    it('should escape HTML special characters', () => {
      const input = '<script>alert("xss")</script>';
      const sanitized = sanitizeInput(input);
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).toContain('&lt;');
      expect(sanitized).toContain('&gt;');
    });

    it('should escape quotes', () => {
      const input = 'He said "hello" and she said \'hi\'';
      const sanitized = sanitizeInput(input);
      expect(sanitized).toContain('&quot;');
      expect(sanitized).toContain('&#x27;');
    });

    it('should escape ampersands', () => {
      const input = 'Tom & Jerry';
      const sanitized = sanitizeInput(input);
      expect(sanitized).toBe('Tom &amp; Jerry');
    });

    it('should escape forward slashes', () => {
      const input = '</script>';
      const sanitized = sanitizeInput(input);
      expect(sanitized).toContain('&#x2F;');
    });

    it('should handle empty string', () => {
      expect(sanitizeInput('')).toBe('');
    });

    it('should handle null', () => {
      expect(sanitizeInput(null)).toBe(null);
    });

    it('should handle non-string input', () => {
      expect(sanitizeInput(123)).toBe(123);
      expect(sanitizeInput({})).toEqual({});
    });

    it('should prevent XSS attacks', () => {
      const xssAttempts = [
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        'javascript:alert(1)',
        '<iframe src="javascript:alert(1)">',
      ];

      xssAttempts.forEach(attempt => {
        const sanitized = sanitizeInput(attempt);
        expect(sanitized).not.toContain('<');
        expect(sanitized).not.toContain('>');
      });
    });
  });

  describe('validateRegistrationData', () => {
    it('should validate correct registration data', () => {
      const data = {
        email: 'user@example.com',
        username: 'johndoe',
        password: 'SecurePass123!',
        firstName: 'John',
        lastName: 'Doe',
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
      expect(result.passwordStrength).toBeDefined();
    });

    it('should reject invalid email', () => {
      const data = {
        email: 'invalid-email',
        username: 'johndoe',
        password: 'SecurePass123!',
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('email');
    });

    it('should reject invalid username', () => {
      const data = {
        email: 'user@example.com',
        username: 'ab',
        password: 'SecurePass123!',
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('username');
    });

    it('should reject weak password', () => {
      const data = {
        email: 'user@example.com',
        username: 'johndoe',
        password: 'weak',
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('password');
    });

    it('should reject too long first name', () => {
      const data = {
        email: 'user@example.com',
        username: 'johndoe',
        password: 'SecurePass123!',
        firstName: 'a'.repeat(101),
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('firstName');
    });

    it('should reject too long last name', () => {
      const data = {
        email: 'user@example.com',
        username: 'johndoe',
        password: 'SecurePass123!',
        lastName: 'a'.repeat(101),
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('lastName');
    });

    it('should validate multiple errors at once', () => {
      const data = {
        email: 'invalid',
        username: 'a',
        password: 'weak',
      };

      const result = validateRegistrationData(data);
      expect(result.isValid).toBe(false);
      expect(Object.keys(result.errors).length).toBeGreaterThan(1);
    });

    it('should include password strength for valid passwords', () => {
      const data = {
        email: 'user@example.com',
        username: 'johndoe',
        password: 'SecurePass123!',
      };

      const result = validateRegistrationData(data);
      expect(result.passwordStrength).toHaveProperty('score');
      expect(result.passwordStrength).toHaveProperty('level');
    });
  });
});
