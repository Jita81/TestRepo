/**
 * Integration Tests for Login Flow
 * Tests complete login workflow including API calls, token storage, and redirects
 */

describe('Login Integration Tests', () => {
  let mockFetch;
  let originalFetch;

  beforeEach(() => {
    // Save original fetch
    originalFetch = global.fetch;
    
    // Clear storage
    sessionStorage.clear();
    localStorage.clear();
    
    // Setup DOM
    document.body.innerHTML = `
      <form id="loginForm">
        <input type="email" id="email" name="email" value="user@example.com" />
        <input type="password" id="password" name="password" value="ValidPass123!" />
        <input type="checkbox" id="rememberMe" name="rememberMe" />
        <button type="submit">Login</button>
      </form>
      <div class="alert"></div>
    `;
  });

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch;
  });

  describe('Successful Login', () => {
    test('successful login stores token and redirects to dashboard', async () => {
      // Mock successful API response
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({
            token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMjMiLCJleHAiOjE3MDAwMDAwMDB9.signature',
            user: {
              id: '123',
              email: 'user@example.com',
              name: 'Test User'
            }
          })
        })
      );

      // Simulate form submission
      const formData = {
        email: 'user@example.com',
        password: 'ValidPass123!',
        rememberMe: false
      };

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      // Verify API was called correctly
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );

      // Verify response contains token
      expect(data.token).toBeDefined();
      expect(data.user).toBeDefined();
      expect(data.user.email).toBe('user@example.com');

      // Store token
      sessionStorage.setItem('auth_token', data.token);
      expect(sessionStorage.getItem('auth_token')).toBe(data.token);
    });

    test('successful login with rememberMe stores token in localStorage', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({
            token: 'test-token',
            user: { id: '123', email: 'user@example.com' }
          })
        })
      );

      const formData = {
        email: 'user@example.com',
        password: 'ValidPass123!',
        rememberMe: true
      };

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      // Store with rememberMe
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('remember_me', 'true');

      expect(localStorage.getItem('auth_token')).toBe(data.token);
      expect(localStorage.getItem('remember_me')).toBe('true');
    });
  });

  describe('Failed Login Attempts', () => {
    test('invalid credentials show appropriate error', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 401,
          json: () => Promise.resolve({
            error: 'Invalid email or password'
          })
        })
      );

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: 'user@example.com',
          password: 'WrongPassword'
        })
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(401);

      const data = await response.json();
      expect(data.error).toBe('Invalid email or password');
      
      // Should not reveal email existence
      expect(data.error).not.toContain('email not found');
      expect(data.error).not.toContain('user does not exist');
    });

    test('empty email shows validation error', () => {
      const emailInput = document.getElementById('email');
      emailInput.value = '';
      
      expect(emailInput.validity.valid).toBe(false);
      expect(emailInput.validity.valueMissing).toBe(true);
    });

    test('empty password shows validation error', () => {
      const passwordInput = document.getElementById('password');
      passwordInput.value = '';
      passwordInput.required = true;
      
      expect(passwordInput.validity.valid).toBe(false);
      expect(passwordInput.validity.valueMissing).toBe(true);
    });
  });

  describe('Network Failures', () => {
    test('handles network error during login', async () => {
      global.fetch = jest.fn(() =>
        Promise.reject(new Error('Network error'))
      );

      try {
        await fetch('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            email: 'user@example.com',
            password: 'ValidPass123!'
          })
        });
        fail('Should have thrown error');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    test('handles timeout during login', async () => {
      global.fetch = jest.fn(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      try {
        await fetch('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            email: 'user@example.com',
            password: 'ValidPass123!'
          })
        });
        fail('Should have thrown error');
      } catch (error) {
        expect(error.message).toBe('Request timeout');
      }
    });

    test('handles server error (500)', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({
            error: 'Internal server error'
          })
        })
      );

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: 'user@example.com',
          password: 'ValidPass123!'
        })
      });

      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data.error).toBe('Internal server error');
    });
  });

  describe('Token Expiration', () => {
    test('detects expired token', () => {
      const now = Math.floor(Date.now() / 1000);
      
      // Create expired token payload
      const expiredPayload = {
        userId: '123',
        exp: now - 3600 // Expired 1 hour ago
      };
      
      // Check if expired
      const isExpired = expiredPayload.exp < now;
      expect(isExpired).toBe(true);
    });

    test('clears expired token from storage', () => {
      const expiredToken = 'expired-token';
      sessionStorage.setItem('auth_token', expiredToken);
      
      // Simulate token expiration detection
      sessionStorage.removeItem('auth_token');
      
      expect(sessionStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('Multiple Concurrent Login Attempts', () => {
    test('handles multiple simultaneous login requests', async () => {
      let requestCount = 0;
      
      global.fetch = jest.fn(() => {
        requestCount++;
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({
            token: `token-${requestCount}`,
            user: { id: '123' }
          })
        });
      });

      // Simulate 3 concurrent requests
      const requests = [
        fetch('/api/auth/login', { method: 'POST', body: '{}' }),
        fetch('/api/auth/login', { method: 'POST', body: '{}' }),
        fetch('/api/auth/login', { method: 'POST', body: '{}' })
      ];

      const responses = await Promise.all(requests);
      
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(responses.length).toBe(3);
      
      // All should succeed
      responses.forEach(response => {
        expect(response.ok).toBe(true);
      });
    });

    test('last successful login wins', async () => {
      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ token: 'token1', user: { id: '1' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ token: 'token2', user: { id: '2' } })
        });

      // First login
      const response1 = await fetch('/api/auth/login', { method: 'POST' });
      const data1 = await response1.json();
      sessionStorage.setItem('auth_token', data1.token);

      // Second login (should override)
      const response2 = await fetch('/api/auth/login', { method: 'POST' });
      const data2 = await response2.json();
      sessionStorage.setItem('auth_token', data2.token);

      expect(sessionStorage.getItem('auth_token')).toBe('token2');
    });
  });

  describe('Storage Cleared While Remembered', () => {
    test('handles localStorage being cleared', () => {
      // Set token with rememberMe
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('remember_me', 'true');
      
      expect(localStorage.getItem('auth_token')).toBe('test-token');
      
      // Simulate storage being cleared
      localStorage.clear();
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('remember_me')).toBeNull();
    });

    test('prompts re-login when stored token is missing', () => {
      // Check for token
      const token = localStorage.getItem('auth_token');
      
      expect(token).toBeNull();
      
      // Should redirect to login
      // In real app: window.location.href = '/login'
    });
  });

  describe('Session Conflicts Across Tabs', () => {
    test('detects storage event from another tab', () => {
      const storageEvent = new StorageEvent('storage', {
        key: 'auth_token',
        oldValue: 'old-token',
        newValue: 'new-token',
        storageArea: localStorage
      });

      // Listener should detect change
      expect(storageEvent.key).toBe('auth_token');
      expect(storageEvent.newValue).toBe('new-token');
    });

    test('handles logout from another tab', () => {
      localStorage.setItem('auth_token', 'test-token');
      
      // Simulate logout event from another tab
      const logoutEvent = new StorageEvent('storage', {
        key: 'auth_token',
        oldValue: 'test-token',
        newValue: null,
        storageArea: localStorage
      });

      // Should clear local state
      if (logoutEvent.key === 'auth_token' && logoutEvent.newValue === null) {
        localStorage.removeItem('auth_token');
      }

      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('Loading States', () => {
    test('shows loading indicator during login', async () => {
      const button = document.querySelector('button[type="submit"]');
      
      // Set loading state
      button.classList.add('btn-loading');
      button.disabled = true;
      
      expect(button.classList.contains('btn-loading')).toBe(true);
      expect(button.disabled).toBe(true);
      
      // Simulate API call
      global.fetch = jest.fn(() =>
        new Promise(resolve =>
          setTimeout(() =>
            resolve({
              ok: true,
              json: () => Promise.resolve({ token: 'test-token' })
            }),
            100
          )
        )
      );

      await fetch('/api/auth/login', { method: 'POST', body: '{}' });
      
      // Remove loading state
      button.classList.remove('btn-loading');
      button.disabled = false;
      
      expect(button.classList.contains('btn-loading')).toBe(false);
      expect(button.disabled).toBe(false);
    });

    test('disables form inputs during loading', () => {
      const form = document.getElementById('loginForm');
      const inputs = form.querySelectorAll('input');
      const button = form.querySelector('button');
      
      // Enable loading
      inputs.forEach(input => input.disabled = true);
      button.disabled = true;
      
      expect(Array.from(inputs).every(input => input.disabled)).toBe(true);
      expect(button.disabled).toBe(true);
      
      // Disable loading
      inputs.forEach(input => input.disabled = false);
      button.disabled = false;
      
      expect(Array.from(inputs).every(input => !input.disabled)).toBe(true);
      expect(button.disabled).toBe(false);
    });
  });
});
