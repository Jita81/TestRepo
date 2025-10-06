"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from src.utils.config_manager import ConfigManager
from src.core.status_tracker import StatusTracker


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "text_processor": {
            "max_text_length": 5000,
            "min_text_length": 10,
            "enable_enhancement": True
        },
        "video_generator": {
            "min_duration": 30,
            "default_duration": 30,
            "fps": 24,
            "resolution": [1920, 1080],
            "format": "mp4"
        },
        "model_converter": {
            "output_format": "STL",
            "quality": "medium",
            "max_vertices": 1000000
        }
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def status_tracker(temp_dir):
    """Create a status tracker for testing."""
    persist_path = temp_dir / "status.json"
    return StatusTracker(persist_path=persist_path)


@pytest.fixture
def sample_text_input():
    """Sample text input for testing."""
    return {
        "text": "A vibrant red and blue rotating display stand featuring our new energy drink product with bold graphics and modern design"
    }


@pytest.fixture
def sample_processed_text():
    """Sample processed text output for testing."""
    return {
        "original_text": "A vibrant red and blue rotating display stand",
        "processed_text": "A vibrant red and blue rotating display stand.",
        "normalized_text": "A vibrant red and blue rotating display stand.",
        "keywords": ["vibrant", "red", "blue", "rotating", "display", "stand"],
        "visual_elements": {
            "colors": ["red", "blue"],
            "objects": ["display", "stand"],
            "actions": ["rotating"],
            "style_hints": []
        },
        "text_length": 47,
        "word_count": 8
    }


@pytest.fixture
def sample_video_output(temp_dir):
    """Sample video output for testing."""
    video_path = temp_dir / "test_video.mp4"
    # Create a minimal video file (empty for testing)
    video_path.touch()
    
    return {
        "processed_text": "A vibrant red and blue rotating display stand.",
        "video_path": str(video_path),
        "video_filename": "test_video.mp4",
        "duration": 30.0,
        "frame_count": 720,
        "fps": 24,
        "resolution": [1920, 1080],
        "format": "mp4"
    }


@pytest.fixture
def config_manager():
    """Create a config manager for testing."""
    return ConfigManager()
