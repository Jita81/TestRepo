"""Video generation service implementation."""

import os
import json
import time
from pathlib import Path
from typing import Optional
import numpy as np
import cv2

import sys
sys.path.append(str(Path(__file__).parent.parent))

from common import (
    PipelineMessage,
    PipelineStatus,
    PipelineStage,
    VideoMetadata,
    QueueClient,
    get_logger,
    VideoGenerationError
)
from common.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class VideoGeneratorService:
    """Service for generating videos from text descriptions."""
    
    def __init__(self):
        """Initialize video generator service."""
        self.settings = settings
        self.output_dir = Path(settings.video_storage_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("video_generator_initialized", output_dir=str(self.output_dir))
    
    def generate_video(self, description: str, request_id: str) -> VideoMetadata:
        """
        Generate video from text description.
        
        For the prototype, this creates a simple animated video.
        In production, this would integrate with an actual text-to-video model.
        
        Args:
            description: Text description of the POS display
            request_id: Unique request identifier
            
        Returns:
            VideoMetadata with video information
            
        Raises:
            VideoGenerationError: If video generation fails
        """
        try:
            logger.info(
                "video_generation_started",
                request_id=request_id,
                description=description[:50]
            )
            
            # Video parameters
            frame_rate = settings.video_frame_rate
            duration = settings.video_duration
            width = settings.video_width
            height = settings.video_height
            total_frames = frame_rate * duration
            
            # Output path
            video_filename = f"{request_id}.mp4"
            video_path = self.output_dir / video_filename
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(video_path),
                fourcc,
                frame_rate,
                (width, height)
            )
            
            if not out.isOpened():
                raise VideoGenerationError(
                    "Failed to initialize video writer",
                    details={"path": str(video_path)}
                )
            
            # Generate frames
            # For prototype: create animated gradient frames
            # In production: use actual text-to-video model
            logger.info("generating_frames", total_frames=total_frames)
            
            for frame_idx in range(total_frames):
                frame = self._generate_frame(
                    frame_idx,
                    total_frames,
                    width,
                    height,
                    description
                )
                out.write(frame)
                
                if frame_idx % 30 == 0:
                    logger.debug(
                        "frame_generated",
                        frame=frame_idx,
                        total=total_frames,
                        progress=f"{(frame_idx/total_frames)*100:.1f}%"
                    )
            
            out.release()
            
            # Get video file size
            file_size = video_path.stat().st_size
            
            logger.info(
                "video_generation_completed",
                request_id=request_id,
                path=str(video_path),
                size_mb=f"{file_size / (1024*1024):.2f}"
            )
            
            # Create metadata
            metadata = VideoMetadata(
                video_path=str(video_path),
                duration=float(duration),
                frame_rate=frame_rate,
                resolution=(width, height),
                size_bytes=file_size
            )
            
            return metadata
            
        except Exception as e:
            logger.error(
                "video_generation_failed",
                request_id=request_id,
                error=str(e)
            )
            raise VideoGenerationError(
                f"Video generation failed: {str(e)}",
                details={"request_id": request_id}
            )
    
    def _generate_frame(
        self,
        frame_idx: int,
        total_frames: int,
        width: int,
        height: int,
        description: str
    ) -> np.ndarray:
        """
        Generate a single video frame.
        
        This is a placeholder implementation for the prototype.
        In production, this would use an actual text-to-video model.
        
        Args:
            frame_idx: Current frame index
            total_frames: Total number of frames
            width: Frame width
            height: Frame height
            description: Text description
            
        Returns:
            Frame as numpy array (BGR format)
        """
        # Create animated gradient background
        progress = frame_idx / total_frames
        
        # Generate color based on progress
        hue = int(180 * progress)  # Cycle through HSV hue
        
        # Create HSV image
        hsv_frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create gradient
        for y in range(height):
            for x in range(width):
                h = (hue + int(90 * x / width)) % 180
                s = 255
                v = int(128 + 127 * np.sin(2 * np.pi * (y / height + progress)))
                hsv_frame[y, x] = [h, s, v]
        
        # Convert to BGR
        frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)
        
        # Add text overlay
        text = f"Frame {frame_idx}/{total_frames}"
        cv2.putText(
            frame,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Add description (truncated)
        desc_text = description[:40] + "..." if len(description) > 40 else description
        cv2.putText(
            frame,
            desc_text,
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        return frame
    
    def process_message(self, ch, method, properties, body):
        """
        Process a message from the queue.
        
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
                "processing_message",
                request_id=message.request_id,
                stage=message.stage
            )
            
            # Generate video
            description = message.payload.get("description", "")
            video_metadata = self.generate_video(description, message.request_id)
            
            # Update message for next stage
            message.stage = PipelineStage.VIDEO_GENERATION
            message.status = PipelineStatus.COMPLETED
            message.payload["video_metadata"] = video_metadata.model_dump()
            
            # Publish to next stage queue
            queue_client = QueueClient(
                host=settings.queue_host,
                port=settings.queue_port,
                username=settings.queue_username,
                password=settings.queue_password
            )
            queue_client.connect()
            queue_client.declare_queue("model_conversion_input")
            queue_client.publish(
                queue_name="model_conversion_input",
                message=message.model_dump()
            )
            queue_client.close()
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            logger.info(
                "message_processed",
                request_id=message.request_id
            )
            
        except Exception as e:
            logger.error("message_processing_failed", error=str(e))
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """Start the video generator service."""
        logger.info("starting_video_generator_service")
        
        # Connect to queue
        queue_client = QueueClient(
            host=settings.queue_host,
            port=settings.queue_port,
            username=settings.queue_username,
            password=settings.queue_password
        )
        
        queue_client.connect()
        queue_client.declare_queue("pipeline_input")
        
        logger.info("consuming_messages")
        queue_client.consume(
            queue_name="pipeline_input",
            callback=self.process_message,
            auto_ack=False
        )


def main():
    """Main entry point for video generator service."""
    from common.logging_config import configure_logging
    from common.config import ensure_directories
    
    configure_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        json_logs=settings.json_logs
    )
    ensure_directories(settings)
    
    service = VideoGeneratorService()
    service.start()


if __name__ == "__main__":
    main()