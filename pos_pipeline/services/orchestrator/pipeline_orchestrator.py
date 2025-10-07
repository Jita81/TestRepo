"""
Pipeline Orchestrator Service.

This service coordinates the execution of all pipeline stages.
"""
import asyncio
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logging_config import get_logger
from utils.exceptions import PipelineException, TimeoutError as PipelineTimeoutError
from models.schemas import (
    PipelineInput,
    PipelineOutput,
    ProcessingStage,
    ProcessingStatus,
    PipelineError
)
from services.text_processor import TextProcessor
from services.video_generator import VideoGenerator
from services.model_converter import ModelConverter
from config.settings import settings


logger = get_logger("orchestrator")


class PipelineOrchestrator:
    """Orchestrates the complete pipeline from text to 3D model."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.video_generator = VideoGenerator()
        self.model_converter = ModelConverter()
        self.logger = logger
        
        # Job status tracking (in production, use Redis or database)
        self._job_statuses: Dict[str, ProcessingStatus] = {}
        self._job_results: Dict[str, PipelineOutput] = {}
        
    def _generate_job_id(self) -> str:
        """Generate unique job identifier."""
        return str(uuid.uuid4())
    
    def _update_status(
        self,
        job_id: str,
        stage: ProcessingStage,
        progress: float,
        message: str,
        error: Optional[str] = None
    ) -> None:
        """
        Update job processing status.
        
        Args:
            job_id: Job identifier
            stage: Current processing stage
            progress: Progress percentage
            message: Status message
            error: Error message if any
        """
        status = ProcessingStatus(
            job_id=job_id,
            stage=stage,
            progress=progress,
            message=message,
            error=error
        )
        
        self._job_statuses[job_id] = status
        self.logger.info(
            f"Job {job_id} - Stage: {stage.value}, Progress: {progress}%, Message: {message}"
        )
    
    async def _execute_with_timeout(
        self,
        coro,
        timeout: int,
        stage: ProcessingStage,
        job_id: str
    ):
        """
        Execute coroutine with timeout.
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            stage: Processing stage
            job_id: Job identifier
            
        Returns:
            Result of coroutine
            
        Raises:
            PipelineTimeoutError: If execution exceeds timeout
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise PipelineTimeoutError(
                f"Processing exceeded timeout of {timeout}s",
                stage=stage,
                details={"job_id": job_id, "timeout": timeout}
            )
    
    async def process(self, input_data: PipelineInput) -> str:
        """
        Process pipeline request asynchronously.
        
        Args:
            input_data: Pipeline input data
            
        Returns:
            Job ID for tracking
        """
        job_id = self._generate_job_id()
        
        # Start processing in background
        asyncio.create_task(self._process_pipeline(job_id, input_data))
        
        # Update initial status
        self._update_status(
            job_id,
            ProcessingStage.QUEUED,
            0.0,
            "Job queued for processing"
        )
        
        return job_id
    
    async def _process_pipeline(
        self,
        job_id: str,
        input_data: PipelineInput
    ) -> None:
        """
        Execute complete pipeline processing.
        
        Args:
            job_id: Unique job identifier
            input_data: Pipeline input data
        """
        start_time = time.time()
        stages_data = {}
        
        try:
            # Stage 1: Text Processing
            self._update_status(
                job_id,
                ProcessingStage.TEXT_PROCESSING,
                10.0,
                "Processing text input"
            )
            
            text_result = await self._execute_with_timeout(
                self.text_processor.process(job_id, input_data.text),
                settings.text_processing_timeout,
                ProcessingStage.TEXT_PROCESSING,
                job_id
            )
            
            stages_data["text_processing"] = {
                "processing_time": text_result.processing_time,
                "token_count": text_result.token_count,
                "keywords": text_result.metadata.get("keywords", [])
            }
            
            # Stage 2: Video Generation
            self._update_status(
                job_id,
                ProcessingStage.VIDEO_GENERATION,
                35.0,
                "Generating video from text"
            )
            
            video_result = await self._execute_with_timeout(
                self.video_generator.generate_video(job_id, text_result.processed_text),
                settings.video_generation_timeout,
                ProcessingStage.VIDEO_GENERATION,
                job_id
            )
            
            stages_data["video_generation"] = {
                "processing_time": video_result.processing_time,
                "duration": video_result.duration,
                "file_size_mb": video_result.file_size_mb,
                "resolution": video_result.resolution
            }
            
            # Stage 3: 3D Model Conversion
            self._update_status(
                job_id,
                ProcessingStage.MODEL_CONVERSION,
                70.0,
                "Converting video to 3D model"
            )
            
            model_result = await self._execute_with_timeout(
                self.model_converter.convert_to_3d(job_id, video_result.video_path),
                settings.model_conversion_timeout,
                ProcessingStage.MODEL_CONVERSION,
                job_id
            )
            
            stages_data["model_conversion"] = {
                "processing_time": model_result.processing_time,
                "vertex_count": model_result.vertex_count,
                "face_count": model_result.face_count,
                "file_size_mb": model_result.file_size_mb
            }
            
            # Pipeline completed successfully
            total_time = time.time() - start_time
            
            output = PipelineOutput(
                job_id=job_id,
                status=ProcessingStage.COMPLETED,
                video_url=video_result.video_url,
                model_url=model_result.model_url,
                video_path=video_result.video_path,
                model_path=model_result.model_path,
                processing_time=total_time,
                stages=stages_data,
                completed_at=datetime.utcnow()
            )
            
            self._job_results[job_id] = output
            
            self._update_status(
                job_id,
                ProcessingStage.COMPLETED,
                100.0,
                f"Pipeline completed successfully in {total_time:.2f}s"
            )
            
            self.logger.info(
                f"Pipeline completed for job {job_id} in {total_time:.2f}s"
            )
            
        except PipelineException as e:
            self.logger.error(f"Pipeline failed for job {job_id}: {e.message}")
            
            self._update_status(
                job_id,
                ProcessingStage.FAILED,
                0.0,
                f"Pipeline failed: {e.message}",
                error=e.message
            )
            
            # Store error result
            error_output = PipelineOutput(
                job_id=job_id,
                status=ProcessingStage.FAILED,
                processing_time=time.time() - start_time,
                stages=stages_data
            )
            self._job_results[job_id] = error_output
            
        except Exception as e:
            self.logger.error(f"Unexpected error in pipeline for job {job_id}: {str(e)}")
            
            self._update_status(
                job_id,
                ProcessingStage.FAILED,
                0.0,
                f"Unexpected error: {str(e)}",
                error=str(e)
            )
    
    def get_status(self, job_id: str) -> Optional[ProcessingStatus]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            ProcessingStatus if job exists, None otherwise
        """
        return self._job_statuses.get(job_id)
    
    def get_result(self, job_id: str) -> Optional[PipelineOutput]:
        """
        Get result of a completed job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            PipelineOutput if job is complete, None otherwise
        """
        return self._job_results.get(job_id)