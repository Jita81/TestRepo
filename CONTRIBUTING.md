# Contributing to Todo List Application

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When creating a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, browser, Node version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**Include:**
- Clear description of the enhancement
- Use case and benefits
- Possible implementation approach
- Examples from other projects (if applicable)

### Pull Requests

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the coding style
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   npm test
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
   
   Follow conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions or changes
   - `chore:` Build process or auxiliary tool changes

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**

## Development Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up database**
   ```bash
   cp .env.example .env
   # Configure .env with your settings
   npm run db:migrate
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

## Coding Standards

### JavaScript

- Use ES6+ features
- Use `const` and `let`, not `var`
- Use async/await over promises when possible
- Add JSDoc comments for functions
- Use meaningful variable names
- Keep functions small and focused

### CSS

- Use CSS variables for theming
- Follow BEM naming convention when appropriate
- Mobile-first responsive design
- Use semantic class names

### Database

- Use parameterized queries
- Add indexes for frequently queried columns
- Include migration scripts for schema changes

## Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Test edge cases and error conditions
- Include both unit and integration tests

## Documentation

- Update README.md for user-facing changes
- Add JSDoc comments for new functions
- Update API documentation for endpoint changes
- Include code examples where helpful

## Questions?

Feel free to open an issue with the "question" label.

Thank you for contributing! 🎉