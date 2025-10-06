"""
Pipeline orchestrator for managing stage execution.
"""

from typing import Dict, Any, List, Optional
import asyncio
import uuid
from datetime import datetime

from .base import PipelineStage, PipelineError, ProcessingError
from .status_tracker import StatusTracker, PipelineStatus


class PipelineOrchestrator:
    """
    Orchestrates execution of pipeline stages.
    
    Manages stage sequencing, error handling, and status tracking.
    """
    
    def __init__(self, status_tracker: Optional[StatusTracker] = None):
        """
        Initialize pipeline orchestrator.
        
        Args:
            status_tracker: Optional status tracker instance
        """
        self.stages: List[PipelineStage] = []
        self.status_tracker = status_tracker or StatusTracker()
    
    def add_stage(self, stage: PipelineStage):
        """
        Add a stage to the pipeline.
        
        Args:
            stage: Pipeline stage to add
        """
        self.stages.append(stage)
    
    def clear_stages(self):
        """Remove all stages from the pipeline."""
        self.stages.clear()
    
    async def execute_pipeline(
        self,
        input_data: Dict[str, Any],
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute all pipeline stages in sequence.
        
        Args:
            input_data: Initial input data for the pipeline
            execution_id: Optional execution ID (auto-generated if not provided)
            
        Returns:
            Final pipeline output data
            
        Raises:
            PipelineError: If any stage fails
        """
        # Generate execution ID if not provided
        if execution_id is None:
            execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        # Create execution tracking
        await self.status_tracker.create_execution(execution_id, input_data)
        await self.status_tracker.update_execution_status(
            execution_id,
            PipelineStatus.RUNNING
        )
        
        try:
            result = input_data
            total_stages = len(self.stages)
            
            for idx, stage in enumerate(self.stages):
                stage_name = stage.stage_name
                
                # Update status: stage starting
                await self.status_tracker.update_stage(
                    execution_id,
                    stage_name,
                    "running"
                )
                
                # Calculate progress
                progress = int((idx / total_stages) * 100)
                await self.status_tracker.update_execution_status(
                    execution_id,
                    PipelineStatus.RUNNING,
                    progress
                )
                
                try:
                    # Execute stage
                    result = await stage.execute(result)
                    
                    # Update status: stage completed
                    await self.status_tracker.update_stage(
                        execution_id,
                        stage_name,
                        "completed",
                        result=result
                    )
                    
                except PipelineError as e:
                    # Update status: stage failed
                    await self.status_tracker.update_stage(
                        execution_id,
                        stage_name,
                        "failed",
                        error=e.to_dict()
                    )
                    await self.status_tracker.update_execution_status(
                        execution_id,
                        PipelineStatus.FAILED,
                        progress
                    )
                    raise
            
            # Pipeline completed successfully
            await self.status_tracker.update_execution_status(
                execution_id,
                PipelineStatus.COMPLETED,
                100
            )
            
            # Add execution ID to result
            result["execution_id"] = execution_id
            
            return result
            
        except Exception as e:
            if not isinstance(e, PipelineError):
                error = ProcessingError(
                    stage="orchestrator",
                    message=f"Pipeline execution failed: {str(e)}",
                    details={"exception_type": type(e).__name__}
                )
                await self.status_tracker.update_execution_status(
                    execution_id,
                    PipelineStatus.FAILED
                )
                raise error
            raise
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a pipeline execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Status dictionary or None if not found
        """
        return await self.status_tracker.get_status(execution_id)
    
    def get_stage_info(self) -> List[Dict[str, Any]]:
        """
        Get information about configured stages.
        
        Returns:
            List of stage information dictionaries
        """
        return [
            {
                "name": stage.stage_name,
                "config": stage.config
            }
            for stage in self.stages
        ]
