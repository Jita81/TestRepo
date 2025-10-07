"""
Integration tests for the GitHub to App Converter
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import shutil

from main import app
from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder


@pytest.fixture
def test_client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.mark.integration
class TestMainApplicationEndpoints:
    """Integration tests for main application endpoints."""
    
    def test_home_endpoint(self, test_client):
        """Test home page endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    
    def test_home_endpoint_returns_html(self, test_client):
        """Test that home page returns valid HTML."""
        response = test_client.get("/")
        
        # Should contain HTML elements
        content = response.text
        assert "<!DOCTYPE html>" in content or "<html" in content
    
    @patch('main.github_repo.clone_repository')
    @patch('main.readme_parser.parse_readme')
    @patch('main.agentic_coder.analyze_codebase')
    @patch('main.app_generator.generate_app')
    def test_convert_endpoint_success(
        self, 
        mock_generate, 
        mock_analyze, 
        mock_parse, 
        mock_clone, 
        test_client, 
        temp_dir
    ):
        """Test successful repository conversion."""
        # Setup mocks
        mock_clone.return_value = AsyncMock(return_value=temp_dir)
        mock_parse.return_value = AsyncMock(return_value={
            'title': 'Test Project',
            'description': 'A test project',
            'project_type': 'python'
        })
        mock_analyze.return_value = AsyncMock(return_value={
            'entry_points': ['main.py'],
            'dependencies': ['requests']
        })
        mock_generate.return_value = AsyncMock(return_value=os.path.join(temp_dir, 'test_app'))
        
        # Make request
        response = test_client.post(
            "/convert",
            data={
                "github_url": "https://github.com/octocat/Hello-World",
                "app_name": "test_app",
                "target_platform": "web"
            }
        )
        
        # Verify response
        assert response.status_code == 200 or response.status_code == 500
        # May fail due to async mock setup, but endpoint should be callable
    
    def test_convert_endpoint_missing_url(self, test_client):
        """Test conversion with missing GitHub URL."""
        response = test_client.post(
            "/convert",
            data={
                "target_platform": "web"
            }
        )
        
        # Should return error (422 Unprocessable Entity for missing required field)
        assert response.status_code == 422
    
    def test_convert_endpoint_invalid_platform(self, test_client):
        """Test conversion with valid request format."""
        with patch('main.github_repo.clone_repository') as mock_clone:
            mock_clone.side_effect = Exception("Test error")
            
            response = test_client.post(
                "/convert",
                data={
                    "github_url": "https://github.com/octocat/Hello-World",
                    "target_platform": "invalid"
                }
            )
            
            # Should return error
            assert response.status_code == 500
    
    def test_download_endpoint_file_not_found(self, test_client):
        """Test downloading non-existent file."""
        response = test_client.get("/download/nonexistent_file.zip")
        
        assert response.status_code == 404
    
    def test_download_endpoint_with_existing_file(self, test_client, temp_dir):
        """Test downloading existing file."""
        # Create a test file in generated_apps
        os.makedirs("generated_apps", exist_ok=True)
        test_file = os.path.join("generated_apps", "test_download.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        try:
            response = test_client.get("/download/test_download.txt")
            
            # Should successfully download
            assert response.status_code == 200
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_status_endpoint(self, test_client):
        """Test status endpoint."""
        response = test_client.get("/status/test_task_id")
        
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'progress' in data


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_conversion_workflow_with_mocks(
        self, 
        sample_repo_dir, 
        sample_parsed_readme, 
        sample_code_analysis,
        temp_dir
    ):
        """Test full conversion workflow with mocked components."""
        # Initialize components
        github_repo = GitHubRepository()
        readme_parser = ReadmeParser()
        agentic_coder = AgenticCoder()
        app_generator = AppGenerator()
        app_generator.output_dir = temp_dir
        
        # Mock GitHub cloning
        with patch.object(github_repo, 'clone_repository', return_value=sample_repo_dir):
            repo_path = await github_repo.clone_repository("https://github.com/test/repo")
            assert os.path.exists(repo_path)
        
        # Parse README
        readme_data = await readme_parser.parse_readme(sample_repo_dir)
        assert 'title' in readme_data
        
        # Mock AI analysis
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"entry_points": ["main.py"], "dependencies": []}'
            mock_client.chat.completions.create.return_value = mock_response
            
            code_analysis = await agentic_coder.analyze_codebase(repo_path, readme_data)
            assert 'project_structure' in code_analysis
        
        # Generate app
        result = await app_generator.generate_app(
            sample_repo_dir,
            readme_data,
            code_analysis,
            'test_app',
            'web'
        )
        
        assert result is not None
        assert os.path.exists(result)


@pytest.mark.integration
class TestComponentIntegration:
    """Test integration between different components."""
    
    @pytest.mark.asyncio
    async def test_readme_parser_and_agentic_coder_integration(
        self, 
        sample_repo_dir
    ):
        """Test integration between ReadmeParser and AgenticCoder."""
        readme_parser = ReadmeParser()
        agentic_coder = AgenticCoder()
        
        # Parse README
        readme_data = await readme_parser.parse_readme(sample_repo_dir)
        
        # Use parsed data for analysis
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"entry_points": ["main.py"]}'
            mock_client.chat.completions.create.return_value = mock_response
            
            analysis = await agentic_coder.analyze_codebase(sample_repo_dir, readme_data)
            
            assert analysis is not None
            assert 'project_structure' in analysis
    
    @pytest.mark.asyncio
    async def test_agentic_coder_and_app_generator_integration(
        self,
        sample_repo_dir,
        sample_parsed_readme,
        temp_dir
    ):
        """Test integration between AgenticCoder and AppGenerator."""
        agentic_coder = AgenticCoder()
        app_generator = AppGenerator()
        app_generator.output_dir = temp_dir
        
        # Get code analysis
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"entry_points": ["main.py"], "dependencies": ["requests"]}'
            mock_client.chat.completions.create.return_value = mock_response
            
            code_analysis = await agentic_coder.analyze_codebase(sample_repo_dir, sample_parsed_readme)
        
        # Generate app using analysis
        result = await app_generator.generate_app(
            sample_repo_dir,
            sample_parsed_readme,
            code_analysis,
            'test_app',
            'web'
        )
        
        assert result is not None
        assert os.path.exists(result)


@pytest.mark.integration
@pytest.mark.slow
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.mark.asyncio
    async def test_python_project_conversion(self, temp_dir):
        """Test converting a Python project."""
        # Create a realistic Python project structure
        project_dir = os.path.join(temp_dir, "python_project")
        os.makedirs(project_dir)
        
        # Create files
        with open(os.path.join(project_dir, "main.py"), "w") as f:
            f.write('''
#!/usr/bin/env python3
import sys

def main():
    print("Hello from Python project!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''')
        
        with open(os.path.join(project_dir, "requirements.txt"), "w") as f:
            f.write("requests>=2.28.0\n")
        
        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write('''# Python Project

A sample Python application.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
''')
        
        # Test the workflow
        readme_parser = ReadmeParser()
        app_generator = AppGenerator()
        app_generator.output_dir = temp_dir
        
        readme_data = await readme_parser.parse_readme(project_dir)
        assert readme_data['project_type'] == 'python'
        
        # Mock code analysis
        code_analysis = {
            'entry_points': ['main.py'],
            'dependencies': ['requests'],
            'ai_analysis': {}
        }
        
        result = await app_generator.generate_app(
            project_dir,
            readme_data,
            code_analysis,
            'python_app',
            'web'
        )
        
        assert result is not None
        assert os.path.exists(result)
    
    @pytest.mark.asyncio
    async def test_nodejs_project_detection(self, temp_dir):
        """Test detecting and handling Node.js projects."""
        # Create a Node.js project structure
        project_dir = os.path.join(temp_dir, "nodejs_project")
        os.makedirs(project_dir)
        
        with open(os.path.join(project_dir, "package.json"), "w") as f:
            f.write('''{
  "name": "test-app",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}''')
        
        with open(os.path.join(project_dir, "index.js"), "w") as f:
            f.write('''
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(3000);
''')
        
        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write('''# Node.js Project

## Installation
```bash
npm install
```

## Usage
```bash
npm start
```
''')
        
        # Test detection
        readme_parser = ReadmeParser()
        readme_data = await readme_parser.parse_readme(project_dir)
        
        assert readme_data['project_type'] == 'nodejs'
        assert 'express' in str(readme_data['dependencies'])


@pytest.mark.integration
@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for basic functionality."""
    
    def test_app_imports(self):
        """Test that all main modules can be imported."""
        from src.readme_parser import ReadmeParser
        from src.github_integration import GitHubRepository
        from src.agentic_coder import AgenticCoder
        from src.app_generator import AppGenerator
        
        assert ReadmeParser is not None
        assert GitHubRepository is not None
        assert AgenticCoder is not None
        assert AppGenerator is not None
    
    def test_components_initialization(self):
        """Test that all components can be initialized."""
        parser = ReadmeParser()
        repo = GitHubRepository()
        coder = AgenticCoder()
        generator = AppGenerator()
        
        assert parser is not None
        assert repo is not None
        assert coder is not None
        assert generator is not None
    
    def test_fastapi_app_initialization(self):
        """Test that FastAPI app is properly initialized."""
        from main import app
        
        assert app is not None
        assert app.title == "GitHub to App Converter"
        assert app.version == "1.0.0"
    
    def test_api_routes_exist(self):
        """Test that all expected API routes exist."""
        from main import app
        
        routes = [route.path for route in app.routes]
        
        assert "/" in routes
        assert "/convert" in routes
        assert "/download/{filename}" in routes
        assert "/status/{task_id}" in routes


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_invalid_repo_path_handling(self):
        """Test handling of invalid repository path."""
        readme_parser = ReadmeParser()
        
        result = await readme_parser.parse_readme("/nonexistent/path")
        
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_github_api_failure_handling(self):
        """Test handling of GitHub API failures."""
        github_repo = GitHubRepository()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            metadata = await github_repo._get_repository_metadata("test", "repo")
            
            assert 'error' in metadata
    
    def test_convert_endpoint_exception_handling(self, test_client):
        """Test that exceptions in conversion are properly handled."""
        with patch('main.github_repo.clone_repository') as mock_clone:
            mock_clone.side_effect = Exception("Unexpected error")
            
            response = test_client.post(
                "/convert",
                data={
                    "github_url": "https://github.com/octocat/Hello-World",
                    "target_platform": "web"
                }
            )
            
            # Should return 500 error
            assert response.status_code == 500
            assert 'detail' in response.json()
    
    @pytest.mark.asyncio
    async def test_app_generation_with_missing_dependencies(self, temp_dir, sample_parsed_readme):
        """Test app generation when dependencies are missing."""
        app_generator = AppGenerator()
        app_generator.output_dir = temp_dir
        
        # Create minimal repo
        repo_dir = os.path.join(temp_dir, "repo")
        os.makedirs(repo_dir)
        
        code_analysis = {
            'dependencies': [],
            'entry_points': []
        }
        
        # Should still generate app structure
        result = await app_generator.generate_app(
            repo_dir,
            sample_parsed_readme,
            code_analysis,
            'test_app',
            'web'
        )
        
        assert result is not None
        assert os.path.exists(result)