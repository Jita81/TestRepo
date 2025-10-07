"""
README Parser Module
Extracts installation instructions, dependencies, and usage patterns from README files.
"""

import re
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import markdown
from bs4 import BeautifulSoup
from src.logger_config import get_logger

# Setup logger
logger = get_logger(__name__)

class ReadmeParser:
    """Parses README files to extract actionable information."""
    
    def __init__(self):
        logger.info("ReadmeParser initialized")
        
        self.installation_patterns = [
            r'install.*?(\w+)',
            r'pip install',
            r'npm install',
            r'yarn install',
            r'cargo install',
            r'go install',
            r'gem install',
            r'composer install',
            r'./install',
            r'make install',
            r'cmake.*install',
            r'./configure.*make.*install'
        ]
        
        self.dependency_patterns = [
            r'requirements\.txt',
            r'package\.json',
            r'Cargo\.toml',
            r'pom\.xml',
            r'build\.gradle',
            r'Gemfile',
            r'composer\.json',
            r'go\.mod',
            r'Dockerfile'
        ]
        
        self.run_patterns = [
            r'python.*\.py',
            r'node.*\.js',
            r'java.*\.jar',
            r'\./.*',
            r'docker run',
            r'docker-compose up',
            r'npm start',
            r'yarn start',
            r'cargo run',
            r'go run'
        ]
    
    async def parse_readme(self, repo_path: str) -> Dict[str, Any]:
        """
        Parse README file and extract structured information.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary containing parsed README information
        """
        logger.info(f"Starting README parsing for: {repo_path}")
        
        readme_path = self._find_readme_file(repo_path)
        if not readme_path:
            logger.warning(f"No README file found in: {repo_path}")
            return {"error": "No README file found"}
        
        logger.info(f"README file found: {readme_path}")
        
        # Read and parse the README
        logger.debug("Reading README file content")
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        logger.info(f"README content length: {len(content)} characters")
        
        # Convert markdown to HTML for better parsing
        logger.debug("Converting markdown to HTML")
        html_content = markdown.markdown(content)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract structured information
        logger.debug("Extracting title")
        title = self._extract_title(soup)
        
        logger.debug("Extracting description")
        description = self._extract_description(soup)
        
        logger.debug("Extracting installation instructions")
        installation_instructions = self._extract_installation_instructions(content)
        
        logger.debug("Extracting dependencies")
        dependencies = self._extract_dependencies(content, repo_path)
        
        logger.debug("Extracting usage instructions")
        usage_instructions = self._extract_usage_instructions(content)
        
        logger.debug("Extracting configuration")
        configuration = self._extract_configuration(content)
        
        logger.debug("Extracting examples")
        examples = self._extract_examples(content)
        
        logger.debug("Extracting troubleshooting info")
        troubleshooting = self._extract_troubleshooting(content)
        
        logger.debug("Detecting project type")
        project_type = self._detect_project_type(repo_path)
        
        logger.debug("Identifying main files")
        main_files = self._identify_main_files(repo_path)
        
        parsed_data = {
            'raw_content': content,
            'html_content': html_content,
            'title': title,
            'description': description,
            'installation_instructions': installation_instructions,
            'dependencies': dependencies,
            'usage_instructions': usage_instructions,
            'configuration': configuration,
            'examples': examples,
            'troubleshooting': troubleshooting,
            'project_type': project_type,
            'main_files': main_files
        }
        
        logger.info(
            "README parsing completed",
            extra={
                "title": title,
                "project_type": project_type,
                "dependencies_count": len(dependencies.get('packages', [])),
                "installation_steps": len(installation_instructions),
                "main_files": len(main_files)
            }
        )
        
        return parsed_data
    
    def _find_readme_file(self, repo_path: str) -> Optional[str]:
        """Find the README file in the repository."""
        logger.debug(f"Searching for README file in: {repo_path}")
        
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
                logger.debug(f"Found README: {readme_file}")
                return readme_path
        
        logger.debug("No README file found")
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the main title from the README."""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Fallback to first heading
        heading = soup.find(['h1', 'h2', 'h3'])
        if heading:
            return heading.get_text().strip()
        
        return "Untitled Project"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract project description."""
        # Look for description after title
        h1 = soup.find('h1')
        if h1:
            next_p = h1.find_next('p')
            if next_p:
                return next_p.get_text().strip()
        
        # Look for any paragraph with substantial content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:  # Substantial description
                return text
        
        return "No description available"
    
    def _extract_installation_instructions(self, content: str) -> List[str]:
        """Extract installation instructions from README."""
        instructions = []
        
        # Look for installation section
        install_section = self._extract_section(content, ['install', 'setup', 'getting started'])
        if install_section:
            # Extract code blocks
            code_blocks = re.findall(r'```[\s\S]*?```', install_section)
            for block in code_blocks:
                # Remove markdown code block markers
                clean_block = re.sub(r'^```\w*\n?', '', block).strip()
                clean_block = re.sub(r'\n?```$', '', clean_block).strip()
                if clean_block:
                    instructions.append(clean_block)
        
        # Look for inline installation commands
        for pattern in self.installation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            instructions.extend(matches)
        
        return list(set(instructions))  # Remove duplicates
    
    def _extract_dependencies(self, content: str, repo_path: str) -> Dict[str, Any]:
        """Extract dependency information."""
        dependencies = {
            'files': [],
            'packages': [],
            'system_requirements': []
        }
        
        # Find dependency files
        for pattern in self.dependency_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                dependencies['files'].append(pattern)
        
        # Check if dependency files actually exist
        for dep_file in dependencies['files']:
            file_path = os.path.join(repo_path, dep_file)
            if os.path.exists(file_path):
                dependencies['packages'].extend(self._parse_dependency_file(file_path))
        
        # Extract system requirements
        requirements_section = self._extract_section(content, ['requirements', 'prerequisites', 'system requirements'])
        if requirements_section:
            dependencies['system_requirements'] = self._extract_requirements_list(requirements_section)
        
        return dependencies
    
    def _extract_usage_instructions(self, content: str) -> List[str]:
        """Extract usage instructions."""
        instructions = []
        
        # Look for usage section
        usage_section = self._extract_section(content, ['usage', 'how to use', 'examples', 'getting started'])
        if usage_section:
            # Extract code blocks
            code_blocks = re.findall(r'```[\s\S]*?```', usage_section)
            for block in code_blocks:
                clean_block = re.sub(r'^```\w*\n?', '', block).strip()
                clean_block = re.sub(r'\n?```$', '', clean_block).strip()
                if clean_block:
                    instructions.append(clean_block)
        
        # Look for run commands
        for pattern in self.run_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            instructions.extend(matches)
        
        return list(set(instructions))
    
    def _extract_configuration(self, content: str) -> Dict[str, Any]:
        """Extract configuration information."""
        config = {
            'environment_variables': [],
            'config_files': [],
            'settings': []
        }
        
        # Look for environment variables
        env_vars = re.findall(r'(\w+)=["\']?([^"\'\s]+)["\']?', content)
        config['environment_variables'] = [f"{var}={value}" for var, value in env_vars]
        
        # Look for config files
        config_files = re.findall(r'(\w+\.(?:json|yaml|yml|toml|ini|conf|cfg))', content, re.IGNORECASE)
        config['config_files'] = list(set(config_files))
        
        return config
    
    def _extract_examples(self, content: str) -> List[str]:
        """Extract code examples."""
        examples = []
        
        # Extract all code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        for block in code_blocks:
            clean_block = re.sub(r'^```\w*\n?', '', block).strip()
            clean_block = re.sub(r'\n?```$', '', clean_block).strip()
            if clean_block and len(clean_block) > 10:  # Substantial code
                examples.append(clean_block)
        
        return examples
    
    def _extract_troubleshooting(self, content: str) -> List[str]:
        """Extract troubleshooting information."""
        troubleshooting_section = self._extract_section(content, ['troubleshooting', 'troubleshoot', 'issues', 'problems', 'faq'])
        if troubleshooting_section:
            # Extract bullet points or numbered lists
            items = re.findall(r'[-*]\s+(.+)|^\d+\.\s+(.+)', troubleshooting_section, re.MULTILINE)
            return [item[0] or item[1] for item in items if item[0] or item[1]]
        
        return []
    
    def _detect_project_type(self, repo_path: str) -> str:
        """Detect the type of project based on files present."""
        logger.debug(f"Detecting project type for: {repo_path}")
        
        files = os.listdir(repo_path)
        
        project_type = 'unknown'
        if 'package.json' in files:
            project_type = 'nodejs'
        elif 'requirements.txt' in files or any(f.endswith('.py') for f in files):
            project_type = 'python'
        elif 'Cargo.toml' in files:
            project_type = 'rust'
        elif 'pom.xml' in files:
            project_type = 'java'
        elif 'Dockerfile' in files:
            project_type = 'docker'
        elif any(f.endswith('.go') for f in files):
            project_type = 'go'
        elif any(f.endswith('.rs') for f in files):
            project_type = 'rust'
        
        logger.info(f"Detected project type: {project_type}")
        return project_type
    
    def _identify_main_files(self, repo_path: str) -> List[str]:
        """Identify main entry point files."""
        logger.debug(f"Identifying main files in: {repo_path}")
        
        main_files = []
        
        # Common main file patterns
        main_patterns = [
            'main.py', 'app.py', 'index.py', '__main__.py',
            'main.js', 'index.js', 'app.js', 'server.js',
            'main.go', 'main.rs', 'main.cpp', 'main.c',
            'Main.java', 'Application.java'
        ]
        
        for pattern in main_patterns:
            file_path = os.path.join(repo_path, pattern)
            if os.path.exists(file_path):
                main_files.append(pattern)
                logger.debug(f"Found main file: {pattern}")
        
        logger.info(f"Identified {len(main_files)} main files")
        return main_files
    
    def _extract_section(self, content: str, section_names: List[str]) -> str:
        """Extract a specific section from the content."""
        content_lower = content.lower()
        
        for section_name in section_names:
            # Look for headers with the section name
            pattern = rf'^#+\s*{re.escape(section_name)}.*?\n(.*?)(?=^#+|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_requirements_list(self, content: str) -> List[str]:
        """Extract requirements from a requirements section."""
        requirements = []
        
        # Look for bullet points or numbered lists
        items = re.findall(r'[-*]\s+(.+)|^\d+\.\s+(.+)', content, re.MULTILINE)
        for item in items:
            req = item[0] or item[1]
            if req and len(req.strip()) > 3:
                requirements.append(req.strip())
        
        return requirements
    
    def _parse_dependency_file(self, file_path: str) -> List[str]:
        """Parse a specific dependency file."""
        logger.debug(f"Parsing dependency file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith('requirements.txt'):
                deps = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                logger.info(f"Parsed {len(deps)} dependencies from requirements.txt")
                return deps
            elif file_path.endswith('package.json'):
                import json
                data = json.loads(content)
                deps = []
                if 'dependencies' in data:
                    deps.extend(data['dependencies'].keys())
                if 'devDependencies' in data:
                    deps.extend(data['devDependencies'].keys())
                logger.info(f"Parsed {len(deps)} dependencies from package.json")
                return deps
            # Add more parsers for other file types as needed
            
        except Exception as e:
            logger.warning(
                f"Failed to parse dependency file: {file_path}",
                extra={"file_path": file_path, "error": str(e)}
            )
        
        return []