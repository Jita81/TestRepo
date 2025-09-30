import { test, expect } from './fixtures/todoFixtures';

/**
 * Keyboard Interaction Tests
 * Tests all keyboard shortcuts and navigation
 */

test.describe('Keyboard Interactions', () => {
  
  test('should add task with Enter key', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Task via Enter');
    await todoPage.page.keyboard.press('Enter');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should clear input with Escape key', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Text to clear');
    await todoPage.page.keyboard.press('Escape');
    
    const inputValue = await todoPage.getInputValue();
    expect(inputValue).toBe('');
  });

  test('should focus input with Ctrl+K shortcut', async ({ todoPage }) => {
    // Focus should start on input, but click elsewhere first
    await todoPage.page.locator('body').click();
    
    await todoPage.page.keyboard.press('Control+k');
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });

  test('should focus input with Cmd+K on Mac', async ({ todoPage }) => {
    await todoPage.page.locator('body').click();
    
    await todoPage.page.keyboard.press('Meta+k');
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });

  test('should clear completed tasks with Ctrl+Shift+C', async ({ todoPage }) => {
    // Add and complete some tasks
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    await todoPage.addTask('Task 3');
    
    await todoPage.toggleTaskCompletion(0);
    await todoPage.toggleTaskCompletion(2);
    
    // Use keyboard shortcut
    await todoPage.page.keyboard.press('Control+Shift+C');
    
    // Wait for feedback
    await todoPage.page.waitForTimeout(500);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const remainingTask = await todoPage.getTaskText(0);
    expect(remainingTask).toBe('Task 2');
  });

  test('should navigate through tasks with Tab key', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Start from input
    await todoPage.taskInput.focus();
    
    // Tab through elements
    await todoPage.page.keyboard.press('Tab'); // Add button
    await todoPage.page.keyboard.press('Tab'); // First complete button
    await todoPage.page.keyboard.press('Tab'); // First delete button
    await todoPage.page.keyboard.press('Tab'); // Second complete button
    
    const focusedElement = await todoPage.page.evaluate(() => {
      const el = document.activeElement as HTMLElement;
      return {
        className: el.className,
        parentId: el.closest('.task-item')?.getAttribute('data-id')
      };
    });
    
    expect(focusedElement.className).toContain('btn-complete');
  });

  test('should navigate backwards with Shift+Tab', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    
    // Focus on delete button
    const deleteBtn = todoPage.getTaskItem(0).locator('.btn-delete');
    await deleteBtn.focus();
    
    // Shift+Tab back
    await todoPage.page.keyboard.press('Shift+Tab');
    
    const focusedElement = await todoPage.page.evaluate(() => {
      return document.activeElement?.className;
    });
    
    expect(focusedElement).toContain('btn-complete');
  });

  test('should activate buttons with Space key', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const completeBtn = todoPage.getTaskItem(0).locator('.btn-complete');
    await completeBtn.focus();
    await todoPage.page.keyboard.press('Space');
    
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should activate buttons with Enter key', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const completeBtn = todoPage.getTaskItem(0).locator('.btn-complete');
    await completeBtn.focus();
    await todoPage.page.keyboard.press('Enter');
    
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should not submit form on Ctrl+Enter', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Test');
    await todoPage.page.keyboard.press('Control+Enter');
    
    // Task should not be added with Ctrl+Enter
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
  });

  test('should maintain focus on input after adding task', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    // Wait for focus to settle
    await todoPage.page.waitForTimeout(100);
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });

  test('should allow rapid task addition with keyboard', async ({ todoPage }) => {
    const tasks = ['Task 1', 'Task 2', 'Task 3'];
    
    for (const task of tasks) {
      await todoPage.taskInput.fill(task);
      await todoPage.page.keyboard.press('Enter');
    }
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(3);
  });

  test('should prevent default Ctrl+K browser behavior', async ({ todoPage }) => {
    // This keyboard shortcut should focus input, not trigger browser search
    await todoPage.page.keyboard.press('Control+k');
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });
});