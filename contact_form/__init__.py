"""
Contact Form Package

A comprehensive contact form implementation with:
- Backend API (FastAPI)
- Frontend UI (HTML/CSS/JavaScript)
- Input validation (client and server-side)
- Error handling
- Comprehensive tests

Usage:
    from contact_form.api import app
    
    # Run with uvicorn
    # uvicorn contact_form.api:app --reload
"""

__version__ = "1.0.0"
__author__ = "Developer"
__description__ = "Contact form with validation and error handling"

from .models import ContactFormRequest, ContactFormResponse, ErrorResponse
from .api import app, ContactFormService

__all__ = [
    "app",
    "ContactFormRequest",
    "ContactFormResponse",
    "ErrorResponse",
    "ContactFormService"
]