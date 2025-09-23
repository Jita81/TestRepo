"""
App Generator Module
Generates working applications from analyzed codebases.
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import zipfile
import tarfile

class AppGenerator:
    """Generates working applications from codebases."""
    
    def __init__(self):
        self.output_dir = "generated_apps"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_app(self, repo_path: str, readme_data: Dict[str, Any], 
                          code_analysis: Dict[str, Any], app_name: str, 
                          target_platform: str) -> str:
        """
        Generate a working application from the analyzed codebase.
        
        Args:
            repo_path: Path to the repository
            readme_data: Parsed README information
            code_analysis: AI analysis of the codebase
            app_name: Name for the generated app
            target_platform: Target platform (executable, docker, web)
            
        Returns:
            Path to the generated application
        """
        try:
            # Create app directory
            app_dir = os.path.join(self.output_dir, app_name)
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)
            os.makedirs(app_dir, exist_ok=True)
            
            # Copy source code
            self._copy_source_code(repo_path, app_dir)
            
            # Generate platform-specific wrapper
            if target_platform == "executable":
                return await self._generate_executable(app_dir, readme_data, code_analysis, app_name)
            elif target_platform == "docker":
                return await self._generate_docker(app_dir, readme_data, code_analysis, app_name)
            elif target_platform == "web":
                return await self._generate_web_app(app_dir, readme_data, code_analysis, app_name)
            else:
                raise ValueError(f"Unsupported target platform: {target_platform}")
                
        except Exception as e:
            raise Exception(f"Failed to generate app: {str(e)}")
    
    def _copy_source_code(self, repo_path: str, app_dir: str):
        """Copy source code to app directory."""
        # Copy all files except common non-essential directories
        exclude_dirs = {'.git', '__pycache__', 'node_modules', 'target', 'build', 'dist', 'venv', 'env'}
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Create relative path
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                target_dir = app_dir
            else:
                target_dir = os.path.join(app_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
            
            # Copy files
            for file in files:
                if not file.startswith('.'):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    shutil.copy2(src_file, dst_file)
    
    async def _generate_executable(self, app_dir: str, readme_data: Dict[str, Any], 
                                 code_analysis: Dict[str, Any], app_name: str) -> str:
        """Generate a standalone executable."""
        try:
            # Create main wrapper script
            wrapper_script = self._create_executable_wrapper(readme_data, code_analysis)
            wrapper_path = os.path.join(app_dir, f"{app_name}_wrapper.py")
            
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_script)
            
            # Create requirements.txt
            requirements = self._extract_requirements(readme_data, code_analysis)
            req_path = os.path.join(app_dir, "requirements.txt")
            with open(req_path, 'w') as f:
                f.write('\n'.join(requirements))
            
            # Create build script
            build_script = self._create_build_script(app_name)
            build_path = os.path.join(app_dir, "build.py")
            with open(build_path, 'w') as f:
                f.write(build_script)
            
            # Create README for the generated app
            app_readme = self._create_app_readme(readme_data, code_analysis, "executable")
            readme_path = os.path.join(app_dir, "README_GENERATED_APP.md")
            with open(readme_path, 'w') as f:
                f.write(app_readme)
            
            # Try to build the executable
            try:
                result = subprocess.run([
                    "python", build_path
                ], cwd=app_dir, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Look for generated executable
                    exe_files = [f for f in os.listdir(app_dir) if f.endswith('.exe') or (os.path.isfile(os.path.join(app_dir, f)) and os.access(os.path.join(app_dir, f), os.X_OK))]
                    if exe_files:
                        return os.path.join(app_dir, exe_files[0])
                
            except Exception as e:
                print(f"Build failed, but app structure created: {e}")
            
            # Return the app directory if build failed
            return app_dir
            
        except Exception as e:
            raise Exception(f"Failed to generate executable: {str(e)}")
    
    async def _generate_docker(self, app_dir: str, readme_data: Dict[str, Any], 
                             code_analysis: Dict[str, Any], app_name: str) -> str:
        """Generate Docker container."""
        try:
            # Create Dockerfile
            dockerfile = self._create_dockerfile(readme_data, code_analysis)
            dockerfile_path = os.path.join(app_dir, "Dockerfile")
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile)
            
            # Create docker-compose.yml
            compose_file = self._create_docker_compose(readme_data, code_analysis, app_name)
            compose_path = os.path.join(app_dir, "docker-compose.yml")
            with open(compose_path, 'w') as f:
                f.write(compose_file)
            
            # Create startup script
            startup_script = self._create_docker_startup_script(readme_data, code_analysis)
            startup_path = os.path.join(app_dir, "start.sh")
            with open(startup_path, 'w') as f:
                f.write(startup_script)
            os.chmod(startup_path, 0o755)
            
            # Create README for the generated app
            app_readme = self._create_app_readme(readme_data, code_analysis, "docker")
            readme_path = os.path.join(app_dir, "README_GENERATED_APP.md")
            with open(readme_path, 'w') as f:
                f.write(app_readme)
            
            return app_dir
            
        except Exception as e:
            raise Exception(f"Failed to generate Docker app: {str(e)}")
    
    async def _generate_web_app(self, app_dir: str, readme_data: Dict[str, Any], 
                              code_analysis: Dict[str, Any], app_name: str) -> str:
        """Generate web application."""
        try:
            # Create web wrapper
            web_wrapper = self._create_web_wrapper(readme_data, code_analysis)
            web_path = os.path.join(app_dir, "web_app.py")
            with open(web_path, 'w') as f:
                f.write(web_wrapper)
            
            # Create HTML template
            html_template = self._create_html_template(readme_data, code_analysis)
            template_path = os.path.join(app_dir, "templates")
            os.makedirs(template_path, exist_ok=True)
            with open(os.path.join(template_path, "index.html"), 'w') as f:
                f.write(html_template)
            
            # Create static files directory
            static_path = os.path.join(app_dir, "static")
            os.makedirs(static_path, exist_ok=True)
            
            # Create requirements.txt
            requirements = self._extract_requirements(readme_data, code_analysis)
            requirements.extend(['fastapi', 'uvicorn', 'jinja2'])
            req_path = os.path.join(app_dir, "requirements.txt")
            with open(req_path, 'w') as f:
                f.write('\n'.join(requirements))
            
            # Create README for the generated app
            app_readme = self._create_app_readme(readme_data, code_analysis, "web")
            readme_path = os.path.join(app_dir, "README_GENERATED_APP.md")
            with open(readme_path, 'w') as f:
                f.write(app_readme)
            
            return app_dir
            
        except Exception as e:
            raise Exception(f"Failed to generate web app: {str(e)}")
    
    def _create_executable_wrapper(self, readme_data: Dict[str, Any], 
                                 code_analysis: Dict[str, Any]) -> str:
        """Create wrapper script for executable."""
        project_type = readme_data.get('project_type', 'unknown')
        entry_points = code_analysis.get('entry_points', [])
        
        wrapper = f'''#!/usr/bin/env python3
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
        self.project_type = "{project_type}"
        
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
                print(f"Failed to install dependencies: {{e}}")
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
        entry_points = {entry_points}
        
        for entry_point in entry_points:
            if entry_point.endswith('.py'):
                print(f"Running {{entry_point}}...")
                try:
                    subprocess.run([sys.executable, entry_point], cwd=self.app_dir, check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Failed to run {{entry_point}}: {{e}}")
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
        run_commands = {readme_data.get('usage_instructions', [])}
        
        for cmd in run_commands:
            if cmd:
                print(f"Trying command: {{cmd}}")
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
'''
        return wrapper
    
    def _create_dockerfile(self, readme_data: Dict[str, Any], 
                          code_analysis: Dict[str, Any]) -> str:
        """Create Dockerfile for the application."""
        project_type = readme_data.get('project_type', 'python')
        
        if project_type == 'python':
            base_image = "python:3.9-slim"
            dockerfile = f'''FROM {base_image}

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port (adjust as needed)
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
'''
        elif project_type == 'nodejs':
            base_image = "node:16-slim"
            dockerfile = f'''FROM {base_image}

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
'''
        else:
            # Generic Dockerfile
            dockerfile = f'''FROM ubuntu:20.04

WORKDIR /app

# Install basic tools
RUN apt-get update && apt-get install -y \\
    python3 python3-pip git curl wget \\
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Run the application
CMD ["./start.sh"]
'''
        
        return dockerfile
    
    def _create_docker_compose(self, readme_data: Dict[str, Any], 
                             code_analysis: Dict[str, Any], app_name: str) -> str:
        """Create docker-compose.yml file."""
        compose = f'''version: '3.8'

services:
  {app_name}:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
'''
        return compose
    
    def _create_docker_startup_script(self, readme_data: Dict[str, Any], 
                                    code_analysis: Dict[str, Any]) -> str:
        """Create startup script for Docker."""
        project_type = readme_data.get('project_type', 'python')
        
        if project_type == 'python':
            script = '''#!/bin/bash
echo "Starting Python application..."

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Try to run the main Python file
if [ -f main.py ]; then
    python main.py
elif [ -f app.py ]; then
    python app.py
elif [ -f index.py ]; then
    python index.py
else
    echo "No main Python file found. Available files:"
    ls -la *.py
fi
'''
        elif project_type == 'nodejs':
            script = '''#!/bin/bash
echo "Starting Node.js application..."

# Install dependencies if package.json exists
if [ -f package.json ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start the application
if [ -f package.json ]; then
    npm start
else
    echo "No package.json found. Available files:"
    ls -la
fi
'''
        else:
            script = '''#!/bin/bash
echo "Starting application..."

# Try to detect and run the application
if [ -f main.py ]; then
    python3 main.py
elif [ -f app.py ]; then
    python3 app.py
elif [ -f package.json ]; then
    npm install && npm start
else
    echo "Could not determine how to start the application."
    echo "Available files:"
    ls -la
fi
'''
        
        return script
    
    def _create_web_wrapper(self, readme_data: Dict[str, Any], 
                          code_analysis: Dict[str, Any]) -> str:
        """Create web application wrapper."""
        wrapper = '''from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import os
import json
from pathlib import Path

app = FastAPI(title="Generated App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main application interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run")
async def run_application():
    """Run the underlying application."""
    try:
        # Try to run the main application
        result = subprocess.run(
            ["python", "main.py"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
async def get_status():
    """Get application status."""
    return {"status": "running", "message": "Application is ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        return wrapper
    
    def _create_html_template(self, readme_data: Dict[str, Any], 
                            code_analysis: Dict[str, Any]) -> str:
        """Create HTML template for web app."""
        title = readme_data.get('title', 'Generated App')
        description = readme_data.get('description', 'No description available')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .description {{
            color: #666;
            margin: 20px 0;
            line-height: 1.6;
        }}
        .run-button {{
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 0;
        }}
        .run-button:hover {{
            background: #0056b3;
        }}
        .output {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            white-space: pre-wrap;
            font-family: monospace;
        }}
        .status {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="description">{description}</div>
        
        <button class="run-button" onclick="runApp()">Run Application</button>
        
        <div id="status"></div>
        <div id="output"></div>
    </div>

    <script>
        async function runApp() {{
            const statusDiv = document.getElementById('status');
            const outputDiv = document.getElementById('output');
            
            statusDiv.innerHTML = '<div class="status">Running application...</div>';
            outputDiv.innerHTML = '';
            
            try {{
                const response = await fetch('/run', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }}
                }});
                
                const result = await response.json();
                
                if (result.status === 'success') {{
                    statusDiv.innerHTML = '<div class="status success">Application ran successfully!</div>';
                }} else {{
                    statusDiv.innerHTML = '<div class="status error">Application failed to run</div>';
                }}
                
                outputDiv.innerHTML = '<div class="output">' + 
                    (result.output || result.error || result.message || 'No output') + 
                    '</div>';
                    
            }} catch (error) {{
                statusDiv.innerHTML = '<div class="status error">Error: ' + error.message + '</div>';
            }}
        }}
        
        // Check status on page load
        fetch('/status')
            .then(response => response.json())
            .then(data => {{
                document.getElementById('status').innerHTML = 
                    '<div class="status success">' + data.message + '</div>';
            }});
    </script>
</body>
</html>
'''
        return html
    
    def _create_build_script(self, app_name: str) -> str:
        """Create build script for executable."""
        script = f'''#!/usr/bin/env python3
"""
Build script for {app_name}
"""

import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build executable using PyInstaller."""
    try:
        # Install PyInstaller if not available
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Build executable
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "{app_name}",
            "--add-data", ".:.",
            f"{app_name}_wrapper.py"
        ]
        
        print("Building executable...")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("Executable built successfully!")
            print(f"Find your executable in: dist/{app_name}")
        else:
            print("Build failed!")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {{e}}")
    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    build_executable()
'''
        return script
    
    def _extract_requirements(self, readme_data: Dict[str, Any], 
                            code_analysis: Dict[str, Any]) -> List[str]:
        """Extract requirements from analysis."""
        requirements = []
        
        # From README data
        if 'dependencies' in readme_data and 'packages' in readme_data['dependencies']:
            requirements.extend(readme_data['dependencies']['packages'])
        
        # From AI analysis
        if 'dependencies' in code_analysis:
            requirements.extend(code_analysis['dependencies'])
        
        # Remove duplicates and empty strings
        requirements = list(set([req for req in requirements if req.strip()]))
        
        return requirements
    
    def _create_app_readme(self, readme_data: Dict[str, Any], 
                         code_analysis: Dict[str, Any], platform: str) -> str:
        """Create README for the generated app."""
        title = readme_data.get('title', 'Generated App')
        description = readme_data.get('description', 'No description available')
        
        readme = f'''# {title} - Generated Application

{description}

## Generated App Information

This application was automatically generated from a GitHub repository using the GitHub-to-App converter.

### Platform: {platform.upper()}

### How to Use

'''
        
        if platform == "executable":
            readme += '''
1. Install Python 3.7+ if not already installed
2. Run the generated executable: `./{app_name}` (Linux/Mac) or `{app_name}.exe` (Windows)
3. The app will automatically install dependencies and start

### Manual Installation (if needed)

1. Install dependencies: `pip install -r requirements.txt`
2. Run the wrapper: `python {app_name}_wrapper.py`
'''
        elif platform == "docker":
            readme += '''
1. Install Docker and Docker Compose
2. Build and run: `docker-compose up --build`
3. Access the application at http://localhost:8000

### Manual Docker Commands

```bash
docker build -t {app_name} .
docker run -p 8000:8000 {app_name}
```
'''
        elif platform == "web":
            readme += '''
1. Install Python 3.7+ and pip
2. Install dependencies: `pip install -r requirements.txt`
3. Run the web app: `python web_app.py`
4. Open http://localhost:8000 in your browser
'''
        
        readme += f'''

### Original Repository Information

- **Title**: {title}
- **Description**: {description}
- **Project Type**: {readme_data.get('project_type', 'Unknown')}

### Troubleshooting

If you encounter issues:

1. Check that all dependencies are installed
2. Verify the original repository's README for specific requirements
3. Check the logs for error messages
4. Ensure you have the required system dependencies

### Support

For issues with this generated app, please refer to the original repository or create an issue with the GitHub-to-App converter.
'''
        
        return readme