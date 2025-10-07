"""
Unit tests for AppGenerator module
"""

import os
import shutil
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import subprocess

from src.app_generator import AppGenerator


@pytest.mark.unit
class TestAppGenerator:
    """Tests for AppGenerator class."""
    
    def test_init(self, app_generator):
        """Test AppGenerator initialization."""
        assert app_generator is not None
        assert hasattr(app_generator, 'output_dir')
        assert app_generator.output_dir == "generated_apps"
    
    def test_copy_source_code(self, app_generator, sample_repo_dir, temp_dir):
        """Test copying source code."""
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        app_generator._copy_source_code(sample_repo_dir, app_dir)
        
        # Check that files were copied
        assert os.path.exists(os.path.join(app_dir, "main.py"))
        assert os.path.exists(os.path.join(app_dir, "requirements.txt"))
        assert os.path.exists(os.path.join(app_dir, "README.md"))
    
    def test_copy_source_code_excludes_directories(self, app_generator, temp_dir):
        """Test that excluded directories are not copied."""
        # Create source directory with excluded dirs
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        
        # Create excluded directories
        for dirname in ['.git', '__pycache__', 'node_modules', 'venv']:
            dir_path = os.path.join(source_dir, dirname)
            os.makedirs(dir_path)
            with open(os.path.join(dir_path, 'test.txt'), 'w') as f:
                f.write('test')
        
        # Create normal file
        with open(os.path.join(source_dir, 'main.py'), 'w') as f:
            f.write('test')
        
        # Copy
        app_dir = os.path.join(temp_dir, "app")
        os.makedirs(app_dir)
        app_generator._copy_source_code(source_dir, app_dir)
        
        # Check that excluded dirs are not copied
        assert not os.path.exists(os.path.join(app_dir, '.git'))
        assert not os.path.exists(os.path.join(app_dir, '__pycache__'))
        assert not os.path.exists(os.path.join(app_dir, 'node_modules'))
        assert not os.path.exists(os.path.join(app_dir, 'venv'))
        # But normal file should be copied
        assert os.path.exists(os.path.join(app_dir, 'main.py'))
    
    def test_create_executable_wrapper(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating executable wrapper."""
        wrapper = app_generator._create_executable_wrapper(
            sample_parsed_readme, 
            sample_code_analysis
        )
        
        assert isinstance(wrapper, str)
        assert len(wrapper) > 0
        assert 'AppWrapper' in wrapper
        assert 'python' in wrapper.lower()
    
    def test_create_dockerfile_python(self, app_generator, sample_code_analysis):
        """Test creating Dockerfile for Python project."""
        readme_data = {'project_type': 'python'}
        
        dockerfile = app_generator._create_dockerfile(readme_data, sample_code_analysis)
        
        assert isinstance(dockerfile, str)
        assert 'FROM python' in dockerfile
        assert 'requirements.txt' in dockerfile
        assert 'pip install' in dockerfile
    
    def test_create_dockerfile_nodejs(self, app_generator, sample_code_analysis):
        """Test creating Dockerfile for Node.js project."""
        readme_data = {'project_type': 'nodejs'}
        
        dockerfile = app_generator._create_dockerfile(readme_data, sample_code_analysis)
        
        assert isinstance(dockerfile, str)
        assert 'FROM node' in dockerfile
        assert 'package.json' in dockerfile
        assert 'npm install' in dockerfile
    
    def test_create_dockerfile_generic(self, app_generator, sample_code_analysis):
        """Test creating generic Dockerfile."""
        readme_data = {'project_type': 'unknown'}
        
        dockerfile = app_generator._create_dockerfile(readme_data, sample_code_analysis)
        
        assert isinstance(dockerfile, str)
        assert 'FROM ubuntu' in dockerfile
    
    def test_create_docker_compose(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating docker-compose.yml."""
        compose = app_generator._create_docker_compose(
            sample_parsed_readme, 
            sample_code_analysis, 
            'test_app'
        )
        
        assert isinstance(compose, str)
        assert 'version:' in compose
        assert 'services:' in compose
        assert 'test_app:' in compose
        assert 'ports:' in compose
    
    def test_create_docker_startup_script_python(self, app_generator, sample_code_analysis):
        """Test creating startup script for Python."""
        readme_data = {'project_type': 'python'}
        
        script = app_generator._create_docker_startup_script(readme_data, sample_code_analysis)
        
        assert isinstance(script, str)
        assert '#!/bin/bash' in script
        assert 'python' in script.lower()
        assert 'requirements.txt' in script
    
    def test_create_docker_startup_script_nodejs(self, app_generator, sample_code_analysis):
        """Test creating startup script for Node.js."""
        readme_data = {'project_type': 'nodejs'}
        
        script = app_generator._create_docker_startup_script(readme_data, sample_code_analysis)
        
        assert isinstance(script, str)
        assert 'npm install' in script
        assert 'npm start' in script
    
    def test_create_web_wrapper(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating web wrapper."""
        wrapper = app_generator._create_web_wrapper(sample_parsed_readme, sample_code_analysis)
        
        assert isinstance(wrapper, str)
        assert 'FastAPI' in wrapper
        assert '@app.get' in wrapper
        assert '@app.post' in wrapper
    
    def test_create_html_template(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating HTML template."""
        html = app_generator._create_html_template(sample_parsed_readme, sample_code_analysis)
        
        assert isinstance(html, str)
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
        assert 'Test Project' in html
    
    def test_create_build_script(self, app_generator):
        """Test creating build script."""
        script = app_generator._create_build_script('test_app')
        
        assert isinstance(script, str)
        assert 'PyInstaller' in script
        assert 'test_app' in script
    
    def test_extract_requirements(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test extracting requirements."""
        requirements = app_generator._extract_requirements(
            sample_parsed_readme, 
            sample_code_analysis
        )
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
    
    def test_extract_requirements_removes_duplicates(self, app_generator):
        """Test that duplicate requirements are removed."""
        readme_data = {
            'dependencies': {
                'packages': ['requests', 'pyyaml', 'requests']
            }
        }
        code_analysis = {
            'dependencies': ['pyyaml', 'flask']
        }
        
        requirements = app_generator._extract_requirements(readme_data, code_analysis)
        
        assert isinstance(requirements, list)
        # Should not have duplicates
        assert len(requirements) == len(set(requirements))
        assert 'requests' in requirements
        assert 'pyyaml' in requirements
        assert 'flask' in requirements
    
    def test_create_app_readme_executable(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating app README for executable."""
        readme = app_generator._create_app_readme(
            sample_parsed_readme, 
            sample_code_analysis, 
            'executable'
        )
        
        assert isinstance(readme, str)
        assert 'Generated Application' in readme
        assert 'executable' in readme.lower()
        assert 'How to Use' in readme
    
    def test_create_app_readme_docker(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating app README for Docker."""
        readme = app_generator._create_app_readme(
            sample_parsed_readme, 
            sample_code_analysis, 
            'docker'
        )
        
        assert isinstance(readme, str)
        assert 'docker-compose' in readme.lower()
    
    def test_create_app_readme_web(self, app_generator, sample_parsed_readme, sample_code_analysis):
        """Test creating app README for web."""
        readme = app_generator._create_app_readme(
            sample_parsed_readme, 
            sample_code_analysis, 
            'web'
        )
        
        assert isinstance(readme, str)
        assert 'localhost:8000' in readme


@pytest.mark.unit
class TestAppGeneratorGeneration:
    """Tests for app generation workflows."""
    
    @pytest.mark.asyncio
    async def test_generate_executable(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test generating executable app."""
        app_generator.output_dir = temp_dir
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        # Mock subprocess to avoid actual build
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)  # Simulate build failure
            
            result = await app_generator._generate_executable(
                app_dir,
                sample_parsed_readme,
                sample_code_analysis,
                'test_app'
            )
        
        assert result is not None
        # Should create wrapper script
        assert os.path.exists(os.path.join(app_dir, 'test_app_wrapper.py'))
        # Should create requirements.txt
        assert os.path.exists(os.path.join(app_dir, 'requirements.txt'))
        # Should create build script
        assert os.path.exists(os.path.join(app_dir, 'build.py'))
        # Should create README
        assert os.path.exists(os.path.join(app_dir, 'README_GENERATED_APP.md'))
    
    @pytest.mark.asyncio
    async def test_generate_docker(self, app_generator, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test generating Docker app."""
        app_generator.output_dir = temp_dir
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        result = await app_generator._generate_docker(
            app_dir,
            sample_parsed_readme,
            sample_code_analysis,
            'test_app'
        )
        
        assert result is not None
        # Should create Dockerfile
        assert os.path.exists(os.path.join(app_dir, 'Dockerfile'))
        # Should create docker-compose.yml
        assert os.path.exists(os.path.join(app_dir, 'docker-compose.yml'))
        # Should create startup script
        assert os.path.exists(os.path.join(app_dir, 'start.sh'))
        # Should create README
        assert os.path.exists(os.path.join(app_dir, 'README_GENERATED_APP.md'))
    
    @pytest.mark.asyncio
    async def test_generate_web_app(self, app_generator, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test generating web app."""
        app_generator.output_dir = temp_dir
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        result = await app_generator._generate_web_app(
            app_dir,
            sample_parsed_readme,
            sample_code_analysis,
            'test_app'
        )
        
        assert result is not None
        # Should create web wrapper
        assert os.path.exists(os.path.join(app_dir, 'web_app.py'))
        # Should create templates directory
        assert os.path.exists(os.path.join(app_dir, 'templates'))
        assert os.path.exists(os.path.join(app_dir, 'templates', 'index.html'))
        # Should create static directory
        assert os.path.exists(os.path.join(app_dir, 'static'))
        # Should create requirements.txt
        assert os.path.exists(os.path.join(app_dir, 'requirements.txt'))
        # Should create README
        assert os.path.exists(os.path.join(app_dir, 'README_GENERATED_APP.md'))
    
    @pytest.mark.asyncio
    async def test_generate_app_executable(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test full app generation for executable."""
        app_generator.output_dir = temp_dir
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            
            result = await app_generator.generate_app(
                sample_repo_dir,
                sample_parsed_readme,
                sample_code_analysis,
                'test_app',
                'executable'
            )
        
        assert result is not None
        assert os.path.exists(result)
    
    @pytest.mark.asyncio
    async def test_generate_app_docker(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test full app generation for Docker."""
        app_generator.output_dir = temp_dir
        
        result = await app_generator.generate_app(
            sample_repo_dir,
            sample_parsed_readme,
            sample_code_analysis,
            'test_app',
            'docker'
        )
        
        assert result is not None
        assert os.path.exists(result)
    
    @pytest.mark.asyncio
    async def test_generate_app_web(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test full app generation for web."""
        app_generator.output_dir = temp_dir
        
        result = await app_generator.generate_app(
            sample_repo_dir,
            sample_parsed_readme,
            sample_code_analysis,
            'test_app',
            'web'
        )
        
        assert result is not None
        assert os.path.exists(result)
    
    @pytest.mark.asyncio
    async def test_generate_app_unsupported_platform(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test generating app with unsupported platform."""
        app_generator.output_dir = temp_dir
        
        with pytest.raises(Exception, match="Unsupported target platform"):
            await app_generator.generate_app(
                sample_repo_dir,
                sample_parsed_readme,
                sample_code_analysis,
                'test_app',
                'invalid_platform'
            )
    
    @pytest.mark.asyncio
    async def test_generate_app_replaces_existing(self, app_generator, sample_repo_dir, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test that existing app directory is replaced."""
        app_generator.output_dir = temp_dir
        
        # Create existing app directory
        existing_dir = os.path.join(temp_dir, 'test_app')
        os.makedirs(existing_dir)
        with open(os.path.join(existing_dir, 'old_file.txt'), 'w') as f:
            f.write('old content')
        
        result = await app_generator.generate_app(
            sample_repo_dir,
            sample_parsed_readme,
            sample_code_analysis,
            'test_app',
            'web'
        )
        
        assert result is not None
        # Old file should not exist
        assert not os.path.exists(os.path.join(existing_dir, 'old_file.txt'))


@pytest.mark.unit
class TestAppGeneratorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_copy_source_code_empty_directory(self, app_generator, temp_dir):
        """Test copying from empty directory."""
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        
        app_dir = os.path.join(temp_dir, "app")
        os.makedirs(app_dir)
        
        # Should not raise error
        app_generator._copy_source_code(source_dir, app_dir)
    
    def test_create_executable_wrapper_minimal_data(self, app_generator):
        """Test creating wrapper with minimal data."""
        readme_data = {}
        code_analysis = {}
        
        wrapper = app_generator._create_executable_wrapper(readme_data, code_analysis)
        
        assert isinstance(wrapper, str)
        assert len(wrapper) > 0
    
    def test_extract_requirements_empty_data(self, app_generator):
        """Test extracting requirements with no data."""
        requirements = app_generator._extract_requirements({}, {})
        
        assert isinstance(requirements, list)
        assert len(requirements) == 0
    
    def test_extract_requirements_filters_empty_strings(self, app_generator):
        """Test that empty requirement strings are filtered out."""
        readme_data = {
            'dependencies': {
                'packages': ['requests', '', '  ', 'flask']
            }
        }
        code_analysis = {}
        
        requirements = app_generator._extract_requirements(readme_data, code_analysis)
        
        assert '' not in requirements
        assert '  ' not in requirements
        assert 'requests' in requirements
        assert 'flask' in requirements
    
    @pytest.mark.asyncio
    async def test_generate_executable_build_success(self, app_generator, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test executable generation with successful build."""
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        # Mock successful build
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Mock executable file
            with patch('os.listdir') as mock_listdir:
                mock_listdir.return_value = ['test_app.exe']
                with patch('os.path.isfile', return_value=True):
                    with patch('os.access', return_value=True):
                        result = await app_generator._generate_executable(
                            app_dir,
                            sample_parsed_readme,
                            sample_code_analysis,
                            'test_app'
                        )
        
        # Should return path to executable
        assert 'test_app.exe' in result or app_dir in result
    
    @pytest.mark.asyncio
    async def test_generate_executable_build_timeout(self, app_generator, sample_parsed_readme, sample_code_analysis, temp_dir):
        """Test executable generation with build timeout."""
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        # Mock timeout
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('python', 300)
            
            result = await app_generator._generate_executable(
                app_dir,
                sample_parsed_readme,
                sample_code_analysis,
                'test_app'
            )
        
        # Should still return app directory
        assert result == app_dir
    
    @pytest.mark.asyncio
    async def test_generate_app_error_handling(self, app_generator, temp_dir):
        """Test error handling in app generation."""
        app_generator.output_dir = temp_dir
        
        # Use non-existent repo path
        with pytest.raises(Exception, match="Failed to generate app"):
            await app_generator.generate_app(
                '/nonexistent/path',
                {},
                {},
                'test_app',
                'web'
            )