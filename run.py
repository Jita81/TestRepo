#!/usr/bin/env python3
"""
GitHub to App Converter - Startup Script
"""

import os
import sys
from pathlib import Path
from src.logger_config import setup_logging, get_logger

# Setup logging first
setup_logging(
    app_name="github_to_app_startup",
    log_dir="logs",
    log_level="INFO",
    console_output=True,
    file_output=True,
    json_format=True
)

logger = get_logger(__name__)

def check_dependencies():
    """Check if required dependencies are installed."""
    logger.info("Checking dependencies")
    
    try:
        import fastapi
        import uvicorn
        import requests
        import git
        import yaml
        import jinja2
        import openai
        
        print("✅ All dependencies are installed!")
        logger.info("All dependencies are installed successfully")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        logger.error(
            f"Missing dependency",
            exc_info=True,
            extra={"import_error": str(e)}
        )
        return False

def setup_environment():
    """Set up the environment."""
    logger.info("Setting up environment")
    
    # Create necessary directories
    directories = [
        "generated_apps",
        "temp_repos", 
        "static",
        "templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
        logger.debug(f"Created directory: {directory}")
    
    logger.info("All directories created successfully")
    
    # Check for .env file
    if not Path(".env").exists():
        logger.warning("No .env file found")
        if Path(".env.example").exists():
            print("⚠️  No .env file found. Copying from .env.example")
            logger.info("Copying .env.example to .env")
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Please edit .env file and add your OpenAI API key")
            logger.info(".env file created from example")
        else:
            print("⚠️  No .env file found. Please create one with your OpenAI API key")
            logger.warning("No .env.example file found")
    else:
        logger.info(".env file already exists")

def main():
    """Main startup function."""
    logger.info("Starting GitHub to App Converter application")
    
    print("🚀 Starting GitHub to App Converter...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed, exiting")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check for OpenAI API key
    logger.debug("Loading environment variables")
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No OpenAI API key found in .env file")
        print("   The AI-powered features will not work without an API key")
        print("   You can still use the basic conversion features")
        logger.warning("No OpenAI API key found in environment variables")
    else:
        logger.info("OpenAI API key found")
    
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the application
    try:
        logger.info("Starting uvicorn server")
        from main import app
        import uvicorn
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)  # Use our custom logging
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        logger.info("Application shutdown by user (Ctrl+C)")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        logger.error(
            "Failed to start server",
            exc_info=True,
            extra={"error": str(e)}
        )
        sys.exit(1)

if __name__ == "__main__":
    main()