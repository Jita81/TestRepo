"""Orchestrator service for pipeline coordination."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import threading

import sys
sys.path.append(str(Path(__file__).parent.parent))

from common import (
    PipelineMessage,
    PipelineResult,
    PipelineStatus,
    PipelineStage,
    QueueClient,
    get_logger,
    PipelineError
)
from common.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class OrchestratorService:
    """
    Orchestrator service for monitoring and coordinating pipeline execution.
    
    This service:
    - Monitors pipeline progress
    - Stores pipeline state
    - Handles timeouts and retries
    - Provides status updates
    """
    
    def __init__(self):
        """Initialize orchestrator service."""
        self.settings = settings
        self.pipeline_states: Dict[str, PipelineResult] = {}
        self.state_lock = threading.Lock()
        logger.info("orchestrator_initialized")
    
    def update_pipeline_state(
        self,
        request_id: str,
        status: PipelineStatus,
        stage: PipelineStage,
        **kwargs
    ) -> None:
        """
        Update the state of a pipeline request.
        
        Args:
            request_id: Request identifier
            status: Current status
            stage: Current stage
            **kwargs: Additional state information
        """
        with self.state_lock:
            if request_id not in self.pipeline_states:
                self.pipeline_states[request_id] = PipelineResult(
                    request_id=request_id,
                    status=status,
                    created_at=datetime.utcnow()
                )
            
            state = self.pipeline_states[request_id]
            state.status = status
            
            # Update specific fields based on kwargs
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            
            logger.info(
                "pipeline_state_updated",
                request_id=request_id,
                status=status,
                stage=stage
            )
    
    def get_pipeline_state(self, request_id: str) -> Optional[PipelineResult]:
        """
        Get the state of a pipeline request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Pipeline result or None if not found
        """
        with self.state_lock:
            return self.pipeline_states.get(request_id)
    
    def process_completion_message(self, ch, method, properties, body):
        """
        Process completion messages from the pipeline.
        
        Args:
            ch: Channel
            method: Method
            properties: Properties
            body: Message body
        """
        try:
            # Parse message
            message_data = json.loads(body)
            message = PipelineMessage(**message_data)
            
            logger.info(
                "completion_message_received",
                request_id=message.request_id,
                stage=message.stage,
                status=message.status
            )
            
            # Calculate processing time
            start_time = self.pipeline_states.get(message.request_id)
            processing_time = None
            if start_time:
                processing_time = (
                    datetime.utcnow() - start_time.created_at
                ).total_seconds()
            
            # Update pipeline state
            self.update_pipeline_state(
                request_id=message.request_id,
                status=message.status,
                stage=message.stage,
                video_metadata=message.payload.get("video_metadata"),
                model_metadata=message.payload.get("model_metadata"),
                processing_time_seconds=processing_time,
                completed_at=datetime.utcnow()
            )
            
            # Log completion
            logger.info(
                "pipeline_completed",
                request_id=message.request_id,
                processing_time=f"{processing_time:.2f}s" if processing_time else "unknown"
            )
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error("completion_processing_failed", error=str(e))
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_monitoring(self):
        """Start monitoring completed pipelines."""
        logger.info("starting_orchestrator_monitoring")
        
        # Connect to queue
        queue_client = QueueClient(
            host=settings.queue_host,
            port=settings.queue_port,
            username=settings.queue_username,
            password=settings.queue_password
        )
        
        queue_client.connect()
        queue_client.declare_queue("pipeline_completed")
        
        logger.info("consuming_completion_messages")
        queue_client.consume(
            queue_name="pipeline_completed",
            callback=self.process_completion_message,
            auto_ack=False
        )
    
    def cleanup_old_states(self, max_age_seconds: int = 86400):
        """
        Clean up old pipeline states.
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 24 hours)
        """
        logger.info("cleaning_up_old_states", max_age_seconds=max_age_seconds)
        
        with self.state_lock:
            current_time = datetime.utcnow()
            to_remove = []
            
            for request_id, state in self.pipeline_states.items():
                age = (current_time - state.created_at).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(request_id)
            
            for request_id in to_remove:
                del self.pipeline_states[request_id]
                logger.info("state_removed", request_id=request_id)
            
            logger.info("cleanup_completed", removed=len(to_remove))
    
    def start_cleanup_task(self):
        """Start periodic cleanup task."""
        def cleanup_loop():
            while True:
                time.sleep(settings.cleanup_interval_seconds)
                try:
                    self.cleanup_old_states()
                except Exception as e:
                    logger.error("cleanup_task_failed", error=str(e))
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("cleanup_task_started")
    
    def start(self):
        """Start the orchestrator service."""
        logger.info("starting_orchestrator_service")
        
        # Start cleanup task
        self.start_cleanup_task()
        
        # Start monitoring
        self.start_monitoring()


def main():
    """Main entry point for orchestrator service."""
    from common.logging_config import configure_logging
    from common.config import ensure_directories
    
    configure_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        json_logs=settings.json_logs
    )
    ensure_directories(settings)
    
    service = OrchestratorService()
    service.start()


if __name__ == "__main__":
    main()