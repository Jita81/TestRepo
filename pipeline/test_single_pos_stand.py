"""
Quick test: Single POS stand with 1-minute video.
"""

import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager
from src.utils.logger import PipelineLogger


async def main():
    """Run test for a single POS stand."""
    
    # Initialize
    config_manager = ConfigManager()
    config_manager.ensure_directories()
    
    logger = PipelineLogger(name="pos_test", level="INFO", use_json=False)
    
    logger.info("="*80)
    logger.info("POS STAND TEST - 1 Minute Video Generation")
    logger.info("="*80)
    
    # Create pipeline
    tracker = StatusTracker(persist_path=Path("pipeline/storage/temp/status_test.json"))
    orchestrator = PipelineOrchestrator(status_tracker=tracker)
    
    # Configure for 60-second videos
    text_config = config_manager.get_stage_config("text_processor")
    video_config = config_manager.get_stage_config("video_generator").copy()
    video_config["default_duration"] = 60  # 1 minute
    video_config["min_duration"] = 60
    model_config = config_manager.get_stage_config("model_converter")
    
    # Add stages
    orchestrator.add_stage(TextProcessor(text_config))
    orchestrator.add_stage(VideoGenerator(video_config))
    orchestrator.add_stage(ModelConverter(model_config))
    
    # Test with chips display
    description = """
A vibrant cardboard tower display stand for premium potato chips. The structure is 
180cm tall with a hexagonal base design made from corrugated cardboard. Features 
five rotating tiers in bold red and yellow colors with crispy chip graphics. Each 
tier displays different chip flavors with eye-catching product photography. The 
top features a 3D crown-shaped header with the brand logo. Modern geometric patterns 
frame each product shelf with appetizing imagery of golden crispy chips.
"""
    
    input_data = {
        "text": description.strip(),
        "metadata": {
            "test": "single_pos_stand",
            "duration": "60_seconds"
        }
    }
    
    logger.info("\nInput Description:")
    logger.info(description.strip()[:200] + "...")
    logger.info("\nStarting pipeline...")
    
    start_time = time.time()
    
    try:
        result = await orchestrator.execute_pipeline(input_data, execution_id="test_chips_tower")
        execution_time = time.time() - start_time
        
        logger.info("\n" + "="*80)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"\n⏱️  Total Time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
        
        # Display results
        logger.info(f"\n📝 Text Analysis:")
        logger.info(f"   Keywords: {', '.join(result.get('keywords', [])[:10])}")
        logger.info(f"   Colors: {', '.join(result.get('visual_elements', {}).get('colors', []))}")
        logger.info(f"   Objects: {', '.join(result.get('visual_elements', {}).get('objects', [])[:5])}")
        
        logger.info(f"\n🎬 Video Output:")
        logger.info(f"   File: {result.get('video_filename', 'N/A')}")
        logger.info(f"   Path: {result.get('video_path', 'N/A')}")
        logger.info(f"   Duration: {result.get('duration', 0):.1f} seconds")
        logger.info(f"   Frames: {result.get('frame_count', 0):,} frames")
        logger.info(f"   Resolution: {result.get('resolution', 'N/A')}")
        logger.info(f"   FPS: {result.get('fps', 0)}")
        
        video_path = Path(result.get('video_path', ''))
        if video_path.exists():
            video_size_mb = video_path.stat().st_size / (1024*1024)
            logger.info(f"   Size: {video_size_mb:.2f} MB")
        
        logger.info(f"\n🎨 3D Model Output:")
        logger.info(f"   File: {result.get('model_filename', 'N/A')}")
        logger.info(f"   Path: {result.get('model_path', 'N/A')}")
        logger.info(f"   Format: {result.get('format', 'N/A')}")
        logger.info(f"   Vertices: {result.get('vertices', 0):,}")
        logger.info(f"   Faces: {result.get('faces', 0):,}")
        
        model_path = Path(result.get('model_path', ''))
        if model_path.exists():
            model_size_kb = model_path.stat().st_size / 1024
            logger.info(f"   Size: {model_size_kb:.2f} KB")
        
        logger.info(f"\n📂 Output Location: pipeline/storage/output/")
        logger.info(f"\n💡 How to View:")
        logger.info(f"   Video: Open {result.get('video_filename')} in any video player")
        logger.info(f"   3D Model: Open {result.get('model_filename')} in Blender, MeshLab, or 3D Builder")
        
        logger.info("\n" + "="*80)
        logger.info("✅ Test completed successfully!")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
