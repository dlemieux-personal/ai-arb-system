"""
Tests for Reliability Agent output models and parser.
Validates Pydantic models, JSON serialization, and markdown parsing.
"""

import pytest
from src.schemas.agent_outputs import (
    ReliabilityFinding,
    ReliabilityFailureMode,
    ReliabilityRecommendation,
    ReliabilityAgentOutput
)
from src.agents.output_parsers import (
    ReliabilityAgentOutputParser,
    ReliabilityMarkdownParseError
)


class TestReliabilityFindingModel:
    def test_create_finding_basic(self):
        finding = ReliabilityFinding(
            title="Single region database deployment",
            description="Database replicas are only deployed in one region.",
            severity="high",
            affected_components=["Database"]
        )
        assert finding.title == "Single region database deployment"
        assert finding.severity == "high"
        assert finding.affected_components == ["Database"]

    def test_invalid_severity_finding(self):
        with pytest.raises(ValueError):
            ReliabilityFinding(
                title="Test",
                description="Test",
                severity="low",
                affected_components=[]
            )


class TestReliabilityFailureModeModel:
    def test_create_failure_mode_basic(self):
        failure_mode = ReliabilityFailureMode(
            title="Regional outage",
            description="Failure of the primary region causes full application outage.",
            impact="Service unavailable for all users",
            affected_components=["Application", "Database"]
        )
        assert failure_mode.impact == "Service unavailable for all users"
        assert "Database" in failure_mode.affected_components


class TestReliabilityRecommendationModel:
    def test_create_recommendation_basic(self):
        recommendation = ReliabilityRecommendation(
            title="Add cross-region failover",
            description="Deploy a secondary standby cluster in a second region.",
            severity="critical",
            affected_components=["Database", "Traffic Management"]
        )
        assert recommendation.severity == "critical"
        assert "Database" in recommendation.affected_components


class TestReliabilityAgentOutputParser:
    def test_parse_complete_output(self):
        markdown = """## RELIABILITY FINDINGS

- **Single region deployment**: The primary services are only deployed in one region, increasing outage risk. Severity: high. Affected: API Gateway, Application Servers

## FAILURE MODES

- **Regional data center failure**: Loss of the primary region would stop all traffic. Impact: Complete service outage. Affected: API Gateway, Database Cluster

## RELIABILITY RECOMMENDATIONS

- **Add multi-region failover**: Deploy active-active infrastructure across two regions. Severity: critical. Affected: Application Tier, Database Cluster

## RELIABILITY SCORE

Overall Reliability Score: 0.68

Confidence Level: 0.85

## SUMMARY

The architecture currently relies on a single region and lacks disaster recovery. Cross-region failover is necessary to meet high-availability targets.
"""
        output = ReliabilityAgentOutputParser.parse(markdown)
        assert len(output.findings) == 1
        assert len(output.failure_modes) == 1
        assert len(output.recommendations) == 1
        assert output.reliability_score == 0.68
        assert output.confidence == 0.85

    def test_parse_missing_score_section(self):
        markdown = """## RELIABILITY FINDINGS

- **No findings**: None found. Severity: low. Affected: None

## FAILURE MODES

None identified.

## RELIABILITY RECOMMENDATIONS

None - architecture is resilient.

## SUMMARY

Test summary
"""
        with pytest.raises(ReliabilityMarkdownParseError):
            ReliabilityAgentOutputParser.parse(markdown)
