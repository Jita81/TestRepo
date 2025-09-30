import { test, expect } from './fixtures/test-fixtures';

/**
 * Basic Todo Functionality Tests
 * Tests core features: add, complete, delete tasks
 */

test.describe('Basic Todo Operations', () => {
  
  test('should display empty state when no tasks exist', async ({ todoPage }) => {
    // Assert - Empty state should be visible
    await expect(todoPage.emptyState).toBeVisible();
    await expect(todoPage.emptyState).toContainText('No tasks yet');
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
  
  test('should add a new task using the add button', async ({ todoPage }) => {
    // Arrange
    const taskText = 'Buy groceries';
    
    // Act - Add task
    await todoPage.addTask(taskText);
    
    // Assert - Task appears in the list
    await expect(todoPage.getTaskByText(taskText)).toBeVisible();
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    await expect(todoPage.taskCounter).toContainText('1 task');
    await expect(todoPage.emptyState).not.toBeVisible();
  });
  
  test('should add a new task using Enter key', async ({ todoPage }) => {
    // Arrange
    const taskText = 'Write documentation';
    
    // Act - Add task with Enter key
    await todoPage.addTaskWithEnter(taskText);
    
    // Assert - Task appears in the list
    await expect(todoPage.getTaskByText(taskText)).toBeVisible();
    await expect(todoPage.getTaskItems()).toHaveCount(1);
  });
  
  test('should clear input field after adding task', async ({ todoPage }) => {
    // Arrange & Act
    await todoPage.addTask('Test task');
    
    // Assert - Input should be cleared
    const inputValue = await todoPage.getInputValue();
    expect(inputValue).toBe('');
  });
  
  test('should focus input after adding task', async ({ todoPage }) => {
    // Arrange & Act
    await todoPage.addTask('Test task');
    
    // Assert - Input should be focused for quick entry
    await expect(todoPage.taskInput).toBeFocused();
  });
  
  test('should add multiple tasks', async ({ todoPage }) => {
    // Arrange
    const tasks = ['Task 1', 'Task 2', 'Task 3'];
    
    // Act - Add multiple tasks
    for (const task of tasks) {
      await todoPage.addTask(task);
      // Small delay to ensure proper rendering
      await todoPage.page.waitForTimeout(100);
    }
    
    // Assert - All tasks should appear
    await expect(todoPage.getTaskItems()).toHaveCount(3);
    await expect(todoPage.taskCounter).toContainText('3 tasks');
    
    // Verify order (newest at bottom)
    const taskTexts = await todoPage.getAllTaskTexts();
    expect(taskTexts).toEqual(tasks);
  });
  
  test('should show success feedback when task is added', async ({ todoPage }) => {
    // Act
    await todoPage.addTask('Test task');
    
    // Assert - Success message should appear
    await expect(todoPage.inputFeedback).toContainText('Task added successfully');
    await expect(todoPage.inputFeedback).toHaveClass(/success/);
  });
});

test.describe('Task Completion', () => {
  
  test('should mark task as complete when complete button is clicked', async ({ todoPage }) => {
    // Arrange - Add a task
    const taskText = 'Complete this task';
    await todoPage.addTask(taskText);
    
    // Act - Click complete button
    await todoPage.completeTask(taskText);
    
    // Assert - Task should have completed styling
    const task = todoPage.getTaskByText(taskText);
    await expect(task).toHaveClass(/completed/);
  });
  
  test('should toggle task between complete and incomplete', async ({ todoPage }) => {
    // Arrange - Add and complete a task
    const taskText = 'Toggle this task';
    await todoPage.addTask(taskText);
    await todoPage.completeTask(taskText);
    
    const task = todoPage.getTaskByText(taskText);
    await expect(task).toHaveClass(/completed/);
    
    // Act - Click complete button again to uncomplete
    await todoPage.completeTask(taskText);
    
    // Assert - Task should no longer be completed
    await expect(task).not.toHaveClass(/completed/);
  });
  
  test('should update counter when task is completed', async ({ todoPage }) => {
    // Arrange - Add two tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Act - Complete one task
    await todoPage.completeTask('Task 1');
    
    // Assert - Counter should show 1 of 2 remaining
    await expect(todoPage.taskCounter).toContainText('1 of 2 tasks remaining');
  });
  
  test('should show celebration message when all tasks are completed', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Act - Complete all tasks
    await todoPage.completeTask('Task 1');
    await todoPage.completeTask('Task 2');
    
    // Assert - Counter should show celebration
    await expect(todoPage.taskCounter).toContainText('All 2 tasks completed! 🎉');
  });
  
  test('should show feedback when task is completed', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Test task');
    
    // Act
    await todoPage.completeTask('Test task');
    
    // Assert - Feedback should indicate completion
    await expect(todoPage.inputFeedback).toContainText('completed');
  });
});

test.describe('Task Deletion', () => {
  
  test('should delete a task when delete button is clicked', async ({ todoPage }) => {
    // Arrange - Add a task
    const taskText = 'Delete this task';
    await todoPage.addTask(taskText);
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    
    // Act - Delete the task
    await todoPage.deleteTask(taskText);
    
    // Assert - Task should be removed
    await expect(todoPage.getTaskItems()).toHaveCount(0);
    await expect(todoPage.emptyState).toBeVisible();
  });
  
  test('should delete task with smooth animation', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Task to delete');
    const task = todoPage.getTaskByText('Task to delete');
    
    // Act - Click delete and check for animation class
    await task.locator('.btn-delete').click();
    
    // Assert - Task should have deleting class during animation
    await expect(task).toHaveClass(/deleting/);
  });
  
  test('should update counter after deletion', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toContainText('2 tasks');
    
    // Act - Delete one task
    await todoPage.deleteTask('Task 1');
    
    // Assert - Counter should update
    await expect(todoPage.taskCounter).toContainText('1 task');
  });
  
  test('should delete multiple tasks independently', async ({ todoPage }) => {
    // Arrange - Add multiple tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Act - Delete middle task
    await todoPage.deleteTask('Task 2');
    
    // Assert - Only Task 2 should be deleted
    await expect(todoPage.getTaskItems()).toHaveCount(2);
    await expect(todoPage.getTaskByText('Task 1')).toBeVisible();
    await expect(todoPage.getTaskByText('Task 3')).toBeVisible();
    await expect(todoPage.getTaskByText('Task 2')).not.toBeVisible();
  });
  
  test('should show empty state after deleting all tasks', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Only task');
    
    // Act
    await todoPage.deleteTask('Only task');
    
    // Assert
    await expect(todoPage.emptyState).toBeVisible();
    await expect(todoPage.taskCounter).toContainText('0 tasks');
  });
});