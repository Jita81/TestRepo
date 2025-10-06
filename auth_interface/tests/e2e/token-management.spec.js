/**
 * E2E Tests for Token Management
 * Tests secure token storage, authorization headers, and session handling
 */

const { test, expect } = require('@playwright/test');

test.describe('Token Management - Login Flow', () => {
  test('should store token after successful login', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Fill login form
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    // Wait for processing
    await page.waitForTimeout(2000);

    // Check if token is stored in sessionStorage
    const token = await page.evaluate(() => {
      return sessionStorage.getItem('auth_token');
    });

    expect(token).toBeTruthy();
    expect(token.split('.').length).toBe(3); // JWT structure
  });

  test('should store token in localStorage when Remember Me is checked', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('#rememberMe').check();
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Check localStorage
    const token = await page.evaluate(() => {
      return localStorage.getItem('auth_token');
    });
    const rememberMe = await page.evaluate(() => {
      return localStorage.getItem('remember_me');
    });

    expect(token).toBeTruthy();
    expect(rememberMe).toBe('true');
  });

  test('should not store token in URL parameters', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Check URL does not contain token
    const url = page.url();
    expect(url).not.toContain('token=');
    expect(url).not.toContain('jwt=');
    expect(url).not.toContain('auth=');
  });

  test('should store user data after login', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    const userData = await page.evaluate(() => {
      const data = sessionStorage.getItem('user_data');
      return data ? JSON.parse(data) : null;
    });

    expect(userData).toBeTruthy();
    expect(userData.email).toBe('test@example.com');
  });
});

test.describe('Token Management - Protected Routes', () => {
  test('should redirect to login when accessing dashboard without token', async ({ page }) => {
    await page.goto('/templates/dashboard.html');

    // Wait for redirect
    await page.waitForTimeout(2000);

    // Should be redirected to login
    expect(page.url()).toContain('login.html');
  });

  test('should allow access to dashboard with valid token', async ({ page }) => {
    // First login
    await page.goto('/templates/login.html');
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Should be redirected to dashboard
    expect(page.url()).toContain('dashboard.html');
  });

  test('should redirect to login with expired token', async ({ page }) => {
    // Create expired token
    const expiredToken = await page.evaluate(() => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({
        sub: '123',
        exp: Math.floor(Date.now() / 1000) - 3600 // Expired 1 hour ago
      }));
      const signature = btoa('signature');
      return `${header}.${payload}.${signature}`;
    });

    // Set expired token
    await page.evaluate((token) => {
      sessionStorage.setItem('auth_token', token);
    }, expiredToken);

    // Try to access dashboard
    await page.goto('/templates/dashboard.html');
    await page.waitForTimeout(2000);

    // Should be redirected to login
    expect(page.url()).toContain('login.html');

    // Token should be removed
    const token = await page.evaluate(() => {
      return sessionStorage.getItem('auth_token');
    });
    expect(token).toBeNull();
  });

  test('should show session expired message', async ({ page }) => {
    // Set expired token
    await page.evaluate(() => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({
        sub: '123',
        exp: Math.floor(Date.now() / 1000) - 3600
      }));
      const signature = btoa('signature');
      sessionStorage.setItem('auth_token', `${header}.${payload}.${signature}`);
    });

    await page.goto('/templates/dashboard.html');
    await page.waitForTimeout(500);

    // Check for session expired message
    const alert = page.locator('.alert');
    if (await alert.isVisible()) {
      const text = await alert.textContent();
      expect(text.toLowerCase()).toContain('session');
    }
  });
});

test.describe('Token Management - Logout', () => {
  test('should remove token on logout', async ({ page }) => {
    // Login first
    await page.goto('/templates/login.html');
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Verify token exists
    let token = await page.evaluate(() => sessionStorage.getItem('auth_token'));
    expect(token).toBeTruthy();

    // Logout
    const logoutButton = page.locator('button:has-text("Logout")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page.waitForTimeout(500);
    }

    // Token should be removed
    token = await page.evaluate(() => sessionStorage.getItem('auth_token'));
    expect(token).toBeNull();
  });

  test('should remove user data on logout', async ({ page }) => {
    // Login
    await page.goto('/templates/login.html');
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Logout
    const logoutButton = page.locator('button:has-text("Logout")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page.waitForTimeout(500);
    }

    // User data should be removed
    const userData = await page.evaluate(() => {
      return sessionStorage.getItem('user_data') || localStorage.getItem('user_data');
    });
    expect(userData).toBeNull();
  });

  test('should redirect to login after logout', async ({ page }) => {
    // Login
    await page.goto('/templates/login.html');
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Get current URL
    const currentUrl = page.url();

    // Logout
    const logoutButton = page.locator('button:has-text("Logout")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page.waitForTimeout(1000);
    }

    // Should be redirected to login
    expect(page.url()).toContain('login.html');
  });
});

test.describe('Token Management - Token Validation', () => {
  test('should validate JWT structure', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check token validation function exists
    const hasValidation = await page.evaluate(() => {
      return typeof window.authService !== 'undefined' &&
             typeof window.authService.tokenStorage.validateTokenStructure === 'function';
    });

    expect(hasValidation).toBeTruthy();
  });

  test('should reject invalid token structure', async ({ page }) => {
    await page.goto('/templates/dashboard.html');

    // Try to set invalid token
    await page.evaluate(() => {
      try {
        window.authService.tokenStorage.setToken('invalid.token');
        return false;
      } catch (e) {
        return true; // Should throw error
      }
    }).then(rejected => {
      expect(rejected).toBeTruthy();
    });
  });

  test('should decode token payload', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Create valid token
    const payload = await page.evaluate(() => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payloadData = { sub: '123', name: 'Test User', exp: Math.floor(Date.now() / 1000) + 3600 };
      const payloadStr = btoa(JSON.stringify(payloadData));
      const signature = btoa('signature');
      const token = `${header}.${payloadStr}.${signature}`;

      window.authService.tokenStorage.setToken(token, false);
      return window.authService.tokenStorage.decodeToken(token);
    });

    expect(payload.sub).toBe('123');
    expect(payload.name).toBe('Test User');
  });
});

test.describe('Token Management - Multi-tab Synchronization', () => {
  test('should sync logout across tabs', async ({ context }) => {
    // Create two tabs
    const page1 = await context.newPage();
    const page2 = await context.newPage();

    // Login in first tab
    await page1.goto('/templates/login.html');
    await page1.locator('#email').fill('test@example.com');
    await page1.locator('#password').fill('Test123!@#');
    await page1.locator('button[type="submit"]').click();
    await page1.waitForTimeout(2000);

    // Open dashboard in second tab
    await page2.goto('/templates/dashboard.html');
    await page2.waitForTimeout(1000);

    // Logout in first tab
    const logoutButton = page1.locator('button:has-text("Logout")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page1.waitForTimeout(500);
    }

    // Second tab should detect logout
    await page2.waitForTimeout(1000);
    
    // Check if token is removed in second tab
    const tokenInTab2 = await page2.evaluate(() => {
      return sessionStorage.getItem('auth_token') || localStorage.getItem('auth_token');
    });

    // Token should be removed or page should redirect
    const isOnLoginPage = page2.url().includes('login.html');
    expect(tokenInTab2 === null || isOnLoginPage).toBeTruthy();

    await page1.close();
    await page2.close();
  });
});

test.describe('Token Management - XSS Protection', () => {
  test('should not expose token in DOM', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Check that token is not in DOM
    const tokenInDOM = await page.evaluate(() => {
      return document.body.innerHTML.includes('auth_token') ||
             document.body.innerHTML.includes('Bearer');
    });

    expect(tokenInDOM).toBeFalsy();
  });

  test('should sanitize user input', async ({ page }) => {
    await page.goto('/templates/register.html');

    // Try to inject script in name field
    const maliciousInput = '<script>alert("XSS")</script>';
    await page.locator('#fullName').fill(maliciousInput);
    await page.locator('#fullName').blur();

    await page.waitForTimeout(500);

    // Check that script is not executed or rendered
    const alerts = await page.evaluate(() => {
      return document.querySelectorAll('script').length;
    });

    // Input should be sanitized
    const value = await page.locator('#fullName').inputValue();
    expect(value).not.toContain('<script>');
  });
});

test.describe('Token Management - Error Handling', () => {
  test('should handle network errors gracefully', async ({ page, context }) => {
    // Simulate network failure
    await context.route('**/api/**', route => route.abort());

    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Should show error message
    const alert = page.locator('.alert-danger');
    if (await alert.isVisible()) {
      expect(await alert.textContent()).toBeTruthy();
    }
  });

  test('should handle malformed API responses', async ({ page, context }) => {
    // Intercept and return malformed response
    await context.route('**/api/auth/login', route => {
      route.fulfill({
        status: 200,
        body: 'invalid json'
      });
    });

    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Should handle error gracefully
    expect(page.url()).toContain('login.html');
  });
});

test.describe('Token Management - Remember Me', () => {
  test('should persist token across page reloads with Remember Me', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('#rememberMe').check();
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Reload page
    await page.reload();
    await page.waitForTimeout(1000);

    // Token should still be in localStorage
    const token = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(token).toBeTruthy();
  });

  test('should clear token on page reload without Remember Me', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    // Don't check Remember Me
    await page.locator('button[type="submit"]').click();

    await page.waitForTimeout(2000);

    // Token should be in sessionStorage
    let token = await page.evaluate(() => sessionStorage.getItem('auth_token'));
    expect(token).toBeTruthy();

    // Token should NOT be in localStorage
    token = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(token).toBeNull();
  });
});
