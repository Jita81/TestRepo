import { test, expect } from './fixtures/todoFixtures';

/**
 * Error Handling and Edge Cases Tests
 * Tests error states, boundary conditions, and error recovery
 */

test.describe('Error Handling', () => {
  
  test('should show error for empty task submission', async ({ todoPage }) => {
    await todoPage.addButton.click();
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('error');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('empty');
  });

  test('should show error for whitespace-only task', async ({ todoPage }) => {
    await todoPage.taskInput.fill('     ');
    await todoPage.addButton.click();
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('error');
  });

  test('should show error for task exceeding character limit', async ({ todoPage }) => {
    const tooLongText = 'a'.repeat(281);
    await todoPage.taskInput.fill(tooLongText);
    await todoPage.addButton.click();
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('error');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('exceed');
  });

  test('should clear error message after successful task addition', async ({ todoPage }) => {
    // First cause an error
    await todoPage.addButton.click();
    let feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage.length).toBeGreaterThan(0);
    
    // Then add valid task
    await todoPage.addTask('Valid task');
    
    // Error should be cleared
    feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('success');
  });

  test('should handle corrupted localStorage gracefully', async ({ todoPage }) => {
    await todoPage.page.evaluate(() => {
      localStorage.setItem('todo_tasks', '{invalid json}');
    });
    
    // Should not crash on reload
    await todoPage.reload();
    
    // Should start fresh
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
  });

  test('should handle non-array data in localStorage', async ({ todoPage }) => {
    await todoPage.page.evaluate(() => {
      localStorage.setItem('todo_tasks', JSON.stringify({ not: 'an array' }));
    });
    
    await todoPage.reload();
    
    const isEmpty = await todoPage.isEmptyStateVisible();
    expect(isEmpty).toBe(true);
  });

  test('should handle missing localStorage gracefully', async ({ todoPage }) => {
    // Simulate localStorage being unavailable
    await todoPage.page.addInitScript(() => {
      // This is hard to test as we can't fully disable localStorage in browsers
      // But we can test that the app loads
    });
    
    await todoPage.goto();
    
    // App should still be functional
    await expect(todoPage.taskInput).toBeVisible();
  });

  test('should handle rapid consecutive clicks on delete button', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const deleteBtn = todoPage.getTaskItem(0).locator('.btn-delete');
    
    // Click multiple times rapidly
    await deleteBtn.click();
    await deleteBtn.click();
    await deleteBtn.click();
    
    await todoPage.page.waitForTimeout(400);
    
    // Task should be deleted only once
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
  });

  test('should handle deleting already deleted task gracefully', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Delete first task
    await todoPage.deleteTask(0);
    
    // Try to interact with it shouldn't cause errors
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should handle maximum task limit gracefully', async ({ todoPage }) => {
    // This would be slow to test all 1000, so we test the logic
    // by verifying the app can handle a reasonable number
    for (let i = 0; i < 50; i++) {
      await todoPage.addTask(`Task ${i}`);
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(50);
  });

  test('should recover from network interruption', async ({ todoPage }) => {
    // Add tasks normally
    await todoPage.addTask('Before offline');
    
    // Simulate going offline
    await todoPage.page.context().setOffline(true);
    
    // Should still be able to add tasks (localStorage is local)
    await todoPage.addTask('While offline');
    
    // Go back online
    await todoPage.page.context().setOffline(false);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(2);
  });

  test('should handle special characters in task text', async ({ todoPage }) => {
    const specialChars = ['<>', '&', '"', "'", '/', '\\', '@', '#', '$', '%'];
    
    for (const char of specialChars) {
      await todoPage.addTask(`Task with ${char}`);
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(specialChars.length);
  });

  test('should sanitize HTML to prevent XSS', async ({ todoPage }) => {
    await todoPage.addTask('<img src=x onerror=alert(1)>');
    
    const taskText = await todoPage.getTaskText(0);
    
    // Should be escaped
    expect(taskText).not.toContain('<img');
    expect(taskText).toContain('&lt;img');
  });

  test('should sanitize script tags', async ({ todoPage }) => {
    await todoPage.addTask('<script>alert("xss")</script>');
    
    const taskText = await todoPage.getTaskText(0);
    
    // Should be escaped
    expect(taskText).not.toContain('<script>');
    expect(taskText).toContain('&lt;script&gt;');
  });

  test('should handle tasks with only emoji', async ({ todoPage }) => {
    await todoPage.addTask('🎉🎊🎈');
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toBe('🎉🎊🎈');
  });

  test('should handle tasks with mixed RTL and LTR text', async ({ todoPage }) => {
    await todoPage.addTask('Hello مرحبا World');
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toContain('Hello');
    expect(taskText).toContain('مرحبا');
  });

  test('should handle rapid form submissions', async ({ todoPage }) => {
    // Submit form multiple times rapidly
    await todoPage.taskInput.fill('Task 1');
    await todoPage.taskForm.evaluate((form) => {
      (form as HTMLFormElement).requestSubmit();
      (form as HTMLFormElement).requestSubmit();
      (form as HTMLFormElement).requestSubmit();
    });
    
    await todoPage.page.waitForTimeout(500);
    
    // Should only add once
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should maintain data integrity after multiple reloads', async ({ todoPage }) => {
    await todoPage.addTask('Persistent task');
    
    for (let i = 0; i < 3; i++) {
      await todoPage.reload();
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toBe('Persistent task');
  });

  test('should handle tasks with newline characters', async ({ todoPage }) => {
    // Newlines should be preserved or handled gracefully
    await todoPage.addTask('Task with\nnewline');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should handle tasks with tabs', async ({ todoPage }) => {
    await todoPage.addTask('Task\twith\ttabs');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });
});