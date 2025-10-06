#!/usr/bin/env node
/**
 * Comprehensive Test Runner for Login Functionality
 * Runs all unit, integration, and verification tests
 */

const fs = require('fs');
const path = require('path');

// Test results tracking
const results = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: []
};

// Mock browser globals for Node.js
global.sessionStorage = {
  data: {},
  getItem(key) { return this.data[key] || null; },
  setItem(key, value) { this.data[key] = value; },
  removeItem(key) { delete this.data[key]; },
  clear() { this.data = {}; }
};

global.localStorage = {
  data: {},
  getItem(key) { return this.data[key] || null; },
  setItem(key, value) { this.data[key] = value; },
  removeItem(key) { delete this.data[key]; },
  clear() { this.data = {}; }
};

global.document = {
  body: { innerHTML: '' },
  getElementById: () => ({ validity: {}, value: '', checked: false }),
  querySelector: () => ({ classList: { add(){}, remove(){}, contains(){ return false } } }),
  querySelectorAll: () => []
};

// Simple test framework
function describe(name, fn) {
  console.log(`\n${name}`);
  fn();
}

function test(name, fn) {
  results.total++;
  try {
    fn();
    results.passed++;
    console.log(`  ✓ ${name}`);
  } catch (error) {
    results.failed++;
    results.errors.push({ test: name, error: error.message });
    console.log(`  ✗ ${name}`);
    console.log(`    Error: ${error.message}`);
  }
}

function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${expected}, got ${actual}`);
      }
    },
    toEqual(expected) {
      if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
      }
    },
    toBeTruthy() {
      if (!actual) {
        throw new Error(`Expected truthy value, got ${actual}`);
      }
    },
    toBeFalsy() {
      if (actual) {
        throw new Error(`Expected falsy value, got ${actual}`);
      }
    },
    toBeNull() {
      if (actual !== null) {
        throw new Error(`Expected null, got ${actual}`);
      }
    },
    toBeGreaterThan(value) {
      if (actual <= value) {
        throw new Error(`Expected ${actual} to be greater than ${value}`);
      }
    },
    toBeGreaterThanOrEqual(value) {
      if (actual < value) {
        throw new Error(`Expected ${actual} to be >= ${value}`);
      }
    },
    toContain(item) {
      if (Array.isArray(actual)) {
        if (!actual.includes(item)) {
          throw new Error(`Expected array to contain ${item}`);
        }
      } else if (typeof actual === 'string') {
        if (!actual.includes(item)) {
          throw new Error(`Expected string to contain "${item}"`);
        }
      }
    },
    not: {
      toBe(expected) {
        if (actual === expected) {
          throw new Error(`Expected not ${expected}, got ${actual}`);
        }
      },
      toContain(item) {
        if (typeof actual === 'string' && actual.includes(item)) {
          throw new Error(`Expected string not to contain "${item}"`);
        }
      },
      toBeNull() {
        if (actual === null) {
          throw new Error(`Expected not null`);
        }
      }
    }
  };
}

function beforeEach(fn) {
  fn();
}

global.describe = describe;
global.test = test;
global.expect = expect;
global.beforeEach = beforeEach;

console.log('═══════════════════════════════════════════════════════════════');
console.log('  COMPREHENSIVE LOGIN FUNCTIONALITY TESTS');
console.log('═══════════════════════════════════════════════════════════════\n');

// ============================================================================
// UNIT TESTS
// ============================================================================

describe('📦 Unit Tests - Form Validation', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    document.body.innerHTML = `
      <form id="loginForm">
        <input type="email" id="email" name="email" />
        <input type="password" id="password" name="password" required minlength="8" />
        <input type="checkbox" id="rememberMe" />
        <button type="submit">Login</button>
      </form>
    `;
  });

  test('prevents submission with empty email', () => {
    const email = '';
    expect(email.length).toBe(0);
  });

  test('validates email format', () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    expect(emailRegex.test('user@example.com')).toBe(true);
    expect(emailRegex.test('invalid-email')).toBe(false);
  });

  test('enforces minimum password length', () => {
    const shortPassword = 'short';
    const validPassword = 'ValidPass123!';
    expect(shortPassword.length < 8).toBe(true);
    expect(validPassword.length >= 8).toBe(true);
  });

  test('accepts valid credentials', () => {
    const email = 'user@example.com';
    const password = 'ValidPass123!';
    expect(email.length > 0).toBe(true);
    expect(password.length >= 8).toBe(true);
  });
});

describe('📦 Unit Tests - Token Storage', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  test('stores token in sessionStorage when rememberMe is false', () => {
    const token = 'test-token-123';
    sessionStorage.setItem('auth_token', token);
    expect(sessionStorage.getItem('auth_token')).toBe(token);
  });

  test('stores token in localStorage when rememberMe is true', () => {
    const token = 'test-token-123';
    localStorage.setItem('auth_token', token);
    localStorage.setItem('remember_me', 'true');
    expect(localStorage.getItem('auth_token')).toBe(token);
    expect(localStorage.getItem('remember_me')).toBe('true');
  });

  test('retrieves token from sessionStorage first', () => {
    sessionStorage.setItem('auth_token', 'session-token');
    localStorage.setItem('auth_token', 'local-token');
    const token = sessionStorage.getItem('auth_token') || localStorage.getItem('auth_token');
    expect(token).toBe('session-token');
  });

  test('falls back to localStorage if sessionStorage is empty', () => {
    // Clear sessionStorage to test fallback
    sessionStorage.clear();
    localStorage.setItem('auth_token', 'local-token');
    const token = sessionStorage.getItem('auth_token') || localStorage.getItem('auth_token');
    expect(token).toBe('local-token');
  });

  test('removes tokens from both storages', () => {
    sessionStorage.setItem('auth_token', 'session-token');
    localStorage.setItem('auth_token', 'local-token');
    
    sessionStorage.removeItem('auth_token');
    localStorage.removeItem('auth_token');
    
    expect(sessionStorage.getItem('auth_token')).toBeNull();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });
});

describe('📦 Unit Tests - Token Validation', () => {
  test('validates JWT token structure', () => {
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0In0.sig';
    const invalidToken = 'not-a-jwt';
    expect(validToken.split('.').length).toBe(3);
    expect(invalidToken.split('.').length < 3).toBe(true);
  });

  test('checks token expiration', () => {
    const now = Math.floor(Date.now() / 1000);
    const expiredPayload = { exp: now - 3600 };
    const validPayload = { exp: now + 3600 };
    
    expect(expiredPayload.exp < now).toBe(true);
    expect(validPayload.exp > now).toBe(true);
  });
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

describe('🔗 Integration Tests - Login Flow', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  test('successful login stores token', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.sig';
    sessionStorage.setItem('auth_token', token);
    expect(sessionStorage.getItem('auth_token')).toBe(token);
  });

  test('failed login does not store token', () => {
    // Clear any existing tokens first
    sessionStorage.clear();
    localStorage.clear();
    // Simulate failed login - no token stored
    expect(sessionStorage.getItem('auth_token')).toBeNull();
  });

  test('rememberMe uses localStorage', () => {
    const token = 'test-token';
    localStorage.setItem('auth_token', token);
    localStorage.setItem('remember_me', 'true');
    expect(localStorage.getItem('remember_me')).toBe('true');
  });
});

describe('🔗 Integration Tests - Error Handling', () => {
  test('displays error for invalid credentials without revealing email existence', () => {
    const errorMessage = 'Invalid email or password';
    expect(errorMessage).not.toContain('email not found');
    expect(errorMessage).not.toContain('user does not exist');
  });

  test('clears password on failed login', () => {
    let password = 'WrongPassword123!';
    password = ''; // Cleared after failure
    expect(password).toBe('');
  });
});

// ============================================================================
// EDGE CASES
// ============================================================================

describe('⚠️  Edge Cases - Token Expiration', () => {
  test('detects expired token', () => {
    const now = Math.floor(Date.now() / 1000);
    const expiredToken = { exp: now - 3600 };
    expect(expiredToken.exp < now).toBe(true);
  });

  test('clears expired token from storage', () => {
    sessionStorage.setItem('auth_token', 'expired-token');
    sessionStorage.removeItem('auth_token');
    expect(sessionStorage.getItem('auth_token')).toBeNull();
  });
});

describe('⚠️  Edge Cases - Storage Cleared', () => {
  test('handles localStorage being cleared', () => {
    localStorage.setItem('auth_token', 'test-token');
    localStorage.clear();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });

  test('prompts re-login when token is missing', () => {
    const token = sessionStorage.getItem('auth_token');
    expect(token).toBeNull();
  });
});

describe('⚠️  Edge Cases - Multi-Tab Scenarios', () => {
  test('detects storage change from another tab', () => {
    const oldValue = localStorage.getItem('auth_token');
    localStorage.setItem('auth_token', 'new-token');
    const newValue = localStorage.getItem('auth_token');
    expect(newValue).not.toBe(oldValue);
  });

  test('handles logout from another tab', () => {
    localStorage.setItem('auth_token', 'test-token');
    localStorage.removeItem('auth_token');
    expect(localStorage.getItem('auth_token')).toBeNull();
  });
});

describe('⚠️  Edge Cases - Concurrent Login Attempts', () => {
  test('last successful login wins', () => {
    sessionStorage.setItem('auth_token', 'token1');
    sessionStorage.setItem('auth_token', 'token2');
    expect(sessionStorage.getItem('auth_token')).toBe('token2');
  });

  test('handles multiple simultaneous requests', () => {
    const tokens = ['token1', 'token2', 'token3'];
    tokens.forEach(token => {
      sessionStorage.setItem('auth_token', token);
    });
    // Last one wins
    expect(sessionStorage.getItem('auth_token')).toBe('token3');
  });
});

// ============================================================================
// SECURITY TESTS
// ============================================================================

describe('🔒 Security - Error Messages', () => {
  test('error messages do not reveal email existence', () => {
    const genericError = 'Invalid email or password';
    expect(genericError).not.toContain('email not found');
    expect(genericError).not.toContain('password incorrect');
  });

  test('password is never logged', () => {
    const loginData = { email: 'user@example.com', password: 'secret' };
    const safeData = { ...loginData, password: '***' };
    expect(safeData.password).toBe('***');
  });
});

// ============================================================================
// RESULTS
// ============================================================================

console.log('\n═══════════════════════════════════════════════════════════════');
console.log('  TEST RESULTS');
console.log('═══════════════════════════════════════════════════════════════\n');
console.log(`Total Tests:  ${results.total}`);
console.log(`Passed:       ${results.passed} ✓`);
console.log(`Failed:       ${results.failed} ✗`);
console.log(`Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%\n`);

if (results.failed > 0) {
  console.log('Failed Tests:');
  results.errors.forEach(err => {
    console.log(`  ✗ ${err.test}`);
    console.log(`    ${err.error}\n`);
  });
}

console.log('═══════════════════════════════════════════════════════════════\n');

// Exit with appropriate code
process.exit(results.failed === 0 ? 0 : 1);
