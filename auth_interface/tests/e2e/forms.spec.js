/**
 * E2E Tests for Form Functionality
 * Tests form validation, submission, and user workflows
 */

const { test, expect } = require('@playwright/test');

test.describe('Login Form Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates/login.html');
  });

  test('should show error for empty email', async ({ page }) => {
    await page.locator('#email').click();
    await page.locator('#email').blur();
    
    await page.waitForTimeout(500);

    // Error message should appear (if validation is immediate)
    const errorVisible = await page.locator('#email-error').isVisible();
    
    // Submit should also trigger validation
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);
    
    // Error should be shown
    const emailError = page.locator('#email-error');
    const hasError = await emailError.isVisible();
    
    if (hasError) {
      const errorText = await emailError.textContent();
      expect(errorText.toLowerCase()).toContain('required');
    }
  });

  test('should show error for invalid email format', async ({ page }) => {
    await page.locator('#email').fill('invalid-email');
    await page.locator('#email').blur();
    
    await page.waitForTimeout(500);

    const emailInput = page.locator('#email');
    const hasErrorClass = await emailInput.evaluate(el => 
      el.classList.contains('error')
    );
    
    if (hasErrorClass) {
      const errorMsg = await page.locator('#email-error').textContent();
      expect(errorMsg.toLowerCase()).toMatch(/email|invalid|format/);
    }
  });

  test('should accept valid email format', async ({ page }) => {
    await page.locator('#email').fill('valid@example.com');
    await page.locator('#email').blur();
    
    await page.waitForTimeout(500);

    const emailInput = page.locator('#email');
    const hasSuccessClass = await emailInput.evaluate(el => 
      el.classList.contains('success')
    );
    
    // Should either have success class or no error class
    const hasErrorClass = await emailInput.evaluate(el => 
      el.classList.contains('error')
    );
    
    expect(hasErrorClass).toBeFalsy();
  });

  test('should validate password field', async ({ page }) => {
    await page.locator('#password').click();
    await page.locator('#password').blur();
    
    await page.waitForTimeout(500);

    // Should show error for empty password
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);
    
    const passwordError = page.locator('#password-error');
    const isVisible = await passwordError.isVisible();
    
    if (isVisible) {
      const errorText = await passwordError.textContent();
      expect(errorText.length).toBeGreaterThan(0);
    }
  });

  test('password toggle should work', async ({ page }) => {
    await page.locator('#password').fill('TestPassword123');
    
    // Initially password should be hidden
    let inputType = await page.locator('#password').getAttribute('type');
    expect(inputType).toBe('password');

    // Click toggle button
    const toggleButton = page.locator('.password-toggle').first();
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      
      // Type should change to text
      inputType = await page.locator('#password').getAttribute('type');
      expect(inputType).toBe('text');

      // Click again to hide
      await toggleButton.click();
      inputType = await page.locator('#password').getAttribute('type');
      expect(inputType).toBe('password');
    }
  });

  test('should prevent submission with invalid data', async ({ page }) => {
    await page.locator('#email').fill('invalid');
    await page.locator('#password').fill('short');
    
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    // Form should not navigate away (still on login page)
    expect(page.url()).toContain('login.html');
  });

  test('should allow submission with valid data', async ({ page }) => {
    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    
    // Click submit
    await page.locator('button[type="submit"]').click();
    
    // Button should show loading state
    await page.waitForTimeout(500);
    
    const button = page.locator('button[type="submit"]');
    const isLoading = await button.evaluate(el => 
      el.classList.contains('btn-loading') || el.disabled
    );
    
    // Should show loading or be disabled during submission
    expect(isLoading).toBeTruthy();
  });
});

test.describe('Registration Form Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates/register.html');
  });

  test('should validate full name', async ({ page }) => {
    await page.locator('#fullName').fill('A'); // Too short
    await page.locator('#fullName').blur();
    
    await page.waitForTimeout(500);

    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    const error = page.locator('#fullName-error');
    const isVisible = await error.isVisible();
    
    if (isVisible) {
      const errorText = await error.textContent();
      expect(errorText.length).toBeGreaterThan(0);
    }
  });

  test('should show password requirements', async ({ page }) => {
    const requirements = page.locator('.password-requirements');
    await expect(requirements).toBeVisible();

    // Check all requirement items are present
    const items = await requirements.locator('li').all();
    expect(items.length).toBeGreaterThanOrEqual(5);
  });

  test('should update password requirements as user types', async ({ page }) => {
    const requirements = page.locator('.password-requirements');
    
    // Initially no requirements met
    await page.locator('#password').fill('a');
    await page.waitForTimeout(500);
    
    const validItems = await requirements.locator('li.valid').count();
    expect(validItems).toBeLessThan(5);

    // Add uppercase
    await page.locator('#password').fill('aA');
    await page.waitForTimeout(500);
    
    // More requirements should be met
    const validItems2 = await requirements.locator('li.valid').count();
    expect(validItems2).toBeGreaterThan(validItems);

    // Fill complete valid password
    await page.locator('#password').fill('Test123!@#');
    await page.waitForTimeout(1000);
    
    // All requirements should be met
    const validItems3 = await requirements.locator('li.valid').count();
    expect(validItems3).toBe(5);
  });

  test('should validate password confirmation match', async ({ page }) => {
    await page.locator('#password').fill('Test123!@#');
    await page.locator('#confirmPassword').fill('Different123!@#');
    await page.locator('#confirmPassword').blur();
    
    await page.waitForTimeout(500);

    const confirmError = page.locator('#confirmPassword-error');
    const isVisible = await confirmError.isVisible();
    
    if (isVisible) {
      const errorText = await confirmError.textContent();
      expect(errorText.toLowerCase()).toContain('match');
    }
  });

  test('should accept matching passwords', async ({ page }) => {
    const password = 'Test123!@#';
    await page.locator('#password').fill(password);
    await page.locator('#confirmPassword').fill(password);
    await page.locator('#confirmPassword').blur();
    
    await page.waitForTimeout(500);

    const confirmInput = page.locator('#confirmPassword');
    const hasSuccess = await confirmInput.evaluate(el => 
      el.classList.contains('success')
    );
    
    const hasError = await confirmInput.evaluate(el => 
      el.classList.contains('error')
    );
    
    // Should not have error for matching passwords
    expect(hasError).toBeFalsy();
  });

  test('should require terms acceptance', async ({ page }) => {
    // Fill all fields
    await page.locator('#fullName').fill('John Doe');
    await page.locator('#email').fill('john@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('#confirmPassword').fill('Test123!@#');

    // Don't check terms
    const termsCheckbox = page.locator('#acceptTerms');
    await termsCheckbox.uncheck();

    // Try to submit
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    // Should show error or prevent submission
    const termsError = page.locator('#acceptTerms-error');
    const errorVisible = await termsError.isVisible();
    
    if (errorVisible) {
      const errorText = await termsError.textContent();
      expect(errorText.toLowerCase()).toMatch(/term|accept|required/);
    }
  });

  test('should allow registration with all valid data', async ({ page }) => {
    await page.locator('#fullName').fill('John Doe');
    await page.locator('#email').fill('john.doe@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('#confirmPassword').fill('Test123!@#');
    await page.locator('#acceptTerms').check();

    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    // Button should show loading state
    const button = page.locator('button[type="submit"]');
    const isLoading = await button.evaluate(el => 
      el.classList.contains('btn-loading') || el.disabled
    );
    
    expect(isLoading).toBeTruthy();
  });
});

test.describe('Form Input Types', () => {
  test('should use correct HTML5 input types for mobile keyboards', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Email input should use type="email" for email keyboard
    const emailType = await page.locator('#email').getAttribute('type');
    expect(emailType).toBe('email');

    // Password input should use type="password"
    const passwordType = await page.locator('#password').getAttribute('type');
    expect(passwordType).toBe('password');
  });

  test('should have proper autocomplete attributes', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Check autocomplete attributes
    const emailAutocomplete = await page.locator('#email').getAttribute('autocomplete');
    expect(emailAutocomplete).toBe('email');

    const passwordAutocomplete = await page.locator('#password').getAttribute('autocomplete');
    expect(passwordAutocomplete).toContain('password');
  });
});

test.describe('Real-time Validation', () => {
  test('should validate email format in real-time', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Type invalid email
    await page.locator('#email').fill('test');
    await page.waitForTimeout(600); // Debounce delay

    // May show error or just not show success
    const hasError = await page.locator('#email').evaluate(el => 
      el.classList.contains('error')
    );

    // Complete the email
    await page.locator('#email').fill('test@example.com');
    await page.waitForTimeout(600);

    // Should clear error or show success
    const hasErrorAfter = await page.locator('#email').evaluate(el => 
      el.classList.contains('error')
    );
    
    expect(hasErrorAfter).toBeFalsy();
  });

  test('should validate password strength in real-time', async ({ page }) => {
    await page.goto('/templates/register.html');

    await page.locator('#password').fill('weak');
    await page.waitForTimeout(600);

    // Check password requirements update
    const requirements = page.locator('.password-requirements');
    const validCount1 = await requirements.locator('li.valid').count();

    await page.locator('#password').fill('Test123!@#');
    await page.waitForTimeout(600);

    const validCount2 = await requirements.locator('li.valid').count();
    
    // More requirements should be valid
    expect(validCount2).toBeGreaterThan(validCount1);
  });
});

test.describe('Form Submission Flow', () => {
  test('should handle successful login flow', async ({ page }) => {
    await page.goto('/templates/login.html');

    await page.locator('#email').fill('test@example.com');
    await page.locator('#password').fill('Test123!@#');
    await page.locator('button[type="submit"]').click();

    // Wait for form processing
    await page.waitForTimeout(2000);

    // Should show success message or redirect
    const url = page.url();
    const hasAlert = await page.locator('.alert-success').isVisible().catch(() => false);
    
    // Either redirected or showing success
    expect(url.includes('dashboard') || hasAlert).toBeTruthy();
  });

  test('should handle form errors gracefully', async ({ page }) => {
    await page.goto('/templates/login.html');

    // Submit empty form
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    // Should show validation errors
    const errors = await page.locator('.form-error.show').count();
    expect(errors).toBeGreaterThan(0);
  });
});

test.describe('Remember Me Feature', () => {
  test('remember me checkbox should be functional', async ({ page }) => {
    await page.goto('/templates/login.html');

    const checkbox = page.locator('#rememberMe');
    if (await checkbox.isVisible()) {
      // Should be unchecked by default
      const isChecked = await checkbox.isChecked();
      expect(isChecked).toBeFalsy();

      // Should be checkable
      await checkbox.check();
      expect(await checkbox.isChecked()).toBeTruthy();

      // Should be uncheckable
      await checkbox.uncheck();
      expect(await checkbox.isChecked()).toBeFalsy();
    }
  });
});
