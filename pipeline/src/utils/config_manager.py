"""
Configuration management for the pipeline.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
import yaml


class ConfigManager:
    """
    Manages pipeline configuration from environment and files.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file (JSON or YAML)
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment."""
        config = self._get_default_config()
        
        # Load from file if provided
        if self.config_path and self.config_path.exists():
            file_config = self._load_config_file(self.config_path)
            config = self._merge_configs(config, file_config)
        
        # Override with environment variables
        env_config = self._load_from_env()
        config = self._merge_configs(config, env_config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "pipeline": {
                "name": "pos_to_3d_pipeline",
                "version": "0.1.0",
                "max_concurrent_executions": 4
            },
            "storage": {
                "base_path": Path("storage"),
                "input_path": Path("storage/input"),
                "output_path": Path("storage/output"),
                "temp_path": Path("storage/temp"),
                "retention_days": 7
            },
            "stages": {
                "text_processor": {
                    "max_text_length": 5000,
                    "min_text_length": 10,
                    "enable_enhancement": True
                },
                "video_generator": {
                    "min_duration": 30,
                    "default_duration": 30,
                    "fps": 24,
                    "resolution": [1920, 1080],
                    "format": "mp4"
                },
                "model_converter": {
                    "output_format": "STL",
                    "quality": "medium",
                    "max_vertices": 1000000
                }
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "log_file": Path("logs/pipeline.log")
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4
            }
        }
    
    def _load_config_file(self, path: Path) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file."""
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {path.suffix}")
        except Exception as e:
            print(f"Warning: Failed to load config file {path}: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Pipeline settings
        if os.getenv("PIPELINE_MAX_CONCURRENT"):
            env_config.setdefault("pipeline", {})["max_concurrent_executions"] = int(
                os.getenv("PIPELINE_MAX_CONCURRENT")
            )
        
        # Storage paths
        if os.getenv("STORAGE_BASE_PATH"):
            base_path = Path(os.getenv("STORAGE_BASE_PATH"))
            env_config.setdefault("storage", {}).update({
                "base_path": base_path,
                "input_path": base_path / "input",
                "output_path": base_path / "output",
                "temp_path": base_path / "temp"
            })
        
        # Logging
        if os.getenv("LOG_LEVEL"):
            env_config.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
        
        # API settings
        if os.getenv("API_HOST"):
            env_config.setdefault("api", {})["host"] = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            env_config.setdefault("api", {})["port"] = int(os.getenv("API_PORT"))
        
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Configuration key path (e.g., "stages.video_generator.fps")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_stage_config(self, stage_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific stage.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Stage configuration dictionary
        """
        return self.get(f"stages.{stage_name}", {})
    
    def ensure_directories(self):
        """Ensure all configured directories exist."""
        storage_config = self.config.get("storage", {})
        
        for key, path in storage_config.items():
            if key.endswith("_path") and isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
        
        # Ensure log directory exists
        log_file = self.config.get("logging", {}).get("log_file")
        if log_file and isinstance(log_file, Path):
            log_file.parent.mkdir(parents=True, exist_ok=True)
