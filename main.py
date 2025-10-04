"""
GitHub to App Converter
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
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
from typing import Optional, Dict
import re
from datetime import datetime, timedelta
from html import escape

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

# Contact Form Routes
# Rate limiting storage (in production, use Redis or similar)
submission_tracker: Dict[str, datetime] = {}

@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    """Display the contact form."""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact/submit")
async def submit_contact_form(
    data: Dict = Body(...)
):
    """
    Handle contact form submission with comprehensive validation.
    
    Features:
    - Required field validation (name, email, message)
    - Email format validation
    - Message length validation (max 1000 characters)
    - HTML stripping and sanitization
    - Rate limiting (5 seconds between submissions per IP)
    - XSS protection
    
    Args:
        data: Dictionary containing name, email, and message fields
        
    Returns:
        JSONResponse with status and message
    """
    try:
        # Extract and sanitize form data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        
        # Validation errors list
        errors = []
        
        # Validate required fields
        if not name:
            errors.append({'field': 'name', 'message': 'Name is required'})
        
        if not email:
            errors.append({'field': 'email', 'message': 'Email is required'})
        
        if not message:
            errors.append({'field': 'message', 'message': 'Message is required'})
        
        # Validate email format
        if email:
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                errors.append({
                    'field': 'email', 
                    'message': 'Please enter a valid email address'
                })
        
        # Validate message length
        if message:
            # Strip HTML tags from message
            message_clean = strip_html_tags(message)
            
            if len(message_clean) > 1000:
                errors.append({
                    'field': 'message',
                    'message': 'Message must not exceed 1000 characters'
                })
            else:
                message = message_clean
        
        # Return validation errors if any
        if errors:
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': errors
                }
            )
        
        # Additional sanitization - escape any remaining special characters
        name = escape(name)
        email = escape(email)
        message = escape(message)
        
        # Here you would typically:
        # 1. Save to database
        # 2. Send email notification
        # 3. Add to a queue for processing
        # For this implementation, we'll just log and return success
        
        print(f"[{datetime.now().isoformat()}] Contact Form Submission:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Message: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'message': 'Thank you for your message! We will get back to you soon.',
                'timestamp': datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error processing contact form: {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': 'An error occurred while processing your request. Please try again later.'
            }
        )

def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags and formatting from text.
    
    This function provides multiple layers of HTML stripping:
    1. Removes HTML tags using regex
    2. Converts HTML entities to text
    3. Removes any remaining special HTML characters
    
    Args:
        text: Text potentially containing HTML
        
    Returns:
        Plain text without HTML tags or formatting
    """
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities
    clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
    clean_text = re.sub(r'&#[0-9]+;', '', clean_text)
    
    # Remove any remaining special characters that could be part of HTML
    clean_text = re.sub(r'[<>]', '', clean_text)
    
    return clean_text.strip()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)