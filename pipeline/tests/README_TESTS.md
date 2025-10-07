# Test Suite Guide

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

## Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `test_basic.py` | Project structure validation | 8 |
| `test_models.py` | Data model validation | 20+ |
| `test_api.py` | API endpoint testing | 8 |
| `test_api_security.py` | Security validation | 20+ |
| `test_exceptions.py` | Exception handling | 12 |
| `test_config.py` | Configuration management | 8 |
| `test_logging.py` | Logging functionality | 8 |
| `test_edge_cases.py` | Boundary conditions | 25+ |
| `test_queue_client.py` | Queue operations | 12 |
| `test_video_generator.py` | Video generation | 5+ |
| `test_model_converter.py` | 3D conversion | 5+ |
| `test_integration.py` | End-to-end flows | 3+ |

**Total**: 140+ test cases

## Running Specific Tests

```bash
# Run specific file
pytest tests/test_models.py

# Run specific class
pytest tests/test_models.py::TestTextInput

# Run specific test
pytest tests/test_models.py::TestTextInput::test_valid_input

# Run tests matching pattern
pytest -k "test_security"
```

## Test Categories

### Unit Tests
```bash
pytest tests/test_models.py tests/test_exceptions.py tests/test_config.py
```

### Integration Tests
```bash
pytest tests/test_integration.py
```

### Security Tests
```bash
pytest tests/test_api_security.py
```

### Edge Case Tests
```bash
pytest tests/test_edge_cases.py
```

## Expected Results

All tests are designed to pass. If a test fails:

1. Check that dependencies are installed
2. Verify services are running (for integration tests)
3. Check logs for error details
4. Review test documentation in TEST_COVERAGE.md

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -v
```

## Test Coverage Report

After running tests with coverage:

```bash
pytest --cov=. --cov-report=html
```

View the report:
```bash
open htmlcov/index.html
```

## For More Information

See [TEST_COVERAGE.md](../TEST_COVERAGE.md) for detailed test documentation.