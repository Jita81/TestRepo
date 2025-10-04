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
import re
from typing import Optional

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

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a conversion task."""
    # This would integrate with a task queue system
    return {"status": "completed", "progress": 100}

@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    """
    Serve the contact form page.
    
    This endpoint displays a validated contact form with fields for:
    - Name (2-50 characters, letters, spaces, hyphens only)
    - Email (valid email format)
    - Message (10-1000 characters)
    """
    return templates.TemplateResponse("contact_form.html", {"request": request})

@app.post("/contact/submit")
async def submit_contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """
    Handle contact form submission with server-side validation.
    
    This endpoint:
    1. Validates all form fields against defined rules
    2. Strips HTML/formatting from message field
    3. Returns success/error responses
    
    Args:
        name: Contact name (2-50 chars, letters/spaces/hyphens only)
        email: Valid email address
        message: Message content (10-1000 characters)
        
    Returns:
        JSON response with status and message
    """
    try:
        # Strip whitespace from inputs
        name = name.strip()
        email = email.strip()
        message = message.strip()
        
        # Server-side validation patterns
        name_pattern = re.compile(r'^[a-zA-Z\s-]{2,50}$')
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Validate name
        if not name:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Name is required"}
            )
        
        if not name_pattern.match(name):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Name must be 2-50 characters and contain only letters, spaces, or hyphens"
                }
            )
        
        # Validate email
        if not email:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Email is required"}
            )
        
        if not email_pattern.match(email):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Please enter a valid email address"}
            )
        
        # Validate message
        if not message:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Message is required"}
            )
        
        message_length = len(message)
        if message_length < 10:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Message must be at least 10 characters"}
            )
        
        if message_length > 1000:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Message cannot exceed 1000 characters"}
            )
        
        # Strip any HTML tags from message (security measure)
        # Remove HTML tags using regex
        message = re.sub(r'<[^>]+>', '', message)
        
        # In a production environment, you would:
        # 1. Save to database
        # 2. Send email notification
        # 3. Log the submission
        # 4. Possibly integrate with a CRM
        
        # For now, we'll just log the submission
        print(f"Contact form submission received:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Message: {message[:50]}...")
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Message sent successfully!"
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Error processing contact form: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An error occurred while processing your request. Please try again."
            }
        )

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)