"""
Unit Tests for AgenticCoder Module

Tests AI-powered code analysis including:
- Codebase analysis
- App wrapper generation
- Project structure analysis
- Entry point identification
- OpenAI API integration
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path

from src.agentic_coder import AgenticCoder


class TestAgenticCoderInitialization:
    """Test AgenticCoder initialization."""
    
    def test_coder_initialization(self, mock_env_vars):
        """Test that AgenticCoder initializes correctly."""
        with patch('openai.OpenAI'):
            coder = AgenticCoder()
            
            assert coder is not None
            assert hasattr(coder, 'client')
            assert hasattr(coder, 'max_tokens')
            assert hasattr(coder, 'model')
    
    def test_coder_default_settings(self, mock_env_vars):
        """Test default settings are correct."""
        with patch('openai.OpenAI'):
            coder = AgenticCoder()
            
            assert coder.max_tokens == 4000
            assert coder.model == "gpt-4"
    
    def test_coder_initialization_with_api_key(self, mock_env_vars):
        """Test initialization with API key from environment."""
        with patch('openai.OpenAI') as mock_openai:
            coder = AgenticCoder()
            
            mock_openai.assert_called_once()
            # Verify API key was used
            call_kwargs = mock_openai.call_args[1]
            assert 'api_key' in call_kwargs


class TestProjectStructureAnalysis:
    """Test project structure analysis."""
    
    def test_get_project_structure(self, temp_dir):
        """Test getting project structure."""
        coder = AgenticCoder()
        
        # Create test files
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(temp_dir, "utils.py"), "w") as f:
            f.write("def helper(): pass")
        
        structure = coder._get_project_structure(temp_dir)
        
        assert 'files' in structure
        assert 'directories' in structure
        assert 'extensions' in structure
        assert 'size' in structure
        assert len(structure['files']) >= 2
    
    def test_get_project_structure_excludes_hidden(self, temp_dir):
        """Test that hidden directories are excluded."""
        coder = AgenticCoder()
        
        # Create hidden directory
        hidden_dir = os.path.join(temp_dir, ".git")
        os.makedirs(hidden_dir, exist_ok=True)
        with open(os.path.join(hidden_dir, "config"), "w") as f:
            f.write("config")
        
        # Create normal file
        with open(os.path.join(temp_dir, "app.py"), "w") as f:
            f.write("pass")
        
        structure = coder._get_project_structure(temp_dir)
        
        # Should not include .git directory
        file_paths = [f['path'] for f in structure['files']]
        assert not any('.git' in path for path in file_paths)
    
    def test_get_project_structure_excludes_common_dirs(self, temp_dir):
        """Test that common non-source directories are excluded."""
        coder = AgenticCoder()
        
        # Create excluded directories
        for excluded_dir in ['node_modules', '__pycache__', 'venv', 'build']:
            dir_path = os.path.join(temp_dir, excluded_dir)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, "file.txt"), "w") as f:
                f.write("content")
        
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("pass")
        
        structure = coder._get_project_structure(temp_dir)
        
        file_paths = [f['path'] for f in structure['files']]
        assert not any('node_modules' in path for path in file_paths)
        assert not any('__pycache__' in path for path in file_paths)
        assert any('main.py' in path for path in file_paths)
    
    def test_get_project_structure_extensions(self, temp_dir):
        """Test that file extensions are collected."""
        coder = AgenticCoder()
        
        # Create files with different extensions
        with open(os.path.join(temp_dir, "file.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(temp_dir, "file.js"), "w") as f:
            f.write("console.log();")
        with open(os.path.join(temp_dir, "file.txt"), "w") as f:
            f.write("text")
        
        structure = coder._get_project_structure(temp_dir)
        
        assert '.py' in structure['extensions']
        assert '.js' in structure['extensions']
        assert '.txt' in structure['extensions']
    
    def test_get_project_structure_total_size(self, temp_dir):
        """Test that total size is calculated."""
        coder = AgenticCoder()
        
        # Create files
        with open(os.path.join(temp_dir, "file1.py"), "w") as f:
            f.write("a" * 100)  # 100 bytes
        with open(os.path.join(temp_dir, "file2.py"), "w") as f:
            f.write("b" * 200)  # 200 bytes
        
        structure = coder._get_project_structure(temp_dir)
        
        assert structure['size'] >= 300  # At least 300 bytes


class TestKeyFileReading:
    """Test reading key files for analysis."""
    
    def test_read_key_files_important_files(self, temp_dir):
        """Test reading important files."""
        coder = AgenticCoder()
        
        # Create important files
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("def main(): pass")
        with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
            f.write("fastapi\nuvicorn")
        
        project_files = {'files': [
            {'path': 'main.py', 'size': 100, 'extension': '.py'},
            {'path': 'requirements.txt', 'size': 50, 'extension': '.txt'}
        ]}
        
        key_files = coder._read_key_files(temp_dir, project_files)
        
        assert 'main.py' in key_files
        assert 'requirements.txt' in key_files
        assert 'def main' in key_files['main.py']
    
    def test_read_key_files_size_limit(self, temp_dir):
        """Test that large files are truncated."""
        coder = AgenticCoder()
        
        # Create a file larger than 5000 bytes
        large_content = "x" * 10000
        with open(os.path.join(temp_dir, "large.py"), "w") as f:
            f.write(large_content)
        
        project_files = {'files': [
            {'path': 'large.py', 'size': 500, 'extension': '.py'}  # Size below threshold
        ]}
        
        key_files = coder._read_key_files(temp_dir, project_files)
        
        # Content should be truncated to 5000 bytes
        if 'large.py' in key_files:
            assert len(key_files['large.py']) <= 5000
    
    def test_read_key_files_error_handling(self, temp_dir):
        """Test error handling when file can't be read."""
        coder = AgenticCoder()
        
        # Reference a file that doesn't exist
        project_files = {'files': [
            {'path': 'nonexistent.py', 'size': 100, 'extension': '.py'}
        ]}
        
        key_files = coder._read_key_files(temp_dir, project_files)
        
        # Should handle gracefully
        if 'nonexistent.py' in key_files:
            assert 'Error reading file' in key_files['nonexistent.py']
    
    def test_read_key_files_skips_large_files(self, temp_dir):
        """Test that very large files are skipped."""
        coder = AgenticCoder()
        
        project_files = {'files': [
            {'path': 'huge.py', 'size': 100000, 'extension': '.py'},  # 100KB
            {'path': 'small.py', 'size': 100, 'extension': '.py'}
        ]}
        
        with open(os.path.join(temp_dir, "small.py"), "w") as f:
            f.write("pass")
        
        key_files = coder._read_key_files(temp_dir, project_files)
        
        # Large file should be skipped
        assert 'huge.py' not in key_files or len(key_files) <= 1


class TestEntryPointIdentification:
    """Test identifying entry points."""
    
    def test_identify_entry_points_main_py(self):
        """Test identifying main.py as entry point."""
        coder = AgenticCoder()
        
        key_files = {
            'main.py': 'def main(): pass',
            'utils.py': 'def helper(): pass'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        assert 'main.py' in entry_points
    
    def test_identify_entry_points_if_main(self):
        """Test identifying file with if __name__ == "__main__"."""
        coder = AgenticCoder()
        
        key_files = {
            'run.py': 'if __name__ == "__main__":\n    main()',
            'utils.py': 'def helper(): pass'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        assert 'run.py' in entry_points
    
    def test_identify_entry_points_def_main(self):
        """Test identifying file with def main() function."""
        coder = AgenticCoder()
        
        key_files = {
            'app.py': 'def main():\n    print("hello")',
            'config.py': 'DEBUG = True'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        assert 'app.py' in entry_points
    
    def test_identify_entry_points_nodejs(self):
        """Test identifying Node.js entry points."""
        coder = AgenticCoder()
        
        key_files = {
            'index.js': 'console.log("hello");',
            'package.json': '{"main": "index.js"}'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        assert 'index.js' in entry_points
        assert 'package.json' in entry_points
    
    def test_identify_entry_points_multiple(self):
        """Test identifying multiple entry points."""
        coder = AgenticCoder()
        
        key_files = {
            'main.py': 'if __name__ == "__main__":\n    pass',
            'app.py': 'def main(): pass',
            'utils.py': 'def helper(): pass'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        assert len(entry_points) >= 2
        assert 'main.py' in entry_points
        assert 'app.py' in entry_points
    
    def test_identify_entry_points_no_duplicates(self):
        """Test that entry points are unique."""
        coder = AgenticCoder()
        
        key_files = {
            'main.py': 'if __name__ == "__main__":\n    def main(): pass'
        }
        
        entry_points = coder._identify_entry_points(key_files)
        
        # Should only appear once even though it has both patterns
        assert entry_points.count('main.py') == 1


class TestAIAnalysisPrompts:
    """Test AI analysis prompt creation."""
    
    def test_create_analysis_prompt(self, sample_readme_data):
        """Test creating analysis prompt."""
        coder = AgenticCoder()
        
        project_files = {
            'files': [{'path': 'main.py', 'size': 100, 'extension': '.py'}],
            'extensions': ['.py'],
            'size': 100
        }
        
        key_files = {'main.py': 'def main(): pass'}
        
        prompt = coder._create_analysis_prompt(sample_readme_data, project_files, key_files)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'Test Project' in prompt
        assert 'main.py' in prompt
        assert 'JSON' in prompt  # Should ask for JSON response
    
    def test_create_generation_prompt(self, sample_code_analysis):
        """Test creating generation prompt."""
        coder = AgenticCoder()
        
        prompt = coder._create_generation_prompt(sample_code_analysis, 'executable')
        
        assert isinstance(prompt, str)
        assert 'executable' in prompt
        assert 'wrapper' in prompt.lower()


class TestDependencyExtraction:
    """Test extracting dependencies from analysis."""
    
    def test_extract_ai_dependencies_with_deps(self):
        """Test extracting dependencies when present."""
        coder = AgenticCoder()
        
        analysis = {
            'dependencies': ['fastapi', 'uvicorn', 'requests']
        }
        
        deps = coder._extract_ai_dependencies(analysis)
        
        assert deps == ['fastapi', 'uvicorn', 'requests']
    
    def test_extract_ai_dependencies_without_deps(self):
        """Test extracting dependencies when not present."""
        coder = AgenticCoder()
        
        analysis = {'other': 'data'}
        
        deps = coder._extract_ai_dependencies(analysis)
        
        assert deps == []
    
    def test_extract_ai_dependencies_invalid_input(self):
        """Test with invalid input."""
        coder = AgenticCoder()
        
        deps = coder._extract_ai_dependencies("not a dict")
        
        assert deps == []


class TestBuildInstructionsExtraction:
    """Test extracting build instructions."""
    
    def test_extract_build_instructions_with_commands(self):
        """Test extracting build commands when present."""
        coder = AgenticCoder()
        
        analysis = {
            'build_commands': ['pip install -r requirements.txt', 'npm install']
        }
        
        commands = coder._extract_build_instructions(analysis)
        
        assert len(commands) == 2
        assert 'pip install' in commands[0]
    
    def test_extract_build_instructions_without_commands(self):
        """Test extracting when no commands present."""
        coder = AgenticCoder()
        
        analysis = {'other': 'data'}
        
        commands = coder._extract_build_instructions(analysis)
        
        assert commands == []


class TestRuntimeRequirementsExtraction:
    """Test extracting runtime requirements."""
    
    def test_extract_runtime_requirements_complete(self):
        """Test extracting complete runtime requirements."""
        coder = AgenticCoder()
        
        analysis = {
            'environment_variables': ['API_KEY', 'DEBUG'],
            'ports': ['8000', '3000'],
            'special_requirements': ['Docker', 'Redis']
        }
        
        requirements = coder._extract_runtime_requirements(analysis)
        
        assert 'environment_variables' in requirements
        assert 'ports' in requirements
        assert 'special_requirements' in requirements
        assert requirements['environment_variables'] == ['API_KEY', 'DEBUG']
        assert requirements['ports'] == ['8000', '3000']
    
    def test_extract_runtime_requirements_partial(self):
        """Test extracting with partial data."""
        coder = AgenticCoder()
        
        analysis = {
            'ports': ['8000']
        }
        
        requirements = coder._extract_runtime_requirements(analysis)
        
        assert requirements['ports'] == ['8000']
        assert requirements['environment_variables'] == []
        assert requirements['special_requirements'] == []
    
    def test_extract_runtime_requirements_empty(self):
        """Test extracting with no data."""
        coder = AgenticCoder()
        
        analysis = {}
        
        requirements = coder._extract_runtime_requirements(analysis)
        
        # When empty, returns dict with empty lists
        assert isinstance(requirements, dict)
        assert requirements.get('environment_variables', []) == []
        assert requirements.get('ports', []) == []
        assert requirements.get('special_requirements', []) == []


class TestAIAnalysis:
    """Test AI analysis functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_analysis_success(self, mock_openai_client, mock_openai_response):
        """Test successful AI analysis."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_openai_class.return_value = mock_openai_client
            coder = AgenticCoder()
            
            prompt = "Analyze this code"
            result = await coder._get_ai_analysis(prompt)
            
            assert isinstance(result, dict)
            mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_analysis_json_parsing(self, mock_openai_client):
        """Test JSON parsing in AI analysis."""
        with patch('openai.OpenAI') as mock_openai_class:
            # Create mock response with valid JSON
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"key": "value", "number": 42}'
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder._get_ai_analysis("test prompt")
            
            assert result == {"key": "value", "number": 42}
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_analysis_non_json_response(self, mock_openai_client):
        """Test handling non-JSON response."""
        with patch('openai.OpenAI') as mock_openai_class:
            # Create mock response with non-JSON content
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "This is plain text, not JSON"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder._get_ai_analysis("test prompt")
            
            assert 'analysis' in result
            assert result['analysis'] == "This is plain text, not JSON"
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_analysis_api_error(self, mock_openai_client):
        """Test handling API errors."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder._get_ai_analysis("test prompt")
            
            assert 'error' in result
            assert 'API Error' in result['error']


class TestAIGeneration:
    """Test AI code generation functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_generation_success(self, mock_openai_client):
        """Test successful code generation."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "# Generated code\nprint('hello')"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder._get_ai_generation("Generate code")
            
            assert isinstance(result, str)
            assert "Generated code" in result
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_ai_generation_error(self, mock_openai_client):
        """Test handling generation errors."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Generation failed")
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder._get_ai_generation("Generate code")
            
            assert '# Error generating code' in result


class TestCodebaseAnalysis:
    """Test complete codebase analysis."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_analyze_codebase_success(self, mock_repo_path, sample_readme_data, mock_openai_client):
        """Test successful codebase analysis."""
        with patch('openai.OpenAI') as mock_openai_class:
            # Mock successful API response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entry_points": ["main.py"],
                "dependencies": ["fastapi"],
                "build_commands": ["pip install -r requirements.txt"]
            })
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder.analyze_codebase(mock_repo_path, sample_readme_data)
            
            assert 'project_structure' in result
            assert 'ai_analysis' in result
            assert 'entry_points' in result
            assert 'dependencies' in result
    
    @pytest.mark.asyncio
    async def test_analyze_codebase_error_handling(self, temp_dir, sample_readme_data):
        """Test error handling in codebase analysis."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder.analyze_codebase(temp_dir, sample_readme_data)
            
            # Error is nested in ai_analysis
            assert 'ai_analysis' in result
            assert 'error' in result['ai_analysis']


class TestAppWrapperGeneration:
    """Test app wrapper generation."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_generate_app_wrapper_executable(self, sample_code_analysis, mock_openai_client):
        """Test generating executable wrapper."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "#!/usr/bin/env python\n# Wrapper code"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder.generate_app_wrapper(sample_code_analysis, 'executable')
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_generate_app_wrapper_docker(self, sample_code_analysis, mock_openai_client):
        """Test generating Docker wrapper."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "FROM python:3.9\n# Docker config"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder.generate_app_wrapper(sample_code_analysis, 'docker')
            
            assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_generate_app_wrapper_error(self, sample_code_analysis):
        """Test error handling in wrapper generation."""
        with patch('openai.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Generation failed")
            mock_openai_class.return_value = mock_client
            
            coder = AgenticCoder()
            result = await coder.generate_app_wrapper(sample_code_analysis, 'executable')
            
            # Check for error message (could be "code" or "wrapper")
            assert '# Error generating' in result
            assert 'Generation failed' in result