# Test Suite Documentation

Comprehensive test suite for the GitHub to App Converter project.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Test Categories](#test-categories)
- [Writing New Tests](#writing-new-tests)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

This test suite provides comprehensive coverage for the GitHub to App Converter, including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **End-to-End Tests**: Test complete user workflows
- **Smoke Tests**: Quick validation of critical functionality

The test suite uses:
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and fixtures
- **httpx**: HTTP client testing for FastAPI

## Installation

### 1. Install Production Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Testing Dependencies

```bash
# Option 1: Install from main requirements (includes basic test dependencies)
pip install -r requirements.txt

# Option 2: Install all development dependencies (recommended for contributors)
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
pytest --version
python -m pytest --version
```

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run smoke tests (quick validation)
pytest -m smoke

# Exclude slow tests
pytest -m "not slow"

# Run tests that don't require API keys
pytest -m "not requires_api"
```

### Run Specific Test Files

```bash
# Run tests for a specific module
pytest tests/test_readme_parser.py

# Run tests for multiple modules
pytest tests/test_readme_parser.py tests/test_github_integration.py

# Run a specific test class
pytest tests/test_readme_parser.py::TestReadmeParser

# Run a specific test function
pytest tests/test_readme_parser.py::TestReadmeParser::test_init
```

### Code Coverage

```bash
# Run tests with coverage
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Generate coverage report with missing lines
pytest --cov=src --cov-report=term-missing

# Set minimum coverage threshold (fail if below 70%)
pytest --cov=src --cov-fail-under=70
```

### Parallel Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers
```

### Output Options

```bash
# Capture output (default)
pytest

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show test durations
pytest --durations=10
```

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_readme_parser.py       # Unit tests for ReadmeParser
├── test_github_integration.py  # Unit tests for GitHubRepository
├── test_agentic_coder.py       # Unit tests for AgenticCoder
├── test_app_generator.py       # Unit tests for AppGenerator
├── test_integration.py         # Integration and E2E tests
├── test_utils.py               # Test utilities and helpers
└── README.md                   # This file
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

```python
@pytest.mark.unit
def test_parse_readme_success(readme_parser, sample_repo_dir):
    """Test successful README parsing."""
    result = await readme_parser.parse_readme(sample_repo_dir)
    assert result is not None
```

**Run unit tests:**
```bash
pytest -m unit
```

### Integration Tests (`@pytest.mark.integration`)

Test interactions between components:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_conversion_workflow():
    """Test complete conversion workflow."""
    # Test multiple components working together
```

**Run integration tests:**
```bash
pytest -m integration
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to execute:

```python
@pytest.mark.slow
def test_large_repository_conversion():
    """Test conversion of large repository."""
    # Long-running test
```

**Skip slow tests:**
```bash
pytest -m "not slow"
```

### API Tests (`@pytest.mark.requires_api`)

Tests requiring API keys:

```python
@pytest.mark.requires_api
async def test_openai_integration():
    """Test OpenAI API integration."""
    # Requires OPENAI_API_KEY
```

**Skip API tests:**
```bash
pytest -m "not requires_api"
```

### Network Tests (`@pytest.mark.requires_network`)

Tests requiring network connectivity:

```python
@pytest.mark.requires_network
async def test_github_api_call():
    """Test GitHub API call."""
    # Requires internet connection
```

**Skip network tests:**
```bash
pytest -m "not requires_network"
```

### Smoke Tests (`@pytest.mark.smoke`)

Quick validation tests:

```python
@pytest.mark.smoke
def test_app_initialization():
    """Test that app initializes correctly."""
    from main import app
    assert app is not None
```

**Run smoke tests:**
```bash
pytest -m smoke
```

## Writing New Tests

### Test File Naming

- Test files must start with `test_` or end with `_test.py`
- Name test files after the module they test: `test_module_name.py`

### Test Function Naming

- Test functions must start with `test_`
- Use descriptive names: `test_parse_readme_with_missing_file`

### Using Fixtures

Fixtures are defined in `conftest.py` and available to all tests:

```python
def test_with_fixtures(readme_parser, sample_repo_dir, temp_dir):
    """Test using fixtures."""
    # readme_parser, sample_repo_dir, temp_dir are automatically provided
    result = readme_parser.parse_readme(sample_repo_dir)
    assert result is not None
```

### Available Fixtures

- `temp_dir`: Temporary directory (auto-cleanup)
- `sample_repo_dir`: Sample repository with test files
- `sample_readme_content`: Sample README content
- `readme_parser`: ReadmeParser instance
- `github_repo`: GitHubRepository instance
- `agentic_coder`: AgenticCoder instance
- `app_generator`: AppGenerator instance
- `mock_openai_response`: Mock OpenAI API response
- `mock_github_api_response`: Mock GitHub API response
- `test_client`: FastAPI test client

### Example Test

```python
import pytest
from src.readme_parser import ReadmeParser

@pytest.mark.unit
class TestMyFeature:
    """Tests for my new feature."""
    
    @pytest.mark.asyncio
    async def test_feature_success(self, readme_parser, sample_repo_dir):
        """Test successful feature operation."""
        # Arrange
        expected_result = {"status": "success"}
        
        # Act
        result = await readme_parser.parse_readme(sample_repo_dir)
        
        # Assert
        assert result is not None
        assert "title" in result
    
    def test_feature_error(self, readme_parser):
        """Test feature error handling."""
        with pytest.raises(ValueError):
            readme_parser._parse_invalid_data(None)
```

### Mocking

Use `unittest.mock` or `pytest-mock` for mocking:

```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
def test_with_mock():
    """Test with mocked dependency."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        # Your test code here
```

### Async Tests

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

## Test Configuration

### pytest.ini

Test configuration is in `/workspace/pytest.ini`:

```ini
[pytest]
testpaths = tests
addopts = -v --cov=src --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    requires_api: Tests requiring API keys
    requires_network: Tests requiring network
    smoke: Smoke tests
```

### Coverage Configuration

Coverage settings are in `pytest.ini`:
- Minimum coverage: 70%
- Coverage reports: terminal, HTML, XML
- Omit: tests, venv, __pycache__

## Continuous Integration

### GitHub Actions

Example CI configuration (`.github/workflows/tests.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements-dev.txt
      - run: pytest -m "not requires_api and not requires_network"
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Example `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest -m "not slow and not requires_api"
        language: system
        pass_filenames: false
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run pytest from project root
cd /workspace && pytest
```

#### 2. Async Test Failures

**Problem:** `RuntimeError: Event loop is closed`

**Solution:** Ensure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

#### 3. Coverage Not Working

**Problem:** Coverage report shows 0%

**Solution:** Ensure coverage is configured correctly:
```bash
pytest --cov=src --cov-report=term-missing
```

#### 4. Tests Timeout

**Problem:** Tests hang or timeout

**Solution:** Add timeout marker:
```python
@pytest.mark.timeout(10)
def test_function():
    pass
```

Or use command line:
```bash
pytest --timeout=10
```

#### 5. API Key Required

**Problem:** Tests fail due to missing API key

**Solution:** Skip tests requiring API:
```bash
pytest -m "not requires_api"
```

Or set environment variable:
```bash
export OPENAI_API_KEY="your_key_here"
pytest
```

### Debug Mode

Run tests in debug mode:

```bash
# Use ipdb for debugging
pip install ipdb
pytest --pdb  # Drop into debugger on failure

# Or add breakpoint in code
import ipdb; ipdb.set_trace()
```

### Verbose Output

Get more information:

```bash
# Show all output
pytest -vv -s

# Show local variables on failure
pytest -l

# Show test durations
pytest --durations=0
```

## Best Practices

1. **Keep tests independent**: Each test should work in isolation
2. **Use descriptive names**: Test names should explain what is being tested
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Mock external dependencies**: Don't make real API calls in unit tests
5. **Clean up resources**: Use fixtures with cleanup or context managers
6. **Test edge cases**: Include tests for error conditions and edge cases
7. **Maintain test speed**: Keep unit tests fast, mark slow tests appropriately
8. **Document complex tests**: Add docstrings explaining test purpose
9. **Use parametrize**: Test multiple inputs with `@pytest.mark.parametrize`
10. **Check coverage**: Aim for >70% code coverage

## Contributing

When contributing new features:

1. Write tests for new functionality
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov=src --cov-report=term-missing`
4. Run linters: `flake8 src tests`
5. Format code: `black src tests`

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Support

For issues or questions:
1. Check this documentation
2. Review existing tests for examples
3. Check pytest documentation
4. Open an issue on GitHub