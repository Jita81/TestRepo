import { test, expect } from './fixtures/todoFixtures';

/**
 * Data Persistence Tests
 * Tests localStorage persistence and data recovery
 */

test.describe('Data Persistence', () => {
  
  test('should persist tasks after page reload', async ({ todoPage }) => {
    // Add tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Reload page
    await todoPage.reload();
    
    // Tasks should still be there
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(3);
    
    const task1 = await todoPage.getTaskText(0);
    const task2 = await todoPage.getTaskText(1);
    const task3 = await todoPage.getTaskText(2);
    
    expect(task1).toBe('Task 1');
    expect(task2).toBe('Task 2');
    expect(task3).toBe('Task 3');
  });

  test('should persist task completion status', async ({ todoPage }) => {
    // Add and complete tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.toggleTaskCompletion(0);
    
    // Reload page
    await todoPage.reload();
    
    // Completion status should persist
    const task1Completed = await todoPage.isTaskCompleted(0);
    const task2Completed = await todoPage.isTaskCompleted(1);
    
    expect(task1Completed).toBe(true);
    expect(task2Completed).toBe(false);
  });

  test('should save tasks to localStorage', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    // Wait for debounced save
    await todoPage.page.waitForTimeout(1500);
    
    const storedTasks = await todoPage.getTasksFromStorage();
    expect(storedTasks).toHaveLength(1);
    expect(storedTasks[0].text).toBe('Test task');
  });

  test('should load tasks from localStorage on initialization', async ({ todoPage, sampleTasks }) => {
    // Manually set tasks in storage
    await todoPage.setTasksInStorage(sampleTasks);
    await todoPage.reload();
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(sampleTasks.length);
    
    // Verify tasks are displayed
    for (let i = 0; i < sampleTasks.length; i++) {
      const taskText = await todoPage.getTaskText(i);
      expect(taskText).toBe(sampleTasks[i].text);
    }
  });

  test('should handle corrupted localStorage data gracefully', async ({ todoPage }) => {
    // Set invalid JSON in localStorage
    await todoPage.page.evaluate(() => {
      localStorage.setItem('todo_tasks', 'invalid json {]');
    });
    
    // Reload - should not crash
    await todoPage.reload();
    
    // Should start with empty list
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
  });

  test('should handle empty localStorage', async ({ todoPage }) => {
    await todoPage.clearLocalStorage();
    await todoPage.reload();
    
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
    
    await expect(todoPage.taskCounter).toHaveText('0 tasks');
  });

  test('should maintain task order after reload', async ({ todoPage }) => {
    const tasks = ['First task', 'Second task', 'Third task'];
    
    for (const task of tasks) {
      await todoPage.addTask(task);
    }
    
    await todoPage.reload();
    
    // Tasks should be in same order
    for (let i = 0; i < tasks.length; i++) {
      const taskText = await todoPage.getTaskText(i);
      expect(taskText).toBe(tasks[i]);
    }
  });

  test('should persist deleted tasks correctly', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    await todoPage.deleteTask(1);
    
    await todoPage.reload();
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(2);
    
    const task1 = await todoPage.getTaskText(0);
    const task2 = await todoPage.getTaskText(1);
    
    expect(task1).toBe('Task 1');
    expect(task2).toBe('Task 3');
  });
});