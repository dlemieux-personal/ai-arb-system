"""
Submission Parser Module
Handles parsing and extraction of architecture submissions from various formats.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import re
from datetime import datetime
import yaml
from dateutil import parser as date_parser


@dataclass
class SubmissionMetadata:
    """Metadata about a submission"""
    submission_id: str
    team_name: str
    submission_date: str
    system_title: str


@dataclass
class ParsedSubmission:
    """Parsed submission containing metadata and sections"""
    metadata: SubmissionMetadata
    sections: Dict[str, Any]
    raw_content: str
    file_path: Optional[Path] = None


class MarkdownParseError(Exception):
    """Raised when Markdown parsing fails validation"""
    pass


class SubmissionParser:
    """Parser for architecture submissions"""
    
    def __init__(self):
        """Initialize the submission parser"""
        self.supported_formats = ['.md', '.markdown', '.json']
    
    def parse(self, submission_path: Path) -> ParsedSubmission:
        """
        Parse a submission file
        
        Args:
            submission_path: Path to the submission file
            
        Returns:
            ParsedSubmission object with parsed content
        """
        if not submission_path.exists():
            raise FileNotFoundError(f"Submission file not found: {submission_path}")
        
        file_ext = submission_path.suffix.lower()
        
        if file_ext in ['.md', '.markdown']:
            return self._parse_markdown(submission_path)
        elif file_ext == '.json':
            return self._parse_json(submission_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
    
    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML frontmatter from markdown content
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (frontmatter_dict, remaining_content)
        """
        if not content.startswith('---'):
            return {}, content
        
        # Find the closing --- delimiter
        lines = content.split('\n')
        closing_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                closing_idx = i
                break
        
        if closing_idx is None:
            raise MarkdownParseError("Unclosed frontmatter delimiter")
        
        frontmatter_text = '\n'.join(lines[1:closing_idx])
        remaining = '\n'.join(lines[closing_idx + 1:])
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError as e:
            raise MarkdownParseError(f"Invalid YAML frontmatter: {str(e)}")
        
        return frontmatter, remaining
    
    def _parse_boolean(self, value: Any) -> bool:
        """
        Parse boolean values from various formats
        
        Accepts:
        - Boolean literals: True, False
        - Strings: 'true', 'false', 'yes', 'no'
        - Checkboxes: '- [x]', '- [ ]'
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            checked = value.strip().lower()
            if checked in ['true', 'yes', '- [x]', '-[x]']:
                return True
            if checked in ['false', 'no', '- [ ]', '-[ ]']:
                return False
        raise MarkdownParseError(f"Invalid boolean value: {value}")
    
    def _normalize_enum(self, value: str, valid_options: List[str]) -> str:
        """
        Normalize enum value (case-insensitive matching)
        
        Args:
            value: User-provided string
            valid_options: List of valid enum values
            
        Returns:
            Normalized enum value (matching case of valid_options)
        """
        if not isinstance(value, str):
            raise MarkdownParseError(f"Enum value must be string, got {type(value)}")
        
        value_lower = value.strip().lower()
        for option in valid_options:
            if option.lower() == value_lower:
                return option
        
        raise MarkdownParseError(f"Invalid enum value: {value}. Must be one of {valid_options}")
    
    def _extract_bullet_list(self, text: str, start_idx: int) -> Tuple[List[str], int]:
        """
        Extract bullet list items starting from a given position
        
        Args:
            text: The text to search in
            start_idx: Starting index for the search
            
        Returns:
            Tuple of (list_items, next_index)
        """
        items = []
        lines = text[start_idx:].split('\n')
        
        for i, line in enumerate(lines):
            # Stop at heading, empty line before non-bullet, or end
            if not line.strip():
                return items, start_idx + sum(len(l) + 1 for l in lines[:i])
            
            if line.startswith('##') or line.startswith('#'):
                return items, start_idx + sum(len(l) + 1 for l in lines[:i])
            
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                # Remove bullet marker and clean up
                item = re.sub(r'^[\s]*[-*]\s*', '', line)
                # Remove checkbox notation if present
                item = re.sub(r'\s*-\s*\[[x ]\]\s*', '', item).strip()
                if item:
                    items.append(item)
            elif items:
                # Non-bullet line after bullets started - stop
                return items, start_idx + sum(len(l) + 1 for l in lines[:i])
        
        return items, start_idx + sum(len(l) + 1 for l in lines)
    
    def _parse_markdown_sections(self, content: str) -> Dict[str, Any]:
        """
        Parse markdown content into sections matching the schema
        
        Uses flexible section matching based on heading levels and keywords
        """
        sections = {}
        content_lower = content.lower()
        
        # Try to extract common sections
        # This is flexible - allow missing sections, ignore unknown sections
        
        # Security section
        if 'security' in content_lower:
            sections['security'] = self._extract_section_content(content, 'security')
        
        # Scalability section
        if 'scalability' in content_lower or 'performance' in content_lower:
            sections['scalability'] = self._extract_section_content(content, 'scalability|performance')
        
        # Reliability section
        if 'reliability' in content_lower or 'resilience' in content_lower:
            sections['reliability'] = self._extract_section_content(content, 'reliability|resilience')
        
        # Data Architecture section
        if 'data' in content_lower:
            sections['data_architecture'] = self._extract_section_content(content, 'data')
        
        # Cost section
        if 'cost' in content_lower:
            sections['cost'] = self._extract_section_content(content, 'cost')
        
        # Compliance section
        if 'compliance' in content_lower or 'governance' in content_lower:
            sections['compliance'] = self._extract_section_content(content, 'compliance|governance')
        
        # Risks section
        if 'risk' in content_lower:
            sections['risks'] = self._extract_risks_section(content)
        
        return sections
    
    def _extract_section_content(self, content: str, keyword_pattern: str) -> Dict[str, Any]:
        """Extract content for a specific section"""
        section_data = {}
        
        # Find section heading
        pattern = rf'#+ \s*[^\n]*({keyword_pattern})[^\n]*'
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return section_data
        
        section_start = match.end()
        
        # Find next heading at same or higher level to mark section end
        next_heading = re.search(r'\n#+\s', content[section_start:])
        section_end = section_start + next_heading.start() if next_heading else len(content)
        section_text = content[section_start:section_end]
        
        # Extract subsection content as key-value pairs
        subsections = re.findall(r'###\s+([^\n]+)\n(.*?)(?=###|##|$)', section_text, re.DOTALL)
        
        for subsection_name, subsection_content in subsections:
            clean_name = subsection_name.strip().lower().replace(' & ', '_').replace(' ', '_')
            # Store raw content for now - validation will parse as needed
            section_data[clean_name] = subsection_content.strip()
        
        return section_data
    
    def _extract_risks_section(self, content: str) -> List[Dict[str, str]]:
        """Extract risks as structured list"""
        risks = []
        
        pattern = r'###\s*Risk[^\n]*\n(.*?)(?=###|##|$)'
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return risks
        
        section_text = match.group(1)
        
        # Look for risk items (bullet points with description, severity, mitigation)
        risk_patterns = re.findall(
            r'-\s*\*\*([^*]+)\*\*.*?(?:severity|level):\s*([^\n]+).*?(?:mitigation|solution):\s*([^\n]+)',
            section_text,
            re.IGNORECASE | re.DOTALL
        )
        
        for desc, severity, mitigation in risk_patterns:
            risks.append({
                'description': desc.strip(),
                'severity': severity.strip(),
                'mitigation': mitigation.strip()
            })
        
        return risks
    
    def _parse_markdown(self, file_path: Path) -> ParsedSubmission:
        """Parse markdown submission"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            # Extract and validate frontmatter
            frontmatter, body = self._extract_frontmatter(content)
            
            # Validate required frontmatter fields
            required_fields = ['submission_id', 'team_name', 'submission_date', 'system_title']
            missing = [f for f in required_fields if f not in frontmatter]
            if missing:
                raise MarkdownParseError(f"Missing required frontmatter fields: {missing}")
            
            # Parse and validate submission_date
            try:
                submission_date = frontmatter['submission_date']
                if isinstance(submission_date, str):
                    parsed_date = date_parser.parse(submission_date)
                else:
                    parsed_date = submission_date
                submission_date_str = parsed_date.isoformat()
            except (ValueError, TypeError) as e:
                raise MarkdownParseError(f"Invalid submission_date format: {str(e)}")
            
            # Create metadata
            metadata = SubmissionMetadata(
                submission_id=str(frontmatter['submission_id']),
                team_name=str(frontmatter['team_name']),
                submission_date=submission_date_str,
                system_title=str(frontmatter['system_title'])
            )
            
            # Parse body sections
            sections = self._parse_markdown_sections(body)
            
            return ParsedSubmission(
                metadata=metadata,
                sections=sections,
                raw_content=content,
                file_path=file_path
            )
        
        except MarkdownParseError as e:
            raise MarkdownParseError(f"Failed to parse {file_path.name}: {str(e)}")
    
    def _parse_json(self, file_path: Path) -> ParsedSubmission:
        """Parse JSON submission"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ['submission_id', 'team_name', 'submission_date', 'system_overview', 'sections']
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required JSON fields: {missing}")
        
        # Parse and normalize submission_date
        try:
            submission_date = data['submission_date']
            if isinstance(submission_date, str):
                parsed_date = date_parser.parse(submission_date)
            else:
                parsed_date = submission_date
            submission_date_str = parsed_date.isoformat()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid submission_date format: {str(e)}")
        
        # Extract system title from system_overview
        system_title = data.get('system_overview', {}).get('title', 'Unknown')
        
        metadata = SubmissionMetadata(
            submission_id=data['submission_id'],
            team_name=data['team_name'],
            submission_date=submission_date_str,
            system_title=system_title
        )
        
        return ParsedSubmission(
            metadata=metadata,
            sections=data.get('sections', {}),
            raw_content=json.dumps(data, indent=2),
            file_path=file_path
        )
