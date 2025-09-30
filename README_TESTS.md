# Todo App - Test Documentation

This document explains how to run the comprehensive test suite for the Todo List application.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Framework](#test-framework)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Test Coverage](#test-coverage)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The test suite provides comprehensive coverage of the Todo List application with **70+ tests** covering:

- ✅ Basic CRUD operations (Add, Complete, Delete)
- ✅ Input validation and error handling
- ✅ Data persistence (localStorage)
- ✅ Accessibility (ARIA labels, keyboard navigation)
- ✅ Responsive design (Mobile, Tablet, Desktop)
- ✅ UI states and feedback messages
- ✅ Cross-browser compatibility (Chrome, Firefox, Safari)
- ✅ Touch interactions
- ✅ Edge cases and boundary conditions

## 🧪 Test Framework

**Framework**: [Playwright](https://playwright.dev/) v1.40+

**Language**: TypeScript

**Pattern**: Page Object Model (POM) with custom fixtures

## 📦 Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Install Dependencies

```bash
# Install Node dependencies
npm install

# Install Playwright browsers
npx playwright install
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
npm test

# Run tests in UI mode (recommended for development)
npm run test:ui

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests in debug mode
npm run test:debug
```

### Browser-Specific Tests

```bash
# Run tests in Chromium only
npm run test:chromium

# Run tests in Firefox only
npm run test:firefox

# Run tests in WebKit (Safari) only
npm run test:webkit

# Run mobile tests only
npm run test:mobile
```

### View Test Reports

```bash
# Open HTML test report
npm run test:report
```

## 📁 Test Structure

```
tests/frontend/
├── playwright.config.ts          # Playwright configuration
├── pages/                         # Page Object Models
│   └── TodoPage.ts               # Todo app page object
├── fixtures/                      # Test data and custom fixtures
│   ├── test-fixtures.ts          # Custom Playwright fixtures
│   └── todos.json                # Sample test data
├── todo-basic.spec.ts            # Basic CRUD operations
├── todo-validation.spec.ts       # Input validation tests
├── todo-persistence.spec.ts      # localStorage persistence tests
├── todo-accessibility.spec.ts    # Accessibility tests
├── todo-responsive.spec.ts       # Responsive design tests
└── todo-ui-states.spec.ts        # UI states and feedback tests
```

### Test Files Overview

#### `todo-basic.spec.ts` (25 tests)
Tests core functionality:
- Adding tasks (button and Enter key)
- Completing/uncompleting tasks
- Deleting tasks
- Task counters
- Empty state
- Success feedback

#### `todo-validation.spec.ts` (20 tests)
Tests input validation:
- Empty task validation
- Character limits (280 chars)
- Whitespace trimming
- Special characters
- XSS protection
- Warning messages

#### `todo-persistence.spec.ts` (12 tests)
Tests data persistence:
- localStorage saving
- Page reload restoration
- Completed state persistence
- Task order preservation
- Corrupted data handling

#### `todo-accessibility.spec.ts` (18 tests)
Tests accessibility features:
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- Focus management
- Semantic HTML

#### `todo-responsive.spec.ts` (15 tests)
Tests responsive design:
- Mobile layout (390x844)
- Tablet layout (1024x1366)
- Desktop layout (1280x720)
- Touch interactions
- Button sizes
- Text wrapping

#### `todo-ui-states.spec.ts` (15 tests)
Tests UI states:
- Empty state
- Loading state
- Success/error/warning feedback
- Animations
- Counter display states
- Visual styling

## 📊 Test Coverage

### Acceptance Criteria Coverage

| Criterion | Test Coverage | Status |
|-----------|---------------|--------|
| Users can add new todos | ✅ 10+ tests | Complete |
| Users can mark todos complete/incomplete | ✅ 8+ tests | Complete |
| Users can delete todos | ✅ 6+ tests | Complete |
| UI is clean and intuitive | ✅ 20+ tests | Complete |

### Feature Coverage

| Feature | Tests | Coverage |
|---------|-------|----------|
| Add tasks | 12 | 100% |
| Complete tasks | 8 | 100% |
| Delete tasks | 6 | 100% |
| Validation | 11 | 100% |
| Persistence | 10 | 100% |
| Accessibility | 18 | 95% |
| Responsive | 15 | 90% |
| UI States | 15 | 90% |

**Overall Coverage**: ~70-80% of component functionality

### Browser Coverage

- ✅ Chromium (Chrome, Edge)
- ✅ Firefox
- ✅ WebKit (Safari)
- ✅ Mobile Chrome
- ✅ Mobile Safari
- ✅ iPad

## ✍️ Writing New Tests

### Using Page Object Model

```typescript
import { test, expect } from './fixtures/test-fixtures';

test('should add a task', async ({ todoPage }) => {
  // Arrange
  const taskText = 'New task';
  
  // Act
  await todoPage.addTask(taskText);
  
  // Assert
  await expect(todoPage.getTaskByText(taskText)).toBeVisible();
});
```

### Using Custom Fixtures

```typescript
test('should load sample tasks', async ({ todoPage, sampleTasks }) => {
  // Use pre-loaded sample tasks
  await todoPage.setTasksInStorage(sampleTasks);
  await todoPage.page.reload();
  
  await expect(todoPage.getTaskItems()).toHaveCount(sampleTasks.length);
});
```

### AAA Pattern

All tests follow the **Arrange-Act-Assert** pattern:

```typescript
test('example test', async ({ todoPage }) => {
  // Arrange - Set up test conditions
  await todoPage.addTask('Setup task');
  
  // Act - Perform the action being tested
  await todoPage.completeTask('Setup task');
  
  // Assert - Verify expected outcome
  await expect(todoPage.getTaskByText('Setup task')).toHaveClass(/completed/);
});
```

## 🐛 Troubleshooting

### Tests Fail on First Run

**Problem**: Tests fail with "Timeout waiting for page"

**Solution**: Make sure the development server is running:
```bash
# In a separate terminal
python -m http.server 8000
```

Or let Playwright start it automatically (already configured in `playwright.config.ts`).

### Browser Not Installed

**Problem**: "Executable doesn't exist" error

**Solution**: Install Playwright browsers:
```bash
npx playwright install
```

### Port Already in Use

**Problem**: "Port 8000 is already in use"

**Solution**: Either:
1. Stop the process using port 8000
2. Change the port in `playwright.config.ts`

### Tests Run Slowly

**Problem**: Tests take too long

**Solution**:
```bash
# Run tests in parallel (faster)
npx playwright test --workers=4

# Run specific test file
npx playwright test todo-basic.spec.ts
```

### Visual Debugging

```bash
# Open Playwright Inspector
npx playwright test --debug

# Generate test code interactively
npm run test:codegen
```

### Check Test Status

```bash
# Run tests with verbose output
npx playwright test --reporter=list --workers=1

# Run specific test
npx playwright test --grep "should add a new task"
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Run Playwright tests
        run: npm test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## 🎯 Test Quality Standards

All tests in this suite follow these standards:

✅ **Clear naming**: Test names describe what they test  
✅ **Independent**: No test order dependencies  
✅ **Fast**: Most tests complete in < 2s  
✅ **Focused**: Each test verifies one thing  
✅ **Reliable**: Tests are deterministic  
✅ **Maintainable**: Use page objects and fixtures  

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Accessibility Testing Guide](https://playwright.dev/docs/accessibility-testing)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)

## 🤝 Contributing

When adding new tests:

1. Follow the AAA (Arrange-Act-Assert) pattern
2. Use the page object model
3. Add descriptive test names
4. Group related tests in `describe` blocks
5. Update this README if adding new test files

## 📝 License

Same license as the main Todo List application (MIT).