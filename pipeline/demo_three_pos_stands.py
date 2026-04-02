"""
DEMO: Three POS Stands - Quick Demonstration
Shows pipeline working for all three designs with summary output.
"""

import asyncio
import sys
from pathlib import Path
import time
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.utils.config_manager import ConfigManager


# Three POS stand designs
POS_STANDS = [
    {
        "id": 1,
        "name": "Chips Tower Display",
        "material": "Corrugated Cardboard",
        "height": "180cm",
        "description": "A vibrant cardboard tower display stand for premium potato chips. The structure is 180cm tall with a hexagonal base design made from corrugated cardboard. Features five rotating tiers in bold red and yellow colors with crispy chip graphics. Each tier displays different chip flavors with eye-catching product photography. The top features a 3D crown-shaped header with the brand logo. Modern geometric patterns frame each product shelf."
    },
    {
        "id": 2,
        "name": "Energy Drink Pyramid",
        "material": "Triple-Wall Cardboard",
        "height": "150cm",
        "description": "A dynamic pyramid-shaped cardboard display stand for energy drinks featuring an aggressive modern design. The structure is 150cm tall made from triple-wall corrugated cardboard for extra strength. Electric blue and neon green color scheme with lightning bolt graphics racing across the surfaces. Four-sided pyramid design with stepped shelving on each face, capable of holding 48 cans. The apex features a rotating holographic logo panel."
    },
    {
        "id": 3,
        "name": "Premium Beverage Column",
        "material": "Eco-Friendly Kraft Cardboard",
        "height": "200cm",
        "description": "An elegant cylindrical column display stand for premium craft beverages. Standing 200cm tall, constructed from eco-friendly kraft cardboard with a natural brown finish and white accent printing. The circular design features rotating shelves at three levels, each with curved product cradles that securely hold bottles. Minimalist Scandinavian-inspired design with clean lines and sophisticated typography. Perforated ventilation patterns create an artistic shadow effect."
    }
]


async def main():
    """Run demonstration for all three POS stands."""
    
    print("╔" + "="*78 + "╗")
    print("║" + " "*22 + "THREE POS STANDS - PIPELINE DEMO" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    print()
    print("Configuration:")
    print(f"  • Number of Designs: {len(POS_STANDS)}")
    print(f"  • Video Duration: 60 seconds (1 minute) each")
    print(f"  • Output Format: MP4 video + STL 3D model")
    print(f"  • Total Expected Time: ~6-7 minutes")
    print()
    
    # Initialize config
    config_manager = ConfigManager()
    config_manager.ensure_directories()
    
    # Process each stand
    results = []
    overall_start = time.time()
    
    for idx, stand in enumerate(POS_STANDS, 1):
        print("─" * 80)
        print(f"Stand {idx}/3: {stand['name']}")
        print("─" * 80)
        print(f"Material: {stand['material']}")
        print(f"Height: {stand['height']}")
        print(f"Description: {stand['description'][:100]}...")
        print()
        
        # Create pipeline
        tracker = StatusTracker()
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        
        # Configure for 60-second videos
        text_config = config_manager.get_stage_config("text_processor")
        video_config = config_manager.get_stage_config("video_generator").copy()
        video_config["default_duration"] = 60
        video_config["min_duration"] = 60
        model_config = config_manager.get_stage_config("model_converter")
        
        orchestrator.add_stage(TextProcessor(text_config))
        orchestrator.add_stage(VideoGenerator(video_config))
        orchestrator.add_stage(ModelConverter(model_config))
        
        # Process
        start_time = time.time()
        print(f"⏳ Processing started at {datetime.now().strftime('%H:%M:%S')}...")
        
        try:
            result = await orchestrator.execute_pipeline(
                {"text": stand["description"]},
                execution_id=f"demo_{idx}"
            )
            
            exec_time = time.time() - start_time
            
            print(f"✅ Completed in {exec_time:.1f} seconds")
            print()
            print("📊 Output:")
            print(f"  Video: {result['video_filename']}")
            print(f"    - Duration: {result['duration']:.1f} seconds")
            print(f"    - Frames: {result['frame_count']:,}")
            print(f"    - Size: {Path(result['video_path']).stat().st_size / (1024*1024):.2f} MB")
            print()
            print(f"  3D Model: {result['model_filename']}")
            print(f"    - Vertices: {result['vertices']:,}")
            print(f"    - Faces: {result['faces']:,}")
            print(f"    - Size: {Path(result['model_path']).stat().st_size / 1024:.2f} KB")
            print()
            
            results.append({
                "name": stand["name"],
                "status": "success",
                "time": exec_time,
                "video": result['video_filename'],
                "model": result['model_filename']
            })
            
        except Exception as e:
            exec_time = time.time() - start_time
            print(f"❌ Failed in {exec_time:.1f} seconds")
            print(f"Error: {str(e)}")
            print()
            
            results.append({
                "name": stand["name"],
                "status": "failed",
                "time": exec_time,
                "error": str(e)
            })
    
    total_time = time.time() - overall_start
    
    # Final summary
    print()
    print("╔" + "="*78 + "╗")
    print("║" + " "*32 + "FINAL SUMMARY" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    successful = sum(1 for r in results if r["status"] == "success")
    
    print(f"✅ Successfully Processed: {successful}/{len(POS_STANDS)} stands")
    print(f"⏱️  Total Time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print()
    
    if successful > 0:
        print("Generated Files:")
        print()
        for result in results:
            if result["status"] == "success":
                print(f"  📦 {result['name']}:")
                print(f"      Video:  {result['video']}")
                print(f"      Model:  {result['model']}")
                print()
        
        print("📂 Location: /workspace/pipeline/storage/output/")
        print()
        print("💡 Next Steps:")
        print("  1. View videos in any video player (VLC, QuickTime, etc.)")
        print("  2. Open STL files in:")
        print("     • Blender (free 3D software)")
        print("     • MeshLab (free mesh viewer)")
        print("     • Online: https://www.viewstl.com/")
        print("  3. Use STL files for 3D printing or manufacturing")
        print()
    
    print("="*80)
    
    return 0 if successful == len(POS_STANDS) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
