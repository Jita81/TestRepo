"""
GitHub Integration Module
Handles cloning repositories and extracting metadata.
"""

import git
import os
import tempfile
import requests
from urllib.parse import urlparse
from pathlib import Path
import asyncio
from typing import Dict, Any, Optional
import shutil
import logging
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configure logging
logger = logging.getLogger(__name__)

class GitHubRepositoryError(Exception):
    """Custom exception for GitHub repository operations."""
    pass

class GitHubRepository:
    """Handles GitHub repository operations with comprehensive error handling."""
    
    def __init__(self):
        self.temp_dir = "temp_repos"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.max_retries = 3
        self.timeout = 30
    
    async def clone_repository(self, github_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory with comprehensive error handling.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Path to the cloned repository
            
        Raises:
            GitHubRepositoryError: If cloning fails for any reason
        """
        if not github_url:
            raise GitHubRepositoryError("GitHub URL cannot be empty")
        
        try:
            # Validate and parse GitHub URL
            try:
                repo_info = self._parse_github_url(github_url)
                logger.info(f"Parsed repository: {repo_info['owner']}/{repo_info['repo']}")
            except ValueError as e:
                raise GitHubRepositoryError(f"Invalid GitHub URL format: {str(e)}")
            
            # Create unique directory for this repo
            repo_dir = os.path.join(self.temp_dir, f"{repo_info['owner']}_{repo_info['repo']}")
            
            # Clean up existing directory if it exists
            if os.path.exists(repo_dir):
                try:
                    shutil.rmtree(repo_dir)
                    logger.info(f"Removed existing directory: {repo_dir}")
                except PermissionError as e:
                    raise GitHubRepositoryError(f"Cannot remove existing directory: {str(e)}")
            
            # Clone the repository with retry logic
            clone_url = github_url
            if self.github_token and "github.com" in github_url:
                # Add authentication if token is available
                parsed = urlparse(github_url)
                clone_url = f"https://{self.github_token}@{parsed.netloc}{parsed.path}"
            
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Cloning repository (attempt {attempt + 1}/{self.max_retries})...")
                    git.Repo.clone_from(
                        clone_url, 
                        repo_dir,
                        depth=1,  # Shallow clone for performance
                        single_branch=True  # Only clone default branch
                    )
                    logger.info(f"Repository cloned successfully to: {repo_dir}")
                    break
                except git.GitCommandError as e:
                    if "not found" in str(e).lower() or "404" in str(e):
                        raise GitHubRepositoryError(f"Repository not found or inaccessible: {github_url}")
                    elif "authentication" in str(e).lower() or "403" in str(e):
                        raise GitHubRepositoryError(f"Authentication failed. Repository may be private.")
                    elif attempt == self.max_retries - 1:
                        raise GitHubRepositoryError(f"Git clone failed after {self.max_retries} attempts: {str(e)}")
                    else:
                        logger.warning(f"Clone attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise GitHubRepositoryError(f"Unexpected error during clone: {str(e)}")
                    await asyncio.sleep(2 ** attempt)
            
            # Verify repository was cloned successfully
            if not os.path.exists(repo_dir) or not os.path.isdir(repo_dir):
                raise GitHubRepositoryError("Repository directory was not created")
            
            # Get additional metadata from GitHub API
            try:
                metadata = await self._get_repository_metadata(repo_info['owner'], repo_info['repo'])
                
                # Save metadata for later use
                metadata_file = os.path.join(repo_dir, ".github_metadata.json")
                import json
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                logger.info("Repository metadata saved")
            except Exception as e:
                # Metadata fetch failure is not critical
                logger.warning(f"Failed to fetch repository metadata: {str(e)}")
            
            return repo_dir
            
        except GitHubRepositoryError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in clone_repository: {str(e)}", exc_info=True)
            raise GitHubRepositoryError(f"Failed to clone repository: {str(e)}")
    
    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """
        Parse GitHub URL to extract owner and repository name.
        
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git
        """
        try:
            # Handle SSH URLs
            if url.startswith("git@"):
                # git@github.com:owner/repo.git
                url = url.replace("git@github.com:", "https://github.com/")
            
            # Validate it's a GitHub URL
            if "github.com" not in url:
                raise ValueError("URL must be from github.com")
            
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise ValueError("URL must contain owner and repository name (e.g., github.com/owner/repo)")
            
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            
            # Validate owner and repo names
            if not owner or not repo:
                raise ValueError("Owner and repository name cannot be empty")
            
            # Basic validation of GitHub naming rules
            import re
            if not re.match(r'^[a-zA-Z0-9._-]+$', owner) or not re.match(r'^[a-zA-Z0-9._-]+$', repo):
                raise ValueError("Invalid GitHub username or repository name")
            
            return {
                'owner': owner,
                'repo': repo
            }
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL: {str(e)}")
    
    async def _get_repository_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get additional metadata from GitHub API with retry logic and error handling.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with repository metadata or error information
        """
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {}
        
        # Add authentication if token is available
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Fetching metadata (attempt {attempt + 1}/{self.max_retries})")
                response = requests.get(
                    api_url, 
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    logger.info("Repository metadata fetched successfully")
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Repository {owner}/{repo} not found via API")
                    return {"error": "Repository not found", "status": 404}
                elif response.status_code == 403:
                    logger.warning("Rate limit exceeded or authentication required")
                    return {"error": "API rate limit exceeded or authentication required", "status": 403}
                elif response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"GitHub API server error, retrying...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return {"error": f"GitHub API server error: {response.status_code}", "status": response.status_code}
                else:
                    return {"error": f"API request failed with status {response.status_code}", "status": response.status_code}
                    
            except Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"error": "Request timeout - GitHub API is not responding"}
            except ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"error": f"Network connection error: {str(e)}"}
            except RequestException as e:
                logger.error(f"Request error: {str(e)}")
                return {"error": f"Failed to fetch metadata: {str(e)}"}
            except Exception as e:
                logger.error(f"Unexpected error fetching metadata: {str(e)}", exc_info=True)
                return {"error": f"Unexpected error: {str(e)}"}
        
        return {"error": "Failed to fetch metadata after all retry attempts"}
    
    def get_readme_path(self, repo_path: str) -> Optional[str]:
        """Find the README file in the repository."""
        readme_files = [
            "README.md",
            "README.rst", 
            "README.txt",
            "readme.md",
            "readme.rst",
            "readme.txt"
        ]
        
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                return readme_path
        
        return None
    
    def get_project_files(self, repo_path: str) -> list:
        """Get list of important project files."""
        important_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php',
            '.rb', '.swift', '.kt', '.scala', '.r', '.m', '.h', '.hpp',
            'package.json', 'requirements.txt', 'setup.py', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'Dockerfile', 'docker-compose.yml'
        }
        
        project_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build', 'dist']]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in important_extensions or file in important_extensions:
                    project_files.append(file_path)
        
        return project_files