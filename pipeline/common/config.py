"""Configuration management for the pipeline."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_timeout: int = 30
    api_key: Optional[str] = None
    
    # Queue Settings
    queue_host: str = "localhost"
    queue_port: int = 5672
    queue_username: str = "guest"
    queue_password: str = "guest"
    queue_retry_count: int = 3
    
    # Video Generation Settings
    video_model_path: str = "models/video_gen"
    video_frame_rate: int = 30
    video_duration: int = 30
    video_width: int = 512
    video_height: int = 512
    
    # Model Conversion Settings
    point_cloud_density: int = 1000
    mesh_quality: str = "medium"
    
    # Storage Settings
    storage_base_path: str = "storage"
    video_storage_path: str = "storage/videos"
    model_storage_path: str = "storage/models"
    temp_storage_path: str = "storage/temp"
    max_storage_mb: int = 10240  # 10GB
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/pipeline.log"
    json_logs: bool = True
    
    # Performance Settings
    max_concurrent_jobs: int = 3
    job_timeout_seconds: int = 600  # 10 minutes
    cleanup_interval_seconds: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def ensure_directories(settings: Settings) -> None:
    """Ensure all required directories exist."""
    directories = [
        settings.storage_base_path,
        settings.video_storage_path,
        settings.model_storage_path,
        settings.temp_storage_path,
        Path(settings.log_file).parent if settings.log_file else None,
    ]
    
    for directory in directories:
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)