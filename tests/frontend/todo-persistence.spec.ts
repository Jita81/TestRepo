import { test, expect } from './fixtures/test-fixtures';

/**
 * Data Persistence Tests
 * Tests localStorage functionality and data persistence across page reloads
 */

test.describe('LocalStorage Persistence', () => {
  
  test('should persist tasks to localStorage after adding', async ({ todoPage }) => {
    // Act - Add task
    await todoPage.addTask('Persistent task');
    
    // Wait for debounced save
    await todoPage.page.waitForTimeout(1500);
    
    // Assert - Task should be in localStorage
    const storedTasks = await todoPage.getTasksFromStorage();
    expect(storedTasks).toHaveLength(1);
    expect(storedTasks[0].text).toBe('Persistent task');
    expect(storedTasks[0].completed).toBe(false);
  });
  
  test('should persist completed status to localStorage', async ({ todoPage }) => {
    // Arrange - Add and complete task
    await todoPage.addTask('Task to complete');
    await todoPage.completeTask('Task to complete');
    
    // Wait for save
    await todoPage.page.waitForTimeout(1500);
    
    // Assert - Completed status should be in localStorage
    const storedTasks = await todoPage.getTasksFromStorage();
    expect(storedTasks[0].completed).toBe(true);
  });
  
  test('should restore tasks after page reload', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.completeTask('Task 1');
    
    // Wait for save
    await todoPage.page.waitForTimeout(1500);
    
    // Act - Reload page
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - Tasks should be restored
    await expect(todoPage.getTaskItems()).toHaveCount(2);
    await expect(todoPage.getTaskByText('Task 1')).toHaveClass(/completed/);
    await expect(todoPage.getTaskByText('Task 2')).not.toHaveClass(/completed/);
  });
  
  test('should persist task deletion', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Wait for save
    await todoPage.page.waitForTimeout(1500);
    
    // Act - Delete one task
    await todoPage.deleteTask('Task 1');
    await todoPage.page.waitForTimeout(1500);
    
    // Reload page
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - Only Task 2 should remain
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    await expect(todoPage.getTaskByText('Task 2')).toBeVisible();
  });
  
  test('should load empty state when no saved tasks', async ({ todoPage }) => {
    // Arrange - Clear storage
    await todoPage.clearStorage();
    
    // Act - Reload page
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - Empty state should be visible
    await expect(todoPage.emptyState).toBeVisible();
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
  
  test('should handle localStorage with pre-existing data', async ({ todoPage, sampleTasks }) => {
    // Arrange - Set tasks in localStorage
    await todoPage.setTasksInStorage(sampleTasks);
    
    // Act - Reload page to load tasks
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - Tasks should be loaded
    await expect(todoPage.getTaskItems()).toHaveCount(sampleTasks.length);
    
    // Verify completed states are preserved
    const completedCount = await todoPage.getCompletedTaskCount();
    const expectedCompleted = sampleTasks.filter(t => t.completed).length;
    expect(completedCount).toBe(expectedCompleted);
  });
  
  test('should preserve task order after reload', async ({ todoPage }) => {
    // Arrange - Add tasks in specific order
    const tasks = ['First', 'Second', 'Third'];
    for (const task of tasks) {
      await todoPage.addTask(task);
      await todoPage.page.waitForTimeout(100);
    }
    
    // Wait for save
    await todoPage.page.waitForTimeout(1500);
    
    // Act - Reload
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - Order should be preserved
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts).toEqual(tasks);
  });
  
  test('should maintain state across multiple reload cycles', async ({ todoPage }) => {
    // First cycle - Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.page.waitForTimeout(1500);
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Second cycle - Add more tasks
    await todoPage.addTask('Task 2');
    await todoPage.page.waitForTimeout(1500);
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Third cycle - Complete a task
    await todoPage.completeTask('Task 1');
    await todoPage.page.waitForTimeout(1500);
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - All changes should persist
    await expect(todoPage.getTaskItems()).toHaveCount(2);
    await expect(todoPage.getTaskByText('Task 1')).toHaveClass(/completed/);
    await expect(todoPage.getTaskByText('Task 2')).not.toHaveClass(/completed/);
  });
});

test.describe('Character Limit Feedback', () => {
  
  test('should show character count warning at 90% limit', async ({ todoPage }) => {
    // Arrange - 252 characters (90% of 280)
    const text = 'a'.repeat(252);
    
    // Act - Fill input
    await todoPage.fillInput(text);
    await todoPage.page.waitForTimeout(400);
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('28 characters remaining');
    await expect(todoPage.inputFeedback).toHaveClass(/warning/);
  });
  
  test('should show error when exceeding character limit', async ({ todoPage }) => {
    // Arrange - 281 characters
    const text = 'a'.repeat(281);
    
    // Act - Fill input
    await todoPage.fillInput(text);
    await todoPage.page.waitForTimeout(400);
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('1 characters too long');
    await expect(todoPage.inputFeedback).toHaveClass(/error/);
  });
  
  test('should clear feedback when input is below warning threshold', async ({ todoPage }) => {
    // Arrange - Fill with long text to trigger warning
    await todoPage.fillInput('a'.repeat(252));
    await todoPage.page.waitForTimeout(400);
    await expect(todoPage.inputFeedback).toContainText('remaining');
    
    // Act - Clear input and type normal text
    await todoPage.fillInput('Short task');
    await todoPage.page.waitForTimeout(400);
    
    // Assert - Feedback should be cleared
    const feedbackText = await todoPage.getFeedbackMessage();
    expect(feedbackText).toBe('');
  });
  
  test('should update character count dynamically as user types', async ({ todoPage }) => {
    // Act - Type to 252 characters
    await todoPage.fillInput('a'.repeat(252));
    await todoPage.page.waitForTimeout(400);
    await expect(todoPage.inputFeedback).toContainText('28 characters remaining');
    
    // Type more characters
    await todoPage.taskInput.type('aaaa');
    await todoPage.page.waitForTimeout(400);
    await expect(todoPage.inputFeedback).toContainText('24 characters remaining');
  });
});

test.describe('Edge Cases', () => {
  
  test('should handle special characters correctly', async ({ todoPage, edgeCaseTasks }) => {
    // Act - Add tasks with special characters
    for (const task of edgeCaseTasks) {
      await todoPage.addTask(task.text);
      await todoPage.page.waitForTimeout(100);
    }
    
    // Assert - All tasks should be added
    await expect(todoPage.getTaskItems()).toHaveCount(edgeCaseTasks.length);
  });
  
  test('should prevent adding task when at maximum limit', async ({ todoPage }) => {
    // Note: Testing with smaller number for practical test execution
    // Arrange - Mock reaching max limit by evaluating JS directly
    await todoPage.page.evaluate(() => {
      // Override config temporarily
      (window as any).CONFIG.MAX_TASKS = 3;
    });
    
    // Act - Add tasks up to limit
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Try to add one more
    await todoPage.taskInput.fill('Task 4');
    await todoPage.addButton.click();
    
    // Assert - Error should show
    await expect(todoPage.inputFeedback).toContainText('Maximum task limit');
    await expect(todoPage.getTaskItems()).toHaveCount(3);
  });
  
  test('should handle rapid task additions', async ({ todoPage }) => {
    // Act - Rapidly add tasks
    const tasks = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5'];
    
    for (const task of tasks) {
      await todoPage.taskInput.fill(task);
      await todoPage.addButton.click();
      // No delay between additions
    }
    
    // Wait for all tasks to be processed
    await todoPage.page.waitForTimeout(500);
    
    // Assert - All tasks should be added
    await expect(todoPage.getTaskItems()).toHaveCount(5);
  });
  
  test('should handle rapid completion toggles', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Toggle task');
    const task = todoPage.getTaskByText('Toggle task');
    const completeBtn = task.locator('.btn-complete');
    
    // Act - Rapidly toggle completion
    await completeBtn.click();
    await completeBtn.click();
    await completeBtn.click();
    
    // Assert - Final state should be complete (odd number of clicks)
    await expect(task).toHaveClass(/completed/);
  });
});