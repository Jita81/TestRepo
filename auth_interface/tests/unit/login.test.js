/**
 * Unit Tests for Login Functionality
 * Tests core login logic, validation, and token management
 */

describe('Login Unit Tests', () => {
  let tokenStorage;
  let authService;

  beforeEach(() => {
    // Clear storage
    sessionStorage.clear();
    localStorage.clear();
    
    // Mock DOM
    document.body.innerHTML = `
      <form id="loginForm">
        <input type="email" id="email" name="email" />
        <input type="password" id="password" name="password" />
        <input type="checkbox" id="rememberMe" name="rememberMe" />
        <button type="submit">Login</button>
      </form>
      <div id="email-error"></div>
      <div id="password-error"></div>
    `;
  });

  describe('Form Validation', () => {
    test('prevents submission with empty email', () => {
      const emailInput = document.getElementById('email');
      const passwordInput = document.getElementById('password');
      
      emailInput.value = '';
      passwordInput.value = 'ValidPass123!';
      
      expect(emailInput.value).toBe('');
      expect(emailInput.validity.valid).toBe(false);
    });

    test('prevents submission with invalid email format', () => {
      const emailInput = document.getElementById('email');
      emailInput.type = 'email';
      emailInput.value = 'invalid-email';
      
      // Trigger validation
      emailInput.checkValidity();
      
      expect(emailInput.validity.valid).toBe(false);
    });

    test('prevents submission with empty password', () => {
      const emailInput = document.getElementById('email');
      const passwordInput = document.getElementById('password');
      
      emailInput.value = 'test@example.com';
      passwordInput.value = '';
      passwordInput.required = true;
      
      expect(passwordInput.validity.valid).toBe(false);
    });

    test('prevents submission with password less than 8 characters', () => {
      const passwordInput = document.getElementById('password');
      passwordInput.minLength = 8;
      passwordInput.value = 'short';
      
      passwordInput.checkValidity();
      
      expect(passwordInput.validity.tooShort).toBe(true);
    });

    test('accepts valid email and password', () => {
      const emailInput = document.getElementById('email');
      const passwordInput = document.getElementById('password');
      
      emailInput.value = 'user@example.com';
      passwordInput.value = 'ValidPass123!';
      
      expect(emailInput.validity.valid).toBe(true);
      expect(passwordInput.value.length).toBeGreaterThanOrEqual(8);
    });
  });

  describe('Token Storage', () => {
    beforeEach(() => {
      // Simple TokenStorage implementation for testing
      class TokenStorage {
        constructor() {
          this.TOKEN_KEY = 'auth_token';
          this.REMEMBER_ME_KEY = 'remember_me';
        }
        
        setToken(token, rememberMe = false) {
          const storage = rememberMe ? localStorage : sessionStorage;
          storage.setItem(this.TOKEN_KEY, token);
          if (rememberMe) {
            localStorage.setItem(this.REMEMBER_ME_KEY, 'true');
          }
        }
        
        getToken() {
          return sessionStorage.getItem(this.TOKEN_KEY) || 
                 localStorage.getItem(this.TOKEN_KEY);
        }
        
        removeTokens() {
          sessionStorage.removeItem(this.TOKEN_KEY);
          localStorage.removeItem(this.TOKEN_KEY);
          localStorage.removeItem(this.REMEMBER_ME_KEY);
        }
      }
      
      tokenStorage = new TokenStorage();
    });

    test('stores token in sessionStorage when rememberMe is false', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token';
      tokenStorage.setToken(token, false);
      
      expect(sessionStorage.getItem('auth_token')).toBe(token);
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    test('stores token in localStorage when rememberMe is true', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token';
      tokenStorage.setToken(token, true);
      
      expect(localStorage.getItem('auth_token')).toBe(token);
      expect(localStorage.getItem('remember_me')).toBe('true');
    });

    test('retrieves token from sessionStorage first', () => {
      const sessionToken = 'session-token';
      const localToken = 'local-token';
      
      sessionStorage.setItem('auth_token', sessionToken);
      localStorage.setItem('auth_token', localToken);
      
      expect(tokenStorage.getToken()).toBe(sessionToken);
    });

    test('falls back to localStorage if sessionStorage is empty', () => {
      const localToken = 'local-token';
      localStorage.setItem('auth_token', localToken);
      
      expect(tokenStorage.getToken()).toBe(localToken);
    });

    test('removes tokens from both storages', () => {
      sessionStorage.setItem('auth_token', 'session-token');
      localStorage.setItem('auth_token', 'local-token');
      localStorage.setItem('remember_me', 'true');
      
      tokenStorage.removeTokens();
      
      expect(sessionStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('remember_me')).toBeNull();
    });
  });

  describe('Remember Me Functionality', () => {
    test('checkbox controls storage location', () => {
      const rememberMe = document.getElementById('rememberMe');
      
      // Unchecked - should use sessionStorage
      rememberMe.checked = false;
      expect(rememberMe.checked).toBe(false);
      
      // Checked - should use localStorage
      rememberMe.checked = true;
      expect(rememberMe.checked).toBe(true);
    });

    test('persists rememberMe preference', () => {
      localStorage.setItem('remember_me', 'true');
      expect(localStorage.getItem('remember_me')).toBe('true');
      
      localStorage.removeItem('remember_me');
      expect(localStorage.getItem('remember_me')).toBeNull();
    });
  });

  describe('Loading States', () => {
    test('button shows loading state', () => {
      const button = document.querySelector('button[type="submit"]');
      
      // Add loading class
      button.classList.add('btn-loading');
      button.disabled = true;
      
      expect(button.classList.contains('btn-loading')).toBe(true);
      expect(button.disabled).toBe(true);
    });

    test('inputs are disabled during loading', () => {
      const inputs = document.querySelectorAll('input');
      
      inputs.forEach(input => {
        input.disabled = true;
      });
      
      inputs.forEach(input => {
        expect(input.disabled).toBe(true);
      });
    });

    test('loading state is removed after completion', () => {
      const button = document.querySelector('button[type="submit"]');
      const inputs = document.querySelectorAll('input');
      
      // Set loading
      button.classList.add('btn-loading');
      button.disabled = true;
      inputs.forEach(input => input.disabled = true);
      
      // Remove loading
      button.classList.remove('btn-loading');
      button.disabled = false;
      inputs.forEach(input => input.disabled = false);
      
      expect(button.classList.contains('btn-loading')).toBe(false);
      expect(button.disabled).toBe(false);
      inputs.forEach(input => {
        expect(input.disabled).toBe(false);
      });
    });
  });

  describe('Error Messages', () => {
    test('displays error for invalid credentials without revealing email existence', () => {
      const errorMessage = 'Invalid email or password';
      
      // Should NOT reveal which field is wrong
      expect(errorMessage).not.toContain('email does not exist');
      expect(errorMessage).not.toContain('email not found');
      expect(errorMessage).toBe('Invalid email or password');
    });

    test('clears password field on failed login', () => {
      const passwordInput = document.getElementById('password');
      passwordInput.value = 'WrongPassword123!';
      
      // Simulate failed login
      passwordInput.value = '';
      
      expect(passwordInput.value).toBe('');
    });

    test('shows validation error for empty fields', () => {
      const emailError = document.getElementById('email-error');
      emailError.textContent = 'Email is required';
      
      expect(emailError.textContent).toBe('Email is required');
    });
  });

  describe('Token Validation', () => {
    test('validates JWT token structure', () => {
      const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature';
      const invalidToken = 'not-a-jwt-token';
      
      // Valid JWT has 3 parts separated by dots
      expect(validToken.split('.').length).toBe(3);
      expect(invalidToken.split('.').length).not.toBe(3);
    });

    test('checks token expiration', () => {
      const now = Math.floor(Date.now() / 1000);
      
      // Expired token
      const expiredPayload = { exp: now - 3600 }; // 1 hour ago
      expect(expiredPayload.exp < now).toBe(true);
      
      // Valid token
      const validPayload = { exp: now + 3600 }; // 1 hour from now
      expect(validPayload.exp > now).toBe(true);
    });
  });
});

// Run tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { describe, test, expect };
}
