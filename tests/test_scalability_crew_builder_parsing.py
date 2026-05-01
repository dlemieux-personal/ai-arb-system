"""
Tests for CrewBuilder scalability agent output parsing integration
"""

import pytest
from src.orchestration.crew_builder import CrewBuilder
from src.schemas.agent_outputs import ScalabilityAgentOutput


SAMPLE_SCALABILITY_OUTPUT = """## SCALABILITY BOTTLENECKS

- **Database connection pool exhaustion**: Pool of 100 connections insufficient for 150 peak requests per second. Severity: critical. Affected: Database, Connection Pool Manager

## SCALABILITY RECOMMENDATIONS

- **Implement PgBouncer connection pooling**: Deploy connection pooler to handle 10x concurrent connections. Severity: critical. Affected: Database, Connection Pool Manager

## SCALABILITY SCORE

Overall Scalability Score: 0.52
Confidence Level: 0.89

## SUMMARY

Critical database bottleneck prevents scaling beyond current capacity. Connection pooling implementation should be immediate priority.
"""


class TestCrewBuilderScalabilityParsing:
    """Test CrewBuilder scalability parsing methods"""
    
    def test_parse_scalability_agent_output(self):
        """Test parsing scalability agent output through CrewBuilder"""
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(SAMPLE_SCALABILITY_OUTPUT)
        
        assert result.is_valid()
        assert result.parsed_output.scalability_score == 0.52
        assert result.parsed_output.confidence == 0.89
        assert len(result.parsed_output.bottlenecks) == 1
        assert len(result.parsed_output.recommendations) == 1
    
    def test_scalability_output_has_correct_type(self):
        """Test that scalability output is correct type"""
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(SAMPLE_SCALABILITY_OUTPUT)
        
        assert isinstance(result.parsed_output, ScalabilityAgentOutput)
    
    def test_scalability_parser_accessible_via_crew_builder(self):
        """Test that CrewBuilder has parse_scalability_agent_output method"""
        builder = CrewBuilder()
        
        assert hasattr(builder, 'parse_scalability_agent_output')
        assert callable(builder.parse_scalability_agent_output)
    
    def test_extract_section_for_scalability(self):
        """Test extracting scalability section from crew output"""
        crew_output = """
Execution Progress:

## SCALABILITY BOTTLENECKS

- **Issue**: Description. Severity: high. Affected: Component

## OTHER SECTION

- **Item**: Description. Severity: medium. Affected: Service

End
"""
        
        scalability_section = CrewBuilder._extract_section_from_crew_output(
            crew_output, 
            'scalability'
        )
        
        assert scalability_section is not None
        assert 'SCALABILITY' in scalability_section
        assert 'Issue' in scalability_section
        assert 'OTHER' not in scalability_section
    
    def test_both_security_and_scalability_extraction(self):
        """Test extracting both security and scalability sections"""
        crew_output = """
Review Results:

## SECURITY FINDINGS
- **Issue1**: Desc. Severity: high. Affected: Network

## SCALABILITY BOTTLENECKS
- **Issue2**: Desc. Severity: critical. Affected: Database

## SUMMARY
Done
"""
        
        security = CrewBuilder._extract_section_from_crew_output(crew_output, 'security')
        scalability = CrewBuilder._extract_section_from_crew_output(crew_output, 'scalability')
        
        assert security is not None
        assert scalability is not None
        assert 'Issue1' in security
        assert 'Issue2' in scalability
        assert 'Issue1' not in scalability
        assert 'Issue2' not in security


class TestScalabilityTaskOutputIntegration:
    """Integration tests for scalability output through CrewBuilder"""
    
    def test_full_scalability_parsing_workflow(self):
        """Test complete scalability workflow: parse, validate scalability output"""
        builder = CrewBuilder()
        
        # Use the sample output directly (section extraction is tested separately)
        agent_output = SAMPLE_SCALABILITY_OUTPUT
        
        # Parse through builder
        result = builder.parse_scalability_agent_output(agent_output)
        
        # Validate
        assert result.is_valid()
        assert result.parsed_output.scalability_score == 0.52
        assert len(result.parsed_output.bottlenecks) == 1
    
    def test_scalability_output_error_handling(self):
        """Test error handling for invalid scalability output"""
        builder = CrewBuilder()
        
        bad_output = """
## SCALABILITY BOTTLENECKS

Incomplete output
"""
        
        result = builder.parse_scalability_agent_output(bad_output)
        assert not result.is_valid()
        assert result.parsing_error is not None
    
    def test_parser_preserves_raw_output(self):
        """Test that raw output is preserved during parsing"""
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(SAMPLE_SCALABILITY_OUTPUT)
        
        assert result.raw_output == SAMPLE_SCALABILITY_OUTPUT
    
    def test_bottleneck_details_extracted(self):
        """Test that bottleneck details are correctly extracted"""
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(SAMPLE_SCALABILITY_OUTPUT)
        
        bottleneck = result.parsed_output.bottlenecks[0]
        assert "connection pool" in bottleneck.title.lower()
        assert bottleneck.severity == "critical"
        assert "Database" in bottleneck.affected_components
        assert "Connection Pool Manager" in bottleneck.affected_components
    
    def test_recommendation_details_extracted(self):
        """Test that recommendation details are correctly extracted"""
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(SAMPLE_SCALABILITY_OUTPUT)
        
        rec = result.parsed_output.recommendations[0]
        assert "pgbouncer" in rec.title.lower()
        assert rec.severity == "critical"
        assert "Database" in rec.affected_components


class TestScalabilityCrewBuilderConsistency:
    """Test consistency between security and scalability parsing"""
    
    def test_both_agents_use_same_executor_pattern(self):
        """Test that both parsing methods follow same executor pattern"""
        builder = CrewBuilder()
        
        # Both methods should exist
        assert hasattr(builder, 'parse_security_agent_output')
        assert hasattr(builder, 'parse_scalability_agent_output')
        
        # Both should return TaskOutput
        from src.orchestration.task_output import TaskOutput
        
        security_result = builder.parse_security_agent_output(
            "## SECURITY FINDINGS\n\nNone found.\n\n## SECURITY RECOMMENDATIONS\n\nNone\n\n## SECURITY SCORE\n\nOverall Security Score: 0.50\n\nConfidence Level: 0.50\n\n## SUMMARY\n\nTest"
        )
        scalability_result = builder.parse_scalability_agent_output(
            "## SCALABILITY BOTTLENECKS\n\nNone identified.\n\n## SCALABILITY RECOMMENDATIONS\n\nNone\n\n## SCALABILITY SCORE\n\nOverall Scalability Score: 0.50\n\nConfidence Level: 0.50\n\n## SUMMARY\n\nTest"
        )
        
        assert isinstance(security_result, TaskOutput)
        assert isinstance(scalability_result, TaskOutput)
    
    def test_retry_logic_consistent(self):
        """Test that retry logic is same for both agents"""
        from src.orchestration.task_output import (
            SecurityAgentTaskExecutor,
            ScalabilityAgentTaskExecutor
        )
        
        # Both should have same max retries
        assert (ScalabilityAgentTaskExecutor.MAX_PARSE_RETRIES ==
                SecurityAgentTaskExecutor.MAX_PARSE_RETRIES)
    
    def test_error_message_consistency(self):
        """Test that error messages follow same pattern"""
        builder = CrewBuilder()
        
        bad_security = "No valid format"
        bad_scalability = "No valid format"
        
        security_result = builder.parse_security_agent_output(bad_security)
        scalability_result = builder.parse_scalability_agent_output(bad_scalability)
        
        # Both should have error messages
        assert security_result.parsing_error is not None
        assert scalability_result.parsing_error is not None


class TestScalabilityExtendedOutputs:
    """Test with various scalability output formats"""
    
    def test_multiple_bottlenecks_parsing(self):
        """Test parsing output with multiple bottlenecks"""
        output = """## SCALABILITY BOTTLENECKS

- **Bottleneck 1**: Description 1. Severity: critical. Affected: Component A
- **Bottleneck 2**: Description 2. Severity: high. Affected: Component B, Component C
- **Bottleneck 3**: Description 3. Severity: medium. Affected: Component D

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.45

Confidence Level: 0.80

## SUMMARY

Multiple scaling issues identified."""
        
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(output)
        
        assert result.is_valid()
        assert len(result.parsed_output.bottlenecks) == 3
        assert result.parsed_output.bottlenecks[0].severity == "critical"
        assert result.parsed_output.bottlenecks[1].severity == "high"
        assert result.parsed_output.bottlenecks[2].severity == "medium"
    
    def test_multiple_recommendations_parsing(self):
        """Test parsing output with multiple recommendations"""
        output = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

- **Rec 1**: Description 1. Severity: critical. Affected: A
- **Rec 2**: Description 2. Severity: high. Affected: B
- **Rec 3**: Description 3. Severity: medium. Affected: C, D

## SCALABILITY SCORE

Overall Scalability Score: 0.75

Confidence Level: 0.85

## SUMMARY

Good potential with improvements."""
        
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(output)
        
        assert result.is_valid()
        assert len(result.parsed_output.recommendations) == 3
    
    def test_no_bottlenecks_identified(self):
        """Test output indicating no bottlenecks found"""
        output = """## SCALABILITY BOTTLENECKS

None identified.

## SCALABILITY RECOMMENDATIONS

- **Optimization 1**: Consider caching strategy. Severity: low. Affected: Cache Layer

## SCALABILITY SCORE

Overall Scalability Score: 0.92

Confidence Level: 0.88

## SUMMARY

Architecture scales well with minor optimizations available."""
        
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(output)
        
        assert result.is_valid()
        assert len(result.parsed_output.bottlenecks) == 0
        assert len(result.parsed_output.recommendations) == 1
    
    def test_no_recommendations_needed(self):
        """Test output where no recommendations are needed"""
        output = """## SCALABILITY BOTTLENECKS

- **Minor issue**: Not critical. Severity: low. Affected: Analytics

## SCALABILITY RECOMMENDATIONS

None - architecture scales well.

## SCALABILITY SCORE

Overall Scalability Score: 0.95

Confidence Level: 0.90

## SUMMARY

Excellent scalability design with no immediate action needed."""
        
        builder = CrewBuilder()
        result = builder.parse_scalability_agent_output(output)
        
        assert result.is_valid()
        assert len(result.parsed_output.bottlenecks) == 1
        assert len(result.parsed_output.recommendations) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
