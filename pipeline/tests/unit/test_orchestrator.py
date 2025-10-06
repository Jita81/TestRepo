"""
Unit tests for PipelineOrchestrator.
"""

import pytest
from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import PipelineStatus
from src.core.base import PipelineStage, ProcessingError
from typing import Dict, Any


class MockStage(PipelineStage):
    """Mock pipeline stage for testing."""
    
    def __init__(self, config: Dict[str, Any], should_fail: bool = False):
        self.should_fail = should_fail
        super().__init__(config)
    
    async def validate(self, data: Dict[str, Any], is_input: bool = True) -> bool:
        return True
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.should_fail:
            raise ProcessingError(
                stage=self.stage_name,
                message="Mock stage failure"
            )
        
        return {
            **input_data,
            f"{self.stage_name}_processed": True
        }


@pytest.mark.asyncio
class TestPipelineOrchestrator:
    """Test cases for PipelineOrchestrator."""
    
    async def test_orchestrator_initialization(self, status_tracker):
        """Test orchestrator initialization."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        assert len(orchestrator.stages) == 0
        assert orchestrator.status_tracker is not None
    
    async def test_add_stage(self, status_tracker):
        """Test adding stages to orchestrator."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        
        stage1 = MockStage({"name": "stage1"})
        stage2 = MockStage({"name": "stage2"})
        
        orchestrator.add_stage(stage1)
        orchestrator.add_stage(stage2)
        
        assert len(orchestrator.stages) == 2
    
    async def test_clear_stages(self, status_tracker):
        """Test clearing all stages."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        
        orchestrator.add_stage(MockStage({"name": "stage1"}))
        orchestrator.add_stage(MockStage({"name": "stage2"}))
        
        orchestrator.clear_stages()
        assert len(orchestrator.stages) == 0
    
    async def test_execute_pipeline_success(self, status_tracker):
        """Test successful pipeline execution."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        
        orchestrator.add_stage(MockStage({"name": "stage1"}))
        orchestrator.add_stage(MockStage({"name": "stage2"}))
        
        input_data = {"test": "data"}
        result = await orchestrator.execute_pipeline(input_data)
        
        assert "execution_id" in result
        assert result["MockStage_processed"] is True
        
        # Check status
        status = await status_tracker.get_status(result["execution_id"])
        assert status["status"] == PipelineStatus.COMPLETED.value
        assert status["progress"] == 100
    
    async def test_execute_pipeline_failure(self, status_tracker):
        """Test pipeline execution with stage failure."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        
        orchestrator.add_stage(MockStage({"name": "stage1"}))
        orchestrator.add_stage(MockStage({"name": "stage2"}, should_fail=True))
        
        input_data = {"test": "data"}
        
        with pytest.raises(ProcessingError):
            await orchestrator.execute_pipeline(input_data)
    
    async def test_get_stage_info(self, status_tracker):
        """Test getting stage information."""
        orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
        
        config1 = {"name": "stage1", "param": "value1"}
        config2 = {"name": "stage2", "param": "value2"}
        
        orchestrator.add_stage(MockStage(config1))
        orchestrator.add_stage(MockStage(config2))
        
        stage_info = orchestrator.get_stage_info()
        
        assert len(stage_info) == 2
        assert stage_info[0]["name"] == "MockStage"
        assert stage_info[0]["config"] == config1
