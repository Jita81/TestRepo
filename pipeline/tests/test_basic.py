"""Basic sanity tests that don't require external dependencies."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBasicSanity:
    """Basic sanity tests."""
    
    def test_python_version(self):
        """Test Python version is adequate."""
        assert sys.version_info >= (3, 11)
    
    def test_imports(self):
        """Test that basic imports work."""
        # These should work without any dependencies
        import json
        import os
        import sys
        assert True
    
    def test_path_setup(self):
        """Test that paths are set up correctly."""
        pipeline_dir = Path(__file__).parent.parent
        assert pipeline_dir.exists()
        assert (pipeline_dir / "common").exists()
        assert (pipeline_dir / "api").exists()
    
    def test_common_module_structure(self):
        """Test that common module has expected structure."""
        common_dir = Path(__file__).parent.parent / "common"
        assert (common_dir / "__init__.py").exists()
        assert (common_dir / "models.py").exists()
        assert (common_dir / "exceptions.py").exists()
        assert (common_dir / "config.py").exists()


class TestProjectStructure:
    """Tests for project structure."""
    
    def test_all_services_present(self):
        """Test that all service directories exist."""
        pipeline_dir = Path(__file__).parent.parent
        
        services = ["api", "video_generator", "model_converter", "orchestrator", "common"]
        for service in services:
            service_dir = pipeline_dir / service
            assert service_dir.exists(), f"Service directory {service} not found"
            assert (service_dir / "__init__.py").exists(), f"{service}/__init__.py not found"
    
    def test_docker_files_present(self):
        """Test that Docker files exist."""
        pipeline_dir = Path(__file__).parent.parent
        
        docker_files = [
            "Dockerfile.api",
            "Dockerfile.video",
            "Dockerfile.model",
            "Dockerfile.orchestrator",
            "docker-compose.yml"
        ]
        
        for docker_file in docker_files:
            assert (pipeline_dir / docker_file).exists(), f"{docker_file} not found"
    
    def test_documentation_present(self):
        """Test that documentation files exist."""
        pipeline_dir = Path(__file__).parent.parent
        
        docs = [
            "README.md",
            "SETUP.md",
            "API_EXAMPLES.md",
            "ARCHITECTURE.md"
        ]
        
        for doc in docs:
            assert (pipeline_dir / doc).exists(), f"{doc} not found"
    
    def test_config_files_present(self):
        """Test that configuration files exist."""
        pipeline_dir = Path(__file__).parent.parent
        
        configs = [
            "requirements.txt",
            ".env.example",
            "pytest.ini",
            "Makefile"
        ]
        
        for config in configs:
            assert (pipeline_dir / config).exists(), f"{config} not found"