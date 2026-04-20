"""
Pydantic Models for API Request/Response Validation
Type-safe contracts for all API endpoints
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr


class SubmissionRequest(BaseModel):
    """Architecture submission request model"""
    
    title: str = Field(..., description="Architecture proposal title", min_length=1, max_length=256)
    description: str = Field(..., description="Detailed description of the architecture", max_length=5000)
    architect_name: str = Field(..., description="Name of the submitting architect", min_length=1, max_length=128)
    architect_email: EmailStr = Field(..., description="Email of the submitting architect")
    submission_date: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")
    architecture_json: Dict[str, Any] = Field(..., description="Architecture details in JSON format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Microservices Architecture for E-Commerce Platform",
                "description": "Proposed migration from monolith to microservices with Kubernetes",
                "architect_name": "Alice Johnson",
                "architect_email": "alice@acme.com",
                "submission_date": "2026-04-09T10:30:00Z",
                "architecture_json": {
                    "components": ["API Gateway", "Auth Service", "Product Service"],
                    "deployment_model": "kubernetes",
                    "estimated_cost": "$50k/month"
                }
            }
        }


class SubmissionResponse(BaseModel):
    """Response after submission is received"""
    
    submission_id: str = Field(..., description="Unique submission identifier", pattern="^sub_[a-f0-9]{8}$")
    status: Literal["queued", "processing"] = Field(default="queued", description="Current status")
    message: str = Field(..., description="Status message for client")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    status_check_url: str = Field(..., description="URL to check submission status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "submission_id": "sub_1af7e2c9",
                "status": "queued",
                "message": "Submission received and queued for review",
                "estimated_completion": "2026-04-09T10:35:00Z",
                "status_check_url": "/api/v1/status/sub_1af7e2c9"
            }
        }


class SubmissionDimensions(BaseModel):
    """Scores for each review dimension"""
    
    security: float = Field(..., ge=0.0, le=1.0, description="Security score (0.0-1.0)")
    scalability: float = Field(..., ge=0.0, le=1.0, description="Scalability score (0.0-1.0)")
    reliability: float = Field(..., ge=0.0, le=1.0, description="Reliability score (0.0-1.0)")
    data_architecture: float = Field(..., ge=0.0, le=1.0, description="Data architecture score (0.0-1.0)")
    cost_optimization: float = Field(..., ge=0.0, le=1.0, description="Cost optimization score (0.0-1.0)")
    compliance: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0.0-1.0)")


class ReviewFindings(BaseModel):
    """Detailed findings from each review dimension"""
    
    security: Optional[str] = Field(None, description="Security findings and recommendations")
    scalability: Optional[str] = Field(None, description="Scalability findings and recommendations")
    reliability: Optional[str] = Field(None, description="Reliability findings and recommendations")
    data_architecture: Optional[str] = Field(None, description="Data architecture findings")
    cost_optimization: Optional[str] = Field(None, description="Cost optimization findings")
    compliance: Optional[str] = Field(None, description="Compliance findings")


class RoadmapPhase(BaseModel):
    """Single phase in the recommendation roadmap"""
    
    phase: int = Field(..., description="Phase number")
    title: str = Field(..., description="Phase title/objective")
    duration_weeks: int = Field(..., ge=1, description="Estimated duration in weeks")
    items: List[str] = Field(..., description="Action items in this phase")
    priority: Optional[str] = Field(None, description="Phase priority (high/medium/low)")


class RecommendationRoadmap(BaseModel):
    """Phased improvement recommendations"""
    
    executive_summary: str = Field(..., description="High-level summary of recommendations")
    roadmap: List[RoadmapPhase] = Field(..., description="Phased implementation roadmap")
    action_items: List[str] = Field(..., description="Specific action items")
    success_criteria: List[str] = Field(..., description="Criteria for success")
    effort_estimates: Optional[Dict[str, str]] = Field(None, description="Effort estimates per item")


class ReviewResults(BaseModel):
    """Complete review results from ARBPipeline"""
    
    submission_id: str = Field(..., description="Submission identifier")
    status: Literal["processing", "completed", "failed"] = Field(..., description="Current status")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall score (0.0-1.0)")
    approval_decision: Literal["approved", "conditional", "rejected"] = Field(..., description="Approval decision")
    dimensions: SubmissionDimensions = Field(..., description="Scores for each dimension")
    review_findings: ReviewFindings = Field(..., description="Detailed findings from review")
    recommendations: Optional[RecommendationRoadmap] = Field(None, description="Improvement recommendations")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "submission_id": "sub_1af7e2c9",
                "status": "completed",
                "overall_score": 0.82,
                "approval_decision": "approved",
                "dimensions": {
                    "security": 0.85,
                    "scalability": 0.88,
                    "reliability": 0.78,
                    "data_architecture": 0.79,
                    "cost_optimization": 0.81,
                    "compliance": 0.83
                },
                "review_findings": {
                    "security": "Strong encryption practices...",
                    "scalability": "Horizontal scaling well-designed..."
                },
                "recommendations": {
                    "executive_summary": "Overall strong submission...",
                    "roadmap": [
                        {
                            "phase": 1,
                            "title": "Security Hardening",
                            "duration_weeks": 4,
                            "items": ["Implement mTLS", "Add API rate limiting"]
                        }
                    ],
                    "action_items": ["Implement mTLS", "Add rate limiting"],
                    "success_criteria": ["mTLS enforced on all inter-service communication"]
                }
            }
        }


class StatusResponse(BaseModel):
    """Current processing status of a submission"""
    
    submission_id: str = Field(..., description="Submission identifier")
    status: Literal["queued", "processing", "completed", "failed"] = Field(..., description="Current status")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    current_phase: Optional[str] = Field(None, description="Current processing phase")
    active_agents: Optional[List[str]] = Field(None, description="Currently active review agents")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    started_at: Optional[datetime] = Field(None, description="When processing started")
    
    class Config:
        json_schema_extra = {
            "example": {
                "submission_id": "sub_1af7e2c9",
                "status": "processing",
                "progress_percentage": 65,
                "current_phase": "Review Phase",
                "active_agents": ["Security Agent", "Scalability Agent"],
                "estimated_completion": "2026-04-09T10:35:00Z",
                "started_at": "2026-04-09T10:30:30Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standardized error response"""
    
    error: str = Field(..., description="Error type/class name")
    message: str = Field(..., description="Human-friendly error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Missing required field: architect_email",
                "details": {
                    "field": "architect_email",
                    "reason": "field required"
                },
                "request_id": "req_abc123xyz"
            }
        }


class HealthCheck(BaseModel):
    """Health check response"""
    
    status: Literal["healthy", "degraded"] = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-04-09T10:30:00Z",
                "version": "1.0.0"
            }
        }
