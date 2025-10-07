"""
Configuration settings for the POS Pipeline system.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Settings
    api_title: str = "POS Display Pipeline"
    api_description: str = "End-to-end pipeline for POS display generation"
    api_version: str = "1.0.0"
    api_key: str = "dev-key-change-in-production"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # RabbitMQ Settings
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Storage Settings
    storage_path: str = "/workspace/pos_pipeline/storage"
    max_storage_size_mb: int = 1000
    
    # Processing Limits
    max_text_length: int = 1024
    max_concurrent_processes: int = 5
    max_video_size_mb: int = 100
    max_model_size_mb: int = 50
    
    # Video Settings
    video_format: str = "mp4"
    min_video_duration: int = 30  # seconds
    video_fps: int = 24
    video_resolution: tuple = (512, 512)
    
    # Model Settings
    model_format: str = "stl"
    mesh_quality: str = "medium"
    
    # Timeout Settings
    text_processing_timeout: int = 60
    video_generation_timeout: int = 300
    model_conversion_timeout: int = 180
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/workspace/pos_pipeline/logs/pipeline.log"
    
    # Security
    cors_origins: list = ["*"]
    allowed_hosts: list = ["*"]


settings = Settings()