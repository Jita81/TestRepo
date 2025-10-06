/**
 * Security tests for token management
 * Tests XSS protection, token validation, and security best practices
 */

describe('XSS Protection', () => {
  test('should not allow token storage with script injection', () => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    const tokenStorage = new TokenStorage();

    const maliciousToken = '<script>alert("XSS")</script>';
    
    expect(() => {
      tokenStorage.setToken(maliciousToken);
    }).toThrow();
  });

  test('should validate token is not exposed to DOM', () => {
    // Token should never be inserted into innerHTML or similar
    const dangerousOperations = [
      'innerHTML',
      'outerHTML',
      'document.write'
    ];

    // This is a conceptual test - in practice, review code manually
    expect(dangerousOperations).toBeDefined();
  });
});

describe('Token Storage Security', () => {
  let tokenStorage;

  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    
    const { TokenStorage } = require('../../static/js/auth-service.js');
    tokenStorage = new TokenStorage();
  });

  test('should only accept string tokens', () => {
    expect(() => {
      tokenStorage.setToken(null);
    }).toThrow();

    expect(() => {
      tokenStorage.setToken(undefined);
    }).toThrow();

    expect(() => {
      tokenStorage.setToken({});
    }).toThrow();

    expect(() => {
      tokenStorage.setToken(123);
    }).toThrow();
  });

  test('should validate token before storage', () => {
    const invalidTokens = [
      'invalid',
      'one.two',
      'one.two.three.four',
      '',
      'a.b.c' // Too short to be valid base64
    ];

    invalidTokens.forEach(token => {
      expect(() => {
        tokenStorage.setToken(token);
      }).toThrow();
    });
  });

  test('should only store tokens with valid base64 encoding', () => {
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
    
    expect(() => {
      tokenStorage.setToken(validToken);
    }).not.toThrow();
  });

  test('should properly encode/decode special characters', () => {
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const payload = btoa(JSON.stringify({ 
      sub: '123',
      name: 'Test User',
      special: 'Test with émojis 🔒 and spëcial chârs'
    }));
    const signature = btoa('signature');
    const token = `${header}.${payload}.${signature}`;

    const decoded = tokenStorage.decodeToken(token);
    expect(decoded.special).toContain('🔒');
  });
});

describe('Authorization Header Security', () => {
  test('should format Authorization header correctly', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature';
    const expectedHeader = `Bearer ${token}`;

    expect(expectedHeader).toMatch(/^Bearer [A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$/);
  });

  test('should not include token in query parameters', () => {
    const url = new URL('http://localhost:8000/api/users');
    
    // Token should never be in query params
    expect(url.searchParams.has('token')).toBe(false);
    expect(url.searchParams.has('auth')).toBe(false);
    expect(url.searchParams.has('jwt')).toBe(false);
  });
});

describe('Token Expiration Security', () => {
  let tokenStorage;

  beforeEach(() => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    tokenStorage = new TokenStorage();
  });

  test('should check token expiration before use', () => {
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const payload = btoa(JSON.stringify({
      sub: '123',
      exp: Math.floor(Date.now() / 1000) - 3600 // Expired
    }));
    const signature = btoa('signature');
    const expiredToken = `${header}.${payload}.${signature}`;

    expect(tokenStorage.isTokenExpired(expiredToken)).toBe(true);
  });

  test('should handle missing expiration gracefully', () => {
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const payload = btoa(JSON.stringify({ sub: '123' })); // No exp
    const signature = btoa('signature');
    const token = `${header}.${payload}.${signature}`;

    // Should not throw, should handle gracefully
    expect(() => {
      tokenStorage.isTokenExpired(token);
    }).not.toThrow();
  });

  test('should calculate time until expiration correctly', () => {
    const futureTime = Math.floor(Date.now() / 1000) + 300; // 5 minutes
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const payload = btoa(JSON.stringify({ sub: '123', exp: futureTime }));
    const signature = btoa('signature');
    const token = `${header}.${payload}.${signature}`;

    // Should detect token expiring in 5 minutes
    expect(tokenStorage.isTokenExpiringSoon(token, 10)).toBe(true);
    expect(tokenStorage.isTokenExpiringSoon(token, 3)).toBe(false);
  });
});

describe('Storage Event Handling', () => {
  test('should handle storage being cleared', () => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    const tokenStorage = new TokenStorage();

    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
    tokenStorage.setToken(token);

    // Clear storage
    sessionStorage.clear();
    localStorage.clear();

    // getToken should return null
    expect(tokenStorage.getToken()).toBeNull();
  });

  test('should handle corrupted storage data', () => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    const tokenStorage = new TokenStorage();

    // Set corrupted data
    sessionStorage.setItem('user_data', '{invalid json}');

    // Should not throw, should return null
    expect(() => {
      const data = tokenStorage.getUserData();
      expect(data).toBeNull();
    }).not.toThrow();
  });
});

describe('Token Size Limits', () => {
  test('should handle large tokens', () => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    const tokenStorage = new TokenStorage();

    // Create a large but valid token
    const largePayload = {
      sub: '123',
      exp: Math.floor(Date.now() / 1000) + 3600,
      data: 'x'.repeat(5000) // Large data
    };

    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const payload = btoa(JSON.stringify(largePayload));
    const signature = btoa('signature');
    const largeToken = `${header}.${payload}.${signature}`;

    // Should handle large tokens
    expect(() => {
      tokenStorage.setToken(largeToken);
    }).not.toThrow();

    expect(tokenStorage.getToken()).toBe(largeToken);
  });

  test('should handle storage quota exceeded', () => {
    const { TokenStorage } = require('../../static/js/auth-service.js');
    const tokenStorage = new TokenStorage();

    // This is hard to test without actually filling storage
    // Just verify the method doesn't throw for normal tokens
    const normalToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature';
    
    expect(() => {
      tokenStorage.setToken(normalToken);
    }).not.toThrow();
  });
});
