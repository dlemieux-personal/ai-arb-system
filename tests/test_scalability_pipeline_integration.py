"""
Tests for Scalability Agent Pipeline Integration
Tests the integration of scalability orchestrator with the ARB pipeline
"""

import pytest

from src.orchestration.scalability_orchestrator import (
    ScalabilityAgentOrchestrator,
    ScalabilityDimensionScore,
)
from src.orchestration.task_specs import ScalabilityTaskOutput
from src.schemas.agent_outputs import (
    ScalabilityAgentOutput,
    ScalabilityBottleneck,
    ScalabilityRecommendation,
)


class TestScalabilityPipelineIntegration:
    """Test scalability orchestrator integration with ARB pipeline"""

    def test_pipeline_includes_scalability_orchestrator(self):
        """Test that pipeline can import scalability orchestrator"""
        try:
            from src.orchestration.arb_pipeline import ARBPipeline, create_scalability_orchestrator

            assert ARBPipeline is not None
            assert create_scalability_orchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import scalability components from pipeline: {e}")

    def test_scalability_orchestrator_execution_in_pipeline(self):
        """Test scalability orchestrator execution as part of pipeline"""
        orchestrator = ScalabilityAgentOrchestrator()

        valid_output = """## SCALABILITY BOTTLENECKS
- **Cache miss rate**: 40% of requests bypass cache. Severity: high. Affected: Cache, Frontend

## SCALABILITY RECOMMENDATIONS
- **Implement cache warming**: Preload frequently accessed data. Severity: high. Affected: Cache, Backend

## SCALABILITY SCORE
Overall Scalability Score: 0.62
Confidence Level: 0.92

## SUMMARY
Good caching strategy with room for optimization in cache warming."""

        result = orchestrator.execute_task(valid_output)

        assert result.parsing_successful
        assert result.parsed_output is not None
        assert result.parsed_output.scalability_score == 0.62

    def test_scalability_orchestrator_failure_handling(self):
        """Test pipeline handling of orchestrator failures"""
        orchestrator = ScalabilityAgentOrchestrator()

        invalid_output = "This is not a valid scalability review output"

        result = orchestrator.execute_task(invalid_output)

        assert not result.parsing_successful
        assert result.parsing_error is not None
        assert result.raw_output == invalid_output

    def test_scalability_dimension_score_extraction(self):
        """Test extracting dimension score from scalability output for pipeline"""
        orchestrator = ScalabilityAgentOrchestrator()

        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[
                    ScalabilityBottleneck(
                        title='Database scaling limit',
                        description='Single database instance cannot scale',
                        severity='critical',
                        affected_components=['Database', 'Backend']
                    )
                ],
                recommendations=[
                    ScalabilityRecommendation(
                        title='Implement database sharding',
                        description='Partition data across multiple instances',
                        severity='critical',
                        affected_components=['Database', 'Sharding Layer']
                    )
                ],
                scalability_score=0.48,
                confidence=0.87,
                summary='Critical database scaling issues'
            ),
            raw_output='mock output',
            parsing_successful=True,
            parsing_error=None,
        )

        dim_score = orchestrator.get_dimension_score(task_output)

        assert dim_score.score == 0.48
        assert dim_score.confidence == 0.87
        assert dim_score.bottleneck_count == 1
        assert dim_score.recommendation_count == 1
        assert 'Database scaling limit' in dim_score.critical_bottlenecks

    def test_scalability_fallback_score_handling(self):
        """Test pipeline fallback when scalability parsing fails"""
        orchestrator = ScalabilityAgentOrchestrator()

        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=0.50,
                confidence=0.0,
                summary='Parsing failed - using default score'
            ),
            raw_output='invalid',
            parsing_successful=False,
            parsing_error='Parse error: missing sections',
        )

        dim_score = orchestrator.get_dimension_score(task_output)

        assert dim_score.score == 0.50
        assert dim_score.confidence == 0.0
        assert dim_score.critical_bottlenecks == []

    def test_scalability_context_retrieval(self):
        """Test retrieval context support for scalability agent"""
        orchestrator = ScalabilityAgentOrchestrator()

        task = orchestrator.build_task(
            architecture_description='Microservices with 100k concurrent users',
            submission_id='submission-001',
            retrieval_context='Consider horizontal scaling patterns for microservices',
        )

        assert 'Relevant Scalability Knowledge' in task.description
        assert 'Microservices with 100k concurrent users' in task.description

    def test_scalability_critical_bottleneck_identification(self):
        """Test identification of critical bottlenecks for approval logic"""
        orchestrator = ScalabilityAgentOrchestrator()

        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[
                    ScalabilityBottleneck(
                        title='No horizontal scaling',
                        description='All components single-instance',
                        severity='critical',
                        affected_components=['All components'],
                    ),
                    ScalabilityBottleneck(
                        title='Synchronous communication',
                        description='All inter-service calls are synchronous',
                        severity='high',
                        affected_components=['Service-to-Service'],
                    ),
                ],
                recommendations=[],
                scalability_score=0.20,
                confidence=0.95,
                summary='Critical scalability issues prevent any horizontal scaling',
            ),
            raw_output='mock',
            parsing_successful=True,
            parsing_error=None,
        )

        dim_score = orchestrator.get_dimension_score(task_output)

        assert len(dim_score.critical_bottlenecks) == 1
        assert 'No horizontal scaling' in dim_score.critical_bottlenecks
        assert dim_score.score == 0.20

    def test_scalability_dimension_score_none_handling(self):
        """Test handling of None/missing scalability scores"""
        orchestrator = ScalabilityAgentOrchestrator()

        task_output = ScalabilityTaskOutput(
            agent_output=ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=0.50,
                confidence=0.0,
                summary='Default',
            ),
            raw_output='',
            parsing_successful=False,
            parsing_error='Failed',
        )

        dim_score = orchestrator.get_dimension_score(task_output)

        assert dim_score is not None
        assert 0.0 <= dim_score.score <= 1.0
