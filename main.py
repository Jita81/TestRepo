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
import html
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

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact form page."""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """
    Handle contact form submission with validation and sanitization.
    
    Args:
        name: User's name (2-50 characters)
        email: User's email address (valid email format)
        message: User's message (10-1000 characters)
    
    Returns:
        JSON response with status and message
    """
    # Sanitize inputs - escape HTML entities to prevent XSS attacks
    name = html.escape(name.strip())
    email = html.escape(email.strip())
    message = html.escape(message.strip())
    
    # Server-side validation
    errors = []
    
    # Validate name
    if not name:
        errors.append("Name is required")
    elif len(name) < 2:
        errors.append("Name must be at least 2 characters long")
    elif len(name) > 50:
        errors.append("Name must not exceed 50 characters")
    
    # Validate email with regex pattern
    email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    if not email:
        errors.append("Email address is required")
    elif not email_pattern.match(email):
        errors.append("Please enter a valid email address")
    
    # Validate message
    if not message:
        errors.append("Message is required")
    elif len(message) < 10:
        errors.append("Message must be at least 10 characters long")
    elif len(message) > 1000:
        errors.append("Message must not exceed 1000 characters")
    
    # If there are validation errors, return them
    if errors:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "; ".join(errors)
            }
        )
    
    # In a production environment, you would:
    # 1. Store the message in a database
    # 2. Send an email notification
    # 3. Queue the message for processing
    # For this demo, we'll just log it and return success
    
    try:
        # Log the contact form submission (in production, save to database or send email)
        print(f"Contact form submission:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Message: {message[:100]}...")  # Log first 100 chars
        
        # Here you would typically:
        # - Save to database
        # - Send email to admin
        # - Send confirmation email to user
        # - Add to CRM system
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Message sent successfully"
            }
        )
        
    except Exception as e:
        # Handle any unexpected errors
        print(f"Error processing contact form: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Unable to send message. Please try again later."
            }
        )

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

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)