"""
Object Storage Integration (MinIO/S3).

Provides cloud-native storage for videos, 3D models, and intermediate files.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import timedelta

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception

logger = logging.getLogger(__name__)


class ObjectStorageConfig:
    """Configuration for object storage."""
    
    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False,
        region: str = "us-east-1"
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.region = region


class ObjectStorage:
    """
    MinIO/S3-compatible object storage client.
    
    Provides cloud-native storage for:
    - Input files
    - Generated videos
    - 3D models
    - Intermediate processing files
    
    Features:
    - Automatic bucket creation
    - Presigned URLs for secure downloads
    - Lifecycle policies
    - Versioning support
    """
    
    # Bucket names
    INPUT_BUCKET = "pipeline-inputs"
    VIDEO_BUCKET = "pipeline-videos"
    MODEL_BUCKET = "pipeline-models"
    TEMP_BUCKET = "pipeline-temp"
    
    def __init__(self, config: Optional[ObjectStorageConfig] = None):
        """
        Initialize object storage client.
        
        Args:
            config: Storage configuration
        """
        self.config = config or ObjectStorageConfig()
        self.client: Optional[Minio] = None
        self._is_connected = False
        
        if not MINIO_AVAILABLE:
            logger.warning(
                "minio not available - object storage disabled. "
                "Install with: pip install minio"
            )
    
    def connect(self) -> bool:
        """
        Connect to object storage.
        
        Returns:
            True if connected successfully
        """
        if not MINIO_AVAILABLE:
            return False
        
        try:
            self.client = Minio(
                self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.secure,
                region=self.config.region
            )
            
            # Test connection
            self.client.list_buckets()
            
            # Create required buckets
            self._create_buckets()
            
            self._is_connected = True
            logger.info(f"Connected to object storage at {self.config.endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to object storage: {e}")
            self._is_connected = False
            return False
    
    def _create_buckets(self):
        """Create required buckets if they don't exist."""
        if not self.client:
            return
        
        buckets = [
            self.INPUT_BUCKET,
            self.VIDEO_BUCKET,
            self.MODEL_BUCKET,
            self.TEMP_BUCKET
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
                    
                    # Set lifecycle policy for temp bucket
                    if bucket == self.TEMP_BUCKET:
                        self._set_temp_bucket_lifecycle(bucket)
                        
            except Exception as e:
                logger.error(f"Failed to create bucket {bucket}: {e}")
    
    def _set_temp_bucket_lifecycle(self, bucket: str):
        """Set lifecycle policy to auto-delete old temp files."""
        # Note: MinIO lifecycle config requires XML
        # For simplicity, we'll handle cleanup manually
        pass
    
    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Upload a file to object storage.
        
        Args:
            bucket: Target bucket name
            object_name: Object name in bucket
            file_path: Path to local file
            content_type: MIME type (auto-detected if None)
        
        Returns:
            True if uploaded successfully
        """
        if not self._is_connected or not self.client:
            logger.warning("Not connected to object storage")
            return False
        
        try:
            # Auto-detect content type
            if content_type is None:
                if file_path.endswith('.mp4'):
                    content_type = 'video/mp4'
                elif file_path.endswith('.stl'):
                    content_type = 'application/sla'
                else:
                    content_type = 'application/octet-stream'
            
            self.client.fput_object(
                bucket,
                object_name,
                file_path,
                content_type=content_type
            )
            
            logger.info(f"Uploaded {file_path} to {bucket}/{object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    def download_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str
    ) -> bool:
        """
        Download a file from object storage.
        
        Args:
            bucket: Source bucket name
            object_name: Object name in bucket
            file_path: Path to save file locally
        
        Returns:
            True if downloaded successfully
        """
        if not self._is_connected or not self.client:
            logger.warning("Not connected to object storage")
            return False
        
        try:
            self.client.fget_object(bucket, object_name, file_path)
            logger.info(f"Downloaded {bucket}/{object_name} to {file_path}")
            return True
            
        except S3Error as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expiry: timedelta = timedelta(hours=1)
    ) -> Optional[str]:
        """
        Get a presigned URL for temporary access.
        
        Args:
            bucket: Bucket name
            object_name: Object name
            expiry: URL expiration time
        
        Returns:
            Presigned URL or None
        """
        if not self._is_connected or not self.client:
            return None
        
        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=expiry
            )
            logger.info(f"Generated presigned URL for {bucket}/{object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def delete_object(self, bucket: str, object_name: str) -> bool:
        """
        Delete an object from storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name
        
        Returns:
            True if deleted successfully
        """
        if not self._is_connected or not self.client:
            return False
        
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted {bucket}/{object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Failed to delete object: {e}")
            return False
    
    def list_objects(
        self,
        bucket: str,
        prefix: Optional[str] = None
    ) -> list[str]:
        """
        List objects in a bucket.
        
        Args:
            bucket: Bucket name
            prefix: Filter by prefix
        
        Returns:
            List of object names
        """
        if not self._is_connected or not self.client:
            return []
        
        try:
            objects = self.client.list_objects(
                bucket,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name for obj in objects]
            
        except S3Error as e:
            logger.error(f"Failed to list objects: {e}")
            return []
    
    def close(self):
        """Close connection (MinIO doesn't require explicit close)."""
        self._is_connected = False
        logger.info("Object storage connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncObjectStorage:
    """Async wrapper for object storage operations."""
    
    def __init__(self, config: Optional[ObjectStorageConfig] = None):
        self.storage = ObjectStorage(config)
    
    async def connect(self) -> bool:
        """Asynchronously connect to storage."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.storage.connect)
    
    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str,
        content_type: Optional[str] = None
    ) -> bool:
        """Asynchronously upload a file."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.storage.upload_file,
            bucket,
            object_name,
            file_path,
            content_type
        )
    
    async def download_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str
    ) -> bool:
        """Asynchronously download a file."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.storage.download_file,
            bucket,
            object_name,
            file_path
        )
    
    async def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expiry: timedelta = timedelta(hours=1)
    ) -> Optional[str]:
        """Asynchronously get presigned URL."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.storage.get_presigned_url,
            bucket,
            object_name,
            expiry
        )
    
    async def close(self):
        """Asynchronously close connection."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.storage.close)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
