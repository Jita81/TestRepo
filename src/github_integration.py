"""
GitHub Integration Module
Handles cloning repositories and extracting metadata.
"""

import git
import os
import tempfile
import requests
import shutil
from urllib.parse import urlparse
from pathlib import Path
import asyncio
from typing import Dict, Any, Optional
from src.logger_config import get_logger

# Setup logger
logger = get_logger(__name__)

class GitHubRepository:
    """Handles GitHub repository operations."""
    
    def __init__(self):
        self.temp_dir = "temp_repos"
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"GitHubRepository initialized with temp directory: {self.temp_dir}")
    
    async def clone_repository(self, github_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Path to the cloned repository
        """
        logger.info(f"Starting repository clone: {github_url}")
        
        try:
            # Parse GitHub URL to get repo info
            logger.debug(f"Parsing GitHub URL: {github_url}")
            repo_info = self._parse_github_url(github_url)
            logger.info(
                f"Parsed repository info",
                extra={
                    "owner": repo_info['owner'],
                    "repo": repo_info['repo']
                }
            )
            
            # Create unique directory for this repo
            repo_dir = os.path.join(self.temp_dir, f"{repo_info['owner']}_{repo_info['repo']}")
            
            # Clone the repository
            if os.path.exists(repo_dir):
                logger.debug(f"Removing existing repository directory: {repo_dir}")
                shutil.rmtree(repo_dir)
            
            logger.info(f"Cloning repository to: {repo_dir}")
            git.Repo.clone_from(github_url, repo_dir)
            logger.info(f"Repository cloned successfully")
            
            # Get additional metadata from GitHub API
            logger.debug("Fetching repository metadata from GitHub API")
            metadata = await self._get_repository_metadata(repo_info['owner'], repo_info['repo'])
            
            # Save metadata for later use
            metadata_file = os.path.join(repo_dir, ".github_metadata.json")
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.debug(f"Metadata saved to: {metadata_file}")
            
            logger.info(
                f"Repository clone completed",
                extra={
                    "repo_path": repo_dir,
                    "owner": repo_info['owner'],
                    "repo": repo_info['repo']
                }
            )
            
            return repo_dir
            
        except git.GitCommandError as e:
            logger.error(
                f"Git clone failed for {github_url}",
                exc_info=True,
                extra={"github_url": github_url, "git_error": str(e)}
            )
            raise Exception(f"Failed to clone repository: {str(e)}")
        except Exception as e:
            logger.error(
                f"Repository clone failed for {github_url}",
                exc_info=True,
                extra={"github_url": github_url}
            )
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repository name."""
        logger.debug(f"Parsing URL: {url}")
        
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            logger.error(f"Invalid GitHub URL format: {url}")
            raise ValueError("Invalid GitHub URL format")
        
        result = {
            'owner': path_parts[0],
            'repo': path_parts[1].replace('.git', '')
        }
        
        logger.debug(f"Parsed owner: {result['owner']}, repo: {result['repo']}")
        return result
    
    async def _get_repository_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get additional metadata from GitHub API."""
        logger.debug(f"Fetching metadata for {owner}/{repo}")
        
        try:
            # Use GitHub API to get repository information
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            logger.debug(f"GitHub API URL: {api_url}")
            
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                metadata = response.json()
                logger.info(
                    f"Successfully fetched metadata for {owner}/{repo}",
                    extra={
                        "stars": metadata.get('stargazers_count'),
                        "language": metadata.get('language'),
                        "size": metadata.get('size')
                    }
                )
                return metadata
            else:
                logger.warning(
                    f"GitHub API request failed for {owner}/{repo}",
                    extra={
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    }
                )
                return {"error": f"API request failed with status {response.status_code}"}
                
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch metadata for {owner}/{repo}",
                exc_info=True,
                extra={"owner": owner, "repo": repo}
            )
            return {"error": f"Failed to fetch metadata: {str(e)}"}
    
    def get_readme_path(self, repo_path: str) -> Optional[str]:
        """Find the README file in the repository."""
        logger.debug(f"Searching for README in: {repo_path}")
        
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
                logger.info(f"Found README file: {readme_path}")
                return readme_path
        
        logger.warning(f"No README file found in: {repo_path}")
        return None
    
    def get_project_files(self, repo_path: str) -> list:
        """Get list of important project files."""
        logger.debug(f"Scanning project files in: {repo_path}")
        
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
        
        logger.info(
            f"Found {len(project_files)} important project files",
            extra={"file_count": len(project_files)}
        )
        
        return project_files