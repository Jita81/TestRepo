#!/usr/bin/env python
"""
Quick start script for testing the pipeline locally.

This script demonstrates the basic usage of the pipeline components.
"""

import sys
import time
from pathlib import Path
import asyncio

# Add common to path
sys.path.insert(0, str(Path(__file__).parent))

from common import (
    TextInput,
    configure_logging,
    get_logger,
)
from common.config import get_settings, ensure_directories
from video_generator.service import VideoGeneratorService
from model_converter.service import ModelConverterService


def print_banner():
    """Print welcome banner."""
    print("=" * 80)
    print("  POS Display Pipeline - Quick Start Demo")
    print("  Version 1.0.0")
    print("=" * 80)
    print()


def main():
    """Run quick start demo."""
    print_banner()
    
    # Initialize settings
    settings = get_settings()
    configure_logging(
        log_level="INFO",
        log_file=None,  # Log to console only
        json_logs=False  # Human-readable logs
    )
    ensure_directories(settings)
    
    logger = get_logger(__name__)
    logger.info("Starting pipeline demo...")
    
    # Test input
    description = "A modern retail display for energy drinks with LED backlighting and metallic finish"
    request_id = "demo_" + str(int(time.time()))
    
    print(f"📝 Input Description: {description}")
    print(f"🆔 Request ID: {request_id}")
    print()
    
    # Validate input
    try:
        text_input = TextInput(description=description)
        logger.info("✅ Input validation passed")
        print("✅ Input validation: PASSED")
    except Exception as e:
        logger.error(f"❌ Input validation failed: {e}")
        print(f"❌ Input validation: FAILED - {e}")
        return 1
    
    print()
    print("=" * 80)
    print("Step 1: Video Generation")
    print("=" * 80)
    
    # Generate video
    try:
        video_service = VideoGeneratorService()
        print("🎬 Generating video...")
        print(f"   - Duration: {settings.video_duration} seconds")
        print(f"   - Frame rate: {settings.video_frame_rate} fps")
        print(f"   - Resolution: {settings.video_width}x{settings.video_height}")
        print()
        
        video_metadata = video_service.generate_video(description, request_id)
        
        print(f"✅ Video generation complete!")
        print(f"   - Path: {video_metadata.video_path}")
        print(f"   - Size: {video_metadata.size_bytes / (1024*1024):.2f} MB")
        print(f"   - Duration: {video_metadata.duration} seconds")
        print()
        
    except Exception as e:
        logger.error(f"❌ Video generation failed: {e}")
        print(f"❌ Video generation: FAILED - {e}")
        return 1
    
    print()
    print("=" * 80)
    print("Step 2: 3D Model Conversion")
    print("=" * 80)
    
    # Convert to 3D model
    try:
        model_service = ModelConverterService()
        print("🔄 Converting video to 3D model...")
        print(f"   - Point cloud density: {settings.point_cloud_density}")
        print(f"   - Mesh quality: {settings.mesh_quality}")
        print()
        
        model_metadata = model_service.convert_video_to_3d(
            video_metadata.video_path,
            request_id
        )
        
        print(f"✅ 3D model conversion complete!")
        print(f"   - Path: {model_metadata.model_path}")
        print(f"   - Format: {model_metadata.format.upper()}")
        print(f"   - Vertices: {model_metadata.vertex_count:,}")
        print(f"   - Faces: {model_metadata.face_count:,}")
        print(f"   - Size: {model_metadata.size_bytes / 1024:.2f} KB")
        print()
        
    except Exception as e:
        logger.error(f"❌ 3D conversion failed: {e}")
        print(f"❌ 3D model conversion: FAILED - {e}")
        return 1
    
    print()
    print("=" * 80)
    print("🎉 Pipeline Demo Complete!")
    print("=" * 80)
    print()
    print("Generated files:")
    print(f"  📹 Video: {video_metadata.video_path}")
    print(f"  📦 3D Model: {model_metadata.model_path}")
    print()
    print("Next steps:")
    print("  1. View the generated video with any video player")
    print("  2. Open the STL file in a 3D viewer (e.g., MeshLab, Blender)")
    print("  3. Start the full pipeline with: docker-compose up -d")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)