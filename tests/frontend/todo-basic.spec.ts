import { test, expect } from './fixtures/todoFixtures';

/**
 * Basic Todo Functionality Tests
 * Tests core CRUD operations for tasks
 */

test.describe('Basic Todo Functionality', () => {
  
  test('should display the application title and subtitle', async ({ todoPage }) => {
    await expect(todoPage.appHeader.locator('h1')).toHaveText('My Todo List');
    await expect(todoPage.appHeader.locator('.app-subtitle')).toContainText('Stay organized');
  });

  test('should show empty state when no tasks exist', async ({ todoPage }) => {
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
    
    await expect(todoPage.emptyState).toContainText('No tasks yet');
    await expect(todoPage.taskCounter).toHaveText('0 tasks');
  });

  test('should add a new task using the add button', async ({ todoPage }) => {
    const taskText = 'Buy groceries';
    
    await todoPage.addTask(taskText);
    
    // Verify task was added
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const addedTaskText = await todoPage.getTaskText(0);
    expect(addedTaskText).toBe(taskText);
    
    // Verify counter updated
    await expect(todoPage.taskCounter).toHaveText('1 task');
    
    // Verify empty state is hidden
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(false);
  });

  test('should add a new task by pressing Enter', async ({ todoPage }) => {
    const taskText = 'Write documentation';
    
    await todoPage.addTaskWithEnter(taskText);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const addedTaskText = await todoPage.getTaskText(0);
    expect(addedTaskText).toBe(taskText);
  });

  test('should clear input field after adding a task', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const inputValue = await todoPage.getInputValue();
    expect(inputValue).toBe('');
  });

  test('should add multiple tasks', async ({ todoPage }) => {
    const tasks = ['Task 1', 'Task 2', 'Task 3'];
    
    for (const task of tasks) {
      await todoPage.addTask(task);
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(3);
    
    // Verify order (newest at bottom)
    for (let i = 0; i < tasks.length; i++) {
      const text = await todoPage.getTaskText(i);
      expect(text).toBe(tasks[i]);
    }
  });

  test('should mark a task as completed', async ({ todoPage }) => {
    await todoPage.addTask('Complete this task');
    
    // Initially not completed
    let isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(false);
    
    // Toggle completion
    await todoPage.toggleTaskCompletion(0);
    
    // Now should be completed
    isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should toggle task between completed and incomplete', async ({ todoPage }) => {
    await todoPage.addTask('Toggle me');
    
    // Complete the task
    await todoPage.toggleTaskCompletion(0);
    let isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
    
    // Uncomplete the task
    await todoPage.toggleTaskCompletion(0);
    isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(false);
  });

  test('should delete a task', async ({ todoPage }) => {
    await todoPage.addTask('Task to delete');
    
    let taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    await todoPage.deleteTask(0);
    
    taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
    
    // Empty state should be visible again
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
  });

  test('should delete the correct task when multiple tasks exist', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Delete middle task
    await todoPage.deleteTask(1);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(2);
    
    // Verify remaining tasks
    const task1Text = await todoPage.getTaskText(0);
    const task2Text = await todoPage.getTaskText(1);
    expect(task1Text).toBe('Task 1');
    expect(task2Text).toBe('Task 3');
  });

  test('should update task counter correctly', async ({ todoPage }) => {
    await expect(todoPage.taskCounter).toHaveText('0 tasks');
    
    await todoPage.addTask('Task 1');
    await expect(todoPage.taskCounter).toHaveText('1 task');
    
    await todoPage.addTask('Task 2');
    await expect(todoPage.taskCounter).toHaveText('2 tasks');
    
    await todoPage.toggleTaskCompletion(0);
    await expect(todoPage.taskCounter).toContainText('1 of 2 tasks remaining');
    
    await todoPage.toggleTaskCompletion(1);
    await expect(todoPage.taskCounter).toContainText('All 2 tasks completed');
  });

  test('should show success feedback after adding a task', async ({ todoPage }) => {
    await todoPage.addTask('New task');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('added successfully');
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('success');
  });
});