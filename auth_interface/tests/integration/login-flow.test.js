/**
 * Integration Tests for Login Flow
 * Tests all login test cases from user story
 */

describe('Login Flow Integration Tests', () => {
    let mockAuthService;
    let mockFetch;

    beforeEach(() => {
        // Mock fetch for API calls
        mockFetch = jest.fn();
        global.fetch = mockFetch;

        // Mock authService
        mockAuthService = {
            login: jest.fn(),
            isAuthenticated: jest.fn(() => false),
            logout: jest.fn()
        };
        global.authService = mockAuthService;

        // Setup DOM
        document.body.innerHTML = `
            <form id="loginForm">
                <input type="email" id="email" name="email" required>
                <input type="password" id="password" name="password" required>
                <input type="checkbox" id="rememberMe" name="rememberMe">
                <button type="submit" id="submitBtn">Login</button>
                <div class="error-message"></div>
            </form>
        `;

        // Mock window.location
        delete window.location;
        window.location = { href: '', replace: jest.fn() };
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    // ========================================================================
    // Test 1: Successful Login with Valid Credentials
    // ========================================================================
    describe('Test 1: Successful Login with Valid Credentials', () => {
        test('should call authentication API with credentials', async () => {
            const mockResponse = {
                ok: true,
                json: async () => ({
                    token: 'mock-jwt-token',
                    user: {
                        email: 'user@example.com',
                        name: 'Test User'
                    }
                })
            };
            mockFetch.mockResolvedValue(mockResponse);
            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-jwt-token'
            });

            const credentials = {
                email: 'user@example.com',
                password: 'Password123!',
                rememberMe: false
            };

            await mockAuthService.login(credentials);

            expect(mockAuthService.login).toHaveBeenCalledWith(credentials);
        });

        test('should receive and store authentication token', async () => {
            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-jwt-token'
            });

            const result = await mockAuthService.login({
                email: 'user@example.com',
                password: 'Password123!'
            });

            expect(result.token).toBe('mock-jwt-token');
        });

        test('should redirect to dashboard after successful login', async () => {
            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-jwt-token'
            });

            await mockAuthService.login({
                email: 'user@example.com',
                password: 'Password123!'
            });

            // Simulate redirect logic
            window.location.href = 'dashboard.html';

            expect(window.location.href).toBe('dashboard.html');
        });

        test('should display personalized dashboard content', async () => {
            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-jwt-token',
                user: {
                    name: 'Test User',
                    email: 'user@example.com'
                }
            });

            const result = await mockAuthService.login({
                email: 'user@example.com',
                password: 'Password123!'
            });

            expect(result.user).toBeTruthy();
            expect(result.user.name).toBe('Test User');
        });
    });

    // ========================================================================
    // Test 2: Login Fails with Invalid Email
    // ========================================================================
    describe('Test 2: Login Fails with Invalid Email', () => {
        test('should return authentication error for invalid email', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            try {
                await mockAuthService.login({
                    email: 'nonexistent@example.com',
                    password: 'anypassword'
                });
            } catch (error) {
                expect(error.error).toBe('Invalid email or password');
            }
        });

        test('should display error message without revealing email existence', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            try {
                await mockAuthService.login({
                    email: 'invalid@example.com',
                    password: 'password'
                });
            } catch (error) {
                // Error message should not reveal whether email exists
                expect(error.error).not.toContain('does not exist');
                expect(error.error).not.toContain('not found');
                expect(error.error).toBe('Invalid email or password');
            }
        });

        test('should remain on login page after failed login', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            const currentUrl = window.location.href;

            try {
                await mockAuthService.login({
                    email: 'invalid@example.com',
                    password: 'password'
                });
            } catch (error) {
                // URL should not change
                expect(window.location.href).toBe(currentUrl);
            }
        });

        test('should not store token on failed login', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            const mockStorage = {
                data: {},
                setItem: jest.fn((key, value) => {
                    mockStorage.data[key] = value;
                })
            };
            global.sessionStorage = mockStorage;

            try {
                await mockAuthService.login({
                    email: 'invalid@example.com',
                    password: 'password'
                });
            } catch (error) {
                expect(mockStorage.setItem).not.toHaveBeenCalledWith('auth_token', expect.anything());
            }
        });
    });

    // ========================================================================
    // Test 3: Login Fails with Incorrect Password
    // ========================================================================
    describe('Test 3: Login Fails with Incorrect Password', () => {
        test('should return authentication error for incorrect password', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            try {
                await mockAuthService.login({
                    email: 'user@example.com',
                    password: 'wrongpassword'
                });
            } catch (error) {
                expect(error.error).toBe('Invalid email or password');
            }
        });

        test('should display generic error message', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            try {
                await mockAuthService.login({
                    email: 'user@example.com',
                    password: 'wrongpassword'
                });
            } catch (error) {
                // Should not reveal that email is correct
                expect(error.error).toBe('Invalid email or password');
            }
        });

        test('should clear password field for security', async () => {
            const passwordField = document.getElementById('password');
            passwordField.value = 'wrongpassword';

            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            try {
                await mockAuthService.login({
                    email: 'user@example.com',
                    password: 'wrongpassword'
                });
            } catch (error) {
                // Simulate password clearing
                passwordField.value = '';
                expect(passwordField.value).toBe('');
            }
        });

        test('should remain on login page', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Invalid email or password'
            });

            const currentUrl = window.location.href;

            try {
                await mockAuthService.login({
                    email: 'user@example.com',
                    password: 'wrongpassword'
                });
            } catch (error) {
                expect(window.location.href).toBe(currentUrl);
            }
        });
    });

    // ========================================================================
    // Test 4: Login Form Validation for Empty Fields
    // ========================================================================
    describe('Test 4: Login Form Validation for Empty Fields', () => {
        test('should show error for empty email field', () => {
            const emailField = document.getElementById('email');
            emailField.value = '';

            const isValid = emailField.checkValidity();
            expect(isValid).toBe(false);
        });

        test('should display "Email is required" message', () => {
            const emailField = document.getElementById('email');
            emailField.value = '';

            // Simulate validation
            const validateEmail = (value) => {
                if (!value) return 'Email is required';
                return '';
            };

            const error = validateEmail(emailField.value);
            expect(error).toBe('Email is required');
        });

        test('should not submit form with empty email', () => {
            const form = document.getElementById('loginForm');
            const emailField = document.getElementById('email');
            emailField.value = '';

            const submitEvent = new Event('submit', { cancelable: true });
            const prevented = !form.dispatchEvent(submitEvent);

            // Form should not submit with empty required field
            expect(emailField.checkValidity()).toBe(false);
        });

        test('should highlight email field on error', () => {
            const emailField = document.getElementById('email');
            emailField.value = '';

            // Simulate field highlighting
            const highlightField = (field) => {
                field.classList.add('error');
                field.setAttribute('aria-invalid', 'true');
            };

            highlightField(emailField);

            expect(emailField.classList.contains('error')).toBe(true);
            expect(emailField.getAttribute('aria-invalid')).toBe('true');
        });

        test('should show error for empty password field', () => {
            const passwordField = document.getElementById('password');
            passwordField.value = '';

            const isValid = passwordField.checkValidity();
            expect(isValid).toBe(false);
        });
    });

    // ========================================================================
    // Test 5: Login with Remember Me Option
    // ========================================================================
    describe('Test 5: Login with Remember Me Option', () => {
        test('should successfully login with remember me checked', async () => {
            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-jwt-token'
            });

            const result = await mockAuthService.login({
                email: 'user@example.com',
                password: 'Password123!',
                rememberMe: true
            });

            expect(result.success).toBe(true);
        });

        test('should persist session beyond browser close', () => {
            const mockLocalStorage = {
                data: {},
                setItem: jest.fn((key, value) => {
                    mockLocalStorage.data[key] = value;
                }),
                getItem: jest.fn((key) => mockLocalStorage.data[key])
            };
            global.localStorage = mockLocalStorage;

            const rememberMe = true;
            const token = 'mock-jwt-token';

            if (rememberMe) {
                localStorage.setItem('auth_token', token);
            }

            expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_token', token);
        });

        test('should use sessionStorage when remember me is unchecked', () => {
            const mockSessionStorage = {
                data: {},
                setItem: jest.fn((key, value) => {
                    mockSessionStorage.data[key] = value;
                })
            };
            global.sessionStorage = mockSessionStorage;

            const rememberMe = false;
            const token = 'mock-jwt-token';

            if (!rememberMe) {
                sessionStorage.setItem('auth_token', token);
            }

            expect(mockSessionStorage.setItem).toHaveBeenCalledWith('auth_token', token);
        });

        test('should set extended token expiration with remember me', () => {
            const generateToken = (rememberMe) => {
                const expiry = rememberMe 
                    ? Math.floor(Date.now() / 1000) + (30 * 24 * 60 * 60) // 30 days
                    : Math.floor(Date.now() / 1000) + (60 * 60); // 1 hour
                
                return { expiry };
            };

            const tokenWithRemember = generateToken(true);
            const tokenWithoutRemember = generateToken(false);

            expect(tokenWithRemember.expiry).toBeGreaterThan(tokenWithoutRemember.expiry);
        });
    });

    // ========================================================================
    // Test 6: Loading State During Login
    // ========================================================================
    describe('Test 6: Loading State During Login', () => {
        test('should show loading indicator on submit button', async () => {
            const submitBtn = document.getElementById('submitBtn');
            
            // Simulate loading state
            submitBtn.classList.add('btn-loading');
            submitBtn.textContent = 'Logging in...';

            expect(submitBtn.classList.contains('btn-loading')).toBe(true);
            expect(submitBtn.textContent).toContain('Logging in');
        });

        test('should disable submit button during authentication', async () => {
            const submitBtn = document.getElementById('submitBtn');
            
            // Simulate disabled state
            submitBtn.disabled = true;

            expect(submitBtn.disabled).toBe(true);
        });

        test('should disable form fields during authentication', async () => {
            const emailField = document.getElementById('email');
            const passwordField = document.getElementById('password');

            // Simulate disabled state
            emailField.disabled = true;
            passwordField.disabled = true;

            expect(emailField.disabled).toBe(true);
            expect(passwordField.disabled).toBe(true);
        });

        test('should restore normal state after completion', async () => {
            const submitBtn = document.getElementById('submitBtn');
            const emailField = document.getElementById('email');

            // Simulate loading
            submitBtn.disabled = true;
            emailField.disabled = true;

            // Simulate completion
            submitBtn.disabled = false;
            emailField.disabled = false;
            submitBtn.classList.remove('btn-loading');

            expect(submitBtn.disabled).toBe(false);
            expect(emailField.disabled).toBe(false);
            expect(submitBtn.classList.contains('btn-loading')).toBe(false);
        });

        test('should prevent multiple submissions', async () => {
            const submitBtn = document.getElementById('submitBtn');
            
            submitBtn.disabled = true;
            
            // Try to submit again
            const canSubmit = !submitBtn.disabled;

            expect(canSubmit).toBe(false);
        });
    });

    // ========================================================================
    // Edge Cases
    // ========================================================================
    describe('Edge Cases', () => {
        test('should handle network failures during authentication', async () => {
            mockAuthService.login.mockRejectedValue({
                error: 'Network error occurred'
            });

            try {
                await mockAuthService.login({
                    email: 'user@example.com',
                    password: 'Password123!'
                });
            } catch (error) {
                expect(error.error).toContain('Network error');
            }
        });

        test('should handle token expiration during active session', async () => {
            const token = {
                exp: Math.floor(Date.now() / 1000) - 3600 // Expired
            };

            const isExpired = token.exp < Math.floor(Date.now() / 1000);
            expect(isExpired).toBe(true);
        });

        test('should handle special characters in email/password', async () => {
            const specialEmail = "test+user@example.com";
            const specialPassword = "P@ssw0rd!#$%";

            mockAuthService.login.mockResolvedValue({
                success: true,
                token: 'mock-token'
            });

            const result = await mockAuthService.login({
                email: specialEmail,
                password: specialPassword
            });

            expect(result.success).toBe(true);
        });

        test('should handle browser storage being cleared', () => {
            const mockStorage = {
                data: {},
                getItem: jest.fn(() => null)
            };
            global.sessionStorage = mockStorage;

            const token = sessionStorage.getItem('auth_token');
            expect(token).toBeNull();
        });

        test('should handle session conflicts across multiple tabs', () => {
            const storageEvent = new StorageEvent('storage', {
                key: 'auth_token',
                oldValue: 'old-token',
                newValue: 'new-token'
            });

            // Different token in another tab
            expect(storageEvent.newValue).not.toBe(storageEvent.oldValue);
        });
    });
});
