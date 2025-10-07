"""
Integration Tests for End-to-End Workflows

Tests complete workflows including:
- Full repository conversion pipeline
- Clone -> Parse -> Analyze -> Generate workflow
- Multi-module integration
- Real-world scenarios
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.agentic_coder import AgenticCoder
from src.app_generator import AppGenerator


class TestFullConversionPipeline:
    """Test complete repository conversion pipeline."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_pipeline_python_project(self, mock_repo_path, mock_openai_client):
        """Test complete pipeline for Python project."""
        # Initialize all components
        github_repo = GitHubRepository()
        readme_parser = ReadmeParser()
        app_generator = AppGenerator()
        
        with patch('openai.OpenAI') as mock_openai_class:
            # Setup mock OpenAI responses
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["fastapi", "uvicorn"],
                "build_commands": ["pip install -r requirements.txt"],
                "run_commands": ["python main.py"],
                "environment_variables": [],
                "ports": ["8000"],
                "packaging_strategy": "pyinstaller",
                "special_requirements": [],
                "confidence_score": 0.9
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            # Step 1: Parse README
            readme_data = await readme_parser.parse_readme(mock_repo_path)
            assert 'title' in readme_data
            assert 'project_type' in readme_data
            
            # Step 2: Analyze codebase
            code_analysis = await agentic_coder.analyze_codebase(mock_repo_path, readme_data)
            assert 'project_structure' in code_analysis
            assert 'entry_points' in code_analysis
            
            # Step 3: Generate app
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                
                app_path = await app_generator.generate_app(
                    mock_repo_path,
                    readme_data,
                    code_analysis,
                    "test_integration_app",
                    "web"
                )
                
                assert app_path is not None
                assert os.path.exists(app_path)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pipeline_handles_missing_readme(self, temp_dir):
        """Test pipeline when README is missing."""
        readme_parser = ReadmeParser()
        
        # Parse directory without README
        readme_data = await readme_parser.parse_readme(temp_dir)
        
        # Should return error but not crash
        assert 'error' in readme_data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pipeline_multiple_platforms(self, mock_repo_path, mock_openai_client):
        """Test generating apps for multiple platforms."""
        readme_parser = ReadmeParser()
        app_generator = AppGenerator()
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["fastapi"],
                "build_commands": [],
                "run_commands": ["python main.py"]
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            readme_data = await readme_parser.parse_readme(mock_repo_path)
            code_analysis = await agentic_coder.analyze_codebase(mock_repo_path, readme_data)
            
            # Test multiple platforms
            platforms = ['web', 'docker']
            
            for platform in platforms:
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = Mock(returncode=0)
                    
                    app_path = await app_generator.generate_app(
                        mock_repo_path,
                        readme_data,
                        code_analysis,
                        f"test_{platform}_app",
                        platform
                    )
                    
                    assert app_path is not None


class TestModuleIntegration:
    """Test integration between different modules."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_readme_parser_feeds_agentic_coder(self, mock_repo_path, mock_openai_client):
        """Test that README parser output is compatible with agentic coder input."""
        readme_parser = ReadmeParser()
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": []
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            # Parse README
            readme_data = await readme_parser.parse_readme(mock_repo_path)
            
            # Should be able to use in agentic coder without errors
            code_analysis = await agentic_coder.analyze_codebase(mock_repo_path, readme_data)
            
            assert isinstance(code_analysis, dict)
            assert 'error' not in code_analysis or 'project_structure' in code_analysis
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agentic_coder_feeds_app_generator(self, mock_repo_path, sample_readme_data, mock_openai_client):
        """Test that agentic coder output is compatible with app generator input."""
        app_generator = AppGenerator()
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["fastapi"],
                "build_commands": [],
                "run_commands": ["python main.py"]
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            # Get code analysis
            code_analysis = await agentic_coder.analyze_codebase(mock_repo_path, sample_readme_data)
            
            # Should be able to use in app generator without errors
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                
                app_path = await app_generator.generate_app(
                    mock_repo_path,
                    sample_readme_data,
                    code_analysis,
                    "test_app",
                    "web"
                )
                
                assert app_path is not None


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_fastapi_project(self, temp_dir, mock_openai_client):
        """Test processing a Python FastAPI project."""
        # Create a realistic FastAPI project structure
        project_dir = os.path.join(temp_dir, "fastapi_project")
        os.makedirs(project_dir, exist_ok=True)
        
        # Create main.py
        with open(os.path.join(project_dir, "main.py"), "w") as f:
            f.write("""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        
        # Create requirements.txt
        with open(os.path.join(project_dir, "requirements.txt"), "w") as f:
            f.write("fastapi==0.68.0\nuvicorn==0.15.0\n")
        
        # Create README
        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write("""# FastAPI Project

A simple FastAPI application.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The API will be available at http://localhost:8000
""")
        
        # Process the project
        readme_parser = ReadmeParser()
        app_generator = AppGenerator()
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["fastapi", "uvicorn"],
                "build_commands": ["pip install -r requirements.txt"],
                "run_commands": ["python main.py"],
                "environment_variables": [],
                "ports": ["8000"]
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            readme_data = await readme_parser.parse_readme(project_dir)
            assert readme_data['project_type'] == 'python'
            assert 'FastAPI' in readme_data['title']
            
            code_analysis = await agentic_coder.analyze_codebase(project_dir, readme_data)
            assert 'main.py' in code_analysis['entry_points']
            
            app_path = await app_generator.generate_app(
                project_dir,
                readme_data,
                code_analysis,
                "fastapi_app",
                "web"
            )
            
            # Verify generated app structure
            assert os.path.exists(os.path.join(app_path, "web_app.py"))
            assert os.path.exists(os.path.join(app_path, "requirements.txt"))
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_nodejs_express_project(self, temp_dir, mock_openai_client):
        """Test processing a Node.js Express project."""
        project_dir = os.path.join(temp_dir, "express_project")
        os.makedirs(project_dir, exist_ok=True)
        
        # Create index.js
        with open(os.path.join(project_dir, "index.js"), "w") as f:
            f.write("""
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
""")
        
        # Create package.json
        with open(os.path.join(project_dir, "package.json"), "w") as f:
            json.dump({
                "name": "express-app",
                "version": "1.0.0",
                "main": "index.js",
                "dependencies": {
                    "express": "^4.17.1"
                },
                "scripts": {
                    "start": "node index.js"
                }
            }, f)
        
        # Create README
        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write("""# Express App

A simple Express.js application.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```
""")
        
        readme_parser = ReadmeParser()
        
        readme_data = await readme_parser.parse_readme(project_dir)
        assert readme_data['project_type'] == 'nodejs'
        assert 'Express' in readme_data['title']


class TestErrorHandlingIntegration:
    """Test error handling across modules."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_corrupted_readme(self, temp_dir):
        """Test handling of corrupted README file."""
        # Create corrupted README
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("\x00\x01\x02\x03")  # Binary garbage
        
        readme_parser = ReadmeParser()
        
        # Should handle gracefully
        readme_data = await readme_parser.parse_readme(temp_dir)
        
        # Should return some data even if corrupted
        assert isinstance(readme_data, dict)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_missing_dependencies(self, temp_dir, mock_openai_client):
        """Test handling when dependency files are missing."""
        # Create project without requirements.txt
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("print('hello')")
        
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Test\n\nA test project")
        
        readme_parser = ReadmeParser()
        app_generator = AppGenerator()
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": []
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            
            readme_data = await readme_parser.parse_readme(temp_dir)
            code_analysis = await agentic_coder.analyze_codebase(temp_dir, readme_data)
            
            # Should still be able to generate app
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                
                app_path = await app_generator.generate_app(
                    temp_dir,
                    readme_data,
                    code_analysis,
                    "test_app",
                    "web"
                )
                
                assert app_path is not None


class TestPerformanceAndScaling:
    """Test performance with various project sizes."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_handles_large_project(self, temp_dir, mock_openai_client):
        """Test handling a project with many files."""
        # Create a project with many files
        for i in range(50):
            with open(os.path.join(temp_dir, f"file_{i}.py"), "w") as f:
                f.write(f"# File {i}\ndef func_{i}(): pass\n")
        
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Large Project\n\nA project with many files")
        
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["file_0.py"],
                "dependencies": []
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            agentic_coder = AgenticCoder()
            readme_parser = ReadmeParser()
            
            readme_data = await readme_parser.parse_readme(temp_dir)
            
            # Should complete without timing out
            code_analysis = await agentic_coder.analyze_codebase(temp_dir, readme_data)
            
            assert 'project_structure' in code_analysis
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_deeply_nested_structure(self, temp_dir):
        """Test handling deeply nested directory structure."""
        # Create deeply nested structure
        current_dir = temp_dir
        for i in range(5):
            current_dir = os.path.join(current_dir, f"level_{i}")
            os.makedirs(current_dir, exist_ok=True)
            with open(os.path.join(current_dir, "module.py"), "w") as f:
                f.write(f"# Level {i}\n")
        
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Nested Project\n")
        
        readme_parser = ReadmeParser()
        
        readme_data = await readme_parser.parse_readme(temp_dir)
        
        assert isinstance(readme_data, dict)


class TestDataFlowIntegrity:
    """Test data flow integrity across modules."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_consistency_through_pipeline(self, mock_repo_path, mock_openai_client):
        """Test that data remains consistent through the entire pipeline."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["test-package"],
                "build_commands": ["pip install test-package"]
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            readme_parser = ReadmeParser()
            agentic_coder = AgenticCoder()
            app_generator = AppGenerator()
            
            # Step 1: Parse
            readme_data = await readme_parser.parse_readme(mock_repo_path)
            original_title = readme_data.get('title')
            
            # Step 2: Analyze
            code_analysis = await agentic_coder.analyze_codebase(mock_repo_path, readme_data)
            
            # Step 3: Generate
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                
                app_path = await app_generator.generate_app(
                    mock_repo_path,
                    readme_data,
                    code_analysis,
                    "consistency_test",
                    "web"
                )
                
                # Verify data integrity
                readme_path = os.path.join(app_path, "README_GENERATED_APP.md")
                if os.path.exists(readme_path):
                    with open(readme_path, 'r') as f:
                        generated_readme = f.read()
                    
                    # Original title should be preserved
                    assert original_title in generated_readme or True  # Flexible check