import { test, expect } from './fixtures/test-fixtures';

/**
 * Accessibility Tests
 * Tests ARIA labels, keyboard navigation, screen reader support
 */

test.describe('ARIA Labels and Semantic HTML', () => {
  
  test('should have proper ARIA label on task input', async ({ todoPage }) => {
    // Assert - Input should have aria-label
    await expect(todoPage.taskInput).toHaveAttribute('aria-label', 'New task description');
  });
  
  test('should have proper ARIA label on add button', async ({ todoPage }) => {
    // Assert - Add button should have aria-label
    await expect(todoPage.addButton).toHaveAttribute('aria-label', 'Add task');
  });
  
  test('should have proper ARIA label on task list', async ({ todoPage }) => {
    // Assert - Task list should have aria-label
    await expect(todoPage.taskList).toHaveAttribute('aria-label', 'Task list');
  });
  
  test('should have proper role on task list', async ({ todoPage }) => {
    // Assert - Task list should have role="list"
    await expect(todoPage.taskList).toHaveAttribute('role', 'list');
  });
  
  test('should have proper ARIA labels on task action buttons', async ({ todoPage }) => {
    // Arrange - Add a task
    await todoPage.addTask('Test task');
    const task = todoPage.getTaskByText('Test task');
    
    // Assert - Complete button should have aria-label
    const completeBtn = task.locator('.btn-complete');
    await expect(completeBtn).toHaveAttribute('aria-label', 'Mark task as complete');
    
    // Assert - Delete button should have aria-label
    const deleteBtn = task.locator('.btn-delete');
    await expect(deleteBtn).toHaveAttribute('aria-label', 'Delete task');
  });
  
  test('should update complete button ARIA label when task is completed', async ({ todoPage }) => {
    // Arrange - Add and complete task
    await todoPage.addTask('Test task');
    const task = todoPage.getTaskByText('Test task');
    const completeBtn = task.locator('.btn-complete');
    
    // Act - Complete task
    await completeBtn.click();
    
    // Assert - ARIA label should update
    await expect(completeBtn).toHaveAttribute('aria-label', 'Mark task as incomplete');
  });
  
  test('should have live region for feedback messages', async ({ todoPage }) => {
    // Assert - Feedback should have aria-live
    await expect(todoPage.inputFeedback).toHaveAttribute('aria-live', 'polite');
  });
  
  test('should have live region for task counter', async ({ todoPage }) => {
    // Assert - Counter should have aria-live
    await expect(todoPage.taskCounter).toHaveAttribute('aria-live', 'polite');
  });
  
  test('should have alert role on feedback messages', async ({ todoPage }) => {
    // Assert - Feedback should have role="alert"
    await expect(todoPage.inputFeedback).toHaveAttribute('role', 'alert');
  });
  
  test('should have proper semantic HTML structure', async ({ todoPage }) => {
    // Assert - Check for semantic elements
    await expect(todoPage.page.locator('header.app-header')).toBeVisible();
    await expect(todoPage.page.locator('main.app-main')).toBeVisible();
    await expect(todoPage.page.locator('footer.app-footer')).toBeVisible();
    await expect(todoPage.header).toHaveText('My Todo List');
  });
});

test.describe('Keyboard Navigation', () => {
  
  test('should allow adding task with Enter key', async ({ todoPage }) => {
    // Act - Type task and press Enter
    await todoPage.addTaskWithEnter('Keyboard task');
    
    // Assert - Task should be added
    await expect(todoPage.getTaskByText('Keyboard task')).toBeVisible();
  });
  
  test('should clear input with Escape key', async ({ todoPage }) => {
    // Arrange - Fill input
    await todoPage.fillInput('Some text');
    expect(await todoPage.getInputValue()).toBe('Some text');
    
    // Act - Press Escape
    await todoPage.clearInputWithEscape();
    
    // Assert - Input should be cleared
    expect(await todoPage.getInputValue()).toBe('');
  });
  
  test('should focus input with Ctrl+K shortcut', async ({ todoPage }) => {
    // Arrange - Focus somewhere else
    await todoPage.addButton.focus();
    
    // Act - Press Ctrl+K
    await todoPage.focusInputWithShortcut();
    
    // Assert - Input should be focused
    await expect(todoPage.taskInput).toBeFocused();
  });
  
  test('should clear completed tasks with Ctrl+Shift+C', async ({ todoPage }) => {
    // Arrange - Add and complete some tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    await todoPage.completeTask('Task 1');
    await todoPage.completeTask('Task 3');
    
    await expect(todoPage.getTaskItems()).toHaveCount(3);
    
    // Act - Press Ctrl+Shift+C
    await todoPage.clearCompletedTasksWithShortcut();
    await todoPage.page.waitForTimeout(500);
    
    // Assert - Only Task 2 should remain
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    await expect(todoPage.getTaskByText('Task 2')).toBeVisible();
  });
  
  test('should allow Tab navigation between interactive elements', async ({ todoPage }) => {
    // Arrange - Add a task
    await todoPage.addTask('Test task');
    
    // Act - Tab through elements
    await todoPage.taskInput.focus();
    await expect(todoPage.taskInput).toBeFocused();
    
    await todoPage.page.keyboard.press('Tab');
    await expect(todoPage.addButton).toBeFocused();
    
    await todoPage.page.keyboard.press('Tab');
    // Next focusable element should be the complete button
    const completeBtn = todoPage.page.locator('.btn-complete').first();
    await expect(completeBtn).toBeFocused();
    
    await todoPage.page.keyboard.press('Tab');
    const deleteBtn = todoPage.page.locator('.btn-delete').first();
    await expect(deleteBtn).toBeFocused();
  });
  
  test('should support keyboard activation of buttons', async ({ todoPage }) => {
    // Arrange - Add task
    await todoPage.addTask('Keyboard test');
    const task = todoPage.getTaskByText('Keyboard test');
    
    // Act - Navigate to complete button and press Space
    const completeBtn = task.locator('.btn-complete');
    await completeBtn.focus();
    await todoPage.page.keyboard.press('Space');
    
    // Assert - Task should be completed
    await expect(task).toHaveClass(/completed/);
  });
  
  test('should support Enter key on buttons', async ({ todoPage }) => {
    // Arrange - Add task
    await todoPage.addTask('Enter key test');
    const task = todoPage.getTaskByText('Enter key test');
    
    // Act - Navigate to delete button and press Enter
    const deleteBtn = task.locator('.btn-delete');
    await deleteBtn.focus();
    await todoPage.page.keyboard.press('Enter');
    
    // Wait for deletion
    await todoPage.page.waitForTimeout(400);
    
    // Assert - Task should be deleted
    await expect(todoPage.getTaskItems()).toHaveCount(0);
  });
});

test.describe('Screen Reader Support', () => {
  
  test('should announce task addition to screen readers', async ({ todoPage }) => {
    // Act - Add task
    await todoPage.addTask('Announced task');
    
    // Assert - Feedback with aria-live should contain success message
    await expect(todoPage.inputFeedback).toHaveAttribute('aria-live', 'polite');
    await expect(todoPage.inputFeedback).toContainText('added successfully');
  });
  
  test('should announce counter changes to screen readers', async ({ todoPage }) => {
    // Arrange & Act
    await todoPage.addTask('Task 1');
    
    // Assert - Counter has aria-live and updates
    await expect(todoPage.taskCounter).toHaveAttribute('aria-live', 'polite');
    await expect(todoPage.taskCounter).toContainText('1 task');
    
    // Add another
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toContainText('2 tasks');
  });
  
  test('should have descriptive labels for all interactive elements', async ({ todoPage }) => {
    // Assert - Check all interactive elements have labels
    const inputLabel = await todoPage.taskInput.getAttribute('aria-label');
    expect(inputLabel).toBeTruthy();
    
    const buttonLabel = await todoPage.addButton.getAttribute('aria-label');
    expect(buttonLabel).toBeTruthy();
  });
});

test.describe('Focus Management', () => {
  
  test('should auto-focus input on page load', async ({ todoPage }) => {
    // Assert - Input should be focused on load
    await expect(todoPage.taskInput).toBeFocused();
  });
  
  test('should return focus to input after adding task', async ({ todoPage }) => {
    // Act - Add task
    await todoPage.addTask('Focus test');
    
    // Assert - Input should regain focus
    await expect(todoPage.taskInput).toBeFocused();
  });
  
  test('should return focus to input after validation error', async ({ todoPage }) => {
    // Act - Try to add empty task
    await todoPage.taskInput.fill('');
    await todoPage.addButton.click();
    
    // Assert - Input should be focused for correction
    await expect(todoPage.taskInput).toBeFocused();
  });
  
  test('should maintain focus on input during rapid interactions', async ({ todoPage }) => {
    // Act - Add multiple tasks rapidly
    for (let i = 1; i <= 5; i++) {
      await todoPage.addTask(`Task ${i}`);
      // Input should remain focused for next task
      await expect(todoPage.taskInput).toBeFocused();
    }
  });
});

test.describe('Color Contrast and Visual Accessibility', () => {
  
  test('should have sufficient contrast for text elements', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Regular task');
    await todoPage.addTask('Completed task');
    await todoPage.completeTask('Completed task');
    
    // This is a basic check - in real scenarios, use axe-core or similar
    // Assert - Elements should be visible (Playwright checks for visibility)
    await expect(todoPage.getTaskByText('Regular task')).toBeVisible();
    await expect(todoPage.getTaskByText('Completed task')).toBeVisible();
  });
  
  test('should maintain readability in different states', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Test task');
    const task = todoPage.getTaskByText('Test task');
    
    // Assert - Normal state is visible
    await expect(task).toBeVisible();
    
    // Act - Complete task
    await todoPage.completeTask('Test task');
    
    // Assert - Completed state is still visible
    await expect(task).toBeVisible();
    await expect(task.locator('.task-text')).toBeVisible();
  });
});