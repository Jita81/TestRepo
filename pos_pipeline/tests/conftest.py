"""
Pytest configuration and fixtures for POS Pipeline tests.
"""
import pytest
import asyncio
from pathlib import Path
import shutil
import tempfile
from services.text_processor import TextProcessor
from services.video_generator import VideoGenerator
from services.model_converter import ModelConverter
from services.orchestrator import PipelineOrchestrator
from config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (storage_dir / "videos").mkdir(exist_ok=True)
    (storage_dir / "models").mkdir(exist_ok=True)
    
    # Override settings for tests
    original_storage = settings.storage_path
    settings.storage_path = str(storage_dir)
    
    yield storage_dir
    
    # Restore original settings
    settings.storage_path = original_storage
    
    # Cleanup
    if storage_dir.exists():
        shutil.rmtree(storage_dir)


@pytest.fixture
def text_processor():
    """Create TextProcessor instance."""
    return TextProcessor()


@pytest.fixture
def video_generator(temp_storage):
    """Create VideoGenerator instance with temp storage."""
    return VideoGenerator()


@pytest.fixture
def model_converter(temp_storage):
    """Create ModelConverter instance with temp storage."""
    return ModelConverter()


@pytest.fixture
def orchestrator(temp_storage):
    """Create PipelineOrchestrator instance."""
    return PipelineOrchestrator()


@pytest.fixture
def sample_text():
    """Sample text input for testing."""
    return "A modern red and white POS display stand for electronics products"


@pytest.fixture
def sample_input_data(sample_text):
    """Sample PipelineInput for testing."""
    from models.schemas import PipelineInput
    return PipelineInput(
        text=sample_text,
        metadata={"category": "electronics"}
    )