"""
Submission Loader Module
Loads and prepares submissions for processing.
"""

from typing import Optional
from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class SubmissionContent:
    """Container for submission content"""
    submission_id: str
    team_name: str
    content: str
    file_path: Path
    format: str  # 'markdown' or 'json'


class SubmissionLoader:
    """Loads submissions from the file system"""
    
    def __init__(self, intake_path: Path):
        """
        Initialize the submission loader
        
        Args:
            intake_path: Path to the incoming submissions directory
        """
        self.intake_path = Path(intake_path)
    
    def load_submission(self, filename: str) -> SubmissionContent:
        """
        Load a submission from the intake directory
        
        Args:
            filename: Name of the submission file
            
        Returns:
            SubmissionContent object
        """
        file_path = self.intake_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Submission file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine format from file extension
        file_ext = file_path.suffix.lower()
        format_type = 'markdown' if file_ext in ['.md', '.markdown'] else 'json'
        
        # TODO: Extract submission_id and team_name from content
        
        return SubmissionContent(
            submission_id="UNKNOWN",
            team_name="UNKNOWN",
            content=content,
            file_path=file_path,
            format=format_type
        )
    
    def list_submissions(self) -> list[str]:
        """
        List all submissions in the intake directory
        
        Returns:
            List of submission filenames
        """
        return [f.name for f in self.intake_path.glob('*') if f.is_file()]
