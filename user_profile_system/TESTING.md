# Testing Documentation

## Overview

This document describes the testing strategy and implementation for the User Profile System.

## Testing Philosophy

- **Test Coverage**: Aim for >80% code coverage
- **Test Types**: Unit, Integration, and E2E tests
- **Test-Driven**: Write tests before or alongside feature code
- **Continuous Testing**: Run tests on every commit
- **Quality Over Quantity**: Focus on meaningful tests

## Backend Testing

### Tech Stack
- **Framework**: pytest
- **HTTP Client**: TestClient (FastAPI)
- **Coverage**: pytest-cov
- **Async**: pytest-asyncio

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_api.py              # API endpoint tests
├── test_services.py         # Service layer tests
└── test_security.py         # Security utility tests
```

### Running Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_register_user -v
```

### Test Categories

#### 1. API Tests (`test_api.py`)

**Authentication Tests:**
- User registration success
- Duplicate email rejection
- User login success
- Invalid credentials handling

**Profile Management Tests:**
- Get user profile (authenticated)
- Get user profile (unauthorized)
- Update profile success
- Update profile with invalid data
- Update profile unauthorized access
- Profile picture upload
- Invalid file type rejection

**Example:**
```python
def test_register_user(client, test_user_data):
    response = client.post("/api/register", json=test_user_data)
    assert response.status_code == 201
    assert "access_token" in response.json()
```

#### 2. Service Tests (`test_services.py`)

**UserService Tests:**
- Create user
- Get user by ID
- Get user by email
- Update profile
- Authorization checks

**Example:**
```python
def test_create_user(db_session):
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    user = service.create_user(user_data)
    assert user.id is not None
    assert user.name == "Test User"
```

#### 3. Security Tests (`test_security.py`)

**Password Security:**
- Password hashing
- Password verification

**JWT Tokens:**
- Token creation
- Token decoding

**Sanitization:**
- HTML sanitization
- Input sanitization

**Example:**
```python
def test_password_hashing():
    password = "TestPassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) == True
```

### Fixtures

**Database Fixture:**
```python
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

**Authenticated Client:**
```python
@pytest.fixture
def authenticated_client(client, test_user_data):
    response = client.post("/api/register", json=test_user_data)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client, token
```

## Frontend Testing

### Tech Stack
- **Framework**: Vitest
- **Component Testing**: React Testing Library
- **User Simulation**: @testing-library/user-event
- **DOM Assertions**: @testing-library/jest-dom

### Test Structure

```
frontend/src/tests/
├── setup.ts                 # Test configuration
├── validation.test.ts       # Validation utility tests
├── sanitize.test.ts         # Sanitization utility tests
└── ProfilePage.test.tsx     # Component tests
```

### Running Frontend Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test -- --watch

# Run specific test file
npm run test validation.test.ts
```

### Test Categories

#### 1. Utility Tests

**Validation Tests (`validation.test.ts`):**
- Name validation (valid, empty, too short, too long, invalid characters)
- Email validation (valid, empty, invalid format)
- Image validation (valid types, invalid types, size limits)
- Form validation (valid data, invalid data)

**Example:**
```typescript
describe('validateName', () => {
  it('should accept valid names', () => {
    expect(validateName('John Doe')).toBeNull();
  });

  it('should reject empty names', () => {
    expect(validateName('')).toBe('Name is required');
  });
});
```

**Sanitization Tests (`sanitize.test.ts`):**
- HTML sanitization (script removal, safe tags)
- Text sanitization (tag removal)
- HTML escaping

**Example:**
```typescript
describe('sanitizeHTML', () => {
  it('should remove script tags', () => {
    const dirty = '<script>alert("XSS")</script><p>Hello</p>';
    const clean = sanitizeHTML(dirty);
    expect(clean).not.toContain('<script>');
    expect(clean).toContain('<p>Hello</p>');
  });
});
```

#### 2. Component Tests

**ProfilePage Tests (`ProfilePage.test.tsx`):**
- Loading state display
- Profile data rendering
- Edit button visibility (own profile)
- Edit button hidden (other profiles)
- Error handling
- Modal opening

**Example:**
```typescript
describe('ProfilePage', () => {
  it('should render profile data after loading', async () => {
    vi.mocked(apiClient.getUserProfile).mockResolvedValue(mockProfile);
    
    render(<ProfilePage userId="user123" isOwnProfile={true} />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });
});
```

### Mocking

**API Mocking:**
```typescript
vi.mock('../utils/api', () => ({
  apiClient: {
    getUserProfile: vi.fn(),
    updateProfile: vi.fn(),
    uploadProfilePicture: vi.fn(),
  },
}));
```

**Toast Mocking:**
```typescript
vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
  ToastContainer: () => null,
}));
```

## Test Coverage Goals

### Backend Coverage Targets
- Overall: >85%
- API Routes: >90%
- Services: >90%
- Security Utils: >95%
- Models/Schemas: >80%

### Frontend Coverage Targets
- Overall: >80%
- Components: >85%
- Utils: >90%
- Types: N/A (TypeScript provides type safety)

## Integration Testing

Integration tests verify that multiple components work together correctly.

**Example Integration Test:**
```python
def test_full_profile_update_flow(client, test_user_data):
    # Register
    response = client.post("/api/register", json=test_user_data)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    
    # Get profile
    profile = client.get("/api/users/me/profile").json()
    
    # Update profile
    update_data = {"name": "Updated Name"}
    client.put(f"/api/users/{profile['id']}/profile", json=update_data)
    
    # Verify update
    updated = client.get("/api/users/me/profile").json()
    assert updated["name"] == "Updated Name"
```

## E2E Testing (Recommended)

While not implemented in the current version, E2E testing with Playwright or Cypress is recommended for production.

**Recommended E2E Tests:**
1. User registration flow
2. Login and profile viewing
3. Profile editing and saving
4. Image upload
5. Form validation errors
6. Network error handling
7. Session timeout handling

**Example E2E Test (Playwright):**
```typescript
test('user can update profile', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name=email]', 'test@example.com');
  await page.fill('[name=password]', 'TestPass123');
  await page.click('button[type=submit]');
  
  await page.click('text=Edit Profile');
  await page.fill('[name=name]', 'New Name');
  await page.click('text=Save Changes');
  
  await expect(page.locator('text=New Name')).toBeVisible();
});
```

## Test Best Practices

### 1. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange - Set up test data
    user_data = {"name": "Test", "email": "test@example.com"}
    
    # Act - Perform action
    result = some_function(user_data)
    
    # Assert - Verify result
    assert result is not None
```

### 2. Descriptive Test Names
```python
# Good
def test_register_user_with_duplicate_email_returns_400():
    ...

# Bad
def test_user():
    ...
```

### 3. One Assertion Per Test (when possible)
```python
# Good - focused test
def test_user_name_is_set():
    assert user.name == "Test User"

def test_user_email_is_set():
    assert user.email == "test@example.com"

# Acceptable - related assertions
def test_user_profile_fields():
    assert user.name == "Test User"
    assert user.email == "test@example.com"
```

### 4. Use Fixtures for Reusable Data
```python
@pytest.fixture
def test_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123"
    }
```

### 5. Mock External Dependencies
```python
# Mock API calls
@patch('app.services.user_service.external_api_call')
def test_with_mock(mock_api):
    mock_api.return_value = {"status": "success"}
    result = function_that_calls_api()
    assert result is not None
```

### 6. Test Edge Cases
- Empty inputs
- Null values
- Very long inputs
- Special characters
- Concurrent operations
- Network failures

### 7. Keep Tests Fast
- Use in-memory databases
- Mock slow operations
- Run heavy tests separately
- Parallelize when possible

## Continuous Integration

**GitHub Actions Example:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run test:coverage
```

## Test Maintenance

- **Regular Updates**: Update tests when features change
- **Refactor Tests**: Keep tests DRY (Don't Repeat Yourself)
- **Remove Obsolete Tests**: Delete tests for removed features
- **Review Coverage**: Regularly check and improve coverage
- **Fix Flaky Tests**: Immediately fix unreliable tests

## Debugging Tests

```bash
# Backend - verbose output
pytest tests/ -v -s

# Backend - print output
pytest tests/ --capture=no

# Backend - debugger
pytest tests/ --pdb

# Frontend - UI mode
npm run test -- --ui

# Frontend - debug specific test
npm run test -- --reporter=verbose validation.test.ts
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)