"""
GitHub to App Converter - Enhanced Security Version
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.

Security Enhancements:
- CSRF token validation
- Rate limiting
- XSS prevention
- Security headers
- Input sanitization
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import asyncio
from typing import Optional
import re
import html
import secrets
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

app = FastAPI(title="GitHub to App Converter", version="2.0.0")

# ===================================================================
# SECURITY MIDDLEWARE
# ===================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses
    - X-Content-Type-Options: Prevents MIME-type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables XSS filter
    - Strict-Transport-Security: Enforces HTTPS
    - Content-Security-Policy: Restricts resource loading
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent spam/abuse
    Implements a sliding window algorithm
    
    Limits:
    - 5 requests per minute per IP for form submissions
    - 60 requests per minute per IP for general requests
    """
    
    def __init__(self, app, requests_per_minute=60, form_requests_per_minute=5):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.form_requests_per_minute = form_requests_per_minute
        self.request_counts = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Determine rate limit based on path
        is_form_submission = request.url.path == "/contact" and request.method == "POST"
        limit = self.form_requests_per_minute if is_form_submission else self.requests_per_minute
        
        # Clean old requests (older than 1 minute)
        while self.request_counts[client_ip] and current_time - self.request_counts[client_ip][0] > 60:
            self.request_counts[client_ip].popleft()
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Too many requests. Please try again later."
                }
            )
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
github_repo = GitHubRepository()
readme_parser = ReadmeParser()
app_generator = AppGenerator()
agentic_coder = AgenticCoder()

# ===================================================================
# CSRF TOKEN MANAGEMENT
# ===================================================================

# Store CSRF tokens (in production, use Redis or database)
csrf_tokens = {}

def generate_csrf_token():
    """
    Generates a cryptographically secure CSRF token
    
    Returns:
        str: 64-character hex token
    """
    return secrets.token_hex(32)

def validate_csrf_token(token: str, request: Request) -> bool:
    """
    Validates a CSRF token
    
    Args:
        token: CSRF token to validate
        request: FastAPI request object
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not token:
        return False
    
    client_ip = request.client.host
    
    # Check if token exists and is valid
    if token in csrf_tokens:
        token_data = csrf_tokens[token]
        
        # Check expiration (tokens valid for 1 hour)
        if datetime.now() - token_data['created'] < timedelta(hours=1):
            # Optional: Check if token was issued to this IP
            # if token_data['ip'] == client_ip:
            return True
    
    return False

def cleanup_expired_tokens():
    """Removes expired CSRF tokens to prevent memory bloat"""
    current_time = datetime.now()
    expired_tokens = [
        token for token, data in csrf_tokens.items()
        if current_time - data['created'] > timedelta(hours=1)
    ]
    for token in expired_tokens:
        del csrf_tokens[token]

# ===================================================================
# SANITIZATION UTILITIES
# ===================================================================

def sanitize_input(text: str, max_length: int = None) -> str:
    """
    Sanitizes user input to prevent XSS and injection attacks
    
    Args:
        text: Raw input text
        max_length: Optional maximum length
    
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # HTML escape
    sanitized = html.escape(sanitized)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Enforce max length
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_and_sanitize_name(name: str) -> tuple[str, Optional[str]]:
    """
    Validates and sanitizes name input
    
    Returns:
        tuple: (sanitized_name, error_message)
    """
    name = sanitize_input(name, max_length=50)
    
    if not name:
        return name, "Name is required"
    elif len(name) < 2:
        return name, "Name must be at least 2 characters"
    elif len(name) > 50:
        return name, "Name must not exceed 50 characters"
    elif not re.match(r'^[a-zA-Z0-9\s-]+$', name):
        return name, "Name can only contain letters, numbers, spaces, and hyphens"
    
    return name, None

def validate_and_sanitize_email(email: str) -> tuple[str, Optional[str]]:
    """
    Validates and sanitizes email input
    
    Returns:
        tuple: (sanitized_email, error_message)
    """
    email = sanitize_input(email, max_length=255)
    
    if not email:
        return email, "Email is required"
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email, "Please enter a valid email address"
    
    return email, None

def validate_and_sanitize_message(message: str) -> tuple[str, Optional[str]]:
    """
    Validates and sanitizes message input
    
    Returns:
        tuple: (sanitized_message, error_message)
    """
    message = sanitize_input(message, max_length=1000)
    
    if not message:
        return message, "Message is required"
    elif len(message) < 10:
        return message, "Message must be at least 10 characters"
    elif len(message) > 1000:
        return message, "Message must not exceed 1000 characters"
    
    return message, None

# ===================================================================
# ROUTES
# ===================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface for the GitHub to App converter."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact form page with enhanced security."""
    return templates.TemplateResponse("contact_form_v2.html", {"request": request})

@app.get("/api/csrf-token")
async def get_csrf_token(request: Request):
    """
    Generates and returns a CSRF token
    
    Returns:
        JSON with CSRF token
    """
    # Cleanup expired tokens periodically
    cleanup_expired_tokens()
    
    # Generate new token
    token = generate_csrf_token()
    
    # Store token with metadata
    csrf_tokens[token] = {
        'created': datetime.now(),
        'ip': request.client.host
    }
    
    return JSONResponse(
        status_code=200,
        content={"csrf_token": token}
    )

@app.post("/contact")
async def submit_contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    csrf_token: str = Form(...),
    x_csrf_token: Optional[str] = Header(None)
):
    """
    Handle contact form submission with enhanced security
    
    Security features:
    - CSRF token validation
    - Input sanitization
    - XSS prevention
    - Rate limiting (via middleware)
    
    Args:
        request: FastAPI request object
        name: User's name
        email: User's email
        message: User's message
        csrf_token: CSRF token from form
        x_csrf_token: CSRF token from header
    
    Returns:
        JSON response with success or error status
    """
    errors = []
    
    try:
        # Validate CSRF token
        token_to_validate = x_csrf_token or csrf_token
        if not validate_csrf_token(token_to_validate, request):
            return JSONResponse(
                status_code=403,
                content={
                    "status": "error",
                    "message": "Invalid or expired security token. Please refresh the page and try again."
                }
            )
        
        # Validate and sanitize inputs
        name, name_error = validate_and_sanitize_name(name)
        if name_error:
            errors.append(name_error)
        
        email, email_error = validate_and_sanitize_email(email)
        if email_error:
            errors.append(email_error)
        
        message, message_error = validate_and_sanitize_message(message)
        if message_error:
            errors.append(message_error)
        
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
        
        # Log submission
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"Contact Form Submission - {timestamp}")
        print(f"{'='*60}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print(f"IP: {request.client.host}")
        print(f"{'='*60}\n")
        
        # Save to file (in production, use a database)
        os.makedirs("contact_submissions", exist_ok=True)
        safe_timestamp = timestamp.replace(':', '-').replace(' ', '_')
        submission_file = f"contact_submissions/{safe_timestamp}_{secrets.token_hex(4)}.txt"
        
        with open(submission_file, 'w', encoding='utf-8') as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Name: {name}\n")
            f.write(f"Email: {email}\n")
            f.write(f"IP: {request.client.host}\n")
            f.write(f"Message:\n{message}\n")
        
        # Invalidate used CSRF token (one-time use)
        if token_to_validate in csrf_tokens:
            del csrf_tokens[token_to_validate]
        
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
    # Sanitize filename to prevent directory traversal
    filename = os.path.basename(filename)
    file_path = f"generated_apps/{filename}"
    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a conversion task."""
    # Sanitize task_id
    task_id = re.sub(r'[^a-zA-Z0-9_-]', '', task_id)
    
    # This would integrate with a task queue system
    return {"status": "completed", "progress": 100}

# ===================================================================
# STARTUP/SHUTDOWN
# ===================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Create necessary directories
    os.makedirs("generated_apps", exist_ok=True)
    os.makedirs("temp_repos", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("contact_submissions", exist_ok=True)
    
    print("🔒 Security features enabled:")
    print("  ✅ CSRF protection")
    print("  ✅ Rate limiting")
    print("  ✅ XSS prevention")
    print("  ✅ Security headers")
    print("  ✅ Input sanitization")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Clear CSRF tokens
    csrf_tokens.clear()
    print("\n👋 Application shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
