"""
Video Generation Service for the POS Pipeline.

This service generates video from processed text using AI models.
"""
import asyncio
import time
import uuid
from pathlib import Path
from typing import Optional
import numpy as np
import cv2
from moviepy.editor import VideoClip, AudioClip
from utils.logging_config import get_logger
from utils.exceptions import VideoGenerationError, StorageError
from models.schemas import VideoGenerationResult
from config.settings import settings


logger = get_logger("video_generator")


class VideoGenerator:
    """Handles video generation from text descriptions."""
    
    def __init__(self):
        self.output_format = settings.video_format
        self.min_duration = settings.min_video_duration
        self.fps = settings.video_fps
        self.resolution = settings.video_resolution
        self.storage_path = Path(settings.storage_path) / "videos"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        
    def _create_placeholder_video(
        self,
        text: str,
        duration: int,
        output_path: Path
    ) -> None:
        """
        Create a placeholder video for prototype.
        In production, this would integrate with actual text-to-video models.
        
        Args:
            text: Text description for video
            duration: Video duration in seconds
            output_path: Path to save video
        """
        width, height = self.resolution
        
        # Create a simple animated video as placeholder
        def make_frame(t):
            """Generate frame at time t."""
            # Create gradient background that changes over time
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Animated gradient
            color_shift = int((t / duration) * 255)
            frame[:, :, 0] = (color_shift + np.linspace(0, 255, width)).astype(np.uint8)
            frame[:, :, 1] = (255 - color_shift + np.linspace(0, 255, height)[:, None]).astype(np.uint8)
            frame[:, :, 2] = 128
            
            # Add text overlay
            text_display = text[:50] + "..." if len(text) > 50 else text
            cv2.putText(
                frame,
                text_display,
                (20, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # Add timestamp
            cv2.putText(
                frame,
                f"t={t:.1f}s",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
            return frame
        
        # Create video clip
        clip = VideoClip(make_frame, duration=duration)
        
        # Write video file
        clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )
        
        clip.close()
    
    def _validate_storage(self, file_size_mb: float) -> None:
        """
        Validate storage constraints.
        
        Args:
            file_size_mb: Size of file to store
            
        Raises:
            StorageError: If storage limits exceeded
        """
        if file_size_mb > settings.max_video_size_mb:
            raise StorageError(
                f"Video size {file_size_mb:.2f}MB exceeds limit of {settings.max_video_size_mb}MB",
                stage="video_generation",
                details={"size_mb": file_size_mb, "limit_mb": settings.max_video_size_mb}
            )
    
    async def generate_video(
        self,
        job_id: str,
        processed_text: str,
        duration: Optional[int] = None
    ) -> VideoGenerationResult:
        """
        Generate video from processed text.
        
        Args:
            job_id: Unique job identifier
            processed_text: Processed text description
            duration: Video duration in seconds (defaults to min_duration)
            
        Returns:
            VideoGenerationResult with video path and metadata
            
        Raises:
            VideoGenerationError: If video generation fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting video generation for job {job_id}")
            
            # Set duration
            video_duration = duration or self.min_duration
            
            if video_duration < self.min_duration:
                raise VideoGenerationError(
                    f"Video duration must be at least {self.min_duration} seconds",
                    details={"requested_duration": video_duration}
                )
            
            # Generate unique filename
            video_filename = f"{job_id}.{self.output_format}"
            video_path = self.storage_path / video_filename
            
            self.logger.info(f"Generating {video_duration}s video at {self.resolution}")
            
            # Generate video (placeholder for prototype)
            # In production, integrate with actual text-to-video model
            # e.g., ModelScope, Stable Video Diffusion, etc.
            await asyncio.to_thread(
                self._create_placeholder_video,
                processed_text,
                video_duration,
                video_path
            )
            
            # Validate video was created
            if not video_path.exists():
                raise VideoGenerationError(
                    "Video file was not created",
                    details={"expected_path": str(video_path)}
                )
            
            # Get file size
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            
            # Validate storage
            self._validate_storage(file_size_mb)
            
            processing_time = time.time() - start_time
            
            result = VideoGenerationResult(
                job_id=job_id,
                video_path=str(video_path),
                video_url=f"/storage/videos/{video_filename}",
                duration=video_duration,
                format=self.output_format,
                resolution=self.resolution,
                fps=self.fps,
                file_size_mb=file_size_mb,
                processing_time=processing_time
            )
            
            self.logger.info(
                f"Video generation completed for job {job_id} in {processing_time:.2f}s "
                f"(size: {file_size_mb:.2f}MB)"
            )
            
            return result
            
        except (VideoGenerationError, StorageError):
            raise
        except Exception as e:
            self.logger.error(f"Video generation failed for job {job_id}: {str(e)}")
            raise VideoGenerationError(
                f"Failed to generate video: {str(e)}",
                details={"job_id": job_id, "error": str(e)}
            )