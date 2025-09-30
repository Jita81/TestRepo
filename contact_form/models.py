"""
Contact Form Data Models

This module defines the data models and validation schemas for the contact form.
Implements strict validation rules for name, email, and message fields.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class ContactFormRequest(BaseModel):
    """
    Contact form submission request model.
    
    Attributes:
        name: User's full name (2-100 characters, letters, spaces, hyphens only)
        email: Valid email address
        message: Message content (10-2000 characters)
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the person submitting the form"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address for contact"
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Message content"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """
        Validate name contains only letters, spaces, hyphens, and apostrophes.
        
        Args:
            v: Name value to validate
            
        Returns:
            str: Validated and stripped name
            
        Raises:
            ValueError: If name contains invalid characters
        """
        v = v.strip()
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError(
                "Name must contain only letters, spaces, hyphens, and apostrophes"
            )
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """
        Validate and sanitize message content.
        
        Args:
            v: Message value to validate
            
        Returns:
            str: Validated and stripped message
            
        Raises:
            ValueError: If message is too short after stripping whitespace
        """
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Message must be at least 10 characters long")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "message": "This is a sample message from the contact form."
            }
        }


class ContactFormResponse(BaseModel):
    """
    Successful contact form submission response.
    
    Attributes:
        success: Whether the submission was successful
        message: Human-readable response message
        submission_id: Unique identifier for this submission
        timestamp: When the submission was received
    """
    success: bool = True
    message: str = "Your message has been received. We'll get back to you soon!"
    submission_id: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Your message has been received. We'll get back to you soon!",
                "submission_id": "abc123def456",
                "timestamp": "2025-09-30T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model for validation or processing errors.
    
    Attributes:
        success: Always False for error responses
        message: Human-readable error message
        errors: Optional detailed error information
        error_code: Optional machine-readable error code
    """
    success: bool = False
    message: str
    errors: Optional[dict] = None
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": {
                    "email": ["Invalid email format"]
                },
                "error_code": "VALIDATION_ERROR"
            }
        }