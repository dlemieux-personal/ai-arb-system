"""
Parser for structured markdown output from AI agents.
Converts agent markdown responses back into validated Pydantic models.
"""

import re
from typing import Tuple, List, Optional, Literal
from src.schemas.agent_outputs import (
    SecurityAgentOutput,
    SecurityFinding,
    SecurityRecommendation
)


class SecurityMarkdownParseError(Exception):
    """Raised when security agent markdown cannot be parsed"""
    pass


class SecurityAgentOutputParser:
    """Parse Security Agent structured markdown output into Pydantic models"""
    
    @staticmethod
    def parse(markdown_output: str) -> SecurityAgentOutput:
        """
        Parse security agent markdown output into structured model
        
        Args:
            markdown_output: Raw markdown response from security agent
            
        Returns:
            SecurityAgentOutput with validated data
            
        Raises:
            SecurityMarkdownParseError: If parsing fails validation
        """
        try:
            findings = SecurityAgentOutputParser._extract_findings(markdown_output)
            recommendations = SecurityAgentOutputParser._extract_recommendations(markdown_output)
            score, confidence = SecurityAgentOutputParser._extract_scores(markdown_output)
            summary = SecurityAgentOutputParser._extract_summary(markdown_output)
            
            # Validate with Pydantic model
            return SecurityAgentOutput(
                findings=findings,
                recommendations=recommendations,
                security_score=score,
                confidence=confidence,
                summary=summary
            )
        
        except SecurityMarkdownParseError as e:
            raise e
        except Exception as e:
            raise SecurityMarkdownParseError(f"Failed to parse security agent output: {str(e)}")
    
    @staticmethod
    def _extract_findings(markdown: str) -> List[SecurityFinding]:
        """Extract findings from SECURITY FINDINGS section"""
        findings_section = SecurityAgentOutputParser._extract_section(
            markdown, 
            "SECURITY FINDINGS"
        )
        
        if not findings_section or findings_section.strip().lower() == "none found.":
            return []
        
        findings = []
        for line in findings_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            finding = SecurityAgentOutputParser._parse_finding_line(line)
            if finding:
                findings.append(finding)
        
        return findings
    
    @staticmethod
    def _extract_recommendations(markdown: str) -> List[SecurityRecommendation]:
        """Extract recommendations from SECURITY RECOMMENDATIONS section"""
        rec_section = SecurityAgentOutputParser._extract_section(
            markdown,
            "SECURITY RECOMMENDATIONS"
        )
        
        if not rec_section or rec_section.strip().lower() == "none - architecture is exemplary.":
            return []
        
        recommendations = []
        for line in rec_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            rec = SecurityAgentOutputParser._parse_recommendation_line(line)
            if rec:
                recommendations.append(rec)
        
        return recommendations
    
    @staticmethod
    def _extract_scores(markdown: str) -> Tuple[float, float]:
        """Extract score and confidence from SECURITY SCORE section"""
        score_section = SecurityAgentOutputParser._extract_section(
            markdown,
            "SECURITY SCORE"
        )
        
        if not score_section:
            raise SecurityMarkdownParseError("SECURITY SCORE section not found")
        
        # Extract Overall Security Score
        score_match = re.search(
            r'Overall Security Score:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not score_match:
            raise SecurityMarkdownParseError(
                "Could not extract Overall Security Score. Expected format: 'Overall Security Score: 0.XX'"
            )
        security_score = float(score_match.group(1))
        
        # Extract Confidence Level
        confidence_match = re.search(
            r'Confidence Level:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not confidence_match:
            raise SecurityMarkdownParseError(
                "Could not extract Confidence Level. Expected format: 'Confidence Level: 0.XX'"
            )
        confidence = float(confidence_match.group(1))
        
        return security_score, confidence
    
    @staticmethod
    def _extract_summary(markdown: str) -> str:
        """Extract summary from SUMMARY section"""
        summary_section = SecurityAgentOutputParser._extract_section(
            markdown,
            "SUMMARY"
        )
        return summary_section.strip() if summary_section else ""
    
    @staticmethod
    def _extract_section(markdown: str, section_name: str) -> str:
        """
        Extract content from a markdown section
        
        Args:
            markdown: Full markdown text
            section_name: Section header (without ##)
            
        Returns:
            Content between section header and next section
        """
        # Find section with case-insensitive search
        pattern = rf"##\s*{re.escape(section_name)}\s*\n(.*?)(?=##\s*\w+|$)"
        match = re.search(pattern, markdown, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return ""
        
        return match.group(1).strip()
    
    @staticmethod
    def _parse_finding_line(line: str) -> Optional[SecurityFinding]:
        """
        Parse a single finding line
        
        Format: - **[Title]**: [Description]. Severity: [level]. Affected: [Components]
        """
        # Extract title (between ** **)
        title_match = re.search(r'\*\*([^*]+)\*\*:', line)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        
        # Extract description (between **: and . Severity)
        desc_match = re.search(r'\*\*[^*]+\*\*:\s*([^.]+)\.', line)
        if not desc_match:
            return None
        description = desc_match.group(1).strip()
        
        # Extract severity
        sev_match = re.search(
            r'Severity:\s*(critical|high|medium|low)',
            line,
            re.IGNORECASE
        )
        if not sev_match:
            raise SecurityMarkdownParseError(
                f"Could not extract severity from line: {line}"
            )
        severity = sev_match.group(1).lower()
        
        # Extract affected components
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            # Split by comma and clean up
            affected_components = [c.strip() for c in components_str.split(',')]
        
        return SecurityFinding(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )
    
    @staticmethod
    def _parse_recommendation_line(line: str) -> Optional[SecurityRecommendation]:
        """
        Parse a single recommendation line
        
        Format: - **[Title]**: [Description]. Severity: [level]. Affected: [Components]
        """
        # Extract title (between ** **)
        title_match = re.search(r'\*\*([^*]+)\*\*:', line)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        
        # Extract description (between **: and . Severity)
        desc_match = re.search(r'\*\*[^*]+\*\*:\s*([^.]+)\.', line)
        if not desc_match:
            return None
        description = desc_match.group(1).strip()
        
        # Extract severity
        sev_match = re.search(
            r'Severity:\s*(critical|high|medium|low)',
            line,
            re.IGNORECASE
        )
        if not sev_match:
            raise SecurityMarkdownParseError(
                f"Could not extract severity from line: {line}"
            )
        severity = sev_match.group(1).lower()
        
        # Extract affected components
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            affected_components = [c.strip() for c in components_str.split(',')]
        
        return SecurityRecommendation(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )
