/**
 * Authentication Service
 * Handles secure token management, storage, and authentication state
 * 
 * @module AuthService
 * @version 1.0.0
 */

'use strict';

/**
 * Token Storage Manager
 * Handles secure storage and retrieval of authentication tokens
 */
class TokenStorage {
  constructor() {
    this.TOKEN_KEY = 'auth_token';
    this.REFRESH_TOKEN_KEY = 'refresh_token';
    this.REMEMBER_ME_KEY = 'remember_me';
    this.USER_DATA_KEY = 'user_data';
  }

  /**
   * Store authentication token
   * @param {string} token - JWT token
   * @param {boolean} rememberMe - Whether to persist in localStorage
   */
  setToken(token, rememberMe = false) {
    if (!token || typeof token !== 'string') {
      throw new Error('Invalid token format');
    }

    // Validate token structure before storing
    if (!this.validateTokenStructure(token)) {
      throw new Error('Invalid JWT token structure');
    }

    const storage = rememberMe ? localStorage : sessionStorage;
    
    // Store token
    storage.setItem(this.TOKEN_KEY, token);
    
    // Store remember me preference
    if (rememberMe) {
      localStorage.setItem(this.REMEMBER_ME_KEY, 'true');
    } else {
      localStorage.removeItem(this.REMEMBER_ME_KEY);
    }

    console.log('[TokenStorage] Token stored successfully');
  }

  /**
   * Store refresh token
   * @param {string} refreshToken - Refresh token
   * @param {boolean} rememberMe - Whether to persist in localStorage
   */
  setRefreshToken(refreshToken, rememberMe = false) {
    if (!refreshToken) return;
    
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  /**
   * Retrieve authentication token
   * @returns {string|null} JWT token or null
   */
  getToken() {
    // Check sessionStorage first (active session)
    let token = sessionStorage.getItem(this.TOKEN_KEY);
    
    // Fall back to localStorage (remember me)
    if (!token) {
      token = localStorage.getItem(this.TOKEN_KEY);
    }
    
    return token;
  }

  /**
   * Retrieve refresh token
   * @returns {string|null} Refresh token or null
   */
  getRefreshToken() {
    return sessionStorage.getItem(this.REFRESH_TOKEN_KEY) ||
           localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Remove all authentication tokens
   */
  removeTokens() {
    // Remove from both storages
    sessionStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(this.USER_DATA_KEY);
    
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.REMEMBER_ME_KEY);
    localStorage.removeItem(this.USER_DATA_KEY);
    
    console.log('[TokenStorage] All tokens removed');
  }

  /**
   * Validate JWT token structure
   * @param {string} token - Token to validate
   * @returns {boolean} Whether token has valid structure
   */
  validateTokenStructure(token) {
    if (!token || typeof token !== 'string') return false;
    
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      // Validate each part can be base64 decoded
      parts.forEach(part => {
        atob(part.replace(/-/g, '+').replace(/_/g, '/'));
      });
      return true;
    } catch (e) {
      console.error('[TokenStorage] Invalid token structure:', e);
      return false;
    }
  }

  /**
   * Check if token is expired
   * @param {string} token - JWT token
   * @returns {boolean} Whether token is expired
   */
  isTokenExpired(token) {
    if (!token) return true;

    try {
      const payload = this.decodeToken(token);
      
      if (!payload.exp) {
        console.warn('[TokenStorage] Token has no expiration');
        return false; // If no exp claim, assume not expired
      }

      // Check if token is expired (exp is in seconds, Date.now() in milliseconds)
      const isExpired = payload.exp * 1000 < Date.now();
      
      if (isExpired) {
        console.log('[TokenStorage] Token is expired');
      }
      
      return isExpired;
    } catch (e) {
      console.error('[TokenStorage] Error checking token expiration:', e);
      return true; // Assume expired on error
    }
  }

  /**
   * Check if token will expire soon
   * @param {string} token - JWT token
   * @param {number} minutesThreshold - Minutes before expiration to consider "soon"
   * @returns {boolean} Whether token expires soon
   */
  isTokenExpiringSoon(token, minutesThreshold = 5) {
    if (!token) return true;

    try {
      const payload = this.decodeToken(token);
      
      if (!payload.exp) return false;

      const expirationTime = payload.exp * 1000;
      const thresholdTime = Date.now() + (minutesThreshold * 60 * 1000);
      
      return expirationTime < thresholdTime;
    } catch (e) {
      return true;
    }
  }

  /**
   * Decode JWT token payload
   * @param {string} token - JWT token
   * @returns {Object} Decoded payload
   */
  decodeToken(token) {
    if (!token) throw new Error('No token provided');
    
    const parts = token.split('.');
    if (parts.length !== 3) throw new Error('Invalid token format');

    try {
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const decoded = JSON.parse(atob(payload));
      return decoded;
    } catch (e) {
      throw new Error('Failed to decode token: ' + e.message);
    }
  }

  /**
   * Store user data
   * @param {Object} userData - User information
   */
  setUserData(userData) {
    if (!userData) return;
    
    const storage = localStorage.getItem(this.REMEMBER_ME_KEY) === 'true' 
      ? localStorage 
      : sessionStorage;
    
    storage.setItem(this.USER_DATA_KEY, JSON.stringify(userData));
  }

  /**
   * Retrieve user data
   * @returns {Object|null} User data or null
   */
  getUserData() {
    const data = sessionStorage.getItem(this.USER_DATA_KEY) ||
                 localStorage.getItem(this.USER_DATA_KEY);
    
    if (!data) return null;
    
    try {
      return JSON.parse(data);
    } catch (e) {
      console.error('[TokenStorage] Failed to parse user data:', e);
      return null;
    }
  }

  /**
   * Check if remember me is enabled
   * @returns {boolean} Whether remember me is enabled
   */
  isRememberMeEnabled() {
    return localStorage.getItem(this.REMEMBER_ME_KEY) === 'true';
  }
}

/**
 * HTTP Client with Authentication
 * Handles API requests with automatic token injection
 */
class AuthHttpClient {
  constructor(tokenStorage) {
    this.tokenStorage = tokenStorage;
    this.baseURL = '/api'; // Configure your API base URL
    this.requestQueue = [];
    this.isRefreshing = false;
  }

  /**
   * Make authenticated API request
   * @param {string} url - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>} Fetch response
   */
  async request(url, options = {}) {
    const token = this.tokenStorage.getToken();
    
    // Prepare headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // Add authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Make request
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        ...options,
        headers
      });

      // Handle unauthorized response
      if (response.status === 401) {
        return this.handleUnauthorized(url, options);
      }

      return response;
    } catch (error) {
      console.error('[AuthHttpClient] Request failed:', error);
      throw error;
    }
  }

  /**
   * Handle 401 Unauthorized response
   * @param {string} url - Original request URL
   * @param {Object} options - Original request options
   * @returns {Promise<Response>} Retry response or rejection
   */
  async handleUnauthorized(url, options) {
    console.log('[AuthHttpClient] Handling unauthorized response');
    
    const refreshToken = this.tokenStorage.getRefreshToken();
    
    // If no refresh token, user must log in again
    if (!refreshToken) {
      throw new Error('SESSION_EXPIRED');
    }

    // If already refreshing, queue this request
    if (this.isRefreshing) {
      return new Promise((resolve, reject) => {
        this.requestQueue.push({ url, options, resolve, reject });
      });
    }

    // Start refresh process
    this.isRefreshing = true;

    try {
      // Attempt to refresh token
      const newToken = await this.refreshToken(refreshToken);
      
      // Store new token
      const rememberMe = this.tokenStorage.isRememberMeEnabled();
      this.tokenStorage.setToken(newToken, rememberMe);

      // Retry queued requests
      this.requestQueue.forEach(({ url, options, resolve }) => {
        resolve(this.request(url, options));
      });
      this.requestQueue = [];

      // Retry original request
      return this.request(url, options);
    } catch (error) {
      console.error('[AuthHttpClient] Token refresh failed:', error);
      
      // Clear queued requests
      this.requestQueue.forEach(({ reject }) => {
        reject(new Error('SESSION_EXPIRED'));
      });
      this.requestQueue = [];
      
      throw new Error('SESSION_EXPIRED');
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Refresh authentication token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<string>} New access token
   */
  async refreshToken(refreshToken) {
    console.log('[AuthHttpClient] Refreshing token');
    
    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refreshToken })
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    return data.token;
  }

  /**
   * Convenience methods for HTTP verbs
   */
  get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' });
  }

  post(url, body, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  put(url, body, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body)
    });
  }

  delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }
}

/**
 * Main Authentication Service
 * Central service for authentication operations
 */
class AuthService {
  constructor() {
    this.tokenStorage = new TokenStorage();
    this.httpClient = new AuthHttpClient(this.tokenStorage);
    this.sessionCheckInterval = null;
    this.SESSION_CHECK_INTERVAL = 60000; // Check every minute
  }

  /**
   * Initialize authentication service
   */
  init() {
    console.log('[AuthService] Initializing');
    
    // Check if there's an existing valid session
    const token = this.tokenStorage.getToken();
    if (token && !this.tokenStorage.isTokenExpired(token)) {
      console.log('[AuthService] Valid session found');
      this.startSessionMonitoring();
    } else if (token) {
      console.log('[AuthService] Expired session found, cleaning up');
      this.logout();
    }

    // Listen for storage events (multi-tab synchronization)
    window.addEventListener('storage', this.handleStorageChange.bind(this));
    
    // Listen for page visibility changes
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  /**
   * Authenticate user with credentials
   * @param {Object} credentials - Login credentials
   * @returns {Promise<Object>} Authentication result
   */
  async login(credentials) {
    console.log('[AuthService] Attempting login');
    
    try {
      // TODO: Replace with actual API endpoint
      // For now, simulating API call
      const response = await this.simulateLogin(credentials);
      
      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      
      // Validate and store token
      if (!data.token) {
        throw new Error('No token received from server');
      }

      // Store token
      this.tokenStorage.setToken(data.token, credentials.rememberMe);
      
      // Store refresh token if provided
      if (data.refreshToken) {
        this.tokenStorage.setRefreshToken(data.refreshToken, credentials.rememberMe);
      }

      // Store user data
      if (data.user) {
        this.tokenStorage.setUserData(data.user);
      }

      // Start session monitoring
      this.startSessionMonitoring();

      console.log('[AuthService] Login successful');
      
      return {
        success: true,
        user: data.user
      };
    } catch (error) {
      console.error('[AuthService] Login failed:', error);
      throw error;
    }
  }

  /**
   * Simulate login API call (replace with actual API)
   * @param {Object} credentials - Login credentials
   * @returns {Promise<Response>} Simulated response
   */
  async simulateLogin(credentials) {
    // TODO: Replace with actual API call
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simulate successful login
        const mockToken = this.generateMockToken();
        resolve({
          ok: true,
          json: async () => ({
            token: mockToken,
            refreshToken: 'mock_refresh_token',
            user: {
              email: credentials.email,
              name: 'Test User'
            }
          })
        });
      }, 500);
    });
  }

  /**
   * Generate mock JWT token for testing
   * @returns {string} Mock JWT token
   */
  generateMockToken() {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
      sub: '1234567890',
      name: 'Test User',
      email: 'test@example.com',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hour
    }));
    const signature = btoa('mock_signature');
    
    return `${header}.${payload}.${signature}`;
  }

  /**
   * Log out current user
   */
  logout() {
    console.log('[AuthService] Logging out');
    
    // Stop session monitoring
    this.stopSessionMonitoring();
    
    // Clear all tokens
    this.tokenStorage.removeTokens();
    
    // Redirect to login page
    if (window.location.pathname !== '/templates/login.html') {
      window.location.href = '/templates/login.html';
    }
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} Whether user is authenticated
   */
  isAuthenticated() {
    const token = this.tokenStorage.getToken();
    
    if (!token) return false;
    
    // Check if token is expired
    if (this.tokenStorage.isTokenExpired(token)) {
      console.log('[AuthService] Token expired');
      this.logout();
      return false;
    }
    
    return true;
  }

  /**
   * Get current user data
   * @returns {Object|null} User data or null
   */
  getCurrentUser() {
    if (!this.isAuthenticated()) return null;
    return this.tokenStorage.getUserData();
  }

  /**
   * Get current token
   * @returns {string|null} Current token or null
   */
  getToken() {
    return this.tokenStorage.getToken();
  }

  /**
   * Start monitoring session validity
   */
  startSessionMonitoring() {
    // Clear existing interval
    this.stopSessionMonitoring();
    
    console.log('[AuthService] Starting session monitoring');
    
    this.sessionCheckInterval = setInterval(() => {
      this.checkSession();
    }, this.SESSION_CHECK_INTERVAL);
  }

  /**
   * Stop monitoring session
   */
  stopSessionMonitoring() {
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
      this.sessionCheckInterval = null;
      console.log('[AuthService] Stopped session monitoring');
    }
  }

  /**
   * Check session validity
   */
  checkSession() {
    const token = this.tokenStorage.getToken();
    
    if (!token) {
      console.log('[AuthService] No token found during session check');
      this.logout();
      return;
    }

    // Check if expired
    if (this.tokenStorage.isTokenExpired(token)) {
      console.log('[AuthService] Token expired during session check');
      this.showSessionExpiredMessage();
      this.logout();
      return;
    }

    // Check if expiring soon and refresh if needed
    if (this.tokenStorage.isTokenExpiringSoon(token)) {
      console.log('[AuthService] Token expiring soon, attempting refresh');
      this.attemptTokenRefresh();
    }
  }

  /**
   * Attempt to refresh token
   */
  async attemptTokenRefresh() {
    const refreshToken = this.tokenStorage.getRefreshToken();
    
    if (!refreshToken) {
      console.log('[AuthService] No refresh token available');
      return;
    }

    try {
      const newToken = await this.httpClient.refreshToken(refreshToken);
      const rememberMe = this.tokenStorage.isRememberMeEnabled();
      this.tokenStorage.setToken(newToken, rememberMe);
      console.log('[AuthService] Token refreshed successfully');
    } catch (error) {
      console.error('[AuthService] Token refresh failed:', error);
      this.logout();
    }
  }

  /**
   * Show session expired message
   */
  showSessionExpiredMessage() {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning';
    alert.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10000; max-width: 90%; width: 400px;';
    alert.innerHTML = `
      <strong>Session Expired</strong><br>
      Your session has expired. Please log in again.
    `;
    
    document.body.appendChild(alert);
    
    // Remove after 5 seconds
    setTimeout(() => {
      alert.remove();
    }, 5000);
  }

  /**
   * Handle storage changes (multi-tab sync)
   * @param {StorageEvent} event - Storage event
   */
  handleStorageChange(event) {
    // Check if token was changed in another tab
    if (event.key === this.tokenStorage.TOKEN_KEY) {
      if (!event.newValue) {
        // Token was removed in another tab
        console.log('[AuthService] Token removed in another tab');
        this.stopSessionMonitoring();
        window.location.reload();
      } else {
        // Token was updated in another tab
        console.log('[AuthService] Token updated in another tab');
        this.startSessionMonitoring();
      }
    }
  }

  /**
   * Handle page visibility changes
   */
  handleVisibilityChange() {
    if (!document.hidden) {
      // Page became visible, check session
      console.log('[AuthService] Page visible, checking session');
      this.checkSession();
    }
  }

  /**
   * Make authenticated API request
   * @param {string} url - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>} Response
   */
  async apiRequest(url, options = {}) {
    if (!this.isAuthenticated()) {
      throw new Error('Not authenticated');
    }

    try {
      return await this.httpClient.request(url, options);
    } catch (error) {
      if (error.message === 'SESSION_EXPIRED') {
        this.showSessionExpiredMessage();
        this.logout();
      }
      throw error;
    }
  }
}

// Create and export singleton instance
const authService = new AuthService();

// Initialize on page load
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => authService.init());
  } else {
    authService.init();
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AuthService, TokenStorage, AuthHttpClient, authService };
}
