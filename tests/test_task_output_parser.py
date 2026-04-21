"""
Tests for task output wrapper and security agent execution
"""

import pytest
from src.orchestration.task_output import SecurityAgentTaskExecutor, TaskOutput
from src.schemas.agent_outputs import SecurityAgentOutput, SecurityFinding


VALID_AGENT_OUTPUT = """## SECURITY FINDINGS

- **Missing TLS encryption**: API calls use HTTP without encryption. Severity: high. Affected: API Gateway, Services
- **Weak secret management**: Credentials stored in files. Severity: critical. Affected: Database

## SECURITY RECOMMENDATIONS

- **Enable TLS 1.3**: Implement mTLS for all services. Severity: high. Affected: API Gateway
- **Use vault**: Implement HashiCorp Vault. Severity: critical. Affected: Configuration

## SECURITY SCORE

Overall Security Score: 0.65
Confidence Level: 0.85

## SUMMARY

Architecture has significant security gaps in encryption and secrets management that must be addressed.
"""


class TestTaskOutput:
    """Test the TaskOutput container"""
    
    def test_valid_task_output(self):
        """Test creating a valid task output"""
        output = TaskOutput[SecurityAgentOutput](
            agent_name="Security Agent",
            raw_output="test",
            parsed_output=SecurityAgentOutput(
                security_score=0.75,
                confidence=0.85
            ),
            parsing_successful=True
        )
        
        assert output.is_valid()
        assert output.agent_name == "Security Agent"
        assert output.parsed_output.security_score == 0.75
    
    def test_invalid_task_output(self):
        """Test that get_parsed_or_raise raises on invalid output"""
        output = TaskOutput[SecurityAgentOutput](
            agent_name="Security Agent",
            raw_output="test",
            parsing_successful=False,
            parsing_error="Parse failed"
        )
        
        assert not output.is_valid()
        
        with pytest.raises(ValueError) as exc_info:
            output.get_parsed_or_raise()
        
        assert "could not be parsed" in str(exc_info.value)
    
    def test_task_output_without_parsed_content(self):
        """Test task output with raw output only"""
        output = TaskOutput[SecurityAgentOutput](
            agent_name="Test Agent",
            raw_output="some raw text",
            parsing_successful=False,
            parsing_error="Failed to parse"
        )
        
        assert not output.is_valid()
        assert output.raw_output == "some raw text"
        assert output.parsing_error == "Failed to parse"


class TestSecurityAgentTaskExecutor:
    """Test the security agent task executor"""
    
    def test_execute_and_parse_valid_output(self):
        """Test executing and parsing valid agent output"""
        result = SecurityAgentTaskExecutor.execute_and_parse(VALID_AGENT_OUTPUT)
        
        assert result.is_valid()
        assert result.parsing_successful
        assert result.parsing_attempts == 1
        assert result.parsed_output is not None
        assert isinstance(result.parsed_output, SecurityAgentOutput)
        assert result.parsed_output.security_score == 0.65
        assert result.parsed_output.confidence == 0.85
        assert len(result.parsed_output.findings) == 2
        assert len(result.parsed_output.recommendations) == 2
    
    def test_agent_name_in_output(self):
        """Test that custom agent name is stored"""
        result = SecurityAgentTaskExecutor.execute_and_parse(
            VALID_AGENT_OUTPUT,
            agent_name="Custom Security Agent"
        )
        
        assert result.agent_name == "Custom Security Agent"
    
    def test_parse_failure_with_error_message(self):
        """Test parsing failure captures error message"""
        bad_output = """## SECURITY FINDINGS

None found.

## SECURITY SCORE

This is not the right format
"""
        
        result = SecurityAgentTaskExecutor.execute_and_parse(bad_output)
        
        assert not result.is_valid()
        assert result.parsing_successful is False
        assert result.parsing_error is not None
        assert len(result.parsing_error) > 0
    
    def test_raw_output_preserved(self):
        """Test that raw output is always preserved"""
        result = SecurityAgentTaskExecutor.execute_and_parse(VALID_AGENT_OUTPUT)
        
        assert result.raw_output == VALID_AGENT_OUTPUT
    
    def test_retry_attempts_tracked(self):
        """Test that retry attempts are tracked"""
        bad_output = "This will fail definitely"
        
        result = SecurityAgentTaskExecutor.execute_and_parse(bad_output)
        
        # Should have tried MAX_PARSE_RETRIES + 1 times
        assert result.parsing_attempts == SecurityAgentTaskExecutor.MAX_PARSE_RETRIES + 1
        assert not result.parsing_successful


class TestSecurityAgentTaskExecutorValidation:
    """Test validation of parsed security agent output"""
    
    def test_validate_valid_output(self):
        """Test validation of valid output"""
        output = SecurityAgentOutput(
            findings=[
                SecurityFinding(
                    title="Test",
                    description="Test description",
                    severity="high"
                )
            ],
            security_score=0.75,
            confidence=0.85
        )
        
        is_valid, error = SecurityAgentTaskExecutor.validate_output(output)
        assert is_valid
        assert error == ""
    
    def test_validate_score_outside_range(self):
        """Test Pydantic validation rejects scores outside 0.0-1.0"""
        from pydantic import ValidationError
        
        # Pydantic validates on instantiation
        with pytest.raises(ValidationError):
            SecurityAgentOutput(
                security_score=1.5,  # Invalid: > 1.0
                confidence=0.85,
                findings=[
                    SecurityFinding(
                        title="Test",
                        description="Test",
                        severity="high"
                    )
                ]
            )
    
    def test_validate_confidence_outside_range(self):
        """Test Pydantic validation rejects confidence outside 0.0-1.0"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SecurityAgentOutput(
                security_score=0.75,
                confidence=-0.1,  # Invalid: < 0.0
                findings=[
                    SecurityFinding(
                        title="Test",
                        description="Test",
                        severity="high"
                    )
                ]
            )
    
    def test_validate_empty_findings_and_recommendations(self):
        """Test validation requires at least findings or recommendations"""
        output = SecurityAgentOutput(
            findings=[],
            recommendations=[],
            security_score=0.75,
            confidence=0.85
        )
        
        is_valid, error = SecurityAgentTaskExecutor.validate_output(output)
        assert not is_valid
        assert "must contain at least" in error.lower()
    
    def test_validate_severity_enum_enforcement(self):
        """Test Pydantic validation enforces valid severity values"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SecurityFinding(
                title="Test",
                description="Test",
                severity="unknown"  # Invalid enum value
            )
    
    def test_validate_valid_all_severity_levels(self):
        """Test all valid severity levels are accepted"""
        for severity in ["critical", "high", "medium", "low"]:
            finding = SecurityFinding(
                title="Test",
                description="Test",
                severity=severity
            )
            assert finding.severity == severity


class TestTaskOutputIntegration:
    """Integration tests for task output with parsing"""
    
    def test_full_workflow(self):
        """Test complete workflow: parse, validate, store"""
        # 1. Agent produces output
        agent_output = VALID_AGENT_OUTPUT
        
        # 2. Execute and parse
        result = SecurityAgentTaskExecutor.execute_and_parse(agent_output)
        
        # 3. Check parsing succeeded
        assert result.is_valid()
        
        # 4. Validate result
        is_valid, error = SecurityAgentTaskExecutor.validate_output(result.parsed_output)
        assert is_valid
        
        # 5. Use the result
        parsed = result.get_parsed_or_raise()
        assert parsed.security_score == 0.65
        assert len(parsed.findings) == 2
    
    def test_error_handling_workflow(self):
        """Test workflow with parsing error"""
        # 1. Bad agent output
        bad_output = "This is not valid markdown"
        
        # 2. Execute and parse
        result = SecurityAgentTaskExecutor.execute_and_parse(bad_output)
        
        # 3. Check parsing failed gracefully
        assert not result.is_valid()
        assert result.parsing_error is not None
        
        # 4. Getting parsed output should fail
        with pytest.raises(ValueError):
            result.get_parsed_or_raise()
