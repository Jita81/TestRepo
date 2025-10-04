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
from pydantic import BaseModel, EmailStr, field_validator, Field
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Optional
import re
import html

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

# Contact form data model with validation
class ContactFormData(BaseModel):
    """
    Contact form submission model with comprehensive validation.
    Handles name, email, and message fields with security measures.
    """
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    message: str = Field(..., min_length=5, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validates name field:
        - Trims whitespace
        - Checks for whitespace-only input
        - Validates character pattern
        - Sanitizes HTML/script tags
        """
        # Trim whitespace
        v = v.strip()
        
        # Check for empty or whitespace-only
        if not v or len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\'-]+$', v):
            raise ValueError('Name contains invalid characters')
        
        # Sanitize HTML entities
        v = html.escape(v)
        
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Validates email field:
        - Trims whitespace
        - Checks length constraints
        - Sanitizes HTML/script tags
        """
        # Trim whitespace
        v = v.strip()
        
        # Check for whitespace-only
        if not v:
            raise ValueError('Email cannot be empty')
        
        # Additional length check
        if len(v) > 100:
            raise ValueError('Email must not exceed 100 characters')
        
        # Sanitize HTML entities
        v = html.escape(v)
        
        return v
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """
        Validates message field:
        - Trims whitespace
        - Checks length constraints
        - Sanitizes HTML/script tags
        """
        # Trim whitespace
        v = v.strip()
        
        # Check for empty or whitespace-only
        if not v or len(v) < 5:
            raise ValueError('Message must be at least 5 characters')
        
        if len(v) > 1000:
            raise ValueError('Message must not exceed 1000 characters')
        
        # Sanitize HTML entities to prevent XSS
        v = html.escape(v)
        
        return v

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
    Displays the contact form page.
    
    Returns:
        HTMLResponse: Rendered contact form template
    """
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact")
async def submit_contact_form(contact_data: ContactFormData):
    """
    Handles contact form submission with comprehensive validation.
    
    Args:
        contact_data: Validated contact form data (name, email, message)
    
    Returns:
        JSONResponse: Success/error response
    
    Security features:
    - Input sanitization (HTML/script tag removal)
    - Length validation (prevents DoS attacks)
    - Email format validation
    - Whitespace-only input rejection
    
    Edge cases handled:
    - Whitespace-only fields
    - HTML/script tags in input
    - Email over 100 characters
    - Rapid submission attempts (handled client-side)
    """
    try:
        # Log the contact form submission (in production, save to database)
        print(f"Contact form submission received:")
        print(f"  Name: {contact_data.name}")
        print(f"  Email: {contact_data.email}")
        print(f"  Message: {contact_data.message[:50]}...")
        
        # In production, you would:
        # 1. Save to database
        # 2. Send email notification
        # 3. Add to CRM system
        # 4. Trigger webhooks
        
        # Simulate processing delay (max 2 seconds as per requirements)
        await asyncio.sleep(0.5)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Message sent successfully"
            }
        )
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process contact form: {str(e)}"
        )

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)