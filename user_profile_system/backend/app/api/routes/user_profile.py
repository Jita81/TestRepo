"""User profile API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.user import (
    UserProfileResponse,
    ProfileUpdateDTO,
    UserCreate,
    Token,
    LoginRequest,
    APIResponse,
    UserSettings
)
from app.services.user_service import UserService
from app.services.image_service import ImageService
from app.core.security import (
    get_current_user_id,
    verify_password,
    create_access_token
)
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """User login."""
    user_service = UserService(db)
    user = user_service.get_user_by_email(login_data.email)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get user profile by ID."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Convert to response model
    settings_obj = UserSettings(
        email_notifications=user.email_notifications,
        privacy_level=user.privacy_level,
        theme=user.theme
    )
    
    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        profile_picture=user.profile_picture,
        join_date=user.join_date,
        last_updated=user.last_updated,
        settings=settings_obj
    )


@router.put("/users/{user_id}/profile", response_model=APIResponse)
async def update_user_profile(
    user_id: str,
    update_data: ProfileUpdateDTO,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile."""
    user_service = UserService(db)
    
    # Check authorization
    if not user_service.check_authorization(current_user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this profile"
        )
    
    try:
        updated_user = user_service.update_profile(user_id, update_data)
        
        return APIResponse(
            data={
                "id": updated_user.id,
                "name": updated_user.name,
                "email": updated_user.email,
                "profile_picture": updated_user.profile_picture
            },
            status=status.HTTP_200_OK,
            message="Profile updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.patch("/users/{user_id}/profile/picture", response_model=APIResponse)
async def upload_profile_picture(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Upload and update profile picture."""
    user_service = UserService(db)
    
    # Check authorization
    if not user_service.check_authorization(current_user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this profile"
        )
    
    try:
        # Save and process image
        image_service = ImageService()
        image_path = await image_service.save_image(file)
        
        # Update user profile
        updated_user = user_service.update_profile_picture(user_id, image_path)
        
        return APIResponse(
            data={"profile_picture": updated_user.profile_picture},
            status=status.HTTP_200_OK,
            message="Profile picture updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile picture: {str(e)}"
        )


@router.get("/users/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's profile."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    settings_obj = UserSettings(
        email_notifications=user.email_notifications,
        privacy_level=user.privacy_level,
        theme=user.theme
    )
    
    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        profile_picture=user.profile_picture,
        join_date=user.join_date,
        last_updated=user.last_updated,
        settings=settings_obj
    )