"""
GitHub to App Converter with User Registration
A tool that converts any GitHub repository into a working application
using README analysis and agentic coding.

Now includes user authentication with registration endpoint.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
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
import hashlib
import re
import json
from datetime import datetime, timedelta

from src.github_integration import GitHubRepository
from src.readme_parser import ReadmeParser
from src.app_generator import AppGenerator
from src.agentic_coder import AgenticCoder

app = FastAPI(title="GitHub to App Converter", version="1.0.0")

# CSRF Protection Configuration
CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_EXPIRY = 3600  # 1 hour in seconds
csrf_tokens = {}  # In production, use Redis or database

# User Storage (In production, use a proper database)
users_db = {}  # {email: {password_hash: str, created_at: datetime, ...}}

# Registration Rate Limiting
registration_attempts = {}  # {ip: [timestamps]}
REGISTRATION_RATE_LIMIT = 5  # Max registrations per IP per hour
REGISTRATION_WINDOW = 3600  # 1 hour in seconds


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


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 with salt
    In production, use bcrypt or argon2
    """
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split('$')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return secrets.compare_digest(pwd_hash, computed_hash)
    except:
        return False


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    
    # Check for special characters in local part
    local_part = email.split('@')[0]
    if any(char in '<>()[]\\,;:\s"' for char in local_part.replace('.', '')):
        return False, "Email contains invalid characters"
    
    # Check length
    if len(email) > 254:
        return False, "Email is too long"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password against requirements
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    if not password:
        return False, ["Password is required"]
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def check_registration_rate_limit(ip_address: str) -> tuple[bool, str]:
    """
    Check if IP has exceeded registration rate limit
    Returns: (is_allowed, error_message)
    """
    current_time = time.time()
    
    # Clean old attempts
    if ip_address in registration_attempts:
        registration_attempts[ip_address] = [
            timestamp for timestamp in registration_attempts[ip_address]
            if current_time - timestamp < REGISTRATION_WINDOW
        ]
    
    # Check rate limit
    attempts = registration_attempts.get(ip_address, [])
    if len(attempts) >= REGISTRATION_RATE_LIMIT:
        return False, "Too many registration attempts. Please try again later."
    
    return True, ""


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


@app.post("/api/auth/register")
async def register_user(request: Request):
    """
    Register a new user
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    Returns:
    {
        "success": true,
        "message": "Registration successful",
        "user_id": "..."
    }
    """
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # Check rate limit
    is_allowed, rate_limit_message = check_registration_rate_limit(client_ip)
    if not is_allowed:
        raise HTTPException(status_code=429, detail=rate_limit_message)
    
    # Parse request body
    try:
        body = await request.json()
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    # Validate email
    email_valid, email_error = validate_email(email)
    if not email_valid:
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validate password
    password_valid, password_errors = validate_password(password)
    if not password_valid:
        raise HTTPException(
            status_code=400,
            detail="Password does not meet requirements",
            headers={"X-Password-Errors": json.dumps(password_errors)}
        )
    
    # Check if email already exists
    if email in users_db:
        raise HTTPException(
            status_code=409,
            detail="This email address is already registered"
        )
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    users_db[email] = {
        'user_id': user_id,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active'
    }
    
    # Record registration attempt
    if client_ip not in registration_attempts:
        registration_attempts[client_ip] = []
    registration_attempts[client_ip].append(time.time())
    
    return {
        "success": True,
        "message": "Registration successful",
        "user_id": user_id
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
