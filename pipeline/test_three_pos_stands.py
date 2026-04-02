"""
End-to-End Test: Three Marketing POS Stands
Creates 1-minute videos and 3D models for three different cardboard displays.
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


# Three detailed POS stand descriptions
POS_STANDS = [
    {
        "id": "chips_tower",
        "name": "Chips Tower Display",
        "description": """
A vibrant cardboard tower display stand for premium potato chips. The structure is 
180cm tall with a hexagonal base design made from corrugated cardboard. Features 
five rotating tiers in bold red and yellow colors with crispy chip graphics. Each 
tier displays different chip flavors with eye-catching product photography. The 
top features a 3D crown-shaped header with the brand logo illuminated by LED strips. 
The base has reinforced cardboard feet for stability and includes a built-in 
storage compartment. Modern geometric patterns frame each product shelf with 
appetizing imagery of golden crispy chips and fresh ingredients.
"""
    },
    {
        "id": "energy_drink_pyramid",
        "name": "Energy Drink Pyramid",
        "description": """
A dynamic pyramid-shaped cardboard display stand for energy drinks featuring an 
aggressive modern design. The structure is 150cm tall made from triple-wall 
corrugated cardboard for extra strength. Electric blue and neon green color scheme 
with lightning bolt graphics racing across the surfaces. Four-sided pyramid design 
with stepped shelving on each face, capable of holding 48 cans. The apex features 
a rotating holographic logo panel that catches light. Bold typography announces 
'FUEL YOUR DAY' in metallic silver print. Reinforced edges and corner protectors 
ensure structural integrity. The base includes anti-slip rubber pads and built-in 
cable management for optional LED accent lighting.
"""
    },
    {
        "id": "premium_beverage_column",
        "name": "Premium Beverage Column",
        "description": """
An elegant cylindrical column display stand for premium craft beverages and specialty 
drinks. Standing 200cm tall, constructed from eco-friendly kraft cardboard with a 
natural brown finish and white accent printing. The circular design features rotating 
shelves at three levels, each with curved product cradles that securely hold bottles. 
Minimalist Scandinavian-inspired design with clean lines and sophisticated typography. 
The top showcases a fabric banner system for seasonal messaging. Perforated ventilation 
patterns create an artistic shadow effect. The weighted base includes a hidden storage 
drawer for extra stock. Embossed texture panels add tactile interest while maintaining 
the premium aesthetic. Includes hanging hooks for promotional materials and a QR code 
panel for digital engagement.
"""
    }
]


async def process_pos_stand(stand_data: dict, config_manager: ConfigManager, logger: PipelineLogger):
    """
    Process a single POS stand through the complete pipeline.
    
    Args:
        stand_data: Dictionary with stand information
        config_manager: Configuration manager instance
        logger: Logger instance
    
    Returns:
        Dictionary with processing results
    """
    stand_id = stand_data["id"]
    stand_name = stand_data["name"]
    description = stand_data["description"].strip()
    
    logger.info("="*80)
    logger.info(f"Processing: {stand_name}")
    logger.info(f"ID: {stand_id}")
    logger.info("="*80)
    
    # Create status tracker
    tracker = StatusTracker(persist_path=Path(f"pipeline/storage/temp/status_{stand_id}.json"))
    
    # Create pipeline orchestrator
    orchestrator = PipelineOrchestrator(status_tracker=tracker)
    
    # Configure stages with 60-second video duration
    text_config = config_manager.get_stage_config("text_processor")
    
    # Modify video config for 60-second videos (1 minute)
    video_config = config_manager.get_stage_config("video_generator").copy()
    video_config["default_duration"] = 60  # 1 minute
    video_config["min_duration"] = 60
    
    model_config = config_manager.get_stage_config("model_converter")
    
    # Add stages
    orchestrator.add_stage(TextProcessor(text_config))
    orchestrator.add_stage(VideoGenerator(video_config))
    orchestrator.add_stage(ModelConverter(model_config))
    
    # Prepare input
    input_data = {
        "text": description,
        "metadata": {
            "stand_id": stand_id,
            "stand_name": stand_name,
            "duration": "60_seconds"
        }
    }
    
    # Execute pipeline
    start_time = time.time()
    
    try:
        result = await orchestrator.execute_pipeline(input_data, execution_id=f"pos_{stand_id}")
        execution_time = time.time() - start_time
        
        logger.info("")
        logger.info(f"✅ {stand_name} - COMPLETED")
        logger.info(f"⏱️  Execution time: {execution_time:.2f} seconds")
        logger.info("")
        logger.info("📊 Results:")
        logger.info(f"   Keywords: {', '.join(result.get('keywords', [])[:8])}")
        logger.info(f"   Video: {result.get('video_filename', 'N/A')}")
        logger.info(f"   Video Duration: {result.get('duration', 0):.1f} seconds")
        logger.info(f"   Video Frame Count: {result.get('frame_count', 0)}")
        logger.info(f"   3D Model: {result.get('model_filename', 'N/A')}")
        logger.info(f"   Model Vertices: {result.get('vertices', 0):,}")
        logger.info(f"   Model Faces: {result.get('faces', 0):,}")
        
        # Check file sizes
        video_path = Path(result.get('video_path', ''))
        model_path = Path(result.get('model_path', ''))
        
        video_size = video_path.stat().st_size / (1024*1024) if video_path.exists() else 0
        model_size = model_path.stat().st_size / 1024 if model_path.exists() else 0
        
        logger.info(f"   Video Size: {video_size:.2f} MB")
        logger.info(f"   Model Size: {model_size:.2f} KB")
        logger.info("")
        
        return {
            "stand_id": stand_id,
            "stand_name": stand_name,
            "status": "success",
            "execution_time": execution_time,
            "video_path": str(video_path),
            "model_path": str(model_path),
            "video_size_mb": video_size,
            "model_size_kb": model_size,
            "vertices": result.get('vertices', 0),
            "faces": result.get('faces', 0),
            "duration": result.get('duration', 0)
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ {stand_name} - FAILED")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Execution time: {execution_time:.2f} seconds")
        
        return {
            "stand_id": stand_id,
            "stand_name": stand_name,
            "status": "failed",
            "error": str(e),
            "execution_time": execution_time
        }


async def main():
    """Run the complete test for all three POS stands."""
    
    # Initialize configuration and logging
    config_manager = ConfigManager()
    config_manager.ensure_directories()
    
    logger = PipelineLogger(
        name="pos_test",
        level="INFO",
        use_json=False
    )
    
    logger.info("╔" + "="*78 + "╗")
    logger.info("║" + " "*20 + "THREE POS STANDS - END-TO-END TEST" + " "*24 + "║")
    logger.info("╚" + "="*78 + "╝")
    logger.info("")
    logger.info("Test Configuration:")
    logger.info("  • Number of Stands: 3")
    logger.info("  • Video Duration: 60 seconds (1 minute)")
    logger.info("  • Output Format: MP4 video + STL 3D model")
    logger.info("")
    
    # Process all three stands
    results = []
    total_start = time.time()
    
    for idx, stand in enumerate(POS_STANDS, 1):
        logger.info(f"Processing Stand {idx}/3...")
        logger.info("")
        
        result = await process_pos_stand(stand, config_manager, logger)
        results.append(result)
        
        logger.info("")
    
    total_time = time.time() - total_start
    
    # Print summary
    logger.info("╔" + "="*78 + "╗")
    logger.info("║" + " "*30 + "FINAL SUMMARY" + " "*35 + "║")
    logger.info("╚" + "="*78 + "╝")
    logger.info("")
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    logger.info(f"Total Execution Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    logger.info(f"Successful: {successful}/{len(results)}")
    logger.info(f"Failed: {failed}/{len(results)}")
    logger.info("")
    
    # Detailed results table
    logger.info("Detailed Results:")
    logger.info("-" * 80)
    
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        logger.info(f"{status_icon} {result['stand_name']}")
        logger.info(f"   Status: {result['status'].upper()}")
        logger.info(f"   Time: {result['execution_time']:.2f}s")
        
        if result["status"] == "success":
            logger.info(f"   Video: {result['video_size_mb']:.2f} MB ({result['duration']:.1f}s)")
            logger.info(f"   Model: {result['model_size_kb']:.2f} KB ({result['vertices']:,} vertices)")
            logger.info(f"   Files:")
            logger.info(f"     - {result['video_path']}")
            logger.info(f"     - {result['model_path']}")
        else:
            logger.info(f"   Error: {result.get('error', 'Unknown')}")
        
        logger.info("")
    
    # Output file locations
    logger.info("Output Location: pipeline/storage/output/")
    logger.info("")
    logger.info("To view the results:")
    logger.info("  • Videos: Open .mp4 files in any video player")
    logger.info("  • 3D Models: Open .stl files in:")
    logger.info("    - Blender (free)")
    logger.info("    - MeshLab (free)")
    logger.info("    - 3D Builder (Windows)")
    logger.info("    - Any 3D slicer software")
    logger.info("")
    
    if successful == len(results):
        logger.info("🎉 All POS stands processed successfully!")
        return 0
    else:
        logger.info(f"⚠️  {failed} stand(s) failed to process")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
