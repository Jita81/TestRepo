"""FastAPI application for pipeline API."""

import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common import (
    TextInput,
    GenerateResponse,
    PipelineMessage,
    PipelineStatus,
    PipelineStage,
    QueueClient,
    configure_logging,
    get_logger,
    PipelineError,
    ValidationError as CustomValidationError
)
from common.config import get_settings, ensure_directories

# Initialize settings and logger
settings = get_settings()
configure_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    json_logs=settings.json_logs
)
logger = get_logger(__name__)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> Optional[str]:
    """Verify API key if authentication is enabled."""
    if settings.api_key:
        if api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing API key"
            )
    return api_key


# Queue client instance
queue_client: Optional[QueueClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global queue_client
    
    # Startup
    logger.info("api_service_starting")
    ensure_directories(settings)
    
    try:
        queue_client = QueueClient(
            host=settings.queue_host,
            port=settings.queue_port,
            username=settings.queue_username,
            password=settings.queue_password,
            retry_attempts=settings.queue_retry_count
        )
        queue_client.connect()
        queue_client.declare_queue("pipeline_input")
        logger.info("queue_client_initialized")
    except Exception as e:
        logger.error("queue_client_initialization_failed", error=str(e))
        # Continue without queue for now (will fail on actual requests)
    
    yield
    
    # Shutdown
    logger.info("api_service_shutting_down")
    if queue_client:
        queue_client.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="POS Display Pipeline API",
        description="API for generating 3D models from POS display descriptions",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    @app.exception_handler(PydanticValidationError)
    async def validation_exception_handler(request, exc):
        logger.warning("validation_error", errors=exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
    @app.exception_handler(CustomValidationError)
    async def custom_validation_exception_handler(request, exc):
        logger.warning("custom_validation_error", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "stage": exc.stage}
        )
    
    @app.exception_handler(PipelineError)
    async def pipeline_exception_handler(request, exc):
        logger.error("pipeline_error", stage=exc.stage, error=exc.message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": exc.message, "stage": exc.stage}
        )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Check API health and component status.
        
        Returns status of all pipeline components.
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "api": "healthy",
                "queue": "healthy" if queue_client and queue_client.connection else "unhealthy"
            }
        }
        
        overall_healthy = all(
            v == "healthy" for v in health_status["components"].values()
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    # Main generation endpoint
    @app.post(
        "/generate",
        response_model=GenerateResponse,
        tags=["Pipeline"],
        status_code=status.HTTP_202_ACCEPTED
    )
    async def generate_pos_display(
        input_data: TextInput,
        api_key: str = Security(verify_api_key)
    ):
        """
        Generate a 3D model from POS display description.
        
        This endpoint initiates the pipeline process:
        1. Accepts text description
        2. Queues for video generation
        3. Returns request ID for tracking
        
        Args:
            input_data: Text description and metadata
            
        Returns:
            GenerateResponse with request ID and status
            
        Raises:
            HTTPException: If validation fails or queue is unavailable
        """
        try:
            # Generate unique request ID
            request_id = f"req_{uuid.uuid4().hex[:12]}"
            
            logger.info(
                "generation_request_received",
                request_id=request_id,
                description_length=len(input_data.description)
            )
            
            # Create pipeline message
            message = PipelineMessage(
                request_id=request_id,
                stage=PipelineStage.INPUT,
                payload={
                    "description": input_data.description,
                    "metadata": input_data.metadata
                },
                status=PipelineStatus.PENDING
            )
            
            # Publish to queue
            if not queue_client:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Queue service is not available"
                )
            
            queue_client.publish(
                queue_name="pipeline_input",
                message=message.model_dump()
            )
            
            logger.info(
                "generation_request_queued",
                request_id=request_id
            )
            
            return GenerateResponse(
                request_id=request_id,
                status=PipelineStatus.PENDING,
                message="Pipeline initiated successfully",
                created_at=datetime.utcnow()
            )
            
        except PydanticValidationError as e:
            logger.error("input_validation_failed", errors=e.errors())
            raise
        except Exception as e:
            logger.error("generation_request_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initiate pipeline: {str(e)}"
            )
    
    # Status check endpoint
    @app.get(
        "/status/{request_id}",
        tags=["Pipeline"]
    )
    async def check_status(request_id: str):
        """
        Check the status of a pipeline request.
        
        Args:
            request_id: The request ID to check
            
        Returns:
            Status information for the request
        """
        # This would typically query a database or cache
        # For prototype, we return a basic response
        logger.info("status_check", request_id=request_id)
        
        return {
            "request_id": request_id,
            "status": "processing",
            "message": "Status tracking will be implemented with state storage"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )