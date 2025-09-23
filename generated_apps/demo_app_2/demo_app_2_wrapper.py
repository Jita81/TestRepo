#!/usr/bin/env python3
"""
Generated App Wrapper
Auto-generated from GitHub repository
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

class AppWrapper:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.project_type = "python"
        
    def install_dependencies(self):
        """Install required dependencies."""
        requirements_file = self.app_dir / "requirements.txt"
        if requirements_file.exists():
            print("Installing dependencies...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                             check=True, capture_output=True)
                print("Dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install dependencies: {e}")
                return False
        return True
    
    def run_application(self):
        """Run the main application."""
        print("Starting application...")
        
        # Install dependencies first
        if not self.install_dependencies():
            print("Failed to install dependencies. Please install manually.")
            return
        
        # Try to run based on project type
        if self.project_type == "python":
            self._run_python_app()
        elif self.project_type == "nodejs":
            self._run_nodejs_app()
        else:
            self._run_generic_app()
    
    def _run_python_app(self):
        """Run Python application."""
        entry_points = ['docs_src/request_files/tutorial003_an.py', 'docs_src/custom_response/tutorial009b.py', 'docs_src/custom_response/tutorial005.py', 'docs_src/settings/app02/main.py', 'docs_src/request_files/tutorial002_an_py39.py', 'docs_src/settings/app03_an/main.py', 'docs_src/settings/app02_an_py39/main.py', 'docs_src/request_files/tutorial003.py', 'docs_src/request_files/tutorial003_an_py39.py', 'docs_src/custom_response/tutorial009.py', 'scripts/deploy_docs_status.py', 'docs_src/debugging/tutorial001.py', 'docs_src/settings/app03/main.py', 'docs_src/settings/app01/main.py', 'docs_src/bigger_applications/app_an_py39/main.py', 'docs_src/app_testing/app_b_py310/main.py', 'docs_src/app_testing/app_b_an_py39/main.py', 'docs_src/custom_response/tutorial009c.py', 'scripts/sponsors.py', 'docs/en/docs/features.md', 'docs_src/advanced_middleware/tutorial003.py', 'docs_src/custom_response/tutorial008.py', 'docs_src/request_files/tutorial002_an.py', 'docs_src/app_testing/app_b/main.py', 'docs_src/bigger_applications/app_an/main.py', 'fastapi/__main__.py', 'docs_src/advanced_middleware/tutorial001.py', 'docs_src/request_files/tutorial002_py39.py', 'scripts/topic_repos.py', 'docs_src/request_files/tutorial002.py', 'docs_src/settings/app03_an_py39/main.py', 'docs_src/custom_response/tutorial007.py', 'docs_src/async_tests/main.py', 'docs_src/cors/tutorial001.py', 'fastapi/cli.py', 'docs_src/request_files/tutorial003_py39.py', 'docs/zh-hant/docs/features.md', 'docs_src/app_testing/app_b_an_py310/main.py', 'docs_src/app_testing/app_b_an/main.py', 'docs_src/settings/app02_an/main.py', 'docs/zh/docs/features.md', 'docs/em/docs/features.md', 'docs_src/bigger_applications/app/main.py', 'docs_src/advanced_middleware/tutorial002.py', 'docs_src/app_testing/main.py']
        
        for entry_point in entry_points:
            if entry_point.endswith('.py'):
                print(f"Running {entry_point}...")
                try:
                    subprocess.run([sys.executable, entry_point], cwd=self.app_dir, check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Failed to run {entry_point}: {e}")
                    continue
        
        print("No valid Python entry point found.")
    
    def _run_nodejs_app(self):
        """Run Node.js application."""
        package_json = self.app_dir / "package.json"
        if package_json.exists():
            print("Installing npm dependencies...")
            subprocess.run(["npm", "install"], cwd=self.app_dir, check=True)
            
            print("Starting Node.js application...")
            subprocess.run(["npm", "start"], cwd=self.app_dir, check=True)
        else:
            print("No package.json found for Node.js app.")
    
    def _run_generic_app(self):
        """Run generic application."""
        print("Attempting to run application...")
        # Try common run commands
        run_commands = []
        
        for cmd in run_commands:
            if cmd:
                print(f"Trying command: {cmd}")
                try:
                    subprocess.run(cmd.split(), cwd=self.app_dir, check=True)
                    return
                except subprocess.CalledProcessError:
                    continue
        
        print("Could not determine how to run the application.")
        print("Please check the README for manual instructions.")

if __name__ == "__main__":
    app = AppWrapper()
    app.run_application()
