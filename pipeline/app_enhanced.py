"""
Enhanced POS to 3D Pipeline API - Production Version.

This version includes:
- RabbitMQ message queue integration
- Circuit breaker pattern
- Prometheus metrics
- Object storage (MinIO)
- Retry mechanisms
- Health checks
- Production-grade error handling
"""

import asyncio
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import existing pipeline components
from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker, PipelineStatus
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager
from src.utils.logger import PipelineLogger

# Import new production components
from src.core.message_queue import AsyncPipelineQueue, MessageQueueConfig
from src.core.circuit_breaker import MultiCircuitBreaker
from src.core.metrics import metrics, get_metrics_text, get_metrics_content_type
from src.core.object_storage import AsyncObjectStorage, ObjectStorageConfig
from src.core.retry import retry_async, RetryConfig


# ============================================================================
# Configuration
# ============================================================================

config_manager = ConfigManager()
logger = PipelineLogger(name="pipeline_api_enhanced", level="INFO")

# Circuit breakers for different services
circuit_breakers = MultiCircuitBreaker(default_config={
    "failure_threshold": 5,
    "timeout": 60,
    "recovery_timeout": 30
})

# Message queue (optional - gracefully degrade if not available)
message_queue: Optional[AsyncPipelineQueue] = None
try:
    mq_config = MessageQueueConfig(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        username=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASS", "guest")
    )
    message_queue = AsyncPipelineQueue(mq_config)
except Exception as e:
    logger.warning(f"Message queue not available: {e}")

# Object storage (optional - gracefully degrade if not available)
object_storage: Optional[AsyncObjectStorage] = None
try:
    storage_config = ObjectStorageConfig(
        endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
    )
    object_storage = AsyncObjectStorage(storage_config)
except Exception as e:
    logger.warning(f"Object storage not available: {e}")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="POS to 3D Pipeline API - Enhanced",
    description="Production-ready pipeline for converting marketing POS descriptions to 3D models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ProcessRequest(BaseModel):
    """Request model for processing POS description."""
    text: str = Field(..., min_length=10, max_length=5000, description="POS description")
    priority: int = Field(default=0, ge=0, le=9, description="Processing priority (0-9)")
    use_async: bool = Field(default=False, description="Use async processing via message queue")
    upload_to_storage: bool = Field(default=False, description="Upload results to object storage")


class ProcessResponse(BaseModel):
    """Response model for process request."""
    job_id: str
    status: str
    message: str
    estimated_time_seconds: Optional[int] = None
    queue_position: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Starting POS to 3D Pipeline API (Enhanced)")
    
    # Ensure directories exist
    config_manager.ensure_directories()
    
    # Connect to message queue
    if message_queue:
        try:
            await message_queue.connect()
            logger.info("Connected to message queue")
        except Exception as e:
            logger.warning(f"Failed to connect to message queue: {e}")
    
    # Connect to object storage
    if object_storage:
        try:
            await object_storage.connect()
            logger.info("Connected to object storage")
        except Exception as e:
            logger.warning(f"Failed to connect to object storage: {e}")
    
    # Set system info metrics
    metrics.set_system_info({
        "version": "2.0.0",
        "python_version": os.sys.version,
        "environment": os.getenv("ENVIRONMENT", "production")
    })
    
    logger.info("Pipeline API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Pipeline API")
    
    if message_queue:
        await message_queue.close()
    
    if object_storage:
        await object_storage.close()
    
    logger.info("Shutdown complete")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service health and component status.
    """
    components = {
        "api": "healthy",
        "message_queue": "healthy" if message_queue and message_queue.queue._is_connected else "unavailable",
        "object_storage": "healthy" if object_storage and object_storage.storage._is_connected else "unavailable"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        components=components
    )


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format.
    """
    return Response(
        content=get_metrics_text(),
        media_type=get_metrics_content_type()
    )


@app.post("/api/v1/process", response_model=ProcessResponse)
@metrics.track_request()
async def process_text(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Process POS description to generate video and 3D model.
    
    Supports both synchronous and asynchronous processing.
    """
    start_time = time.time()
    job_id = f"job_{int(time.time() * 1000)}"
    
    logger.info(f"Received process request: {job_id}")
    metrics.record_request("/api/v1/process", "POST", "received")
    
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Async processing via message queue
        if request.use_async and message_queue:
            success = await message_queue.publish_message(
                message_queue.queue.TEXT_TO_VIDEO_QUEUE,
                {
                    "job_id": job_id,
                    "text": request.text,
                    "upload_to_storage": request.upload_to_storage
                },
                priority=request.priority
            )
            
            if success:
                queue_size = await message_queue.get_queue_size(
                    message_queue.queue.TEXT_TO_VIDEO_QUEUE
                )
                
                metrics.set_queue_size(message_queue.queue.TEXT_TO_VIDEO_QUEUE, queue_size)
                
                return ProcessResponse(
                    job_id=job_id,
                    status="queued",
                    message="Request queued for async processing",
                    estimated_time_seconds=120,
                    queue_position=queue_size
                )
            else:
                # Fallback to sync processing
                logger.warning("Failed to queue job, falling back to sync processing")
        
        # Synchronous processing
        background_tasks.add_task(
            process_pipeline_sync,
            job_id,
            request.text,
            request.upload_to_storage
        )
        
        metrics.record_request("/api/v1/process", "POST", "success")
        
        return ProcessResponse(
            job_id=job_id,
            status="processing",
            message="Request accepted for processing",
            estimated_time_seconds=120
        )
    
    except HTTPException:
        metrics.record_request("/api/v1/process", "POST", "error")
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        metrics.record_request("/api/v1/process", "POST", "error")
        metrics.record_error("api", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status for a job."""
    try:
        tracker = StatusTracker()
        status = tracker.get_status(job_id)
        
        if status:
            return {
                "job_id": job_id,
                **status
            }
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/circuit-breakers")
async def get_circuit_breaker_stats():
    """Get circuit breaker statistics."""
    return circuit_breakers.get_all_stats()


# ============================================================================
# Background Processing
# ============================================================================

@circuit_breakers.get("pipeline").call
@retry_async(RetryConfig(max_attempts=3, initial_delay=2.0))
async def process_pipeline_sync(
    job_id: str,
    text: str,
    upload_to_storage: bool = False
):
    """
    Process pipeline synchronously with circuit breaker and retry.
    
    Args:
        job_id: Unique job identifier
        text: Input text description
        upload_to_storage: Whether to upload results to object storage
    """
    logger.info(f"Processing job {job_id}")
    
    try:
        # Create pipeline
        tracker = StatusTracker()
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        
        # Add stages
        text_config = config_manager.get_stage_config("text_processor")
        video_config = config_manager.get_stage_config("video_generator")
        model_config = config_manager.get_stage_config("model_converter")
        
        orchestrator.add_stage(TextProcessor(text_config))
        orchestrator.add_stage(VideoGenerator(video_config))
        orchestrator.add_stage(ModelConverter(model_config))
        
        # Execute
        result = await orchestrator.execute_pipeline(
            {"text": text},
            execution_id=job_id
        )
        
        # Record metrics
        metrics.record_video_generated()
        metrics.record_model_generated()
        
        if "video_path" in result:
            video_path = Path(result["video_path"])
            if video_path.exists():
                metrics.record_output_size("video", video_path.stat().st_size)
        
        if "model_path" in result:
            model_path = Path(result["model_path"])
            if model_path.exists():
                metrics.record_output_size("model", model_path.stat().st_size)
        
        # Upload to object storage if requested
        if upload_to_storage and object_storage:
            await upload_results_to_storage(job_id, result)
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        metrics.record_error("pipeline", type(e).__name__)
        raise


async def upload_results_to_storage(job_id: str, result: dict):
    """Upload processing results to object storage."""
    if not object_storage:
        return
    
    try:
        # Upload video
        if "video_path" in result:
            await object_storage.upload_file(
                object_storage.storage.VIDEO_BUCKET,
                f"{job_id}/video.mp4",
                result["video_path"],
                "video/mp4"
            )
        
        # Upload model
        if "model_path" in result:
            await object_storage.upload_file(
                object_storage.storage.MODEL_BUCKET,
                f"{job_id}/model.stl",
                result["model_path"],
                "application/sla"
            )
        
        logger.info(f"Uploaded results for {job_id} to object storage")
    
    except Exception as e:
        logger.error(f"Failed to upload results: {e}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )
