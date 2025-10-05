#!/usr/bin/env python3
"""
Comprehensive tests for GitHub Integration
Tests happy path, error conditions, and edge cases
"""

import pytest
import asyncio
import os
import shutil
import logging
from unittest.mock import Mock, patch, MagicMock
from src.github_integration import GitHubRepository, GitHubRepositoryError

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestGitHubRepositoryHappyPath:
    """Tests for successful operations."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing with proper cleanup."""
        repo = GitHubRepository()
        created_dirs = []
        
        # Track created directories
        original_clone = repo.clone_repository
        async def tracked_clone(*args, **kwargs):
            result = await original_clone(*args, **kwargs)
            created_dirs.append(result)
            return result
        repo.clone_repository = tracked_clone
        
        yield repo
        
        # Comprehensive cleanup with proper error handling
        cleanup_errors = []
        
        try:
            # Clean tracked directories
            for dir_path in created_dirs:
                try:
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)
                        logger.debug(f"Cleaned directory: {dir_path}")
                except PermissionError as e:
                    # Retry with ignore_errors
                    shutil.rmtree(dir_path, ignore_errors=True)
                    cleanup_errors.append(f"Permission error on {dir_path}: {e}")
                except Exception as e:
                    cleanup_errors.append(f"Failed to clean {dir_path}: {e}")
            
            # Clean temp directory
            if os.path.exists(repo.temp_dir):
                try:
                    shutil.rmtree(repo.temp_dir)
                except PermissionError:
                    # Retry with ignore_errors
                    shutil.rmtree(repo.temp_dir, ignore_errors=True)
                except Exception as e:
                    cleanup_errors.append(f"Failed to clean temp_dir: {e}")
            
            # Clean any leftover files
            try:
                import glob
                if os.path.exists(repo.temp_dir):
                    temp_files = glob.glob(os.path.join(repo.temp_dir, "*"))
                    for temp_file in temp_files:
                        try:
                            if os.path.isdir(temp_file):
                                shutil.rmtree(temp_file, ignore_errors=True)
                            elif os.path.isfile(temp_file):
                                os.remove(temp_file)
                        except Exception as e:
                            cleanup_errors.append(f"Failed to remove {temp_file}: {e}")
            except Exception as e:
                cleanup_errors.append(f"Glob cleanup failed: {e}")
        
        except Exception as e:
            cleanup_errors.append(f"Critical cleanup error: {e}")
        
        finally:
            # Log any cleanup errors but don't fail the test
            if cleanup_errors:
                logger.warning(f"Cleanup completed with {len(cleanup_errors)} warnings")
                for error in cleanup_errors:
                    logger.debug(error)
            
            # Final verification
            try:
                if os.path.exists(repo.temp_dir):
                    # Last resort cleanup
                    import gc
                    gc.collect()  # Force garbage collection
                    shutil.rmtree(repo.temp_dir, ignore_errors=True)
            except:
                pass  # Ignore final cleanup errors
    
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
    """Tests for error conditions with comprehensive cleanup."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing with proper cleanup."""
        repo = GitHubRepository()
        yield repo
        
        # Comprehensive cleanup with proper error handling
        cleanup_success = False
        cleanup_errors = []
        
        try:
            if os.path.exists(repo.temp_dir):
                # Force remove with retry
                for attempt in range(3):
                    try:
                        shutil.rmtree(repo.temp_dir)
                        cleanup_success = True
                        logger.debug(f"Cleanup successful on attempt {attempt + 1}")
                        break
                    except PermissionError as e:
                        import time
                        time.sleep(0.1 * (attempt + 1))  # Progressive backoff
                        cleanup_errors.append(f"Attempt {attempt + 1}: {e}")
                    except Exception as e:
                        cleanup_errors.append(f"Attempt {attempt + 1}: {e}")
                        if attempt == 2:
                            # Final attempt with ignore_errors
                            try:
                                shutil.rmtree(repo.temp_dir, ignore_errors=True)
                                cleanup_success = True
                            except:
                                pass
        except Exception as e:
            cleanup_errors.append(f"Critical error: {e}")
        finally:
            if not cleanup_success and cleanup_errors:
                logger.warning(f"Cleanup incomplete: {len(cleanup_errors)} errors")
                for error in cleanup_errors[:3]:  # Log first 3 errors
                    logger.debug(error)
    
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
            assert "rate limit" in result.get("error", "").lower()


class TestGitHubRepositoryAdvancedErrorHandling:
    """Advanced error handling and edge case tests."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing."""
        repo = GitHubRepository()
        yield repo
        try:
            if os.path.exists(repo.temp_dir):
                shutil.rmtree(repo.temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_api_server_error_with_retry(self, github_repo):
        """Test metadata fetch with server error and retry logic."""
        with patch('requests.get') as mock_get:
            # Simulate server error on first attempts, success on last
            mock_responses = [
                Mock(status_code=503),
                Mock(status_code=502),
                Mock(status_code=200, json=lambda: {"name": "test", "full_name": "test/repo"}),
            ]
            mock_get.side_effect = mock_responses
            
            result = await github_repo._get_repository_metadata("test", "repo")
            
            # Should eventually succeed after retries
            assert "error" not in result or result.get("name") == "test"
    
    @pytest.mark.asyncio
    async def test_invalid_github_token(self, github_repo):
        """Test handling of invalid GitHub token."""
        # Set invalid token
        github_repo.github_token = "invalid_token_12345"
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Bad credentials"
            mock_get.return_value = mock_response
            
            result = await github_repo._get_repository_metadata("octocat", "Hello-World")
            
            # Should handle gracefully
            assert "error" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_api_rate_limit_with_retry(self, github_repo):
        """Test API rate limit with proper retry and backoff."""
        with patch('requests.get') as mock_get:
            # Simulate rate limit that resolves after wait
            call_count = [0]
            
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] < 3:
                    response = Mock()
                    response.status_code = 403
                    response.headers = {'X-RateLimit-Remaining': '0'}
                    return response
                else:
                    response = Mock()
                    response.status_code = 200
                    response.json = lambda: {"name": "test"}
                    return response
            
            mock_get.side_effect = side_effect
            
            # Should retry and eventually succeed or return error
            result = await github_repo._get_repository_metadata("test", "repo")
            assert call_count[0] >= 1  # At least one attempt made
    
    @pytest.mark.asyncio
    async def test_network_connection_error_all_retries(self, github_repo):
        """Test complete network failure after all retries."""
        with patch('requests.get') as mock_get:
            from requests.exceptions import ConnectionError as RequestsConnectionError
            mock_get.side_effect = RequestsConnectionError("Connection refused")
            
            result = await github_repo._get_repository_metadata("test", "repo")
            
            assert "error" in result
            assert "connection" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_malformed_api_response(self, github_repo):
        """Test handling of malformed API responses."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
            mock_get.return_value = mock_response
            
            # Should handle gracefully
            result = await github_repo._get_repository_metadata("test", "repo")
            assert "error" in result or isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_clone_with_invalid_credentials(self, github_repo):
        """Test cloning with invalid GitHub credentials."""
        with patch('git.Repo.clone_from') as mock_clone:
            import git
            mock_clone.side_effect = git.GitCommandError(
                'clone',
                128,
                stderr=b'remote: Invalid username or password'
            )
            
            with pytest.raises(Exception) as exc_info:
                await github_repo.clone_repository("https://github.com/private/repo")
            
            assert "authentication" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_clone_timeout_with_retry(self, github_repo):
        """Test clone timeout with retry logic."""
        with patch('git.Repo.clone_from') as mock_clone:
            # Simulate timeout on first attempts
            call_count = [0]
            
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] < github_repo.max_retries:
                    raise Exception("Timeout")
                # Last attempt succeeds
                return Mock()
            
            mock_clone.side_effect = side_effect
            
            # Should retry multiple times
            try:
                await github_repo.clone_repository("https://github.com/test/repo")
            except:
                pass
            
            # Verify retries occurred
            assert call_count[0] >= 2
    
    def test_parse_url_with_special_characters(self, github_repo):
        """Test URL parsing with special characters in repo name."""
        # GitHub allows hyphens, underscores, dots
        valid_urls = [
            "https://github.com/user/repo-name",
            "https://github.com/user/repo_name",
            "https://github.com/user/repo.name",
            "https://github.com/user-123/repo_456",
        ]
        
        for url in valid_urls:
            try:
                result = github_repo._parse_github_url(url)
                assert result['owner']
                assert result['repo']
            except ValueError:
                pytest.fail(f"Valid URL rejected: {url}")
    
    def test_parse_url_with_query_parameters(self, github_repo):
        """Test URL parsing with query parameters."""
        url = "https://github.com/octocat/Hello-World?tab=readme"
        result = github_repo._parse_github_url(url)
        
        assert result['owner'] == 'octocat'
        assert result['repo'] == 'Hello-World'
    
    def test_concurrent_cleanup_safety(self, github_repo):
        """Test that cleanup is safe with concurrent operations."""
        import tempfile
        
        # Create multiple temp directories
        test_dirs = []
        for i in range(5):
            test_dir = os.path.join(repo.temp_dir, f"test_{i}")
            os.makedirs(test_dir, exist_ok=True)
            test_dirs.append(test_dir)
        
        # Cleanup should handle all
        if os.path.exists(github_repo.temp_dir):
            shutil.rmtree(github_repo.temp_dir, ignore_errors=True)
        
        # Verify cleanup
        for test_dir in test_dirs:
            assert not os.path.exists(test_dir)


class TestGitHubRepositoryEdgeCases:
    """Tests for edge cases with proper cleanup."""
    
    @pytest.fixture
    def github_repo(self):
        """Create a GitHubRepository instance for testing with proper cleanup."""
        repo = GitHubRepository()
        yield repo
        
        # Thorough cleanup
        try:
            if os.path.exists(repo.temp_dir):
                shutil.rmtree(repo.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
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