# Contributing to Calculator Component

Thank you for your interest in contributing! This document provides guidelines for contributing to the calculator component.

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Run tests:
   ```bash
   npm test
   ```

## Coding Standards

### TypeScript

- Use TypeScript for all new code
- Ensure strict type checking passes
- No `any` types unless absolutely necessary
- Document complex type definitions

### React

- Use functional components with hooks
- Follow React best practices
- Keep components small and focused
- Use custom hooks to separate logic from UI

### Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML
- Include proper ARIA labels
- Test with screen readers
- Support high contrast mode
- Support reduced motion preferences

### Testing

- Write tests for all new features
- Maintain 90%+ code coverage
- Include unit tests for utilities
- Include integration tests for components
- Test error cases
- Test accessibility features

### Code Style

- Use ESLint for linting
- Follow the existing code style
- Use meaningful variable names
- Write clear comments for complex logic
- Keep functions small and focused

## Pull Request Process

1. **Create a branch** from `main` for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add/update tests
   - Ensure all tests pass
   - Update documentation if needed

3. **Test your changes**
   ```bash
   npm test
   npm run lint
   npm run type-check
   ```

4. **Commit your changes**
   - Use clear, descriptive commit messages
   - Follow conventional commits format:
     - `feat:` for new features
     - `fix:` for bug fixes
     - `docs:` for documentation
     - `test:` for tests
     - `refactor:` for refactoring

5. **Submit a pull request**
   - Provide a clear description
   - Reference any related issues
   - Ensure CI passes

## Testing Guidelines

### Unit Tests

Test individual functions and utilities:

```typescript
describe('add', () => {
  test('adds two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

### Integration Tests

Test component behavior:

```typescript
test('calculates sum when clicking Calculate button', async () => {
  const user = userEvent.setup();
  render(<Calculator />);
  
  await user.type(screen.getByLabelText('First Number'), '5');
  await user.type(screen.getByLabelText('Second Number'), '3');
  await user.click(screen.getByRole('button', { name: /calculate/i }));
  
  expect(screen.getByRole('status')).toHaveTextContent('8');
});
```

### Accessibility Tests

Test accessibility features:

```typescript
test('marks inputs as invalid when there is an error', async () => {
  // Test implementation
});
```

## Accessibility Checklist

- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Focus indicators are visible
- [ ] ARIA labels are present and accurate
- [ ] Error messages use `role="alert"`
- [ ] Status updates use `role="status"`
- [ ] Color contrast meets WCAG AA standards
- [ ] Supports high contrast mode
- [ ] Respects reduced motion preferences

## Error Handling Checklist

- [ ] Invalid inputs are caught and handled
- [ ] Error messages are user-friendly
- [ ] Errors don't crash the application
- [ ] Edge cases are considered
- [ ] Error states are tested

## Documentation Checklist

- [ ] JSDoc comments for public APIs
- [ ] README updated if needed
- [ ] Examples provided for new features
- [ ] Type definitions documented

## Questions?

If you have questions about contributing, please open an issue for discussion.

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing!