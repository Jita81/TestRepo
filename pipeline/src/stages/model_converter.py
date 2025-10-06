"""
3D model conversion stage for converting videos to 3D models.
"""

import asyncio
from typing import Dict, Any, List, Tuple
from pathlib import Path
import numpy as np
import cv2
from datetime import datetime
import struct

from ..core.base import PipelineStage, ValidationError, ProcessingError


class ModelConverter(PipelineStage):
    """
    Converts video to 3D model in STL format.
    
    For prototype: Uses depth estimation from video frames to create basic 3D mesh.
    Production: Would use advanced video-to-3D models like NeRF, 3D Gaussian Splatting, etc.
    """
    
    def _setup(self):
        """Initialize model converter."""
        self.output_format = self.get_config("output_format", "STL")
        self.quality = self.get_config("quality", "medium")
        self.max_vertices = self.get_config("max_vertices", 1000000)
        
        # Quality settings
        self.quality_settings = {
            "low": {"sample_rate": 10, "depth_levels": 5},
            "medium": {"sample_rate": 5, "depth_levels": 10},
            "high": {"sample_rate": 2, "depth_levels": 20}
        }
        self.settings = self.quality_settings.get(self.quality, self.quality_settings["medium"])
    
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
            # Validate input has video path
            if "video_path" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Missing required field: 'video_path'"
                )
            
            # Validate video file exists
            video_path = Path(data["video_path"])
            if not video_path.exists():
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Video file not found: {video_path}"
                )
        else:
            # Validate output has model path
            if "model_path" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Output missing 'model_path' field"
                )
            
            # Validate model file exists
            model_path = Path(data["model_path"])
            if not model_path.exists():
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Model file not found: {model_path}"
                )
            
            # Validate format
            if "format" not in data or data["format"] != self.output_format:
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Invalid model format, expected {self.output_format}"
                )
        
        return True
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert video to 3D model.
        
        Args:
            input_data: Dictionary containing video path and metadata
            
        Returns:
            Dictionary with model path and metadata
            
        Raises:
            ProcessingError: If conversion fails
        """
        try:
            video_path = Path(input_data["video_path"])
            
            # Generate output filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            model_filename = f"pos_model_{timestamp}.stl"
            model_path = Path("pipeline/storage/output") / model_filename
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract frames from video
            frames = await self._extract_video_frames(video_path)
            
            # Generate depth maps from frames
            depth_maps = await self._generate_depth_maps(frames)
            
            # Create 3D mesh from depth maps
            vertices, faces = await self._create_mesh(frames, depth_maps)
            
            # Export to STL format
            await self._export_stl(vertices, faces, model_path)
            
            return {
                **input_data,  # Pass through previous stage data
                "model_path": str(model_path),
                "model_filename": model_filename,
                "format": self.output_format,
                "vertices": len(vertices),
                "faces": len(faces),
                "quality": self.quality
            }
            
        except Exception as e:
            raise ProcessingError(
                stage=self.stage_name,
                message=f"Model conversion failed: {str(e)}",
                details={"exception_type": type(e).__name__}
            )
    
    async def _extract_video_frames(self, video_path: Path) -> List[np.ndarray]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of video frames
        """
        frames = []
        cap = cv2.VideoCapture(str(video_path))
        
        try:
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on quality setting
                if frame_idx % self.settings["sample_rate"] == 0:
                    frames.append(frame)
                
                frame_idx += 1
                
                # Limit total frames to prevent excessive processing
                if len(frames) >= 100:
                    break
        finally:
            cap.release()
        
        return frames
    
    async def _generate_depth_maps(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Generate depth maps from video frames.
        
        For prototype: Uses simple edge-based depth estimation.
        Production: Would use ML models like MiDaS, DPT, etc.
        
        Args:
            frames: List of video frames
            
        Returns:
            List of depth maps
        """
        depth_maps = []
        
        for frame in frames:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect edges (proxy for depth)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Invert edges for depth (edges are closer)
            depth = 255 - edges
            
            # Apply distance transform for smooth depth
            depth = cv2.distanceTransform(depth, cv2.DIST_L2, 5)
            
            # Normalize depth map
            depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            depth_maps.append(depth_normalized)
        
        return depth_maps
    
    async def _create_mesh(
        self,
        frames: List[np.ndarray],
        depth_maps: List[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create 3D mesh from frames and depth maps.
        
        Args:
            frames: Video frames
            depth_maps: Corresponding depth maps
            
        Returns:
            Tuple of (vertices, faces) as numpy arrays
        """
        # Use middle frame for texture/color
        middle_idx = len(frames) // 2
        frame = frames[middle_idx]
        depth_map = depth_maps[middle_idx]
        
        # Resize for manageable mesh size
        target_height = 100
        aspect_ratio = frame.shape[1] / frame.shape[0]
        target_width = int(target_height * aspect_ratio)
        
        frame_resized = cv2.resize(frame, (target_width, target_height))
        depth_resized = cv2.resize(depth_map, (target_width, target_height))
        
        # Create vertices from depth map
        vertices = []
        vertex_indices = {}
        
        height, width = depth_resized.shape
        
        for y in range(height):
            for x in range(width):
                # Z value from depth map (normalized)
                z = depth_resized[y, x] / 255.0 * 50.0  # Scale depth
                
                # Add vertex
                vertices.append([
                    x * 2.0,  # X coordinate
                    y * 2.0,  # Y coordinate
                    z          # Z coordinate (depth)
                ])
                vertex_indices[(y, x)] = len(vertices) - 1
        
        # Create faces (triangles) from grid
        faces = []
        
        for y in range(height - 1):
            for x in range(width - 1):
                # Get vertex indices for quad
                v1 = vertex_indices[(y, x)]
                v2 = vertex_indices[(y, x + 1)]
                v3 = vertex_indices[(y + 1, x + 1)]
                v4 = vertex_indices[(y + 1, x)]
                
                # Create two triangles from quad
                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])
        
        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)
    
    async def _export_stl(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        output_path: Path
    ):
        """
        Export mesh to STL format (binary).
        
        Args:
            vertices: Vertex array
            faces: Face array
            output_path: Output file path
        """
        with open(output_path, 'wb') as f:
            # Write STL header (80 bytes)
            header = b'Binary STL file generated by POS Pipeline'
            header = header.ljust(80, b'\x00')
            f.write(header)
            
            # Write number of triangles
            num_triangles = len(faces)
            f.write(struct.pack('<I', num_triangles))
            
            # Write each triangle
            for face in faces:
                # Get vertices for this face
                v1 = vertices[face[0]]
                v2 = vertices[face[1]]
                v3 = vertices[face[2]]
                
                # Calculate normal vector
                edge1 = v2 - v1
                edge2 = v3 - v1
                normal = np.cross(edge1, edge2)
                
                # Normalize
                norm_length = np.linalg.norm(normal)
                if norm_length > 0:
                    normal = normal / norm_length
                else:
                    normal = np.array([0.0, 0.0, 1.0])
                
                # Write normal
                f.write(struct.pack('<fff', *normal))
                
                # Write vertices
                f.write(struct.pack('<fff', *v1))
                f.write(struct.pack('<fff', *v2))
                f.write(struct.pack('<fff', *v3))
                
                # Write attribute byte count (unused)
                f.write(struct.pack('<H', 0))
