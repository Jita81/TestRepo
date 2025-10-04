# 🚀 How to Run Tests

Quick guide to running all tests for the Task Management System.

## Prerequisites

```bash
# Backend
cd backend
npm install

# Frontend
cd frontend
npm install
npm run playwright:install  # For E2E tests
```

## Backend Tests

### 1. Unit Tests (✅ ALL PASSING)
```bash
cd backend

# Run all unit tests
npm run test:unit

# Expected output:
# Test Suites: 2 passed, 2 total
# Tests:       36 passed, 36 total
# Time:        ~3.5s
```

**Tests Included:**
- JWT utilities (16 tests)
- User model (20 tests)

### 2. Integration Tests (⚠️ 90% PASSING)
```bash
cd backend

# Run all integration tests
npm run test:integration

# Expected output:
# Test Suites: 3 total
# Tests:       56 passed, 6 failed, 62 total
# Time:        ~16s
```

**Tests Included:**
- Authentication API (28 tests)
- Tasks API (23 tests)
- WebSocket (9 tests)

**Note:** 6 tests fail due to environment setup (database, Redis). They pass with proper configuration.

### 3. All Backend Tests
```bash
cd backend

# Run everything
npm test

# With coverage
npm run test:coverage

# Watch mode (for development)
npm run test:watch
```

## Frontend Tests

### 1. Unit Tests (✅ READY)
```bash
cd frontend

# Run unit tests
npm test

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage
```

**Tests Included:**
- WebSocket service (20+ tests)

### 2. E2E Tests with Playwright (✅ READY)
```bash
cd frontend

# Install browsers (first time only)
npm run playwright:install

# Run all E2E tests
npm run test:e2e

# Run with UI (interactive)
npm run test:e2e:ui

# Run headed (see browser)
npm run test:e2e:headed

# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

**Tests Included:**
- Authentication flow (12 tests)
- Dashboard navigation (10 tests)
- Real-time features (10 tests)

**Note:** Some E2E tests are skipped because they require a running backend. Start backend server first to run all E2E tests.

## Running Tests for Development

### Continuous Testing (Watch Mode)

**Terminal 1 - Backend:**
```bash
cd backend
npm run test:watch
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run test:watch
```

This will automatically re-run tests when you change files.

### Test Specific Files

**Backend:**
```bash
cd backend

# Specific file
npm test -- jwt.test.js

# Specific test by name
npm test -- -t "should generate valid token"

# All tests in a directory
npm test tests/unit/
```

**Frontend:**
```bash
cd frontend

# Specific file
npm test websocket.test.jsx

# Specific test
npm test -- -t "should connect"
```

## Viewing Test Coverage

### Backend Coverage
```bash
cd backend
npm run test:coverage

# Open coverage report
# Linux/Mac: open coverage/lcov-report/index.html
# Windows: start coverage/lcov-report/index.html
```

### Frontend Coverage
```bash
cd frontend
npm run test:coverage

# Open coverage report
open coverage/index.html
```

## Expected Results

### ✅ What Should Pass

1. **All Unit Tests** (36/36)
   - JWT utilities
   - User model

2. **Most Integration Tests** (56/62)
   - Authentication endpoints
   - Task CRUD operations
   - Basic WebSocket functionality

3. **All Frontend Unit Tests**
   - WebSocket service

4. **Most E2E Tests**
   - Login/register flows
   - Dashboard navigation
   - Responsive design

### ⚠️ What Might Fail (Known Issues)

1. **Integration Tests** (6 tests)
   - Require test database setup
   - Require Redis server
   - WebSocket tests need server running
   - **Solution:** Start PostgreSQL and Redis before running

2. **Some E2E Tests** (marked as `.skip()`)
   - Need running backend server
   - Require real data
   - **Solution:** Start backend with `npm run dev` first

## Debugging Failed Tests

### Enable Verbose Output
```bash
npm test -- --verbose
```

### Run Single Test
```bash
npm test -- -t "exact test name"
```

### Debug in Node Inspector
```bash
node --inspect-brk node_modules/.bin/jest --runInBand specific.test.js
```

### Show Console Logs
Jest/Vitest suppress console.log by default. They will show if tests fail.

## Common Issues

### "Cannot find module"
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Jest cache
npm test -- --clearCache
```

### "Port already in use"
```bash
# Kill process on port
lsof -ti:3000 | xargs kill -9  # Backend
lsof -ti:3001 | xargs kill -9  # Frontend
```

### "Test timeout"
```bash
# Increase timeout
npm test -- --testTimeout=20000
```

### Playwright Issues
```bash
# Reinstall browsers
npx playwright install

# Install with dependencies
npx playwright install --with-deps
```

## Quick Test Summary

Run this command to get a quick overview:

```bash
cd backend && echo "=== Backend Unit Tests ===" && npm run test:unit && echo "\n=== Backend Integration Tests ===" && npm run test:integration
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      # Backend tests
      - run: cd backend && npm ci
      - run: cd backend && npm run test:unit
      - run: cd backend && npm run test:coverage
      
      # Frontend tests
      - run: cd frontend && npm ci
      - run: cd frontend && npm test
```

## Test Results

See [TEST_RESULTS.md](./TEST_RESULTS.md) for detailed test results and coverage reports.

## Quick Commands Reference

```bash
# Backend
npm run test:unit          # Unit tests only (FAST ✅)
npm run test:integration   # Integration tests (needs DB)
npm test                   # All tests
npm run test:coverage      # With coverage report
npm run test:watch         # Watch mode

# Frontend
npm test                   # Unit tests
npm run test:e2e          # E2E tests (needs backend)
npm run test:e2e:ui       # E2E with UI
npm run test:coverage      # With coverage
npm run test:watch         # Watch mode

# Specific
npm test -- jwt.test.js    # Single file
npm test -- -t "pattern"   # By name
```

---

**Ready to test!** 🚀

For detailed results, see [TEST_RESULTS.md](./TEST_RESULTS.md)

For test documentation, see [TESTING.md](./TESTING.md)
