"""
Unit tests for ReadmeParser module
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from src.readme_parser import ReadmeParser


@pytest.mark.unit
class TestReadmeParser:
    """Tests for ReadmeParser class."""
    
    def test_init(self, readme_parser):
        """Test ReadmeParser initialization."""
        assert readme_parser is not None
        assert hasattr(readme_parser, 'installation_patterns')
        assert hasattr(readme_parser, 'dependency_patterns')
        assert hasattr(readme_parser, 'run_patterns')
        assert len(readme_parser.installation_patterns) > 0
    
    @pytest.mark.asyncio
    async def test_parse_readme_success(self, readme_parser, sample_repo_dir):
        """Test successful README parsing."""
        result = await readme_parser.parse_readme(sample_repo_dir)
        
        assert result is not None
        assert 'title' in result
        assert 'description' in result
        assert 'installation_instructions' in result
        assert 'dependencies' in result
        assert 'usage_instructions' in result
        assert 'project_type' in result
        assert result['title'] == 'Sample Project'
        assert result['project_type'] == 'python'
    
    @pytest.mark.asyncio
    async def test_parse_readme_no_file(self, readme_parser, temp_dir):
        """Test parsing when no README file exists."""
        result = await readme_parser.parse_readme(temp_dir)
        
        assert result is not None
        assert 'error' in result
        assert result['error'] == "No README file found"
    
    def test_find_readme_file_success(self, readme_parser, sample_repo_dir):
        """Test finding README file."""
        readme_path = readme_parser._find_readme_file(sample_repo_dir)
        
        assert readme_path is not None
        assert os.path.exists(readme_path)
        assert 'README' in readme_path
    
    def test_find_readme_file_not_found(self, readme_parser, temp_dir):
        """Test when README file doesn't exist."""
        readme_path = readme_parser._find_readme_file(temp_dir)
        
        assert readme_path is None
    
    def test_extract_title_from_h1(self, readme_parser):
        """Test extracting title from H1 tag."""
        html = '<h1>My Awesome Project</h1><p>Description</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        title = readme_parser._extract_title(soup)
        
        assert title == 'My Awesome Project'
    
    def test_extract_title_fallback(self, readme_parser):
        """Test title extraction fallback."""
        html = '<h2>Project Title</h2><p>Description</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        title = readme_parser._extract_title(soup)
        
        assert title == 'Project Title'
    
    def test_extract_title_no_heading(self, readme_parser):
        """Test title extraction when no heading exists."""
        html = '<p>Just a paragraph</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        title = readme_parser._extract_title(soup)
        
        assert title == "Untitled Project"
    
    def test_extract_description_after_h1(self, readme_parser):
        """Test extracting description after H1."""
        html = '<h1>Title</h1><p>This is a comprehensive description of the project.</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        description = readme_parser._extract_description(soup)
        
        assert 'comprehensive description' in description
    
    def test_extract_description_fallback(self, readme_parser):
        """Test description extraction fallback."""
        html = '<p>Short</p><p>This is a much longer paragraph with substantial content about the project.</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        description = readme_parser._extract_description(soup)
        
        assert len(description) > 50
        assert 'substantial content' in description
    
    def test_extract_installation_instructions(self, readme_parser, sample_readme_content):
        """Test extracting installation instructions."""
        instructions = readme_parser._extract_installation_instructions(sample_readme_content)
        
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        # Should find pip install and npm install
        assert any('pip' in inst.lower() or 'requirements' in inst.lower() for inst in instructions)
    
    def test_extract_dependencies_from_content(self, readme_parser, sample_readme_content, sample_repo_dir):
        """Test extracting dependencies."""
        dependencies = readme_parser._extract_dependencies(sample_readme_content, sample_repo_dir)
        
        assert isinstance(dependencies, dict)
        assert 'files' in dependencies
        assert 'packages' in dependencies
        assert 'system_requirements' in dependencies
        assert len(dependencies['system_requirements']) > 0
    
    def test_extract_usage_instructions(self, readme_parser, sample_readme_content):
        """Test extracting usage instructions."""
        instructions = readme_parser._extract_usage_instructions(sample_readme_content)
        
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        assert any('python' in inst.lower() or 'docker' in inst.lower() for inst in instructions)
    
    def test_extract_configuration(self, readme_parser, sample_readme_content):
        """Test extracting configuration information."""
        config = readme_parser._extract_configuration(sample_readme_content)
        
        assert isinstance(config, dict)
        assert 'environment_variables' in config
        assert 'config_files' in config
        assert 'settings' in config
        assert len(config['environment_variables']) > 0
    
    def test_extract_examples(self, readme_parser, sample_readme_content):
        """Test extracting code examples."""
        examples = readme_parser._extract_examples(sample_readme_content)
        
        assert isinstance(examples, list)
        assert len(examples) > 0
    
    def test_extract_troubleshooting(self, readme_parser, sample_readme_content):
        """Test extracting troubleshooting information."""
        troubleshooting = readme_parser._extract_troubleshooting(sample_readme_content)
        
        assert isinstance(troubleshooting, list)
    
    def test_detect_project_type_python(self, readme_parser, sample_repo_dir):
        """Test detecting Python project type."""
        project_type = readme_parser._detect_project_type(sample_repo_dir)
        
        assert project_type == 'python'
    
    def test_detect_project_type_nodejs(self, readme_parser, temp_dir):
        """Test detecting Node.js project type."""
        # Create package.json
        with open(os.path.join(temp_dir, 'package.json'), 'w') as f:
            f.write('{"name": "test"}')
        
        project_type = readme_parser._detect_project_type(temp_dir)
        
        assert project_type == 'nodejs'
    
    def test_detect_project_type_rust(self, readme_parser, temp_dir):
        """Test detecting Rust project type."""
        # Create Cargo.toml
        with open(os.path.join(temp_dir, 'Cargo.toml'), 'w') as f:
            f.write('[package]\nname = "test"')
        
        project_type = readme_parser._detect_project_type(temp_dir)
        
        assert project_type == 'rust'
    
    def test_detect_project_type_unknown(self, readme_parser, temp_dir):
        """Test detecting unknown project type."""
        project_type = readme_parser._detect_project_type(temp_dir)
        
        assert project_type == 'unknown'
    
    def test_identify_main_files_python(self, readme_parser, sample_repo_dir):
        """Test identifying Python main files."""
        main_files = readme_parser._identify_main_files(sample_repo_dir)
        
        assert isinstance(main_files, list)
        assert 'main.py' in main_files
    
    def test_identify_main_files_none(self, readme_parser, temp_dir):
        """Test when no main files exist."""
        main_files = readme_parser._identify_main_files(temp_dir)
        
        assert isinstance(main_files, list)
        assert len(main_files) == 0
    
    def test_extract_section_found(self, readme_parser):
        """Test extracting a section that exists."""
        content = """
# My Project

## Installation

Run pip install

## Usage

Run python main.py
"""
        section = readme_parser._extract_section(content, ['installation'])
        
        assert section is not None
        assert 'pip install' in section.lower()
    
    def test_extract_section_not_found(self, readme_parser):
        """Test extracting a section that doesn't exist."""
        content = """
# My Project

Some content here.
"""
        section = readme_parser._extract_section(content, ['nonexistent'])
        
        assert section == ""
    
    def test_extract_requirements_list(self, readme_parser):
        """Test extracting requirements from a list."""
        content = """
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
"""
        requirements = readme_parser._extract_requirements_list(content)
        
        assert isinstance(requirements, list)
        assert len(requirements) == 3
        assert any('Python' in req for req in requirements)
    
    def test_parse_dependency_file_requirements_txt(self, readme_parser, temp_dir):
        """Test parsing requirements.txt file."""
        req_file = os.path.join(temp_dir, 'requirements.txt')
        with open(req_file, 'w') as f:
            f.write("requests==2.28.0\npyyaml>=6.0\n# Comment line\nflask\n")
        
        packages = readme_parser._parse_dependency_file(req_file)
        
        assert isinstance(packages, list)
        assert len(packages) >= 3
        assert 'requests==2.28.0' in packages
        assert 'pyyaml>=6.0' in packages
        assert 'flask' in packages
    
    def test_parse_dependency_file_package_json(self, readme_parser, temp_dir):
        """Test parsing package.json file."""
        pkg_file = os.path.join(temp_dir, 'package.json')
        with open(pkg_file, 'w') as f:
            f.write('''{
                "dependencies": {
                    "express": "^4.18.0",
                    "axios": "^1.0.0"
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }''')
        
        packages = readme_parser._parse_dependency_file(pkg_file)
        
        assert isinstance(packages, list)
        assert len(packages) == 3
        assert 'express' in packages
        assert 'axios' in packages
        assert 'jest' in packages
    
    def test_parse_dependency_file_error(self, readme_parser):
        """Test parsing non-existent dependency file."""
        packages = readme_parser._parse_dependency_file('/nonexistent/file.txt')
        
        assert isinstance(packages, list)
        assert len(packages) == 0


@pytest.mark.unit
class TestReadmeParserEdgeCases:
    """Test edge cases and error handling."""
    
    def test_parse_empty_readme(self, readme_parser, temp_dir):
        """Test parsing empty README file."""
        readme_path = os.path.join(temp_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write('')
        
        # Should not raise exception
        result = readme_parser._find_readme_file(temp_dir)
        assert result is not None
    
    def test_parse_readme_with_unicode(self, readme_parser, temp_dir):
        """Test parsing README with unicode characters."""
        readme_path = os.path.join(temp_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write('# プロジェクト\n\n中文测试 🚀')
        
        result = readme_parser._find_readme_file(temp_dir)
        assert result is not None
    
    def test_malformed_json_in_package_file(self, readme_parser, temp_dir):
        """Test parsing malformed package.json."""
        pkg_file = os.path.join(temp_dir, 'package.json')
        with open(pkg_file, 'w') as f:
            f.write('{invalid json}')
        
        packages = readme_parser._parse_dependency_file(pkg_file)
        
        assert isinstance(packages, list)
        assert len(packages) == 0
    
    @pytest.mark.asyncio
    async def test_parse_readme_with_special_characters(self, readme_parser, temp_dir):
        """Test parsing README with special markdown characters."""
        readme_path = os.path.join(temp_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write('''# Test `Project`

Description with **bold** and *italic*.

## Installation

```bash
pip install package-name
```

| Feature | Status |
|---------|--------|
| Test    | ✅     |
''')
        
        result = await readme_parser.parse_readme(temp_dir)
        
        assert 'title' in result
        assert 'Test' in result['title']