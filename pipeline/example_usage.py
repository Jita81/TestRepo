"""
Example usage of the POS to 3D Pipeline.

This script demonstrates how to use the pipeline programmatically
(without the API).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager
from src.utils.logger import PipelineLogger


async def run_pipeline_example():
    """Run a complete pipeline example."""
    
    # Initialize configuration
    config_manager = ConfigManager()
    config_manager.ensure_directories()
    
    # Initialize logger
    logger = PipelineLogger(
        level="INFO",
        use_json=False  # Use text format for easier reading
    )
    
    logger.info("=" * 60)
    logger.info("POS to 3D Pipeline - Example Usage")
    logger.info("=" * 60)
    
    # Create status tracker
    status_tracker = StatusTracker(
        persist_path=Path("pipeline/storage/temp/status.json")
    )
    
    # Create pipeline orchestrator
    orchestrator = PipelineOrchestrator(status_tracker=status_tracker)
    
    # Add pipeline stages
    logger.info("Configuring pipeline stages...")
    
    orchestrator.add_stage(TextProcessor(
        config=config_manager.get_stage_config("text_processor")
    ))
    
    orchestrator.add_stage(VideoGenerator(
        config=config_manager.get_stage_config("video_generator")
    ))
    
    orchestrator.add_stage(ModelConverter(
        config=config_manager.get_stage_config("model_converter")
    ))
    
    logger.info(f"Pipeline configured with {len(orchestrator.stages)} stages")
    
    # Example input
    input_text = """
    A vibrant red and blue rotating display stand featuring our new energy drink 
    product line. The modern design includes bold graphics, LED lighting accents, 
    and premium product placement shelves. The display rotates slowly to showcase 
    products from all angles with eye-catching branding.
    """.strip()
    
    logger.info(f"\nInput text:\n{input_text}\n")
    
    # Prepare input data
    input_data = {
        "text": input_text,
        "metadata": {
            "example": True,
            "timestamp": "2025-10-06"
        }
    }
    
    try:
        # Execute pipeline
        logger.info("Starting pipeline execution...")
        result = await orchestrator.execute_pipeline(input_data)
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline Execution Complete!")
        logger.info("=" * 60)
        
        # Display results
        logger.info(f"\nExecution ID: {result['execution_id']}")
        logger.info(f"\nProcessed Text: {result.get('processed_text', 'N/A')[:100]}...")
        logger.info(f"\nExtracted Keywords: {', '.join(result.get('keywords', [])[:10])}")
        
        if 'visual_elements' in result:
            ve = result['visual_elements']
            logger.info(f"\nVisual Elements:")
            logger.info(f"  - Colors: {', '.join(ve.get('colors', []))}")
            logger.info(f"  - Objects: {', '.join(ve.get('objects', []))}")
            logger.info(f"  - Actions: {', '.join(ve.get('actions', []))}")
        
        logger.info(f"\nVideo Output:")
        logger.info(f"  - Path: {result.get('video_path', 'N/A')}")
        logger.info(f"  - Duration: {result.get('duration', 0):.1f} seconds")
        logger.info(f"  - Frame Count: {result.get('frame_count', 0)}")
        logger.info(f"  - Resolution: {result.get('resolution', 'N/A')}")
        
        logger.info(f"\n3D Model Output:")
        logger.info(f"  - Path: {result.get('model_path', 'N/A')}")
        logger.info(f"  - Format: {result.get('format', 'N/A')}")
        logger.info(f"  - Vertices: {result.get('vertices', 0):,}")
        logger.info(f"  - Faces: {result.get('faces', 0):,}")
        
        # Check if files exist
        video_path = Path(result.get('video_path', ''))
        model_path = Path(result.get('model_path', ''))
        
        if video_path.exists():
            video_size = video_path.stat().st_size
            logger.info(f"  - Video file size: {video_size / (1024*1024):.2f} MB")
        
        if model_path.exists():
            model_size = model_path.stat().st_size
            logger.info(f"  - Model file size: {model_size / 1024:.2f} KB")
        
        # Get execution status
        status = await status_tracker.get_status(result['execution_id'])
        logger.info(f"\nExecution Status: {status['status']}")
        logger.info(f"Progress: {status['progress']}%")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Example completed successfully!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_pipeline_example())
    sys.exit(exit_code)
