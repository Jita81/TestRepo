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

class GitHubRepository:
    """Handles GitHub repository operations."""
    
    def __init__(self):
        self.temp_dir = "temp_repos"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def clone_repository(self, github_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Path to the cloned repository
        """
        try:
            # Parse GitHub URL to get repo info
            repo_info = self._parse_github_url(github_url)
            
            # Create unique directory for this repo
            repo_dir = os.path.join(self.temp_dir, f"{repo_info['owner']}_{repo_info['repo']}")
            
            # Clone the repository
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            
            git.Repo.clone_from(github_url, repo_dir)
            
            # Get additional metadata from GitHub API
            metadata = await self._get_repository_metadata(repo_info['owner'], repo_info['repo'])
            
            # Save metadata for later use
            metadata_file = os.path.join(repo_dir, ".github_metadata.json")
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return repo_dir
            
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repository name."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        return {
            'owner': path_parts[0],
            'repo': path_parts[1].replace('.git', '')
        }
    
    async def _get_repository_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get additional metadata from GitHub API."""
        try:
            # Use GitHub API to get repository information
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Failed to fetch metadata: {str(e)}"}
    
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