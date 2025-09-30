# Contributing to Greeting API

Thank you for your interest in contributing to the Greeting API! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn
- Git

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/greeting-api.git
   cd greeting-api
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
5. Run tests to ensure everything is working:
   ```bash
   npm test
   ```

## Development Workflow

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the coding standards

3. **Write tests** for your changes

4. **Run tests** to ensure everything passes:
   ```bash
   npm test
   ```

5. **Run the application** locally to verify:
   ```bash
   npm run dev
   ```

6. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of your feature"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** with a clear description of your changes

## Coding Standards

### JavaScript Style Guide

- Use ES6+ features where appropriate
- Use `const` by default, `let` when reassignment is needed
- Never use `var`
- Use arrow functions for anonymous functions
- Use template literals for string interpolation
- Use destructuring when appropriate

### Formatting

We use Prettier for code formatting. Configuration is in `.prettierrc`:

```bash
npm run format  # (if formatter script is added)
```

### Linting

We use ESLint for code linting. Configuration is in `.eslintrc.js`:

```bash
npm run lint  # (if lint script is added)
```

### File Structure

```
src/
├── config/         # Configuration files
├── middleware/     # Express middleware
├── routes/         # Route handlers
├── services/       # Business logic
└── utils/          # Utility functions and constants
```

### Naming Conventions

- **Files**: camelCase (e.g., `greetingService.js`)
- **Classes**: PascalCase (e.g., `GreetingService`)
- **Functions/Variables**: camelCase (e.g., `getGreeting`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_NAME_LENGTH`)

### Comments

- Use JSDoc comments for functions and classes
- Include parameter types and return types
- Add inline comments for complex logic

Example:
```javascript
/**
 * Get a greeting message
 * 
 * @param {string} lang - Language code (default: 'en')
 * @param {string} name - Optional name for personalized greeting
 * @returns {Object} Greeting object with message property
 * @throws {Error} If language is not supported
 */
getGreeting(lang = 'en', name = '') {
  // Implementation
}
```

## Testing

### Test Requirements

- All new features must include unit tests
- All new API endpoints must include integration tests
- Maintain or improve code coverage (minimum 80%)
- Tests must pass before submitting a PR

### Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm test -- --coverage
```

### Writing Tests

#### Unit Tests

Place unit tests in `tests/unit/` directory:

```javascript
describe('FeatureName', () => {
  describe('methodName', () => {
    it('should do something specific', () => {
      // Arrange
      const input = 'test';
      
      // Act
      const result = someFunction(input);
      
      // Assert
      expect(result).toBe('expected');
    });
  });
});
```

#### Integration Tests

Place integration tests in `tests/integration/` directory:

```javascript
describe('API Endpoint', () => {
  it('should return expected response', async () => {
    const response = await request(app)
      .get('/api/endpoint')
      .query({ param: 'value' });
    
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ expected: 'data' });
  });
});
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if you've changed APIs or added features
2. **Update the README.md** if needed
3. **Ensure all tests pass** and coverage is maintained
4. **Update CHANGELOG.md** (if exists) with your changes
5. **Fill out the PR template** with a clear description
6. **Request review** from maintainers

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How have these changes been tested?

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No linter warnings
```

## Reporting Bugs

### Before Submitting

- Check if the bug has already been reported
- Verify the bug exists in the latest version
- Collect relevant information

### Bug Report Template

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Node.js version:
- OS:
- API version:

## Additional Context
Any other relevant information
```

## Feature Requests

We welcome feature requests! Please provide:

1. **Use case**: Why is this feature needed?
2. **Description**: What should the feature do?
3. **Examples**: How would it be used?
4. **Alternatives**: What alternatives have you considered?

## Adding New Languages

To add support for a new language:

1. Update `src/utils/constants.js`:
   ```javascript
   const SUPPORTED_LANGUAGES = {
     en: { default: 'Hello!', withName: 'Hello, {name}!' },
     es: { default: '¡Hola!', withName: '¡Hola, {name}!' },
     fr: { default: 'Bonjour!', withName: 'Bonjour, {name}!' },
     de: { default: 'Hallo!', withName: 'Hallo, {name}!' } // New language
   };
   ```

2. Add tests in `tests/unit/greetingService.test.js`
3. Add tests in `tests/integration/greeting.test.js`
4. Update documentation in `README.md` and `docs/swagger.yaml`
5. Update the language list in `docs/API_EXAMPLES.md`

## Questions?

If you have questions, please:
- Open an issue with the "question" label
- Reach out to maintainers
- Check existing documentation

## Recognition

Contributors will be recognized in the project. Thank you for helping make this project better!

---

**Happy Contributing! 🎉**