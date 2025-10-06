"""
Input validation utilities.
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class ValidationError(Exception):
    """Validation error exception."""
    pass


class InputValidator:
    """
    Validates input data against schemas and rules.
    """
    
    def __init__(self):
        """Initialize input validator."""
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas."""
        return {
            "text_input": {
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 5000
                    },
                    "metadata": {
                        "type": "object"
                    }
                }
            },
            "video_output": {
                "type": "object",
                "required": ["video_path", "duration"],
                "properties": {
                    "video_path": {"type": "string"},
                    "duration": {"type": "number", "minimum": 0},
                    "frame_count": {"type": "integer", "minimum": 1},
                    "fps": {"type": "number", "minimum": 1}
                }
            },
            "model_output": {
                "type": "object",
                "required": ["model_path", "format"],
                "properties": {
                    "model_path": {"type": "string"},
                    "format": {"type": "string", "enum": ["STL", "OBJ", "PLY"]},
                    "vertices": {"type": "integer", "minimum": 0},
                    "faces": {"type": "integer", "minimum": 0}
                }
            }
        }
    
    async def validate(
        self,
        data: Dict[str, Any],
        schema_name: Optional[str] = None
    ) -> bool:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema_name: Optional schema name to use
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        if schema_name and schema_name in self.schemas:
            schema = self.schemas[schema_name]
            self._validate_against_schema(data, schema)
        
        return True
    
    def _validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        path: str = ""
    ):
        """
        Validate data against a schema definition.
        
        Args:
            data: Data to validate
            schema: Schema definition
            path: Current path in data (for error messages)
        """
        # Check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    raise ValidationError(
                        f"Missing required field: {path}.{field}" if path else f"Missing required field: {field}"
                    )
        
        # Validate properties
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    value = data[field]
                    field_path = f"{path}.{field}" if path else field
                    self._validate_value(value, field_schema, field_path)
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str):
        """Validate a single value against its schema."""
        # Type validation
        if "type" in schema:
            expected_type = schema["type"]
            if not self._check_type(value, expected_type):
                raise ValidationError(
                    f"Invalid type for {path}: expected {expected_type}, got {type(value).__name__}"
                )
        
        # String validations
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                raise ValidationError(
                    f"String too short for {path}: minimum {schema['minLength']} characters"
                )
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                raise ValidationError(
                    f"String too long for {path}: maximum {schema['maxLength']} characters"
                )
            if "pattern" in schema and not re.match(schema["pattern"], value):
                raise ValidationError(
                    f"String does not match pattern for {path}"
                )
            if "enum" in schema and value not in schema["enum"]:
                raise ValidationError(
                    f"Invalid value for {path}: must be one of {schema['enum']}"
                )
        
        # Number validations
        if isinstance(value, (int, float)):
            if "minimum" in schema and value < schema["minimum"]:
                raise ValidationError(
                    f"Value too small for {path}: minimum {schema['minimum']}"
                )
            if "maximum" in schema and value > schema["maximum"]:
                raise ValidationError(
                    f"Value too large for {path}: maximum {schema['maximum']}"
                )
        
        # Object validation
        if isinstance(value, dict) and "properties" in schema:
            self._validate_against_schema(value, schema, path)
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        
        return isinstance(value, expected)
    
    def validate_text_input(self, text: str) -> bool:
        """
        Validate text input for pipeline.
        
        Args:
            text: Input text to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        if len(text.strip()) < 10:
            raise ValidationError("Text must be at least 10 characters")
        
        if len(text) > 5000:
            raise ValidationError("Text must not exceed 5000 characters")
        
        # Check for suspicious content
        if self._contains_suspicious_content(text):
            raise ValidationError("Text contains suspicious or potentially harmful content")
        
        return True
    
    def _contains_suspicious_content(self, text: str) -> bool:
        """Check for suspicious content patterns."""
        # Basic checks for script injection, etc.
        suspicious_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'\x00',  # Null bytes
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def validate_file_path(self, file_path: Path, must_exist: bool = False) -> bool:
        """
        Validate file path.
        
        Args:
            file_path: Path to validate
            must_exist: Whether file must exist
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(file_path, (str, Path)):
            raise ValidationError("File path must be a string or Path object")
        
        file_path = Path(file_path)
        
        # Check for path traversal
        try:
            file_path.resolve()
        except Exception:
            raise ValidationError("Invalid file path")
        
        if must_exist and not file_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        return True
