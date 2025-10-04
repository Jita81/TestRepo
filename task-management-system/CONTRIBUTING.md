# Contributing to Task Management System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Report unacceptable behavior

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots if applicable

### Suggesting Features

1. **Open a feature request issue**
2. **Describe the feature** clearly:
   - Problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**:
   - Follow code style guidelines
   - Add tests
   - Update documentation
   - Ensure all tests pass

4. **Commit your changes**:
   ```bash
   git commit -m "Add: amazing feature"
   ```
   
   Use conventional commits:
   - `Add:` - New feature
   - `Fix:` - Bug fix
   - `Update:` - Improvements
   - `Docs:` - Documentation
   - `Test:` - Testing
   - `Refactor:` - Code refactoring

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**:
   - Clear title and description
   - Link related issues
   - Add screenshots/videos if UI changes
   - Request review from maintainers

## Development Setup

### Prerequisites

- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Git

### Setup Steps

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/task-management-system.git
   cd task-management-system
   ```

2. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   npm install

   # Frontend
   cd ../frontend
   npm install
   ```

3. **Set up database**:
   ```bash
   createdb task_management_dev
   psql -d task_management_dev -f database/schema.sql
   ```

4. **Configure environment**:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

5. **Start development servers**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   npm run dev

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Code Style

### Backend (Node.js)

- Use ES6+ features
- Async/await over callbacks
- Descriptive variable names
- JSDoc comments for functions
- Error handling in all async operations

Example:
```javascript
/**
 * Get user by ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User object
 */
async function getUserById(userId) {
  try {
    const user = await User.findById(userId);
    return user;
  } catch (error) {
    logger.error('Failed to get user:', error);
    throw error;
  }
}
```

### Frontend (React)

- Functional components with hooks
- PropTypes for type checking
- Descriptive component names
- Extract reusable logic into custom hooks
- Keep components small and focused

Example:
```jsx
/**
 * Task card component
 */
function TaskCard({ task, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);

  const handleUpdate = async (updates) => {
    try {
      await onUpdate(task.id, updates);
      setIsEditing(false);
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

  return (
    <div className="task-card">
      {/* Component JSX */}
    </div>
  );
}
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
npm test

# Run specific test
npm test -- auth.test.js

# Watch mode
npm run test:watch

# Coverage
npm test -- --coverage
```

### Writing Tests

```javascript
describe('Task API', () => {
  let authToken;

  beforeEach(async () => {
    // Setup
  });

  afterEach(async () => {
    // Cleanup
  });

  it('should create a new task', async () => {
    const response = await request(app)
      .post('/api/tasks')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ title: 'Test Task' });

    expect(response.statusCode).toBe(201);
    expect(response.body.success).toBe(true);
  });
});
```

## Documentation

- Update README.md for feature changes
- Update API.md for API changes
- Add JSDoc comments for functions
- Include examples in documentation
- Keep deployment guide current

## Git Workflow

1. **Keep your fork updated**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL/task-management-system.git
   git fetch upstream
   git merge upstream/main
   ```

2. **Create feature branches from main**
3. **One feature per pull request**
4. **Rebase before merging** to keep history clean

## Review Process

1. **Automated checks** must pass:
   - Linting
   - Tests
   - Build

2. **Code review** by maintainer:
   - Code quality
   - Test coverage
   - Documentation
   - Best practices

3. **Address feedback** promptly

4. **Merge** after approval

## Release Process

1. Version bump following semver
2. Update CHANGELOG.md
3. Tag release
4. Deploy to production
5. Announce release

## Getting Help

- **Discord**: Join our community server
- **GitHub Discussions**: Ask questions
- **Issues**: Report bugs
- **Email**: maintainer@example.com

## Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Added to contributors page

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
