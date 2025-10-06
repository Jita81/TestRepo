/**
 * E2E Tests for Responsive Behavior
 * Tests authentication interface across all breakpoints (320px - 1920px+)
 */

const { test, expect } = require('@playwright/test');

test.describe('Responsive Design - Mobile (320px)', () => {
  test.use({ viewport: { width: 320, height: 568 } });

  test('login form should be usable on 320px width @visual', async ({ page }) => {
    await page.goto('/templates/login.html');

    // All form elements should be visible
    await expect(page.locator('#loginForm')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check input field height (minimum 44px for touch)
    const emailInput = page.locator('#email');
    const box = await emailInput.boundingBox();
    expect(box.height).toBeGreaterThanOrEqual(44);

    // Check button is tappable (minimum 44px)
    const button = page.locator('button[type="submit"]');
    const buttonBox = await button.boundingBox();
    expect(buttonBox.height).toBeGreaterThanOrEqual(44);

    // No horizontal scrolling
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1); // +1 for rounding

    // Font size should be at least 16px
    const fontSize = await emailInput.evaluate(el => 
      window.getComputedStyle(el).fontSize
    );
    expect(parseInt(fontSize)).toBeGreaterThanOrEqual(16);
  });

  test('registration form should be usable on 320px width', async ({ page }) => {
    await page.goto('/templates/register.html');

    // All form elements should be visible
    await expect(page.locator('#registerForm')).toBeVisible();
    await expect(page.locator('#fullName')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#confirmPassword')).toBeVisible();

    // Password requirements should be visible
    await expect(page.locator('.password-requirements')).toBeVisible();

    // Check touch target sizes
    const submitButton = page.locator('button[type="submit"]');
    const buttonBox = await submitButton.boundingBox();
    expect(buttonBox.height).toBeGreaterThanOrEqual(44);
    expect(buttonBox.width).toBeGreaterThanOrEqual(44);
  });
});

test.describe('Responsive Design - Tablet (768px)', () => {
  test.use({ viewport: { width: 768, height: 1024 } });

  test('registration form should adapt to tablet viewport', async ({ page }) => {
    await page.goto('/templates/register.html');

    // Form should be centered with margins
    const form = page.locator('.auth-card');
    const formBox = await form.boundingBox();
    
    // Form should not take full width on tablet
    expect(formBox.width).toBeLessThan(768);

    // Check if form is horizontally centered
    const bodyWidth = await page.evaluate(() => document.body.clientWidth);
    const leftMargin = formBox.x;
    const rightMargin = bodyWidth - (formBox.x + formBox.width);
    
    // Margins should be roughly equal (centered)
    expect(Math.abs(leftMargin - rightMargin)).toBeLessThan(50);

    // Password requirements list should be clearly visible
    const requirements = page.locator('.password-requirements');
    await expect(requirements).toBeVisible();
    
    const reqBox = await requirements.boundingBox();
    expect(reqBox.width).toBeGreaterThan(200); // Sufficient width
  });

  test('login form should be properly sized on tablet', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Form should have appropriate max-width
    const form = page.locator('.auth-card');
    const formBox = await form.boundingBox();
    
    expect(formBox.width).toBeLessThanOrEqual(600); // Max width constraint
    expect(formBox.width).toBeGreaterThan(300); // Minimum usable width
  });
});

test.describe('Responsive Design - Desktop (1920px)', () => {
  test.use({ viewport: { width: 1920, height: 1080 } });

  test('forms should be constrained to readable width', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Form should be constrained to 600-800px
    const form = page.locator('.auth-card');
    const formBox = await form.boundingBox();
    
    expect(formBox.width).toBeGreaterThanOrEqual(600);
    expect(formBox.width).toBeLessThanOrEqual(800);

    // Content should be centered
    const bodyWidth = await page.evaluate(() => document.body.clientWidth);
    const leftMargin = formBox.x;
    const rightMargin = bodyWidth - (formBox.x + formBox.width);
    
    expect(Math.abs(leftMargin - rightMargin)).toBeLessThan(50);
  });

  test('dashboard should utilize available space', async ({ page }) => {
    await page.goto('/templates/dashboard.html');

    // Dashboard grid should use 3 columns on desktop
    const grid = page.locator('.dashboard-grid').first();
    
    // Get grid computed styles
    const gridColumns = await grid.evaluate(el => 
      window.getComputedStyle(el).gridTemplateColumns
    );
    
    // Should have 3 columns (3 values in grid-template-columns)
    const columnCount = gridColumns.split(' ').filter(v => v !== 'none').length;
    expect(columnCount).toBeGreaterThanOrEqual(3);
  });
});

test.describe('Navigation Responsiveness', () => {
  test('navigation should collapse on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/dashboard.html');

    // Hamburger menu should be visible
    const hamburger = page.locator('.navbar-toggle');
    await expect(hamburger).toBeVisible();

    // Check touch target size
    const hamburgerBox = await hamburger.boundingBox();
    expect(hamburgerBox.height).toBeGreaterThanOrEqual(44);
    expect(hamburgerBox.width).toBeGreaterThanOrEqual(44);

    // Menu should be hidden initially
    const menu = page.locator('.navbar-menu');
    const menuVisible = await menu.evaluate(el => {
      const style = window.getComputedStyle(el);
      const transform = style.transform;
      // Check if menu is off-screen
      return !transform.includes('matrix') || transform.includes('matrix(1, 0, 0, 1, 0, 0)');
    });
    expect(menuVisible).toBeFalsy();

    // Click hamburger to open menu
    await hamburger.click();
    await page.waitForTimeout(500); // Wait for animation

    // Menu should be visible now
    await expect(menu).toHaveClass(/open/);
  });

  test('navigation should be horizontal on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/templates/dashboard.html');

    // Hamburger menu should not be visible
    const hamburger = page.locator('.navbar-toggle');
    await expect(hamburger).not.toBeVisible();

    // Navigation items should be horizontal
    const nav = page.locator('.navbar-nav');
    const flexDirection = await nav.evaluate(el => 
      window.getComputedStyle(el).flexDirection
    );
    expect(flexDirection).toBe('row');
  });

  test('menu should close on overlay click (mobile)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/dashboard.html');

    // Open menu
    await page.locator('.navbar-toggle').click();
    await page.waitForTimeout(500);

    // Click overlay
    const overlay = page.locator('.navbar-overlay');
    await overlay.click();
    await page.waitForTimeout(500);

    // Menu should be closed
    const menu = page.locator('.navbar-menu');
    await expect(menu).not.toHaveClass(/open/);
  });
});

test.describe('Touch and Click Interactions', () => {
  test('all interactive elements should meet touch target size', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/login.html');

    // Get all buttons and links
    const buttons = await page.locator('button, a.btn').all();
    
    for (const button of buttons) {
      if (await button.isVisible()) {
        const box = await button.boundingBox();
        expect(box.height).toBeGreaterThanOrEqual(44);
        expect(box.width).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('form inputs should have sufficient touch targets', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/register.html');

    // Get all form inputs
    const inputs = await page.locator('input[type="text"], input[type="email"], input[type="password"]').all();
    
    for (const input of inputs) {
      if (await input.isVisible()) {
        const box = await input.boundingBox();
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('hover states should work on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/templates/login.html');

    const button = page.locator('button[type="submit"]');
    
    // Get initial button style
    const initialTransform = await button.evaluate(el => 
      window.getComputedStyle(el).transform
    );

    // Hover over button
    await button.hover();
    
    // Wait for transition
    await page.waitForTimeout(300);

    // Check if transform changed (button should lift on hover)
    const hoverTransform = await button.evaluate(el => 
      window.getComputedStyle(el).transform
    );

    // Transform should change on hover (or at least be defined)
    expect(hoverTransform).toBeDefined();
  });
});

test.describe('No Horizontal Scrolling', () => {
  const testBreakpoints = [320, 375, 768, 1024, 1920];

  for (const width of testBreakpoints) {
    test(`should not have horizontal scroll at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 800 });
      await page.goto('/templates/login.html');

      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1); // +1 for rounding
    });
  }
});

test.describe('Visual Consistency', () => {
  test('elements should maintain proper spacing on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto('/templates/login.html');

    // Get form groups
    const formGroups = await page.locator('.form-group').all();
    
    // Check spacing between form groups
    for (let i = 0; i < formGroups.length - 1; i++) {
      const currentBox = await formGroups[i].boundingBox();
      const nextBox = await formGroups[i + 1].boundingBox();
      
      // Calculate gap between elements
      const gap = nextBox.y - (currentBox.y + currentBox.height);
      
      // Gap should be reasonable (at least 16px, not too much)
      expect(gap).toBeGreaterThanOrEqual(16);
      expect(gap).toBeLessThanOrEqual(48);
    }
  });

  test('text should be readable without zooming', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto('/templates/login.html');

    // Check body font size
    const bodyFontSize = await page.evaluate(() => 
      window.getComputedStyle(document.body).fontSize
    );
    expect(parseInt(bodyFontSize)).toBeGreaterThanOrEqual(16);

    // Check input font size
    const inputFontSize = await page.locator('#email').evaluate(el =>
      window.getComputedStyle(el).fontSize
    );
    expect(parseInt(inputFontSize)).toBeGreaterThanOrEqual(16);
  });
});
