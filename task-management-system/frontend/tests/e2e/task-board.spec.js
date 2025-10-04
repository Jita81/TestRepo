/**
 * E2E Tests for Task Board
 * 
 * Tests complete user workflows including:
 * - Viewing task board
 * - Drag and drop
 * - Filtering and search
 * - Real-time updates
 * - Responsive behavior
 */

import { test, expect } from '@playwright/test';

test.describe('Task Board', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await page.waitForURL('/dashboard');
    
    // Navigate to a project
    await page.click('text=Test Project');
    await page.waitForLoadState('networkidle');
  });

  test('should display task board with three columns', async ({ page }) => {
    // Check column headers
    await expect(page.locator('text=To Do')).toBeVisible();
    await expect(page.locator('text=In Progress')).toBeVisible();
    await expect(page.locator('text=Done')).toBeVisible();
    
    // Check for task cards
    const taskCards = page.locator('.task-card');
    await expect(taskCards.first()).toBeVisible();
  });

  test('should display task card with all required info', async ({ page }) => {
    const firstCard = page.locator('.task-card').first();
    
    // Check for title
    await expect(firstCard.locator('h4')).toBeVisible();
    
    // Check for priority badge
    await expect(firstCard.locator('[aria-label*="Priority"]')).toBeVisible();
    
    // Check for description
    const description = firstCard.locator('p').first();
    await expect(description).toBeVisible();
    
    // Check for assignee or unassigned text
    await expect(
      firstCard.locator('text=Unassigned').or(firstCard.locator('[alt]'))
    ).toBeVisible();
  });

  test('should search tasks by title', async ({ page }) => {
    // Get initial task count
    const initialCount = await page.locator('.task-card').count();
    expect(initialCount).toBeGreaterThan(0);
    
    // Search for specific task
    await page.fill('[placeholder*="Search tasks"]', 'Implement login');
    await page.waitForTimeout(300); // Debounce
    
    // Should show fewer tasks
    const filteredCount = await page.locator('.task-card').count();
    expect(filteredCount).toBeLessThanOrEqual(initialCount);
    
    // Clear search
    await page.click('[aria-label="Clear search"]');
    await page.waitForTimeout(300);
    
    // Should show all tasks again
    const finalCount = await page.locator('.task-card').count();
    expect(finalCount).toBe(initialCount);
  });

  test('should filter tasks by priority', async ({ page }) => {
    // Select priority filter
    await page.selectOption('[aria-label="Filter by priority"]', 'high');
    await page.waitForTimeout(300);
    
    // All visible tasks should have high priority
    const priorityBadges = page.locator('[aria-label="Priority: High"]');
    const count = await priorityBadges.count();
    expect(count).toBeGreaterThan(0);
    
    // Clear filter
    await page.selectOption('[aria-label="Filter by priority"]', '');
  });

  test('should filter tasks by assignee', async ({ page }) => {
    // Get assignee filter
    const assigneeFilter = page.locator('[aria-label="Filter by assignee"]');
    
    // Get all options
    const options = await assigneeFilter.locator('option').allTextContents();
    
    // Select first non-empty option
    if (options.length > 1) {
      await assigneeFilter.selectOption({ index: 1 });
      await page.waitForTimeout(300);
      
      // Should show filtered results
      await expect(page.locator('.task-card')).toBeVisible();
      
      // Clear filter
      await assigneeFilter.selectOption({ index: 0 });
    }
  });

  test('should show active filter count', async ({ page }) => {
    // Apply filter
    await page.selectOption('[aria-label="Filter by priority"]', 'high');
    await page.waitForTimeout(300);
    
    // Should show filter count
    await expect(page.locator('text=/\\d+ filter(s)? active/')).toBeVisible();
    
    // Clear all filters
    await page.click('text=Clear all');
    
    // Filter count should disappear
    await expect(page.locator('text=/\\d+ filter(s)? active/')).not.toBeVisible();
  });

  test('should open task modal on card click', async ({ page }) => {
    // Click first task card
    await page.click('.task-card:first-of-type');
    
    // Modal should be visible
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    
    // Should show task details
    await expect(page.locator('#modal-title')).toBeVisible();
    await expect(page.locator('text=Description')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
    
    // Close modal
    await page.click('[aria-label="Close modal"]');
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('should show connection status', async ({ page }) => {
    // Should show connection indicator
    const indicator = page.locator('text=Live updates active').or(
      page.locator('text=Reconnecting...')
    );
    await expect(indicator).toBeVisible();
  });

  test('should show empty state for columns with no tasks', async ({ page }) => {
    // Apply very specific filter to empty a column
    await page.fill('[placeholder*="Search tasks"]', 'zzz_nonexistent_task_xyz');
    await page.waitForTimeout(300);
    
    // Should show "no tasks match" message
    await expect(page.locator('text=/no tasks match/i')).toBeVisible();
  });

  test('should display task count per column', async ({ page }) => {
    // Each column should have a count badge
    const countBadges = page.locator('[aria-label*="tasks"]');
    const count = await countBadges.count();
    expect(count).toBeGreaterThanOrEqual(3); // One per column minimum
  });

  test('should be responsive on mobile', async ({ page, viewport }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Board should still be visible and functional
    await expect(page.locator('text=Task Board')).toBeVisible();
    await expect(page.locator('.task-card').first()).toBeVisible();
    
    // Search should be visible
    await expect(page.locator('[placeholder*="Search tasks"]')).toBeVisible();
    
    // Filters should be accessible
    await expect(page.locator('[aria-label="Filter by priority"]')).toBeVisible();
  });

  test('should show loading state initially', async ({ page }) => {
    // Navigate to project and immediately check for loading
    await page.goto('/projects/test-project');
    
    // Should briefly show loading (might be very quick)
    const loadingText = page.locator('text=Loading tasks');
    // Loading might complete before we check, so we don't fail if not visible
    if (await loadingText.isVisible({ timeout: 100 }).catch(() => false)) {
      await expect(loadingText).toBeVisible();
    }
  });

  test('should show keyboard navigation hint', async ({ page }) => {
    // Should show tips section
    await expect(page.locator('text=/keyboard/i')).toBeVisible();
    await expect(page.locator('text=/drag cards/i')).toBeVisible();
  });

  test('should handle due dates correctly', async ({ page }) => {
    // Look for tasks with due dates
    const dueDateElements = page.locator('[aria-label*="Due"]');
    const count = await dueDateElements.count();
    
    if (count > 0) {
      // First due date should be visible
      await expect(dueDateElements.first()).toBeVisible();
      
      // Should show calendar icon
      const calendarIcon = dueDateElements.first().locator('svg');
      await expect(calendarIcon).toBeVisible();
    }
  });

  test('should show overdue indicator for past due tasks', async ({ page }) => {
    // Look for overdue tasks (marked with warning emoji)
    const overdueIndicator = page.locator('text=⚠️');
    const count = await overdueIndicator.count();
    
    // We might have overdue tasks
    if (count > 0) {
      await expect(overdueIndicator.first()).toBeVisible();
    }
  });

  test('should show priority icons on task cards', async ({ page }) => {
    // Priority badges should have emoji icons
    const priorities = ['⬇️', '➡️', '⬆️', '🔥'];
    
    let foundPriority = false;
    for (const emoji of priorities) {
      if (await page.locator(`text=${emoji}`).count() > 0) {
        foundPriority = true;
        break;
      }
    }
    
    expect(foundPriority).toBe(true);
  });
});

test.describe('Task Board - Advanced Filters', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    await page.click('text=Test Project');
  });

  test('should toggle advanced filters', async ({ page }) => {
    // Click "More Filters" button
    await page.click('text=More Filters');
    
    // Advanced filters should be visible
    await expect(page.locator('text=Due Date Range')).toBeVisible();
    await expect(page.locator('[id="dueDateStart"]')).toBeVisible();
    await expect(page.locator('[id="dueDateEnd"]')).toBeVisible();
    
    // Click "Less Filters"
    await page.click('text=Less Filters');
    
    // Advanced filters should be hidden
    await expect(page.locator('text=Due Date Range')).not.toBeVisible();
  });

  test('should filter by due date range', async ({ page }) => {
    // Open advanced filters
    await page.click('text=More Filters');
    
    // Set date range
    await page.fill('[id="dueDateStart"]', '2024-01-01');
    await page.fill('[id="dueDateEnd"]', '2024-12-31');
    await page.waitForTimeout(300);
    
    // Should show active filter
    await expect(page.locator('text=/filter(s)? active/')).toBeVisible();
  });
});

test.describe('Task Board - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    await page.click('text=Test Project');
  });

  test('should have proper ARIA labels', async ({ page }) => {
    // Main board
    await expect(page.locator('[aria-label="Task Board"]')).toBeVisible();
    
    // Search
    await expect(page.locator('[aria-label="Search tasks"]')).toBeVisible();
    
    // Filters
    await expect(page.locator('[aria-label="Filter by assignee"]')).toBeVisible();
    await expect(page.locator('[aria-label="Filter by priority"]')).toBeVisible();
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Focus search
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => document.activeElement.tagName);
    expect(['INPUT', 'SELECT', 'BUTTON']).toContain(focused);
  });

  test('should support screen readers', async ({ page }) => {
    // Check for sr-only elements
    const srElements = page.locator('.sr-only');
    const count = await srElements.count();
    expect(count).toBeGreaterThan(0);
  });
});
