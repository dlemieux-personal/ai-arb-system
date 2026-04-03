"""
Schema Validator Module
Validates submissions against JSON schema.
"""

from typing import Dict, Any, List, Tuple, cast
import json
from pathlib import Path
import jsonschema
from jsonschema import Draft7Validator, ValidationError


class SchemaValidator:
    """Validates submissions against JSON schema"""
    
    def __init__(self, schema_path: Path):
        """
        Initialize the schema validator
        
        Args:
            schema_path: Path to the JSON schema file
        """
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load and return the JSON schema"""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return cast(Dict[str, Any], json.load(f))
    
    def validate(self, submission_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate submission data against schema
        
        Args:
            submission_data: Dictionary of submission data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            self.validator.validate(submission_data)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")
            return False, errors
    
    def get_validation_errors(self, submission_data: Dict[str, Any]) -> List[str]:
        """
        Get detailed validation errors
        
        Args:
            submission_data: Dictionary of submission data
            
        Returns:
            List of detailed error messages
        """
        errors = []
        for error in self.validator.iter_errors(submission_data):
            path = " -> ".join(str(p) for p in error.absolute_path)
            errors.append(f"Path: {path}, Error: {error.message}")
        return errors
