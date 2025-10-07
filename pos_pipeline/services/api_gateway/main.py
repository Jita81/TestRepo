"""
API Gateway for the POS Pipeline system.

This provides REST API endpoints for pipeline operations.
"""
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional
from utils.logging_config import setup_logging, get_logger
from utils.exceptions import PipelineException
from models.schemas import PipelineInput, PipelineOutput, ProcessingStatus
from services.orchestrator import PipelineOrchestrator
from config.settings import settings


# Initialize logging
setup_logging()
logger = get_logger("api_gateway")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = PipelineOrchestrator()

# Mount storage directories for file serving
storage_path = Path(settings.storage_path)
storage_path.mkdir(parents=True, exist_ok=True)

try:
    app.mount(
        "/storage",
        StaticFiles(directory=str(storage_path)),
        name="storage"
    )
except Exception as e:
    logger.warning(f"Could not mount storage directory: {e}")


# Security dependency
async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Verify API key for authentication.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != settings.api_key:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version
    }


@app.post(
    "/pipeline/process",
    response_model=dict,
    tags=["Pipeline"],
    status_code=status.HTTP_202_ACCEPTED
)
async def process_pipeline(
    input_data: PipelineInput,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit a POS display request for processing through the pipeline.
    
    This endpoint accepts text descriptions and returns a job ID for tracking.
    The actual processing happens asynchronously.
    
    Args:
        input_data: Text description and metadata
        api_key: Authentication key (via X-API-Key header)
        
    Returns:
        Job ID for tracking progress
        
    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        logger.info(f"Received pipeline request: {input_data.text[:50]}...")
        
        # Submit job for processing
        job_id = await orchestrator.process(input_data)
        
        return {
            "job_id": job_id,
            "message": "Job submitted successfully",
            "status_url": f"/pipeline/status/{job_id}",
            "result_url": f"/pipeline/result/{job_id}"
        }
        
    except PipelineException as e:
        logger.error(f"Pipeline submission failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.message,
                "stage": e.stage.value,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during pipeline submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get(
    "/pipeline/status/{job_id}",
    response_model=ProcessingStatus,
    tags=["Pipeline"]
)
async def get_pipeline_status(
    job_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get the current status of a pipeline job.
    
    Args:
        job_id: Unique job identifier
        api_key: Authentication key (via X-API-Key header)
        
    Returns:
        Current processing status
        
    Raises:
        HTTPException: If job not found
    """
    status_info = orchestrator.get_status(job_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return status_info


@app.get(
    "/pipeline/result/{job_id}",
    response_model=PipelineOutput,
    tags=["Pipeline"]
)
async def get_pipeline_result(
    job_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get the result of a completed pipeline job.
    
    Args:
        job_id: Unique job identifier
        api_key: Authentication key (via X-API-Key header)
        
    Returns:
        Pipeline output with URLs to generated assets
        
    Raises:
        HTTPException: If job not found or not completed
    """
    result = orchestrator.get_result(job_id)
    
    if not result:
        # Check if job exists but is not complete
        status_info = orchestrator.get_status(job_id)
        if status_info:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail={
                    "message": "Job is still processing",
                    "stage": status_info.stage.value,
                    "progress": status_info.progress
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
    
    return result


@app.exception_handler(PipelineException)
async def pipeline_exception_handler(request, exc: PipelineException):
    """
    Handle pipeline-specific exceptions.
    
    Args:
        request: Request object
        exc: Pipeline exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Pipeline error: {exc.message}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.message,
            "stage": exc.stage.value,
            "details": exc.details,
            "recoverable": exc.recoverable
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )