"""
Prometheus Metrics Collection.

Provides comprehensive metrics for monitoring pipeline performance,
reliability, and resource usage.
"""

import time
import logging
from typing import Optional
from functools import wraps

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        Info,
        generate_latest,
        CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = Summary = Info = None

logger = logging.getLogger(__name__)


class PipelineMetrics:
    """
    Prometheus metrics for pipeline monitoring.
    
    Tracks:
    - Request counts and rates
    - Processing times
    - Error rates
    - Queue sizes
    - Resource usage
    - Pipeline stages
    """
    
    def __init__(self):
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning(
                "prometheus_client not available - metrics disabled. "
                "Install with: pip install prometheus-client"
            )
            self.enabled = False
            return
        
        self.enabled = True
        
        # Request metrics
        self.requests_total = Counter(
            'pipeline_requests_total',
            'Total number of pipeline requests',
            ['endpoint', 'method', 'status']
        )
        
        self.requests_in_progress = Gauge(
            'pipeline_requests_in_progress',
            'Number of requests currently being processed'
        )
        
        # Processing time metrics
        self.processing_duration = Histogram(
            'pipeline_processing_duration_seconds',
            'Time spent processing pipeline requests',
            ['stage'],
            buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800)
        )
        
        self.stage_duration = Histogram(
            'pipeline_stage_duration_seconds',
            'Time spent in each pipeline stage',
            ['stage_name'],
            buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120)
        )
        
        # Error metrics
        self.errors_total = Counter(
            'pipeline_errors_total',
            'Total number of pipeline errors',
            ['stage', 'error_type']
        )
        
        # Pipeline stage metrics
        self.stages_completed = Counter(
            'pipeline_stages_completed_total',
            'Number of pipeline stages completed',
            ['stage_name', 'status']
        )
        
        # Output metrics
        self.videos_generated = Counter(
            'pipeline_videos_generated_total',
            'Total number of videos generated'
        )
        
        self.models_generated = Counter(
            'pipeline_models_generated_total',
            'Total number of 3D models generated'
        )
        
        self.output_size_bytes = Summary(
            'pipeline_output_size_bytes',
            'Size of generated output files',
            ['output_type']
        )
        
        # Queue metrics
        self.queue_size = Gauge(
            'pipeline_queue_size',
            'Current size of processing queues',
            ['queue_name']
        )
        
        # Resource metrics
        self.memory_usage_bytes = Gauge(
            'pipeline_memory_usage_bytes',
            'Current memory usage in bytes'
        )
        
        self.cpu_usage_percent = Gauge(
            'pipeline_cpu_usage_percent',
            'Current CPU usage percentage'
        )
        
        # System info
        self.system_info = Info(
            'pipeline_system',
            'Pipeline system information'
        )
        
        logger.info("Prometheus metrics initialized")
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        status: str
    ):
        """
        Record an API request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status: Response status (success/error)
        """
        if not self.enabled:
            return
        
        self.requests_total.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
    
    def record_processing_time(
        self,
        stage: str,
        duration: float
    ):
        """
        Record processing time for a stage.
        
        Args:
            stage: Pipeline stage name
            duration: Processing time in seconds
        """
        if not self.enabled:
            return
        
        self.processing_duration.labels(stage=stage).observe(duration)
        self.stage_duration.labels(stage_name=stage).observe(duration)
    
    def record_error(
        self,
        stage: str,
        error_type: str
    ):
        """
        Record an error.
        
        Args:
            stage: Pipeline stage where error occurred
            error_type: Type of error
        """
        if not self.enabled:
            return
        
        self.errors_total.labels(
            stage=stage,
            error_type=error_type
        ).inc()
    
    def record_stage_completion(
        self,
        stage_name: str,
        status: str
    ):
        """
        Record pipeline stage completion.
        
        Args:
            stage_name: Name of the stage
            status: Completion status (success/failure)
        """
        if not self.enabled:
            return
        
        self.stages_completed.labels(
            stage_name=stage_name,
            status=status
        ).inc()
    
    def record_video_generated(self):
        """Record that a video was generated."""
        if not self.enabled:
            return
        
        self.videos_generated.inc()
    
    def record_model_generated(self):
        """Record that a 3D model was generated."""
        if not self.enabled:
            return
        
        self.models_generated.inc()
    
    def record_output_size(
        self,
        output_type: str,
        size_bytes: int
    ):
        """
        Record output file size.
        
        Args:
            output_type: Type of output (video/model)
            size_bytes: File size in bytes
        """
        if not self.enabled:
            return
        
        self.output_size_bytes.labels(
            output_type=output_type
        ).observe(size_bytes)
    
    def set_queue_size(
        self,
        queue_name: str,
        size: int
    ):
        """
        Set current queue size.
        
        Args:
            queue_name: Name of the queue
            size: Current size
        """
        if not self.enabled:
            return
        
        self.queue_size.labels(queue_name=queue_name).set(size)
    
    def set_memory_usage(self, bytes_used: int):
        """
        Set current memory usage.
        
        Args:
            bytes_used: Memory usage in bytes
        """
        if not self.enabled:
            return
        
        self.memory_usage_bytes.set(bytes_used)
    
    def set_cpu_usage(self, percent: float):
        """
        Set current CPU usage.
        
        Args:
            percent: CPU usage percentage (0-100)
        """
        if not self.enabled:
            return
        
        self.cpu_usage_percent.set(percent)
    
    def set_system_info(self, info: dict):
        """
        Set system information.
        
        Args:
            info: Dictionary of system information
        """
        if not self.enabled:
            return
        
        self.system_info.info(info)
    
    def track_request(self):
        """
        Decorator to track request metrics.
        
        Usage:
            @metrics.track_request()
            async def process_request():
                ...
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                self.requests_in_progress.inc()
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.record_processing_time("request", duration)
                    return result
                finally:
                    self.requests_in_progress.dec()
            
            return wrapper
        return decorator
    
    def track_stage(self, stage_name: str):
        """
        Decorator to track stage execution metrics.
        
        Usage:
            @metrics.track_stage("text_processing")
            async def process_text():
                ...
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.record_processing_time(stage_name, duration)
                    self.record_stage_completion(stage_name, "success")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.record_processing_time(stage_name, duration)
                    self.record_error(stage_name, type(e).__name__)
                    self.record_stage_completion(stage_name, "failure")
                    raise
            
            return wrapper
        return decorator


# Global metrics instance
metrics = PipelineMetrics()


def get_metrics_text() -> str:
    """
    Get metrics in Prometheus text format.
    
    Returns:
        Metrics text for Prometheus scraping
    """
    if not PROMETHEUS_AVAILABLE:
        return "# Metrics unavailable\n"
    
    return generate_latest().decode('utf-8')


def get_metrics_content_type() -> str:
    """
    Get metrics content type.
    
    Returns:
        Content type for Prometheus metrics
    """
    if not PROMETHEUS_AVAILABLE:
        return "text/plain"
    
    return CONTENT_TYPE_LATEST
