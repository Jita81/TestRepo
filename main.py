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
from pydantic import BaseModel, Field, validator, EmailStr
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


# ============================================
# Contact Form Models and Validators
# ============================================

class ContactFormData(BaseModel):
    """
    Contact form data model with comprehensive validation.
    
    Validates:
    - Name: 2-50 characters, Unicode support
    - Email: Valid email format
    - Message: 10-1000 characters, no whitespace-only content
    """
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name field with Unicode support and sanitization."""
        # Strip whitespace
        v = v.strip()
        
        # Check length after stripping
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if len(v) > 50:
            raise ValueError('Name must not exceed 50 characters')
        
        # Check for obviously invalid characters (control characters, etc.)
        # This pattern allows letters (including Unicode), spaces, hyphens, and apostrophes
        # Using a more permissive approach that allows most Unicode characters
        # but blocks control characters and common XSS vectors
        invalid_chars = set('<>{}[]()\\|/;:@#$%^&*+=`~"')
        if any(char in invalid_chars for char in v):
            raise ValueError('Name contains invalid characters')
        
        # Block control characters
        if any(ord(char) < 32 or ord(char) == 127 for char in v):
            raise ValueError('Name contains invalid characters')
        
        # Sanitize for XSS prevention
        v = html.escape(v)
        
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Additional email validation and normalization."""
        # Normalize to lowercase
        v = v.strip().lower()
        
        # Basic email pattern check (EmailStr already validates)
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError('Please enter valid email address')
        
        # Sanitize for XSS prevention
        v = html.escape(v)
        
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message field with whitespace and content checks."""
        # Strip leading/trailing whitespace
        v = v.strip()
        
        # Check if message is only whitespace
        if not v or not v.replace(' ', '').replace('\n', '').replace('\t', ''):
            raise ValueError('Message cannot contain only whitespace')
        
        # Check length
        if len(v) < 10:
            raise ValueError('Message must be at least 10 characters')
        if len(v) > 1000:
            raise ValueError('Message must not exceed 1000 characters')
        
        # Sanitize for XSS prevention
        v = html.escape(v)
        
        return v


class ContactFormResponse(BaseModel):
    """Response model for contact form submission."""
    status: str
    message: str

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


@app.post("/api/contact", response_model=ContactFormResponse)
async def submit_contact_form(form_data: ContactFormData):
    """
    Handle contact form submissions with comprehensive validation and error handling.
    
    This endpoint:
    1. Validates all input fields (name, email, message)
    2. Sanitizes input to prevent XSS attacks
    3. Handles edge cases (Unicode, whitespace, etc.)
    4. Returns appropriate error messages
    
    Args:
        form_data: ContactFormData object with validated fields
        
    Returns:
        ContactFormResponse with status and message
        
    Raises:
        HTTPException: For validation errors or server errors
    """
    try:
        # Additional server-side checks
        # Note: Pydantic validators have already run at this point
        
        # Log the contact form submission (in production, you would save to database)
        # For now, we'll just print it
        print(f"Contact Form Submission:")
        print(f"  Name: {form_data.name}")
        print(f"  Email: {form_data.email}")
        print(f"  Message: {form_data.message[:50]}...")  # Print first 50 chars
        
        # In a real application, you would:
        # 1. Save to database
        # 2. Send email notification
        # 3. Add to support ticket system
        # 4. Send confirmation email to user
        
        # Simulate some processing (e.g., sending email)
        await asyncio.sleep(0.5)  # Simulate async operation
        
        # Check for any server-side issues (simulated)
        # In production, you might check database connection, email service, etc.
        
        # Success response
        return ContactFormResponse(
            status="success",
            message="Message sent successfully"
        )
        
    except ValueError as e:
        # Validation errors from Pydantic validators
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(e)
            }
        )
    except Exception as e:
        # Unexpected server errors
        print(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
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