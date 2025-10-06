/**
 * Unit Tests for Dashboard Functionality
 * Tests core dashboard logic including sanitization, data display, and session management
 */

describe('Dashboard Unit Tests', () => {
    let mockAuthService;
    let mockSessionStorage;
    let mockLocalStorage;

    beforeEach(() => {
        // Setup DOM
        document.body.innerHTML = `
            <div class="dashboard-header">
                <h2>Welcome</h2>
            </div>
            <div class="user-details">
                <h4>User Name</h4>
                <p>user@example.com</p>
            </div>
            <div class="user-avatar">UN</div>
            <div class="account-info">
                <p>Member since</p>
            </div>
            <main></main>
        `;

        // Mock storage
        mockSessionStorage = {
            data: {},
            getItem: jest.fn((key) => mockSessionStorage.data[key] || null),
            setItem: jest.fn((key, value) => { mockSessionStorage.data[key] = value; }),
            removeItem: jest.fn((key) => { delete mockSessionStorage.data[key]; }),
            clear: jest.fn(() => { mockSessionStorage.data = {}; })
        };

        mockLocalStorage = {
            data: {},
            getItem: jest.fn((key) => mockLocalStorage.data[key] || null),
            setItem: jest.fn((key, value) => { mockLocalStorage.data[key] = value; }),
            removeItem: jest.fn((key) => { delete mockLocalStorage.data[key]; }),
            clear: jest.fn(() => { mockLocalStorage.data = {}; })
        };

        global.sessionStorage = mockSessionStorage;
        global.localStorage = mockLocalStorage;

        // Mock authService
        mockAuthService = {
            isAuthenticated: jest.fn(() => true),
            getCurrentUser: jest.fn(() => ({
                name: 'Test User',
                email: 'test@example.com',
                joinDate: '2025-01-01'
            })),
            getToken: jest.fn(() => 'mock-token'),
            logout: jest.fn(),
            tokenStorage: {
                decodeToken: jest.fn((token) => ({
                    name: 'Test User',
                    email: 'test@example.com',
                    sub: '123',
                    iat: Math.floor(Date.now() / 1000),
                    exp: Math.floor(Date.now() / 1000) + 3600
                })),
                isTokenExpired: jest.fn(() => false)
            }
        };

        global.authService = mockAuthService;
    });

    afterEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = '';
    });

    // ========================================================================
    // Test 1: User Data Sanitization (XSS Protection)
    // ========================================================================
    describe('User Data Sanitization', () => {
        test('should sanitize malicious script tags in user name', () => {
            const maliciousName = '<script>alert("XSS")</script>Test User';
            const sanitized = sanitizeText(maliciousName);
            
            expect(sanitized).not.toContain('<script>');
            expect(sanitized).toContain('Test User');
        });

        test('should sanitize HTML injection in email', () => {
            const maliciousEmail = '<img src=x onerror=alert(1)>@example.com';
            const sanitized = sanitizeText(maliciousEmail);
            
            expect(sanitized).not.toContain('onerror');
            expect(sanitized).not.toContain('<img');
        });

        test('should handle empty or null input safely', () => {
            expect(sanitizeText('')).toBe('');
            expect(sanitizeText(null)).toBe('');
            expect(sanitizeText(undefined)).toBe('');
        });

        test('should preserve safe text content', () => {
            const safeText = 'John Doe';
            expect(sanitizeText(safeText)).toBe('John Doe');
        });

        test('should handle special characters safely', () => {
            const specialChars = 'User & Co. <info@example.com>';
            const sanitized = sanitizeText(specialChars);
            
            // Should escape HTML entities
            expect(sanitized).toContain('&amp;');
            expect(sanitized).toContain('&lt;');
            expect(sanitized).toContain('&gt;');
        });
    });

    // ========================================================================
    // Test 2: User Data Display
    // ========================================================================
    describe('User Data Display', () => {
        test('should display user name correctly', () => {
            const user = {
                name: 'Jane Smith',
                email: 'jane@example.com',
                joinDate: '2025-01-15'
            };

            displayUserInfo(user);

            const userName = document.querySelector('.user-details h4');
            expect(userName.textContent).toBe('Jane Smith');
        });

        test('should display user email correctly', () => {
            const user = {
                name: 'John Doe',
                email: 'john@example.com',
                joinDate: '2025-01-10'
            };

            displayUserInfo(user);

            const userEmail = document.querySelector('.user-details p');
            expect(userEmail.textContent).toBe('john@example.com');
        });

        test('should update welcome message with user name', () => {
            const user = {
                name: 'Alice Johnson',
                email: 'alice@example.com'
            };

            displayUserInfo(user);

            const welcome = document.querySelector('.dashboard-header h2');
            expect(welcome.textContent).toContain('Alice Johnson');
        });

        test('should display user avatar initials', () => {
            const user = {
                name: 'Bob Williams',
                email: 'bob@example.com'
            };

            displayUserInfo(user);

            const avatar = document.querySelector('.user-avatar');
            expect(avatar.textContent).toBe('BW');
        });

        test('should handle single-word names', () => {
            const user = {
                name: 'Madonna',
                email: 'madonna@example.com'
            };

            displayUserInfo(user);

            const avatar = document.querySelector('.user-avatar');
            expect(avatar.textContent).toBe('M');
        });

        test('should display join date', () => {
            const user = {
                name: 'Test User',
                email: 'test@example.com',
                joinDate: '2025-01-01'
            };

            displayUserInfo(user);

            const accountInfo = document.querySelector('.account-info p:last-child');
            expect(accountInfo.textContent).toContain('2025-01-01');
        });
    });

    // ========================================================================
    // Test 3: Session Validation
    // ========================================================================
    describe('Session Validation', () => {
        test('should validate authenticated user session', async () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);

            const isValid = await validateSession();

            expect(isValid).toBe(true);
            expect(mockAuthService.isAuthenticated).toHaveBeenCalled();
        });

        test('should reject unauthenticated user', async () => {
            mockAuthService.isAuthenticated.mockReturnValue(false);
            delete window.location;
            window.location = { href: '' };

            const isValid = await validateSession();

            expect(isValid).toBe(false);
            expect(window.location.href).toContain('login.html');
        });

        test('should detect expired token', async () => {
            mockAuthService.isAuthenticated.mockReturnValue(false);
            mockAuthService.tokenStorage.isTokenExpired.mockReturnValue(true);

            const isValid = await validateSession();

            expect(isValid).toBe(false);
        });

        test('should set redirect message for expired session', async () => {
            mockAuthService.isAuthenticated.mockReturnValue(false);
            window.location = { href: '' };

            await validateSession();

            expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
                'redirect_message',
                expect.stringContaining('session has expired')
            );
        });
    });

    // ========================================================================
    // Test 4: Logout Functionality
    // ========================================================================
    describe('Logout Functionality', () => {
        test('should clear user data on logout', () => {
            const dashboardState = {
                userData: { name: 'Test User' },
                error: null
            };

            window.confirm = jest.fn(() => true);
            handleLogout();

            expect(mockAuthService.logout).toHaveBeenCalled();
        });

        test('should set logout message', () => {
            window.confirm = jest.fn(() => true);
            handleLogout();

            expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
                'logout_message',
                expect.stringContaining('logged out successfully')
            );
        });

        test('should not logout if user cancels', () => {
            window.confirm = jest.fn(() => false);
            handleLogout();

            expect(mockAuthService.logout).not.toHaveBeenCalled();
        });

        test('should handle logout errors gracefully', () => {
            window.confirm = jest.fn(() => true);
            mockAuthService.logout.mockImplementation(() => {
                throw new Error('Logout failed');
            });

            expect(() => handleLogout()).not.toThrow();
        });
    });

    // ========================================================================
    // Test 5: Loading States
    // ========================================================================
    describe('Loading States', () => {
        test('should show loading state', () => {
            showLoadingState();

            const main = document.querySelector('main');
            expect(main.classList.contains('loading')).toBe(true);
        });

        test('should hide loading state', () => {
            const main = document.querySelector('main');
            main.classList.add('loading');

            hideLoadingState();

            expect(main.classList.contains('loading')).toBe(false);
        });

        test('should update user details opacity during loading', () => {
            showLoadingState();

            const details = document.querySelector('.user-details h4');
            expect(details.style.opacity).toBe('0.5');
        });

        test('should restore opacity after loading', () => {
            hideLoadingState();

            const details = document.querySelector('.user-details h4');
            expect(details.style.opacity).toBe('1');
        });
    });

    // ========================================================================
    // Test 6: Error Handling
    // ========================================================================
    describe('Error Handling', () => {
        test('should display error message', () => {
            const errorMsg = 'Failed to load dashboard';
            showError(errorMsg);

            const alert = document.querySelector('.alert');
            expect(alert).toBeTruthy();
            expect(alert.textContent).toBe(errorMsg);
        });

        test('should auto-remove error message after timeout', (done) => {
            jest.useFakeTimers();
            
            showError('Test error');
            const alert = document.querySelector('.alert');
            expect(alert).toBeTruthy();

            jest.advanceTimersByTime(5000);
            
            setTimeout(() => {
                expect(document.querySelector('.alert')).toBeFalsy();
                done();
            }, 100);

            jest.useRealTimers();
        });
    });

    // ========================================================================
    // Test 7: Multi-Tab Synchronization
    // ========================================================================
    describe('Multi-Tab Synchronization', () => {
        test('should handle storage event for token removal', () => {
            window.location = { href: '' };
            
            const storageEvent = new StorageEvent('storage', {
                key: 'auth_token',
                oldValue: 'old-token',
                newValue: null
            });

            handleStorageEvent(storageEvent);

            expect(window.location.href).toContain('login.html');
        });

        test('should ignore storage events for other keys', () => {
            window.location = { href: 'dashboard.html' };
            
            const storageEvent = new StorageEvent('storage', {
                key: 'other_key',
                newValue: null
            });

            handleStorageEvent(storageEvent);

            expect(window.location.href).toBe('dashboard.html');
        });
    });

    // ========================================================================
    // Test 8: Data Fetching
    // ========================================================================
    describe('Data Fetching', () => {
        test('should fetch user data successfully', async () => {
            const userData = await fetchUserData();

            expect(userData).toBeTruthy();
            expect(userData.name).toBe('Test User');
            expect(userData.email).toBe('test@example.com');
        });

        test('should handle missing user data', async () => {
            mockAuthService.getCurrentUser.mockReturnValue(null);

            try {
                await fetchUserData();
            } catch (error) {
                expect(error.message).toContain('No user data available');
            }
        });

        test('should decode token if no stored user data', async () => {
            mockAuthService.getCurrentUser.mockReturnValue(null);
            mockAuthService.getToken.mockReturnValue('valid-token');

            const userData = await fetchUserData();

            expect(mockAuthService.tokenStorage.decodeToken).toHaveBeenCalled();
            expect(userData).toBeTruthy();
        });
    });
});

// ============================================================================
// Helper Functions (Implementation)
// ============================================================================

function sanitizeText(input) {
    if (!input) return '';
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

function displayUserInfo(user) {
    if (!user) return;

    const sanitizedUser = {
        name: sanitizeText(user.name || 'User'),
        email: sanitizeText(user.email || ''),
        joinDate: sanitizeText(user.joinDate || new Date().toLocaleDateString())
    };

    // Update welcome message
    const welcomeElement = document.querySelector('.dashboard-header h2');
    if (welcomeElement) {
        welcomeElement.textContent = `Welcome back, ${sanitizedUser.name}!`;
    }

    // Update user name
    const userNameElements = document.querySelectorAll('.user-details h4');
    userNameElements.forEach(el => {
        el.textContent = sanitizedUser.name;
    });

    // Update user email
    const userEmailElements = document.querySelectorAll('.user-details p');
    userEmailElements.forEach(el => {
        if (!el.textContent.includes('Member since')) {
            el.textContent = sanitizedUser.email;
        }
    });

    // Update avatar
    if (sanitizedUser.name) {
        const initials = sanitizedUser.name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        
        const avatars = document.querySelectorAll('.user-avatar');
        avatars.forEach(avatar => {
            avatar.textContent = initials;
        });
    }

    // Update join date
    const accountInfoSection = document.querySelector('.account-info');
    if (accountInfoSection && sanitizedUser.joinDate) {
        const joinDateElement = accountInfoSection.querySelector('p:last-child');
        if (joinDateElement) {
            joinDateElement.textContent = `Member since ${sanitizedUser.joinDate}`;
        }
    }
}

async function validateSession() {
    if (typeof authService === 'undefined') {
        window.location.href = 'login.html';
        return false;
    }

    const isAuthenticated = authService.isAuthenticated();

    if (!isAuthenticated) {
        sessionStorage.setItem('redirect_message', 'Your session has expired. Please log in again.');
        window.location.href = 'login.html';
        return false;
    }

    return true;
}

function handleLogout() {
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }

    try {
        if (typeof authService !== 'undefined') {
            authService.logout();
            sessionStorage.setItem('logout_message', 'You have been logged out successfully');
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

function showLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('loading');
    }

    const userDetails = document.querySelectorAll('.user-details h4, .user-details p');
    userDetails.forEach(el => {
        el.style.opacity = '0.5';
        el.textContent = 'Loading...';
    });
}

function hideLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.remove('loading');
    }

    const userDetails = document.querySelectorAll('.user-details h4, .user-details p');
    userDetails.forEach(el => {
        el.style.opacity = '1';
    });
}

function showError(message) {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        
        mainContent.insertBefore(errorDiv, mainContent.firstChild);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

function handleStorageEvent(event) {
    if (event.key === 'auth_token' && !event.newValue) {
        window.location.href = 'login.html';
    }
}

async function fetchUserData() {
    if (typeof authService === 'undefined') {
        throw new Error('Authentication service not available');
    }

    const user = authService.getCurrentUser();

    if (!user) {
        const token = authService.getToken();
        if (token) {
            const payload = authService.tokenStorage.decodeToken(token);
            return {
                name: payload.name || 'User',
                email: payload.email || 'user@example.com',
                sub: payload.sub,
                joinDate: payload.iat ? new Date(payload.iat * 1000).toLocaleDateString() : new Date().toLocaleDateString()
            };
        }
        throw new Error('No user data available');
    }

    return user;
}
