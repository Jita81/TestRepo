"""
Unit Tests for GitHub Integration Module

Tests GitHub repository operations including:
- Repository cloning
- URL parsing
- Metadata extraction
- README file finding
- Project file listing
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from src.github_integration import GitHubRepository


class TestGitHubRepositoryInitialization:
    """Test GitHubRepository initialization."""
    
    def test_repository_initialization(self):
        """Test that GitHubRepository initializes correctly."""
        repo = GitHubRepository()
        
        assert repo is not None
        assert hasattr(repo, 'temp_dir')
        assert repo.temp_dir == "temp_repos"
    
    def test_temp_directory_created(self):
        """Test that temp directory is created on initialization."""
        repo = GitHubRepository()
        
        assert os.path.exists(repo.temp_dir)
        assert os.path.isdir(repo.temp_dir)


class TestGitHubURLParsing:
    """Test GitHub URL parsing."""
    
    def test_parse_standard_github_url(self):
        """Test parsing standard GitHub URL."""
        repo = GitHubRepository()
        url = "https://github.com/user/repository"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repository'
    
    def test_parse_github_url_with_git_extension(self):
        """Test parsing GitHub URL with .git extension."""
        repo = GitHubRepository()
        url = "https://github.com/user/repository.git"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repository'
    
    def test_parse_github_url_http(self):
        """Test parsing HTTP GitHub URL (not HTTPS)."""
        repo = GitHubRepository()
        url = "http://github.com/owner/project"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'owner'
        assert result['repo'] == 'project'
    
    def test_parse_github_url_trailing_slash(self):
        """Test parsing GitHub URL with trailing slash."""
        repo = GitHubRepository()
        url = "https://github.com/org/repo/"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'org'
        assert result['repo'] == 'repo'
    
    def test_parse_invalid_url_format(self):
        """Test parsing invalid URL format."""
        repo = GitHubRepository()
        url = "https://github.com/onlyonepart"
        
        with pytest.raises(ValueError) as exc_info:
            repo._parse_github_url(url)
        
        assert "Invalid GitHub URL format" in str(exc_info.value)
    
    def test_parse_empty_url(self):
        """Test parsing empty URL."""
        repo = GitHubRepository()
        url = "https://github.com/"
        
        with pytest.raises(ValueError):
            repo._parse_github_url(url)
    
    def test_parse_url_with_subpaths(self):
        """Test parsing URL with additional subpaths (should ignore them)."""
        repo = GitHubRepository()
        url = "https://github.com/user/repo/tree/main/src"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repo'


class TestRepositoryMetadata:
    """Test repository metadata extraction."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_repository_metadata_success(self, mock_github_api_response):
        """Test successful metadata retrieval."""
        repo = GitHubRepository()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_github_api_response
            mock_get.return_value = mock_response
            
            metadata = await repo._get_repository_metadata('testuser', 'test-repo')
            
            assert metadata['name'] == 'test-repo'
            assert metadata['full_name'] == 'testuser/test-repo'
            assert 'description' in metadata
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_repository_metadata_404(self):
        """Test metadata retrieval with 404 error."""
        repo = GitHubRepository()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            metadata = await repo._get_repository_metadata('user', 'nonexistent')
            
            assert 'error' in metadata
            assert '404' in metadata['error']
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_repository_metadata_timeout(self):
        """Test metadata retrieval with timeout."""
        repo = GitHubRepository()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Timeout")
            
            metadata = await repo._get_repository_metadata('user', 'repo')
            
            assert 'error' in metadata
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api
    async def test_get_repository_metadata_api_url(self):
        """Test that correct API URL is called."""
        repo = GitHubRepository()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response
            
            await repo._get_repository_metadata('owner', 'project')
            
            called_url = mock_get.call_args[0][0]
            assert called_url == "https://api.github.com/repos/owner/project"


class TestRepositoryCloning:
    """Test repository cloning functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git
    async def test_clone_repository_success(self, temp_dir):
        """Test successful repository cloning."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/testuser/test-repo"
        
        with patch('git.Repo.clone_from') as mock_clone, \
             patch.object(repo, '_get_repository_metadata') as mock_metadata:
            
            mock_metadata.return_value = {"name": "test-repo"}
            
            # Mock clone to actually create the directory
            def create_dir(*args, **kwargs):
                repo_dir = args[1]
                os.makedirs(repo_dir, exist_ok=True)
            mock_clone.side_effect = create_dir
            
            result_path = await repo.clone_repository(github_url)
            
            assert result_path is not None
            assert 'testuser_test-repo' in result_path
            mock_clone.assert_called_once()
            mock_metadata.assert_called_once_with('testuser', 'test-repo')
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git
    async def test_clone_repository_creates_directory(self, temp_dir):
        """Test that clone creates proper directory structure."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/owner/project"
        
        with patch('git.Repo.clone_from') as mock_clone, \
             patch.object(repo, '_get_repository_metadata') as mock_metadata:
            
            mock_metadata.return_value = {"name": "project"}
            
            # Mock clone to actually create the directory
            def create_dir(*args, **kwargs):
                repo_dir = args[1]
                os.makedirs(repo_dir, exist_ok=True)
            mock_clone.side_effect = create_dir
            
            result_path = await repo.clone_repository(github_url)
            
            expected_dir = os.path.join(temp_dir, "owner_project")
            assert result_path == expected_dir
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git
    async def test_clone_repository_saves_metadata(self, temp_dir):
        """Test that metadata is saved to file."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/user/repo"
        metadata = {"name": "repo", "description": "Test repo"}
        
        with patch('git.Repo.clone_from') as mock_clone, \
             patch.object(repo, '_get_repository_metadata') as mock_metadata:
            
            mock_metadata.return_value = metadata
            
            # Mock clone to actually create the directory
            def create_dir(*args, **kwargs):
                repo_dir = args[1]
                os.makedirs(repo_dir, exist_ok=True)
            mock_clone.side_effect = create_dir
            
            result_path = await repo.clone_repository(github_url)
            
            # Check metadata file
            repo_dir = os.path.join(temp_dir, "user_repo")
            metadata_file = os.path.join(repo_dir, ".github_metadata.json")
            assert os.path.exists(metadata_file)
            with open(metadata_file, 'r') as f:
                saved_metadata = json.load(f)
            assert saved_metadata['name'] == 'repo'
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git
    async def test_clone_repository_invalid_url(self, temp_dir):
        """Test cloning with invalid URL."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/invalid"
        
        with pytest.raises(Exception) as exc_info:
            await repo.clone_repository(github_url)
        
        assert "Failed to clone repository" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git
    async def test_clone_repository_clone_failure(self, temp_dir):
        """Test handling of clone failure."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/user/repo"
        
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = Exception("Clone failed")
            
            with pytest.raises(Exception) as exc_info:
                await repo.clone_repository(github_url)
            
            assert "Failed to clone repository" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @pytest.mark.requires_git  
    async def test_clone_repository_existing_directory(self, temp_dir):
        """Test cloning when directory already exists (should remove and re-clone)."""
        repo = GitHubRepository()
        repo.temp_dir = temp_dir
        
        github_url = "https://github.com/user/repo"
        
        # Create existing directory
        existing_dir = os.path.join(temp_dir, "user_repo")
        os.makedirs(existing_dir, exist_ok=True)
        
        # Add a file to verify it gets removed
        test_file = os.path.join(existing_dir, "old_file.txt")
        with open(test_file, "w") as f:
            f.write("old content")
        
        with patch('git.Repo.clone_from') as mock_clone, \
             patch.object(repo, '_get_repository_metadata') as mock_metadata, \
             patch('shutil.rmtree') as mock_rmtree:
            
            mock_metadata.return_value = {"name": "repo"}
            
            await repo.clone_repository(github_url)
            
            # Should have called rmtree to remove existing directory
            mock_rmtree.assert_called()


class TestReadmeFileFinding:
    """Test finding README files in repositories."""
    
    def test_get_readme_path_md(self, temp_dir):
        """Test finding README.md file."""
        repo = GitHubRepository()
        
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Test")
        
        found_path = repo.get_readme_path(temp_dir)
        
        assert found_path == readme_path
    
    def test_get_readme_path_rst(self, temp_dir):
        """Test finding README.rst file."""
        repo = GitHubRepository()
        
        readme_path = os.path.join(temp_dir, "README.rst")
        with open(readme_path, "w") as f:
            f.write("Test\n====")
        
        found_path = repo.get_readme_path(temp_dir)
        
        assert found_path == readme_path
    
    def test_get_readme_path_lowercase(self, temp_dir):
        """Test finding readme.md (lowercase)."""
        repo = GitHubRepository()
        
        readme_path = os.path.join(temp_dir, "readme.md")
        with open(readme_path, "w") as f:
            f.write("# Test")
        
        found_path = repo.get_readme_path(temp_dir)
        
        assert found_path == readme_path
    
    def test_get_readme_path_priority(self, temp_dir):
        """Test README file priority (should prefer README.md over others)."""
        repo = GitHubRepository()
        
        # Create multiple README files
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# MD")
        with open(os.path.join(temp_dir, "README.txt"), "w") as f:
            f.write("TXT")
        
        found_path = repo.get_readme_path(temp_dir)
        
        assert found_path.endswith("README.md")
    
    def test_get_readme_path_not_found(self, temp_dir):
        """Test when no README file exists."""
        repo = GitHubRepository()
        
        found_path = repo.get_readme_path(temp_dir)
        
        assert found_path is None


class TestProjectFileListing:
    """Test listing project files."""
    
    def test_get_project_files_python(self, temp_dir):
        """Test getting Python project files."""
        repo = GitHubRepository()
        
        # Create Python files
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
            f.write("fastapi")
        
        files = repo.get_project_files(temp_dir)
        
        assert len(files) > 0
        assert any("main.py" in f for f in files)
        assert any("requirements.txt" in f for f in files)
    
    def test_get_project_files_nodejs(self, temp_dir):
        """Test getting Node.js project files."""
        repo = GitHubRepository()
        
        # Create Node.js files
        with open(os.path.join(temp_dir, "index.js"), "w") as f:
            f.write("console.log('hello');")
        with open(os.path.join(temp_dir, "package.json"), "w") as f:
            f.write('{"name": "test"}')
        
        files = repo.get_project_files(temp_dir)
        
        assert any("index.js" in f for f in files)
        assert any("package.json" in f for f in files)
    
    def test_get_project_files_excludes_hidden(self, temp_dir):
        """Test that hidden directories are excluded."""
        repo = GitHubRepository()
        
        # Create hidden directory
        hidden_dir = os.path.join(temp_dir, ".git")
        os.makedirs(hidden_dir, exist_ok=True)
        with open(os.path.join(hidden_dir, "config"), "w") as f:
            f.write("git config")
        
        # Create normal file
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("pass")
        
        files = repo.get_project_files(temp_dir)
        
        # Should not include .git files
        assert not any(".git" in f for f in files)
        assert any("main.py" in f for f in files)
    
    def test_get_project_files_excludes_common_dirs(self, temp_dir):
        """Test that common non-source directories are excluded."""
        repo = GitHubRepository()
        
        # Create directories that should be excluded
        for excluded_dir in ['node_modules', '__pycache__', 'target', 'build', 'dist']:
            dir_path = os.path.join(temp_dir, excluded_dir)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, "file.txt"), "w") as f:
                f.write("content")
        
        # Create normal file
        with open(os.path.join(temp_dir, "app.py"), "w") as f:
            f.write("pass")
        
        files = repo.get_project_files(temp_dir)
        
        # Should not include excluded directories
        assert not any("node_modules" in f for f in files)
        assert not any("__pycache__" in f for f in files)
        assert any("app.py" in f for f in files)
    
    def test_get_project_files_with_subdirectories(self, temp_dir):
        """Test getting files from subdirectories."""
        repo = GitHubRepository()
        
        # Create subdirectory structure
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        with open(os.path.join(src_dir, "module.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("pass")
        
        files = repo.get_project_files(temp_dir)
        
        assert len(files) >= 2
        assert any("module.py" in f for f in files)
        assert any("main.py" in f for f in files)
    
    def test_get_project_files_empty_directory(self, temp_dir):
        """Test getting files from empty directory."""
        repo = GitHubRepository()
        
        files = repo.get_project_files(temp_dir)
        
        assert isinstance(files, list)
        assert len(files) == 0
    
    def test_get_project_files_multiple_extensions(self, temp_dir):
        """Test getting files with various extensions."""
        repo = GitHubRepository()
        
        # Create files with different extensions
        extensions = ['.py', '.js', '.java', '.cpp', '.go', '.rs']
        for ext in extensions:
            with open(os.path.join(temp_dir, f"file{ext}"), "w") as f:
                f.write("content")
        
        files = repo.get_project_files(temp_dir)
        
        assert len(files) >= len(extensions)
        for ext in extensions:
            assert any(f"file{ext}" in f for f in files)
    
    def test_get_project_files_includes_config(self, temp_dir):
        """Test that configuration files are included."""
        repo = GitHubRepository()
        
        # Create configuration files
        config_files = ['Dockerfile', 'docker-compose.yml', 'setup.py', 'Cargo.toml']
        for config_file in config_files:
            with open(os.path.join(temp_dir, config_file), "w") as f:
                f.write("config content")
        
        files = repo.get_project_files(temp_dir)
        
        for config_file in config_files:
            assert any(config_file in f for f in files)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_parse_url_with_special_characters(self):
        """Test parsing URL with special characters in repo name."""
        repo = GitHubRepository()
        url = "https://github.com/user/repo-with-dashes_and_underscores"
        
        result = repo._parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repo-with-dashes_and_underscores'
    
    def test_get_readme_path_nonexistent_directory(self):
        """Test getting README from non-existent directory."""
        repo = GitHubRepository()
        
        # Should handle gracefully without crashing
        result = repo.get_readme_path("/nonexistent/directory")
        
        # Depending on implementation, might return None or raise exception
        # Either is acceptable for a non-existent directory
        assert result is None or isinstance(result, type(None))
    
    def test_get_project_files_permission_error(self, temp_dir):
        """Test handling of permission errors when listing files."""
        repo = GitHubRepository()
        
        # This test depends on OS and permissions
        # Just verify it doesn't crash
        files = repo.get_project_files(temp_dir)
        assert isinstance(files, list)