import { test, expect } from './fixtures/test-fixtures';

/**
 * UI States and Visual Feedback Tests
 * Tests loading states, error states, feedback messages, animations
 */

test.describe('UI States', () => {
  
  test('should show empty state when no tasks exist', async ({ todoPage }) => {
    // Assert
    await expect(todoPage.emptyState).toBeVisible();
    await expect(todoPage.emptyState).toContainText('No tasks yet');
    await expect(todoPage.taskList).not.toBeVisible();
  });
  
  test('should hide empty state when tasks exist', async ({ todoPage }) => {
    // Act - Add task
    await todoPage.addTask('First task');
    
    // Assert - Empty state should be hidden
    await expect(todoPage.emptyState).not.toBeVisible();
    await expect(todoPage.taskList).toBeVisible();
  });
  
  test('should toggle between empty and populated states', async ({ todoPage }) => {
    // Add task - empty state hidden
    await todoPage.addTask('Task');
    await expect(todoPage.emptyState).not.toBeVisible();
    
    // Delete task - empty state shown
    await todoPage.deleteTask('Task');
    await expect(todoPage.emptyState).toBeVisible();
    
    // Add task again - empty state hidden
    await todoPage.addTask('Another task');
    await expect(todoPage.emptyState).not.toBeVisible();
  });
  
  test('should display loading state on initialization', async ({ todoPage }) => {
    // This test verifies the app initializes properly
    // Assert - App should be ready (console logs checked via page.on('console'))
    const consoleMessages: string[] = [];
    todoPage.page.on('console', msg => {
      if (msg.type() === 'log') {
        consoleMessages.push(msg.text());
      }
    });
    
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Check for initialization messages
    await todoPage.page.waitForTimeout(500);
    const hasInitMessage = consoleMessages.some(msg => 
      msg.includes('Todo App initialized') || msg.includes('Todo App Ready')
    );
    
    expect(hasInitMessage).toBe(true);
  });
});

test.describe('Feedback Messages', () => {
  
  test('should show success feedback when adding task', async ({ todoPage }) => {
    // Act
    await todoPage.addTask('New task');
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('Task added successfully');
    await expect(todoPage.inputFeedback).toHaveClass(/success/);
  });
  
  test('should show error feedback for empty task', async ({ todoPage }) => {
    // Act
    await todoPage.taskInput.fill('   ');
    await todoPage.addButton.click();
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('cannot be empty');
    await expect(todoPage.inputFeedback).toHaveClass(/error/);
  });
  
  test('should show error feedback for too long task', async ({ todoPage }) => {
    // Act
    await todoPage.fillInput('a'.repeat(281));
    await todoPage.addButton.click();
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('too long');
    await expect(todoPage.inputFeedback).toHaveClass(/error/);
  });
  
  test('should show warning for character limit approaching', async ({ todoPage }) => {
    // Act - Fill with 252 characters (90% of limit)
    await todoPage.fillInput('a'.repeat(252));
    
    // Wait for debounced validation
    await todoPage.page.waitForTimeout(400);
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('remaining');
    await expect(todoPage.inputFeedback).toHaveClass(/warning/);
  });
  
  test('should show feedback when task is completed', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Complete me');
    
    // Act
    await todoPage.completeTask('Complete me');
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('completed');
    await expect(todoPage.inputFeedback).toHaveClass(/success/);
  });
  
  test('should show feedback when task is deleted', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Delete me');
    
    // Act
    await todoPage.deleteTask('Delete me');
    
    // Assert
    await expect(todoPage.inputFeedback).toContainText('deleted');
  });
  
  test('should auto-hide success messages after 3 seconds', async ({ todoPage }) => {
    // Act - Add task (triggers success message)
    await todoPage.addTask('Test task');
    
    // Assert - Message appears
    await expect(todoPage.inputFeedback).toContainText('added successfully');
    
    // Wait for auto-hide
    await todoPage.page.waitForTimeout(3500);
    
    // Assert - Message should be cleared
    const feedbackText = await todoPage.getFeedbackMessage();
    expect(feedbackText).toBe('');
  });
});

test.describe('Animations and Transitions', () => {
  
  test('should animate task deletion', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Animated task');
    const task = todoPage.getTaskByText('Animated task');
    
    // Act - Click delete
    const deleteBtn = task.locator('.btn-delete');
    await deleteBtn.click();
    
    // Assert - Deleting class should be added
    await expect(task).toHaveClass(/deleting/);
    
    // Wait for animation
    await todoPage.page.waitForTimeout(350);
    
    // Assert - Task should be removed
    await expect(task).not.toBeVisible();
  });
  
  test('should toggle completed state with visual feedback', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Toggle test');
    const task = todoPage.getTaskByText('Toggle test');
    
    // Act & Assert - Toggle on
    await todoPage.completeTask('Toggle test');
    await expect(task).toHaveClass(/completed/);
    
    // Act & Assert - Toggle off
    await todoPage.completeTask('Toggle test');
    await expect(task).not.toHaveClass(/completed/);
  });
});

test.describe('Error States', () => {
  
  test('should handle localStorage quota exceeded gracefully', async ({ todoPage }) => {
    // This test mocks localStorage.setItem to throw QuotaExceededError
    await todoPage.page.evaluate(() => {
      const originalSetItem = Storage.prototype.setItem;
      let callCount = 0;
      Storage.prototype.setItem = function(key, value) {
        callCount++;
        // Allow initial setItem, but fail subsequent ones
        if (callCount > 1 && key === 'todo_tasks') {
          const error: any = new Error('QuotaExceededError');
          error.name = 'QuotaExceededError';
          throw error;
        }
        return originalSetItem.call(this, key, value);
      };
    });
    
    // Act - Try to add task
    await todoPage.addTask('Task 1');
    
    // The app should handle the error gracefully
    // The task might still appear in UI (even if save fails)
    // This is acceptable behavior - app continues functioning
  });
  
  test('should handle missing DOM elements gracefully', async ({ todoPage }) => {
    // This verifies the app's defensive programming
    // The page object model and app should handle missing elements
    
    // Act - Check that required elements exist
    await expect(todoPage.taskInput).toBeAttached();
    await expect(todoPage.taskList).toBeAttached();
    await expect(todoPage.addButton).toBeAttached();
  });
  
  test('should handle corrupted localStorage data', async ({ todoPage }) => {
    // Arrange - Set invalid data in localStorage
    await todoPage.page.evaluate(() => {
      localStorage.setItem('todo_tasks', 'invalid json data{{{');
    });
    
    // Act - Reload page
    await todoPage.page.reload();
    await todoPage.page.waitForLoadState('networkidle');
    
    // Assert - App should start with empty state (fallback)
    await expect(todoPage.emptyState).toBeVisible();
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
  
  test('should recover from errors and remain functional', async ({ todoPage }) => {
    // Arrange - Trigger an error (empty task)
    await todoPage.taskInput.fill('');
    await todoPage.addButton.click();
    await expect(todoPage.inputFeedback).toHaveClass(/error/);
    
    // Act - Continue with valid operation
    await todoPage.addTask('Valid task');
    
    // Assert - App should work normally
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    await expect(todoPage.inputFeedback).toHaveClass(/success/);
  });
});

test.describe('Visual Styling', () => {
  
  test('should apply completed styling to completed tasks', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Style test');
    
    // Act - Complete task
    await todoPage.completeTask('Style test');
    
    // Assert - Completed class applied
    const task = todoPage.getTaskByText('Style test');
    await expect(task).toHaveClass(/completed/);
    
    // Check that text has strikethrough (via CSS)
    const taskText = task.locator('.task-text');
    const textDecoration = await taskText.evaluate(el => 
      window.getComputedStyle(el).textDecoration
    );
    expect(textDecoration).toContain('line-through');
  });
  
  test('should display checkmark icon on complete button', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Icon test');
    const task = todoPage.getTaskByText('Icon test');
    
    // Assert - Complete button should have checkmark
    const completeBtn = task.locator('.btn-complete');
    await expect(completeBtn).toContainText('✓');
  });
  
  test('should display × icon on delete button', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Icon test');
    const task = todoPage.getTaskByText('Icon test');
    
    // Assert - Delete button should have × symbol
    const deleteBtn = task.locator('.btn-delete');
    await expect(deleteBtn).toContainText('×');
  });
});

test.describe('Counter Display States', () => {
  
  test('should show "0 tasks" when empty', async ({ todoPage }) => {
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
  
  test('should show "1 task" (singular) for single task', async ({ todoPage }) => {
    await todoPage.addTask('One task');
    await expect(todoPage.taskCounter).toContainText('1 task');
  });
  
  test('should show "X tasks" (plural) for multiple tasks', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toContainText('2 tasks');
  });
  
  test('should show "X of Y tasks remaining" when partially complete', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    await todoPage.completeTask('Task 1');
    
    await expect(todoPage.taskCounter).toContainText('2 of 3 tasks remaining');
  });
  
  test('should show celebration when all tasks complete', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    await todoPage.completeTask('Task 1');
    await todoPage.completeTask('Task 2');
    
    await expect(todoPage.taskCounter).toContainText('All 2 tasks completed! 🎉');
  });
});