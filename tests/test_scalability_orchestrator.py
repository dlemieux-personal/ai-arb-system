"""
Tests for ScalabilityAgentOrchestrator
Tests the end-to-end orchestration of scalability agent tasks
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from crewai import Crew, Agent, Task

from src.agents.definitions.scalability_agent import build_scalability_agent
from src.orchestration.scalability_orchestrator import (
    ScalabilityAgentOrchestrator,
    ScalabilityDimensionScore,
    create_scalability_orchestrator
)
from src.orchestration.task_specs import ScalabilityTaskOutput
from src.schemas.agent_outputs import (
    ScalabilityAgentOutput,
    ScalabilityBottleneck,
    ScalabilityRecommendation,
)
from src.agents.agent_factory import AgentFactory


class TestScalabilityAgentOrchestrator:
    """Test ScalabilityAgentOrchestrator class functionality"""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = ScalabilityAgentOrchestrator()
        assert orchestrator.factory is not None
        assert orchestrator.task_spec is not None
        assert orchestrator.scalability_agent is None
        assert orchestrator.scalability_task is None

    def test_orchestrator_with_custom_factory(self):
        """Test orchestrator with custom agent factory"""
        mock_factory = Mock(spec=AgentFactory)
        orchestrator = ScalabilityAgentOrchestrator(mock_factory)
        assert orchestrator.factory == mock_factory

    @patch('src.orchestration.scalability_orchestrator.build_scalability_agent')
    def test_build_task(self, mock_build_agent):
        """Test task building functionality"""
        mock_agent = build_scalability_agent()
        mock_build_agent.return_value = mock_agent

        orchestrator = ScalabilityAgentOrchestrator()
        task = orchestrator.build_task(
            architecture_description="Test architecture",
            submission_id="test-123",
            retrieval_context="Test context"
        )

        assert orchestrator.scalability_agent == mock_agent
        assert orchestrator.scalability_task == task
        assert task is not None
        assert "Test architecture" in task.description
        assert "Test context" in task.description

    @patch('src.orchestration.scalability_orchestrator.build_scalability_agent')
    def test_build_task_without_context(self, mock_build_agent):
        """Test task building without retrieval context"""
        mock_agent = build_scalability_agent()
        mock_build_agent.return_value = mock_agent

        orchestrator = ScalabilityAgentOrchestrator()
        task = orchestrator.build_task(
            architecture_description="Test architecture",
            submission_id="test-123"
        )

        assert "Test architecture" in task.description
        # Should not contain context section when None
        assert "Relevant Scalability Knowledge" not in task.description

    def test_execute_task_success(self):
        """Test successful task execution"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Mock valid scalability output
        valid_output = """## SCALABILITY BOTTLENECKS
- **Database bottleneck**: Single instance limits scaling. Severity: critical. Affected: Database, Backend

## SCALABILITY RECOMMENDATIONS
- **Implement sharding**: Distribute data across instances. Severity: critical. Affected: Database, Storage

## SCALABILITY SCORE
Overall Scalability Score: 0.35
Confidence Level: 0.85

## SUMMARY
Critical scalability issues prevent horizontal scaling."""

        result = orchestrator.execute_task(valid_output)

        assert result.parsing_successful
        assert result.parsing_error is None
        assert result.parsed_output is not None
        assert result.parsed_output.scalability_score == 0.35
        assert result.parsed_output.confidence == 0.85
        assert len(result.parsed_output.bottlenecks) == 1
        assert len(result.parsed_output.recommendations) == 1

    def test_execute_task_parsing_failure(self):
        """Test task execution with parsing failure"""
        orchestrator = ScalabilityAgentOrchestrator()

        invalid_output = "Invalid output format"

        result = orchestrator.execute_task(invalid_output)

        assert not result.parsing_successful
        assert result.parsing_error is not None
        assert result.parsed_output is None
        assert result.raw_output == invalid_output

    @patch('src.orchestration.scalability_orchestrator.build_scalability_agent')
    @patch('src.orchestration.scalability_orchestrator.Crew')
    def test_run_crew_success(self, mock_crew_class, mock_build_agent):
        """Test successful crew execution"""
        # Setup mocks
        mock_agent = build_scalability_agent()
        mock_build_agent.return_value = mock_agent

        mock_crew = Mock(spec=Crew)
        mock_crew_class.return_value = mock_crew

        valid_crew_output = """## SCALABILITY BOTTLENECKS
- **Load balancer limit**: Single point of failure. Severity: high. Affected: Load Balancer, Traffic

## SCALABILITY RECOMMENDATIONS
- **Add redundancy**: Multiple load balancers. Severity: high. Affected: Load Balancer, HA

## SCALABILITY SCORE
Overall Scalability Score: 0.65
Confidence Level: 0.90

## SUMMARY
Good scalability with minor improvements needed."""

        mock_crew.kickoff.return_value = valid_crew_output

        orchestrator = ScalabilityAgentOrchestrator()
        result = orchestrator.run_crew(
            architecture_description="Test architecture",
            submission_id="test-123"
        )

        assert isinstance(result, ScalabilityTaskOutput)
        assert result.parsing_successful
        assert result.agent_output.scalability_score == 0.65
        assert result.agent_output.confidence == 0.90
        assert result.raw_output == valid_crew_output

    @patch('src.orchestration.scalability_orchestrator.build_scalability_agent')
    @patch('src.orchestration.scalability_orchestrator.Crew')
    def test_run_crew_execution_failure(self, mock_crew_class, mock_build_agent):
        """Test crew execution failure handling"""
        # Setup mocks
        mock_agent = build_scalability_agent()
        mock_build_agent.return_value = mock_agent

        mock_crew = Mock(spec=Crew)
        mock_crew_class.return_value = mock_crew
        mock_crew.kickoff.side_effect = Exception("Crew execution failed")

        orchestrator = ScalabilityAgentOrchestrator()
        result = orchestrator.run_crew(
            architecture_description="Test architecture",
            submission_id="test-123"
        )

        assert isinstance(result, ScalabilityTaskOutput)
        assert not result.parsing_successful
        assert result.parsing_error is not None
        assert "Crew execution failed" in result.raw_output
        assert result.agent_output.scalability_score == 0.50  # Default fallback
        assert result.agent_output.confidence == 0.0

    def test_get_dimension_score(self):
        """Test dimension score extraction"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Create mock task output
        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[
                    ScalabilityBottleneck(
                        title='Critical bottleneck',
                        description='Description of critical bottleneck',
                        severity='critical',
                        affected_components=['Database']
                    ),
                    ScalabilityBottleneck(
                        title='High bottleneck',
                        description='Description of high bottleneck',
                        severity='high',
                        affected_components=['API']
                    )
                ],
                recommendations=[],
                scalability_score=0.75,
                confidence=0.88,
                summary="Test summary"
            ),
            raw_output="test",
            parsing_successful=True,
            parsing_error=None
        )

        dimension_score = orchestrator.get_dimension_score(task_output)

        assert isinstance(dimension_score, ScalabilityDimensionScore)
        assert dimension_score.score == 0.75
        assert dimension_score.confidence == 0.88
        assert dimension_score.bottleneck_count == 2
        assert dimension_score.recommendation_count == 0
        assert dimension_score.critical_bottlenecks == ['Critical bottleneck']

    def test_get_dimension_score_parsing_failed(self):
        """Test dimension score extraction when parsing failed"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Create mock task output with parsing failure
        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=0.50,
                confidence=0.0,
                summary="Default summary"
            ),
            raw_output="test",
            parsing_successful=False,
            parsing_error="Parsing failed"
        )

        dimension_score = orchestrator.get_dimension_score(task_output)

        assert dimension_score.score == 0.50  # Fallback score
        assert dimension_score.confidence == 0.0
        assert dimension_score.critical_bottlenecks == []


class TestScalabilityDimensionScore:
    """Test ScalabilityDimensionScore dataclass"""

    def test_dimension_score_creation(self):
        """Test dimension score creation"""
        score = ScalabilityDimensionScore(
            score=0.80,
            confidence=0.95,
            bottleneck_count=3,
            recommendation_count=5,
            critical_bottlenecks=['Critical issue 1', 'Critical issue 2']
        )

        assert score.score == 0.80
        assert score.confidence == 0.95
        assert score.bottleneck_count == 3
        assert score.recommendation_count == 5
        assert score.critical_bottlenecks == ['Critical issue 1', 'Critical issue 2']


class TestCreateScalabilityOrchestrator:
    """Test create_scalability_orchestrator factory function"""

    def test_create_orchestrator(self):
        """Test orchestrator factory function"""
        orchestrator = create_scalability_orchestrator()
        assert isinstance(orchestrator, ScalabilityAgentOrchestrator)

    def test_create_orchestrator_with_factory(self):
        """Test orchestrator factory with custom factory"""
        mock_factory = Mock(spec=AgentFactory)
        orchestrator = create_scalability_orchestrator(mock_factory)
        assert isinstance(orchestrator, ScalabilityAgentOrchestrator)
        assert orchestrator.factory == mock_factory


class TestScalabilityOrchestratorIntegration:
    """Integration tests for ScalabilityAgentOrchestrator"""

    def test_full_orchestration_workflow(self):
        """Test complete orchestration workflow"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Test with valid output
        valid_output = """## SCALABILITY BOTTLENECKS
- **Memory bottleneck**: Insufficient RAM for load. Severity: high. Affected: Application, Memory

## SCALABILITY RECOMMENDATIONS
- **Increase memory**: Add more RAM instances. Severity: high. Affected: Application, Infrastructure

## SCALABILITY SCORE
Overall Scalability Score: 0.55
Confidence Level: 0.80

## SUMMARY
Memory constraints limit scalability under high load."""

        # Execute task
        task_result = orchestrator.execute_task(valid_output)
        assert task_result.parsing_successful

        # Create task output
        task_output = ScalabilityTaskOutput(
            agent_output=task_result.parsed_output,
            raw_output=valid_output,
            parsing_successful=True,
            parsing_error=None
        )

        # Get dimension score
        dimension_score = orchestrator.get_dimension_score(task_output)

        assert dimension_score.score == 0.55
        assert dimension_score.confidence == 0.80
        assert dimension_score.bottleneck_count == 1
        assert dimension_score.recommendation_count == 1
        assert dimension_score.critical_bottlenecks == []  # No critical severity

    def test_orchestrator_task_spec_validation(self):
        """Test that orchestrator uses correct task spec"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Check task spec properties
        assert orchestrator.task_spec.domain.value == "scalability"
        assert orchestrator.task_spec.task_name == "Scalability Architecture Review"
        assert "scalability" in orchestrator.task_spec.description.lower()

        # Test input validation
        valid_input = {
            'architecture_description': 'Test architecture',
            'submission_id': 'test-123',
            'retrieval_context': 'Test context'
        }
        is_valid, error = orchestrator.task_spec.validate_input(valid_input)
        assert is_valid
        assert error is None

    def test_orchestrator_error_handling(self):
        """Test orchestrator error handling"""
        orchestrator = ScalabilityAgentOrchestrator()

        # Test with malformed output
        malformed_output = """## SCALABILITY BOTTLENECKS
- **Test bottleneck**: Description. Severity: invalid. Affected: Test

## SCALABILITY SCORE
Overall Scalability Score: 1.5
Confidence Level: 1.5"""

        result = orchestrator.execute_task(malformed_output)

        # Should fail parsing due to validation errors
        assert not result.parsing_successful
        assert result.parsing_error is not None
        assert "Could not extract severity" in result.parsing_error or "Invalid" in result.parsing_error