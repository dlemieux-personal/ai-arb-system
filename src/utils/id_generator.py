"""
ID Generator Module
Generates unique identifiers for submissions and reviews.
"""

import uuid
from datetime import datetime
from typing import Optional


class IDGenerator:
    """Generates unique identifiers"""
    
    @staticmethod
    def generate_submission_id(team_prefix: str = "ARB") -> str:
        """
        Generate a submission ID
        
        Args:
            team_prefix: Prefix for the ID (default: ARB)
            
        Returns:
            Unique submission ID
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_part = str(uuid.uuid4())[:8].upper()
        return f"{team_prefix}-{timestamp}-{unique_part}"
    
    @staticmethod
    def generate_review_id() -> str:
        """
        Generate a review ID
        
        Returns:
            Unique review ID
        """
        return f"REV-{uuid.uuid4().hex[:12].upper()}"
    
    @staticmethod
    def generate_finding_id() -> str:
        """
        Generate a finding ID
        
        Returns:
            Unique finding ID
        """
        return f"FND-{uuid.uuid4().hex[:12].upper()}"
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a standard UUID
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
