"""
Structured output schemas for AI agent reviews.
Each agent follows a consistent output format to ensure reliable parsing and validation.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Security Agent Output Schema
# ============================================================================

class SecurityFinding(BaseModel):
    """A specific security issue identified during review"""
    
    title: str = Field(
        ..., 
        description="Clear title of the security finding",
        examples=["Missing encryption in transit for API calls"]
    )
    description: str = Field(
        ...,
        description="Detailed description of the security issue and why it matters",
        examples=["API communication between services uses HTTP without TLS..."]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Severity level of the finding",
        examples=["high"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="List of architecture components affected by this finding",
        examples=[["API Gateway", "Authentication Service", "Data Store"]]
    )


class SecurityRecommendation(BaseModel):
    """A specific, actionable security recommendation"""
    
    title: str = Field(
        ...,
        description="Clear title of the recommendation",
        examples=["Implement TLS 1.3 encryption for all service-to-service communication"]
    )
    description: str = Field(
        ...,
        description="Detailed explanation of the recommendation and its rationale",
        examples=["Enable mutual TLS (mTLS) with certificate rotation..."]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Priority level of this recommendation",
        examples=["high"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="Components that need to implement this recommendation",
        examples=[["API Gateway", "Load Balancer"]]
    )


class SecurityAgentOutput(BaseModel):
    """Complete structured output from the Security review agent"""
    
    findings: List[SecurityFinding] = Field(
        default_factory=list,
        description="List of security findings identified in the architecture"
    )
    recommendations: List[SecurityRecommendation] = Field(
        default_factory=list,
        description="List of actionable security recommendations"
    )
    security_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall security score for the architecture (0.0-1.0)",
        examples=[0.75, 0.82]
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level in this assessment (0.0-1.0)"
    )
    summary: str = Field(
        default="",
        description="Brief summary of security posture and key concerns"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "findings": [
                    {
                        "title": "Missing encryption in transit",
                        "description": "API communication uses HTTP without TLS",
                        "severity": "high",
                        "affected_components": ["API Gateway", "Services"]
                    }
                ],
                "recommendations": [
                    {
                        "title": "Implement TLS encryption",
                        "description": "Enable TLS 1.3 for all connections",
                        "severity": "high",
                        "affected_components": ["API Gateway"]
                    }
                ],
                "security_score": 0.72,
                "confidence": 0.89,
                "summary": "Strong security foundation with encryption gaps"
            }
        }


# ============================================================================
# Placeholder Schemas for Other Agents (to be implemented)
# ============================================================================

class ScalabilityAgentOutput(BaseModel):
    """Placeholder for scalability agent output schema"""
    # TODO: Implement in next PR
    pass


class ReliabilityAgentOutput(BaseModel):
    """Placeholder for reliability agent output schema"""
    # TODO: Implement in next PR
    pass


class DataArchitectureAgentOutput(BaseModel):
    """Placeholder for data architecture agent output schema"""
    # TODO: Implement in next PR
    pass


class CostOptimizationAgentOutput(BaseModel):
    """Placeholder for cost optimization agent output schema"""
    # TODO: Implement in next PR
    pass


class ComplianceAgentOutput(BaseModel):
    """Placeholder for compliance agent output schema"""
    # TODO: Implement in next PR
    pass
