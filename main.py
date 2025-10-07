"""
GitHub to App Converter
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request as FastAPIRequest
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Optional
import uuid
from contextlib import asynccontextmanager

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder
from src.logger_config import setup_logging, get_logger, set_request_context, clear_request_context

# Setup logging
setup_logging(
    app_name="github_to_app",
    log_dir="logs",
    log_level="INFO",
    console_output=True,
    file_output=True,
    json_format=True
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting GitHub to App Converter application", extra={"event": "startup"})
    yield
    logger.info("Shutting down GitHub to App Converter application", extra={"event": "shutdown"})


app = FastAPI(
    title="GitHub to App Converter",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
logger.info("Initializing application components")
github_repo = GitHubRepository()
readme_parser = ReadmeParser()
app_generator = AppGenerator()
agentic_coder = AgenticCoder()
logger.info("Application components initialized successfully")


@app.middleware("http")
async def log_requests(request: FastAPIRequest, call_next):
    """Middleware to log all HTTP requests."""
    request_id = str(uuid.uuid4())
    
    # Set request context
    set_request_context(
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_host=request.client.host if request.client else None
    )
    
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "access_log": True,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None
        }
    )
    
    try:
        response = await call_next(request)
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status {response.status_code}",
            extra={
                "access_log": True,
                "request_id": request_id,
                "status_code": response.status_code
            }
        )
        
        return response
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            exc_info=True,
            extra={
                "access_log": True,
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise
    finally:
        clear_request_context()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface for the GitHub to App converter."""
    logger.debug("Rendering home page")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert_repository(
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
    logger.info(
        f"Starting conversion for repository: {github_url}",
        extra={
            "github_url": github_url,
            "app_name": app_name,
            "target_platform": target_platform
        }
    )
    
    try:
        # Step 1: Clone and analyze repository
        logger.info(f"Step 1: Cloning repository {github_url}")
        repo_path = await github_repo.clone_repository(github_url)
        logger.info(f"Repository cloned successfully to {repo_path}")
        
        # Step 2: Parse README for instructions
        logger.info("Step 2: Parsing README file")
        readme_data = await readme_parser.parse_readme(repo_path)
        logger.info(
            "README parsed successfully",
            extra={
                "project_type": readme_data.get('project_type'),
                "title": readme_data.get('title')
            }
        )
        
        # Step 3: Use agentic coding to understand the codebase
        logger.info("Step 3: Analyzing codebase with AI")
        code_analysis = await agentic_coder.analyze_codebase(repo_path, readme_data)
        logger.info("Codebase analysis completed")
        
        # Step 4: Generate working application
        logger.info(f"Step 4: Generating {target_platform} application")
        app_path = await app_generator.generate_app(
            repo_path, 
            readme_data, 
            code_analysis, 
            app_name or "generated_app",
            target_platform
        )
        logger.info(
            f"Application generated successfully at {app_path}",
            extra={"app_path": app_path}
        )
        
        return {
            "status": "success",
            "message": "Application generated successfully!",
            "app_path": app_path,
            "download_url": f"/download/{os.path.basename(app_path)}"
        }
        
    except Exception as e:
        logger.error(
            f"Conversion failed for {github_url}",
            exc_info=True,
            extra={
                "github_url": github_url,
                "app_name": app_name,
                "target_platform": target_platform,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/download/{filename}")
async def download_app(filename: str):
    """Download the generated application."""
    logger.info(f"Download requested for file: {filename}")
    file_path = f"generated_apps/{filename}"
    
    if os.path.exists(file_path):
        logger.info(f"Serving file: {filename}", extra={"file_path": file_path})
        return FileResponse(file_path, filename=filename)
    else:
        logger.warning(f"File not found: {filename}", extra={"requested_path": file_path})
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a conversion task."""
    logger.debug(f"Status check for task: {task_id}")
    # This would integrate with a task queue system
    return {"status": "completed", "progress": 100}

if __name__ == "__main__":
    # Create necessary directories
    logger.info("Creating necessary directories")
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    logger.info("Directories created successfully")
    
    logger.info("Starting uvicorn server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)  # Use our custom logging