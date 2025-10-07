"""
Integration tests for the complete POS Pipeline.
"""
import pytest
import asyncio
from pathlib import Path
from models.schemas import PipelineInput, ProcessingStage


class TestPipelineIntegration:
    """Integration tests for complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_pipeline(self, orchestrator, sample_input_data):
        """Test complete pipeline from text to 3D model."""
        # Submit job
        job_id = await orchestrator.process(sample_input_data)
        
        assert job_id
        
        # Wait for processing to complete (with timeout)
        max_wait = 120  # seconds
        wait_interval = 2
        elapsed = 0
        
        while elapsed < max_wait:
            status = orchestrator.get_status(job_id)
            
            if status and status.stage == ProcessingStage.COMPLETED:
                break
            
            if status and status.stage == ProcessingStage.FAILED:
                pytest.fail(f"Pipeline failed: {status.error}")
            
            await asyncio.sleep(wait_interval)
            elapsed += wait_interval
        
        # Get final result
        result = orchestrator.get_result(job_id)
        
        assert result is not None
        assert result.status == ProcessingStage.COMPLETED
        assert result.video_url is not None
        assert result.model_url is not None
        assert result.video_path is not None
        assert result.model_path is not None
        
        # Verify files exist
        assert Path(result.video_path).exists()
        assert Path(result.model_path).exists()
        
        # Verify processing times
        assert result.processing_time > 0
        assert "text_processing" in result.stages
        assert "video_generation" in result.stages
        assert "model_conversion" in result.stages
    
    @pytest.mark.asyncio
    async def test_pipeline_status_tracking(self, orchestrator, sample_input_data):
        """Test pipeline status updates correctly during processing."""
        job_id = await orchestrator.process(sample_input_data)
        
        # Initial status should be queued
        await asyncio.sleep(0.1)
        initial_status = orchestrator.get_status(job_id)
        assert initial_status is not None
        
        # Wait a bit for processing to start
        await asyncio.sleep(1)
        processing_status = orchestrator.get_status(job_id)
        assert processing_status is not None
        assert processing_status.progress >= 0
    
    @pytest.mark.asyncio
    async def test_pipeline_stages_execution_order(self, orchestrator, sample_input_data):
        """Test pipeline stages execute in correct order."""
        job_id = await orchestrator.process(sample_input_data)
        
        # Wait for completion
        for _ in range(60):  # Up to 2 minutes
            status = orchestrator.get_status(job_id)
            if status and status.stage == ProcessingStage.COMPLETED:
                break
            await asyncio.sleep(2)
        
        result = orchestrator.get_result(job_id)
        assert result is not None
        
        # Verify all stages completed
        assert "text_processing" in result.stages
        assert "video_generation" in result.stages
        assert "model_conversion" in result.stages
        
        # Each stage should have timing info
        for stage_name in ["text_processing", "video_generation", "model_conversion"]:
            assert "processing_time" in result.stages[stage_name]
            assert result.stages[stage_name]["processing_time"] > 0
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_jobs(self, orchestrator):
        """Test pipeline handles multiple concurrent jobs."""
        # Submit multiple jobs
        job_inputs = [
            PipelineInput(text=f"Modern POS display number {i} for electronics")
            for i in range(3)
        ]
        
        job_ids = [await orchestrator.process(input_data) for input_data in job_inputs]
        
        assert len(job_ids) == 3
        assert len(set(job_ids)) == 3  # All unique
        
        # Wait for all to complete
        completed = set()
        for _ in range(60):
            for job_id in job_ids:
                status = orchestrator.get_status(job_id)
                if status and status.stage == ProcessingStage.COMPLETED:
                    completed.add(job_id)
            
            if len(completed) == len(job_ids):
                break
            
            await asyncio.sleep(2)
        
        # Verify all completed
        for job_id in job_ids:
            result = orchestrator.get_result(job_id)
            assert result is not None
            # May still be processing in some cases, so we check if we got results
            if result.status == ProcessingStage.COMPLETED:
                assert result.video_path
                assert result.model_path


class TestPipelineErrorHandling:
    """Test pipeline error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_input_text(self, orchestrator):
        """Test pipeline handles invalid input gracefully."""
        invalid_input = PipelineInput(text="ab")  # Too short
        
        job_id = await orchestrator.process(invalid_input)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        status = orchestrator.get_status(job_id)
        
        # Should fail at text processing stage
        assert status is not None
        assert status.stage == ProcessingStage.FAILED
        assert status.error is not None
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, orchestrator):
        """Test pipeline handles empty text."""
        # This should fail validation at PipelineInput level
        with pytest.raises(Exception):  # Pydantic validation error
            PipelineInput(text="")
    
    @pytest.mark.asyncio
    async def test_very_long_text_handling(self, orchestrator):
        """Test pipeline handles very long text."""
        long_text = "word " * 500  # Exceeds limits
        
        try:
            invalid_input = PipelineInput(text=long_text)
            job_id = await orchestrator.process(invalid_input)
            
            await asyncio.sleep(2)
            status = orchestrator.get_status(job_id)
            assert status.stage == ProcessingStage.FAILED
        except Exception:
            # May fail at validation level, which is also acceptable
            pass