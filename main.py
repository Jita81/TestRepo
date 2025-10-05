"""
GitHub to App Converter
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Optional
import logging
import time

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter with proper configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
    strategy="fixed-window",
    headers_enabled=True,
)

# Create FastAPI app with rate limiting
app = FastAPI(
    title="GitHub to App Converter",
    version="1.0.0",
    description="Convert GitHub repositories to working applications",
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
github_repo = GitHubRepository()
readme_parser = ReadmeParser()
app_generator = AppGenerator()
agentic_coder = AgenticCoder()

@app.get("/", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def home(request: Request):
    """Main interface for the GitHub to App converter."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
@limiter.limit("5/minute")
async def convert_repository(
    request: Request,
    github_url: str = Form(...),
    app_name: Optional[str] = Form(None),
    target_platform: str = Form("executable")
):
    """
    Convert a GitHub repository to a working application.
    
    Args:
        github_url: GitHub repository URL
        app_name: Optional custom name for the generated app
        target_platform: Target platform (executable, docker, web)
    """
    try:
        logger.info(f"Starting conversion for repository: {github_url}")
        
        # Step 1: Clone and analyze repository
        repo_path = await github_repo.clone_repository(github_url)
        logger.info(f"Repository cloned to: {repo_path}")
        
        # Step 2: Parse README for instructions
        readme_data = await readme_parser.parse_readme(repo_path)
        logger.info("README parsed successfully")
        
        # Step 3: Use agentic coding to understand the codebase
        code_analysis = await agentic_coder.analyze_codebase(repo_path, readme_data)
        logger.info("Codebase analysis completed")
        
        # Step 4: Generate working application
        app_path = await app_generator.generate_app(
            repo_path, 
            readme_data, 
            code_analysis, 
            app_name or "generated_app",
            target_platform
        )
        logger.info(f"Application generated at: {app_path}")
        
        return {
            "status": "success",
            "message": "Application generated successfully!",
            "app_path": app_path,
            "download_url": f"/download/{os.path.basename(app_path)}"
        }
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/download/{filename}")
@limiter.limit("10/minute")
async def download_app(request: Request, filename: str):
    """Download the generated application."""
    # Security: Prevent path traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = f"generated_apps/{filename}"
    if os.path.exists(file_path):
        logger.info(f"Serving file: {filename}")
        return FileResponse(file_path, filename=filename)
    else:
        logger.warning(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/status/{task_id}")
@limiter.limit("60/minute")
async def get_status(request: Request, task_id: str):
    """Get the status of a conversion task."""
    # Validate task_id format
    if not task_id or len(task_id) > 100:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    # This would integrate with a task queue system
    logger.info(f"Status check for task: {task_id}")
    return {"status": "completed", "progress": 100, "task_id": task_id}

@app.get("/api/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)