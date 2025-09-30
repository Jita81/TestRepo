"""Image processing and storage service."""

import os
import uuid
from typing import BinaryIO
from pathlib import Path
from PIL import Image
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings


class ImageService:
    """Service for handling image uploads and processing."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = settings.MAX_UPLOAD_SIZE
        self.allowed_types = settings.ALLOWED_IMAGE_TYPES
    
    def validate_image(self, file: UploadFile) -> None:
        """Validate image file type and size."""
        # Check content type
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(self.allowed_types)}"
            )
    
    async def save_image(self, file: UploadFile) -> str:
        """Save uploaded image and return the file path."""
        # Validate image
        self.validate_image(file)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {self.max_size / (1024 * 1024)}MB"
            )
        
        # Save original file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process image (resize, optimize)
        try:
            self._process_image(file_path)
        except Exception as e:
            # Clean up file if processing fails
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image processing failed: {str(e)}"
            )
        
        # Return relative path for storage in database
        return f"/uploads/profile_pictures/{unique_filename}"
    
    def _process_image(self, file_path: Path) -> None:
        """Process image: resize, optimize."""
        try:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize if too large (max 800x800)
                max_dimension = 800
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")
    
    def delete_image(self, image_path: str) -> None:
        """Delete image file."""
        if image_path and not image_path.startswith("http"):
            # Extract filename from path
            filename = os.path.basename(image_path)
            file_path = self.upload_dir / filename
            
            if file_path.exists():
                os.remove(file_path)