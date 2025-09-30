import { test, expect } from './fixtures/test-fixtures';

/**
 * Input Validation Tests
 * Tests validation rules, character limits, and error handling
 */

test.describe('Input Validation', () => {
  
  test('should not add empty task', async ({ todoPage }) => {
    // Act - Try to add empty task
    await todoPage.taskInput.fill('');
    await todoPage.addButton.click();
    
    // Assert - No task should be added
    await expect(todoPage.getTaskItems()).toHaveCount(0);
    await expect(todoPage.emptyState).toBeVisible();
  });
  
  test('should not add task with only whitespace', async ({ todoPage }) => {
    // Act - Try to add whitespace-only task
    await todoPage.taskInput.fill('   ');
    await todoPage.addButton.click();
    
    // Assert - No task should be added
    await expect(todoPage.getTaskItems()).toHaveCount(0);
    await expect(todoPage.inputFeedback).toContainText('cannot be empty');
  });
  
  test('should trim whitespace from task text', async ({ todoPage }) => {
    // Act - Add task with leading/trailing whitespace
    await todoPage.addTask('  Clean task text  ');
    
    // Assert - Whitespace should be trimmed
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts[0]).toBe('Clean task text');
  });
  
  test('should enforce character limit of 280', async ({ todoPage }) => {
    // Arrange - Create a task with 281 characters
    const longTask = 'a'.repeat(281);
    
    // Act - Try to add task
    await todoPage.taskInput.fill(longTask);
    await todoPage.addButton.click();
    
    // Assert - Error message should appear
    await expect(todoPage.inputFeedback).toContainText('characters too long');
    await expect(todoPage.inputFeedback).toHaveClass(/error/);
    await expect(todoPage.getTaskItems()).toHaveCount(0);
  });
  
  test('should show warning when approaching character limit', async ({ todoPage }) => {
    // Arrange - Create task at 90% of limit (252 characters)
    const almostLongTask = 'a'.repeat(252);
    
    // Act - Fill input
    await todoPage.fillInput(almostLongTask);
    
    // Wait for debounced validation
    await todoPage.page.waitForTimeout(400);
    
    // Assert - Warning should appear
    await expect(todoPage.inputFeedback).toContainText('characters remaining');
    await expect(todoPage.inputFeedback).toHaveClass(/warning/);
  });
  
  test('should accept task at exactly 280 characters', async ({ todoPage }) => {
    // Arrange - Create task with exactly 280 characters
    const maxLengthTask = 'a'.repeat(280);
    
    // Act - Add task
    await todoPage.addTask(maxLengthTask);
    
    // Assert - Task should be added
    await expect(todoPage.getTaskItems()).toHaveCount(1);
  });
  
  test('should accept task with single character', async ({ todoPage }) => {
    // Act - Add single character task
    await todoPage.addTask('a');
    
    // Assert - Task should be added
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts[0]).toBe('a');
  });
  
  test('should handle emoji in task text', async ({ todoPage }) => {
    // Act - Add task with emoji
    const taskWithEmoji = 'Deploy to production 🚀';
    await todoPage.addTask(taskWithEmoji);
    
    // Assert - Emoji should be preserved
    await expect(todoPage.getTaskByText(taskWithEmoji)).toBeVisible();
  });
  
  test('should sanitize HTML special characters', async ({ todoPage }) => {
    // Act - Add task with HTML special characters
    const taskWithHTML = '<script>alert("xss")</script>';
    await todoPage.addTask(taskWithHTML);
    
    // Assert - Task should be added and HTML should be escaped (rendered as text)
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    const task = todoPage.getTaskItems().first();
    const taskText = await task.locator('.task-text').textContent();
    expect(taskText).toBe('<script>alert("xss")</script>');
    
    // Verify no script was executed
    const alertDialogs: string[] = [];
    todoPage.page.on('dialog', dialog => {
      alertDialogs.push(dialog.message());
      dialog.dismiss();
    });
    expect(alertDialogs).toHaveLength(0);
  });
  
  test('should handle quotes in task text', async ({ todoPage }) => {
    // Act - Add task with quotes
    const taskWithQuotes = 'Task with "double" and \'single\' quotes';
    await todoPage.addTask(taskWithQuotes);
    
    // Assert - Quotes should be preserved
    await expect(todoPage.getTaskByText(taskWithQuotes)).toBeVisible();
  });
  
  test('should clear feedback after successful addition', async ({ todoPage }) => {
    // Act - Add task
    await todoPage.addTask('Test task');
    
    // Assert - Success feedback appears
    await expect(todoPage.inputFeedback).toContainText('added successfully');
    
    // Wait for auto-clear
    await todoPage.page.waitForTimeout(3500);
    
    // Assert - Feedback should be cleared
    const feedbackText = await todoPage.getFeedbackMessage();
    expect(feedbackText).toBe('');
  });
});

test.describe('Task Order', () => {
  
  test('should add tasks in chronological order (newest at bottom)', async ({ todoPage }) => {
    // Act - Add tasks in sequence
    await todoPage.addTask('First task');
    await todoPage.page.waitForTimeout(100);
    await todoPage.addTask('Second task');
    await todoPage.page.waitForTimeout(100);
    await todoPage.addTask('Third task');
    
    // Assert - Tasks should appear in chronological order
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts).toEqual(['First task', 'Second task', 'Third task']);
  });
  
  test('should maintain order after completing tasks', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Task A');
    await todoPage.addTask('Task B');
    await todoPage.addTask('Task C');
    
    // Act - Complete middle task
    await todoPage.completeTask('Task B');
    
    // Assert - Order should remain the same
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts).toEqual(['Task A', 'Task B', 'Task C']);
  });
});

test.describe('Task Counter', () => {
  
  test('should display correct count for single task', async ({ todoPage }) => {
    // Act
    await todoPage.addTask('Single task');
    
    // Assert
    await expect(todoPage.taskCounter).toContainText('1 task');
  });
  
  test('should display correct count for multiple tasks', async ({ todoPage }) => {
    // Act
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Assert
    await expect(todoPage.taskCounter).toContainText('3 tasks');
  });
  
  test('should show remaining tasks when some are completed', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Act - Complete one task
    await todoPage.completeTask('Task 1');
    
    // Assert
    await expect(todoPage.taskCounter).toContainText('2 of 3 tasks remaining');
  });
  
  test('should update counter in real-time', async ({ todoPage }) => {
    // Add task
    await todoPage.addTask('Task 1');
    await expect(todoPage.taskCounter).toContainText('1 task');
    
    // Add another
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toContainText('2 tasks');
    
    // Delete one
    await todoPage.deleteTask('Task 1');
    await expect(todoPage.taskCounter).toContainText('1 task');
    
    // Delete last one
    await todoPage.deleteTask('Task 2');
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
});