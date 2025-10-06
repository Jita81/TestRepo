"""
Secure file handling utilities.
"""

import os
import hashlib
import shutil
from typing import Optional, BinaryIO
from pathlib import Path

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

try:
    import magic  # python-magic for file type detection
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class FileSecurityError(Exception):
    """File security error."""
    pass


class SecureFileHandler:
    """
    Handles file operations with security checks.
    """
    
    def __init__(self, base_path: Path, max_file_size: int = 1024 * 1024 * 1024):  # 1GB default
        """
        Initialize secure file handler.
        
        Args:
            base_path: Base path for file operations
            max_file_size: Maximum allowed file size in bytes
        """
        self.base_path = Path(base_path)
        self.max_file_size = max_file_size
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Allowed file extensions by category
        self.allowed_extensions = {
            "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            "model": [".stl", ".obj", ".ply", ".fbx", ".dae"],
            "text": [".txt", ".json", ".yaml", ".yml"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        }
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other issues.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove any directory components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00', '\n', '\r']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Ensure filename is not empty
        if not filename or filename == '.':
            filename = 'unnamed_file'
        
        return filename
    
    def get_safe_path(self, filename: str, subdirectory: str = "") -> Path:
        """
        Get safe file path within base directory.
        
        Args:
            filename: Filename (will be sanitized)
            subdirectory: Optional subdirectory within base path
            
        Returns:
            Safe file path
            
        Raises:
            FileSecurityError: If path escapes base directory
        """
        safe_filename = self.sanitize_filename(filename)
        
        if subdirectory:
            file_path = self.base_path / subdirectory / safe_filename
        else:
            file_path = self.base_path / safe_filename
        
        # Ensure path is within base directory
        try:
            file_path = file_path.resolve()
            self.base_path.resolve()
            
            if not str(file_path).startswith(str(self.base_path.resolve())):
                raise FileSecurityError("Path escapes base directory")
        except Exception as e:
            raise FileSecurityError(f"Invalid path: {e}")
        
        return file_path
    
    async def safe_save(
        self,
        data: bytes,
        filename: str,
        subdirectory: str = "",
        check_size: bool = True
    ) -> Path:
        """
        Safely save binary data to file.
        
        Args:
            data: Binary data to save
            filename: Target filename
            subdirectory: Optional subdirectory
            check_size: Whether to check file size
            
        Returns:
            Path to saved file
            
        Raises:
            FileSecurityError: If security checks fail
        """
        # Check file size
        if check_size and len(data) > self.max_file_size:
            raise FileSecurityError(
                f"File too large: {len(data)} bytes (max: {self.max_file_size})"
            )
        
        # Get safe path
        file_path = self.get_safe_path(filename, subdirectory)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        if HAS_AIOFILES:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)
        else:
            # Fallback to synchronous write
            with open(file_path, 'wb') as f:
                f.write(data)
        
        return file_path
    
    async def safe_copy(
        self,
        source_path: Path,
        filename: str,
        subdirectory: str = ""
    ) -> Path:
        """
        Safely copy a file.
        
        Args:
            source_path: Source file path
            filename: Target filename
            subdirectory: Optional subdirectory
            
        Returns:
            Path to copied file
            
        Raises:
            FileSecurityError: If security checks fail
        """
        # Validate source exists
        if not source_path.exists():
            raise FileSecurityError(f"Source file not found: {source_path}")
        
        # Check file size
        file_size = source_path.stat().st_size
        if file_size > self.max_file_size:
            raise FileSecurityError(
                f"File too large: {file_size} bytes (max: {self.max_file_size})"
            )
        
        # Get safe destination path
        dest_path = self.get_safe_path(filename, subdirectory)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        return dest_path
    
    def validate_file_type(
        self,
        file_path: Path,
        category: str
    ) -> bool:
        """
        Validate file type by extension and magic bytes.
        
        Args:
            file_path: Path to file
            category: Category (video, model, text, image)
            
        Returns:
            True if valid
            
        Raises:
            FileSecurityError: If validation fails
        """
        if category not in self.allowed_extensions:
            raise FileSecurityError(f"Unknown file category: {category}")
        
        # Check extension
        extension = file_path.suffix.lower()
        if extension not in self.allowed_extensions[category]:
            raise FileSecurityError(
                f"Invalid file extension for {category}: {extension}"
            )
        
        return True
    
    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file checksum
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    async def cleanup_old_files(self, days: int = 7):
        """
        Clean up files older than specified days.
        
        Args:
            days: Number of days to retain files
        """
        import time
        
        cutoff_time = time.time() - (days * 86400)
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"Warning: Failed to delete {file_path}: {e}")
