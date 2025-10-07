"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common import QueueClient
from common.config import Settings


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_settings(temp_storage):
    """Create test settings."""
    settings = Settings(
        api_host="127.0.0.1",
        api_port=8001,
        queue_host="localhost",
        queue_port=5672,
        storage_base_path=str(temp_storage),
        video_storage_path=str(temp_storage / "videos"),
        model_storage_path=str(temp_storage / "models"),
        temp_storage_path=str(temp_storage / "temp"),
        log_level="DEBUG"
    )
    return settings


@pytest.fixture
def mock_queue_client():
    """Create mock queue client."""
    mock = MagicMock(spec=QueueClient)
    mock.connection = MagicMock()
    mock.channel = MagicMock()
    mock.connect.return_value = None
    mock.publish.return_value = None
    mock.declare_queue.return_value = None
    return mock


@pytest.fixture
def sample_text_input():
    """Sample text input for testing."""
    return {
        "description": "A modern retail display for energy drinks with LED backlighting",
        "metadata": {"customer_id": "test123"}
    }


@pytest.fixture
def sample_pipeline_message():
    """Sample pipeline message for testing."""
    from common import PipelineMessage, PipelineStage, PipelineStatus
    
    return PipelineMessage(
        request_id="test_req_123",
        stage=PipelineStage.INPUT,
        payload={
            "description": "Test description",
            "metadata": {}
        },
        status=PipelineStatus.PENDING
    )