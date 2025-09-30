import { test, expect } from './fixtures/test-fixtures';

/**
 * Responsive Design Tests
 * Tests mobile, tablet, and desktop layouts
 */

test.describe('Desktop Layout', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
  });
  
  test('should display full button text on desktop', async ({ todoPage }) => {
    // Assert - "Add Task" text should be visible on desktop
    const buttonText = todoPage.addButton.locator('.btn-text');
    await expect(buttonText).toBeVisible();
    await expect(buttonText).toHaveText('Add Task');
  });
  
  test('should show tasks in single column layout', async ({ todoPage }) => {
    // Arrange - Add tasks
    await todoPage.addTask('Desktop task 1');
    await todoPage.addTask('Desktop task 2');
    
    // Assert - Tasks should stack vertically
    const tasks = todoPage.getTaskItems();
    await expect(tasks).toHaveCount(2);
    
    // Check that container has appropriate width
    const container = todoPage.page.locator('.container');
    const boundingBox = await container.boundingBox();
    expect(boundingBox?.width).toBeLessThanOrEqual(800); // Max width constraint
  });
  
  test('should display all UI elements properly on desktop', async ({ todoPage }) => {
    // Assert - All major elements visible
    await expect(todoPage.header).toBeVisible();
    await expect(todoPage.subtitle).toBeVisible();
    await expect(todoPage.taskInput).toBeVisible();
    await expect(todoPage.addButton).toBeVisible();
    await expect(todoPage.taskCounter).toBeVisible();
  });
});

test.describe('Mobile Layout (Phone)', () => {
  
  test.beforeEach(async ({ page }) => {
    // iPhone 12 dimensions
    await page.setViewportSize({ width: 390, height: 844 });
  });
  
  test('should display correctly on mobile devices', async ({ todoPage }) => {
    // Assert - All elements should be visible and usable
    await expect(todoPage.header).toBeVisible();
    await expect(todoPage.taskInput).toBeVisible();
    await expect(todoPage.addButton).toBeVisible();
  });
  
  test('should allow task addition on mobile', async ({ todoPage }) => {
    // Act - Add task on mobile
    await todoPage.addTask('Mobile task');
    
    // Assert - Task should appear
    await expect(todoPage.getTaskByText('Mobile task')).toBeVisible();
  });
  
  test('should allow task completion on mobile', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Mobile task');
    
    // Act - Complete on mobile
    await todoPage.completeTask('Mobile task');
    
    // Assert - Task should be completed
    const task = todoPage.getTaskByText('Mobile task');
    await expect(task).toHaveClass(/completed/);
  });
  
  test('should allow task deletion on mobile', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Mobile task');
    
    // Act - Delete on mobile
    await todoPage.deleteTask('Mobile task');
    
    // Assert - Task should be deleted
    await expect(todoPage.getTaskItems()).toHaveCount(0);
  });
  
  test('should have touchable button sizes on mobile', async ({ todoPage }) => {
    // Arrange - Add task to show action buttons
    await todoPage.addTask('Touch test');
    const task = todoPage.getTaskByText('Touch test');
    
    // Assert - Buttons should be large enough for touch (min 44x44px)
    const completeBtn = task.locator('.btn-complete');
    const deleteBtn = task.locator('.btn-delete');
    
    const completeBtnBox = await completeBtn.boundingBox();
    const deleteBtnBox = await deleteBtn.boundingBox();
    
    expect(completeBtnBox?.width).toBeGreaterThanOrEqual(40);
    expect(completeBtnBox?.height).toBeGreaterThanOrEqual(40);
    expect(deleteBtnBox?.width).toBeGreaterThanOrEqual(40);
    expect(deleteBtnBox?.height).toBeGreaterThanOrEqual(40);
  });
  
  test('should wrap long task text on mobile', async ({ todoPage }) => {
    // Arrange - Add task with long text
    const longText = 'This is a very long task description that should wrap properly on mobile devices without breaking the layout';
    await todoPage.addTask(longText);
    
    // Assert - Task should be visible and text should wrap
    const task = todoPage.getTaskByText(longText);
    await expect(task).toBeVisible();
    
    // Check that task doesn't overflow viewport
    const taskBox = await task.boundingBox();
    const viewportSize = todoPage.page.viewportSize();
    expect(taskBox?.width).toBeLessThanOrEqual(viewportSize?.width || 390);
  });
});

test.describe('Tablet Layout (iPad)', () => {
  
  test.beforeEach(async ({ page }) => {
    // iPad Pro dimensions
    await page.setViewportSize({ width: 1024, height: 1366 });
  });
  
  test('should display correctly on tablet', async ({ todoPage }) => {
    // Assert - Layout should work on tablet
    await expect(todoPage.header).toBeVisible();
    await expect(todoPage.taskInput).toBeVisible();
    await expect(todoPage.addButton).toBeVisible();
  });
  
  test('should allow all interactions on tablet', async ({ todoPage }) => {
    // Act - Perform all basic operations
    await todoPage.addTask('Tablet task 1');
    await todoPage.addTask('Tablet task 2');
    await todoPage.completeTask('Tablet task 1');
    await todoPage.deleteTask('Tablet task 2');
    
    // Assert - Operations should work correctly
    await expect(todoPage.getTaskItems()).toHaveCount(1);
    await expect(todoPage.getTaskByText('Tablet task 1')).toHaveClass(/completed/);
  });
});

test.describe('Responsive Breakpoints', () => {
  
  test('should adapt layout at different viewport widths', async ({ todoPage }) => {
    const viewports = [
      { width: 320, height: 568, name: 'Small phone' },
      { width: 375, height: 667, name: 'Medium phone' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 1024, height: 768, name: 'Landscape tablet' },
      { width: 1440, height: 900, name: 'Desktop' },
    ];
    
    for (const viewport of viewports) {
      // Arrange - Set viewport
      await todoPage.page.setViewportSize({ 
        width: viewport.width, 
        height: viewport.height 
      });
      
      // Assert - All core elements should be visible
      await expect(todoPage.header).toBeVisible();
      await expect(todoPage.taskInput).toBeVisible();
      await expect(todoPage.addButton).toBeVisible();
      
      // Act - Add task
      await todoPage.clearStorage();
      await todoPage.page.reload();
      await todoPage.page.waitForLoadState('networkidle');
      await todoPage.addTask(`Task at ${viewport.name}`);
      
      // Assert - Task should be visible
      await expect(todoPage.getTaskItems()).toHaveCount(1);
    }
  });
  
  test('should not have horizontal scrollbar on any viewport', async ({ todoPage }) => {
    const viewports = [
      { width: 320, height: 568 },
      { width: 768, height: 1024 },
      { width: 1280, height: 720 },
    ];
    
    for (const viewport of viewports) {
      await todoPage.page.setViewportSize(viewport);
      
      // Add task with long text
      await todoPage.clearStorage();
      await todoPage.page.reload();
      await todoPage.page.waitForLoadState('networkidle');
      await todoPage.addTask('Long task '.repeat(20));
      
      // Check for horizontal overflow
      const hasHorizontalScroll = await todoPage.page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      
      expect(hasHorizontalScroll).toBe(false);
    }
  });
});

test.describe('Touch Interactions', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
  });
  
  test('should handle touch events on buttons', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Touch task');
    const task = todoPage.getTaskByText('Touch task');
    
    // Act - Tap complete button
    await task.locator('.btn-complete').tap();
    
    // Assert - Task should be completed
    await expect(task).toHaveClass(/completed/);
    
    // Act - Tap delete button
    await task.locator('.btn-delete').tap();
    await todoPage.page.waitForTimeout(400);
    
    // Assert - Task should be deleted
    await expect(todoPage.getTaskItems()).toHaveCount(0);
  });
  
  test('should handle rapid touches without issues', async ({ todoPage }) => {
    // Arrange
    await todoPage.addTask('Rapid touch task');
    const task = todoPage.getTaskByText('Rapid touch task');
    const completeBtn = task.locator('.btn-complete');
    
    // Act - Rapid taps
    await completeBtn.tap();
    await completeBtn.tap();
    await completeBtn.tap();
    
    // Assert - Should handle all taps (final state: completed)
    await expect(task).toHaveClass(/completed/);
  });
});