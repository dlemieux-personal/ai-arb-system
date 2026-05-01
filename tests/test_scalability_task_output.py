"""
Tests for task output wrapper and scalability agent execution
"""

import pytest
from src.orchestration.task_output import ScalabilityAgentTaskExecutor, TaskOutput
from src.schemas.agent_outputs import ScalabilityAgentOutput, ScalabilityBottleneck


VALID_SCALABILITY_OUTPUT = """## SCALABILITY BOTTLENECKS

- **Database connection pool exhaustion**: Current pool cannot handle peak load concurrency. Severity: critical. Affected: Database, Connection Pool Manager
- **Lack of horizontal scaling for stateful API**: In-memory sessions prevent scaling. Severity: high. Affected: API Gateway, Session Management

## SCALABILITY RECOMMENDATIONS

- **Implement connection pooling**: Deploy PgBouncer for connection multiplexing. Severity: critical. Affected: Database, Connection Pool Manager
- **Externalize session state**: Use distributed Redis for sessions. Severity: high. Affected: API Tier, Session Storage

## SCALABILITY SCORE

Overall Scalability Score: 0.52
Confidence Level: 0.88

## SUMMARY

Architecture has critical database bottleneck and session state issues limiting horizontal scaling. Connection pooling and session externalization are immediate priorities.
"""


class TestTaskOutputScalability:
    """Test the TaskOutput container for scalability results"""
    
    def test_valid_task_output_scalability(self):
        """Test creating a valid task output for scalability"""
        output = TaskOutput[ScalabilityAgentOutput](
            agent_name="Scalability Agent",
            raw_output="test",
            parsed_output=ScalabilityAgentOutput(
                scalability_score=0.75,
                confidence=0.85,
                bottlenecks=[],
                recommendations=[]
            ),
            parsing_successful=True
        )
        
        assert output.is_valid()
        assert output.agent_name == "Scalability Agent"
        assert output.parsed_output.scalability_score == 0.75
    
    def test_invalid_task_output_scalability(self):
        """Test that get_parsed_or_raise raises on invalid scalability output"""
        output = TaskOutput[ScalabilityAgentOutput](
            agent_name="Scalability Agent",
            raw_output="test",
            parsing_successful=False,
            parsing_error="Parse failed"
        )
        
        assert not output.is_valid()
        
        with pytest.raises(ValueError) as exc_info:
            output.get_parsed_or_raise()
        
        assert "could not be parsed" in str(exc_info.value)
    
    def test_task_output_without_parsed_content_scalability(self):
        """Test task output with raw output only (scalability)"""
        output = TaskOutput[ScalabilityAgentOutput](
            agent_name="Test Agent",
            raw_output="some raw text",
            parsing_successful=False,
            parsing_error="Failed to parse"
        )
        
        assert not output.is_valid()
        assert output.raw_output == "some raw text"
        assert output.parsing_error == "Failed to parse"


class TestScalabilityAgentTaskExecutor:
    """Test the scalability agent task executor"""
    
    def test_execute_and_parse_valid_output(self):
        """Test executing and parsing valid scalability agent output"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        
        assert result.is_valid()
        assert result.parsing_successful
        assert result.parsing_attempts == 1
        assert result.parsed_output is not None
        assert isinstance(result.parsed_output, ScalabilityAgentOutput)
        assert result.parsed_output.scalability_score == 0.52
        assert result.parsed_output.confidence == 0.88
        assert len(result.parsed_output.bottlenecks) == 2
        assert len(result.parsed_output.recommendations) == 2
    
    def test_agent_name_in_output_scalability(self):
        """Test that custom agent name is stored (scalability)"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(
            VALID_SCALABILITY_OUTPUT,
            agent_name="Custom Scalability Agent"
        )
        
        assert result.agent_name == "Custom Scalability Agent"
    
    def test_parse_failure_with_error_message_scalability(self):
        """Test scalability parsing failure captures error message"""
        bad_output = """## SCALABILITY BOTTLENECKS

None identified.

## SCALABILITY SCORE

This is not the right format
"""
        
        result = ScalabilityAgentTaskExecutor.execute_and_parse(bad_output)
        
        assert not result.is_valid()
        assert result.parsing_successful is False
        assert result.parsing_error is not None
        assert len(result.parsing_error) > 0
    
    def test_raw_output_preserved_scalability(self):
        """Test that raw output is always preserved (scalability)"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        
        assert result.raw_output == VALID_SCALABILITY_OUTPUT
    
    def test_retry_attempts_tracked_scalability(self):
        """Test that retry attempts are tracked (scalability)"""
        bad_output = "This will fail definitely"
        
        result = ScalabilityAgentTaskExecutor.execute_and_parse(bad_output)
        
        # Should have tried MAX_PARSE_RETRIES + 1 times
        assert result.parsing_attempts == ScalabilityAgentTaskExecutor.MAX_PARSE_RETRIES + 1
        assert not result.parsing_successful
    
    def test_bottleneck_parsing_accuracy(self):
        """Test that bottlenecks are parsed with correct details"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        
        assert result.is_valid()
        
        # Check first bottleneck
        bottleneck = result.parsed_output.bottlenecks[0]
        assert "connection pool" in bottleneck.title.lower()
        assert bottleneck.severity == "critical"
        assert "Database" in bottleneck.affected_components
        assert "Connection Pool Manager" in bottleneck.affected_components
    
    def test_recommendation_parsing_accuracy(self):
        """Test that recommendations are parsed with correct details"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        
        assert result.is_valid()
        
        # Check first recommendation
        rec = result.parsed_output.recommendations[0]
        assert "connection pooling" in rec.title.lower()
        assert rec.severity == "critical"
        assert "Database" in rec.affected_components


class TestScalabilityAgentTaskExecutorValidation:
    """Test validation of parsed scalability agent output"""
    
    def test_validate_valid_output_scalability(self):
        """Test validation of valid scalability output"""
        output = ScalabilityAgentOutput(
            bottlenecks=[
                ScalabilityBottleneck(
                    title="Test",
                    description="Test description",
                    severity="high",
                    affected_components=["Component"]
                )
            ],
            scalability_score=0.75,
            confidence=0.85
        )
        
        is_valid, error = ScalabilityAgentTaskExecutor.validate_output(output)
        assert is_valid
        assert error == ""
    
    def test_validate_score_outside_range_scalability(self):
        """Test Pydantic validation rejects scores outside 0.0-1.0 (scalability)"""
        from pydantic import ValidationError
        
        # Pydantic validates on instantiation
        with pytest.raises(ValidationError):
            ScalabilityAgentOutput(
                scalability_score=1.5,  # Invalid: > 1.0
                confidence=0.85,
                bottlenecks=[
                    ScalabilityBottleneck(
                        title="Test",
                        description="Test",
                        severity="high",
                        affected_components=[]
                    )
                ]
            )
    
    def test_validate_confidence_outside_range_scalability(self):
        """Test Pydantic validation rejects confidence outside 0.0-1.0 (scalability)"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ScalabilityAgentOutput(
                scalability_score=0.75,
                confidence=-0.1,  # Invalid: < 0.0
                bottlenecks=[
                    ScalabilityBottleneck(
                        title="Test",
                        description="Test",
                        severity="high",
                        affected_components=[]
                    )
                ]
            )
    
    def test_validate_empty_bottlenecks_and_recommendations(self):
        """Test validation requires at least bottlenecks or recommendations"""
        output = ScalabilityAgentOutput(
            bottlenecks=[],
            recommendations=[],
            scalability_score=0.75,
            confidence=0.85
        )
        
        is_valid, error = ScalabilityAgentTaskExecutor.validate_output(output)
        assert not is_valid
        assert "must contain at least" in error.lower()
    
    def test_validate_severity_enum_enforcement_scalability(self):
        """Test Pydantic validation enforces valid severity values (scalability)"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ScalabilityBottleneck(
                title="Test",
                description="Test",
                severity="unknown",  # Invalid enum value
                affected_components=[]
            )
    
    def test_validate_valid_all_severity_levels_scalability(self):
        """Test all valid severity levels are accepted (scalability)"""
        for severity in ["critical", "high", "medium", "low"]:
            bottleneck = ScalabilityBottleneck(
                title="Test",
                description="Test",
                severity=severity,
                affected_components=[]
            )
            assert bottleneck.severity == severity
    
    def test_validate_multiple_severity_issues(self):
        """Test validation catches multiple severity issues"""
        from pydantic import ValidationError
        
        # Pydantic validates on instantiation, so expect ValidationError
        with pytest.raises(ValidationError):
            ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=1.5,  # Invalid
                confidence=1.5  # Invalid
            )


class TestTaskOutputIntegrationScalability:
    """Integration tests for task output with scalability parsing"""
    
    def test_full_workflow_scalability(self):
        """Test complete scalability workflow: parse, validate, store"""
        # 1. Agent produces output
        agent_output = VALID_SCALABILITY_OUTPUT
        
        # 2. Execute and parse
        result = ScalabilityAgentTaskExecutor.execute_and_parse(agent_output)
        
        # 3. Check parsing succeeded
        assert result.is_valid()
        
        # 4. Validate result
        is_valid, error = ScalabilityAgentTaskExecutor.validate_output(result.parsed_output)
        assert is_valid
        
        # 5. Use the result
        assert result.parsed_output.scalability_score == 0.52
        assert len(result.parsed_output.bottlenecks) == 2
        assert len(result.parsed_output.recommendations) == 2
    
    def test_multiple_parse_attempts_on_failure(self):
        """Test that parser retries on initial failure"""
        bad_output = "Incomplete output"
        
        result = ScalabilityAgentTaskExecutor.execute_and_parse(bad_output)
        
        # Should have made 3 total attempts (initial + 2 retries)
        assert result.parsing_attempts == 3
        assert not result.is_valid()
    
    def test_successful_parse_stops_retries(self):
        """Test that retries stop after successful parse"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        
        # Should have succeeded on first attempt
        assert result.parsing_attempts == 1
        assert result.is_valid()
    
    def test_empty_lists_valid_output(self):
        """Test that output with empty lists is still valid if at least one field is present"""
        output_with_recommendations_only = """## SCALABILITY BOTTLENECKS

None identified.

## SCALABILITY RECOMMENDATIONS

- **Add caching**: Implement Redis for performance. Severity: medium. Affected: Cache Layer

## SCALABILITY SCORE

Overall Scalability Score: 0.80

Confidence Level: 0.85

## SUMMARY

Good scalability with minor optimizations available."""
        
        result = ScalabilityAgentTaskExecutor.execute_and_parse(output_with_recommendations_only)
        assert result.is_valid()
        assert len(result.parsed_output.bottlenecks) == 0
        assert len(result.parsed_output.recommendations) == 1


class TestScalabilityVsSecurityPatterns:
    """Tests to verify scalability and security agents follow same pattern"""
    
    def test_executor_has_same_max_retries(self):
        """Both agents should have same MAX_PARSE_RETRIES"""
        from src.orchestration.task_output import SecurityAgentTaskExecutor
        
        assert (ScalabilityAgentTaskExecutor.MAX_PARSE_RETRIES == 
                SecurityAgentTaskExecutor.MAX_PARSE_RETRIES)
    
    def test_both_executors_return_task_output(self):
        """Both executors should return TaskOutput objects"""
        result = ScalabilityAgentTaskExecutor.execute_and_parse(VALID_SCALABILITY_OUTPUT)
        assert isinstance(result, TaskOutput)
    
    def test_validation_method_exists_for_both(self):
        """Both executors should have validate_output method"""
        from src.orchestration.task_output import SecurityAgentTaskExecutor
        
        assert hasattr(ScalabilityAgentTaskExecutor, 'validate_output')
        assert hasattr(SecurityAgentTaskExecutor, 'validate_output')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
