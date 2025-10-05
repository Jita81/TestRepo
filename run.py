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
    """
    Validate required environment variables are set.
    
    Returns:
        tuple: (is_valid, missing_vars, warnings)
    """
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for AI features',
    }
    
    optional_vars = {
        'GITHUB_TOKEN': 'GitHub API token for higher rate limits',
        'REDIS_URL': 'Redis connection for rate limiting',
        'API_TOKEN': 'API authentication token',
        'ENCRYPTION_KEY': 'Key for encrypting sensitive data',
    }
    
    missing_vars = []
    warnings = []
    
    # Check required variables
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value or value == f"your_{var_name.lower()}_here":
            missing_vars.append((var_name, description))
    
    # Check optional variables
    for var_name, description in optional_vars.items():
        if not os.getenv(var_name):
            warnings.append((var_name, description))
    
    is_valid = len(missing_vars) == 0
    return is_valid, missing_vars, warnings


def setup_environment():
    """Set up the environment securely with comprehensive validation."""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = [
        "generated_apps",
        "temp_repos", 
        "static",
        "templates",
        "logs"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create {directory}: {e}")
    
    # Comprehensive .gitignore setup
    gitignore_path = Path(".gitignore")
    required_entries = [
        "# Security - Sensitive files",
        ".env",
        ".env.local",
        ".env.*.local",
        ".env.production",
        "*.key",
        "*.pem",
        "",
        "# Python",
        "*.pyc",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        "",
        "# Application data",
        "temp_repos/",
        "generated_apps/",
        "logs/",
        "*.log",
        "",
        "# IDE",
        ".vscode/",
        ".idea/",
        "*.swp",
        "",
        "# OS",
        ".DS_Store",
        "Thumbs.db",
    ]
    
    try:
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
            
            # Add missing entries
            new_entries = []
            for entry in required_entries:
                if entry and entry not in existing_content and not entry.startswith('#'):
                    new_entries.append(entry)
            
            if new_entries:
                with open(gitignore_path, 'a') as f:
                    f.write("\n# Auto-generated security entries\n")
                    for entry in new_entries:
                        f.write(f"{entry}\n")
                print(f"✅ Updated .gitignore ({len(new_entries)} new entries)")
        else:
            with open(gitignore_path, 'w') as f:
                for entry in required_entries:
                    f.write(f"{entry}\n")
            print("✅ Created comprehensive .gitignore")
    except Exception as e:
        print(f"⚠️  Warning: Could not update .gitignore: {e}")
    
    # Check for .env file
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("⚠️  No .env file found. Copying from .env.example")
            try:
                import shutil
                shutil.copy(".env.example", ".env")
                print("📝 Please edit .env file and add your API keys")
                print("🔒 IMPORTANT: .env file is protected in .gitignore")
            except Exception as e:
                print(f"❌ Error copying .env.example: {e}")
        else:
            print("⚠️  No .env file found. Creating secure template...")
            try:
                with open(".env", "w") as f:
                    f.write("# ==========================================\n")
                    f.write("# SECURITY WARNING: Never commit this file\n")
                    f.write("# ==========================================\n\n")
                    f.write("# OpenAI Configuration (REQUIRED)\n")
                    f.write("OPENAI_API_KEY=your_api_key_here\n\n")
                    f.write("# GitHub Configuration (optional, for higher rate limits)\n")
                    f.write("GITHUB_TOKEN=your_github_token_here\n\n")
                    f.write("# Security (optional, for encryption)\n")
                    f.write("ENCRYPTION_KEY=generate_with_fernet.generate_key()\n")
                    f.write("API_TOKEN=your_secure_api_token_here\n\n")
                    f.write("# Application Configuration\n")
                    f.write("DEBUG=False\n")
                    f.write("HOST=0.0.0.0\n")
                    f.write("PORT=8000\n")
                    f.write("NODE_ENV=development\n\n")
                    f.write("# Rate Limiting (optional)\n")
                    f.write("REDIS_URL=memory://\n")
                print("✅ Created secure .env template")
                print("📝 Please edit .env and replace placeholder values")
                print("🔒 IMPORTANT: .env file is protected in .gitignore")
            except Exception as e:
                print(f"❌ Error creating .env: {e}")
    
    # Validate .env file
    print("\n🔍 Validating environment variables...")
    is_valid, missing_vars, warnings = validate_environment_variables()
    
    if not is_valid:
        print("\n❌ Missing required environment variables:")
        for var_name, description in missing_vars:
            print(f"   - {var_name}: {description}")
        print("\n📝 Please update your .env file with valid values")
    else:
        print("✅ All required environment variables are set")
    
    if warnings:
        print("\n⚠️  Optional environment variables not set:")
        for var_name, description in warnings[:3]:  # Show first 3
            print(f"   - {var_name}: {description}")
        if len(warnings) > 3:
            print(f"   ... and {len(warnings) - 3} more")
    
    return is_valid

def main():
    """Main startup function."""
    print("🚀 Starting GitHub to App Converter...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    env_valid = setup_environment()
    
    if not env_valid:
        print("\n⚠️  Environment setup incomplete!")
        print("The application may not work correctly without required variables.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("👋 Setup cancelled. Please configure your .env file.")
            sys.exit(0)
    
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