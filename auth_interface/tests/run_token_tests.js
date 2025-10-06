#!/usr/bin/env node
/**
 * Simple test runner for token management
 * Runs basic validation tests without requiring Jest
 */

// Mock browser APIs for Node.js
global.window = {
  addEventListener: () => {},
  location: { pathname: '/test', href: '' },
  localStorage: {
    storage: {},
    getItem(key) { return this.storage[key] || null; },
    setItem(key, value) { this.storage[key] = String(value); },
    removeItem(key) { delete this.storage[key]; },
    clear() { this.storage = {}; }
  },
  sessionStorage: {
    storage: {},
    getItem(key) { return this.storage[key] || null; },
    setItem(key, value) { this.storage[key] = String(value); },
    removeItem(key) { delete this.storage[key]; },
    clear() { this.storage = {}; }
  }
};

global.document = {
  readyState: 'complete',
  addEventListener: () => {},
  body: { style: {}, appendChild: () => {}, removeChild: () => {} },
  head: { appendChild: () => {} },
  createElement: () => ({ style: {} }),
  querySelector: () => null,
  querySelectorAll: () => []
};

global.console.log = function(...args) {
  // Suppress console logs during tests
  if (process.env.VERBOSE) {
    process.stdout.write(args.join(' ') + '\n');
  }
};

// Set up global aliases
global.sessionStorage = global.window.sessionStorage;
global.localStorage = global.window.localStorage;

// Load the auth service
const fs = require('fs');
const path = require('path');

const authServicePath = path.join(__dirname, '../static/js/auth-service.js');
let authServiceCode = fs.readFileSync(authServicePath, 'utf8');

// Remove auto-initialization for testing
authServiceCode = authServiceCode.replace(/if \(typeof window !== 'undefined'\) \{[\s\S]*?\}\n\n\/\/ Export/, '// Export');

// Execute the code
eval(authServiceCode);

// Test utilities
function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`Assertion failed: ${message}\nExpected: ${expected}\nActual: ${actual}`);
  }
}

// Test suite
const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

// Token Structure Validation Tests
test('should validate correct JWT structure', () => {
  const tokenStorage = new TokenStorage();
  const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
  
  const result = tokenStorage.validateTokenStructure(validToken);
  assertEqual(result, true, 'Should validate correct JWT structure');
});

test('should reject invalid token structure', () => {
  const tokenStorage = new TokenStorage();
  
  assertEqual(tokenStorage.validateTokenStructure('invalid'), false, 'Should reject single part');
  assertEqual(tokenStorage.validateTokenStructure('invalid.token'), false, 'Should reject two parts');
  assertEqual(tokenStorage.validateTokenStructure(''), false, 'Should reject empty string');
  assertEqual(tokenStorage.validateTokenStructure(null), false, 'Should reject null');
});

test('should detect expired token', () => {
  const tokenStorage = new TokenStorage();
  const expiredTime = Math.floor(Date.now() / 1000) - 3600;
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const payload = Buffer.from(JSON.stringify({ sub: '123', exp: expiredTime })).toString('base64');
  const signature = Buffer.from('signature').toString('base64');
  const expiredToken = `${header}.${payload}.${signature}`;

  const result = tokenStorage.isTokenExpired(expiredToken);
  assertEqual(result, true, 'Should detect expired token');
});

test('should detect valid token', () => {
  const tokenStorage = new TokenStorage();
  const futureTime = Math.floor(Date.now() / 1000) + 3600;
  const header = Buffer.from(JSON.stringify({ alg: 'HS256' })).toString('base64');
  const payload = Buffer.from(JSON.stringify({ sub: '123', exp: futureTime })).toString('base64');
  const signature = Buffer.from('signature').toString('base64');
  const validToken = `${header}.${payload}.${signature}`;

  const result = tokenStorage.isTokenExpired(validToken);
  assertEqual(result, false, 'Should detect valid token');
});

test('should store token in sessionStorage by default', () => {
  const tokenStorage = new TokenStorage();
  window.sessionStorage.clear();
  window.localStorage.clear();
  
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
  
  tokenStorage.setToken(token, false);
  
  const stored = window.sessionStorage.getItem('auth_token');
  assertEqual(stored, token, 'Token should be in sessionStorage');
  assertEqual(window.localStorage.getItem('auth_token'), null, 'Token should not be in localStorage');
});

test('should store token in localStorage with rememberMe', () => {
  const tokenStorage = new TokenStorage();
  window.sessionStorage.clear();
  window.localStorage.clear();
  
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
  
  tokenStorage.setToken(token, true);
  
  const stored = window.localStorage.getItem('auth_token');
  assertEqual(stored, token, 'Token should be in localStorage');
  assertEqual(window.localStorage.getItem('remember_me'), 'true', 'Remember me flag should be set');
});

test('should retrieve token from sessionStorage', () => {
  const tokenStorage = new TokenStorage();
  const token = 'test_token_value';
  
  window.sessionStorage.setItem('auth_token', token);
  
  const retrieved = tokenStorage.getToken();
  assertEqual(retrieved, token, 'Should retrieve token from sessionStorage');
});

test('should remove all tokens', () => {
  const tokenStorage = new TokenStorage();
  
  window.sessionStorage.setItem('auth_token', 'session_token');
  window.localStorage.setItem('auth_token', 'local_token');
  
  tokenStorage.removeTokens();
  
  assertEqual(window.sessionStorage.getItem('auth_token'), null, 'SessionStorage should be cleared');
  assertEqual(window.localStorage.getItem('auth_token'), null, 'LocalStorage should be cleared');
});

test('should decode token payload', () => {
  const tokenStorage = new TokenStorage();
  const header = Buffer.from(JSON.stringify({ alg: 'HS256' })).toString('base64');
  const payloadData = { sub: '123', name: 'John Doe' };
  const payload = Buffer.from(JSON.stringify(payloadData)).toString('base64');
  const signature = Buffer.from('signature').toString('base64');
  const token = `${header}.${payload}.${signature}`;

  const decoded = tokenStorage.decodeToken(token);
  assertEqual(decoded.sub, '123', 'Should decode sub claim');
  assertEqual(decoded.name, 'John Doe', 'Should decode name claim');
});

test('should store and retrieve user data', () => {
  const tokenStorage = new TokenStorage();
  const userData = { id: '123', name: 'Test User', email: 'test@example.com' };
  
  tokenStorage.setUserData(userData);
  const retrieved = tokenStorage.getUserData();
  
  assertEqual(JSON.stringify(retrieved), JSON.stringify(userData), 'Should retrieve stored user data');
});

// Run all tests
async function runTests() {
  console.log('='.repeat(60));
  console.log('Running Token Management Tests');
  console.log('='.repeat(60));
  console.log('');

  for (const { name, fn } of tests) {
    try {
      // Clear storage before each test
      window.sessionStorage.clear();
      window.localStorage.clear();
      
      await fn();
      console.log(`✅ PASS: ${name}`);
      passed++;
    } catch (error) {
      console.log(`❌ FAIL: ${name}`);
      console.log(`   ${error.message}`);
      failed++;
    }
  }

  console.log('');
  console.log('='.repeat(60));
  console.log(`Test Results: ${passed} passed, ${failed} failed (${tests.length} total)`);
  console.log('='.repeat(60));
  
  process.exit(failed > 0 ? 1 : 0);
}

runTests();
