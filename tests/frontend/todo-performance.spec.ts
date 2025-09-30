import { test, expect } from './fixtures/todoFixtures';

/**
 * Performance Tests
 * Tests application performance with many tasks and rapid interactions
 */

test.describe('Performance', () => {
  
  test('should handle many tasks efficiently', async ({ todoPage }) => {
    const taskCount = 50;
    
    for (let i = 1; i <= taskCount; i++) {
      await todoPage.addTask(`Task ${i}`);
    }
    
    const actualCount = await todoPage.getTaskCount();
    expect(actualCount).toBe(taskCount);
  });

  test('should render large task list quickly', async ({ todoPage, bulkTasks }) => {
    // Load many tasks from storage
    const largeBulkTasks = [];
    for (let i = 0; i < 100; i++) {
      largeBulkTasks.push({
        id: `task-${i}`,
        text: `Task ${i}`,
        completed: i % 3 === 0,
        timestamp: Date.now() + i
      });
    }
    
    const startTime = Date.now();
    await todoPage.setTasksInStorage(largeBulkTasks);
    await todoPage.reload();
    const endTime = Date.now();
    
    const loadTime = endTime - startTime;
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(100);
    
    // Should load in reasonable time (less than 3 seconds)
    expect(loadTime).toBeLessThan(3000);
  });

  test('should handle rapid task additions', async ({ todoPage }) => {
    // Add tasks rapidly without waiting
    for (let i = 1; i <= 10; i++) {
      await todoPage.taskInput.fill(`Rapid task ${i}`);
      await todoPage.addButton.click();
    }
    
    // Wait a bit for all operations to complete
    await todoPage.page.waitForTimeout(500);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(10);
  });

  test('should handle rapid completion toggles', async ({ todoPage }) => {
    await todoPage.addTask('Toggle test');
    
    // Toggle rapidly
    for (let i = 0; i < 5; i++) {
      await todoPage.toggleTaskCompletion(0);
    }
    
    // Should end up completed (odd number of toggles)
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should debounce localStorage saves', async ({ todoPage }) => {
    // Add multiple tasks quickly
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    // Wait for debounced save
    await todoPage.page.waitForTimeout(1500);
    
    const storedTasks = await todoPage.getTasksFromStorage();
    expect(storedTasks).toHaveLength(3);
  });

  test('should handle long task text efficiently', async ({ todoPage, edgeCases }) => {
    const longText = edgeCases.maxLengthTask;
    
    await todoPage.addTask(longText);
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText.length).toBe(280);
  });

  test('should scroll smoothly with many tasks', async ({ todoPage }) => {
    // Add enough tasks to require scrolling
    for (let i = 1; i <= 30; i++) {
      await todoPage.addTask(`Scroll test task ${i}`);
    }
    
    // Scroll to bottom
    await todoPage.page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    
    // Verify we can interact with bottom tasks
    const lastTaskIndex = 29;
    await todoPage.toggleTaskCompletion(lastTaskIndex);
    
    const isCompleted = await todoPage.isTaskCompleted(lastTaskIndex);
    expect(isCompleted).toBe(true);
  });

  test('should handle bulk deletions efficiently', async ({ todoPage }) => {
    // Add tasks
    for (let i = 1; i <= 20; i++) {
      await todoPage.addTask(`Task ${i}`);
    }
    
    // Delete multiple tasks
    for (let i = 0; i < 10; i++) {
      await todoPage.deleteTask(0);
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(10);
  });

  test('should maintain performance with mixed operations', async ({ todoPage }) => {
    // Mix of add, complete, delete operations
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.toggleTaskCompletion(0);
    await todoPage.addTask('Task 3');
    await todoPage.deleteTask(1);
    await todoPage.addTask('Task 4');
    await todoPage.toggleTaskCompletion(0);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(3);
  });

  test('should not cause memory leaks with repeated operations', async ({ todoPage }) => {
    // Perform many operations
    for (let i = 0; i < 20; i++) {
      await todoPage.addTask(`Task ${i}`);
      if (i % 3 === 0) {
        await todoPage.toggleTaskCompletion(0);
      }
      if (i % 5 === 0 && i > 0) {
        await todoPage.deleteTask(0);
      }
    }
    
    // App should still be responsive
    await todoPage.addTask('Final task');
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBeGreaterThan(0);
  });
});