"""
Pytest configuration and fixtures
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.readme_parser import ReadmeParser
from src.github_integration import GitHubRepository
from src.agentic_coder import AgenticCoder
from src.app_generator import AppGenerator


# ============================================================================
# Directory and File Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_repo_dir(temp_dir):
    """Create a sample repository directory structure."""
    repo_dir = os.path.join(temp_dir, "sample_repo")
    os.makedirs(repo_dir)
    
    # Create sample files
    with open(os.path.join(repo_dir, "main.py"), "w") as f:
        f.write('''#!/usr/bin/env python3
"""Sample Python application."""

def main():
    print("Hello, World!")
    
if __name__ == "__main__":
    main()
''')
    
    with open(os.path.join(repo_dir, "requirements.txt"), "w") as f:
        f.write("requests==2.28.0\npyyaml>=6.0\n")
    
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write('''# Sample Project

A sample Python project for testing.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Configuration

Set the following environment variables:
- API_KEY=your_key_here
- DEBUG=true

## Requirements

- Python 3.7+
- pip
''')
    
    yield repo_dir


@pytest.fixture
def sample_readme_content():
    """Sample README content for testing."""
    return '''# Test Project

This is a test project for the GitHub to App converter.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
npm install
```

## Usage

Run the application:

```bash
python main.py
```

Or use Docker:

```bash
docker-compose up
```

## Configuration

Set these environment variables:
- DATABASE_URL=postgres://localhost/db
- API_KEY=secret

## Requirements

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

## Examples

```python
from app import main

main()
```

## Troubleshooting

- If you get import errors, reinstall dependencies
- Check that all environment variables are set
- Make sure ports 8000 and 5432 are available
'''


@pytest.fixture
def sample_readme_file(temp_dir, sample_readme_content):
    """Create a sample README file."""
    readme_path = os.path.join(temp_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(sample_readme_content)
    return readme_path


# ============================================================================
# Parser and Component Fixtures
# ============================================================================

@pytest.fixture
def readme_parser():
    """Create a ReadmeParser instance."""
    return ReadmeParser()


@pytest.fixture
def github_repo():
    """Create a GitHubRepository instance."""
    return GitHubRepository()


@pytest.fixture
def agentic_coder():
    """Create an AgenticCoder instance."""
    return AgenticCoder()


@pytest.fixture
def app_generator():
    """Create an AppGenerator instance."""
    return AppGenerator()


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "entry_points": ["main.py"],
        "dependencies": ["requests", "pyyaml"],
        "build_commands": ["pip install -r requirements.txt"],
        "run_commands": ["python main.py"],
        "environment_variables": ["API_KEY", "DEBUG"],
        "ports": ["8000"],
        "packaging_strategy": "pyinstaller",
        "special_requirements": [],
        "confidence_score": 0.9
    }


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = str(mock_openai_response).replace("'", '"')
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_github_api_response():
    """Mock GitHub API response."""
    return {
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "description": "A test repository",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "default_branch": "main",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-12-31T23:59:59Z"
    }


@pytest.fixture
def mock_git_repo():
    """Mock Git repository."""
    mock_repo = MagicMock()
    mock_repo.clone_from = MagicMock(return_value=mock_repo)
    return mock_repo


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_parsed_readme():
    """Sample parsed README data."""
    return {
        'raw_content': '# Test Project\n\nA test project.',
        'html_content': '<h1>Test Project</h1><p>A test project.</p>',
        'title': 'Test Project',
        'description': 'A test project for testing.',
        'installation_instructions': [
            'pip install -r requirements.txt',
            'npm install'
        ],
        'dependencies': {
            'files': ['requirements.txt', 'package.json'],
            'packages': ['requests', 'pyyaml', 'express'],
            'system_requirements': ['Python 3.8+', 'Node.js 14+']
        },
        'usage_instructions': ['python main.py', 'npm start'],
        'configuration': {
            'environment_variables': ['API_KEY=secret', 'DEBUG=true'],
            'config_files': ['config.json', 'settings.yml'],
            'settings': []
        },
        'examples': ['python main.py', 'import app\napp.run()'],
        'troubleshooting': ['Check dependencies', 'Verify environment variables'],
        'project_type': 'python',
        'main_files': ['main.py']
    }


@pytest.fixture
def sample_code_analysis():
    """Sample code analysis data."""
    return {
        'project_structure': {
            'files': [
                {'path': 'main.py', 'size': 1024, 'extension': '.py'},
                {'path': 'requirements.txt', 'size': 256, 'extension': '.txt'}
            ],
            'directories': [],
            'extensions': ['.py', '.txt'],
            'size': 1280
        },
        'ai_analysis': {
            'entry_points': ['main.py'],
            'dependencies': ['requests', 'pyyaml'],
            'build_commands': ['pip install -r requirements.txt'],
            'run_commands': ['python main.py'],
            'environment_variables': ['API_KEY'],
            'ports': ['8000'],
            'packaging_strategy': 'pyinstaller',
            'special_requirements': [],
            'confidence_score': 0.9
        },
        'entry_points': ['main.py'],
        'dependencies': ['requests', 'pyyaml'],
        'build_instructions': ['pip install -r requirements.txt'],
        'runtime_requirements': {
            'environment_variables': ['API_KEY'],
            'ports': ['8000'],
            'special_requirements': []
        }
    }


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("API_KEY", "test_key")
    monkeypatch.setenv("DEBUG", "true")


@pytest.fixture
def no_api_key(monkeypatch):
    """Remove API key from environment."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Network Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_requests_get(mock_github_api_response):
    """Mock requests.get for API calls."""
    import requests
    original_get = requests.get
    
    def mock_get(url, *args, **kwargs):
        mock_response = Mock()
        if "api.github.com" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = mock_github_api_response
        else:
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
        return mock_response
    
    import requests
    requests.get = mock_get
    yield mock_get
    requests.get = original_get


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_api: mark test as requiring API keys")
    config.addinivalue_line("markers", "requires_network: mark test as requiring network")
    config.addinivalue_line("markers", "smoke: mark test as a smoke test")