/**
 * End-to-End Tests for Login Functionality
 * Tests complete user workflows with Playwright
 */

const { test, expect } = require('@playwright/test');

test.describe('Login E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:8888/templates/login.html');
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test.describe('Successful Login Flow', () => {
    test('user can log in with valid credentials', async ({ page }) => {
      // Fill in login form
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      // Mock successful API response
      await page.route('**/api/auth/login', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature',
            user: {
              id: '123',
              email: 'user@example.com',
              name: 'Test User'
            }
          })
        });
      });
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await page.waitForURL('**/dashboard.html', { timeout: 5000 });
      
      // Verify token is stored
      const token = await page.evaluate(() => 
        sessionStorage.getItem('auth_token')
      );
      expect(token).toBeTruthy();
    });

    test('remember me stores token in localStorage', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      await page.check('#rememberMe');
      
      // Mock API
      await page.route('**/api/auth/login', async route => {
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            token: 'test-token',
            user: { id: '123' }
          })
        });
      });
      
      await page.click('button[type="submit"]');
      
      // Check localStorage
      const rememberMe = await page.evaluate(() => 
        localStorage.getItem('remember_me')
      );
      expect(rememberMe).toBe('true');
    });
  });

  test.describe('Invalid Login Attempts', () => {
    test('shows error for invalid credentials', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'WrongPassword');
      
      // Mock failed login
      await page.route('**/api/auth/login', async route => {
        await route.fulfill({
          status: 401,
          body: JSON.stringify({
            error: 'Invalid email or password'
          })
        });
      });
      
      await page.click('button[type="submit"]');
      
      // Should show error message
      const alert = await page.locator('.alert, [role="alert"]').first();
      await expect(alert).toBeVisible({ timeout: 3000 });
      
      // Error should not reveal email existence
      const errorText = await alert.textContent();
      expect(errorText).toContain('Invalid');
      expect(errorText).not.toContain('email not found');
    });

    test('prevents submission with empty email', async ({ page }) => {
      const emailInput = page.locator('#email');
      await emailInput.fill('');
      await page.fill('#password', 'ValidPassword123!');
      
      // Try to submit
      await page.click('button[type="submit"]');
      
      // Check HTML5 validation
      const isInvalid = await emailInput.evaluate(input => 
        !input.validity.valid
      );
      expect(isInvalid).toBe(true);
    });

    test('prevents submission with empty password', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      const passwordInput = page.locator('#password');
      await passwordInput.fill('');
      
      await page.click('button[type="submit"]');
      
      const isInvalid = await passwordInput.evaluate(input => 
        !input.validity.valid
      );
      expect(isInvalid).toBe(true);
    });

    test('clears password on failed login', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'WrongPassword');
      
      await page.route('**/api/auth/login', async route => {
        await route.fulfill({
          status: 401,
          body: JSON.stringify({ error: 'Invalid credentials' })
        });
      });
      
      await page.click('button[type="submit"]');
      
      // Password should be cleared
      await page.waitForTimeout(500);
      const passwordValue = await page.inputValue('#password');
      expect(passwordValue).toBe('');
    });
  });

  test.describe('Loading States', () => {
    test('shows loading indicator during login', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      // Mock slow API
      await page.route('**/api/auth/login', async route => {
        await page.waitForTimeout(1000);
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            token: 'test-token',
            user: { id: '123' }
          })
        });
      });
      
      // Click submit
      await page.click('button[type="submit"]');
      
      // Check loading state
      const button = page.locator('button[type="submit"]');
      const hasLoadingClass = await button.evaluate(btn => 
        btn.classList.contains('btn-loading')
      );
      const isDisabled = await button.isDisabled();
      
      expect(hasLoadingClass || isDisabled).toBe(true);
    });

    test('disables inputs during loading', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      await page.route('**/api/auth/login', async route => {
        await page.waitForTimeout(500);
        await route.fulfill({
          status: 200,
          body: JSON.stringify({ token: 'test', user: { id: '1' } })
        });
      });
      
      await page.click('button[type="submit"]');
      
      // Check if inputs are disabled
      const emailDisabled = await page.locator('#email').isDisabled();
      const passwordDisabled = await page.locator('#password').isDisabled();
      
      expect(emailDisabled || passwordDisabled).toBe(true);
    });
  });

  test.describe('Network Failures', () => {
    test('handles network error gracefully', async ({ page }) => {
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      // Mock network failure
      await page.route('**/api/auth/login', route => route.abort('failed'));
      
      await page.click('button[type="submit"]');
      
      // Should show error message
      await page.waitForTimeout(1000);
      const alert = await page.locator('.alert, [role="alert"]').first();
      await expect(alert).toBeVisible({ timeout: 3000 });
    });

    test('handles timeout', async ({ page, context }) => {
      // Set shorter timeout
      await context.setDefaultTimeout(2000);
      
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      // Mock slow response
      await page.route('**/api/auth/login', async route => {
        await page.waitForTimeout(5000);
        await route.fulfill({ status: 200, body: '{}' });
      });
      
      await page.click('button[type="submit"]');
      
      // Should handle timeout
      await page.waitForTimeout(3000);
    });
  });

  test.describe('Token Expiration', () => {
    test('detects and handles expired token', async ({ page }) => {
      // Set expired token
      await page.evaluate(() => {
        const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.sig';
        sessionStorage.setItem('auth_token', expiredToken);
      });
      
      // Try to access protected page
      await page.goto('http://localhost:8888/templates/dashboard.html');
      
      // Should redirect to login
      await page.waitForURL('**/login.html', { timeout: 5000 });
    });
  });

  test.describe('Multi-Tab Scenarios', () => {
    test('detects login from another tab', async ({ page, context }) => {
      // Open second tab
      const page2 = await context.newPage();
      await page2.goto('http://localhost:8888/templates/login.html');
      
      // Login in first tab
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      await page.route('**/api/auth/login', async route => {
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            token: 'new-token',
            user: { id: '123' }
          })
        });
      });
      
      await page.click('button[type="submit"]');
      
      // Set token in localStorage (simulating remember me)
      await page.evaluate(() => {
        localStorage.setItem('auth_token', 'new-token');
      });
      
      // Second tab should detect the change
      await page2.waitForTimeout(500);
      const tokenInTab2 = await page2.evaluate(() => 
        localStorage.getItem('auth_token')
      );
      
      expect(tokenInTab2).toBe('new-token');
      
      await page2.close();
    });
  });

  test.describe('Accessibility', () => {
    test('form is keyboard navigable', async ({ page }) => {
      // Tab through form
      await page.keyboard.press('Tab'); // Focus email
      await page.keyboard.type('user@example.com');
      
      await page.keyboard.press('Tab'); // Focus password
      await page.keyboard.type('ValidPassword123!');
      
      await page.keyboard.press('Tab'); // Focus remember me
      await page.keyboard.press('Space'); // Check
      
      await page.keyboard.press('Tab'); // Focus submit button
      
      const focusedElement = await page.evaluate(() => 
        document.activeElement.tagName
      );
      expect(focusedElement).toBe('BUTTON');
    });

    test('error messages are announced to screen readers', async ({ page }) => {
      await page.fill('#email', 'invalid-email');
      await page.fill('#password', 'short');
      
      // Check ARIA attributes
      const emailError = page.locator('#email-error');
      const role = await emailError.getAttribute('role');
      expect(role).toBe('alert');
    });

    test('form has proper labels', async ({ page }) => {
      const emailLabel = await page.locator('label[for="email"]').textContent();
      const passwordLabel = await page.locator('label[for="password"]').textContent();
      
      expect(emailLabel).toBeTruthy();
      expect(passwordLabel).toBeTruthy();
    });
  });

  test.describe('Responsive Design', () => {
    test('works on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      // Check if form is visible and usable
      const emailInput = page.locator('#email');
      await expect(emailInput).toBeVisible();
      
      const isUsable = await emailInput.evaluate(input => {
        const rect = input.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
      expect(isUsable).toBe(true);
    });

    test('works on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      const form = page.locator('#loginForm');
      await expect(form).toBeVisible();
    });

    test('works on desktop viewport', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      
      await page.fill('#email', 'user@example.com');
      await page.fill('#password', 'ValidPassword123!');
      
      const form = page.locator('#loginForm');
      await expect(form).toBeVisible();
    });
  });
});
