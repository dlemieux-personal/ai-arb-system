"""
Tests for Scalability Agent output models and parser.
Validates Pydantic models, JSON serialization, and markdown parsing.
"""

import pytest
from src.schemas.agent_outputs import (
    ScalabilityBottleneck,
    ScalabilityRecommendation,
    ScalabilityAgentOutput
)
from src.agents.output_parsers import (
    ScalabilityAgentOutputParser,
    ScalabilityMarkdownParseError
)


class TestScalabilityBottleneckModel:
    """Test ScalabilityBottleneck Pydantic model"""
    
    def test_create_bottleneck_basic(self):
        """Create a basic bottleneck"""
        bottleneck = ScalabilityBottleneck(
            title="Database connection pool exhaustion",
            description="Current pool cannot handle peak load",
            severity="critical",
            affected_components=["Database", "Connection Pool"]
        )
        assert bottleneck.title == "Database connection pool exhaustion"
        assert bottleneck.severity == "critical"
        assert len(bottleneck.affected_components) == 2
    
    def test_bottleneck_severity_validation(self):
        """Validate severity enum constraint"""
        # Valid severities
        for severity in ["critical", "high", "medium", "low"]:
            bottleneck = ScalabilityBottleneck(
                title="Test",
                description="Test",
                severity=severity,
                affected_components=[]
            )
            assert bottleneck.severity == severity
    
    def test_bottleneck_invalid_severity(self):
        """Invalid severity raises validation error"""
        with pytest.raises(ValueError):
            ScalabilityBottleneck(
                title="Test",
                description="Test",
                severity="minor",  # invalid
                affected_components=[]
            )
    
    def test_bottleneck_json_serialization(self):
        """Bottleneck serializes to JSON correctly"""
        bottleneck = ScalabilityBottleneck(
            title="Connection Pool Exhaustion",
            description="Pool depleted at peak load",
            severity="high",
            affected_components=["Database", "Connection Manager"]
        )
        json_str = bottleneck.model_dump_json()
        assert "Connection Pool Exhaustion" in json_str
        assert "high" in json_str
    
    def test_bottleneck_empty_affected_components(self):
        """Bottleneck allows empty affected components list"""
        bottleneck = ScalabilityBottleneck(
            title="Test",
            description="Test",
            severity="low",
            affected_components=[]
        )
        assert bottleneck.affected_components == []
    
    def test_bottleneck_multiple_components(self):
        """Bottleneck handles multiple affected components"""
        components = ["API Gateway", "Load Balancer", "Application Server", "Cache"]
        bottleneck = ScalabilityBottleneck(
            title="Load Distribution Issue",
            description="Uneven load across tiers",
            severity="high",
            affected_components=components
        )
        assert len(bottleneck.affected_components) == 4
        assert bottleneck.affected_components == components


class TestScalabilityRecommendationModel:
    """Test ScalabilityRecommendation Pydantic model"""
    
    def test_create_recommendation_basic(self):
        """Create a basic recommendation"""
        rec = ScalabilityRecommendation(
            title="Implement connection pooling",
            description="Deploy PgBouncer for connection management",
            severity="critical",
            affected_components=["Database"]
        )
        assert rec.title == "Implement connection pooling"
        assert rec.severity == "critical"
    
    def test_recommendation_severity_validation(self):
        """Validate recommendation severity enum"""
        for severity in ["critical", "high", "medium", "low"]:
            rec = ScalabilityRecommendation(
                title="Test",
                description="Test",
                severity=severity,
                affected_components=[]
            )
            assert rec.severity == severity
    
    def test_recommendation_json_serialization(self):
        """Recommendation serializes to JSON"""
        rec = ScalabilityRecommendation(
            title="Add Redis Cache",
            description="Implement distributed caching",
            severity="medium",
            affected_components=["Cache Layer", "Database"]
        )
        json_str = rec.model_dump_json()
        assert "Add Redis Cache" in json_str
        assert "medium" in json_str


class TestScalabilityAgentOutputModel:
    """Test ScalabilityAgentOutput Pydantic model"""
    
    def test_create_output_full(self):
        """Create full output with bottlenecks and recommendations"""
        bottleneck = ScalabilityBottleneck(
            title="Database Pool Exhaustion",
            description="Cannot handle concurrency",
            severity="critical",
            affected_components=["Database"]
        )
        rec = ScalabilityRecommendation(
            title="Connection Pooling",
            description="Use PgBouncer",
            severity="critical",
            affected_components=["Database"]
        )
        output = ScalabilityAgentOutput(
            bottlenecks=[bottleneck],
            recommendations=[rec],
            scalability_score=0.45,
            confidence=0.91,
            summary="Critical database bottleneck limits scalability"
        )
        assert len(output.bottlenecks) == 1
        assert len(output.recommendations) == 1
        assert output.scalability_score == 0.45
        assert output.confidence == 0.91
    
    def test_output_empty_lists(self):
        """Output allows empty bottleneck and recommendation lists"""
        output = ScalabilityAgentOutput(
            bottlenecks=[],
            recommendations=[],
            scalability_score=0.92,
            confidence=0.88,
            summary="Excellent scalability"
        )
        assert len(output.bottlenecks) == 0
        assert len(output.recommendations) == 0
    
    def test_output_score_range(self):
        """Score and confidence must be 0.0-1.0"""
        # Valid ranges
        output = ScalabilityAgentOutput(
            bottlenecks=[],
            recommendations=[],
            scalability_score=0.00,
            confidence=1.00,
            summary="Test"
        )
        assert output.scalability_score == 0.00
        assert output.confidence == 1.00
    
    def test_output_invalid_score_too_high(self):
        """Score > 1.0 rejected"""
        with pytest.raises(ValueError):
            ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=1.05,
                confidence=0.90,
                summary="Test"
            )
    
    def test_output_invalid_score_negative(self):
        """Score < 0.0 rejected"""
        with pytest.raises(ValueError):
            ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=-0.10,
                confidence=0.90,
                summary="Test"
            )
    
    def test_output_max_items(self):
        """Output enforces max 20 bottlenecks and recommendations"""
        bottlenecks = [
            ScalabilityBottleneck(
                title=f"Bottleneck {i}",
                description=f"Description {i}",
                severity="low",
                affected_components=[]
            )
            for i in range(20)
        ]
        output = ScalabilityAgentOutput(
            bottlenecks=bottlenecks,
            recommendations=[],
            scalability_score=0.50,
            confidence=0.80,
            summary="Test"
        )
        assert len(output.bottlenecks) == 20
    
    def test_output_json_schema_example(self):
        """Output model includes valid JSON schema"""
        # From agent_outputs.py Config.json_schema_example
        assert hasattr(ScalabilityAgentOutput, 'model_json_schema')
        schema = ScalabilityAgentOutput.model_json_schema()
        assert "properties" in schema
        assert "bottlenecks" in schema["properties"]
        assert "recommendations" in schema["properties"]


class TestScalabilityAgentOutputParser:
    """Test ScalabilityAgentOutputParser markdown parsing"""
    
    def test_parse_complete_output(self):
        """Parse complete structured markdown output"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Database connection pool exhaustion**: Current pool of 100 connections cannot handle peak load. Severity: critical. Affected: Database, Connection Pool Manager

## SCALABILITY RECOMMENDATIONS

- **Implement connection pooling**: Deploy PgBouncer for connection multiplexing. Severity: critical. Affected: Database, Connection Pool Manager

## SCALABILITY SCORE

Overall Scalability Score: 0.45

Confidence Level: 0.91

## SUMMARY

Critical bottleneck in database connectivity prevents scaling beyond current capacity. Connection pooling should be priority."""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 1
        assert len(output.recommendations) == 1
        assert output.scalability_score == 0.45
        assert output.confidence == 0.91
    
    def test_parse_single_bottleneck(self):
        """Parse single bottleneck correctly"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Database Pool Exhaustion**: Cannot handle concurrency growth. Severity: high. Affected: Database, Connection Pool

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.60

Confidence Level: 0.85

## SUMMARY

Test summary"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 1
        assert output.bottlenecks[0].title == "Database Pool Exhaustion"
        assert output.bottlenecks[0].severity == "high"
        assert "Database" in output.bottlenecks[0].affected_components
    
    def test_parse_multiple_bottlenecks(self):
        """Parse multiple bottlenecks"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Bottleneck 1**: Description 1. Severity: critical. Affected: Component A
- **Bottleneck 2**: Description 2. Severity: high. Affected: Component B, Component C
- **Bottleneck 3**: Description 3. Severity: medium. Affected: Component D

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.50

Confidence Level: 0.80

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 3
        assert output.bottlenecks[0].severity == "critical"
        assert output.bottlenecks[1].severity == "high"
        assert output.bottlenecks[2].severity == "medium"
    
    def test_parse_no_bottlenecks(self):
        """Parse when no bottlenecks found"""
        markdown = """## SCALABILITY BOTTLENECKS

None identified.

## SCALABILITY RECOMMENDATIONS

- **Recommendation 1**: Description. Severity: medium. Affected: Component

## SCALABILITY SCORE

Overall Scalability Score: 0.90

Confidence Level: 0.95

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 0
        assert len(output.recommendations) == 1
    
    def test_parse_no_recommendations(self):
        """Parse when no recommendations provided"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Bottleneck**: Description. Severity: low. Affected: Component

## SCALABILITY RECOMMENDATIONS

None - architecture scales well.

## SCALABILITY SCORE

Overall Scalability Score: 0.88

Confidence Level: 0.92

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 1
        assert len(output.recommendations) == 0
    
    def test_parse_multiple_recommendations(self):
        """Parse multiple recommendations"""
        markdown = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

- **Rec 1**: Desc 1. Severity: critical. Affected: Comp A
- **Rec 2**: Desc 2. Severity: high. Affected: Comp B
- **Rec 3**: Desc 3. Severity: medium. Affected: Comp C, Comp D

## SCALABILITY SCORE

Overall Scalability Score: 0.75

Confidence Level: 0.82

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.recommendations) == 3
        assert output.recommendations[0].severity == "critical"
        assert output.recommendations[2].affected_components == ["Comp C", "Comp D"]
    
    def test_parse_extracts_affected_components(self):
        """Affected components parsed correctly"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Issue**: Description. Severity: high. Affected: API Gateway, Load Balancer, Application Server

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.60

Confidence Level: 0.85

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        components = output.bottlenecks[0].affected_components
        assert len(components) == 3
        assert "API Gateway" in components
        assert "Load Balancer" in components
        assert "Application Server" in components
    
    def test_parse_handles_whitespace(self):
        """Whitespace variations handled correctly"""
        markdown = """## SCALABILITY BOTTLENECKS

-    **Issue**:     Description.    Severity:    high.    Affected:    Component A,    Component B

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.70

Confidence Level: 0.80

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 1
        assert "Component A" in output.bottlenecks[0].affected_components
        assert "Component B" in output.bottlenecks[0].affected_components
    
    def test_parse_missing_score_section(self):
        """Missing SCALABILITY SCORE section raises error"""
        markdown = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

## SUMMARY

Test"""
        
        with pytest.raises(ScalabilityMarkdownParseError):
            ScalabilityAgentOutputParser.parse(markdown)
    
    def test_parse_invalid_score_format(self):
        """Invalid score format raises error"""
        markdown = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.5

Confidence Level: 0.85

## SUMMARY

Test"""
        
        with pytest.raises(ScalabilityMarkdownParseError):
            ScalabilityAgentOutputParser.parse(markdown)
    
    def test_parse_missing_confidence(self):
        """Missing confidence raises error"""
        markdown = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.75

## SUMMARY

Test"""
        
        with pytest.raises(ScalabilityMarkdownParseError):
            ScalabilityAgentOutputParser.parse(markdown)
    
    def test_parse_missing_severity(self):
        """Missing severity in item raises error"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Issue**: Description. Affected: Component

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.75

Confidence Level: 0.85

## SUMMARY

Test"""
        
        with pytest.raises(ScalabilityMarkdownParseError):
            ScalabilityAgentOutputParser.parse(markdown)
    
    def test_parse_score_boundaries(self):
        """Score parsing at boundaries (0.00, 1.00)"""
        markdown_min = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.00

Confidence Level: 0.50

## SUMMARY

Test"""
        
        markdown_max = """## SCALABILITY BOTTLENECKS

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 1.00

Confidence Level: 1.00

## SUMMARY

Test"""
        
        output_min = ScalabilityAgentOutputParser.parse(markdown_min)
        assert output_min.scalability_score == 0.00
        
        output_max = ScalabilityAgentOutputParser.parse(markdown_max)
        assert output_max.scalability_score == 1.00
    
    def test_parse_preserves_description_case(self):
        """Description case and punctuation preserved"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Issue**: The Database Connection Pool cannot handle concurrent spikes of 200+ requests per second. Severity: critical. Affected: Database

## SCALABILITY RECOMMENDATIONS

## SCALABILITY SCORE

Overall Scalability Score: 0.45

Confidence Level: 0.90

## SUMMARY

Test"""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert "Database Connection Pool" in output.bottlenecks[0].description
        assert "200+" in output.bottlenecks[0].description
    
    def test_parse_full_realistic_output(self):
        """Parse realistic multi-issue output"""
        markdown = """## SCALABILITY BOTTLENECKS

- **Database connection pool exhaustion under load**: Current pool size of 100 connections cannot handle 150 concurrent requests, causing request queuing. Severity: critical. Affected: Database, Connection Pool Manager
- **Lack of horizontal scaling for stateful API tier**: API servers maintain in-memory sessions, preventing horizontal scaling. Severity: high. Affected: API Gateway, Session Management
- **Missing caching layer for frequent queries**: Repeated expensive SQL queries consume database resources unnecessarily. Severity: medium. Affected: Database, Application Tier

## SCALABILITY RECOMMENDATIONS

- **Implement connection pooling**: Deploy PgBouncer or similar service to multiplex connections. Severity: critical. Affected: Database, Connection Pool Manager
- **Redesign API tier for statelessness**: Migrate sessions to distributed Redis. Severity: high. Affected: API Tier, Session Storage
- **Add Redis caching layer**: Cache read-heavy queries to reduce database load. Severity: medium. Affected: Database, Cache Layer

## SCALABILITY SCORE

Overall Scalability Score: 0.52

Confidence Level: 0.88

## SUMMARY

Architecture demonstrates growth awareness but has critical bottlenecks in database tier and session management. Connection pooling and session externalization are immediate priorities for scaling beyond current capacity."""
        
        output = ScalabilityAgentOutputParser.parse(markdown)
        assert len(output.bottlenecks) == 3
        assert len(output.recommendations) == 3
        assert output.scalability_score == 0.52
        assert output.confidence == 0.88
        assert "priorities" in output.summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
