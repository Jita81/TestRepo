#!/usr/bin/env python3
"""
GitHub to App Converter - Startup Script
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import requests
        import git
        import yaml
        import jinja2
        import openai
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up the environment securely."""
    # Create necessary directories
    directories = [
        "generated_apps",
        "temp_repos", 
        "static",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Ensure .gitignore exists and includes .env
    gitignore_path = Path(".gitignore")
    required_entries = [".env", ".env.local", ".env.*.local", "*.pyc", "__pycache__/", "temp_repos/", "generated_apps/"]
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_entries = f.read()
        
        new_entries = [entry for entry in required_entries if entry not in existing_entries]
        if new_entries:
            with open(gitignore_path, 'a') as f:
                f.write("\n# Security - Environment variables\n")
                for entry in new_entries:
                    f.write(f"{entry}\n")
            print("✅ Updated .gitignore with security entries")
    else:
        with open(gitignore_path, 'w') as f:
            f.write("# Security - Environment variables\n")
            for entry in required_entries:
                f.write(f"{entry}\n")
        print("✅ Created .gitignore with security entries")
    
    # Check for .env file
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("⚠️  No .env file found. Copying from .env.example")
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Please edit .env file and add your OpenAI API key")
            print("🔒 IMPORTANT: .env file is now protected in .gitignore")
        else:
            print("⚠️  No .env file found. Creating template...")
            with open(".env", "w") as f:
                f.write("# OpenAI Configuration\n")
                f.write("OPENAI_API_KEY=your_api_key_here\n\n")
                f.write("# GitHub Configuration (optional)\n")
                f.write("GITHUB_TOKEN=your_github_token_here\n\n")
                f.write("# Application Configuration\n")
                f.write("DEBUG=False\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
            print("✅ Created .env template file")
            print("📝 Please edit .env file and add your API keys")
            print("🔒 IMPORTANT: .env file is protected in .gitignore")

def main():
    """Main startup function."""
    print("🚀 Starting GitHub to App Converter...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Load environment variables securely
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate critical environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  Warning: No valid OpenAI API key found in .env file")
        print("   The AI-powered features will not work without an API key")
        print("   You can still use the basic conversion features")
    else:
        # Mask the API key in logs for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✅ OpenAI API key loaded: {masked_key}")
    
    # Security check: Ensure .env is not in version control
    if Path(".git").exists():
        git_tracked = os.popen("git ls-files .env 2>/dev/null").read().strip()
        if git_tracked:
            print("⚠️  WARNING: .env file is tracked by git!")
            print("   Run: git rm --cached .env")
            print("   This is a security risk - API keys should never be in version control")
    
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the application
    try:
        from main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()