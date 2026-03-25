"""
Test Schema Validator Module
Unit tests for schema validation.
"""

import pytest
from pathlib import Path
from src.intake.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Tests for SchemaValidator class"""
    
    @pytest.fixture
    def schema_validator(self):
        """Fixture for initializing schema validator"""
        schema_path = Path(__file__).parent.parent / "schemas" / "architecture_submission_schema.json"
        return SchemaValidator(schema_path)
    
    def test_validate_valid_submission(self, schema_validator):
        """Test validation of valid submission"""
        valid_submission = {
            "submission_id": "AB-2024-123456",
            "team_name": "Architecture Team",
            "submission_date": "2024-01-15T10:00:00Z",
            "system_overview": {
                "title": "Test System",
                "description": "A test architecture submission"
            },
            "sections": {}
        }
        
        is_valid, errors = schema_validator.validate(valid_submission)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_invalid_submission(self, schema_validator):
        """Test validation of invalid submission"""
        invalid_submission = {
            "submission_id": "invalid-id",  # Invalid format
            "team_name": "Architecture Team",
            "submission_date": "invalid-date",  # Invalid date format
            "system_overview": {
                "title": "Test System",
                "description": "A test architecture submission"
            },
            "sections": {}
        }
        
        is_valid, errors = schema_validator.validate(invalid_submission)
        assert is_valid is False
        assert len(errors) > 0
