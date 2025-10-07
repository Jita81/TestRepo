# Testing Guide - Quick Start

Quick reference for testing the GitHub to App Converter.

## Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies including test tools
pip install -r requirements.txt

# Or install development dependencies (recommended)
pip install -r requirements-dev.txt
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests (fast)
pytest -m unit

# Run smoke tests (quickest)
pytest -m smoke
```

### 3. View Coverage Report

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open in browser
# Linux:   xdg-open htmlcov/index.html
# Mac:     open htmlcov/index.html
# Windows: start htmlcov/index.html
```

## Common Commands

```bash
# Run specific test file
pytest tests/test_readme_parser.py

# Run with verbose output
pytest -v

# Run without API/network tests
pytest -m "not requires_api and not requires_network"

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run in parallel (faster)
pytest -n auto
```

## Test Structure

```
tests/
├── test_readme_parser.py       # ReadmeParser unit tests
├── test_github_integration.py  # GitHubRepository unit tests
├── test_agentic_coder.py       # AgenticCoder unit tests
├── test_app_generator.py       # AppGenerator unit tests
├── test_integration.py         # Integration & E2E tests
├── test_utils.py               # Test utilities
└── conftest.py                 # Fixtures and configuration
```

## Test Coverage

Current test coverage includes:

- ✅ **ReadmeParser**: Complete unit test coverage
  - README parsing and extraction
  - Project type detection
  - Dependency extraction
  - Error handling

- ✅ **GitHubRepository**: Complete unit test coverage
  - URL parsing
  - Repository cloning
  - Metadata fetching
  - File operations

- ✅ **AgenticCoder**: Complete unit test coverage
  - Project structure analysis
  - AI-powered code analysis
  - Entry point detection
  - Mock API interactions

- ✅ **AppGenerator**: Complete unit test coverage
  - Executable generation
  - Docker container generation
  - Web application generation
  - Platform-specific wrappers

- ✅ **Integration Tests**: End-to-end workflows
  - FastAPI endpoints
  - Complete conversion pipeline
  - Component integration
  - Error handling

## Test Markers

Mark tests for selective execution:

```python
@pytest.mark.unit          # Fast, isolated tests
@pytest.mark.integration   # Component interaction tests
@pytest.mark.slow          # Long-running tests
@pytest.mark.requires_api  # Needs API keys
@pytest.mark.requires_network  # Needs internet
@pytest.mark.smoke         # Quick validation
```

Run specific markers:

```bash
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
pytest -m "not slow"     # Skip slow tests
```

## Fixtures

Common fixtures available in all tests:

- `temp_dir` - Temporary directory (auto-cleanup)
- `sample_repo_dir` - Sample repository structure
- `readme_parser` - ReadmeParser instance
- `github_repo` - GitHubRepository instance
- `agentic_coder` - AgenticCoder instance
- `app_generator` - AppGenerator instance
- `test_client` - FastAPI test client
- `mock_openai_response` - Mock AI response
- `mock_github_api_response` - Mock GitHub API

## Writing Tests

### Basic Test Template

```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Tests for my feature."""
    
    def test_success_case(self, fixture):
        """Test successful operation."""
        # Arrange
        input_data = "test"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function_that_should_fail()
```

### Async Test Template

```python
@pytest.mark.asyncio
async def test_async_function(fixture):
    """Test async function."""
    result = await async_function()
    assert result is not None
```

## Continuous Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Manual workflow dispatch

CI excludes tests marked with:
- `requires_api` (no API keys in CI)
- `requires_network` (may be flaky)
- `slow` (time constraints)

## Troubleshooting

### Tests Not Found

```bash
# Make sure you're in project root
cd /workspace
pytest
```

### Import Errors

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Coverage Too Low

```bash
# See which lines are missing coverage
pytest --cov=src --cov-report=term-missing
```

### Tests Hang

```bash
# Add timeout
pytest --timeout=10
```

## Code Quality

Run code quality checks:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type check
mypy src

# Security check
bandit -r src
```

## Coverage Goals

- **Minimum**: 70% overall coverage (enforced)
- **Target**: 80%+ coverage
- **Critical paths**: 90%+ coverage

Current coverage: Check with `pytest --cov=src`

## Performance

Test execution times (approximate):

- **Smoke tests**: < 5 seconds
- **Unit tests**: < 30 seconds
- **All tests**: < 2 minutes
- **With coverage**: < 3 minutes

Use `pytest --durations=10` to see slowest tests.

## Documentation

Full documentation: [tests/README.md](tests/README.md)

Topics covered:
- Detailed installation instructions
- Complete test suite overview
- Writing and organizing tests
- CI/CD integration
- Best practices
- Troubleshooting guide

## Getting Help

1. Check [tests/README.md](tests/README.md) for detailed docs
2. Review existing tests for examples
3. Check pytest docs: https://docs.pytest.org/
4. Open an issue on GitHub

## Quick Reference Card

```bash
# Essential commands
pytest                    # Run all tests
pytest -m unit           # Unit tests only
pytest -v                # Verbose output
pytest -x                # Stop on first failure
pytest -s                # Show print output
pytest --cov=src         # With coverage
pytest -k "test_name"    # Run specific test
pytest --durations=10    # Show slow tests
pytest -n auto           # Parallel execution

# Markers
-m unit                  # Unit tests
-m integration           # Integration tests
-m "not slow"            # Exclude slow
-m "not requires_api"    # No API needed
-m smoke                 # Quick validation

# Coverage
--cov=src                # Coverage report
--cov-report=html        # HTML report
--cov-report=term-missing # Show missing lines
--cov-fail-under=70      # Require 70% coverage
```

---

**Ready to test!** Run `pytest` to get started. 🚀