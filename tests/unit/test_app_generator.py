"""
Unit Tests for AppGenerator Module

Tests application generation including:
- Executable generation
- Docker container generation
- Web app generation
- Source code copying
- Configuration file creation
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from src.app_generator import AppGenerator


class TestAppGeneratorInitialization:
    """Test AppGenerator initialization."""
    
    def test_generator_initialization(self):
        """Test that AppGenerator initializes correctly."""
        generator = AppGenerator()
        
        assert generator is not None
        assert hasattr(generator, 'output_dir')
        assert generator.output_dir == "generated_apps"
    
    def test_output_directory_created(self):
        """Test that output directory is created."""
        generator = AppGenerator()
        
        assert os.path.exists(generator.output_dir)
        assert os.path.isdir(generator.output_dir)


class TestSourceCodeCopying:
    """Test source code copying functionality."""
    
    def test_copy_source_code_basic(self, temp_dir):
        """Test basic source code copying."""
        generator = AppGenerator()
        
        # Create source files
        src_dir = temp_dir
        with open(os.path.join(src_dir, "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(src_dir, "utils.py"), "w") as f:
            f.write("def helper(): pass")
        
        # Create destination
        dst_dir = os.path.join(temp_dir, "output")
        os.makedirs(dst_dir, exist_ok=True)
        
        generator._copy_source_code(src_dir, dst_dir)
        
        assert os.path.exists(os.path.join(dst_dir, "main.py"))
        assert os.path.exists(os.path.join(dst_dir, "utils.py"))
    
    def test_copy_source_code_subdirectories(self, temp_dir):
        """Test copying with subdirectories."""
        generator = AppGenerator()
        
        # Create subdirectory structure
        src_dir = temp_dir
        sub_dir = os.path.join(src_dir, "src")
        os.makedirs(sub_dir, exist_ok=True)
        
        with open(os.path.join(sub_dir, "module.py"), "w") as f:
            f.write("pass")
        
        dst_dir = os.path.join(temp_dir, "output")
        os.makedirs(dst_dir, exist_ok=True)
        
        generator._copy_source_code(src_dir, dst_dir)
        
        assert os.path.exists(os.path.join(dst_dir, "src", "module.py"))
    
    def test_copy_source_code_excludes_git(self, temp_dir):
        """Test that .git directory is excluded."""
        generator = AppGenerator()
        
        # Create .git directory
        src_dir = temp_dir
        git_dir = os.path.join(src_dir, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "config"), "w") as f:
            f.write("config")
        
        with open(os.path.join(src_dir, "main.py"), "w") as f:
            f.write("pass")
        
        dst_dir = os.path.join(temp_dir, "output")
        os.makedirs(dst_dir, exist_ok=True)
        
        generator._copy_source_code(src_dir, dst_dir)
        
        assert not os.path.exists(os.path.join(dst_dir, ".git"))
        assert os.path.exists(os.path.join(dst_dir, "main.py"))
    
    def test_copy_source_code_excludes_node_modules(self, temp_dir):
        """Test that node_modules is excluded."""
        generator = AppGenerator()
        
        src_dir = temp_dir
        node_dir = os.path.join(src_dir, "node_modules")
        os.makedirs(node_dir, exist_ok=True)
        with open(os.path.join(node_dir, "package.js"), "w") as f:
            f.write("module")
        
        dst_dir = os.path.join(temp_dir, "output")
        os.makedirs(dst_dir, exist_ok=True)
        
        generator._copy_source_code(src_dir, dst_dir)
        
        assert not os.path.exists(os.path.join(dst_dir, "node_modules"))
    
    def test_copy_source_code_excludes_pycache(self, temp_dir):
        """Test that __pycache__ is excluded."""
        generator = AppGenerator()
        
        src_dir = temp_dir
        cache_dir = os.path.join(src_dir, "__pycache__")
        os.makedirs(cache_dir, exist_ok=True)
        with open(os.path.join(cache_dir, "cache.pyc"), "w") as f:
            f.write("cache")
        
        dst_dir = os.path.join(temp_dir, "output")
        os.makedirs(dst_dir, exist_ok=True)
        
        generator._copy_source_code(src_dir, dst_dir)
        
        assert not os.path.exists(os.path.join(dst_dir, "__pycache__"))


class TestRequirementsExtraction:
    """Test requirements extraction."""
    
    def test_extract_requirements_from_readme(self, sample_readme_data, sample_code_analysis):
        """Test extracting requirements from README data."""
        generator = AppGenerator()
        
        requirements = generator._extract_requirements(sample_readme_data, sample_code_analysis)
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
    
    def test_extract_requirements_from_analysis(self, sample_readme_data, sample_code_analysis):
        """Test extracting requirements from code analysis."""
        generator = AppGenerator()
        
        requirements = generator._extract_requirements(sample_readme_data, sample_code_analysis)
        
        # Should include dependencies from analysis
        assert any('fastapi' in req.lower() or 'uvicorn' in req.lower() for req in requirements)
    
    def test_extract_requirements_removes_duplicates(self):
        """Test that duplicate requirements are removed."""
        generator = AppGenerator()
        
        readme_data = {
            'dependencies': {
                'packages': ['fastapi', 'uvicorn', 'fastapi']
            }
        }
        
        code_analysis = {
            'dependencies': ['uvicorn', 'requests']
        }
        
        requirements = generator._extract_requirements(readme_data, code_analysis)
        
        # Should be unique
        assert len(requirements) == len(set(requirements))
    
    def test_extract_requirements_empty_data(self):
        """Test with empty data."""
        generator = AppGenerator()
        
        requirements = generator._extract_requirements({}, {})
        
        assert isinstance(requirements, list)


class TestExecutableWrapperCreation:
    """Test executable wrapper creation."""
    
    def test_create_executable_wrapper_python(self, sample_readme_data, sample_code_analysis):
        """Test creating executable wrapper for Python project."""
        generator = AppGenerator()
        
        wrapper = generator._create_executable_wrapper(sample_readme_data, sample_code_analysis)
        
        assert isinstance(wrapper, str)
        assert '#!/usr/bin/env python' in wrapper
        assert 'class AppWrapper' in wrapper
        assert 'def run_application' in wrapper
    
    def test_create_executable_wrapper_includes_entry_points(self, sample_readme_data, sample_code_analysis):
        """Test that entry points are included in wrapper."""
        generator = AppGenerator()
        
        wrapper = generator._create_executable_wrapper(sample_readme_data, sample_code_analysis)
        
        # Should reference entry points
        assert 'main.py' in wrapper or 'entry_point' in wrapper.lower()
    
    def test_create_executable_wrapper_install_dependencies(self, sample_readme_data, sample_code_analysis):
        """Test that wrapper includes dependency installation."""
        generator = AppGenerator()
        
        wrapper = generator._create_executable_wrapper(sample_readme_data, sample_code_analysis)
        
        assert 'install_dependencies' in wrapper
        assert 'pip install' in wrapper or 'requirements.txt' in wrapper


class TestDockerfileCreation:
    """Test Dockerfile creation."""
    
    def test_create_dockerfile_python(self):
        """Test creating Dockerfile for Python project."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'python'}
        code_analysis = {}
        
        dockerfile = generator._create_dockerfile(readme_data, code_analysis)
        
        assert isinstance(dockerfile, str)
        assert 'FROM python' in dockerfile
        assert 'WORKDIR /app' in dockerfile
        assert 'COPY' in dockerfile
        assert 'CMD' in dockerfile
    
    def test_create_dockerfile_nodejs(self):
        """Test creating Dockerfile for Node.js project."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'nodejs'}
        code_analysis = {}
        
        dockerfile = generator._create_dockerfile(readme_data, code_analysis)
        
        assert 'FROM node' in dockerfile
        assert 'npm install' in dockerfile
    
    def test_create_dockerfile_includes_requirements(self):
        """Test that Dockerfile copies requirements file."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'python'}
        code_analysis = {}
        
        dockerfile = generator._create_dockerfile(readme_data, code_analysis)
        
        assert 'requirements.txt' in dockerfile
        assert 'pip install' in dockerfile
    
    def test_create_dockerfile_exposes_port(self):
        """Test that Dockerfile exposes port."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'python'}
        code_analysis = {}
        
        dockerfile = generator._create_dockerfile(readme_data, code_analysis)
        
        assert 'EXPOSE' in dockerfile


class TestDockerComposeCreation:
    """Test docker-compose.yml creation."""
    
    def test_create_docker_compose(self):
        """Test creating docker-compose.yml."""
        generator = AppGenerator()
        
        readme_data = {}
        code_analysis = {}
        app_name = "test_app"
        
        compose = generator._create_docker_compose(readme_data, code_analysis, app_name)
        
        assert isinstance(compose, str)
        assert 'version:' in compose
        assert 'services:' in compose
        assert app_name in compose
        assert 'ports:' in compose
    
    def test_create_docker_compose_includes_build(self):
        """Test that docker-compose includes build configuration."""
        generator = AppGenerator()
        
        compose = generator._create_docker_compose({}, {}, "myapp")
        
        assert 'build:' in compose
    
    def test_create_docker_compose_includes_volumes(self):
        """Test that docker-compose includes volumes."""
        generator = AppGenerator()
        
        compose = generator._create_docker_compose({}, {}, "myapp")
        
        assert 'volumes:' in compose


class TestDockerStartupScript:
    """Test Docker startup script creation."""
    
    def test_create_docker_startup_python(self):
        """Test creating startup script for Python."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'python'}
        code_analysis = {}
        
        script = generator._create_docker_startup_script(readme_data, code_analysis)
        
        assert isinstance(script, str)
        assert '#!/bin/bash' in script
        assert 'python' in script
    
    def test_create_docker_startup_nodejs(self):
        """Test creating startup script for Node.js."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'nodejs'}
        code_analysis = {}
        
        script = generator._create_docker_startup_script(readme_data, code_analysis)
        
        assert 'npm install' in script
        assert 'npm start' in script
    
    def test_create_docker_startup_installs_deps(self):
        """Test that startup script installs dependencies."""
        generator = AppGenerator()
        
        readme_data = {'project_type': 'python'}
        script = generator._create_docker_startup_script(readme_data, {})
        
        assert 'pip install' in script or 'requirements.txt' in script


class TestWebWrapperCreation:
    """Test web wrapper creation."""
    
    def test_create_web_wrapper(self):
        """Test creating web application wrapper."""
        generator = AppGenerator()
        
        readme_data = {}
        code_analysis = {}
        
        wrapper = generator._create_web_wrapper(readme_data, code_analysis)
        
        assert isinstance(wrapper, str)
        assert 'from fastapi import FastAPI' in wrapper
        assert '@app.get' in wrapper
        assert '@app.post' in wrapper
    
    def test_create_web_wrapper_includes_routes(self):
        """Test that web wrapper includes necessary routes."""
        generator = AppGenerator()
        
        wrapper = generator._create_web_wrapper({}, {})
        
        assert 'def home' in wrapper or '@app.get("/")' in wrapper
        assert 'def run_application' in wrapper or '/run' in wrapper
    
    def test_create_web_wrapper_includes_templates(self):
        """Test that web wrapper includes template rendering."""
        generator = AppGenerator()
        
        wrapper = generator._create_web_wrapper({}, {})
        
        assert 'templates' in wrapper.lower() or 'jinja2' in wrapper.lower()


class TestHTMLTemplateCreation:
    """Test HTML template creation."""
    
    def test_create_html_template(self, sample_readme_data):
        """Test creating HTML template."""
        generator = AppGenerator()
        
        html = generator._create_html_template(sample_readme_data, {})
        
        assert isinstance(html, str)
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
        assert '</html>' in html
    
    def test_create_html_template_includes_title(self, sample_readme_data):
        """Test that template includes project title."""
        generator = AppGenerator()
        
        html = generator._create_html_template(sample_readme_data, {})
        
        assert sample_readme_data['title'] in html
    
    def test_create_html_template_includes_description(self, sample_readme_data):
        """Test that template includes project description."""
        generator = AppGenerator()
        
        html = generator._create_html_template(sample_readme_data, {})
        
        assert sample_readme_data['description'] in html
    
    def test_create_html_template_includes_run_button(self):
        """Test that template includes run button."""
        generator = AppGenerator()
        
        html = generator._create_html_template({'title': 'Test', 'description': 'Desc'}, {})
        
        assert 'button' in html.lower()
        assert 'run' in html.lower()
    
    def test_create_html_template_includes_javascript(self):
        """Test that template includes JavaScript for interaction."""
        generator = AppGenerator()
        
        html = generator._create_html_template({'title': 'Test', 'description': 'Desc'}, {})
        
        assert '<script>' in html
        assert 'fetch' in html or 'XMLHttpRequest' in html


class TestBuildScriptCreation:
    """Test build script creation."""
    
    def test_create_build_script(self):
        """Test creating build script."""
        generator = AppGenerator()
        
        script = generator._create_build_script("test_app")
        
        assert isinstance(script, str)
        assert '#!/usr/bin/env python' in script
        assert 'PyInstaller' in script
        assert 'test_app' in script
    
    def test_create_build_script_installs_pyinstaller(self):
        """Test that build script installs PyInstaller."""
        generator = AppGenerator()
        
        script = generator._create_build_script("myapp")
        
        # Check for pip and pyinstaller (might use subprocess.run)
        assert 'pip' in script
        assert 'pyinstaller' in script.lower()


class TestAppReadmeCreation:
    """Test app README creation."""
    
    def test_create_app_readme_executable(self, sample_readme_data):
        """Test creating README for executable."""
        generator = AppGenerator()
        
        readme = generator._create_app_readme(sample_readme_data, {}, 'executable')
        
        assert isinstance(readme, str)
        assert sample_readme_data['title'] in readme
        assert 'executable' in readme.lower()
        assert 'How to Use' in readme
    
    def test_create_app_readme_docker(self, sample_readme_data):
        """Test creating README for Docker."""
        generator = AppGenerator()
        
        readme = generator._create_app_readme(sample_readme_data, {}, 'docker')
        
        assert 'docker' in readme.lower()
        assert 'docker-compose' in readme.lower()
    
    def test_create_app_readme_web(self, sample_readme_data):
        """Test creating README for web app."""
        generator = AppGenerator()
        
        readme = generator._create_app_readme(sample_readme_data, {}, 'web')
        
        assert 'web' in readme.lower()
        assert 'localhost' in readme or '8000' in readme
    
    def test_create_app_readme_includes_troubleshooting(self, sample_readme_data):
        """Test that README includes troubleshooting section."""
        generator = AppGenerator()
        
        readme = generator._create_app_readme(sample_readme_data, {}, 'executable')
        
        assert 'Troubleshooting' in readme or 'troubleshoot' in readme.lower()


class TestExecutableGeneration:
    """Test executable generation."""
    
    @pytest.mark.asyncio
    async def test_generate_executable_creates_files(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test that executable generation creates necessary files."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1)  # Build fails, but files should be created
            
            result = await generator._generate_executable(app_dir, sample_readme_data, sample_code_analysis, "test_app")
            
            # Check that wrapper was created
            wrapper_path = os.path.join(app_dir, "test_app_wrapper.py")
            assert os.path.exists(wrapper_path)
            
            # Check that requirements.txt was created
            req_path = os.path.join(app_dir, "requirements.txt")
            assert os.path.exists(req_path)
            
            # Check that build script was created
            build_path = os.path.join(app_dir, "build.py")
            assert os.path.exists(build_path)
    
    @pytest.mark.asyncio
    async def test_generate_executable_error_handling(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test error handling in executable generation."""
        generator = AppGenerator()
        
        app_dir = "/nonexistent/directory"
        
        with pytest.raises(Exception) as exc_info:
            await generator._generate_executable(app_dir, sample_readme_data, sample_code_analysis, "test_app")
        
        assert "Failed to generate executable" in str(exc_info.value)


class TestDockerGeneration:
    """Test Docker generation."""
    
    @pytest.mark.asyncio
    async def test_generate_docker_creates_files(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test that Docker generation creates necessary files."""
        generator = AppGenerator()
        
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        result = await generator._generate_docker(app_dir, sample_readme_data, sample_code_analysis, "test_app")
        
        # Check that Dockerfile was created
        dockerfile_path = os.path.join(app_dir, "Dockerfile")
        assert os.path.exists(dockerfile_path)
        
        # Check that docker-compose.yml was created
        compose_path = os.path.join(app_dir, "docker-compose.yml")
        assert os.path.exists(compose_path)
        
        # Check that startup script was created
        startup_path = os.path.join(app_dir, "start.sh")
        assert os.path.exists(startup_path)
    
    @pytest.mark.asyncio
    async def test_generate_docker_startup_executable(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test that startup script is executable."""
        generator = AppGenerator()
        
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        await generator._generate_docker(app_dir, sample_readme_data, sample_code_analysis, "test_app")
        
        startup_path = os.path.join(app_dir, "start.sh")
        # Check that file has execute permissions
        assert os.access(startup_path, os.X_OK)


class TestWebAppGeneration:
    """Test web app generation."""
    
    @pytest.mark.asyncio
    async def test_generate_web_app_creates_files(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test that web app generation creates necessary files."""
        generator = AppGenerator()
        
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        result = await generator._generate_web_app(app_dir, sample_readme_data, sample_code_analysis, "test_app")
        
        # Check that web wrapper was created
        web_path = os.path.join(app_dir, "web_app.py")
        assert os.path.exists(web_path)
        
        # Check that template was created
        template_path = os.path.join(app_dir, "templates", "index.html")
        assert os.path.exists(template_path)
        
        # Check that static directory was created
        static_path = os.path.join(app_dir, "static")
        assert os.path.exists(static_path)
    
    @pytest.mark.asyncio
    async def test_generate_web_app_includes_web_dependencies(self, temp_dir, sample_readme_data, sample_code_analysis):
        """Test that web app includes FastAPI dependencies."""
        generator = AppGenerator()
        
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        
        await generator._generate_web_app(app_dir, sample_readme_data, sample_code_analysis, "test_app")
        
        req_path = os.path.join(app_dir, "requirements.txt")
        with open(req_path, 'r') as f:
            requirements = f.read()
        
        assert 'fastapi' in requirements
        assert 'uvicorn' in requirements
        assert 'jinja2' in requirements


class TestCompleteAppGeneration:
    """Test complete app generation workflow."""
    
    @pytest.mark.asyncio
    async def test_generate_app_executable(self, mock_repo_path, sample_readme_data, sample_code_analysis, temp_dir):
        """Test generating complete executable app."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1)
            
            result = await generator.generate_app(
                mock_repo_path,
                sample_readme_data,
                sample_code_analysis,
                "test_app",
                "executable"
            )
            
            assert result is not None
            assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_generate_app_docker(self, mock_repo_path, sample_readme_data, sample_code_analysis, temp_dir):
        """Test generating complete Docker app."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        result = await generator.generate_app(
            mock_repo_path,
            sample_readme_data,
            sample_code_analysis,
            "test_app",
            "docker"
        )
        
        assert result is not None
        assert 'test_app' in result
    
    @pytest.mark.asyncio
    async def test_generate_app_web(self, mock_repo_path, sample_readme_data, sample_code_analysis, temp_dir):
        """Test generating complete web app."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        result = await generator.generate_app(
            mock_repo_path,
            sample_readme_data,
            sample_code_analysis,
            "test_app",
            "web"
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_app_invalid_platform(self, mock_repo_path, sample_readme_data, sample_code_analysis, temp_dir):
        """Test with invalid platform."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        with pytest.raises(Exception) as exc_info:
            await generator.generate_app(
                mock_repo_path,
                sample_readme_data,
                sample_code_analysis,
                "test_app",
                "invalid_platform"
            )
        
        assert "Unsupported target platform" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_app_replaces_existing(self, mock_repo_path, sample_readme_data, sample_code_analysis, temp_dir):
        """Test that existing app directory is replaced."""
        generator = AppGenerator()
        generator.output_dir = temp_dir
        
        # Create existing app directory
        app_dir = os.path.join(temp_dir, "test_app")
        os.makedirs(app_dir, exist_ok=True)
        old_file = os.path.join(app_dir, "old_file.txt")
        with open(old_file, "w") as f:
            f.write("old content")
        
        result = await generator.generate_app(
            mock_repo_path,
            sample_readme_data,
            sample_code_analysis,
            "test_app",
            "web"
        )
        
        # Old file should not exist
        assert not os.path.exists(old_file)