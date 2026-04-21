"""
Tests for CrewBuilder task output parsing integration
"""

import pytest
from src.orchestration.crew_builder import CrewBuilder
from src.schemas.agent_outputs import SecurityAgentOutput


SAMPLE_CREW_OUTPUT = """## SECURITY FINDINGS

- **Missing network segmentation**: Database is directly exposed to public internet. Severity: critical. Affected: Database Layer, Network

## SECURITY RECOMMENDATIONS

- **Implement VPC and security groups**: Place database in private subnet. Severity: critical. Affected: Network Infrastructure

## SECURITY SCORE

Overall Security Score: 0.45
Confidence Level: 0.92

## SUMMARY

Critical security exposure in network architecture that requires immediate remediation.
"""


class TestCrewBuilderParsing:
    """Test CrewBuilder parsing methods"""
    
    def test_parse_security_agent_output(self):
        """Test parsing security agent output through CrewBuilder"""
        builder = CrewBuilder()
        result = builder.parse_security_agent_output(SAMPLE_CREW_OUTPUT)
        
        assert result.is_valid()
        assert result.parsed_output.security_score == 0.45
        assert len(result.parsed_output.findings) == 1
        assert len(result.parsed_output.recommendations) == 1
    
    def test_extract_section_from_crew_output(self):
        """Test extracting a markdown section from crew output"""
        crew_output = """
Some header text

## SECURITY FINDINGS

- **Issue**: Description. Severity: high. Affected: Component

## SCALABILITY FINDINGS

- **Bottleneck**: Description. Severity: medium. Affected: Service

End of output
"""
        
        security_section = CrewBuilder._extract_section_from_crew_output(
            crew_output, 
            'security'
        )
        
        assert security_section is not None
        assert 'SECURITY' in security_section
        assert 'Issue' in security_section
        assert 'Bottleneck' not in security_section  # Different section
    
    def test_extract_section_case_insensitive(self):
        """Test section extraction is case-insensitive"""
        crew_output = """## security FINDINGS
- **Issue**: Description. Severity: low. Affected: Component"""
        
        section = CrewBuilder._extract_section_from_crew_output(crew_output, 'security')
        
        assert section is not None
        assert 'Issue' in section
    
    def test_extract_section_not_found(self):
        """Test extraction returns None if section not found"""
        crew_output = "This output has no security section"
        
        section = CrewBuilder._extract_section_from_crew_output(crew_output, 'security')
        
        assert section is None
    
    def test_extract_and_parse_with_security_section(self):
        """Test extracting and parsing when security section is present"""
        # Don't build agents - just test the parsing logic
        crew_output = f"""
Crew execution completed.

{SAMPLE_CREW_OUTPUT}

End of execution.
"""
        
        # Test the extraction logic directly
        section = CrewBuilder._extract_section_from_crew_output(crew_output, 'security')
        assert section is not None
        assert 'SECURITY' in section


class TestMarketSectionExtraction:
    """Test markdown section extraction logic"""
    
    def test_extract_finds_section_with_various_headers(self):
        """Test extraction with different header formats"""
        test_cases = [
            ("## SECURITY FINDINGS\nContent", True),
            ("### Security Findings\nContent", True),
            ("# SECURITY FINDINGS\nContent", True),
            ("## security findings\nContent", True),
            ("No findings section", False),
        ]
        
        for output, should_find in test_cases:
            result = CrewBuilder._extract_section_from_crew_output(output, "security")
            if should_find:
                assert result is not None, f"Failed to extract from: {output}"
            else:
                assert result is None, f"Should not extract from: {output}"


class TestTaskOutputDocumentation:
    """Test that TaskOutput provides good error messages"""
    
    def test_error_message_contains_agent_name(self):
        """Test that error messages include agent name"""
        from src.orchestration.task_output import TaskOutput
        
        output = TaskOutput[SecurityAgentOutput](
            agent_name="My Security Agent",
            raw_output="test",
            parsing_successful=False,
            parsing_error="Custom error"
        )
        
        with pytest.raises(ValueError) as exc_info:
            output.get_parsed_or_raise()
        
        assert "My Security Agent" in str(exc_info.value)
        assert "Custom error" in str(exc_info.value)
