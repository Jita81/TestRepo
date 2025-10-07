"""
Unit tests for AgenticCoder module
"""

import os
import json
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from src.agentic_coder import AgenticCoder


@pytest.mark.unit
class TestAgenticCoder:
    """Tests for AgenticCoder class."""
    
    def test_init(self, agentic_coder):
        """Test AgenticCoder initialization."""
        assert agentic_coder is not None
        assert hasattr(agentic_coder, 'max_tokens')
        assert hasattr(agentic_coder, 'model')
        assert agentic_coder.max_tokens == 4000
        assert agentic_coder.model == "gpt-4"
    
    def test_init_with_api_key(self, mock_env_vars):
        """Test initialization with API key."""
        coder = AgenticCoder()
        assert coder is not None
        assert hasattr(coder, 'client')
    
    def test_get_project_structure(self, agentic_coder, sample_repo_dir):
        """Test getting project structure."""
        structure = agentic_coder._get_project_structure(sample_repo_dir)
        
        assert structure is not None
        assert 'files' in structure
        assert 'directories' in structure
        assert 'extensions' in structure
        assert 'size' in structure
        assert isinstance(structure['files'], list)
        assert len(structure['files']) > 0
    
    def test_get_project_structure_filters_directories(self, agentic_coder, temp_dir):
        """Test that project structure filters out excluded directories."""
        # Create directories that should be excluded
        excluded_dirs = ['node_modules', '__pycache__', 'venv', '.git', 'build']
        for dirname in excluded_dirs:
            dir_path = os.path.join(temp_dir, dirname)
            os.makedirs(dir_path)
            with open(os.path.join(dir_path, 'test.py'), 'w') as f:
                f.write('test')
        
        # Create normal file
        with open(os.path.join(temp_dir, 'main.py'), 'w') as f:
            f.write('print("test")')
        
        structure = agentic_coder._get_project_structure(temp_dir)
        
        # Should only include main.py
        assert len(structure['files']) == 1
        assert structure['files'][0]['path'] == 'main.py'
    
    def test_get_project_structure_calculates_size(self, agentic_coder, sample_repo_dir):
        """Test that total size is calculated correctly."""
        structure = agentic_coder._get_project_structure(sample_repo_dir)
        
        assert structure['size'] > 0
        # Total size should be sum of all file sizes
        calculated_size = sum(f['size'] for f in structure['files'])
        assert structure['size'] == calculated_size
    
    def test_get_project_structure_identifies_extensions(self, agentic_coder, temp_dir):
        """Test that file extensions are identified."""
        # Create files with different extensions
        extensions = ['.py', '.js', '.md', '.txt']
        for ext in extensions:
            with open(os.path.join(temp_dir, f'test{ext}'), 'w') as f:
                f.write('test')
        
        structure = agentic_coder._get_project_structure(temp_dir)
        
        assert set(structure['extensions']) == set(extensions)
    
    def test_read_key_files(self, agentic_coder, sample_repo_dir):
        """Test reading key files."""
        structure = agentic_coder._get_project_structure(sample_repo_dir)
        key_files = agentic_coder._read_key_files(sample_repo_dir, structure)
        
        assert isinstance(key_files, dict)
        assert len(key_files) > 0
        # Should include main.py and requirements.txt
        assert any('main.py' in path for path in key_files.keys())
        assert any('requirements.txt' in path for path in key_files.keys())
    
    def test_read_key_files_limits_content(self, agentic_coder, temp_dir):
        """Test that file content is limited to 5000 characters."""
        # Create a large file
        large_content = 'x' * 10000
        with open(os.path.join(temp_dir, 'main.py'), 'w') as f:
            f.write(large_content)
        
        structure = {'files': [{'path': 'main.py', 'size': 10000, 'extension': '.py'}]}
        key_files = agentic_coder._read_key_files(temp_dir, structure)
        
        assert 'main.py' in key_files
        # Content should be limited to 5000 characters
        assert len(key_files['main.py']) <= 5000
    
    def test_read_key_files_skips_large_files(self, agentic_coder, temp_dir):
        """Test that very large files are skipped."""
        # Create a very large file (>10000 bytes)
        with open(os.path.join(temp_dir, 'large.py'), 'w') as f:
            f.write('x' * 20000)
        
        structure = {'files': [{'path': 'large.py', 'size': 20000, 'extension': '.py'}]}
        key_files = agentic_coder._read_key_files(temp_dir, structure)
        
        # Large files should not be included
        assert 'large.py' not in key_files
    
    def test_read_key_files_handles_binary(self, agentic_coder, temp_dir):
        """Test handling of binary files."""
        # Create a binary file
        with open(os.path.join(temp_dir, 'image.png'), 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')
        
        structure = {'files': [{'path': 'image.png', 'size': 8, 'extension': '.png'}]}
        key_files = agentic_coder._read_key_files(temp_dir, structure)
        
        # Should handle gracefully (may skip or include with error)
        assert isinstance(key_files, dict)
    
    def test_create_analysis_prompt(self, agentic_coder, sample_parsed_readme, sample_repo_dir):
        """Test creating analysis prompt."""
        structure = agentic_coder._get_project_structure(sample_repo_dir)
        key_files = agentic_coder._read_key_files(sample_repo_dir, structure)
        
        prompt = agentic_coder._create_analysis_prompt(
            sample_parsed_readme, 
            structure, 
            key_files
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'Test Project' in prompt
        assert 'entry_points' in prompt
        assert 'dependencies' in prompt
    
    def test_create_generation_prompt(self, agentic_coder, sample_code_analysis):
        """Test creating generation prompt."""
        prompt = agentic_coder._create_generation_prompt(
            sample_code_analysis, 
            'executable'
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'executable' in prompt.lower()
        assert 'wrapper' in prompt.lower()
    
    def test_identify_entry_points_main_files(self, agentic_coder):
        """Test identifying entry points from main files."""
        key_files = {
            'main.py': 'print("hello")',
            'app.py': 'def run(): pass',
            'util.py': 'def helper(): pass'
        }
        
        entry_points = agentic_coder._identify_entry_points(key_files)
        
        assert isinstance(entry_points, list)
        assert 'main.py' in entry_points
        assert 'app.py' in entry_points
        assert 'util.py' not in entry_points
    
    def test_identify_entry_points_with_main_block(self, agentic_coder):
        """Test identifying entry points with __main__ block."""
        key_files = {
            'script.py': 'if __name__ == "__main__":\n    main()',
            'module.py': 'def function(): pass'
        }
        
        entry_points = agentic_coder._identify_entry_points(key_files)
        
        assert 'script.py' in entry_points
        assert 'module.py' not in entry_points
    
    def test_identify_entry_points_package_json(self, agentic_coder):
        """Test identifying entry points from package.json."""
        key_files = {
            'package.json': '{"main": "index.js", "scripts": {"start": "node index.js"}}'
        }
        
        entry_points = agentic_coder._identify_entry_points(key_files)
        
        assert 'package.json' in entry_points
    
    def test_extract_ai_dependencies(self, agentic_coder):
        """Test extracting dependencies from AI analysis."""
        analysis = {
            'dependencies': ['requests', 'pyyaml', 'flask']
        }
        
        deps = agentic_coder._extract_ai_dependencies(analysis)
        
        assert isinstance(deps, list)
        assert len(deps) == 3
        assert 'requests' in deps
    
    def test_extract_ai_dependencies_empty(self, agentic_coder):
        """Test extracting dependencies when none exist."""
        analysis = {}
        
        deps = agentic_coder._extract_ai_dependencies(analysis)
        
        assert isinstance(deps, list)
        assert len(deps) == 0
    
    def test_extract_build_instructions(self, agentic_coder):
        """Test extracting build instructions."""
        analysis = {
            'build_commands': ['pip install -r requirements.txt', 'npm install']
        }
        
        instructions = agentic_coder._extract_build_instructions(analysis)
        
        assert isinstance(instructions, list)
        assert len(instructions) == 2
    
    def test_extract_runtime_requirements(self, agentic_coder):
        """Test extracting runtime requirements."""
        analysis = {
            'environment_variables': ['API_KEY', 'DEBUG'],
            'ports': ['8000', '5432'],
            'special_requirements': ['PostgreSQL 12+']
        }
        
        requirements = agentic_coder._extract_runtime_requirements(analysis)
        
        assert isinstance(requirements, dict)
        assert 'environment_variables' in requirements
        assert 'ports' in requirements
        assert 'special_requirements' in requirements
        assert len(requirements['environment_variables']) == 2
        assert len(requirements['ports']) == 2
    
    def test_extract_runtime_requirements_empty(self, agentic_coder):
        """Test extracting runtime requirements when none exist."""
        analysis = {}
        
        requirements = agentic_coder._extract_runtime_requirements(analysis)
        
        assert isinstance(requirements, dict)
        assert requirements['environment_variables'] == []
        assert requirements['ports'] == []
        assert requirements['special_requirements'] == []


@pytest.mark.unit
@pytest.mark.requires_api
class TestAgenticCoderWithAPI:
    """Tests for AgenticCoder that require API access."""
    
    @pytest.mark.asyncio
    async def test_get_ai_analysis_with_mock(self, agentic_coder, mock_openai_response):
        """Test getting AI analysis with mocked client."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps(mock_openai_response)
            mock_client.chat.completions.create.return_value = mock_response
            
            prompt = "Analyze this code"
            result = await agentic_coder._get_ai_analysis(prompt)
            
            assert result is not None
            assert isinstance(result, dict)
            assert 'entry_points' in result
            mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_ai_analysis_non_json_response(self, agentic_coder):
        """Test handling non-JSON AI response."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "This is just plain text, not JSON"
            mock_client.chat.completions.create.return_value = mock_response
            
            prompt = "Analyze this code"
            result = await agentic_coder._get_ai_analysis(prompt)
            
            assert result is not None
            assert isinstance(result, dict)
            assert 'analysis' in result
    
    @pytest.mark.asyncio
    async def test_get_ai_analysis_api_error(self, agentic_coder):
        """Test handling API error."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            prompt = "Analyze this code"
            result = await agentic_coder._get_ai_analysis(prompt)
            
            assert result is not None
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_get_ai_generation_with_mock(self, agentic_coder):
        """Test getting AI generation with mocked client."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "# Generated code\nprint('hello')"
            mock_client.chat.completions.create.return_value = mock_response
            
            prompt = "Generate wrapper code"
            result = await agentic_coder._get_ai_generation(prompt)
            
            assert result is not None
            assert isinstance(result, str)
            assert 'Generated code' in result
    
    @pytest.mark.asyncio
    async def test_get_ai_generation_api_error(self, agentic_coder):
        """Test handling API error in generation."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            prompt = "Generate wrapper code"
            result = await agentic_coder._get_ai_generation(prompt)
            
            assert result is not None
            assert '# Error' in result
    
    @pytest.mark.asyncio
    async def test_analyze_codebase_full(self, agentic_coder, sample_repo_dir, sample_parsed_readme):
        """Test full codebase analysis."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                'entry_points': ['main.py'],
                'dependencies': ['requests'],
                'build_commands': ['pip install -r requirements.txt'],
                'run_commands': ['python main.py'],
                'environment_variables': [],
                'ports': [],
                'packaging_strategy': 'pyinstaller',
                'special_requirements': [],
                'confidence_score': 0.9
            })
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await agentic_coder.analyze_codebase(sample_repo_dir, sample_parsed_readme)
            
            assert result is not None
            assert 'project_structure' in result
            assert 'ai_analysis' in result
            assert 'entry_points' in result
            assert 'dependencies' in result
            assert 'build_instructions' in result
            assert 'runtime_requirements' in result
    
    @pytest.mark.asyncio
    async def test_analyze_codebase_error(self, agentic_coder, sample_repo_dir, sample_parsed_readme):
        """Test codebase analysis with error."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("Analysis failed")
            
            result = await agentic_coder.analyze_codebase(sample_repo_dir, sample_parsed_readme)
            
            assert result is not None
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_generate_app_wrapper(self, agentic_coder, sample_code_analysis):
        """Test generating app wrapper."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "#!/usr/bin/env python3\nprint('wrapper')"
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await agentic_coder.generate_app_wrapper(sample_code_analysis, 'executable')
            
            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_app_wrapper_error(self, agentic_coder, sample_code_analysis):
        """Test wrapper generation with error."""
        with patch.object(agentic_coder, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("Generation failed")
            
            result = await agentic_coder.generate_app_wrapper(sample_code_analysis, 'executable')
            
            assert result is not None
            assert '# Error' in result


@pytest.mark.unit
class TestAgenticCoderEdgeCases:
    """Test edge cases and error handling."""
    
    def test_get_project_structure_empty_directory(self, agentic_coder, temp_dir):
        """Test project structure for empty directory."""
        structure = agentic_coder._get_project_structure(temp_dir)
        
        assert structure['files'] == []
        assert structure['size'] == 0
        assert structure['extensions'] == []
    
    def test_read_key_files_with_unreadable_file(self, agentic_coder, temp_dir):
        """Test reading key files with permission error."""
        # Create a file
        file_path = os.path.join(temp_dir, 'main.py')
        with open(file_path, 'w') as f:
            f.write('test')
        
        structure = {'files': [{'path': 'main.py', 'size': 4, 'extension': '.py'}]}
        
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            key_files = agentic_coder._read_key_files(temp_dir, structure)
            
            # Should handle error gracefully
            assert isinstance(key_files, dict)
    
    def test_identify_entry_points_no_matches(self, agentic_coder):
        """Test identifying entry points when none match."""
        key_files = {
            'utils.py': 'def helper(): pass',
            'config.yaml': 'settings: {}'}
        
        entry_points = agentic_coder._identify_entry_points(key_files)
        
        assert isinstance(entry_points, list)
        assert len(entry_points) == 0
    
    def test_create_prompt_with_empty_data(self, agentic_coder):
        """Test creating prompt with minimal data."""
        readme_data = {}
        project_files = {'files': [], 'extensions': [], 'size': 0}
        key_files = {}
        
        prompt = agentic_coder._create_analysis_prompt(
            readme_data, 
            project_files, 
            key_files
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should still contain required sections
        assert 'entry_points' in prompt
        assert 'dependencies' in prompt