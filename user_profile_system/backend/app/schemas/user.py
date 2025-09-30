"""User schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserSettings(BaseModel):
    """User settings schema."""
    email_notifications: bool = True
    privacy_level: str = Field(default="public", pattern="^(public|private|friends)$")
    theme: str = Field(default="light", pattern="^(light|dark)$")


class UserProfileBase(BaseModel):
    """Base user profile schema."""
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name format."""
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()


class UserProfileResponse(UserProfileBase):
    """User profile response schema."""
    id: str
    profile_picture: Optional[str] = None
    join_date: datetime
    last_updated: datetime
    settings: UserSettings
    
    class Config:
        from_attributes = True


class ProfileUpdateDTO(BaseModel):
    """Profile update data transfer object."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    settings: Optional[UserSettings] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name format."""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
                raise ValueError('Name contains invalid characters')
            return v.strip()
        return v


class UserCreate(UserProfileBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class APIResponse(BaseModel):
    """Generic API response schema."""
    data: Optional[dict] = None
    status: int
    message: str