"""User service layer for business logic."""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import ProfileUpdateDTO, UserCreate, UserSettings
from app.core.security import get_password_hash, sanitize_input
import uuid


class UserService:
    """User service for managing user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            name=sanitize_input(user_data.name),
            email=user_data.email.lower(),
            hashed_password=get_password_hash(user_data.password),
            join_date=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_profile(self, user_id: str, update_data: ProfileUpdateDTO) -> User:
        """Update user profile."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if update_data.name is not None:
            user.name = sanitize_input(update_data.name)
        
        if update_data.email is not None:
            # Check if new email is already taken by another user
            existing_user = self.get_user_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = update_data.email.lower()
        
        if update_data.profile_picture is not None:
            user.profile_picture = update_data.profile_picture
        
        if update_data.settings is not None:
            user.email_notifications = update_data.settings.email_notifications
            user.privacy_level = update_data.settings.privacy_level
            user.theme = update_data.settings.theme
        
        user.last_updated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_profile_picture(self, user_id: str, picture_url: str) -> User:
        """Update user profile picture."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.profile_picture = picture_url
        user.last_updated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def check_authorization(self, requesting_user_id: str, target_user_id: str) -> bool:
        """Check if requesting user is authorized to edit target user profile."""
        return requesting_user_id == target_user_id