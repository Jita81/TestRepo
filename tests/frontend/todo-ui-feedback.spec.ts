import { test, expect } from './fixtures/todoFixtures';

/**
 * UI Feedback and User Experience Tests
 * Tests visual feedback, animations, and user experience elements
 */

test.describe('UI Feedback and UX', () => {
  
  test('should show success feedback after adding task', async ({ todoPage }) => {
    await todoPage.addTask('New task');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('success');
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('success');
  });

  test('should show feedback after completing task', async ({ todoPage }) => {
    await todoPage.addTask('Task to complete');
    await todoPage.toggleTaskCompletion(0);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage.length).toBeGreaterThan(0);
  });

  test('should show feedback after deleting task', async ({ todoPage }) => {
    await todoPage.addTask('Task to delete');
    await todoPage.deleteTask(0);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('deleted');
  });

  test('should auto-clear success feedback after timeout', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    let feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage.length).toBeGreaterThan(0);
    
    // Wait for auto-clear (3 seconds)
    await todoPage.page.waitForTimeout(3500);
    
    feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toBe('');
  });

  test('should show warning when approaching character limit', async ({ todoPage, edgeCases }) => {
    await todoPage.taskInput.fill(edgeCases.nearMaxLength);
    
    // Wait for debounced validation
    await todoPage.page.waitForTimeout(400);
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('warning');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('remaining');
  });

  test('should clear warning when input is cleared', async ({ todoPage, edgeCases }) => {
    await todoPage.taskInput.fill(edgeCases.nearMaxLength);
    await todoPage.page.waitForTimeout(400);
    
    // Clear input
    await todoPage.clearInput();
    await todoPage.page.waitForTimeout(400);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toBe('');
  });

  test('should update counter when adding tasks', async ({ todoPage }) => {
    await expect(todoPage.taskCounter).toHaveText('0 tasks');
    
    await todoPage.addTask('Task 1');
    await expect(todoPage.taskCounter).toHaveText('1 task');
    
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toHaveText('2 tasks');
  });

  test('should update counter when deleting tasks', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    await expect(todoPage.taskCounter).toHaveText('2 tasks');
    
    await todoPage.deleteTask(0);
    await expect(todoPage.taskCounter).toHaveText('1 task');
  });

  test('should show completion status in counter', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    await todoPage.toggleTaskCompletion(0);
    
    const counterText = await todoPage.getCounterText();
    expect(counterText).toContain('1 of 2');
  });

  test('should show celebration message when all tasks completed', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    await todoPage.toggleTaskCompletion(0);
    await todoPage.toggleTaskCompletion(1);
    
    const counterText = await todoPage.getCounterText();
    expect(counterText).toContain('All');
    expect(counterText).toContain('completed');
  });

  test('should toggle empty state visibility', async ({ todoPage }) => {
    // Initially empty
    let isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
    
    // Add task
    await todoPage.addTask('Test task');
    isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(false);
    
    // Delete task
    await todoPage.deleteTask(0);
    isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
  });

  test('should show delete animation', async ({ todoPage }) => {
    await todoPage.addTask('Task to delete');
    
    const task = todoPage.getTaskItem(0);
    const deleteBtn = task.locator('.btn-delete');
    
    await deleteBtn.click();
    
    // Task should have deleting class during animation
    const classList = await task.getAttribute('class');
    expect(classList).toContain('deleting');
  });

  test('should visually distinguish completed tasks', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    await todoPage.toggleTaskCompletion(0);
    
    const completedTask = todoPage.getTaskItem(0);
    const normalTask = todoPage.getTaskItem(1);
    
    const completedClass = await completedTask.getAttribute('class');
    const normalClass = await normalTask.getAttribute('class');
    
    expect(completedClass).toContain('completed');
    expect(normalClass).not.toContain('completed');
  });

  test('should maintain input focus after adding task', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    await todoPage.page.waitForTimeout(100);
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });

  test('should clear input immediately after submission', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Test task');
    await todoPage.addButton.click();
    
    const inputValue = await todoPage.getInputValue();
    expect(inputValue).toBe('');
  });

  test('should show appropriate placeholder text', async ({ todoPage }) => {
    const placeholder = await todoPage.taskInput.getAttribute('placeholder');
    expect(placeholder).toContain('What needs to be done?');
  });

  test('should have readable footer text', async ({ todoPage }) => {
    const footer = todoPage.page.locator('.app-footer');
    await expect(footer).toBeVisible();
    await expect(footer).toContainText('Built with vanilla JavaScript');
  });

  test('should show empty state icon', async ({ todoPage }) => {
    const emptyStateIcon = todoPage.emptyState.locator('svg');
    await expect(emptyStateIcon).toBeVisible();
  });

  test('should show empty state message', async ({ todoPage }) => {
    const emptyStateText = todoPage.emptyState.locator('.empty-state-text');
    await expect(emptyStateText).toContainText('No tasks yet');
  });

  test('should handle input maxlength attribute', async ({ todoPage }) => {
    const maxLength = await todoPage.taskInput.getAttribute('maxlength');
    expect(maxLength).toBe('280');
  });

  test('should prevent multiple rapid submissions', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Test');
    
    // Try to submit multiple times rapidly
    await todoPage.addButton.click();
    await todoPage.addButton.click();
    await todoPage.addButton.click();
    
    await todoPage.page.waitForTimeout(500);
    
    // Should only add once (input is cleared after first add)
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });
});