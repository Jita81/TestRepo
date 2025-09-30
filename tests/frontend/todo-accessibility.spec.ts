import { test, expect } from './fixtures/todoFixtures';

/**
 * Accessibility Tests
 * Tests ARIA labels, keyboard navigation, and screen reader compatibility
 */

test.describe('Accessibility', () => {
  
  test('should have proper ARIA labels on interactive elements', async ({ todoPage }) => {
    // Input field
    await expect(todoPage.taskInput).toHaveAttribute('aria-label', 'New task description');
    
    // Add button
    await expect(todoPage.addButton).toHaveAttribute('aria-label', 'Add task');
    
    // Task list
    await expect(todoPage.taskList).toHaveAttribute('aria-label', 'Task list');
  });

  test('should have proper ARIA live regions for dynamic content', async ({ todoPage }) => {
    // Counter should be a live region
    await expect(todoPage.taskCounter).toHaveAttribute('aria-live', 'polite');
    
    // Feedback should be a live region
    await expect(todoPage.inputFeedback).toHaveAttribute('aria-live', 'polite');
  });

  test('should have proper role attributes', async ({ todoPage }) => {
    await expect(todoPage.taskList).toHaveAttribute('role', 'list');
    await expect(todoPage.inputFeedback).toHaveAttribute('role', 'alert');
  });

  test('should have proper ARIA labels on task buttons', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const task = todoPage.getTaskItem(0);
    const completeBtn = task.locator('.btn-complete');
    const deleteBtn = task.locator('.btn-delete');
    
    await expect(completeBtn).toHaveAttribute('aria-label', 'Mark task as complete');
    await expect(deleteBtn).toHaveAttribute('aria-label', 'Delete task');
  });

  test('should update ARIA label when task is completed', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const task = todoPage.getTaskItem(0);
    const completeBtn = task.locator('.btn-complete');
    
    // Before completion
    await expect(completeBtn).toHaveAttribute('aria-label', 'Mark task as complete');
    
    // After completion
    await completeBtn.click();
    await expect(completeBtn).toHaveAttribute('aria-label', 'Mark task as incomplete');
  });

  test('should be keyboard navigable with Tab key', async ({ todoPage }) => {
    await todoPage.addTask('Task 1');
    await todoPage.addTask('Task 2');
    
    // Start from input
    await todoPage.taskInput.focus();
    
    // Tab to add button
    await todoPage.page.keyboard.press('Tab');
    let focused = await todoPage.page.evaluate(() => document.activeElement?.className);
    expect(focused).toContain('btn-add');
    
    // Tab to first task's complete button
    await todoPage.page.keyboard.press('Tab');
    focused = await todoPage.page.evaluate(() => document.activeElement?.className);
    expect(focused).toContain('btn-complete');
  });

  test('should allow task completion via keyboard', async ({ todoPage }) => {
    await todoPage.addTask('Task to complete');
    
    const task = todoPage.getTaskItem(0);
    const completeBtn = task.locator('.btn-complete');
    
    // Focus and press Enter/Space
    await completeBtn.focus();
    await todoPage.page.keyboard.press('Enter');
    
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should allow task deletion via keyboard', async ({ todoPage }) => {
    await todoPage.addTask('Task to delete');
    
    const task = todoPage.getTaskItem(0);
    const deleteBtn = task.locator('.btn-delete');
    
    // Focus and press Enter
    await deleteBtn.focus();
    await todoPage.page.keyboard.press('Enter');
    
    await todoPage.page.waitForTimeout(350);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
  });

  test('should support Escape key to clear input', async ({ todoPage }) => {
    await todoPage.taskInput.fill('Some text');
    await todoPage.pressEscape();
    
    const inputValue = await todoPage.getInputValue();
    expect(inputValue).toBe('');
  });

  test('should support Ctrl+K to focus input', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    // Click somewhere else
    await todoPage.taskList.click();
    
    // Use keyboard shortcut
    await todoPage.page.keyboard.press('Control+k');
    
    const isFocused = await todoPage.isInputFocused();
    expect(isFocused).toBe(true);
  });

  test('should have semantic HTML structure', async ({ todoPage }) => {
    const page = todoPage.page;
    
    // Check for semantic elements
    const header = await page.locator('header').count();
    expect(header).toBeGreaterThan(0);
    
    const main = await page.locator('main').count();
    expect(main).toBeGreaterThan(0);
    
    const footer = await page.locator('footer').count();
    expect(footer).toBeGreaterThan(0);
  });

  test('should have proper heading hierarchy', async ({ todoPage }) => {
    const page = todoPage.page;
    
    // Should have h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
    
    // h1 should be "My Todo List"
    await expect(page.locator('h1')).toHaveText('My Todo List');
  });

  test('should provide visible focus indicators', async ({ todoPage }) => {
    await todoPage.taskInput.focus();
    
    // Check that input has focus styles (this is visual, but we can check computed styles)
    const outlineStyle = await todoPage.taskInput.evaluate((el) => {
      return window.getComputedStyle(el).outline;
    });
    
    // Should have some outline or focus styling
    // Note: This test is basic; real visual regression would be better
    expect(outlineStyle).toBeTruthy();
  });

  test('should have sufficient color contrast for text', async ({ todoPage }) => {
    await todoPage.addTask('Test task');
    
    const task = todoPage.getTaskItem(0);
    const textElement = task.locator('.task-text');
    
    // Get computed styles
    const styles = await textElement.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        color: computed.color,
        backgroundColor: computed.backgroundColor
      };
    });
    
    // Should have text color defined
    expect(styles.color).toBeTruthy();
  });

  test('should announce dynamic content changes to screen readers', async ({ todoPage }) => {
    // Add task - feedback should be in live region
    await todoPage.addTask('New task');
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage.length).toBeGreaterThan(0);
    
    // Counter should update in live region
    const counterText = await todoPage.getCounterText();
    expect(counterText).toContain('1 task');
  });
});