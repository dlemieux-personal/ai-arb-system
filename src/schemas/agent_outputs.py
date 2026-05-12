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
# Scalability Agent Output Schema
# ============================================================================

class ScalabilityBottleneck(BaseModel):
    """A specific scalability bottleneck or constraint identified during review"""
    
    title: str = Field(
        ..., 
        description="Clear title of the scalability bottleneck",
        examples=["Database connection pool exhaustion under load"]
    )
    description: str = Field(
        ...,
        description="Detailed description of the bottleneck and its impact on scalability",
        examples=["Current configuration allows max 100 concurrent connections..."]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Severity level of the bottleneck",
        examples=["high"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="List of architecture components affected by this bottleneck",
        examples=[["Database", "Application Server", "Connection Pool"]]
    )


class ScalabilityRecommendation(BaseModel):
    """A specific, actionable scalability recommendation"""
    
    title: str = Field(
        ...,
        description="Clear title of the recommendation",
        examples=["Implement connection pooling with auto-scaling"]
    )
    description: str = Field(
        ...,
        description="Detailed explanation of the recommendation and its impact",
        examples=["Add a connection pool manager with dynamic sizing..."]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Priority level of this recommendation",
        examples=["high"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="Components that need to implement this recommendation",
        examples=[["Database", "Connection Pool Manager"]]
    )


class ScalabilityAgentOutput(BaseModel):
    """Complete structured output from the Scalability review agent"""
    
    bottlenecks: List[ScalabilityBottleneck] = Field(
        default_factory=list,
        description="List of scalability bottlenecks identified in the architecture"
    )
    recommendations: List[ScalabilityRecommendation] = Field(
        default_factory=list,
        description="List of actionable scalability recommendations"
    )
    scalability_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall scalability score for the architecture (0.0-1.0)",
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
        description="Brief summary of scalability posture and key concerns"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bottlenecks": [
                    {
                        "title": "Database connection pool exhaustion",
                        "description": "Current configuration allows max 100 concurrent connections",
                        "severity": "high",
                        "affected_components": ["Database", "Connection Pool"]
                    }
                ],
                "recommendations": [
                    {
                        "title": "Implement connection pooling",
                        "description": "Add dynamic connection pool with auto-scaling",
                        "severity": "high",
                        "affected_components": ["Database", "Pool Manager"]
                    }
                ],
                "scalability_score": 0.68,
                "confidence": 0.87,
                "summary": "Architecture has good horizontal scaling but database bottleneck limits overall scalability"
            }
        }


class ReliabilityFinding(BaseModel):
    """A specific reliability issue identified during review"""
    title: str = Field(
        ..., 
        description="Clear title of the reliability finding",
        examples=["Single point of failure in the primary database cluster"]
    )
    description: str = Field(
        ...,
        description="Detailed description of the reliability issue and its impact",
        examples=["The primary database cluster does not have a standby replica in another availability zone"]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ..., 
        description="Severity level of the finding",
        examples=["high"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="List of architecture components affected by this finding",
        examples=[['Database Cluster', 'Load Balancer']]
    )


class ReliabilityFailureMode(BaseModel):
    """A specific failure mode and its potential impact"""
    title: str = Field(
        ..., 
        description="Clear title of the failure mode",
        examples=["Regional outage due to single-region deployment"]
    )
    description: str = Field(
        ...,
        description="Description of the failure mode and how it can occur",
        examples=["An availability zone failure would bring down the entire application layer"]
    )
    impact: str = Field(
        ...,
        description="Potential impact of this failure mode on the system",
        examples=["Complete service outage for all customers in the affected region"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="Components that are exposed to this failure mode",
        examples=[['Application Servers', 'Database', 'Messaging Queue']]
    )


class ReliabilityRecommendation(BaseModel):
    """A specific, actionable reliability recommendation"""
    title: str = Field(
        ...,
        description="Clear title of the recommendation",
        examples=["Enable cross-region failover for the database"]
    )
    description: str = Field(
        ...,
        description="Detailed explanation of the recommendation and its rationale",
        examples=["Add a secondary database replica in a second region with automated failover"]
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Priority level of this recommendation",
        examples=["critical"]
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="Components that need to implement this recommendation",
        examples=[['Database', 'Failover Automation']]
    )


class ReliabilityAgentOutput(BaseModel):
    """Complete structured output from the Reliability review agent"""
    findings: List[ReliabilityFinding] = Field(
        default_factory=list,
        description="List of reliability findings identified in the architecture"
    )
    failure_modes: List[ReliabilityFailureMode] = Field(
        default_factory=list,
        description="List of identified failure modes and their potential impact"
    )
    recommendations: List[ReliabilityRecommendation] = Field(
        default_factory=list,
        description="List of actionable reliability recommendations"
    )
    reliability_score: float = Field(
        ..., 
        ge=0.0,
        le=1.0,
        description="Overall reliability score for the architecture (0.0-1.0)",
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
        description="Brief summary of reliability posture and key concerns"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "findings": [
                    {
                        "title": "Single point of failure in database cluster",
                        "description": "The primary database cluster is deployed in one availability zone without a standby replica.",
                        "severity": "high",
                        "affected_components": ["Database Cluster", "Application Layer"]
                    }
                ],
                "failure_modes": [
                    {
                        "title": "Availability zone outage",
                        "description": "Loss of a single availability zone would take down the entire service.",
                        "impact": "Service outage for the application and data layer",
                        "affected_components": ["Application Servers", "Database Cluster"]
                    }
                ],
                "recommendations": [
                    {
                        "title": "Add cross-region failover",
                        "description": "Deploy standby replicas in a second region and automate failover detection.",
                        "severity": "critical",
                        "affected_components": ["Database", "Traffic Management"]
                    }
                ],
                "reliability_score": 0.70,
                "confidence": 0.88,
                "summary": "The architecture shows good reliability practices but is exposed to single-region failure risks."
            }
        }


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
