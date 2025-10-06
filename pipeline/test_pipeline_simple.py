"""
Simple test script to verify pipeline functionality without pytest.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager


async def test_text_processor():
    """Test TextProcessor stage."""
    print("Testing TextProcessor...")
    
    config = {
        "max_text_length": 5000,
        "min_text_length": 10,
        "enable_enhancement": True
    }
    
    processor = TextProcessor(config)
    
    input_data = {
        "text": "A vibrant red and blue rotating display stand featuring energy drink products"
    }
    
    try:
        result = await processor.execute(input_data)
        assert "processed_text" in result
        assert "keywords" in result
        assert "visual_elements" in result
        print("✓ TextProcessor test passed")
        return True
    except Exception as e:
        print(f"✗ TextProcessor test failed: {e}")
        return False


async def test_config_manager():
    """Test ConfigManager."""
    print("Testing ConfigManager...")
    
    try:
        config_manager = ConfigManager()
        
        # Test getting config values
        log_level = config_manager.get("logging.level", "INFO")
        assert log_level is not None
        
        # Test stage config
        text_config = config_manager.get_stage_config("text_processor")
        assert isinstance(text_config, dict)
        
        print("✓ ConfigManager test passed")
        return True
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False


async def test_status_tracker():
    """Test StatusTracker."""
    print("Testing StatusTracker...")
    
    try:
        tracker = StatusTracker()
        
        # Create execution
        execution = await tracker.create_execution(
            "test_exec_001",
            {"text": "test input"}
        )
        
        assert execution["execution_id"] == "test_exec_001"
        assert execution["status"] == "pending"
        
        # Update stage
        await tracker.update_stage(
            "test_exec_001",
            "TestStage",
            "completed",
            result={"output": "test"}
        )
        
        # Get status
        status = await tracker.get_status("test_exec_001")
        assert status is not None
        assert len(status["stages"]) == 1
        
        print("✓ StatusTracker test passed")
        return True
    except Exception as e:
        print(f"✗ StatusTracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator():
    """Test PipelineOrchestrator."""
    print("Testing PipelineOrchestrator...")
    
    try:
        tracker = StatusTracker()
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        
        # Add text processor stage
        config = {
            "max_text_length": 5000,
            "min_text_length": 10,
            "enable_enhancement": True
        }
        orchestrator.add_stage(TextProcessor(config))
        
        # Execute pipeline
        input_data = {"text": "A modern display stand with vibrant colors and bold graphics"}
        result = await orchestrator.execute_pipeline(input_data, execution_id="test_orch_001")
        
        assert "execution_id" in result
        assert "processed_text" in result
        
        # Check status
        status = await tracker.get_status("test_orch_001")
        assert status["status"] == "completed"
        
        print("✓ PipelineOrchestrator test passed")
        return True
    except Exception as e:
        print(f"✗ PipelineOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Pipeline Tests")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(await test_config_manager())
    results.append(await test_status_tracker())
    results.append(await test_text_processor())
    results.append(await test_orchestrator())
    
    print()
    print("=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
