"""
Test utilities and helper functions
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List


def create_test_repo_structure(base_dir: str, project_type: str = 'python') -> str:
    """
    Create a test repository structure for testing.
    
    Args:
        base_dir: Base directory to create the repo in
        project_type: Type of project (python, nodejs, rust, etc.)
        
    Returns:
        Path to the created repository
    """
    repo_dir = os.path.join(base_dir, f"test_{project_type}_repo")
    os.makedirs(repo_dir, exist_ok=True)
    
    if project_type == 'python':
        _create_python_project(repo_dir)
    elif project_type == 'nodejs':
        _create_nodejs_project(repo_dir)
    elif project_type == 'rust':
        _create_rust_project(repo_dir)
    else:
        _create_generic_project(repo_dir)
    
    return repo_dir


def _create_python_project(repo_dir: str):
    """Create a Python project structure."""
    # Main file
    with open(os.path.join(repo_dir, "main.py"), "w") as f:
        f.write('''#!/usr/bin/env python3
"""Main application file."""

def main():
    """Main function."""
    print("Hello from Python!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
''')
    
    # Requirements
    with open(os.path.join(repo_dir, "requirements.txt"), "w") as f:
        f.write("requests>=2.28.0\npyyaml>=6.0\n")
    
    # README
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write('''# Python Test Project

A test Python project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Requirements

- Python 3.7+
- pip
''')
    
    # Config file
    with open(os.path.join(repo_dir, "config.yaml"), "w") as f:
        f.write("debug: true\napi_key: test_key\n")


def _create_nodejs_project(repo_dir: str):
    """Create a Node.js project structure."""
    # Package.json
    with open(os.path.join(repo_dir, "package.json"), "w") as f:
        f.write('''{
  "name": "test-nodejs-app",
  "version": "1.0.0",
  "description": "Test Node.js application",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}''')
    
    # Main file
    with open(os.path.join(repo_dir, "index.js"), "w") as f:
        f.write('''const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello from Node.js!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
''')
    
    # README
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write('''# Node.js Test Project

A test Node.js project.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```

## Requirements

- Node.js 14+
- npm
''')


def _create_rust_project(repo_dir: str):
    """Create a Rust project structure."""
    # Cargo.toml
    with open(os.path.join(repo_dir, "Cargo.toml"), "w") as f:
        f.write('''[package]
name = "test-rust-app"
version = "0.1.0"
edition = "2021"

[dependencies]
''')
    
    # Main file
    src_dir = os.path.join(repo_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    with open(os.path.join(src_dir, "main.rs"), "w") as f:
        f.write('''fn main() {
    println!("Hello from Rust!");
}
''')
    
    # README
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write('''# Rust Test Project

A test Rust project.

## Installation

```bash
cargo build
```

## Usage

```bash
cargo run
```

## Requirements

- Rust 1.60+
- Cargo
''')


def _create_generic_project(repo_dir: str):
    """Create a generic project structure."""
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write('''# Generic Test Project

A generic test project.

## Installation

Follow the installation instructions.

## Usage

Run the application.
''')
    
    with open(os.path.join(repo_dir, "main.txt"), "w") as f:
        f.write("Generic project file")


def create_mock_github_response(
    name: str = "test-repo",
    owner: str = "testuser",
    description: str = "Test repository",
    language: str = "Python"
) -> Dict[str, Any]:
    """
    Create a mock GitHub API response.
    
    Args:
        name: Repository name
        owner: Repository owner
        description: Repository description
        language: Primary language
        
    Returns:
        Mock GitHub API response dictionary
    """
    return {
        "name": name,
        "full_name": f"{owner}/{name}",
        "owner": {"login": owner},
        "description": description,
        "language": language,
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "default_branch": "main",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-12-31T23:59:59Z",
        "clone_url": f"https://github.com/{owner}/{name}.git",
        "ssh_url": f"git@github.com:{owner}/{name}.git",
        "size": 1024,
        "license": {"name": "MIT License"}
    }


def create_mock_openai_response(
    entry_points: List[str] = None,
    dependencies: List[str] = None,
    confidence: float = 0.9
) -> Dict[str, Any]:
    """
    Create a mock OpenAI API response.
    
    Args:
        entry_points: List of entry point files
        dependencies: List of dependencies
        confidence: Confidence score
        
    Returns:
        Mock OpenAI response dictionary
    """
    if entry_points is None:
        entry_points = ["main.py"]
    if dependencies is None:
        dependencies = ["requests", "pyyaml"]
    
    return {
        "entry_points": entry_points,
        "dependencies": dependencies,
        "build_commands": ["pip install -r requirements.txt"],
        "run_commands": ["python main.py"],
        "environment_variables": ["API_KEY", "DEBUG"],
        "ports": ["8000"],
        "packaging_strategy": "pyinstaller",
        "special_requirements": [],
        "confidence_score": confidence
    }


def assert_file_exists(file_path: str, message: str = None):
    """
    Assert that a file exists.
    
    Args:
        file_path: Path to the file
        message: Optional custom error message
    """
    if not os.path.exists(file_path):
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"File does not exist: {file_path}")


def assert_directory_exists(dir_path: str, message: str = None):
    """
    Assert that a directory exists.
    
    Args:
        dir_path: Path to the directory
        message: Optional custom error message
    """
    if not os.path.isdir(dir_path):
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Directory does not exist: {dir_path}")


def assert_file_contains(file_path: str, content: str, message: str = None):
    """
    Assert that a file contains specific content.
    
    Args:
        file_path: Path to the file
        content: Content to search for
        message: Optional custom error message
    """
    assert_file_exists(file_path)
    
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    if content not in file_content:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(
                f"Content not found in file {file_path}:\n"
                f"Looking for: {content}\n"
                f"File content: {file_content[:200]}..."
            )


def count_files_in_directory(dir_path: str, extension: str = None) -> int:
    """
    Count files in a directory.
    
    Args:
        dir_path: Path to the directory
        extension: Optional file extension to filter by (e.g., '.py')
        
    Returns:
        Number of files
    """
    count = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if extension is None or file.endswith(extension):
                count += 1
    return count


def cleanup_test_files(*paths):
    """
    Clean up test files and directories.
    
    Args:
        *paths: Variable number of paths to clean up
    """
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)


class MockFileSystem:
    """Mock file system for testing without actual file I/O."""
    
    def __init__(self):
        self.files = {}
        self.directories = set()
    
    def create_file(self, path: str, content: str):
        """Create a mock file."""
        self.files[path] = content
        # Add parent directories
        parent = os.path.dirname(path)
        while parent:
            self.directories.add(parent)
            parent = os.path.dirname(parent)
    
    def create_directory(self, path: str):
        """Create a mock directory."""
        self.directories.add(path)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return path in self.files
    
    def directory_exists(self, path: str) -> bool:
        """Check if directory exists."""
        return path in self.directories
    
    def read_file(self, path: str) -> str:
        """Read file content."""
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path]
    
    def list_files(self, directory: str = None) -> List[str]:
        """List files in directory."""
        if directory is None:
            return list(self.files.keys())
        
        return [
            path for path in self.files.keys()
            if path.startswith(directory)
        ]


def generate_test_readme(
    title: str = "Test Project",
    description: str = "A test project",
    project_type: str = "python"
) -> str:
    """
    Generate a test README content.
    
    Args:
        title: Project title
        description: Project description
        project_type: Type of project
        
    Returns:
        README content as string
    """
    install_section = ""
    usage_section = ""
    
    if project_type == "python":
        install_section = "```bash\npip install -r requirements.txt\n```"
        usage_section = "```bash\npython main.py\n```"
    elif project_type == "nodejs":
        install_section = "```bash\nnpm install\n```"
        usage_section = "```bash\nnpm start\n```"
    elif project_type == "rust":
        install_section = "```bash\ncargo build\n```"
        usage_section = "```bash\ncargo run\n```"
    
    return f"""# {title}

{description}

## Installation

{install_section}

## Usage

{usage_section}

## Features

- Feature 1
- Feature 2
- Feature 3

## Configuration

Set the following environment variables:
- API_KEY=your_key
- DEBUG=true

## Requirements

- Required dependency 1
- Required dependency 2

## License

MIT License
"""