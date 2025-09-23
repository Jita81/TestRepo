"""
Agentic Coder Module
Uses AI to analyze codebases and generate working applications.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgenticCoder:
    """AI-powered code analysis and application generation."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.max_tokens = 4000
        self.model = "gpt-4"
    
    async def analyze_codebase(self, repo_path: str, readme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the codebase using AI to understand structure and requirements.
        
        Args:
            repo_path: Path to the repository
            readme_data: Parsed README information
            
        Returns:
            AI analysis of the codebase
        """
        try:
            # Get project files and structure
            project_files = self._get_project_structure(repo_path)
            
            # Read key files for analysis
            key_files_content = self._read_key_files(repo_path, project_files)
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(
                readme_data, 
                project_files, 
                key_files_content
            )
            
            # Get AI analysis
            analysis = await self._get_ai_analysis(analysis_prompt)
            
            return {
                'project_structure': project_files,
                'ai_analysis': analysis,
                'entry_points': self._identify_entry_points(key_files_content),
                'dependencies': self._extract_ai_dependencies(analysis),
                'build_instructions': self._extract_build_instructions(analysis),
                'runtime_requirements': self._extract_runtime_requirements(analysis)
            }
            
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def generate_app_wrapper(self, analysis: Dict[str, Any], target_platform: str) -> str:
        """
        Generate application wrapper code based on AI analysis.
        
        Args:
            analysis: AI analysis of the codebase
            target_platform: Target platform (executable, docker, web)
            
        Returns:
            Generated wrapper code
        """
        try:
            generation_prompt = self._create_generation_prompt(analysis, target_platform)
            wrapper_code = await self._get_ai_generation(generation_prompt)
            return wrapper_code
            
        except Exception as e:
            return f"# Error generating wrapper: {str(e)}"
    
    def _get_project_structure(self, repo_path: str) -> Dict[str, Any]:
        """Get the project file structure."""
        structure = {
            'files': [],
            'directories': [],
            'extensions': set(),
            'size': 0
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'target', 'build', 'dist', 
                'venv', 'env', '.git', 'test', 'tests', '__tests__'
            ]]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                structure['files'].append({
                    'path': rel_path,
                    'size': os.path.getsize(file_path),
                    'extension': os.path.splitext(file)[1]
                })
                
                structure['extensions'].add(os.path.splitext(file)[1])
                structure['size'] += os.path.getsize(file_path)
        
        structure['extensions'] = list(structure['extensions'])
        return structure
    
    def _read_key_files(self, repo_path: str, project_files: Dict[str, Any]) -> Dict[str, str]:
        """Read content of key files for analysis."""
        key_files = {}
        
        # Prioritize important files
        important_files = [
            'main.py', 'app.py', 'index.py', '__main__.py',
            'main.js', 'index.js', 'app.js', 'server.js',
            'package.json', 'requirements.txt', 'setup.py',
            'Dockerfile', 'docker-compose.yml',
            'Cargo.toml', 'pom.xml', 'build.gradle'
        ]
        
        for file_info in project_files['files']:
            file_path = file_info['path']
            filename = os.path.basename(file_path)
            
            if filename in important_files or file_info['size'] < 10000:  # Skip very large files
                full_path = os.path.join(repo_path, file_path)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        key_files[file_path] = content[:5000]  # Limit content size
                except Exception as e:
                    key_files[file_path] = f"Error reading file: {str(e)}"
        
        return key_files
    
    def _create_analysis_prompt(self, readme_data: Dict[str, Any], 
                              project_files: Dict[str, Any], 
                              key_files_content: Dict[str, str]) -> str:
        """Create prompt for AI analysis."""
        prompt = f"""
        Analyze this codebase and provide a comprehensive understanding for generating a working application.
        
        README Information:
        - Title: {readme_data.get('title', 'Unknown')}
        - Description: {readme_data.get('description', 'No description')}
        - Project Type: {readme_data.get('project_type', 'Unknown')}
        - Installation Instructions: {readme_data.get('installation_instructions', [])}
        - Dependencies: {readme_data.get('dependencies', {})}
        - Usage Instructions: {readme_data.get('usage_instructions', [])}
        
        Project Structure:
        - Total files: {len(project_files['files'])}
        - File extensions: {project_files['extensions']}
        - Total size: {project_files['size']} bytes
        
        Key Files Content:
        """
        
        for file_path, content in key_files_content.items():
            prompt += f"\n--- {file_path} ---\n{content}\n"
        
        prompt += """
        
        Please analyze this codebase and provide:
        1. Main entry point(s) and how to run the application
        2. Required dependencies and how to install them
        3. Build process and configuration needed
        4. Runtime requirements (environment variables, ports, etc.)
        5. How to package this into a standalone executable
        6. Any special considerations or gotchas
        
        Format your response as JSON with the following structure:
        {
            "entry_points": ["list of main files to run"],
            "dependencies": ["list of required packages"],
            "build_commands": ["list of build/install commands"],
            "run_commands": ["list of commands to run the app"],
            "environment_variables": ["list of required env vars"],
            "ports": ["list of ports the app uses"],
            "packaging_strategy": "strategy for creating executable",
            "special_requirements": ["any special setup needed"],
            "confidence_score": 0.8
        }
        """
        
        return prompt
    
    def _create_generation_prompt(self, analysis: Dict[str, Any], target_platform: str) -> str:
        """Create prompt for generating application wrapper."""
        prompt = f"""
        Generate a {target_platform} wrapper for this application based on the following analysis:
        
        Analysis: {json.dumps(analysis, indent=2)}
        
        Create a complete, working wrapper that:
        1. Handles all dependencies automatically
        2. Provides a simple interface to run the application
        3. Includes error handling and user feedback
        4. Works on the target platform: {target_platform}
        
        For executable: Create a Python script that can be packaged with PyInstaller
        For docker: Create a Dockerfile and docker-compose.yml
        For web: Create a web interface that runs the application
        
        Include all necessary files and instructions.
        """
        
        return prompt
    
    async def _get_ai_analysis(self, prompt: str) -> Dict[str, Any]:
        """Get AI analysis using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer who specializes in analyzing codebases and creating working applications. Provide detailed, accurate analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"analysis": content}
                
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def _get_ai_generation(self, prompt: str) -> str:
        """Get AI-generated code using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer who creates working application wrappers. Generate clean, functional code that works out of the box."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Error generating code: {str(e)}"
    
    def _identify_entry_points(self, key_files_content: Dict[str, str]) -> List[str]:
        """Identify potential entry points from file content."""
        entry_points = []
        
        for file_path, content in key_files_content.items():
            filename = os.path.basename(file_path)
            
            # Common entry point patterns
            if filename in ['main.py', 'app.py', 'index.py', '__main__.py', 'main.js', 'index.js', 'app.js']:
                entry_points.append(file_path)
            
            # Look for main functions or if __name__ == "__main__"
            if 'if __name__ == "__main__"' in content or 'def main(' in content:
                entry_points.append(file_path)
            
            # Look for package.json main field
            if filename == 'package.json' and '"main"' in content:
                entry_points.append(file_path)
        
        return list(set(entry_points))
    
    def _extract_ai_dependencies(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract dependencies from AI analysis."""
        if isinstance(analysis, dict) and 'dependencies' in analysis:
            return analysis['dependencies']
        return []
    
    def _extract_build_instructions(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract build instructions from AI analysis."""
        if isinstance(analysis, dict) and 'build_commands' in analysis:
            return analysis['build_commands']
        return []
    
    def _extract_runtime_requirements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract runtime requirements from AI analysis."""
        if isinstance(analysis, dict):
            return {
                'environment_variables': analysis.get('environment_variables', []),
                'ports': analysis.get('ports', []),
                'special_requirements': analysis.get('special_requirements', [])
            }
        return {}