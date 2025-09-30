# Playwright Tests - Quick Reference

## 🚀 Common Commands

```bash
# Setup (one-time)
npm install
npx playwright install

# Run all tests
npm test

# Interactive mode (recommended)
npm run test:ui

# Headed mode (see browser)
npm run test:headed

# Debug mode
npm run test:debug

# Specific browser
npm run test:chromium
npm run test:firefox
npm run test:webkit

# Mobile only
npm run test:mobile

# View last report
npm run test:report

# Generate test code
npm run test:codegen
```

## 📂 File Locations

```
tests/frontend/
├── pages/TodoPage.ts         - Page object with helper methods
├── fixtures/
│   ├── test-fixtures.ts      - Custom Playwright fixtures
│   └── todos.json            - Test data
├── todo-basic.spec.ts        - CRUD operations
├── todo-validation.spec.ts   - Input validation
├── todo-persistence.spec.ts  - localStorage tests
├── todo-accessibility.spec.ts - ARIA & keyboard
├── todo-responsive.spec.ts   - Mobile/tablet/desktop
└── todo-ui-states.spec.ts    - UI feedback & states
```

## 📝 Writing Tests

### Basic Test

```typescript
import { test, expect } from './fixtures/test-fixtures';

test('test name', async ({ todoPage }) => {
  // Arrange
  await todoPage.addTask('Setup task');
  
  // Act
  await todoPage.completeTask('Setup task');
  
  // Assert
  await expect(todoPage.getTaskByText('Setup task'))
    .toHaveClass(/completed/);
});
```

### Using Fixtures

```typescript
test('with sample data', async ({ todoPage, sampleTasks }) => {
  await todoPage.setTasksInStorage(sampleTasks);
  await todoPage.page.reload();
  
  await expect(todoPage.getTaskItems())
    .toHaveCount(sampleTasks.length);
});
```

## 🔧 TodoPage Methods

### Navigation
```typescript
await todoPage.goto()
```

### Adding Tasks
```typescript
await todoPage.addTask('Task text')
await todoPage.addTaskWithEnter('Task text')
await todoPage.fillInput('Text without submitting')
```

### Task Actions
```typescript
await todoPage.completeTask('Task text')
await todoPage.deleteTask('Task text')
await todoPage.completeTaskByIndex(0)
await todoPage.deleteTaskByIndex(0)
```

### Queries
```typescript
todoPage.getTaskItems()              // All tasks
todoPage.getTaskByText('text')       // Specific task
todoPage.getTaskByIndex(0)           // Task by index
await todoPage.getTaskCount()        // Number of tasks
await todoPage.isTaskCompleted('text') // Check if completed
await todoPage.getAllTaskTexts()     // Array of task texts
```

### Keyboard Actions
```typescript
await todoPage.clearInputWithEscape()
await todoPage.focusInputWithShortcut()  // Ctrl+K
await todoPage.clearCompletedTasksWithShortcut()  // Ctrl+Shift+C
```

### Storage
```typescript
await todoPage.clearStorage()
await todoPage.getTasksFromStorage()
await todoPage.setTasksInStorage(tasks)
```

### Utilities
```typescript
await todoPage.waitForTask('Task text')
await todoPage.isEmptyStateVisible()
await todoPage.getCounterText()
await todoPage.getFeedbackMessage()
await todoPage.isInputFocused()
await todoPage.getInputValue()
```

## 🎨 Common Patterns

### Test Empty State
```typescript
test('empty state', async ({ todoPage }) => {
  await expect(todoPage.emptyState).toBeVisible();
  await expect(todoPage.taskCounter).toContainText('0 tasks');
});
```

### Test Add Task
```typescript
test('add task', async ({ todoPage }) => {
  await todoPage.addTask('New task');
  await expect(todoPage.getTaskByText('New task')).toBeVisible();
  await expect(todoPage.getTaskItems()).toHaveCount(1);
});
```

### Test Complete Task
```typescript
test('complete task', async ({ todoPage }) => {
  await todoPage.addTask('Task');
  await todoPage.completeTask('Task');
  
  const task = todoPage.getTaskByText('Task');
  await expect(task).toHaveClass(/completed/);
});
```

### Test Delete Task
```typescript
test('delete task', async ({ todoPage }) => {
  await todoPage.addTask('Task');
  await todoPage.deleteTask('Task');
  await expect(todoPage.getTaskItems()).toHaveCount(0);
});
```

### Test Validation
```typescript
test('validation', async ({ todoPage }) => {
  await todoPage.taskInput.fill('');
  await todoPage.addButton.click();
  
  await expect(todoPage.inputFeedback)
    .toContainText('cannot be empty');
  await expect(todoPage.inputFeedback)
    .toHaveClass(/error/);
});
```

### Test Persistence
```typescript
test('persistence', async ({ todoPage }) => {
  await todoPage.addTask('Persistent task');
  await todoPage.page.waitForTimeout(1500); // Wait for save
  
  await todoPage.page.reload();
  await todoPage.page.waitForLoadState('networkidle');
  
  await expect(todoPage.getTaskByText('Persistent task'))
    .toBeVisible();
});
```

### Test Responsive
```typescript
test('mobile', async ({ todoPage }) => {
  await todoPage.page.setViewportSize({ 
    width: 390, 
    height: 844 
  });
  
  await todoPage.addTask('Mobile task');
  await expect(todoPage.getTaskByText('Mobile task'))
    .toBeVisible();
});
```

## 🔍 Debugging

### Visual Debug
```bash
# Run with Playwright Inspector
npx playwright test --debug

# Run specific test
npx playwright test --debug -g "test name"
```

### Console Logs
```typescript
test('debug', async ({ todoPage }) => {
  console.log('Task count:', await todoPage.getTaskCount());
  console.log('Counter text:', await todoPage.getCounterText());
  
  // Pause execution
  await todoPage.page.pause();
});
```

### Screenshots
```typescript
test('screenshot', async ({ todoPage }) => {
  await todoPage.addTask('Task');
  await todoPage.page.screenshot({ 
    path: 'debug-screenshot.png' 
  });
});
```

### Wait for Elements
```typescript
// Wait for specific element
await todoPage.getTaskByText('Task').waitFor({ state: 'visible' });

// Wait for timeout
await todoPage.page.waitForTimeout(1000);

// Wait for load state
await todoPage.page.waitForLoadState('networkidle');
```

## 🧪 Test Assertions

### Visibility
```typescript
await expect(element).toBeVisible()
await expect(element).toBeHidden()
await expect(element).not.toBeVisible()
```

### Text Content
```typescript
await expect(element).toHaveText('exact text')
await expect(element).toContainText('partial text')
await expect(element).toHaveText(/regex/)
```

### Attributes
```typescript
await expect(element).toHaveAttribute('attr', 'value')
await expect(element).toHaveClass(/class-name/)
await expect(element).toHaveCSS('property', 'value')
```

### Count
```typescript
await expect(locator).toHaveCount(5)
await expect(locator).toHaveCount(0)
```

### State
```typescript
await expect(element).toBeFocused()
await expect(element).toBeEnabled()
await expect(element).toBeDisabled()
await expect(element).toBeChecked()
```

## 🎯 Coverage Areas

| Area | Test File | Tests |
|------|-----------|-------|
| Add/Complete/Delete | todo-basic | 25 |
| Validation | todo-validation | 20 |
| localStorage | todo-persistence | 12 |
| ARIA & Keyboard | todo-accessibility | 18 |
| Mobile/Tablet/Desktop | todo-responsive | 15 |
| UI States | todo-ui-states | 15 |

## 📊 Test Reports

After running tests:

```bash
# HTML Report (interactive)
npx playwright show-report

# JSON Report
cat test-results.json

# Console Output
npx playwright test --reporter=list
```

## 🐛 Common Issues

### Port in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in playwright.config.ts
```

### Tests timeout
```bash
# Increase timeout
npx playwright test --timeout=60000
```

### Browsers not installed
```bash
npx playwright install
```

### Flaky tests
```bash
# Run with retries
npx playwright test --retries=3
```

## 📚 Resources

- Full docs: `README_TESTS.md`
- Playwright docs: https://playwright.dev
- Page objects: `pages/TodoPage.ts`
- Test data: `fixtures/todos.json`