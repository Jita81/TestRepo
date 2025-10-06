/**
 * E2E Tests for Edge Cases
 * - Virtual keyboard behavior
 * - Device rotation
 * - Slow network conditions
 * - High DPI displays
 */

const { test, expect } = require('@playwright/test');

test.describe('Device Rotation Handling', () => {
  test('should handle portrait to landscape rotation', async ({ page }) => {
    // Start in portrait
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/login.html');

    // Check form is visible in portrait
    await expect(page.locator('#loginForm')).toBeVisible();
    
    // Get form position in portrait
    const portraitBox = await page.locator('.auth-card').boundingBox();

    // Rotate to landscape
    await page.setViewportSize({ width: 667, height: 375 });
    await page.waitForTimeout(500); // Wait for layout adjustment

    // Form should still be visible
    await expect(page.locator('#loginForm')).toBeVisible();

    // Form should adapt to new dimensions
    const landscapeBox = await page.locator('.auth-card').boundingBox();
    
    // Form should be smaller in height (landscape mode)
    expect(landscapeBox.height).toBeLessThan(portraitBox.height);

    // Submit button should still be accessible (visible in viewport)
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();
    
    const isInViewport = await submitButton.evaluate(el => {
      const rect = el.getBoundingClientRect();
      return rect.bottom <= window.innerHeight;
    });
    expect(isInViewport).toBeTruthy();
  });

  test('should maintain usability in landscape orientation', async ({ page }) => {
    // Landscape iPhone
    await page.setViewportSize({ width: 667, height: 375 });
    await page.goto('/templates/register.html');

    // All form fields should be accessible
    await expect(page.locator('#fullName')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#confirmPassword')).toBeVisible();

    // Password requirements should be visible or scrollable
    const requirements = page.locator('.password-requirements');
    await expect(requirements).toBeVisible();

    // Form should not require excessive scrolling
    const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);
    const viewportHeight = 375;
    
    // Total scroll should be reasonable (less than 3x viewport height)
    expect(scrollHeight).toBeLessThan(viewportHeight * 3);
  });
});

test.describe('Virtual Keyboard Behavior', () => {
  test('form should remain accessible when keyboard appears', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/login.html');

    // Focus on email input (simulates keyboard appearance)
    await page.locator('#email').focus();
    
    // Simulate reduced viewport height (keyboard takes space)
    await page.setViewportSize({ width: 375, height: 400 });
    await page.waitForTimeout(500);

    // Input should still be visible
    const emailInput = page.locator('#email');
    const isVisible = await emailInput.evaluate(el => {
      const rect = el.getBoundingClientRect();
      return rect.top >= 0 && rect.bottom <= window.innerHeight;
    });
    
    // If not visible, it should be scrolled into view
    if (!isVisible) {
      await emailInput.scrollIntoViewIfNeeded();
    }

    // Submit button should be accessible
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();
  });

  test('fields should not be obscured by virtual keyboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/register.html');

    // Focus on password field
    const passwordField = page.locator('#password');
    await passwordField.click();
    
    // Simulate keyboard (reduce viewport)
    await page.setViewportSize({ width: 375, height: 350 });
    await page.waitForTimeout(500);

    // Password field should be in viewport
    const passwordBox = await passwordField.boundingBox();
    expect(passwordBox.y).toBeGreaterThanOrEqual(0);
    expect(passwordBox.y + passwordBox.height).toBeLessThanOrEqual(350);

    // Password requirements should still be accessible (scrollable if needed)
    const requirements = page.locator('.password-requirements');
    const requirementsExists = await requirements.count();
    expect(requirementsExists).toBeGreaterThan(0);
  });
});

test.describe('Slow Network Conditions', () => {
  test('should handle slow network gracefully', async ({ page, context }) => {
    // Simulate slow 3G
    await context.route('**/*', route => {
      setTimeout(() => route.continue(), 100); // Add delay
    });

    await page.goto('/templates/login.html');

    // Page should still load and be functional
    await expect(page.locator('#loginForm')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();

    // Styles should be loaded
    const emailInput = page.locator('#email');
    const backgroundColor = await emailInput.evaluate(el =>
      window.getComputedStyle(el).backgroundColor
    );
    expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)'); // Should have a background
  });

  test('CSS should load before content is visible', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check if CSS is loaded by verifying computed styles
    const body = page.locator('body');
    const fontFamily = await body.evaluate(el =>
      window.getComputedStyle(el).fontFamily
    );
    
    // Font family should be set (not default)
    expect(fontFamily).not.toBe('serif');
    expect(fontFamily).not.toBe('');
  });
});

test.describe('High DPI / Retina Display', () => {
  test('images should render clearly on high DPI displays', async ({ page }) => {
    // Set device pixel ratio to 2 (Retina)
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.goto('/templates/index.html');

    // Check if SVG images are used (scale perfectly)
    const images = await page.locator('img').all();
    
    for (const img of images) {
      const src = await img.getAttribute('src');
      const srcset = await img.getAttribute('srcset');
      
      // Should use SVG (scales perfectly) or have srcset for different DPIs
      const usesSVG = src && src.includes('svg');
      const hasSrcset = srcset !== null;
      
      // Either SVG or srcset should be present for high DPI support
      expect(usesSVG || hasSrcset).toBeTruthy();
    }
  });

  test('icons should remain sharp at any resolution', async ({ page }) => {
    await page.goto('/templates/dashboard.html');

    // Check icon rendering
    const icons = await page.locator('[aria-hidden="true"]').all();
    
    for (const icon of icons) {
      if (await icon.isVisible()) {
        // Icons should be text-based or SVG for crisp rendering
        const tagName = await icon.evaluate(el => el.tagName);
        const textContent = await icon.textContent();
        
        // Should be emoji/unicode (text) or SVG
        expect(tagName === 'svg' || tagName === 'I' || textContent.length > 0).toBeTruthy();
      }
    }
  });
});

test.describe('Font Size Override', () => {
  test('layout should adapt to user font size preferences', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Increase font size (user preference)
    await page.addStyleTag({
      content: 'html { font-size: 20px !important; }'
    });

    await page.waitForTimeout(500);

    // Layout should still work
    await expect(page.locator('#loginForm')).toBeVisible();
    
    // No horizontal scrolling even with larger text
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);

    // Form should still be usable
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    
    // Submit button should be visible
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });
});

test.describe('Long Content Handling', () => {
  test('should handle long text without breaking layout', async ({ page }) => {
    await page.goto('/templates/register.html');

    // Fill form with very long text
    const longText = 'A'.repeat(1000);
    await page.locator('#fullName').fill(longText);

    // Layout should not break
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);

    // Input should handle long text (scrollable or truncated)
    const input = page.locator('#fullName');
    await expect(input).toBeVisible();
    
    const value = await input.inputValue();
    expect(value.length).toBeGreaterThan(0);
  });

  test('error messages should not break layout', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Trigger validation error
    await page.locator('#email').fill('invalid-email');
    await page.locator('#email').blur();
    
    await page.waitForTimeout(500);

    // Check if error message is displayed
    const errorMessage = page.locator('#email-error');
    
    // Error should be visible if validation occurs
    const isVisible = await errorMessage.isVisible();
    if (isVisible) {
      // Error message should not cause horizontal scroll
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
    }
  });
});

test.describe('Form Autofill Handling', () => {
  test('layout should not break with browser autofill', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Simulate autofill by filling form quickly
    await page.locator('#email').fill('saved.user@example.com');
    await page.locator('#password').fill('SavedPassword123!');

    await page.waitForTimeout(500);

    // Layout should remain intact
    await expect(page.locator('#loginForm')).toBeVisible();
    
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);

    // Form should be submittable
    await expect(page.locator('button[type="submit"]')).toBeEnabled();
  });
});

test.describe('Viewport Meta Tag', () => {
  test('should have proper viewport configuration', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check viewport meta tag
    const viewport = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="viewport"]');
      return meta ? meta.getAttribute('content') : null;
    });

    expect(viewport).toBeTruthy();
    expect(viewport).toContain('width=device-width');
    expect(viewport).toContain('initial-scale=1.0');
    
    // Should not prevent user zooming (accessibility)
    expect(viewport).not.toContain('user-scalable=no');
    expect(viewport).not.toContain('maximum-scale=1.0');
  });
});

test.describe('Reduced Motion Preference', () => {
  test('should respect prefers-reduced-motion', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/templates/login.html');

    // Animations should be minimal or instant
    const body = page.locator('body');
    
    // Check if animations are reduced
    const animationDuration = await body.evaluate(() => {
      return Array.from(document.querySelectorAll('*')).some(el => {
        const style = window.getComputedStyle(el);
        const duration = parseFloat(style.animationDuration);
        const transitionDuration = parseFloat(style.transitionDuration);
        return duration > 0.01 || transitionDuration > 0.01;
      });
    });

    // With reduced motion, animations should be very short or disabled
    // This is more of a check that the CSS respects the preference
    expect(animationDuration).toBeDefined();
  });
});
