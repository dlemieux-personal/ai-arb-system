"""
Tests for Security Agent Orchestrator and Task Specifications
"""

import pytest
from src.orchestration.task_specs import (
    SecurityTaskInput,
    SecurityTaskOutput,
    SECURITY_AGENT_TASK_SPEC,
    TaskDomain,
    TaskSpecs,
)
from src.orchestration.security_orchestrator import (
    SecurityAgentOrchestrator,
    SecurityDimensionScore,
    create_security_orchestrator,
)
from src.schemas.agent_outputs import SecurityAgentOutput, SecurityFinding, SecurityRecommendation


SAMPLE_SECURITY_OUTPUT = """## SECURITY FINDINGS

- **Missing encryption**: Database traffic is unencrypted. Severity: critical. Affected: Database, Network
- **Weak authentication**: Default credentials in configuration. Severity: high. Affected: API, Authentication

## SECURITY RECOMMENDATIONS

- **Implement TLS**: Enable TLS for all database connections. Severity: critical. Affected: Database, Network
- **Force strong passwords**: Enforce password policies. Severity: high. Affected: Authentication

## SECURITY SCORE

Overall Security Score: 0.45
Confidence Level: 0.90

## SUMMARY

Critical security gaps exist in network encryption and authentication that require immediate remediation.
"""


class TestTaskSpecification:
    """Test task specification validation"""
    
    def test_security_task_spec_attributes(self):
        """Test security task spec has required attributes"""
        assert SECURITY_AGENT_TASK_SPEC.domain == TaskDomain.SECURITY
        assert SECURITY_AGENT_TASK_SPEC.task_name == "Security Architecture Review"
        assert SECURITY_AGENT_TASK_SPEC.max_retries == 2
        assert len(SECURITY_AGENT_TASK_SPEC.validation_rules) > 0
    
    def test_validate_task_input_valid(self):
        """Test validate_input accepts valid input"""
        valid_input = {
            'architecture_description': 'Test architecture',
            'submission_id': 'test-001',
        }
        
        is_valid, error = SECURITY_AGENT_TASK_SPEC.validate_input(valid_input)
        assert is_valid
        assert error is None
    
    def test_validate_task_input_missing_required_field(self):
        """Test validate_input rejects missing required fields"""
        invalid_input = {
            'submission_id': 'test-001',
            # Missing architecture_description
        }
        
        is_valid, error = SECURITY_AGENT_TASK_SPEC.validate_input(invalid_input)
        assert not is_valid
        assert error is not None
    
    def test_validate_task_output_valid(self):
        """Test validate_output accepts valid output"""
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[
                    SecurityFinding(
                        title="Test",
                        description="Test",
                        severity="high"
                    )
                ],
                security_score=0.75,
                confidence=0.85,
                summary="Test"
            ),
            raw_output="Test output",
            parsing_successful=True,
        )
        
        is_valid, error = SECURITY_AGENT_TASK_SPEC.validate_output(output)
        assert is_valid
        assert error is None
    
    def test_validate_task_output_invalid_type(self):
        """Test validate_output rejects invalid type"""
        is_valid, error = SECURITY_AGENT_TASK_SPEC.validate_output("invalid_string")
        assert not is_valid
        assert error is not None


class TestSecurityTaskOutput:
    """Test SecurityTaskOutput helper methods"""
    
    def test_get_dimension_score_from_parsed_output(self):
        """Test extracting dimension score from parsed output"""
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[],
                security_score=0.82,
                confidence=0.90,
                summary="Test"
            ),
            raw_output="Test",
            parsing_successful=True,
        )
        
        score = output.get_dimension_score()
        assert score == 0.82
    
    def test_get_dimension_score_fallback_on_parse_failure(self):
        """Test fallback score when parsing fails"""
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[],
                security_score=0.0,
                confidence=0.0,
                summary=""
            ),
            raw_output="Invalid",
            parsing_successful=False,
            parsing_error="Parse failed"
        )
        
        score = output.get_dimension_score()
        assert score == 0.50  # Neutral fallback
    
    def test_get_critical_issues(self):
        """Test extracting critical issues"""
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[
                    SecurityFinding(title="Critical 1", description="Desc", severity="critical"),
                    SecurityFinding(title="High 1", description="Desc", severity="high"),
                    SecurityFinding(title="Critical 2", description="Desc", severity="critical"),
                ],
                security_score=0.75,
                confidence=0.85,
                summary="Test"
            ),
            raw_output="Test",
            parsing_successful=True,
        )
        
        critical = output.get_critical_issues()
        assert len(critical) == 2
        assert "Critical 1" in critical
        assert "Critical 2" in critical
        assert "High 1" not in critical
    
    def test_get_critical_issues_empty_on_failure(self):
        """Test no critical issues when parsing fails"""
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[],
                security_score=0.0,
                confidence=0.0,
                summary=""
            ),
            raw_output="Invalid",
            parsing_successful=False,
            parsing_error="Parse failed"
        )
        
        critical = output.get_critical_issues()
        assert len(critical) == 0


class TestTaskSpecs:
    """Test task specification registry"""
    
    def test_get_security_spec(self):
        """Test retrieving security task spec"""
        specs = TaskSpecs()
        spec = specs.get_spec("security")
        
        assert spec is not None
        assert spec.domain == TaskDomain.SECURITY
    
    def test_get_nonexistent_spec(self):
        """Test retrieving nonexistent spec returns None"""
        specs = TaskSpecs()
        spec = specs.get_spec("nonexistent")
        
        assert spec is None
    
    def test_get_all_specs(self):
        """Test retrieving all specs"""
        specs = TaskSpecs()
        all_specs = specs.get_all_specs()
        
        assert "security" in all_specs
        assert len(all_specs) >= 1


class TestSecurityAgentOrchestrator:
    """Test security agent orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = SecurityAgentOrchestrator()
        
        assert orchestrator.task_spec is not None
        assert orchestrator.task_spec.domain == TaskDomain.SECURITY
    
    def test_build_task_creates_task(self):
        """Test building a security review task"""
        orchestrator = SecurityAgentOrchestrator()
        task = orchestrator.build_task(
            architecture_description="Test arch",
            submission_id="test-001"
        )
        
        assert task is not None
        assert "SECURITY FINDINGS" in task.description
        assert "Severity:" in task.description
        assert "0.XX" in task.description or "0.XX format" in task.description
    
    def test_build_task_includes_retrieval_context(self):
        """Test task includes retrieval context when provided"""
        orchestrator = SecurityAgentOrchestrator()
        context = "Important security patterns"
        
        task = orchestrator.build_task(
            architecture_description="Test arch",
            submission_id="test-001",
            retrieval_context=context
        )
        
        assert context in task.description
    
    def test_execute_task_valid_output(self):
        """Test executing task with valid output"""
        orchestrator = SecurityAgentOrchestrator()
        result = orchestrator.execute_task(SAMPLE_SECURITY_OUTPUT)
        
        assert result.parsing_successful
        assert result.parsed_output is not None
        assert result.parsed_output.security_score == 0.45
        assert len(result.parsed_output.findings) == 2
    
    def test_extract_dimension_score_formats_correctly(self):
        """Test extracting dimension score with metadata"""
        orchestrator = SecurityAgentOrchestrator()
        
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[
                    SecurityFinding(title="Critical 1", description="Desc", severity="critical"),
                ],
                recommendations=[
                    SecurityRecommendation(title="Rec 1", description="Desc", severity="high"),
                ],
                security_score=0.68,
                confidence=0.92,
                summary="Test"
            ),
            raw_output="Test",
            parsing_successful=True,
        )
        
        dim_score = orchestrator.extract_dimension_score(output)
        
        assert isinstance(dim_score, SecurityDimensionScore)
        assert dim_score.score == 0.68
        assert dim_score.confidence == 0.92
        assert len(dim_score.critical_issues) == 1
        assert dim_score.findings_count == 1
        assert dim_score.recommendations_count == 1
    
    def test_extract_dimension_score_fallback_on_failure(self):
        """Test dimension score extraction with parse failure"""
        orchestrator = SecurityAgentOrchestrator()
        
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[],
                recommendations=[],
                security_score=0.0,
                confidence=0.0,
                summary=""
            ),
            raw_output="Invalid",
            parsing_successful=False,
            parsing_error="Parse error"
        )
        
        dim_score = orchestrator.extract_dimension_score(output)
        
        assert dim_score.score == 0.50  # Fallback
        assert dim_score.confidence == 0.0
        assert len(dim_score.critical_issues) == 0


class TestOrchestrationFactory:
    """Test orchestrator creation"""
    
    def test_create_orchestrator_factory_function(self):
        """Test factory function creates proper orchestrator"""
        orchestrator = create_security_orchestrator()
        
        assert isinstance(orchestrator, SecurityAgentOrchestrator)
        assert orchestrator.task_spec.domain == TaskDomain.SECURITY


class TestIntegrationWithScoringPipeline:
    """Test integration with scoring pipeline"""
    
    def test_dimension_score_integrates_with_scoring_model(self):
        """Test that dimension score format matches scoring model expectations"""
        orchestrator = SecurityAgentOrchestrator()
        
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[],
                security_score=0.75,
                confidence=0.88,
                summary="Test"
            ),
            raw_output="Test",
            parsing_successful=True,
        )
        
        dim_score = orchestrator.extract_dimension_score(output)
        
        # Verify format matches what scoring model expects
        assert 0.0 <= dim_score.score <= 1.0
        assert 0.0 <= dim_score.confidence <= 1.0
        assert isinstance(dim_score.critical_issues, list)
        assert isinstance(dim_score.findings_count, int)
        assert isinstance(dim_score.recommendations_count, int)
    
    def test_critical_issues_for_approval_logic(self):
        """Test critical issues extraction for approval logic"""
        orchestrator = SecurityAgentOrchestrator()
        
        output = SecurityTaskOutput(
            agent_output=SecurityAgentOutput(
                findings=[
                    SecurityFinding(title="Compliance Issue 1", description="Desc", severity="critical"),
                    SecurityFinding(title="Compliance Issue 2", description="Desc", severity="critical"),
                ],
                security_score=0.30,
                confidence=0.95,
                summary="Critical compliance gaps"
            ),
            raw_output="Test",
            parsing_successful=True,
        )
        
        dim_score = orchestrator.extract_dimension_score(output)
        
        # Verify critical issues are extracted for approval engine
        assert len(dim_score.critical_issues) == 2
        assert all(isinstance(issue, str) for issue in dim_score.critical_issues)
