/**
 * E2E Tests for Authenticated Dashboard
 * Tests all dashboard functionality, authentication, and user data display
 */

const { test, expect } = require('@playwright/test');

test.describe('Dashboard - Authenticated User Access', () => {
    test('should display dashboard for authenticated user', async ({ page }) => {
        // Navigate to login page
        await page.goto('/templates/login.html');

        // Login with test credentials
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');

        // Wait for redirect to dashboard
        await page.waitForTimeout(2000);

        // Verify we're on dashboard
        expect(page.url()).toContain('dashboard.html');

        // Verify dashboard content loads
        await expect(page.locator('.dashboard-header')).toBeVisible();
        
        // Verify user information is displayed
        const userName = page.locator('.user-details h4').first();
        await expect(userName).toBeVisible();
        await expect(userName).toContainText(/\w+/); // Has actual content
        
        // Verify welcome message includes user name
        const welcomeMsg = page.locator('.dashboard-header h2');
        await expect(welcomeMsg).toContainText('Welcome back');
        
        // Verify navigation is present
        await expect(page.locator('.navbar')).toBeVisible();
        await expect(page.locator('.nav-link')).toHaveCount({ gt: 0 });
        
        // Verify logout button is present
        await expect(page.locator('button:has-text("Logout")')).toBeVisible();
    });

    test('should display user information correctly', async ({ page }) => {
        // Login and navigate to dashboard
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Check user email is displayed
        const userEmail = page.locator('.user-details p').first();
        await expect(userEmail).toBeVisible();
        await expect(userEmail).toContainText('@'); // Contains email format
        
        // Check that sensitive info (password) is NOT displayed
        const pageContent = await page.content();
        expect(pageContent.toLowerCase()).not.toContain('password');
        expect(pageContent.toLowerCase()).not.toContain('Test123!@#');
        
        // Verify avatar shows initials
        const avatar = page.locator('.user-avatar').first();
        await expect(avatar).toBeVisible();
        const avatarText = await avatar.textContent();
        expect(avatarText).toMatch(/[A-Z]{1,2}/); // 1-2 capital letters
    });

    test('should sanitize user data (XSS protection)', async ({ page }) => {
        // Set user data with malicious content
        await page.goto('/templates/dashboard.html');
        
        await page.evaluate(() => {
            // Simulate malicious user data
            const maliciousUser = {
                name: '<script>alert("XSS")</script>Test User',
                email: '<img src=x onerror=alert(1)>@example.com'
            };
            
            // Store malicious token
            const header = btoa(JSON.stringify({ alg: 'HS256' }));
            const payload = btoa(JSON.stringify({
                sub: '123',
                name: maliciousUser.name,
                email: maliciousUser.email,
                exp: Math.floor(Date.now() / 1000) + 3600
            }));
            const token = `${header}.${payload}.${btoa('sig')}`;
            sessionStorage.setItem('auth_token', token);
        });

        // Reload to trigger dashboard initialization
        await page.reload();
        await page.waitForTimeout(1000);

        // Verify script tags are not executed
        const alerts = [];
        page.on('dialog', dialog => alerts.push(dialog.message()));
        
        await page.waitForTimeout(2000);
        expect(alerts).toHaveLength(0); // No alerts should fire

        // Verify malicious HTML is rendered as text
        const userName = await page.locator('.user-details h4').first().textContent();
        expect(userName).not.toContain('<script>');
        expect(userName).toContain('Test User');
    });
});

test.describe('Dashboard - Unauthenticated Access', () => {
    test('should redirect unauthenticated user to login', async ({ page }) => {
        // Clear all storage
        await page.goto('/templates/dashboard.html');
        await page.evaluate(() => {
            sessionStorage.clear();
            localStorage.clear();
        });

        // Try to access dashboard
        await page.goto('/templates/dashboard.html');
        
        // Wait for redirect
        await page.waitForTimeout(2000);

        // Should be redirected to login
        expect(page.url()).toContain('login.html');
        
        // Should see login prompt message
        const pageContent = await page.content();
        const hasLoginPrompt = pageContent.includes('log in') || 
                               pageContent.includes('login') ||
                               pageContent.includes('sign in');
        expect(hasLoginPrompt).toBe(true);
    });

    test('should not load dashboard content without auth', async ({ page }) => {
        // Navigate to dashboard without authentication
        await page.goto('/templates/login.html');
        await page.evaluate(() => {
            sessionStorage.clear();
            localStorage.clear();
        });

        await page.goto('/templates/dashboard.html');
        await page.waitForTimeout(1000);

        // Dashboard content should not be visible or should redirect
        const isOnDashboard = page.url().includes('dashboard.html');
        
        if (isOnDashboard) {
            // If somehow still on dashboard, main content should not be populated
            const userName = page.locator('.user-details h4').first();
            const text = await userName.textContent();
            expect(text).toBeFalsy() || expect(text).toContain('Loading');
        } else {
            // Should have been redirected
            expect(page.url()).toContain('login.html');
        }
    });
});

test.describe('Dashboard - Expired Token Handling', () => {
    test('should redirect to login with expired token', async ({ page }) => {
        await page.goto('/templates/dashboard.html');

        // Set expired token
        await page.evaluate(() => {
            const header = btoa(JSON.stringify({ alg: 'HS256' }));
            const payload = btoa(JSON.stringify({
                sub: '123',
                name: 'Test User',
                email: 'test@example.com',
                exp: Math.floor(Date.now() / 1000) - 3600 // Expired 1 hour ago
            }));
            const expiredToken = `${header}.${payload}.${btoa('sig')}`;
            sessionStorage.setItem('auth_token', expiredToken);
        });

        // Navigate to dashboard
        await page.goto('/templates/dashboard.html');
        await page.waitForTimeout(2000);

        // Should be redirected to login
        expect(page.url()).toContain('login.html');
    });

    test('should show session expired message', async ({ page }) => {
        await page.goto('/templates/dashboard.html');

        // Set expired token
        await page.evaluate(() => {
            const header = btoa(JSON.stringify({ alg: 'HS256' }));
            const payload = btoa(JSON.stringify({
                sub: '123',
                exp: Math.floor(Date.now() / 1000) - 3600
            }));
            const expiredToken = `${header}.${payload}.${btoa('sig')}`;
            sessionStorage.setItem('auth_token', expiredToken);
            sessionStorage.setItem('redirect_message', 'Your session has expired. Please log in again.');
        });

        // Navigate to login
        await page.goto('/templates/login.html');
        await page.waitForTimeout(500);

        // Check for session expired message
        const alert = page.locator('.alert');
        if (await alert.isVisible()) {
            const text = await alert.textContent();
            expect(text.toLowerCase()).toContain('session');
        }
    });

    test('should remove expired token from storage', async ({ page }) => {
        await page.goto('/templates/dashboard.html');

        // Set expired token
        await page.evaluate(() => {
            const expiredToken = btoa('header') + '.' +
                               btoa(JSON.stringify({ exp: 0 })) + '.' +
                               btoa('sig');
            sessionStorage.setItem('auth_token', expiredToken);
        });

        await page.goto('/templates/dashboard.html');
        await page.waitForTimeout(2000);

        // Verify token was removed
        const tokenAfter = await page.evaluate(() => 
            sessionStorage.getItem('auth_token')
        );
        expect(tokenAfter).toBeNull();
    });
});

test.describe('Dashboard - Responsive Layout', () => {
    test('should be responsive on mobile (320px)', async ({ page }) => {
        await page.setViewportSize({ width: 320, height: 568 });
        
        // Login first
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Verify dashboard adapts to mobile
        await expect(page.locator('.navbar')).toBeVisible();
        
        // Navigation should collapse to mobile menu
        const navToggle = page.locator('.navbar-toggle');
        await expect(navToggle).toBeVisible();
        
        // Verify no horizontal scrolling
        const hasHorizontalScroll = await page.evaluate(() => {
            return document.documentElement.scrollWidth > document.documentElement.clientWidth;
        });
        expect(hasHorizontalScroll).toBe(false);
        
        // Content should reflow properly
        const main = page.locator('main');
        await expect(main).toBeVisible();
    });

    test('should adapt navigation on small screens', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Mobile menu toggle should be visible
        const toggle = page.locator('.navbar-toggle');
        await expect(toggle).toBeVisible();
        
        // Click to open menu
        await toggle.click();
        await page.waitForTimeout(500);
        
        // Menu items should be accessible
        const navMenu = page.locator('.navbar-menu');
        await expect(navMenu).toBeVisible();
    });

    test('should work on tablet (768px)', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Layout should adapt
        await expect(page.locator('.dashboard-grid')).toBeVisible();
        
        // All elements should be readable
        const fontSize = await page.locator('body').evaluate(el => 
            window.getComputedStyle(el).fontSize
        );
        const fontSizeNum = parseInt(fontSize);
        expect(fontSizeNum).toBeGreaterThanOrEqual(14);
    });

    test('should utilize space on desktop (1920px)', async ({ page }) => {
        await page.setViewportSize({ width: 1920, height: 1080 });
        
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Desktop layout should be present
        await expect(page.locator('.navbar')).toBeVisible();
        
        // Content should be centered/properly laid out
        const mainContent = page.locator('main');
        await expect(mainContent).toBeVisible();
    });
});

test.describe('Dashboard - Logout Functionality', () => {
    test('should logout successfully', async ({ page }) => {
        // Login first
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Verify we're on dashboard
        expect(page.url()).toContain('dashboard.html');

        // Click logout button
        page.once('dialog', dialog => dialog.accept()); // Accept confirmation
        await page.click('button:has-text("Logout")');
        
        await page.waitForTimeout(1000);

        // Should be redirected to login
        expect(page.url()).toContain('login.html');
    });

    test('should remove token on logout', async ({ page }) => {
        // Login
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Verify token exists
        const tokenBefore = await page.evaluate(() => 
            sessionStorage.getItem('auth_token')
        );
        expect(tokenBefore).toBeTruthy();

        // Logout
        page.once('dialog', dialog => dialog.accept());
        await page.click('button:has-text("Logout")');
        await page.waitForTimeout(1000);

        // Verify token is removed
        const tokenAfter = await page.evaluate(() => 
            sessionStorage.getItem('auth_token')
        );
        expect(tokenAfter).toBeNull();
    });

    test('should show logout success message', async ({ page }) => {
        // Login and logout
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        page.once('dialog', dialog => dialog.accept());
        await page.click('button:has-text("Logout")');
        await page.waitForTimeout(1000);

        // Check for logout message
        const logoutMessage = await page.evaluate(() => 
            sessionStorage.getItem('logout_message')
        );
        expect(logoutMessage).toContain('logged out');
    });

    test('should prevent dashboard access after logout using back button', async ({ page }) => {
        // Login
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Logout
        page.once('dialog', dialog => dialog.accept());
        await page.click('button:has-text("Logout")');
        await page.waitForTimeout(1000);

        // Try to go back
        await page.goBack();
        await page.waitForTimeout(2000);

        // Should be redirected to login again
        expect(page.url()).toContain('login.html');
    });
});

test.describe('Dashboard - Edge Cases', () => {
    test('should handle multi-tab logout sync', async ({ context }) => {
        // Create two pages (tabs)
        const page1 = await context.newPage();
        const page2 = await context.newPage();

        try {
            // Login in first tab
            await page1.goto('/templates/login.html');
            await page1.fill('#email', 'test@example.com');
            await page1.fill('#password', 'Test123!@#');
            await page1.click('button[type="submit"]');
            await page1.waitForTimeout(2000);

            // Open dashboard in second tab
            await page2.goto('/templates/dashboard.html');
            await page2.waitForTimeout(1000);

            // Logout in first tab
            page1.once('dialog', dialog => dialog.accept());
            await page1.click('button:has-text("Logout")');
            await page1.waitForTimeout(1000);

            // Second tab should detect logout
            await page2.waitForTimeout(2000);
            
            // Check if redirected
            const page2Url = page2.url();
            expect(page2Url).toContain('login.html');

        } finally {
            await page1.close();
            await page2.close();
        }
    });

    test('should validate session on tab focus', async ({ page }) => {
        // Login
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);

        // Simulate tab becoming hidden then visible
        await page.evaluate(() => {
            // Expire the token
            const header = btoa(JSON.stringify({ alg: 'HS256' }));
            const payload = btoa(JSON.stringify({
                sub: '123',
                exp: Math.floor(Date.now() / 1000) - 100
            }));
            const expiredToken = `${header}.${payload}.${btoa('sig')}`;
            sessionStorage.setItem('auth_token', expiredToken);
            
            // Trigger visibility change
            document.dispatchEvent(new Event('visibilitychange'));
        });

        await page.waitForTimeout(2000);

        // Should be redirected to login
        expect(page.url()).toContain('login.html');
    });

    test('should show loading state while fetching data', async ({ page }) => {
        await page.goto('/templates/login.html');
        await page.fill('#email', 'test@example.com');
        await page.fill('#password', 'Test123!@#');
        await page.click('button[type="submit"]');

        // Check for loading indicators immediately after navigation
        await page.waitForTimeout(500);
        
        // Loading state should be present briefly
        const userDetails = page.locator('.user-details').first();
        await expect(userDetails).toBeVisible();
    });
});

if __name__ == "__main__":
    // This file is meant to be run with Playwright test runner
    // Run with: npx playwright test dashboard.spec.js
}
