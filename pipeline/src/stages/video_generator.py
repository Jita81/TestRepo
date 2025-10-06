"""
Video generation stage for creating videos from text descriptions.
"""

import os
import asyncio
from typing import Dict, Any, List, Tuple
from pathlib import Path
import numpy as np
import cv2
from datetime import datetime

from ..core.base import PipelineStage, ValidationError, ProcessingError


class VideoGenerator(PipelineStage):
    """
    Generates video from processed text descriptions.
    
    Creates a video representation of the marketing POS display using
    open-source generative models and rendering techniques.
    """
    
    def _setup(self):
        """Initialize video generator."""
        self.min_duration = self.get_config("min_duration", 30)
        self.default_duration = self.get_config("default_duration", 30)
        self.fps = self.get_config("fps", 24)
        self.resolution = tuple(self.get_config("resolution", [1920, 1080]))
        self.output_format = self.get_config("format", "mp4")
        
        # Video codec
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    async def validate(self, data: Dict[str, Any], is_input: bool = True) -> bool:
        """
        Validate input or output data.
        
        Args:
            data: Data to validate
            is_input: True for input validation, False for output
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        if is_input:
            # Validate input has processed text
            if "processed_text" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Missing required field: 'processed_text'"
                )
            
            if "visual_elements" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Missing required field: 'visual_elements'"
                )
        else:
            # Validate output has video path
            if "video_path" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Output missing 'video_path' field"
                )
            
            # Validate video file exists
            video_path = Path(data["video_path"])
            if not video_path.exists():
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Video file not found: {video_path}"
                )
            
            # Validate duration
            if "duration" not in data or data["duration"] < self.min_duration:
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Video duration must be at least {self.min_duration} seconds"
                )
        
        return True
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from text description.
        
        Args:
            input_data: Dictionary containing processed text and visual elements
            
        Returns:
            Dictionary with video path and metadata
            
        Raises:
            ProcessingError: If video generation fails
        """
        try:
            processed_text = input_data["processed_text"]
            visual_elements = input_data.get("visual_elements", {})
            keywords = input_data.get("keywords", [])
            
            # Generate output filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            video_filename = f"pos_video_{timestamp}.{self.output_format}"
            video_path = Path("pipeline/storage/output") / video_filename
            video_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate video frames
            frames = await self._generate_frames(
                processed_text,
                visual_elements,
                keywords
            )
            
            # Compose video from frames
            await self._compose_video(frames, video_path)
            
            # Calculate video metadata
            duration = len(frames) / self.fps
            
            return {
                **input_data,  # Pass through previous stage data
                "video_path": str(video_path),
                "video_filename": video_filename,
                "duration": duration,
                "frame_count": len(frames),
                "fps": self.fps,
                "resolution": self.resolution,
                "format": self.output_format
            }
            
        except Exception as e:
            raise ProcessingError(
                stage=self.stage_name,
                message=f"Video generation failed: {str(e)}",
                details={"exception_type": type(e).__name__}
            )
    
    async def _generate_frames(
        self,
        text: str,
        visual_elements: Dict[str, Any],
        keywords: List[str]
    ) -> List[np.ndarray]:
        """
        Generate video frames.
        
        For the prototype, we create simple rendered frames.
        In production, this would use text-to-video models.
        
        Args:
            text: Processed text description
            visual_elements: Extracted visual elements
            keywords: Keywords from text
            
        Returns:
            List of video frames as numpy arrays
        """
        # Calculate total frames needed
        total_frames = int(self.default_duration * self.fps)
        
        frames = []
        
        # Generate frames with visual progression
        for frame_idx in range(total_frames):
            frame = await self._generate_frame(
                frame_idx,
                total_frames,
                text,
                visual_elements,
                keywords
            )
            frames.append(frame)
        
        return frames
    
    async def _generate_frame(
        self,
        frame_idx: int,
        total_frames: int,
        text: str,
        visual_elements: Dict[str, Any],
        keywords: List[str]
    ) -> np.ndarray:
        """
        Generate a single video frame.
        
        For prototype: Creates animated text and shapes based on description.
        Production: Would use ML models like ModelScope, CogVideo, etc.
        """
        # Create blank frame
        frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Progress through video (0.0 to 1.0)
        progress = frame_idx / max(total_frames - 1, 1)
        
        # Extract colors or use defaults
        colors = visual_elements.get("colors", [])
        bg_color = self._get_color_value(colors[0] if colors else "blue")
        text_color = (255, 255, 255)  # White text
        
        # Gradient background
        for y in range(self.resolution[1]):
            intensity = int(bg_color[0] * (1 - y / self.resolution[1]))
            frame[y, :] = (intensity, intensity // 2, bg_color[2])
        
        # Add title text
        title = "Marketing POS Display"
        cv2.putText(
            frame,
            title,
            (50, 100),
            cv2.FONT_HERSHEY_DUPLEX,
            2.0,
            text_color,
            3,
            cv2.LINE_AA
        )
        
        # Add description (word-wrapped)
        description_lines = self._wrap_text(text, 60)
        y_offset = 200
        for line in description_lines[:5]:  # Limit to 5 lines
            cv2.putText(
                frame,
                line,
                (50, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                text_color,
                2,
                cv2.LINE_AA
            )
            y_offset += 50
        
        # Add keywords animation
        if keywords:
            keyword_y = 600
            for i, keyword in enumerate(keywords[:10]):  # Show up to 10 keywords
                # Animate keywords appearing
                keyword_progress = max(0, min(1, (progress - i * 0.05) * 2))
                if keyword_progress > 0:
                    alpha = int(255 * keyword_progress)
                    keyword_color = (alpha, alpha, alpha)
                    x_pos = 50 + (i % 5) * 350
                    y_pos = keyword_y + (i // 5) * 60
                    cv2.putText(
                        frame,
                        f"• {keyword}",
                        (x_pos, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        keyword_color,
                        2,
                        cv2.LINE_AA
                    )
        
        # Add rotating 3D-like shapes for visual interest
        center_x = self.resolution[0] - 300
        center_y = self.resolution[1] - 300
        radius = 100 + int(50 * np.sin(progress * np.pi * 4))
        
        # Draw animated circle/shape
        cv2.circle(
            frame,
            (center_x, center_y),
            radius,
            (100, 200, 255),
            3
        )
        
        # Add rotation effect
        angle = progress * 360
        point_x = int(center_x + radius * np.cos(np.radians(angle)))
        point_y = int(center_y + radius * np.sin(np.radians(angle)))
        cv2.circle(frame, (point_x, point_y), 10, (255, 100, 100), -1)
        
        return frame
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _get_color_value(self, color_name: str) -> Tuple[int, int, int]:
        """Convert color name to BGR value."""
        color_map = {
            "red": (0, 0, 255),
            "blue": (255, 0, 0),
            "green": (0, 255, 0),
            "yellow": (0, 255, 255),
            "orange": (0, 165, 255),
            "purple": (255, 0, 255),
            "pink": (203, 192, 255),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
            "brown": (42, 42, 165),
            "gold": (0, 215, 255),
            "silver": (192, 192, 192)
        }
        return color_map.get(color_name.lower(), (255, 0, 0))  # Default to blue
    
    async def _compose_video(self, frames: List[np.ndarray], output_path: Path):
        """
        Compose video from frames.
        
        Args:
            frames: List of video frames
            output_path: Output video file path
        """
        # Create video writer
        video_writer = cv2.VideoWriter(
            str(output_path),
            self.fourcc,
            self.fps,
            self.resolution
        )
        
        try:
            # Write frames
            for frame in frames:
                video_writer.write(frame)
        finally:
            video_writer.release()
