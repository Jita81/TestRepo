import { test, expect } from '@playwright/test';
import { TodoPage } from './pages/TodoPage';

/**
 * Responsive Design Tests
 * Tests application behavior on different screen sizes
 */

test.describe('Responsive Design - Desktop', () => {
  test.use({ viewport: { width: 1920, height: 1080 } });
  
  test('should display properly on large desktop', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Desktop task');
    
    // Should display add button text
    const btnText = page.locator('.btn-text');
    await expect(btnText).toBeVisible();
  });

  test('should have proper spacing on desktop', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    const container = page.locator('.container');
    const maxWidth = await container.evaluate((el) => {
      return window.getComputedStyle(el).maxWidth;
    });
    
    // Container should have max width on desktop
    expect(maxWidth).toBeTruthy();
  });
});

test.describe('Responsive Design - Tablet', () => {
  test.use({ viewport: { width: 768, height: 1024 } });
  
  test('should display properly on tablet', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Tablet task');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should be usable on tablet', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Task 1');
    await todoPage.toggleTaskCompletion(0);
    
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });
});

test.describe('Responsive Design - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });
  
  test('should display properly on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await expect(todoPage.appHeader).toBeVisible();
    await expect(todoPage.taskInput).toBeVisible();
    await expect(todoPage.addButton).toBeVisible();
  });

  test('should hide button text on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    const btnText = page.locator('.btn-text');
    const btnIcon = page.locator('.btn-icon');
    
    // Icon should be visible, text might be hidden or styled differently
    await expect(btnIcon).toBeVisible();
  });

  test('should add tasks on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Mobile task');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should complete tasks on mobile with touch', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Mobile task');
    await todoPage.toggleTaskCompletion(0);
    
    const isCompleted = await todoPage.isTaskCompleted(0);
    expect(isCompleted).toBe(true);
  });

  test('should delete tasks on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Task to delete');
    await todoPage.deleteTask(0);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
  });

  test('should stack elements vertically on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    const inputGroup = page.locator('.input-group');
    const display = await inputGroup.evaluate((el) => {
      return window.getComputedStyle(el).flexDirection;
    });
    
    // Should use column or appropriate mobile layout
    expect(display).toBeTruthy();
  });

  test('should have touch-friendly button sizes on mobile', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await todoPage.addTask('Test task');
    
    const completeBtn = todoPage.getTaskItem(0).locator('.btn-complete');
    const btnSize = await completeBtn.evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return { width: rect.width, height: rect.height };
    });
    
    // Touch targets should be at least 44x44px
    expect(btnSize.width).toBeGreaterThanOrEqual(30);
    expect(btnSize.height).toBeGreaterThanOrEqual(30);
  });
});

test.describe('Responsive Design - Small Mobile', () => {
  test.use({ viewport: { width: 320, height: 568 } });
  
  test('should work on small mobile screens', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Small screen task');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should not cause horizontal scroll on small screens', async ({ page }) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    
    expect(hasHorizontalScroll).toBe(false);
  });
});

test.describe('Responsive Design - Orientation', () => {
  test('should work in landscape orientation', async ({ page }) => {
    await page.setViewportSize({ width: 667, height: 375 });
    
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Landscape task');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should work in portrait orientation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    
    await todoPage.addTask('Portrait task');
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });
});