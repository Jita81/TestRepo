"""
Contact form API routes and endpoints.
Implements secure form submission with CSRF protection and rate limiting.
"""

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
import secrets
from datetime import datetime

from .database import db
from .contact_validation import validator, ValidationError


router = APIRouter(prefix="/api", tags=["contact"])


# In-memory CSRF token store (use Redis in production)
csrf_tokens = {}


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = datetime.now()
    return token


def validate_csrf_token(token: str) -> bool:
    """
    Validate CSRF token.
    
    Args:
        token: CSRF token to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if token not in csrf_tokens:
        return False
    
    # Clean up old tokens (older than 1 hour)
    now = datetime.now()
    expired_tokens = [
        t for t, timestamp in csrf_tokens.items()
        if (now - timestamp).total_seconds() > 3600
    ]
    for t in expired_tokens:
        del csrf_tokens[t]
    
    return True


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Client IP address
    """
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"


@router.get("/csrf-token")
async def get_csrf_token():
    """
    Generate and return a CSRF token.
    
    Returns:
        JSON with CSRF token
    """
    token = generate_csrf_token()
    return JSONResponse({
        "success": True,
        "csrf_token": token
    })


@router.post("/contact")
async def submit_contact_form(
    request: Request,
    fullName: str = Form(..., max_length=100),
    email: str = Form(..., max_length=254),
    csrf_token: str = Form(...)
):
    """
    Handle contact form submission.
    
    Args:
        request: FastAPI request object
        fullName: Contact's full name
        email: Contact's email address
        csrf_token: CSRF protection token
    
    Returns:
        JSON response with success/error message
    
    Raises:
        HTTPException: For validation errors or rate limiting
    """
    try:
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Validate CSRF token
        if not validate_csrf_token(csrf_token):
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "message": "Invalid CSRF token. Please refresh the page and try again."
                }
            )
        
        # Check rate limiting
        is_allowed, remaining = db.check_rate_limit(
            client_ip,
            max_requests=5,
            window_minutes=15
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 900  # 15 minutes in seconds
                }
            )
        
        # Validate and sanitize inputs
        try:
            validated_data = validator.validate_contact_form(fullName, email)
        except ValidationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.errors
                }
            )
        
        # Store in database
        contact_id = db.insert_contact(
            full_name=validated_data['fullName'],
            email=validated_data['email'],
            ip_address=client_ip,
            user_agent=user_agent[:500]  # Truncate user agent
        )
        
        # Invalidate used CSRF token
        if csrf_token in csrf_tokens:
            del csrf_tokens[csrf_token]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Thank you for your message! We'll be in touch soon.",
                "contact_id": contact_id,
                "remaining_requests": remaining - 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error in production
        print(f"Error processing contact form: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "An unexpected error occurred. Please try again later."
            }
        )


@router.get("/contacts")
async def get_contacts(
    limit: int = 100,
    offset: int = 0
):
    """
    Retrieve submitted contacts (admin endpoint - should be protected).
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
    
    Returns:
        JSON with list of contacts
    """
    try:
        contacts = db.get_contacts(limit=min(limit, 1000), offset=offset)
        return JSONResponse({
            "success": True,
            "contacts": contacts,
            "count": len(contacts)
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to retrieve contacts"
            }
        )