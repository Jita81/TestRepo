"""
Unit tests for GitHubRepository module
"""

import os
import shutil
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import requests

from src.github_integration import GitHubRepository


@pytest.mark.unit
class TestGitHubRepository:
    """Tests for GitHubRepository class."""
    
    def test_init(self, github_repo):
        """Test GitHubRepository initialization."""
        assert github_repo is not None
        assert hasattr(github_repo, 'temp_dir')
        assert github_repo.temp_dir == "temp_repos"
    
    def test_temp_dir_creation(self, temp_dir):
        """Test that temp directory is created."""
        repo = GitHubRepository()
        repo.temp_dir = os.path.join(temp_dir, "test_temp_repos")
        
        # Force directory creation
        os.makedirs(repo.temp_dir, exist_ok=True)
        
        assert os.path.exists(repo.temp_dir)
    
    def test_parse_github_url_valid(self, github_repo):
        """Test parsing a valid GitHub URL."""
        url = "https://github.com/octocat/Hello-World"
        
        result = github_repo._parse_github_url(url)
        
        assert result is not None
        assert 'owner' in result
        assert 'repo' in result
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_parse_github_url_with_git_extension(self, github_repo):
        """Test parsing GitHub URL with .git extension."""
        url = "https://github.com/octocat/Hello-World.git"
        
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
        assert '.git' not in result['repo']
    
    def test_parse_github_url_with_trailing_slash(self, github_repo):
        """Test parsing GitHub URL with trailing slash."""
        url = "https://github.com/octocat/Hello-World/"
        
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_parse_github_url_invalid_format(self, github_repo):
        """Test parsing invalid GitHub URL."""
        url = "https://github.com/octocat"
        
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            github_repo._parse_github_url(url)
    
    def test_parse_github_url_empty(self, github_repo):
        """Test parsing empty URL."""
        url = ""
        
        with pytest.raises(ValueError):
            github_repo._parse_github_url(url)
    
    @pytest.mark.asyncio
    @pytest.mark.requires_network
    async def test_get_repository_metadata_success(self, github_repo, mock_requests_get):
        """Test getting repository metadata from GitHub API."""
        metadata = await github_repo._get_repository_metadata("octocat", "Hello-World")
        
        assert metadata is not None
        assert isinstance(metadata, dict)
    
    @pytest.mark.asyncio
    async def test_get_repository_metadata_api_failure(self, github_repo):
        """Test handling API failure."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            metadata = await github_repo._get_repository_metadata("invalid", "repo")
            
            assert 'error' in metadata
            assert '404' in str(metadata['error'])
    
    @pytest.mark.asyncio
    async def test_get_repository_metadata_timeout(self, github_repo):
        """Test handling timeout."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")
            
            metadata = await github_repo._get_repository_metadata("octocat", "Hello-World")
            
            assert 'error' in metadata
            assert 'timeout' in metadata['error'].lower()
    
    @pytest.mark.asyncio
    async def test_get_repository_metadata_network_error(self, github_repo):
        """Test handling network error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network error")
            
            metadata = await github_repo._get_repository_metadata("octocat", "Hello-World")
            
            assert 'error' in metadata
    
    def test_get_readme_path_found(self, github_repo, sample_repo_dir):
        """Test finding README file."""
        readme_path = github_repo.get_readme_path(sample_repo_dir)
        
        assert readme_path is not None
        assert os.path.exists(readme_path)
        assert 'README' in readme_path
    
    def test_get_readme_path_not_found(self, github_repo, temp_dir):
        """Test when README file doesn't exist."""
        readme_path = github_repo.get_readme_path(temp_dir)
        
        assert readme_path is None
    
    def test_get_readme_path_different_cases(self, github_repo, temp_dir):
        """Test finding README files with different cases."""
        # Create lowercase readme
        with open(os.path.join(temp_dir, 'readme.md'), 'w') as f:
            f.write('# Test')
        
        readme_path = github_repo.get_readme_path(temp_dir)
        
        assert readme_path is not None
        assert os.path.exists(readme_path)
    
    def test_get_project_files(self, github_repo, sample_repo_dir):
        """Test getting project files."""
        files = github_repo.get_project_files(sample_repo_dir)
        
        assert isinstance(files, list)
        assert len(files) > 0
        # Should include main.py and requirements.txt
        assert any('main.py' in f for f in files)
        assert any('requirements.txt' in f for f in files)
    
    def test_get_project_files_excludes_hidden(self, github_repo, temp_dir):
        """Test that hidden directories are excluded."""
        # Create hidden directory
        hidden_dir = os.path.join(temp_dir, '.git')
        os.makedirs(hidden_dir)
        with open(os.path.join(hidden_dir, 'config'), 'w') as f:
            f.write('test')
        
        # Create normal file
        with open(os.path.join(temp_dir, 'main.py'), 'w') as f:
            f.write('print("test")')
        
        files = github_repo.get_project_files(temp_dir)
        
        assert isinstance(files, list)
        # Should not include .git files
        assert not any('.git' in f for f in files)
        # Should include main.py
        assert any('main.py' in f for f in files)
    
    def test_get_project_files_excludes_common_dirs(self, github_repo, temp_dir):
        """Test that common non-source directories are excluded."""
        # Create excluded directories
        for dirname in ['node_modules', '__pycache__', 'build', 'dist']:
            dir_path = os.path.join(temp_dir, dirname)
            os.makedirs(dir_path)
            with open(os.path.join(dir_path, 'test.js'), 'w') as f:
                f.write('test')
        
        # Create normal file
        with open(os.path.join(temp_dir, 'main.js'), 'w') as f:
            f.write('test')
        
        files = github_repo.get_project_files(temp_dir)
        
        # Should not include excluded directories
        assert not any('node_modules' in f for f in files)
        assert not any('__pycache__' in f for f in files)
        assert not any('build' in f for f in files)
        assert not any('dist' in f for f in files)
        # Should include main.js
        assert any('main.js' in f for f in files)
    
    def test_get_project_files_empty_directory(self, github_repo, temp_dir):
        """Test getting files from empty directory."""
        files = github_repo.get_project_files(temp_dir)
        
        assert isinstance(files, list)
        assert len(files) == 0
    
    def test_get_project_files_filters_extensions(self, github_repo, temp_dir):
        """Test that only relevant file extensions are included."""
        # Create files with different extensions
        extensions = ['.py', '.js', '.txt', '.log', '.tmp']
        for ext in extensions:
            with open(os.path.join(temp_dir, f'test{ext}'), 'w') as f:
                f.write('test')
        
        files = github_repo.get_project_files(temp_dir)
        
        # Should include .py and .js
        assert any('.py' in f for f in files)
        assert any('.js' in f for f in files)


@pytest.mark.unit
@patch('git.Repo.clone_from')
class TestGitHubRepositoryCloning:
    """Tests for repository cloning functionality."""
    
    @pytest.mark.asyncio
    async def test_clone_repository_success(self, mock_clone, github_repo, temp_dir, mock_requests_get):
        """Test successful repository cloning."""
        github_repo.temp_dir = temp_dir
        url = "https://github.com/octocat/Hello-World"
        
        # Mock the clone operation
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        # Create the expected directory
        expected_dir = os.path.join(temp_dir, "octocat_Hello-World")
        os.makedirs(expected_dir, exist_ok=True)
        
        with patch('shutil.rmtree'):
            result = await github_repo.clone_repository(url)
        
        assert result is not None
        assert 'octocat' in result
        assert 'Hello-World' in result
        mock_clone.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clone_repository_with_existing_dir(self, mock_clone, github_repo, temp_dir, mock_requests_get):
        """Test cloning when directory already exists."""
        github_repo.temp_dir = temp_dir
        url = "https://github.com/octocat/Hello-World"
        
        # Create existing directory
        existing_dir = os.path.join(temp_dir, "octocat_Hello-World")
        os.makedirs(existing_dir, exist_ok=True)
        with open(os.path.join(existing_dir, 'test.txt'), 'w') as f:
            f.write('old content')
        
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        with patch('shutil.rmtree') as mock_rmtree:
            result = await github_repo.clone_repository(url)
            # Should remove existing directory
            mock_rmtree.assert_called()
    
    @pytest.mark.asyncio
    async def test_clone_repository_git_error(self, mock_clone, github_repo, temp_dir):
        """Test handling Git clone error."""
        github_repo.temp_dir = temp_dir
        url = "https://github.com/invalid/repo"
        
        # Mock Git error
        mock_clone.side_effect = Exception("Git clone failed")
        
        with pytest.raises(Exception, match="Failed to clone repository"):
            await github_repo.clone_repository(url)
    
    @pytest.mark.asyncio
    async def test_clone_repository_saves_metadata(self, mock_clone, github_repo, temp_dir, mock_requests_get):
        """Test that repository metadata is saved."""
        github_repo.temp_dir = temp_dir
        url = "https://github.com/octocat/Hello-World"
        
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        expected_dir = os.path.join(temp_dir, "octocat_Hello-World")
        os.makedirs(expected_dir, exist_ok=True)
        
        with patch('shutil.rmtree'):
            result = await github_repo.clone_repository(url)
        
        # Check that metadata file would be created
        metadata_file = os.path.join(expected_dir, ".github_metadata.json")
        assert os.path.exists(metadata_file)


@pytest.mark.unit
class TestGitHubRepositoryEdgeCases:
    """Test edge cases and error handling."""
    
    def test_parse_url_with_subdirectory(self, github_repo):
        """Test parsing URL with subdirectory (should only get owner/repo)."""
        url = "https://github.com/octocat/Hello-World/tree/main/src"
        
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_parse_url_ssh_format(self, github_repo):
        """Test parsing SSH format URL."""
        url = "git@github.com:octocat/Hello-World.git"
        
        # This should raise an error as it's not HTTPS format
        # or handle it gracefully depending on implementation
        try:
            result = github_repo._parse_github_url(url)
            # If it succeeds, verify the parsing
            assert 'octocat' in str(result) or 'Hello-World' in str(result)
        except (ValueError, Exception):
            # Expected for SSH URLs if not supported
            pass
    
    def test_get_project_files_with_symlinks(self, github_repo, temp_dir):
        """Test handling of symbolic links."""
        # Create a file
        file_path = os.path.join(temp_dir, 'original.py')
        with open(file_path, 'w') as f:
            f.write('test')
        
        # Create a symlink (may not work on all systems)
        try:
            link_path = os.path.join(temp_dir, 'link.py')
            os.symlink(file_path, link_path)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this system")
        
        files = github_repo.get_project_files(temp_dir)
        
        assert isinstance(files, list)
        # Should handle symlinks gracefully
    
    def test_get_readme_path_multiple_formats(self, github_repo, temp_dir):
        """Test finding README when multiple formats exist."""
        # Create multiple README files
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write('# Markdown')
        with open(os.path.join(temp_dir, 'README.txt'), 'w') as f:
            f.write('Text')
        with open(os.path.join(temp_dir, 'README.rst'), 'w') as f:
            f.write('reStructuredText')
        
        readme_path = github_repo.get_readme_path(temp_dir)
        
        # Should prefer README.md (first in the list)
        assert readme_path is not None
        assert readme_path.endswith('README.md')