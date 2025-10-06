/**
 * Unit tests for Authentication Service
 * Tests token management, storage, and authentication flows
 */

describe('TokenStorage', () => {
  let tokenStorage;

  beforeEach(() => {
    // Clear storage before each test
    sessionStorage.clear();
    localStorage.clear();
    
    // Import TokenStorage from auth-service.js
    const { TokenStorage } = require('../../static/js/auth-service.js');
    tokenStorage = new TokenStorage();
  });

  describe('Token Structure Validation', () => {
    test('should validate correct JWT structure', () => {
      const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
      expect(tokenStorage.validateTokenStructure(validToken)).toBe(true);
    });

    test('should reject invalid token structure', () => {
      expect(tokenStorage.validateTokenStructure('invalid')).toBe(false);
      expect(tokenStorage.validateTokenStructure('invalid.token')).toBe(false);
      expect(tokenStorage.validateTokenStructure('')).toBe(false);
      expect(tokenStorage.validateTokenStructure(null)).toBe(false);
    });

    test('should reject token with wrong number of parts', () => {
      expect(tokenStorage.validateTokenStructure('part1.part2')).toBe(false);
      expect(tokenStorage.validateTokenStructure('part1.part2.part3.part4')).toBe(false);
    });
  });

  describe('Token Storage', () => {
    const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

    test('should store token in sessionStorage by default', () => {
      tokenStorage.setToken(mockToken, false);
      expect(sessionStorage.getItem('auth_token')).toBe(mockToken);
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    test('should store token in localStorage when rememberMe is true', () => {
      tokenStorage.setToken(mockToken, true);
      expect(localStorage.getItem('auth_token')).toBe(mockToken);
      expect(localStorage.getItem('remember_me')).toBe('true');
    });

    test('should retrieve token from sessionStorage', () => {
      sessionStorage.setItem('auth_token', mockToken);
      expect(tokenStorage.getToken()).toBe(mockToken);
    });

    test('should retrieve token from localStorage if not in sessionStorage', () => {
      localStorage.setItem('auth_token', mockToken);
      expect(tokenStorage.getToken()).toBe(mockToken);
    });

    test('should prioritize sessionStorage over localStorage', () => {
      const sessionToken = 'session_token';
      const localToken = 'local_token';
      
      sessionStorage.setItem('auth_token', sessionToken);
      localStorage.setItem('auth_token', localToken);
      
      expect(tokenStorage.getToken()).toBe(sessionToken);
    });

    test('should remove tokens from both storages', () => {
      const token = mockToken;
      
      sessionStorage.setItem('auth_token', token);
      localStorage.setItem('auth_token', token);
      
      tokenStorage.removeTokens();
      
      expect(sessionStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    test('should throw error for invalid token', () => {
      expect(() => {
        tokenStorage.setToken('invalid.token');
      }).toThrow();
    });
  });

  describe('Token Expiration', () => {
    test('should detect expired token', () => {
      // Create token that expired 1 hour ago
      const expiredTime = Math.floor(Date.now() / 1000) - 3600;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: expiredTime }));
      const signature = btoa('signature');
      const expiredToken = `${header}.${payload}.${signature}`;

      expect(tokenStorage.isTokenExpired(expiredToken)).toBe(true);
    });

    test('should detect valid (not expired) token', () => {
      // Create token that expires in 1 hour
      const futureTime = Math.floor(Date.now() / 1000) + 3600;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: futureTime }));
      const signature = btoa('signature');
      const validToken = `${header}.${payload}.${signature}`;

      expect(tokenStorage.isTokenExpired(validToken)).toBe(false);
    });

    test('should detect token expiring soon', () => {
      // Create token that expires in 2 minutes
      const soonTime = Math.floor(Date.now() / 1000) + 120;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: soonTime }));
      const signature = btoa('signature');
      const soonToken = `${header}.${payload}.${signature}`;

      expect(tokenStorage.isTokenExpiringSoon(soonToken, 5)).toBe(true);
    });

    test('should not consider token expiring soon if far in future', () => {
      // Create token that expires in 1 hour
      const futureTime = Math.floor(Date.now() / 1000) + 3600;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: futureTime }));
      const signature = btoa('signature');
      const validToken = `${header}.${payload}.${signature}`;

      expect(tokenStorage.isTokenExpiringSoon(validToken, 5)).toBe(false);
    });

    test('should handle token without expiration claim', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', name: 'Test' }));
      const signature = btoa('signature');
      const noExpToken = `${header}.${payload}.${signature}`;

      // Token without exp should be considered valid
      expect(tokenStorage.isTokenExpired(noExpToken)).toBe(false);
    });
  });

  describe('Token Decoding', () => {
    test('should decode valid JWT token', () => {
      const expectedPayload = { sub: '123', name: 'John Doe', iat: 1516239022 };
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify(expectedPayload));
      const signature = btoa('signature');
      const token = `${header}.${payload}.${signature}`;

      const decoded = tokenStorage.decodeToken(token);
      expect(decoded).toEqual(expectedPayload);
    });

    test('should throw error for invalid token', () => {
      expect(() => {
        tokenStorage.decodeToken('invalid.token');
      }).toThrow();
    });

    test('should throw error for null token', () => {
      expect(() => {
        tokenStorage.decodeToken(null);
      }).toThrow();
    });
  });

  describe('User Data Storage', () => {
    test('should store and retrieve user data', () => {
      const userData = { id: '123', name: 'John Doe', email: 'john@example.com' };
      
      tokenStorage.setUserData(userData);
      const retrieved = tokenStorage.getUserData();
      
      expect(retrieved).toEqual(userData);
    });

    test('should return null for non-existent user data', () => {
      expect(tokenStorage.getUserData()).toBeNull();
    });

    test('should handle invalid JSON in storage', () => {
      sessionStorage.setItem('user_data', 'invalid json');
      expect(tokenStorage.getUserData()).toBeNull();
    });

    test('should store user data in localStorage when remember me is enabled', () => {
      localStorage.setItem('remember_me', 'true');
      const userData = { id: '123', name: 'John Doe' };
      
      tokenStorage.setUserData(userData);
      
      expect(localStorage.getItem('user_data')).toBeTruthy();
    });
  });

  describe('Remember Me Functionality', () => {
    test('should detect remember me is enabled', () => {
      localStorage.setItem('remember_me', 'true');
      expect(tokenStorage.isRememberMeEnabled()).toBe(true);
    });

    test('should detect remember me is disabled', () => {
      expect(tokenStorage.isRememberMeEnabled()).toBe(false);
    });

    test('should remove remember me flag', () => {
      localStorage.setItem('remember_me', 'true');
      tokenStorage.removeTokens();
      expect(tokenStorage.isRememberMeEnabled()).toBe(false);
    });
  });

  describe('Refresh Token Management', () => {
    const refreshToken = 'refresh_token_value';

    test('should store refresh token', () => {
      tokenStorage.setRefreshToken(refreshToken, false);
      expect(sessionStorage.getItem('refresh_token')).toBe(refreshToken);
    });

    test('should store refresh token in localStorage with remember me', () => {
      tokenStorage.setRefreshToken(refreshToken, true);
      expect(localStorage.getItem('refresh_token')).toBe(refreshToken);
    });

    test('should retrieve refresh token', () => {
      sessionStorage.setItem('refresh_token', refreshToken);
      expect(tokenStorage.getRefreshToken()).toBe(refreshToken);
    });

    test('should remove refresh token on removeTokens', () => {
      sessionStorage.setItem('refresh_token', refreshToken);
      tokenStorage.removeTokens();
      expect(tokenStorage.getRefreshToken()).toBeNull();
    });
  });
});

describe('AuthService', () => {
  let authService;

  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    
    const { AuthService } = require('../../static/js/auth-service.js');
    authService = new AuthService();
  });

  describe('Authentication State', () => {
    test('should return false for isAuthenticated when no token', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });

    test('should return true for isAuthenticated with valid token', () => {
      // Create valid token
      const futureTime = Math.floor(Date.now() / 1000) + 3600;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: futureTime }));
      const signature = btoa('signature');
      const token = `${header}.${payload}.${signature}`;

      sessionStorage.setItem('auth_token', token);
      expect(authService.isAuthenticated()).toBe(true);
    });

    test('should return false and logout for expired token', () => {
      // Create expired token
      const expiredTime = Math.floor(Date.now() / 1000) - 3600;
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ sub: '123', exp: expiredTime }));
      const signature = btoa('signature');
      const expiredToken = `${header}.${payload}.${signature}`;

      sessionStorage.setItem('auth_token', expiredToken);
      expect(authService.isAuthenticated()).toBe(false);
      expect(sessionStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('Login', () => {
    test('should store token after successful login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'Test123!@#',
        rememberMe: false
      };

      await authService.login(credentials);
      
      const token = authService.getToken();
      expect(token).toBeTruthy();
      expect(token.split('.').length).toBe(3); // Valid JWT structure
    });

    test('should store user data after login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'Test123!@#',
        rememberMe: false
      };

      await authService.login(credentials);
      
      const user = authService.getCurrentUser();
      expect(user).toBeTruthy();
      expect(user.email).toBe(credentials.email);
    });

    test('should use localStorage when remember me is true', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'Test123!@#',
        rememberMe: true
      };

      await authService.login(credentials);
      
      expect(localStorage.getItem('auth_token')).toBeTruthy();
      expect(localStorage.getItem('remember_me')).toBe('true');
    });
  });

  describe('Logout', () => {
    test('should remove all tokens on logout', () => {
      const token = 'test_token';
      sessionStorage.setItem('auth_token', token);
      sessionStorage.setItem('user_data', JSON.stringify({ id: '123' }));
      
      authService.logout();
      
      expect(sessionStorage.getItem('auth_token')).toBeNull();
      expect(sessionStorage.getItem('user_data')).toBeNull();
    });

    test('should stop session monitoring on logout', () => {
      authService.startSessionMonitoring();
      expect(authService.sessionCheckInterval).toBeTruthy();
      
      authService.logout();
      
      expect(authService.sessionCheckInterval).toBeNull();
    });
  });

  describe('Session Monitoring', () => {
    test('should start session monitoring', () => {
      authService.startSessionMonitoring();
      expect(authService.sessionCheckInterval).toBeTruthy();
      authService.stopSessionMonitoring(); // Cleanup
    });

    test('should stop session monitoring', () => {
      authService.startSessionMonitoring();
      authService.stopSessionMonitoring();
      expect(authService.sessionCheckInterval).toBeNull();
    });

    test('should check session periodically', (done) => {
      const checkSession = jest.spyOn(authService, 'checkSession');
      
      authService.startSessionMonitoring();
      
      // Wait for at least one check
      setTimeout(() => {
        authService.stopSessionMonitoring();
        done();
      }, 100);
    });
  });

  describe('Current User', () => {
    test('should return null when not authenticated', () => {
      expect(authService.getCurrentUser()).toBeNull();
    });

    test('should return user data when authenticated', () => {
      const futureTime = Math.floor(Date.now() / 1000) + 3600;
      const token = `${btoa('{}')}.${btoa(JSON.stringify({ exp: futureTime }))}.${btoa('sig')}`;
      const userData = { id: '123', name: 'Test User' };
      
      sessionStorage.setItem('auth_token', token);
      sessionStorage.setItem('user_data', JSON.stringify(userData));
      
      const user = authService.getCurrentUser();
      expect(user).toEqual(userData);
    });
  });
});
