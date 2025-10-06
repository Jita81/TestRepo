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

def validate_environment_variables():
    """Validate required environment variables with security checks.
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    warnings = []
    
    # Required environment variables
    required_vars = {
        "OPENAI_API_KEY": {
            "required": True,
            "min_length": 20,
            "description": "OpenAI API key for AI features"
        }
    }
    
    # Optional but recommended environment variables
    optional_vars = {
        "GITHUB_TOKEN": {
            "required": False,
            "min_length": 20,
            "description": "GitHub personal access token for higher API rate limits"
        },
        "MAX_REPO_SIZE_MB": {
            "required": False,
            "validator": lambda x: x.isdigit() and 0 < int(x) < 10000,
            "description": "Maximum repository size to process (in MB)"
        },
        "CONVERSION_TIMEOUT": {
            "required": False,
            "validator": lambda x: x.isdigit() and 0 < int(x) < 3600,
            "description": "Maximum time for conversion (in seconds)"
        }
    }
    
    # Validate required variables
    for var_name, config in required_vars.items():
        value = os.getenv(var_name)
        
        if not value:
            if config["required"]:
                errors.append(f"❌ Missing required environment variable: {var_name}")
                errors.append(f"   Description: {config['description']}")
        else:
            # Validate minimum length for security
            if "min_length" in config and len(value) < config["min_length"]:
                errors.append(f"❌ {var_name} is too short (minimum {config['min_length']} characters)")
            
            # Check for common insecure values
            insecure_values = ["test", "demo", "example", "placeholder", "your-key-here", "xxx"]
            if value.lower() in insecure_values:
                errors.append(f"❌ {var_name} appears to be a placeholder value")
    
    # Validate optional variables
    for var_name, config in optional_vars.items():
        value = os.getenv(var_name)
        
        if value:
            # Validate using custom validator if provided
            if "validator" in config:
                if not config["validator"](value):
                    warnings.append(f"⚠️  {var_name} has invalid format")
                    warnings.append(f"   Description: {config['description']}")
            
            # Validate minimum length if specified
            if "min_length" in config and len(value) < config["min_length"]:
                warnings.append(f"⚠️  {var_name} is too short (minimum {config['min_length']} characters)")
    
    # Display validation results
    if errors:
        print("\n🚨 Environment Validation Failed:")
        for error in errors:
            print(error)
    
    if warnings:
        print("\n⚠️  Environment Warnings:")
        for warning in warnings:
            print(warning)
    
    is_valid = len(errors) == 0
    return is_valid, errors


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
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate environment variables
    print("\n🔍 Validating environment configuration...")
    is_valid, errors = validate_environment_variables()
    
    if not is_valid:
        print("\n❌ Environment validation failed. Please fix the errors above.")
        print("\n💡 Tips:")
        print("   1. Copy .env.example to .env if you haven't already")
        print("   2. Add your OpenAI API key to .env")
        print("   3. Ensure all required credentials are properly set")
        print("   4. Never commit .env file to version control")
        sys.exit(1)
    
    print("✅ Environment configuration is valid")
    
    # Additional security warnings
    if os.getenv("OPENAI_API_KEY") and len(os.getenv("OPENAI_API_KEY")) < 40:
        print("⚠️  OpenAI API key seems unusually short")
    
    if not os.getenv("GITHUB_TOKEN"):
        print("💡 Tip: Set GITHUB_TOKEN for higher GitHub API rate limits")
    
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