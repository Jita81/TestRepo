"""
Pytest Configuration and Fixtures
Provides common test fixtures and configuration for all tests.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import json
from typing import Dict, Any

# Import modules to test
from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.agentic_coder import AgenticCoder
from src.app_generator import AppGenerator


# ============================================================================
# Directory and Path Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def mock_repo_path(temp_dir):
    """Create a mock repository structure."""
    repo_path = os.path.join(temp_dir, "mock_repo")
    os.makedirs(repo_path, exist_ok=True)
    
    # Create mock files
    readme_content = """# Test Project
    
This is a test project for testing purposes.

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
- API_KEY=your_api_key
- DEBUG=True
"""
    
    with open(os.path.join(repo_path, "README.md"), "w") as f:
        f.write(readme_content)
    
    # Create requirements.txt
    with open(os.path.join(repo_path, "requirements.txt"), "w") as f:
        f.write("fastapi\nuvicorn\nrequests\n")
    
    # Create main.py
    main_content = """#!/usr/bin/env python3
import sys

def main():
    print("Hello from test app!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    with open(os.path.join(repo_path, "main.py"), "w") as f:
        f.write(main_content)
    
    # Create package.json for Node.js test
    package_json = {
        "name": "test-app",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.17.1",
            "axios": "^0.21.1"
        },
        "devDependencies": {
            "jest": "^27.0.0"
        },
        "scripts": {
            "start": "node index.js"
        }
    }
    with open(os.path.join(repo_path, "package.json"), "w") as f:
        json.dump(package_json, f, indent=2)
    
    return repo_path


@pytest.fixture
def sample_readme_data():
    """Sample README data for testing."""
    return {
        "raw_content": "# Test Project\n\nA test project",
        "html_content": "<h1>Test Project</h1><p>A test project</p>",
        "title": "Test Project",
        "description": "A test project for testing",
        "installation_instructions": ["pip install -r requirements.txt"],
        "dependencies": {
            "files": ["requirements.txt"],
            "packages": ["fastapi", "uvicorn", "requests"],
            "system_requirements": ["Python 3.7+"]
        },
        "usage_instructions": ["python main.py"],
        "configuration": {
            "environment_variables": ["API_KEY=test", "DEBUG=True"],
            "config_files": ["config.json"],
            "settings": []
        },
        "examples": ["python main.py --help"],
        "troubleshooting": ["Check API key", "Verify dependencies"],
        "project_type": "python",
        "main_files": ["main.py"]
    }


@pytest.fixture
def sample_code_analysis():
    """Sample code analysis data for testing."""
    return {
        "project_structure": {
            "files": [
                {"path": "main.py", "size": 1024, "extension": ".py"},
                {"path": "requirements.txt", "size": 256, "extension": ".txt"}
            ],
            "directories": [],
            "extensions": [".py", ".txt"],
            "size": 1280
        },
        "ai_analysis": {
            "entry_points": ["main.py"],
            "dependencies": ["fastapi", "uvicorn"],
            "build_commands": ["pip install -r requirements.txt"],
            "run_commands": ["python main.py"],
            "environment_variables": ["API_KEY"],
            "ports": ["8000"],
            "packaging_strategy": "pyinstaller",
            "special_requirements": [],
            "confidence_score": 0.9
        },
        "entry_points": ["main.py"],
        "dependencies": ["fastapi", "uvicorn"],
        "build_instructions": ["pip install -r requirements.txt"],
        "runtime_requirements": {
            "environment_variables": ["API_KEY"],
            "ports": ["8000"],
            "special_requirements": []
        }
    }


# ============================================================================
# Mock Object Fixtures
# ============================================================================

@pytest.fixture
def mock_github_api_response():
    """Mock GitHub API response."""
    return {
        "id": 123456,
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "description": "A test repository",
        "html_url": "https://github.com/testuser/test-repo",
        "clone_url": "https://github.com/testuser/test-repo.git",
        "stargazers_count": 100,
        "language": "Python",
        "default_branch": "main"
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "entry_points": ["main.py"],
        "dependencies": ["fastapi", "uvicorn"],
        "build_commands": ["pip install -r requirements.txt"],
        "run_commands": ["python main.py"],
        "environment_variables": ["API_KEY"],
        "ports": ["8000"],
        "packaging_strategy": "pyinstaller",
        "special_requirements": [],
        "confidence_score": 0.9
    })
    return mock_response


# ============================================================================
# Component Instance Fixtures
# ============================================================================

@pytest.fixture
def github_repo_instance():
    """Create a GitHubRepository instance."""
    return GitHubRepository()


@pytest.fixture
def readme_parser_instance():
    """Create a ReadmeParser instance."""
    return ReadmeParser()


@pytest.fixture
def agentic_coder_instance():
    """Create an AgenticCoder instance with mocked OpenAI client."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        coder = AgenticCoder()
        return coder


@pytest.fixture
def app_generator_instance():
    """Create an AppGenerator instance."""
    return AppGenerator()


# ============================================================================
# Mock Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "GITHUB_TOKEN": "test-github-token",
        "DEBUG": "True"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_openai_response
        mock_client.return_value = mock_instance
        yield mock_instance


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_github_urls():
    """Sample GitHub URLs for testing."""
    return {
        "valid": [
            "https://github.com/user/repo",
            "https://github.com/user/repo.git",
            "https://github.com/org/project",
            "http://github.com/user/repo"
        ],
        "invalid": [
            "not-a-url",
            "https://gitlab.com/user/repo",
            "https://github.com/",
            "https://github.com/only-one-part"
        ]
    }


@pytest.fixture
def sample_dependency_files():
    """Sample dependency file contents."""
    return {
        "requirements.txt": "fastapi==0.68.0\nuvicorn==0.15.0\nrequests>=2.26.0\n# Comment line\npyyaml",
        "package.json": json.dumps({
            "dependencies": {
                "express": "^4.17.1",
                "axios": "^0.21.1"
            },
            "devDependencies": {
                "jest": "^27.0.0"
            }
        })
    }


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create test output directories
    Path("htmlcov").mkdir(exist_ok=True)
    Path("test_output").mkdir(exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add markers based on test name
        if "api" in item.name.lower():
            item.add_marker(pytest.mark.requires_api)
        if "git" in item.name.lower() or "clone" in item.name.lower():
            item.add_marker(pytest.mark.requires_git)


def pytest_runtest_makereport(item, call):
    """Hook to customize test reporting."""
    if call.when == "call":
        if call.excinfo is not None:
            # Test failed - could add custom logging here
            pass


# ============================================================================
# Helper Functions
# ============================================================================

@pytest.fixture
def create_test_file():
    """Helper to create test files with content."""
    def _create_file(path: str, content: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path
    return _create_file


@pytest.fixture
def assert_file_exists():
    """Helper to assert file exists."""
    def _assert(path: str, message: str = None):
        msg = message or f"File {path} should exist"
        assert os.path.exists(path), msg
    return _assert


@pytest.fixture
def assert_dir_exists():
    """Helper to assert directory exists."""
    def _assert(path: str, message: str = None):
        msg = message or f"Directory {path} should exist"
        assert os.path.isdir(path), msg
    return _assert