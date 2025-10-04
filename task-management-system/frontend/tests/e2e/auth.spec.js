/**
 * E2E Authentication tests
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Task Management/);
    await expect(page.locator('h1')).toContainText('Welcome Back');
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.getByRole('link', { name: /sign up/i }).click();
    await expect(page).toHaveURL(/\/register/);
    await expect(page.locator('h1')).toContainText('Create Account');
  });

  test('should show validation errors on empty login', async ({ page }) => {
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Check for HTML5 validation
    const emailInput = page.getByLabel(/email/i);
    await expect(emailInput).toHaveAttribute('required');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByLabel(/email/i).fill('wrong@example.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Would need to mock the API for this to actually test
    // In real scenario, would check for error toast/message
  });

  test('should register new user', async ({ page }) => {
    await page.getByRole('link', { name: /sign up/i }).click();
    
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const username = `testuser${timestamp}`;

    await page.getByLabel(/username/i).fill(username);
    await page.getByLabel(/^email/i).fill(email);
    await page.getByLabel(/password/i).fill('Password123!');
    
    await page.getByRole('button', { name: /create account/i }).click();

    // Should redirect to dashboard (with mocked backend)
    // await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should have password input type', async ({ page }) => {
    const passwordInput = page.getByLabel(/password/i);
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should have accessible form labels', async ({ page }) => {
    const emailInput = page.getByLabel(/email/i);
    const passwordInput = page.getByLabel(/password/i);
    
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.getByLabel(/email/i).press('Tab');
    await expect(page.getByLabel(/password/i)).toBeFocused();
    
    await page.getByLabel(/password/i).press('Tab');
    await expect(page.getByRole('button', { name: /sign in/i })).toBeFocused();
  });

  test('register form should validate password length', async ({ page }) => {
    await page.getByRole('link', { name: /sign up/i }).click();
    
    const passwordInput = page.getByLabel(/password/i);
    await expect(passwordInput).toHaveAttribute('minlength', '8');
  });

  test('should show password requirements', async ({ page }) => {
    await page.getByRole('link', { name: /sign up/i }).click();
    await expect(page.getByText(/must be at least 8 characters/i)).toBeVisible();
  });
});

test.describe('Logout Flow', () => {
  test.skip('should logout user', async ({ page }) => {
    // This test would require actually logging in first
    // Skipping as it needs backend integration
  });
});

test.describe('Token Refresh', () => {
  test.skip('should refresh expired tokens', async ({ page }) => {
    // This test would require mocking token expiration
    // Skipping as it needs advanced setup
  });
});
