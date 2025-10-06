"""
Base classes for pipeline stages.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    
    def __init__(self, stage: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.stage = stage
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(f"{stage}: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/response."""
        return {
            "stage": self.stage,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "error_type": self.__class__.__name__
        }


class ValidationError(PipelineError):
    """Error raised when input validation fails."""
    pass


class ProcessingError(PipelineError):
    """Error raised when stage processing fails."""
    pass


class PipelineStage(ABC):
    """
    Abstract base class for all pipeline stages.
    
    Each stage must implement:
    - process: Main processing logic
    - validate: Input/output validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pipeline stage.
        
        Args:
            config: Stage-specific configuration
        """
        self.config = config
        self.stage_name = self.__class__.__name__
        self._setup()
    
    def _setup(self):
        """Optional setup method for stage-specific initialization."""
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data according to stage logic.
        
        Args:
            input_data: Dictionary containing stage input
            
        Returns:
            Dictionary containing processed results
            
        Raises:
            ProcessingError: If processing fails
        """
        pass
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any], is_input: bool = True) -> bool:
        """
        Validate stage input or output data.
        
        Args:
            data: Data to validate
            is_input: True for input validation, False for output
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the stage with validation and error handling.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed output data
        """
        start_time = time.time()
        
        try:
            # Validate input
            await self.validate(input_data, is_input=True)
            
            # Process data
            result = await self.process(input_data)
            
            # Validate output
            await self.validate(result, is_input=False)
            
            # Add metadata
            result["_metadata"] = {
                "stage": self.stage_name,
                "duration": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            return result
            
        except ValidationError as e:
            raise
        except ProcessingError as e:
            raise
        except Exception as e:
            raise ProcessingError(
                stage=self.stage_name,
                message=f"Unexpected error: {str(e)}",
                details={"exception_type": type(e).__name__}
            )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        return self.config.get(key, default)
