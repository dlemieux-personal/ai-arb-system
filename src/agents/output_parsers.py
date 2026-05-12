"""
Parser for structured markdown output from AI agents.
Converts agent markdown responses back into validated Pydantic models.
"""

import re
from typing import Tuple, List, Optional, Literal
from src.schemas.agent_outputs import (
    SecurityAgentOutput,
    SecurityFinding,
    SecurityRecommendation,
    ScalabilityAgentOutput,
    ScalabilityBottleneck,
    ScalabilityRecommendation,
    ReliabilityAgentOutput,
    ReliabilityFinding,
    ReliabilityFailureMode,
    ReliabilityRecommendation
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


class ScalabilityMarkdownParseError(Exception):
    """Raised when scalability agent markdown cannot be parsed"""
    pass


class ScalabilityAgentOutputParser:
    """Parse Scalability Agent structured markdown output into Pydantic models"""
    
    @staticmethod
    def parse(markdown_output: str) -> ScalabilityAgentOutput:
        """
        Parse scalability agent markdown output into structured model
        
        Args:
            markdown_output: Raw markdown response from scalability agent
            
        Returns:
            ScalabilityAgentOutput with validated data
            
        Raises:
            ScalabilityMarkdownParseError: If parsing fails validation
        """
        try:
            bottlenecks = ScalabilityAgentOutputParser._extract_bottlenecks(markdown_output)
            recommendations = ScalabilityAgentOutputParser._extract_recommendations(markdown_output)
            score, confidence = ScalabilityAgentOutputParser._extract_scores(markdown_output)
            summary = ScalabilityAgentOutputParser._extract_summary(markdown_output)
            
            # Validate with Pydantic model
            return ScalabilityAgentOutput(
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                scalability_score=score,
                confidence=confidence,
                summary=summary
            )
        
        except ScalabilityMarkdownParseError as e:
            raise e
        except Exception as e:
            raise ScalabilityMarkdownParseError(f"Failed to parse scalability agent output: {str(e)}")
    
    @staticmethod
    def _extract_bottlenecks(markdown: str) -> List[ScalabilityBottleneck]:
        """Extract bottlenecks from SCALABILITY BOTTLENECKS section"""
        bottlenecks_section = ScalabilityAgentOutputParser._extract_section(
            markdown, 
            "SCALABILITY BOTTLENECKS"
        )
        
        if not bottlenecks_section or bottlenecks_section.strip().lower() == "none identified.":
            return []
        
        bottlenecks = []
        for line in bottlenecks_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            bottleneck = ScalabilityAgentOutputParser._parse_bottleneck_line(line)
            if bottleneck:
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    @staticmethod
    def _extract_recommendations(markdown: str) -> List[ScalabilityRecommendation]:
        """Extract recommendations from SCALABILITY RECOMMENDATIONS section"""
        rec_section = ScalabilityAgentOutputParser._extract_section(
            markdown,
            "SCALABILITY RECOMMENDATIONS"
        )
        
        if not rec_section or rec_section.strip().lower() == "none - architecture scales well.":
            return []
        
        recommendations = []
        for line in rec_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            rec = ScalabilityAgentOutputParser._parse_recommendation_line(line)
            if rec:
                recommendations.append(rec)
        
        return recommendations
    
    @staticmethod
    def _extract_scores(markdown: str) -> Tuple[float, float]:
        """Extract score and confidence from SCALABILITY SCORE section"""
        score_section = ScalabilityAgentOutputParser._extract_section(
            markdown,
            "SCALABILITY SCORE"
        )
        
        if not score_section:
            raise ScalabilityMarkdownParseError("SCALABILITY SCORE section not found")
        
        # Extract Overall Scalability Score
        score_match = re.search(
            r'Overall Scalability Score:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not score_match:
            raise ScalabilityMarkdownParseError(
                "Could not extract Overall Scalability Score. Expected format: 'Overall Scalability Score: 0.XX'"
            )
        scalability_score = float(score_match.group(1))
        
        # Extract Confidence Level
        confidence_match = re.search(
            r'Confidence Level:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not confidence_match:
            raise ScalabilityMarkdownParseError(
                "Could not extract Confidence Level. Expected format: 'Confidence Level: 0.XX'"
            )
        confidence = float(confidence_match.group(1))
        
        return scalability_score, confidence
    
    @staticmethod
    def _extract_summary(markdown: str) -> str:
        """Extract summary from SUMMARY section"""
        summary_section = ScalabilityAgentOutputParser._extract_section(
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
    def _parse_bottleneck_line(line: str) -> Optional[ScalabilityBottleneck]:
        """
        Parse a single bottleneck line
        
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
            raise ScalabilityMarkdownParseError(
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
        
        return ScalabilityBottleneck(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )
    
    @staticmethod
    def _parse_recommendation_line(line: str) -> Optional[ScalabilityRecommendation]:
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
            raise ScalabilityMarkdownParseError(
                f"Could not extract severity from line: {line}"
            )
        severity = sev_match.group(1).lower()
        
        # Extract affected components
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            affected_components = [c.strip() for c in components_str.split(',')]
        
        return ScalabilityRecommendation(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )


class ReliabilityMarkdownParseError(Exception):
    """Raised when reliability agent markdown cannot be parsed"""
    pass


class ReliabilityAgentOutputParser:
    """Parse Reliability Agent structured markdown output into Pydantic models"""

    @staticmethod
    def parse(markdown_output: str) -> ReliabilityAgentOutput:
        """
        Parse reliability agent markdown output into structured model
        
        Args:
            markdown_output: Raw markdown response from reliability agent
            
        Returns:
            ReliabilityAgentOutput with validated data
            
        Raises:
            ReliabilityMarkdownParseError: If parsing fails validation
        """
        try:
            findings = ReliabilityAgentOutputParser._extract_findings(markdown_output)
            failure_modes = ReliabilityAgentOutputParser._extract_failure_modes(markdown_output)
            recommendations = ReliabilityAgentOutputParser._extract_recommendations(markdown_output)
            score, confidence = ReliabilityAgentOutputParser._extract_scores(markdown_output)
            summary = ReliabilityAgentOutputParser._extract_summary(markdown_output)
            
            return ReliabilityAgentOutput(
                findings=findings,
                failure_modes=failure_modes,
                recommendations=recommendations,
                reliability_score=score,
                confidence=confidence,
                summary=summary
            )
        except ReliabilityMarkdownParseError as e:
            raise e
        except Exception as e:
            raise ReliabilityMarkdownParseError(f"Failed to parse reliability agent output: {str(e)}")

    @staticmethod
    def _extract_findings(markdown: str) -> List[ReliabilityFinding]:
        findings_section = ReliabilityAgentOutputParser._extract_section(markdown, "RELIABILITY FINDINGS")
        if not findings_section or findings_section.strip().lower() == "none found.":
            return []
        findings = []
        for line in findings_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            finding = ReliabilityAgentOutputParser._parse_finding_line(line)
            if finding:
                findings.append(finding)
        return findings

    @staticmethod
    def _extract_failure_modes(markdown: str) -> List[ReliabilityFailureMode]:
        failure_modes_section = ReliabilityAgentOutputParser._extract_section(markdown, "FAILURE MODES")
        if not failure_modes_section or failure_modes_section.strip().lower() == "none identified.":
            return []
        failure_modes = []
        for line in failure_modes_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            failure_mode = ReliabilityAgentOutputParser._parse_failure_mode_line(line)
            if failure_mode:
                failure_modes.append(failure_mode)
        return failure_modes

    @staticmethod
    def _extract_recommendations(markdown: str) -> List[ReliabilityRecommendation]:
        rec_section = ReliabilityAgentOutputParser._extract_section(markdown, "RELIABILITY RECOMMENDATIONS")
        if not rec_section or rec_section.strip().lower() == "none - architecture is resilient." :
            return []
        recommendations = []
        for line in rec_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            rec = ReliabilityAgentOutputParser._parse_recommendation_line(line)
            if rec:
                recommendations.append(rec)
        return recommendations

    @staticmethod
    def _extract_scores(markdown: str) -> Tuple[float, float]:
        score_section = ReliabilityAgentOutputParser._extract_section(markdown, "RELIABILITY SCORE")
        if not score_section:
            raise ReliabilityMarkdownParseError("RELIABILITY SCORE section not found")
        score_match = re.search(
            r'Overall Reliability Score:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not score_match:
            raise ReliabilityMarkdownParseError(
                "Could not extract Overall Reliability Score. Expected format: 'Overall Reliability Score: 0.XX'"
            )
        reliability_score = float(score_match.group(1))
        confidence_match = re.search(
            r'Confidence Level:\s*(0\.\d{2}|1\.00)',
            score_section
        )
        if not confidence_match:
            raise ReliabilityMarkdownParseError(
                "Could not extract Confidence Level. Expected format: 'Confidence Level: 0.XX'"
            )
        confidence = float(confidence_match.group(1))
        return reliability_score, confidence

    @staticmethod
    def _extract_summary(markdown: str) -> str:
        summary_section = ReliabilityAgentOutputParser._extract_section(markdown, "SUMMARY")
        return summary_section.strip() if summary_section else ""

    @staticmethod
    def _extract_section(markdown: str, section_name: str) -> str:
        pattern = rf"##\s*{re.escape(section_name)}\s*\n(.*?)(?=##\s*\w+|$)"
        match = re.search(pattern, markdown, re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return match.group(1).strip()

    @staticmethod
    def _parse_finding_line(line: str) -> Optional[ReliabilityFinding]:
        title_match = re.search(r'\*\*([^*]+)\*\*:', line)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        desc_match = re.search(r'\*\*[^*]+\*\*:\s*([^.]+)\.', line)
        if not desc_match:
            return None
        description = desc_match.group(1).strip()
        sev_match = re.search(
            r'Severity:\s*(critical|high|medium|low)',
            line,
            re.IGNORECASE
        )
        if not sev_match:
            raise ReliabilityMarkdownParseError(
                f"Could not extract severity from line: {line}"
            )
        severity = sev_match.group(1).lower()
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            affected_components = [c.strip() for c in components_str.split(',')]
        return ReliabilityFinding(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )

    @staticmethod
    def _parse_failure_mode_line(line: str) -> Optional[ReliabilityFailureMode]:
        title_match = re.search(r'\*\*([^*]+)\*\*:', line)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        desc_match = re.search(r'\*\*[^*]+\*\*:\s*([^\.]+)\.', line)
        if not desc_match:
            return None
        description = desc_match.group(1).strip()
        impact_match = re.search(
            r'Impact:\s*([^\.]+)\.',
            line,
            re.IGNORECASE
        )
        if not impact_match:
            raise ReliabilityMarkdownParseError(
                f"Could not extract impact from line: {line}"
            )
        impact = impact_match.group(1).strip()
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            affected_components = [c.strip() for c in components_str.split(',')]
        return ReliabilityFailureMode(
            title=title,
            description=description,
            impact=impact,
            affected_components=affected_components
        )

    @staticmethod
    def _parse_recommendation_line(line: str) -> Optional[ReliabilityRecommendation]:
        title_match = re.search(r'\*\*([^*]+)\*\*:', line)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        desc_match = re.search(r'\*\*[^*]+\*\*:\s*([^.]+)\.', line)
        if not desc_match:
            return None
        description = desc_match.group(1).strip()
        sev_match = re.search(
            r'Severity:\s*(critical|high|medium|low)',
            line,
            re.IGNORECASE
        )
        if not sev_match:
            raise ReliabilityMarkdownParseError(
                f"Could not extract severity from line: {line}"
            )
        severity = sev_match.group(1).lower()
        affected_match = re.search(r'Affected:\s*([^$\n]+)', line)
        affected_components = []
        if affected_match:
            components_str = affected_match.group(1).strip()
            affected_components = [c.strip() for c in components_str.split(',')]
        return ReliabilityRecommendation(
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components
        )
