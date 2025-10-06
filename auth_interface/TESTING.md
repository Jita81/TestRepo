# Testing Guide - Responsive Authentication Interface

Complete testing documentation covering unit tests, integration tests, and E2E tests.

---

## 📋 Table of Contents

- [Test Overview](#test-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

---

## 🎯 Test Overview

### Test Coverage

| Test Type | Files | Coverage |
|-----------|-------|----------|
| Unit Tests | JavaScript validation logic | Core functions |
| Python Tests | Server rate limiting | Security features |
| E2E Tests | Complete user workflows | All pages |
| Accessibility Tests | WCAG compliance | All interfaces |
| Edge Case Tests | Virtual keyboard, rotation, etc. | All scenarios |

### Test Statistics

- **Total Test Files**: 6
- **Test Scenarios**: 100+
- **Devices Tested**: 13 (mobile, tablet, desktop)
- **Browsers**: Chrome, Firefox, Safari
- **Breakpoints**: 320px, 375px, 768px, 1024px, 1920px

---

## 🛠️ Prerequisites

### Required Software

```bash
# Node.js (v16+)
node --version

# Python 3
python3 --version

# npm
npm --version
```

### Installation

```bash
cd /workspace/auth_interface

# Install Node.js dependencies
npm install

# Install Python dependencies
pip3 install pytest pytest-cov

# Install Playwright browsers
npx playwright install
```

---

## ⚡ Quick Start

```bash
# Run all tests
npm run test:all

# Run unit tests only
npm test

# Run E2E tests only
npm run test:e2e

# Run accessibility tests only
npm run test:accessibility

# Run Python tests
python3 -m pytest tests/test_server.py -v
```

---

## 🧪 Test Types

### 1. Unit Tests (Jest)

**Location**: `tests/unit/`

Tests core JavaScript logic:
- Email validation
- Password validation
- Debounce function
- Rate limiter logic
- Viewport detection

**Run**:
```bash
npm test
npm run test:watch  # Watch mode
```

**Example**:
```javascript
test('should validate correct email formats', () => {
  expect(isValidEmail('user@example.com')).toBe(true);
  expect(isValidEmail('invalid')).toBe(false);
});
```

---

### 2. Python Unit Tests (pytest)

**Location**: `tests/test_server.py`

Tests server functionality:
- Rate limiting
- Port finding
- Security configurations

**Run**:
```bash
python3 -m pytest tests/test_server.py -v
python3 -m pytest tests/test_server.py --cov=server
```

**Example**:
```python
def test_blocks_burst_requests():
    limiter = RateLimiter()
    for i in range(10):
        allowed, msg = limiter.is_allowed('127.0.0.1')
        assert allowed is True
    
    # 11th request should be blocked
    allowed, msg = limiter.is_allowed('127.0.0.1')
    assert allowed is False
```

---

### 3. E2E Tests (Playwright)

**Location**: `tests/e2e/`

Tests complete user workflows across devices.

#### Responsive Design Tests
**File**: `responsive.spec.js`

Tests:
- Mobile layout (320px)
- Tablet layout (768px)
- Desktop layout (1920px)
- Navigation responsiveness
- Touch target sizes
- No horizontal scrolling

**Run**:
```bash
npm run test:e2e -- responsive.spec.js
```

#### Form Tests
**File**: `forms.spec.js`

Tests:
- Login form validation
- Registration form validation
- Password requirements
- Real-time validation
- Form submission

**Run**:
```bash
npm run test:e2e -- forms.spec.js
```

#### Edge Case Tests
**File**: `edge-cases.spec.js`

Tests:
- Device rotation
- Virtual keyboard behavior
- Slow network conditions
- High DPI displays
- Font size overrides
- Long content handling

**Run**:
```bash
npm run test:e2e -- edge-cases.spec.js
```

#### Accessibility Tests
**File**: `accessibility.spec.js`

Tests:
- WCAG 2.1 AAA compliance
- Keyboard navigation
- Focus indicators
- ARIA labels
- Screen reader compatibility
- Color contrast
- Touch target sizes

**Run**:
```bash
npm run test:accessibility
```

---

## 🚀 Running Tests

### Run All Tests

```bash
# Run everything
npm run test:all

# This runs:
# 1. Jest unit tests
# 2. Playwright E2E tests (all devices)
```

### Run Specific Test Suites

```bash
# Unit tests only
npm test

# E2E tests only
npm run test:e2e

# Accessibility tests only
npm run test:accessibility

# Visual regression tests
npm run test:visual
```

### Run Tests for Specific Devices

```bash
# Mobile only
npx playwright test --project="iPhone 12"

# Tablet only
npx playwright test --project="iPad"

# Desktop only
npx playwright test --project="Desktop Chrome"

# Custom viewport
npx playwright test --project="Mobile 320px"
```

### Run Tests with UI

```bash
# Interactive mode
npm run test:e2e:ui

# Headed mode (see browser)
npm run test:e2e:headed

# Debug mode
npx playwright test --debug
```

### Run Specific Test Files

```bash
# Single file
npx playwright test responsive.spec.js

# Multiple files
npx playwright test responsive.spec.js forms.spec.js

# Single test
npx playwright test -g "should validate email format"
```

---

## 📊 Test Coverage

### Generate Coverage Reports

```bash
# Jest coverage
npm test -- --coverage

# Coverage report in browser
open coverage/lcov-report/index.html
```

### Coverage Goals

| Metric | Target | Current |
|--------|--------|---------|
| Unit Tests | 80%+ | TBD |
| E2E Coverage | All pages | ✅ |
| Accessibility | WCAG AAA | ✅ |
| Devices | 10+ | ✅ 13 |
| Breakpoints | 5 | ✅ 5 |

---

## 🎯 Test Scenarios

### Critical User Flows

1. **Login Flow**
   - Navigate to login page
   - Enter valid credentials
   - Submit form
   - Verify redirect to dashboard

2. **Registration Flow**
   - Navigate to registration page
   - Fill all required fields
   - Accept terms
   - Submit form
   - Verify success message

3. **Validation Flow**
   - Enter invalid email
   - See error message
   - Correct email
   - Error disappears

### Responsive Scenarios

1. **Mobile Portrait (320px)**
   - All elements visible
   - Touch targets >= 44px
   - No horizontal scroll
   - Font size >= 16px

2. **Tablet (768px)**
   - Form centered
   - 2-column grid
   - Proper spacing

3. **Desktop (1920px)**
   - Form max-width constrained
   - 3-column grid
   - Proper margins

### Edge Case Scenarios

1. **Virtual Keyboard**
   - Focus input
   - Keyboard appears
   - Input remains visible
   - Form scrolls if needed

2. **Device Rotation**
   - Start in portrait
   - Rotate to landscape
   - Layout adjusts
   - All elements accessible

---

## 🔍 Debugging Tests

### View Test Results

```bash
# HTML report
npx playwright show-report test-results/html

# JSON report
cat test-results/results.json
```

### Debug Failed Tests

```bash
# Run with debug flag
npx playwright test --debug

# Run single test in headed mode
npx playwright test --headed -g "test name"

# Take screenshots
npx playwright test --screenshot=on
```

### Test Artifacts

After test runs, find:
- **Screenshots**: `test-results/`
- **Videos**: `test-results/`
- **Traces**: `test-results/`
- **HTML Report**: `test-results/html/`

---

## 📝 Writing New Tests

### Unit Test Template

```javascript
// tests/unit/myfeature.test.js
describe('My Feature', () => {
  test('should do something', () => {
    const result = myFunction(input);
    expect(result).toBe(expected);
  });
});
```

### E2E Test Template

```javascript
// tests/e2e/mytest.spec.js
const { test, expect } = require('@playwright/test');

test.describe('My Feature', () => {
  test('should work correctly', async ({ page }) => {
    await page.goto('/templates/login.html');
    await expect(page.locator('#element')).toBeVisible();
  });
});
```

### Accessibility Test Template

```javascript
test('should have no a11y violations', async ({ page }) => {
  await page.goto('/templates/login.html');
  
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2aa'])
    .analyze();
  
  expect(results.violations).toEqual([]);
});
```

---

## 🔄 Continuous Integration

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
          node-version: '16'
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npm test
      - run: npm run test:e2e
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/sh
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

---

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Kill process on port 8888
lsof -ti:8888 | xargs kill

# Or use different port
python3 server.py 9000
```

#### Playwright Browser Not Found

```bash
# Install browsers
npx playwright install

# Install with system dependencies
npx playwright install --with-deps
```

#### Tests Timeout

```bash
# Increase timeout
npx playwright test --timeout=60000

# Or in test file
test.setTimeout(60000);
```

#### ECONNREFUSED Error

```bash
# Ensure server is running
python3 server.py 8888

# Check server in another terminal before running tests
curl http://localhost:8888/templates/login.html
```

---

## 📈 Test Reports

### Viewing Reports

```bash
# Playwright HTML report
npx playwright show-report

# Jest coverage report
open coverage/lcov-report/index.html

# Python coverage
python3 -m pytest --cov=server --cov-report=html
open htmlcov/index.html
```

### CI Reports

Tests automatically generate:
- JUnit XML reports
- HTML reports
- Code coverage reports
- Screenshots of failures
- Video recordings of failures

---

## ✅ Test Checklist

Before merging:

- [ ] All unit tests pass
- [ ] All E2E tests pass
- [ ] Python tests pass
- [ ] Accessibility tests pass
- [ ] No new violations
- [ ] Coverage > 80%
- [ ] All devices tested
- [ ] Edge cases covered

---

## 📞 Support

For test issues:

1. Check this documentation
2. Review test output
3. Check browser console
4. Verify server is running
5. Check test artifacts (screenshots, videos)

---

**Last Updated**: 2025-10-06  
**Test Framework**: Playwright + Jest + pytest  
**Total Tests**: 100+ scenarios
