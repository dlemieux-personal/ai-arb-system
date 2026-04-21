"""
Tests for Security Agent output schema and markdown parser
"""

import pytest
from src.schemas.agent_outputs import SecurityAgentOutput, SecurityFinding, SecurityRecommendation
from src.agents.output_parsers import SecurityAgentOutputParser, SecurityMarkdownParseError


class TestSecurityFindingModel:
    """Test SecurityFinding Pydantic model"""
    
    def test_valid_finding(self):
        """Test creating a valid security finding"""
        finding = SecurityFinding(
            title="Missing TLS encryption",
            description="API calls use HTTP without encryption",
            severity="high",
            affected_components=["API Gateway", "Services"]
        )
        assert finding.title == "Missing TLS encryption"
        assert finding.severity == "high"
        assert len(finding.affected_components) == 2
    
    def test_finding_with_empty_components(self):
        """Test finding with no affected components"""
        finding = SecurityFinding(
            title="Test finding",
            description="Test description",
            severity="medium"
        )
        assert finding.affected_components == []
    
    def test_invalid_severity(self):
        """Test that invalid severity is rejected"""
        with pytest.raises(ValueError):
            SecurityFinding(
                title="Test",
                description="Test description",
                severity="invalid"
            )
    
    def test_missing_required_field(self):
        """Test that missing required field raises error"""
        with pytest.raises(ValueError):
            SecurityFinding(
                title="Test",
                description="Test description"
                # severity missing
            )


class TestSecurityRecommendationModel:
    """Test SecurityRecommendation Pydantic model"""
    
    def test_valid_recommendation(self):
        """Test creating a valid recommendation"""
        rec = SecurityRecommendation(
            title="Implement TLS encryption",
            description="Enable TLS 1.3 for all connections",
            severity="high",
            affected_components=["API Gateway"]
        )
        assert rec.title == "Implement TLS encryption"
        assert rec.severity == "high"
    
    def test_all_severity_levels(self):
        """Test all valid severity levels"""
        for severity in ["critical", "high", "medium", "low"]:
            rec = SecurityRecommendation(
                title="Test",
                description="Test description",
                severity=severity
            )
            assert rec.severity == severity


class TestSecurityAgentOutputModel:
    """Test SecurityAgentOutput Pydantic model"""
    
    def test_valid_output(self):
        """Test creating valid security agent output"""
        output = SecurityAgentOutput(
            findings=[
                SecurityFinding(
                    title="Finding 1",
                    description="Description 1",
                    severity="high",
                    affected_components=["Service1"]
                )
            ],
            recommendations=[
                SecurityRecommendation(
                    title="Recommendation 1",
                    description="Description 1",
                    severity="high",
                    affected_components=["Service1"]
                )
            ],
            security_score=0.75,
            confidence=0.85,
            summary="Test summary"
        )
        assert output.security_score == 0.75
        assert output.confidence == 0.85
        assert len(output.findings) == 1
    
    def test_score_boundaries(self):
        """Test score validation at boundaries"""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            output = SecurityAgentOutput(
                security_score=score,
                confidence=0.5
            )
            assert output.security_score == score
        
        # Invalid scores
        with pytest.raises(ValueError):
            SecurityAgentOutput(security_score=-0.1, confidence=0.5)
        
        with pytest.raises(ValueError):
            SecurityAgentOutput(security_score=1.1, confidence=0.5)
    
    def test_empty_lists_allowed(self):
        """Test that empty findings/recommendations are allowed"""
        output = SecurityAgentOutput(
            findings=[],
            recommendations=[],
            security_score=0.80,
            confidence=0.95
        )
        assert output.findings == []
        assert output.recommendations == []


class TestSecurityMarkdownParser:
    """Test parsing security agent markdown output"""
    
    SAMPLE_MARKDOWN = """## SECURITY FINDINGS

- **Missing TLS encryption**: API communication uses HTTP without encryption. Severity: high. Affected: API Gateway, Services
- **Weak secret management**: Database credentials stored in plaintext configuration files. Severity: critical. Affected: Database Layer

## SECURITY RECOMMENDATIONS

- **Implement TLS 1.3**: Enable mutual TLS with certificate rotation. Severity: high. Affected: API Gateway, Load Balancer
- **Implement secrets vault**: Use HashiCorp Vault or AWS Secrets Manager. Severity: critical. Affected: Configuration Management

## SECURITY SCORE

Overall Security Score: 0.72
Confidence Level: 0.89

## SUMMARY

The proposed architecture demonstrates some security awareness but has critical gaps in encryption and secrets management that must be addressed before approval.
"""
    
    def test_parse_valid_output(self):
        """Test parsing valid security agent markdown"""
        output = SecurityAgentOutputParser.parse(self.SAMPLE_MARKDOWN)
        
        assert isinstance(output, SecurityAgentOutput)
        assert len(output.findings) == 2
        assert len(output.recommendations) == 2
        assert output.security_score == 0.72
        assert output.confidence == 0.89
    
    def test_extract_findings(self):
        """Test that findings are correctly extracted"""
        output = SecurityAgentOutputParser.parse(self.SAMPLE_MARKDOWN)
        
        finding1 = output.findings[0]
        assert finding1.title == "Missing TLS encryption"
        assert finding1.severity == "high"
        assert "API Gateway" in finding1.affected_components
        assert "Services" in finding1.affected_components
        
        finding2 = output.findings[1]
        assert finding2.severity == "critical"
    
    def test_extract_recommendations(self):
        """Test that recommendations are correctly extracted"""
        output = SecurityAgentOutputParser.parse(self.SAMPLE_MARKDOWN)
        
        rec1 = output.recommendations[0]
        assert rec1.title == "Implement TLS 1.3"
        assert rec1.severity == "high"
        
        rec2 = output.recommendations[1]
        assert rec2.severity == "critical"
        assert rec2.title == "Implement secrets vault"
    
    def test_no_findings(self):
        """Test handling when there are no findings"""
        markdown = """## SECURITY FINDINGS

None found.

## SECURITY RECOMMENDATIONS

- **Recommendation**: Description. Severity: low. Affected: Component1

## SECURITY SCORE

Overall Security Score: 0.95
Confidence Level: 0.92

## SUMMARY

Architecture is exemplary.
"""
        output = SecurityAgentOutputParser.parse(markdown)
        assert output.findings == []
        assert len(output.recommendations) == 1
    
    def test_no_recommendations(self):
        """Test handling when there are no recommendations"""
        markdown = """## SECURITY FINDINGS

- **Finding**: Description. Severity: low. Affected: Component1

## SECURITY RECOMMENDATIONS

None - architecture is exemplary.

## SECURITY SCORE

Overall Security Score: 0.95
Confidence Level: 0.92

## SUMMARY

Everything is great.
"""
        output = SecurityAgentOutputParser.parse(markdown)
        assert len(output.findings) == 1
        assert output.recommendations == []
    
    def test_missing_security_score_section(self):
        """Test error when SECURITY SCORE is missing"""
        bad_markdown = """## SECURITY FINDINGS

None found.

## SECURITY RECOMMENDATIONS

None.

## SUMMARY

Test
"""
        with pytest.raises(SecurityMarkdownParseError) as exc_info:
            SecurityAgentOutputParser.parse(bad_markdown)
        
        assert "SECURITY SCORE section not found" in str(exc_info.value)
    
    def test_invalid_score_format(self):
        """Test error when score is incorrectly formatted"""
        bad_markdown = """## SECURITY FINDINGS

None found.

## SECURITY SCORE

Overall Security Score: seventy-five
Confidence Level: 0.89

## SUMMARY

Test
"""
        with pytest.raises(SecurityMarkdownParseError):
            SecurityAgentOutputParser.parse(bad_markdown)
    
    def test_case_insensitive_section_headers(self):
        """Test that section headers are case-insensitive"""
        lowercase_markdown = """## security findings

- **Test**: Description. Severity: low. Affected: Component

## security recommendations

None.

## security score

Overall Security Score: 0.80
Confidence Level: 0.85

## summary

Test summary
"""
        output = SecurityAgentOutputParser.parse(lowercase_markdown)
        assert len(output.findings) == 1
        assert output.security_score == 0.80
    
    def test_score_with_two_decimals(self):
        """Test that scores must have exactly 2 decimal places"""
        markdown = """## SECURITY FINDINGS

None found.

## SECURITY SCORE

Overall Security Score: 0.82
Confidence Level: 0.99

## SUMMARY

Test
"""
        output = SecurityAgentOutputParser.parse(markdown)
        assert output.security_score == 0.82
        assert output.confidence == 0.99
    
    def test_multiple_affected_components(self):
        """Test parsing multiple affected components"""
        markdown = """## SECURITY FINDINGS

- **Issue**: Description. Severity: high. Affected: Component1, Component2, Component3, Component4

## SECURITY RECOMMENDATIONS

None.

## SECURITY SCORE

Overall Security Score: 0.75
Confidence Level: 0.80

## SUMMARY

Test
"""
        output = SecurityAgentOutputParser.parse(markdown)
        assert len(output.findings[0].affected_components) == 4
        assert "Component1" in output.findings[0].affected_components
        assert "Component4" in output.findings[0].affected_components
    
    def test_round_trip_output(self):
        """Test that output can be converted back to markdown and re-parsed"""
        output1 = SecurityAgentOutputParser.parse(self.SAMPLE_MARKDOWN)
        
        # Convert back to markdown-like string and re-parse
        rebuilt_markdown = f"""## SECURITY FINDINGS

{chr(10).join([f"- **{f.title}**: {f.description}. Severity: {f.severity}. Affected: {', '.join(f.affected_components)}" for f in output1.findings])}

## SECURITY RECOMMENDATIONS

{chr(10).join([f"- **{r.title}**: {r.description}. Severity: {r.severity}. Affected: {', '.join(r.affected_components)}" for r in output1.recommendations])}

## SECURITY SCORE

Overall Security Score: {output1.security_score:.2f}
Confidence Level: {output1.confidence:.2f}

## SUMMARY

{output1.summary}
"""
        
        output2 = SecurityAgentOutputParser.parse(rebuilt_markdown)
        
        # Should be equivalent
        assert len(output2.findings) == len(output1.findings)
        assert len(output2.recommendations) == len(output1.recommendations)
        assert output2.security_score == output1.security_score
