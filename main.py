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
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Optional
from datetime import datetime
import uuid
import json

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

app = FastAPI(title="GitHub to App Converter", version="1.0.0")

# In-memory storage for conversions (in production, use a database)
conversions_storage = []

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
github_repo = GitHubRepository()
readme_parser = ReadmeParser()
app_generator = AppGenerator()
agentic_coder = AgenticCoder()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface for the GitHub to App converter."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard for viewing conversion statistics and history."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

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
    conversion_id = str(uuid.uuid4())
    repo_name = github_url.split('/')[-1] if '/' in github_url else github_url
    
    # Create conversion record
    conversion_record = {
        "id": conversion_id,
        "github_url": github_url,
        "repo_name": repo_name,
        "platform": target_platform,
        "status": "processing",
        "date": datetime.now().isoformat(),
        "app_name": app_name or "generated_app",
        "download_url": None,
        "error_message": None
    }
    conversions_storage.append(conversion_record)
    
    try:
        # Step 1: Clone and analyze repository
        repo_path = await github_repo.clone_repository(github_url)
        
        # Step 2: Parse README for instructions
        readme_data = await readme_parser.parse_readme(repo_path)
        
        # Step 3: Use agentic coding to understand the codebase
        code_analysis = await agentic_coder.analyze_codebase(repo_path, readme_data)
        
        # Step 4: Generate working application
        app_path = await app_generator.generate_app(
            repo_path, 
            readme_data, 
            code_analysis, 
            app_name or "generated_app",
            target_platform
        )
        
        # Update conversion record
        conversion_record["status"] = "success"
        conversion_record["download_url"] = f"/download/{os.path.basename(app_path)}"
        
        return {
            "status": "success",
            "message": "Application generated successfully!",
            "app_path": app_path,
            "download_url": f"/download/{os.path.basename(app_path)}",
            "conversion_id": conversion_id
        }
        
    except Exception as e:
        # Update conversion record with error
        conversion_record["status"] = "failed"
        conversion_record["error_message"] = str(e)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/download/{filename}")
async def download_app(filename: str):
    """Download the generated application."""
    file_path = f"generated_apps/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a conversion task."""
    # This would integrate with a task queue system
    return {"status": "completed", "progress": 100}

@app.get("/api/statistics")
async def get_statistics():
    """Get conversion statistics for the dashboard."""
    total = len(conversions_storage)
    successful = len([c for c in conversions_storage if c["status"] == "success"])
    failed = len([c for c in conversions_storage if c["status"] == "failed"])
    
    # Calculate success rate
    success_rate = f"{(successful / total * 100):.1f}%" if total > 0 else "0%"
    
    return {
        "total_conversions": total,
        "successful_conversions": successful,
        "failed_conversions": failed,
        "success_rate": success_rate
    }

@app.get("/api/recent-conversions")
async def get_recent_conversions(limit: int = 10):
    """Get recent conversions for the dashboard."""
    # Sort by date (most recent first) and limit results
    sorted_conversions = sorted(
        conversions_storage, 
        key=lambda x: x["date"], 
        reverse=True
    )[:limit]
    
    return {"conversions": sorted_conversions}

@app.delete("/api/conversions/{conversion_id}")
async def delete_conversion(conversion_id: str):
    """Delete a conversion record."""
    global conversions_storage
    
    # Find and remove the conversion
    original_length = len(conversions_storage)
    conversions_storage = [c for c in conversions_storage if c["id"] != conversion_id]
    
    if len(conversions_storage) < original_length:
        return {"status": "success", "message": "Conversion deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversion not found")

@app.post("/api/populate-sample-data")
async def populate_sample_data():
    """Populate dashboard with sample data for demonstration."""
    from populate_sample_data import get_sample_conversions
    
    # Clear existing data
    conversions_storage.clear()
    
    # Add sample data
    sample_data = get_sample_conversions()
    conversions_storage.extend(sample_data)
    
    return {
        "status": "success",
        "message": f"Added {len(sample_data)} sample conversions",
        "count": len(sample_data)
    }

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Optionally populate with sample data for demonstration
    # Uncomment the following lines to auto-populate sample data on startup
    # from populate_sample_data import populate_sample_data
    # populate_sample_data(conversions_storage)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)