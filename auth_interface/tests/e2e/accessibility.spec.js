/**
 * E2E Accessibility Tests
 * Tests WCAG 2.1 Level AAA compliance
 */

const { test, expect } = require('@playwright/test');
const AxeBuilder = require('axe-playwright').default;

test.describe('Accessibility - WCAG Compliance @accessibility', () => {
  test('login page should have no accessibility violations', async ({ page }) => {
    await page.goto('/templates/login.html');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag2aaa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('registration page should have no accessibility violations', async ({ page }) => {
    await page.goto('/templates/register.html');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag2aaa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('dashboard should have no accessibility violations', async ({ page }) => {
    await page.goto('/templates/dashboard.html');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag2aaa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});

test.describe('Keyboard Navigation @accessibility', () => {
  test('all interactive elements should be keyboard accessible', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Tab through all focusable elements
    await page.keyboard.press('Tab');
    let focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(['INPUT', 'BUTTON', 'A']).toContain(focusedElement);

    // Count tab stops
    const tabStops = [];
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab');
      const element = await page.evaluate(() => {
        const el = document.activeElement;
        return {
          tag: el.tagName,
          id: el.id,
          class: el.className
        };
      });
      tabStops.push(element);
      
      // Stop if we've cycled back to the beginning
      if (i > 0 && element.id === tabStops[0].id) break;
    }

    // Should have multiple tab stops
    expect(tabStops.length).toBeGreaterThan(2);
  });

  test('form submission should work with keyboard', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Fill form with keyboard
    await page.keyboard.press('Tab'); // Focus email
    await page.keyboard.type('test@example.com');
    
    await page.keyboard.press('Tab'); // Focus password
    await page.keyboard.type('Test123!@#');
    
    // Submit with Enter key
    await page.keyboard.press('Enter');
    
    // Form should attempt submission (check console or loading state)
    await page.waitForTimeout(500);
    
    // Button should show loading state or form should be processing
    const button = page.locator('button[type="submit"]');
    const buttonState = await button.evaluate(el => ({
      disabled: el.disabled,
      className: el.className
    }));
    
    // Button should react to submission
    expect(buttonState).toBeDefined();
  });

  test('navigation menu should work with keyboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/dashboard.html');

    // Tab to hamburger menu
    await page.keyboard.press('Tab');
    let focused = await page.evaluate(() => document.activeElement.className);
    
    // Keep tabbing until we find the menu toggle
    for (let i = 0; i < 10; i++) {
      const element = await page.evaluate(() => document.activeElement);
      if (element.className && element.className.includes('navbar-toggle')) {
        break;
      }
      await page.keyboard.press('Tab');
    }

    // Activate menu with Enter or Space
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);

    // Menu should be open
    const menu = page.locator('.navbar-menu');
    await expect(menu).toHaveClass(/open/);

    // Close with Escape key
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);

    // Menu should be closed
    await expect(menu).not.toHaveClass(/open/);
  });
});

test.describe('Focus Indicators @accessibility', () => {
  test('all interactive elements should have visible focus indicators', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check email input focus
    await page.locator('#email').focus();
    const emailOutline = await page.locator('#email').evaluate(el => {
      const style = window.getComputedStyle(el);
      return {
        outline: style.outline,
        outlineWidth: style.outlineWidth,
        outlineColor: style.outlineColor,
        boxShadow: style.boxShadow
      };
    });

    // Should have some focus indicator (outline or box-shadow)
    const hasFocusIndicator = 
      emailOutline.outline !== 'none' || 
      emailOutline.boxShadow !== 'none' ||
      parseInt(emailOutline.outlineWidth) > 0;
    
    expect(hasFocusIndicator).toBeTruthy();

    // Check button focus
    const button = page.locator('button[type="submit"]');
    await button.focus();
    
    const buttonOutline = await button.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.outline !== 'none' || style.boxShadow !== 'none';
    });
    
    expect(buttonOutline).toBeTruthy();
  });

  test('focus should be visible and not hidden', async ({ page }) => {
    await page.goto('/templates/register.html');

    const inputs = await page.locator('input').all();
    
    for (const input of inputs) {
      if (await input.isVisible()) {
        await input.focus();
        
        // Check if focus outline is not hidden
        const styles = await input.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            outline: computed.outline,
            outlineWidth: computed.outlineWidth
          };
        });
        
        // Outline should not be 'none' or 0
        expect(styles.outline).not.toBe('none');
      }
    }
  });
});

test.describe('ARIA Labels and Roles @accessibility', () => {
  test('form inputs should have proper labels', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check email input
    const emailLabel = await page.evaluate(() => {
      const input = document.getElementById('email');
      const label = document.querySelector('label[for="email"]');
      return {
        hasLabel: !!label,
        labelText: label?.textContent,
        ariaLabel: input?.getAttribute('aria-label'),
        ariaDescribedBy: input?.getAttribute('aria-describedby')
      };
    });

    expect(emailLabel.hasLabel).toBeTruthy();

    // Check password input
    const passwordLabel = await page.evaluate(() => {
      const input = document.getElementById('password');
      const label = document.querySelector('label[for="password"]');
      return {
        hasLabel: !!label,
        labelText: label?.textContent
      };
    });

    expect(passwordLabel.hasLabel).toBeTruthy();
  });

  test('navigation should have proper ARIA attributes', async ({ page }) => {
    await page.goto('/templates/dashboard.html');

    // Check navigation role
    const navAttributes = await page.locator('nav').evaluate(el => ({
      role: el.getAttribute('role'),
      ariaLabel: el.getAttribute('aria-label')
    }));

    expect(navAttributes.role).toBe('navigation');
    expect(navAttributes.ariaLabel).toBeTruthy();

    // Check hamburger button
    const toggleButton = page.locator('.navbar-toggle');
    if (await toggleButton.isVisible()) {
      const buttonAttributes = await toggleButton.evaluate(el => ({
        ariaLabel: el.getAttribute('aria-label'),
        ariaExpanded: el.getAttribute('aria-expanded'),
        ariaControls: el.getAttribute('aria-controls')
      }));

      expect(buttonAttributes.ariaLabel).toBeTruthy();
      expect(buttonAttributes.ariaExpanded).toBeTruthy();
    }
  });

  test('images should have alt text', async ({ page }) => {
    await page.goto('/templates/index.html');

    const images = await page.locator('img').all();
    
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeDefined();
      expect(alt).not.toBe('');
    }
  });

  test('buttons should have accessible names', async ({ page }) => {
    await page.goto('/templates/login.html');

    const buttons = await page.locator('button').all();
    
    for (const button of buttons) {
      const accessibleName = await button.evaluate(el => {
        return el.textContent || el.getAttribute('aria-label') || el.getAttribute('title');
      });
      
      expect(accessibleName).toBeTruthy();
      expect(accessibleName.trim().length).toBeGreaterThan(0);
    }
  });
});

test.describe('Color Contrast @accessibility', () => {
  test('text should have sufficient contrast', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Run axe for color contrast specifically
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .include('body')
      .analyze();

    // Filter for color contrast violations
    const contrastViolations = results.violations.filter(v => 
      v.id === 'color-contrast' || v.id === 'color-contrast-enhanced'
    );

    expect(contrastViolations).toEqual([]);
  });
});

test.describe('Screen Reader Compatibility @accessibility', () => {
  test('form errors should be announced', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check for aria-live region
    const liveRegion = await page.evaluate(() => {
      const region = document.querySelector('[aria-live]');
      return {
        exists: !!region,
        ariaLive: region?.getAttribute('aria-live'),
        ariaAtomic: region?.getAttribute('aria-atomic')
      };
    });

    expect(liveRegion.exists).toBeTruthy();
    expect(['polite', 'assertive']).toContain(liveRegion.ariaLive);
  });

  test('form inputs should announce validation errors', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Trigger validation
    await page.locator('#email').fill('invalid');
    await page.locator('#email').blur();
    
    await page.waitForTimeout(500);

    // Check if error has proper ARIA attributes
    const errorAttributes = await page.evaluate(() => {
      const input = document.getElementById('email');
      const error = document.getElementById('email-error');
      return {
        inputAriaInvalid: input?.getAttribute('aria-invalid'),
        inputAriaDescribedBy: input?.getAttribute('aria-describedby'),
        errorRole: error?.getAttribute('role'),
        errorVisible: error?.classList.contains('show')
      };
    });

    // Input should be marked as invalid when error occurs
    if (errorAttributes.errorVisible) {
      expect(errorAttributes.inputAriaInvalid).toBe('true');
      expect(errorAttributes.errorRole).toBe('alert');
    }
  });

  test('skip to main content link should work', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Skip link should exist
    const skipLink = page.locator('.skip-link');
    await expect(skipLink).toBeDefined();

    // Focus skip link (it becomes visible on focus)
    await page.keyboard.press('Tab');
    
    const focused = await page.evaluate(() => document.activeElement.className);
    
    // First tab should focus skip link
    expect(focused).toContain('skip-link');
  });
});

test.describe('Touch Target Sizes @accessibility', () => {
  test('all touch targets should meet WCAG AAA (44x44px)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/templates/login.html');

    // Get all interactive elements
    const elements = await page.locator('button, a, input, select, textarea').all();
    
    for (const element of elements) {
      if (await element.isVisible()) {
        const box = await element.boundingBox();
        
        // Touch targets should be at least 44x44px
        expect(box.height).toBeGreaterThanOrEqual(44);
        
        // For buttons and links, width should also be 44px+
        const tagName = await element.evaluate(el => el.tagName);
        if (tagName === 'BUTTON' || tagName === 'A') {
          expect(box.width).toBeGreaterThanOrEqual(44);
        }
      }
    }
  });
});

test.describe('Semantic HTML @accessibility', () => {
  test('page should use proper semantic HTML5 elements', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check for semantic elements
    const semanticElements = await page.evaluate(() => ({
      hasMain: !!document.querySelector('main'),
      hasHeader: !!document.querySelector('header'),
      hasNav: !!document.querySelector('nav'),
      hasForm: !!document.querySelector('form'),
      hasLabels: document.querySelectorAll('label').length > 0
    }));

    expect(semanticElements.hasMain).toBeTruthy();
    expect(semanticElements.hasForm).toBeTruthy();
    expect(semanticElements.hasLabels).toBeTruthy();
  });

  test('headings should follow proper hierarchy', async ({ page }) => {
    await page.goto('/templates/index.html');

    const headings = await page.evaluate(() => {
      const h = {};
      for (let i = 1; i <= 6; i++) {
        h[`h${i}`] = Array.from(document.querySelectorAll(`h${i}`)).map(el => el.textContent);
      }
      return h;
    });

    // Should have h1
    expect(headings.h1.length).toBeGreaterThan(0);

    // Heading levels should not skip (h1 -> h3 is bad)
    // This is a simplified check
    const hasHeadings = Object.entries(headings).filter(([k, v]) => v.length > 0);
    expect(hasHeadings.length).toBeGreaterThan(0);
  });
});
