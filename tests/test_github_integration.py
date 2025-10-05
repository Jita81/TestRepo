#!/usr/bin/env python3
"""
Comprehensive tests for GitHub Integration
Tests happy path, error conditions, and edge cases
"""

import pytest
import asyncio
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from src.github_integration import GitHubRepository, GitHubRepositoryError


class TestGitHubRepositoryHappyPath:
    """Tests for successful operations."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing."""
        repo = GitHubRepository()
        yield repo
        # Cleanup
        if os.path.exists(repo.temp_dir):
            shutil.rmtree(repo.temp_dir, ignore_errors=True)
    
    def test_parse_github_url_https(self, github_repo):
        """Test parsing standard HTTPS GitHub URL."""
        url = "https://github.com/octocat/Hello-World"
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_parse_github_url_with_git_extension(self, github_repo):
        """Test parsing GitHub URL with .git extension."""
        url = "https://github.com/octocat/Hello-World.git"
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_parse_github_url_ssh(self, github_repo):
        """Test parsing SSH GitHub URL."""
        url = "git@github.com:octocat/Hello-World.git"
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'


class TestGitHubRepositoryErrorHandling:
    """Tests for error conditions."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing."""
        repo = GitHubRepository()
        yield repo
        if os.path.exists(repo.temp_dir):
            shutil.rmtree(repo.temp_dir, ignore_errors=True)
    
    def test_parse_github_url_empty(self, github_repo):
        """Test parsing empty URL."""
        with pytest.raises(ValueError):
            github_repo._parse_github_url("")
    
    def test_parse_github_url_invalid_format(self, github_repo):
        """Test parsing invalid URL format."""
        with pytest.raises(ValueError):
            github_repo._parse_github_url("https://github.com/invalid")
    
    def test_parse_github_url_non_github(self, github_repo):
        """Test parsing non-GitHub URL."""
        with pytest.raises(ValueError):
            github_repo._parse_github_url("https://gitlab.com/user/repo")
    
    def test_parse_github_url_invalid_characters(self, github_repo):
        """Test parsing URL with invalid characters."""
        with pytest.raises(ValueError):
            github_repo._parse_github_url("https://github.com/user<>/repo!")
    
    @pytest.mark.asyncio
    async def test_clone_repository_empty_url(self, github_repo):
        """Test cloning with empty URL."""
        with pytest.raises(GitHubRepositoryError, match="cannot be empty"):
            await github_repo.clone_repository("")
    
    @pytest.mark.asyncio
    async def test_clone_repository_invalid_url(self, github_repo):
        """Test cloning with invalid URL."""
        with pytest.raises(GitHubRepositoryError, match="Invalid GitHub URL"):
            await github_repo.clone_repository("not-a-valid-url")
    
    @pytest.mark.asyncio
    async def test_clone_repository_not_found(self, github_repo):
        """Test cloning non-existent repository."""
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = Exception("not found")
            
            with pytest.raises(GitHubRepositoryError):
                await github_repo.clone_repository("https://github.com/nonexistent/repo12345")
    
    @pytest.mark.asyncio
    async def test_clone_repository_network_error(self, github_repo):
        """Test cloning with network error."""
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = Exception("Network error")
            
            with pytest.raises(GitHubRepositoryError):
                await github_repo.clone_repository("https://github.com/octocat/Hello-World")
    
    @pytest.mark.asyncio
    async def test_get_metadata_timeout(self, github_repo):
        """Test metadata fetch with timeout."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Timeout")
            
            result = await github_repo._get_repository_metadata("octocat", "Hello-World")
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_metadata_404(self, github_repo):
        """Test metadata fetch for non-existent repository."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = await github_repo._get_repository_metadata("nonexistent", "repo")
            assert result.get("status") == 404
    
    @pytest.mark.asyncio
    async def test_get_metadata_rate_limit(self, github_repo):
        """Test metadata fetch with rate limit."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 403
            mock_get.return_value = mock_response
            
            result = await github_repo._get_repository_metadata("octocat", "Hello-World")
            assert result.get("status") == 403


class TestGitHubRepositoryEdgeCases:
    """Tests for edge cases."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing."""
        repo = GitHubRepository()
        yield repo
        if os.path.exists(repo.temp_dir):
            shutil.rmtree(repo.temp_dir, ignore_errors=True)
    
    def test_get_readme_path_multiple_formats(self, github_repo):
        """Test finding README in different formats."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create README.md
            readme_path = os.path.join(tmpdir, "README.md")
            with open(readme_path, 'w') as f:
                f.write("# Test")
            
            result = github_repo.get_readme_path(tmpdir)
            assert result == readme_path
    
    def test_get_readme_path_not_found(self, github_repo):
        """Test when README doesn't exist."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = github_repo.get_readme_path(tmpdir)
            assert result is None
    
    def test_get_project_files_filters_correctly(self, github_repo):
        """Test that project files are filtered correctly."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create various files
            open(os.path.join(tmpdir, "test.py"), 'w').close()
            open(os.path.join(tmpdir, "test.txt"), 'w').close()
            open(os.path.join(tmpdir, "package.json"), 'w').close()
            
            # Create ignored directory
            ignored_dir = os.path.join(tmpdir, "node_modules")
            os.makedirs(ignored_dir)
            open(os.path.join(ignored_dir, "ignore.js"), 'w').close()
            
            files = github_repo.get_project_files(tmpdir)
            
            # Should include .py and package.json but not .txt or node_modules
            assert any('test.py' in f for f in files)
            assert any('package.json' in f for f in files)
            assert not any('test.txt' in f for f in files)
            assert not any('node_modules' in f for f in files)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])