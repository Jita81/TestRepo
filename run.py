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
    """Set up the environment."""
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
    
    # Check for .env file
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("⚠️  No .env file found. Copying from .env.example")
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Please edit .env file and add your OpenAI API key")
        else:
            print("⚠️  No .env file found. Please create one with your OpenAI API key")

def main():
    """Main startup function."""
    print("🚀 Starting GitHub to App Converter...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No OpenAI API key found in .env file")
        print("   The AI-powered features will not work without an API key")
        print("   You can still use the basic conversion features")
    
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