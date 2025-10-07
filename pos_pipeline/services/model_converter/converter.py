"""
3D Model Conversion Service for the POS Pipeline.

This service converts video frames to 3D models in STL format.
"""
import asyncio
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np
import cv2
import trimesh
from scipy.spatial import Delaunay
from utils.logging_config import get_logger
from utils.exceptions import ModelConversionError, StorageError
from models.schemas import ModelConversionResult
from config.settings import settings


logger = get_logger("model_converter")


class ModelConverter:
    """Handles conversion of video to 3D models."""
    
    def __init__(self):
        self.output_format = settings.model_format
        self.mesh_quality = settings.mesh_quality
        self.storage_path = Path(settings.storage_path) / "models"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        
    def _extract_key_frames(self, video_path: str, num_frames: int = 5) -> List[np.ndarray]:
        """
        Extract key frames from video for 3D reconstruction.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            
        Returns:
            List of extracted frames as numpy arrays
        """
        frames = []
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ModelConversionError(
                "Failed to open video file",
                details={"video_path": video_path}
            )
        
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame indices to extract
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    frames.append(frame)
                else:
                    self.logger.warning(f"Failed to read frame at index {idx}")
            
        finally:
            cap.release()
        
        if not frames:
            raise ModelConversionError(
                "No frames could be extracted from video",
                details={"video_path": video_path}
            )
        
        return frames
    
    def _frames_to_point_cloud(self, frames: List[np.ndarray]) -> np.ndarray:
        """
        Convert video frames to 3D point cloud.
        
        Args:
            frames: List of video frames
            
        Returns:
            Numpy array of 3D points (N, 3)
        """
        points = []
        
        for i, frame in enumerate(frames):
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect edges for structure
            edges = cv2.Canny(gray, 100, 200)
            
            # Get edge coordinates
            y_coords, x_coords = np.where(edges > 0)
            
            # Normalize coordinates
            height, width = gray.shape
            x_norm = (x_coords / width) * 2 - 1  # Range: -1 to 1
            y_norm = (y_coords / height) * 2 - 1
            z_norm = np.full_like(x_norm, (i / len(frames)) * 2 - 1)  # Depth from frame sequence
            
            # Sample points (limit for performance)
            max_points = 1000
            if len(x_norm) > max_points:
                indices = np.random.choice(len(x_norm), max_points, replace=False)
                x_norm = x_norm[indices]
                y_norm = y_norm[indices]
                z_norm = z_norm[indices]
            
            frame_points = np.column_stack([x_norm, y_norm, z_norm])
            points.append(frame_points)
        
        return np.vstack(points)
    
    def _create_mesh_from_points(self, points: np.ndarray) -> trimesh.Trimesh:
        """
        Create 3D mesh from point cloud using Delaunay triangulation.
        
        Args:
            points: 3D point cloud (N, 3)
            
        Returns:
            Trimesh mesh object
        """
        try:
            # Create convex hull as simplified mesh
            hull = trimesh.convex.convex_hull(points)
            
            # Optionally simplify mesh based on quality setting
            if self.mesh_quality == "low":
                target_faces = 100
            elif self.mesh_quality == "medium":
                target_faces = 500
            else:  # high
                target_faces = 1000
            
            if len(hull.faces) > target_faces:
                # Simplify mesh
                hull = hull.simplify_quadratic_decimation(target_faces)
            
            return hull
            
        except Exception as e:
            self.logger.error(f"Failed to create mesh from points: {str(e)}")
            raise ModelConversionError(
                f"Mesh creation failed: {str(e)}",
                details={"point_count": len(points)}
            )
    
    def _validate_mesh(self, mesh: trimesh.Trimesh) -> None:
        """
        Validate mesh quality and properties.
        
        Args:
            mesh: Trimesh mesh to validate
            
        Raises:
            ModelConversionError: If mesh is invalid
        """
        if not mesh.is_watertight:
            self.logger.warning("Generated mesh is not watertight")
        
        if len(mesh.vertices) < 4:
            raise ModelConversionError(
                "Mesh has insufficient vertices",
                details={"vertex_count": len(mesh.vertices)}
            )
        
        if len(mesh.faces) < 4:
            raise ModelConversionError(
                "Mesh has insufficient faces",
                details={"face_count": len(mesh.faces)}
            )
    
    def _validate_storage(self, file_size_mb: float) -> None:
        """
        Validate storage constraints.
        
        Args:
            file_size_mb: Size of file to store
            
        Raises:
            StorageError: If storage limits exceeded
        """
        if file_size_mb > settings.max_model_size_mb:
            raise StorageError(
                f"Model size {file_size_mb:.2f}MB exceeds limit of {settings.max_model_size_mb}MB",
                stage="model_conversion",
                details={"size_mb": file_size_mb, "limit_mb": settings.max_model_size_mb}
            )
    
    async def convert_to_3d(
        self,
        job_id: str,
        video_path: str
    ) -> ModelConversionResult:
        """
        Convert video to 3D model.
        
        Args:
            job_id: Unique job identifier
            video_path: Path to input video file
            
        Returns:
            ModelConversionResult with model path and metadata
            
        Raises:
            ModelConversionError: If conversion fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting 3D model conversion for job {job_id}")
            
            # Validate video file exists
            if not Path(video_path).exists():
                raise ModelConversionError(
                    "Video file not found",
                    details={"video_path": video_path}
                )
            
            # Extract key frames
            self.logger.info("Extracting key frames from video")
            frames = await asyncio.to_thread(
                self._extract_key_frames,
                video_path,
                num_frames=8
            )
            
            # Convert to point cloud
            self.logger.info(f"Converting {len(frames)} frames to point cloud")
            points = await asyncio.to_thread(
                self._frames_to_point_cloud,
                frames
            )
            
            self.logger.info(f"Generated point cloud with {len(points)} points")
            
            # Create mesh
            self.logger.info("Creating 3D mesh from point cloud")
            mesh = await asyncio.to_thread(
                self._create_mesh_from_points,
                points
            )
            
            # Validate mesh
            self._validate_mesh(mesh)
            
            # Generate output path
            model_filename = f"{job_id}.{self.output_format}"
            model_path = self.storage_path / model_filename
            
            # Export to STL
            self.logger.info(f"Exporting mesh to {self.output_format} format")
            await asyncio.to_thread(
                mesh.export,
                str(model_path)
            )
            
            # Validate file was created
            if not model_path.exists():
                raise ModelConversionError(
                    "Model file was not created",
                    details={"expected_path": str(model_path)}
                )
            
            # Get file size
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            
            # Validate storage
            self._validate_storage(file_size_mb)
            
            processing_time = time.time() - start_time
            
            result = ModelConversionResult(
                job_id=job_id,
                model_path=str(model_path),
                model_url=f"/storage/models/{model_filename}",
                format=self.output_format,
                vertex_count=len(mesh.vertices),
                face_count=len(mesh.faces),
                file_size_mb=file_size_mb,
                processing_time=processing_time
            )
            
            self.logger.info(
                f"Model conversion completed for job {job_id} in {processing_time:.2f}s "
                f"({len(mesh.vertices)} vertices, {len(mesh.faces)} faces, {file_size_mb:.2f}MB)"
            )
            
            return result
            
        except (ModelConversionError, StorageError):
            raise
        except Exception as e:
            self.logger.error(f"Model conversion failed for job {job_id}: {str(e)}")
            raise ModelConversionError(
                f"Failed to convert video to 3D model: {str(e)}",
                details={"job_id": job_id, "error": str(e)}
            )