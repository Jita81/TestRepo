"""Tests for configuration management."""

import pytest
from pathlib import Path
from common.config import Settings, get_settings, ensure_directories


class TestSettings:
    """Tests for Settings class."""
    
    def test_default_settings(self):
        """Test that default settings are created."""
        settings = Settings()
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.queue_host == "localhost"
        assert settings.queue_port == 5672
    
    def test_custom_settings(self):
        """Test custom settings override."""
        settings = Settings(
            api_host="127.0.0.1",
            api_port=9000,
            log_level="DEBUG"
        )
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000
        assert settings.log_level == "DEBUG"
    
    def test_video_settings(self):
        """Test video generation settings."""
        settings = Settings()
        assert settings.video_frame_rate == 30
        assert settings.video_duration == 30
        assert settings.video_width == 512
        assert settings.video_height == 512
    
    def test_storage_settings(self):
        """Test storage path settings."""
        settings = Settings()
        assert "storage" in settings.storage_base_path
        assert "videos" in settings.video_storage_path
        assert "models" in settings.model_storage_path


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_get_settings_returns_instance(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)


class TestEnsureDirectories:
    """Tests for ensure_directories function."""
    
    def test_ensure_directories_creates_paths(self, temp_storage):
        """Test that directories are created."""
        settings = Settings(
            storage_base_path=str(temp_storage),
            video_storage_path=str(temp_storage / "videos"),
            model_storage_path=str(temp_storage / "models"),
            temp_storage_path=str(temp_storage / "temp"),
            log_file=str(temp_storage / "logs" / "test.log")
        )
        
        ensure_directories(settings)
        
        assert Path(settings.storage_base_path).exists()
        assert Path(settings.video_storage_path).exists()
        assert Path(settings.model_storage_path).exists()
        assert Path(settings.temp_storage_path).exists()
        assert Path(settings.log_file).parent.exists()