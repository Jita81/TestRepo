"""
GitHub to App Converter
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
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
import re
from datetime import datetime

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

app = FastAPI(title="GitHub to App Converter", version="1.0.0")

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

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact form page."""
    return templates.TemplateResponse("contact_form.html", {"request": request})

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
        
        return {
            "status": "success",
            "message": "Application generated successfully!",
            "app_path": app_path,
            "download_url": f"/download/{os.path.basename(app_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/download/{filename}")
async def download_app(filename: str):
    """Download the generated application."""
    file_path = f"generated_apps/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/contact")
async def submit_contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """
    Handle contact form submission with server-side validation.
    
    Args:
        name: User's name (2-50 characters, alphanumeric with spaces and hyphens)
        email: User's email address (valid email format)
        message: User's message (10-1000 characters)
    
    Returns:
        JSON response with success or error status
    """
    # Validation patterns (same as client-side for consistency)
    NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    MESSAGE_MIN_LENGTH = 10
    MESSAGE_MAX_LENGTH = 1000
    
    errors = []
    
    try:
        # Validate name
        name = name.strip()
        if not name:
            errors.append("Name is required")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters")
        elif len(name) > 50:
            errors.append("Name must not exceed 50 characters")
        elif not re.match(NAME_PATTERN, name):
            errors.append("Name can only contain letters, numbers, spaces, and hyphens")
        
        # Validate email
        email = email.strip()
        if not email:
            errors.append("Email is required")
        elif not re.match(EMAIL_PATTERN, email):
            errors.append("Please enter a valid email address")
        
        # Validate message
        message = message.strip()
        if not message:
            errors.append("Message is required")
        elif len(message) < MESSAGE_MIN_LENGTH:
            errors.append(f"Message must be at least {MESSAGE_MIN_LENGTH} characters")
        elif len(message) > MESSAGE_MAX_LENGTH:
            errors.append(f"Message must not exceed {MESSAGE_MAX_LENGTH} characters")
        
        # If there are validation errors, return them
        if errors:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Validation failed",
                    "errors": errors
                }
            )
        
        # TODO: In production, you would:
        # 1. Save to database
        # 2. Send email notification
        # 3. Integrate with CRM or support system
        # 4. Queue for processing if needed
        
        # For now, we'll log the submission
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"Contact Form Submission - {timestamp}")
        print(f"{'='*60}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        
        # Save to file for demonstration (in production, use a database)
        os.makedirs("contact_submissions", exist_ok=True)
        submission_file = f"contact_submissions/{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        
        with open(submission_file, 'w') as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Name: {name}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Message:\n{message}\n")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thank you for your message! We'll get back to you soon."
            }
        )
        
    except Exception as e:
        print(f"Error processing contact form: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An error occurred while processing your request. Please try again later."
            }
        )

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a conversion task."""
    # This would integrate with a task queue system
    return {"status": "completed", "progress": 100}

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("contact_submissions", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)