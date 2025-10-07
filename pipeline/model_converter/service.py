"""3D model conversion service implementation."""

import os
import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
import cv2
from stl import mesh

import sys
sys.path.append(str(Path(__file__).parent.parent))

from common import (
    PipelineMessage,
    PipelineStatus,
    PipelineStage,
    ModelMetadata,
    QueueClient,
    get_logger,
    ModelConversionError
)
from common.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ModelConverterService:
    """Service for converting videos to 3D models."""
    
    def __init__(self):
        """Initialize model converter service."""
        self.settings = settings
        self.output_dir = Path(settings.model_storage_path)
        self.temp_dir = Path(settings.temp_storage_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("model_converter_initialized", output_dir=str(self.output_dir))
    
    def convert_video_to_3d(self, video_path: str, request_id: str) -> ModelMetadata:
        """
        Convert video to 3D model in STL format.
        
        For the prototype, this creates a simple 3D mesh from video frames.
        In production, this would use advanced video-to-3D reconstruction.
        
        Args:
            video_path: Path to the video file
            request_id: Unique request identifier
            
        Returns:
            ModelMetadata with model information
            
        Raises:
            ModelConversionError: If conversion fails
        """
        try:
            logger.info(
                "model_conversion_started",
                request_id=request_id,
                video_path=video_path
            )
            
            # Extract frames from video
            frames = self._extract_frames(video_path, request_id)
            
            # Generate point cloud from frames
            point_cloud = self._generate_point_cloud(frames, request_id)
            
            # Create mesh from point cloud
            stl_path = self._create_mesh(point_cloud, request_id)
            
            # Get file statistics
            file_size = Path(stl_path).stat().st_size
            
            # Load mesh to get vertex/face count
            stl_mesh = mesh.Mesh.from_file(stl_path)
            vertex_count = len(stl_mesh.vectors) * 3
            face_count = len(stl_mesh.vectors)
            
            logger.info(
                "model_conversion_completed",
                request_id=request_id,
                path=stl_path,
                vertices=vertex_count,
                faces=face_count,
                size_mb=f"{file_size / (1024*1024):.2f}"
            )
            
            # Create metadata
            metadata = ModelMetadata(
                model_path=stl_path,
                format="stl",
                vertex_count=vertex_count,
                face_count=face_count,
                size_bytes=file_size
            )
            
            return metadata
            
        except Exception as e:
            logger.error(
                "model_conversion_failed",
                request_id=request_id,
                error=str(e)
            )
            raise ModelConversionError(
                f"Model conversion failed: {str(e)}",
                details={"request_id": request_id}
            )
    
    def _extract_frames(self, video_path: str, request_id: str) -> List[np.ndarray]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to video file
            request_id: Request identifier
            
        Returns:
            List of frames as numpy arrays
        """
        logger.info("extracting_frames", video_path=video_path)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ModelConversionError(
                "Failed to open video file",
                details={"path": video_path}
            )
        
        frames = []
        frame_count = 0
        sample_rate = 10  # Extract every 10th frame for efficiency
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        
        logger.info(
            "frames_extracted",
            total_frames=frame_count,
            sampled_frames=len(frames),
            request_id=request_id
        )
        
        return frames
    
    def _generate_point_cloud(
        self,
        frames: List[np.ndarray],
        request_id: str
    ) -> np.ndarray:
        """
        Generate point cloud from video frames.
        
        This is a simplified implementation for the prototype.
        In production, this would use depth estimation and proper 3D reconstruction.
        
        Args:
            frames: List of video frames
            request_id: Request identifier
            
        Returns:
            Point cloud as Nx3 numpy array
        """
        logger.info("generating_point_cloud", num_frames=len(frames))
        
        points = []
        
        # Sample points from each frame
        points_per_frame = settings.point_cloud_density // len(frames)
        
        for frame_idx, frame in enumerate(frames):
            # Convert to grayscale for depth approximation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Sample points based on intensity (simulating depth)
            for _ in range(points_per_frame):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                
                # Use intensity as depth approximation
                depth = gray[y, x] / 255.0
                
                # Normalize coordinates to [-1, 1] range
                norm_x = (x / width) * 2 - 1
                norm_y = (y / height) * 2 - 1
                norm_z = depth * 2 - 1
                
                # Add temporal dimension
                time_offset = (frame_idx / len(frames)) * 0.5
                
                points.append([norm_x, norm_y, norm_z + time_offset])
        
        point_cloud = np.array(points, dtype=np.float32)
        
        logger.info(
            "point_cloud_generated",
            num_points=len(point_cloud),
            request_id=request_id
        )
        
        return point_cloud
    
    def _create_mesh(self, point_cloud: np.ndarray, request_id: str) -> str:
        """
        Create STL mesh from point cloud.
        
        This creates a simple mesh using convex hull.
        In production, would use proper mesh reconstruction algorithms.
        
        Args:
            point_cloud: Nx3 array of 3D points
            request_id: Request identifier
            
        Returns:
            Path to generated STL file
        """
        logger.info("creating_mesh", num_points=len(point_cloud))
        
        try:
            from scipy.spatial import ConvexHull
        except ImportError:
            # Fallback: create simple box mesh if scipy not available
            return self._create_simple_mesh(point_cloud, request_id)
        
        try:
            # Compute convex hull
            hull = ConvexHull(point_cloud)
            
            # Create mesh
            num_faces = len(hull.simplices)
            stl_mesh = mesh.Mesh(np.zeros(num_faces, dtype=mesh.Mesh.dtype))
            
            for i, simplex in enumerate(hull.simplices):
                for j in range(3):
                    stl_mesh.vectors[i][j] = point_cloud[simplex[j]]
            
            # Save to file
            output_path = str(self.output_dir / f"{request_id}.stl")
            stl_mesh.save(output_path)
            
            logger.info(
                "mesh_created",
                path=output_path,
                faces=num_faces,
                request_id=request_id
            )
            
            return output_path
            
        except Exception as e:
            logger.warning(
                "convex_hull_failed, using simple mesh",
                error=str(e)
            )
            return self._create_simple_mesh(point_cloud, request_id)
    
    def _create_simple_mesh(self, point_cloud: np.ndarray, request_id: str) -> str:
        """
        Create a simple box mesh as fallback.
        
        Args:
            point_cloud: Point cloud (used for sizing)
            request_id: Request identifier
            
        Returns:
            Path to generated STL file
        """
        logger.info("creating_simple_box_mesh")
        
        # Calculate bounding box
        min_coords = point_cloud.min(axis=0)
        max_coords = point_cloud.max(axis=0)
        
        # Create box vertices
        vertices = np.array([
            [min_coords[0], min_coords[1], min_coords[2]],
            [max_coords[0], min_coords[1], min_coords[2]],
            [max_coords[0], max_coords[1], min_coords[2]],
            [min_coords[0], max_coords[1], min_coords[2]],
            [min_coords[0], min_coords[1], max_coords[2]],
            [max_coords[0], min_coords[1], max_coords[2]],
            [max_coords[0], max_coords[1], max_coords[2]],
            [min_coords[0], max_coords[1], max_coords[2]],
        ])
        
        # Define box faces (12 triangles)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 6, 5], [4, 7, 6],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2],  # right
        ])
        
        # Create mesh
        stl_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                stl_mesh.vectors[i][j] = vertices[face[j]]
        
        # Save to file
        output_path = str(self.output_dir / f"{request_id}.stl")
        stl_mesh.save(output_path)
        
        logger.info("simple_mesh_created", path=output_path)
        return output_path
    
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
            
            # Get video path from message
            video_metadata = message.payload.get("video_metadata", {})
            video_path = video_metadata.get("video_path")
            
            if not video_path:
                raise ModelConversionError(
                    "Video path not found in message",
                    details={"request_id": message.request_id}
                )
            
            # Convert video to 3D model
            model_metadata = self.convert_video_to_3d(video_path, message.request_id)
            
            # Update message
            message.stage = PipelineStage.MODEL_CONVERSION
            message.status = PipelineStatus.COMPLETED
            message.payload["model_metadata"] = model_metadata.model_dump()
            
            # Publish completion (could go to final queue or storage)
            queue_client = QueueClient(
                host=settings.queue_host,
                port=settings.queue_port,
                username=settings.queue_username,
                password=settings.queue_password
            )
            queue_client.connect()
            queue_client.declare_queue("pipeline_completed")
            queue_client.publish(
                queue_name="pipeline_completed",
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
        """Start the model converter service."""
        logger.info("starting_model_converter_service")
        
        # Connect to queue
        queue_client = QueueClient(
            host=settings.queue_host,
            port=settings.queue_port,
            username=settings.queue_username,
            password=settings.queue_password
        )
        
        queue_client.connect()
        queue_client.declare_queue("model_conversion_input")
        
        logger.info("consuming_messages")
        queue_client.consume(
            queue_name="model_conversion_input",
            callback=self.process_message,
            auto_ack=False
        )


def main():
    """Main entry point for model converter service."""
    from common.logging_config import configure_logging
    from common.config import ensure_directories
    
    configure_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        json_logs=settings.json_logs
    )
    ensure_directories(settings)
    
    service = ModelConverterService()
    service.start()


if __name__ == "__main__":
    main()