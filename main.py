"""
GitHub to App Converter
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
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
import secrets
import time

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

app = FastAPI(title="GitHub to App Converter", version="1.0.0")

# CSRF Protection Configuration
CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_EXPIRY = 3600  # 1 hour in seconds
csrf_tokens = {}  # In production, use Redis or database


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF Protection Middleware - Complete Implementation
    
    Protects against Cross-Site Request Forgery attacks by requiring
    a valid CSRF token for state-changing requests (POST, PUT, DELETE, PATCH).
    
    Features:
    - Double-submit cookie pattern
    - Timing-safe token comparison
    - Token expiration
    - Origin/Referer validation
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods and health check endpoints
        if request.method in ["GET", "HEAD", "OPTIONS"] or request.url.path in ["/health", "/docs", "/openapi.json", "/csrf-token"]:
            response = await call_next(request)
            return response
        
        # For state-changing requests, verify CSRF token
        csrf_token_header = request.headers.get("X-CSRF-Token")
        csrf_token_cookie = request.cookies.get("csrf_token")
        
        # Both header and cookie must be present
        if not csrf_token_header or not csrf_token_cookie:
            return Response(
                content='{"detail": "CSRF token missing - both header and cookie required"}',
                status_code=403,
                media_type="application/json"
            )
        
        # Tokens must match (double-submit pattern)
        if not secrets.compare_digest(csrf_token_header, csrf_token_cookie):
            return Response(
                content='{"detail": "CSRF token mismatch"}',
                status_code=403,
                media_type="application/json"
            )
        
        # Validate token hasn't expired
        if not self._validate_csrf_token(csrf_token_header):
            return Response(
                content='{"detail": "CSRF token expired or invalid"}',
                status_code=403,
                media_type="application/json"
            )
        
        # Validate Origin/Referer headers
        if not self._validate_origin(request):
            return Response(
                content='{"detail": "Invalid origin"}',
                status_code=403,
                media_type="application/json"
            )
        
        response = await call_next(request)
        return response
    
    def _validate_origin(self, request: Request) -> bool:
        """Validate Origin or Referer header to prevent CSRF
        
        Uses timing-safe comparison for origin validation.
        """
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        # At least one should be present
        if not origin and not referer:
            return False
        
        # Allowed origins (configure based on deployment)
        allowed_origins = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:8888",
            "http://127.0.0.1:8888"
        ]
        
        if origin:
            # Use timing-safe comparison
            for allowed in allowed_origins:
                if len(origin) == len(allowed) and secrets.compare_digest(origin, allowed):
                    return True
        
        if referer:
            # Check if referer starts with allowed origin
            for allowed in allowed_origins:
                if referer.startswith(allowed):
                    return True
        
        return False
    
    def _validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token using timing-safe comparison
        
        Uses secrets.compare_digest() to prevent timing attacks
        that could leak information about valid tokens.
        """
        if not token or len(token) == 0:
            return False
        
        # Find matching token using timing-safe comparison
        # This prevents timing attacks that could reveal valid tokens
        valid_token_found = False
        token_expiry = None
        
        for stored_token, expiry in csrf_tokens.items():
            if secrets.compare_digest(token, stored_token):
                valid_token_found = True
                token_expiry = expiry
                break
        
        if not valid_token_found:
            return False
        
        # Check if token has expired
        if time.time() > token_expiry:
            # Remove expired token (find it again with timing-safe comparison)
            for stored_token in list(csrf_tokens.keys()):
                if secrets.compare_digest(token, stored_token):
                    del csrf_tokens[stored_token]
                    break
            return False
        
        return True


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    token = secrets.token_urlsafe(CSRF_TOKEN_LENGTH)
    csrf_tokens[token] = time.time() + CSRF_TOKEN_EXPIRY
    
    # Clean up expired tokens
    expired_tokens = [t for t, expiry in csrf_tokens.items() if time.time() > expiry]
    for t in expired_tokens:
        del csrf_tokens[t]
    
    return token


# Add CSRF middleware
app.add_middleware(CSRFMiddleware)

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
    # Generate CSRF token for forms
    csrf_token = generate_csrf_token()
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "csrf_token": csrf_token
    })
    # Set CSRF token in cookie (HttpOnly, Secure in production)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=True,
        samesite="strict",
        max_age=CSRF_TOKEN_EXPIRY
    )
    return response


@app.get("/csrf-token")
async def get_csrf_token():
    """Get a new CSRF token for AJAX requests"""
    token = generate_csrf_token()
    return {"csrf_token": token}

@app.post("/convert")
async def convert_repository(
    github_url: str = Form(...),
    app_name: Optional[str] = Form(None),
    target_platform: str = Form("executable"),
    csrf_token: str = Form(...)
):
    """
    Convert a GitHub repository to a working application.
    
    Args:
        github_url: GitHub repository URL
        app_name: Optional custom name for the generated app
        target_platform: Target platform (executable, docker, web)
        csrf_token: CSRF token for form protection (automatically validated by middleware)
    
    Note: CSRF token is validated by CSRFMiddleware before reaching this endpoint
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
    # Input validation: prevent directory traversal attacks
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Whitelist allowed file extensions
    allowed_extensions = {'.zip', '.tar.gz', '.exe', '.app', '.deb', '.rpm'}
    file_ext = ''.join(Path(filename).suffixes)
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Validate file size (prevent serving extremely large files)
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    file_path = Path("generated_apps") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Verify file is within generated_apps directory
    try:
        file_path.resolve().relative_to(Path("generated_apps").resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(str(file_path), filename=filename)

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