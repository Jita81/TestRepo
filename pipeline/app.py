"""
FastAPI application for POS to 3D Pipeline.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from pathlib import Path
import uvicorn
import asyncio

from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker, PipelineStatus
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager
from src.utils.logger import PipelineLogger


# Initialize configuration
config_manager = ConfigManager()
config_manager.ensure_directories()

# Initialize logger
logger = PipelineLogger(
    level=config_manager.get("logging.level", "INFO"),
    log_file=config_manager.get("logging.log_file"),
    use_json=config_manager.get("logging.format") == "json"
)

# Initialize status tracker
status_tracker = StatusTracker(
    persist_path=Path("pipeline/storage/temp/status.json")
)

# Create FastAPI app
app = FastAPI(
    title="POS to 3D Pipeline",
    description="Convert marketing POS text descriptions to 3D models via video generation",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class PipelineInput(BaseModel):
    """Input model for pipeline execution."""
    text: str = Field(
        ...,
        description="Marketing POS display description",
        min_length=10,
        max_length=5000,
        example="A vibrant red and blue rotating display stand featuring our new energy drink product with bold graphics and modern design"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata"
    )


class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""
    execution_id: str
    status: str
    message: str
    status_url: str


class StatusResponse(BaseModel):
    """Response model for status check."""
    execution_id: str
    status: str
    progress: int
    current_stage: Optional[str]
    created_at: str
    updated_at: str
    stages: list
    errors: list


class ResultResponse(BaseModel):
    """Response model for pipeline results."""
    execution_id: str
    status: str
    video_path: Optional[str]
    model_path: Optional[str]
    metadata: Dict[str, Any]


def create_pipeline() -> PipelineOrchestrator:
    """
    Create and configure pipeline orchestrator.
    
    Returns:
        Configured PipelineOrchestrator instance
    """
    orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
    
    # Add pipeline stages
    orchestrator.add_stage(TextProcessor(
        config=config_manager.get_stage_config("text_processor")
    ))
    
    orchestrator.add_stage(VideoGenerator(
        config=config_manager.get_stage_config("video_generator")
    ))
    
    orchestrator.add_stage(ModelConverter(
        config=config_manager.get_stage_config("model_converter")
    ))
    
    return orchestrator


async def run_pipeline_task(execution_id: str, input_data: Dict[str, Any]):
    """
    Background task to run pipeline.
    
    Args:
        execution_id: Execution ID
        input_data: Input data for pipeline
    """
    try:
        logger.log_pipeline_start(execution_id, input_data)
        
        # Create and execute pipeline
        pipeline = create_pipeline()
        result = await pipeline.execute_pipeline(input_data, execution_id)
        
        logger.log_pipeline_complete(
            execution_id,
            result.get("_metadata", {}).get("duration", 0),
            {"video": result.get("video_filename"), "model": result.get("model_filename")}
        )
        
    except Exception as e:
        logger.log_error("Pipeline execution failed", e, execution_id=execution_id)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Starting POS to 3D Pipeline API")
    config_manager.ensure_directories()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Shutting down POS to 3D Pipeline API")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "POS to 3D Pipeline",
        "version": "0.1.0",
        "description": "Convert marketing POS text descriptions to 3D models",
        "endpoints": {
            "process": "POST /api/v1/process",
            "status": "GET /api/v1/status/{execution_id}",
            "result": "GET /api/v1/result/{execution_id}",
            "download_video": "GET /api/v1/download/video/{filename}",
            "download_model": "GET /api/v1/download/model/{filename}",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pos-to-3d-pipeline",
        "version": "0.1.0"
    }


@app.post("/api/v1/process", response_model=PipelineResponse)
async def process_text(
    input_data: PipelineInput,
    background_tasks: BackgroundTasks
):
    """
    Process text description through the pipeline.
    
    Args:
        input_data: Text description and optional metadata
        background_tasks: FastAPI background tasks
        
    Returns:
        Pipeline response with execution ID and status URL
    """
    try:
        # Convert input to dict
        data = {
            "text": input_data.text,
            "metadata": input_data.metadata or {}
        }
        
        # Create execution
        import uuid
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        # Add background task
        background_tasks.add_task(run_pipeline_task, execution_id, data)
        
        logger.info(f"Pipeline execution queued: {execution_id}")
        
        return PipelineResponse(
            execution_id=execution_id,
            status="queued",
            message="Pipeline execution started",
            status_url=f"/api/v1/status/{execution_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to queue pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status/{execution_id}", response_model=StatusResponse)
async def get_status(execution_id: str):
    """
    Get pipeline execution status.
    
    Args:
        execution_id: Execution ID
        
    Returns:
        Current execution status
    """
    status = await status_tracker.get_status(execution_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return StatusResponse(
        execution_id=status["execution_id"],
        status=status["status"],
        progress=status["progress"],
        current_stage=status.get("current_stage"),
        created_at=status["created_at"],
        updated_at=status["updated_at"],
        stages=status["stages"],
        errors=status["errors"]
    )


@app.get("/api/v1/result/{execution_id}", response_model=ResultResponse)
async def get_result(execution_id: str):
    """
    Get pipeline execution result.
    
    Args:
        execution_id: Execution ID
        
    Returns:
        Pipeline result with output paths
    """
    status = await status_tracker.get_status(execution_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if status["status"] != PipelineStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline not completed. Current status: {status['status']}"
        )
    
    # Extract result from last stage
    stages = status["stages"]
    if not stages:
        raise HTTPException(status_code=500, detail="No stage results found")
    
    last_stage = stages[-1]
    result_summary = last_stage.get("result_summary", {})
    
    return ResultResponse(
        execution_id=execution_id,
        status=status["status"],
        video_path=result_summary.get("video_path"),
        model_path=result_summary.get("model_path"),
        metadata={
            "duration": result_summary.get("duration"),
            "vertices": result_summary.get("vertices"),
            "faces": result_summary.get("faces")
        }
    )


@app.get("/api/v1/download/video/{filename}")
async def download_video(filename: str):
    """
    Download generated video file.
    
    Args:
        filename: Video filename
        
    Returns:
        Video file
    """
    file_path = Path("pipeline/storage/output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )


@app.get("/api/v1/download/model/{filename}")
async def download_model(filename: str):
    """
    Download generated 3D model file.
    
    Args:
        filename: Model filename
        
    Returns:
        3D model file
    """
    file_path = Path("pipeline/storage/output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Model file not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )


@app.get("/api/v1/executions")
async def list_executions(limit: int = 100):
    """
    List recent pipeline executions.
    
    Args:
        limit: Maximum number of executions to return
        
    Returns:
        List of executions
    """
    executions = await status_tracker.list_executions(limit)
    return {"executions": executions, "total": len(executions)}


if __name__ == "__main__":
    # Get API configuration
    host = config_manager.get("api.host", "0.0.0.0")
    port = config_manager.get("api.port", 8000)
    workers = config_manager.get("api.workers", 1)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        workers=workers,
        reload=False
    )
