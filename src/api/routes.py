"""
API Route Handlers
Endpoints for architecture submission and results retrieval
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import ValidationError

from src.api.models import (
    SubmissionRequest,
    SubmissionResponse,
    StatusResponse,
    ReviewResults,
    ErrorResponse,
    HealthCheck,
)
from src.api.config import settings

logger = logging.getLogger(__name__)

# Router for API v1 endpoints
router = APIRouter(prefix="/api/v1", tags=["v1"])

# In-memory submission state storage (v1.0)
# Format: {submission_id: {"status": "...", "progress": X, "results": {...}}}
SUBMISSIONS_STATE: Dict[str, Any] = {}
STATE_LOCK = asyncio.Lock()


def generate_submission_id() -> str:
    """Generate unique submission ID with 'sub_' prefix"""
    return f"sub_{uuid.uuid4().hex[:8]}"


async def execute_arb_pipeline(submission_id: str, submission_data: SubmissionRequest) -> None:
    """
    Background task: Execute ARBPipeline for a submission
    Updates SUBMISSIONS_STATE with progress and results
    """
    try:
        async with STATE_LOCK:
            SUBMISSIONS_STATE[submission_id]["status"] = "processing"
            SUBMISSIONS_STATE[submission_id]["started_at"] = datetime.utcnow()
        
        # Import here to avoid circular dependencies
        from src.orchestration.arb_pipeline import ARBPipeline
        from pathlib import Path
        
        # Initialize pipeline
        config_path = Path("config")
        pipeline = ARBPipeline(config_path)
        
        logger.info(f"Starting review for submission {submission_id}")
        
        # Simulate phase tracking for demo (replace with actual phase tracking)
        phases = [
            ("Review Phase", 0),
            ("Security Analysis", 20),
            ("Scalability Analysis", 40),
            ("Reliability Analysis", 60),
            ("Data Architecture Review", 75),
            ("Compliance Check", 90),
        ]
        
        for phase_name, progress in phases[:-1]:
            async with STATE_LOCK:
                SUBMISSIONS_STATE[submission_id]["current_phase"] = phase_name
                SUBMISSIONS_STATE[submission_id]["progress_percentage"] = progress
            await asyncio.sleep(1)  # Simulate processing
        
        # Execute pipeline (this is synchronous, so wrap in executor to avoid blocking)
        # For now, using a simple awaitable wrapper
        loop = asyncio.get_event_loop()
        
        # Demo: Create mock results (replace with actual pipeline execution)
        results = {
            "submission_id": submission_id,
            "status": "completed",
            "overall_score": 0.82,
            "approval_decision": "approved",
            "dimensions": {
                "security": 0.85,
                "scalability": 0.88,
                "reliability": 0.78,
                "data_architecture": 0.79,
                "cost_optimization": 0.81,
                "compliance": 0.83,
            },
            "review_findings": {
                "security": "Strong encryption practices and security controls in place.",
                "scalability": "Horizontal scaling well-designed with load balancing.",
                "reliability": "Good redundancy and failover mechanisms.",
                "data_architecture": "Appropriate data modeling and partitioning strategy.",
                "cost_optimization": "Infrastructure costs optimized with reserved instances.",
                "compliance": "Meets regulatory requirements and compliance standards.",
            },
            "recommendations": {
                "executive_summary": "Overall strong architecture submission with good design practices.",
                "roadmap": [
                    {
                        "phase": 1,
                        "title": "Security Hardening",
                        "duration_weeks": 4,
                        "items": ["Implement mTLS", "Add API rate limiting", "Enable encryption in transit"],
                    }
                ],
                "action_items": ["Implement mTLS", "Add rate limiting", "Enable encryption"],
                "success_criteria": ["mTLS enforced", "Rate limits in place", "All data encrypted"],
            },
            "completed_at": datetime.utcnow().isoformat(),
        }
        
        async with STATE_LOCK:
            SUBMISSIONS_STATE[submission_id]["status"] = "completed"
            SUBMISSIONS_STATE[submission_id]["progress_percentage"] = 100
            SUBMISSIONS_STATE[submission_id]["results"] = results
            SUBMISSIONS_STATE[submission_id]["completed_at"] = datetime.utcnow()
        
        logger.info(f"Completed review for submission {submission_id}")
        
    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {str(e)}", exc_info=True)
        async with STATE_LOCK:
            SUBMISSIONS_STATE[submission_id]["status"] = "failed"
            SUBMISSIONS_STATE[submission_id]["error_message"] = str(e)


@router.post(
    "/submissions",
    response_model=SubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit architecture for review",
    description="Accept a new architecture submission and queue it for AI-powered review",
)
async def submit_architecture(
    submission: SubmissionRequest,
    background_tasks: BackgroundTasks,
) -> SubmissionResponse:
    """
    Submit a new architecture for review
    
    Returns 202 Accepted with submission_id for polling
    Background task executes ARBPipeline asynchronously
    """
    # Generate unique submission ID
    submission_id = generate_submission_id()
    
    # Initialize submission state
    async with STATE_LOCK:
        SUBMISSIONS_STATE[submission_id] = {
            "submission_id": submission_id,
            "status": "queued",
            "progress_percentage": 0,
            "created_at": datetime.utcnow(),
            "submission_data": submission.dict(),
        }
    
    # Queue background task for processing
    background_tasks.add_task(execute_arb_pipeline, submission_id, submission)
    
    # Calculate estimated completion (rough estimate: current time + timeout)
    estimated_completion = datetime.utcnow() + timedelta(
        seconds=settings.submission_timeout_seconds
    )
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="queued",
        message="Submission received and queued for review",
        estimated_completion=estimated_completion,
        status_check_url=f"/api/v1/status/{submission_id}",
    )


@router.get(
    "/status/{submission_id}",
    response_model=StatusResponse,
    summary="Check submission status",
    description="Poll the current processing status of a submission",
)
async def get_submission_status(submission_id: str) -> StatusResponse:
    """
    Get current processing status and progress
    
    Returns:
    - 200 OK if submission found (may be queued, processing, or completed)
    - 404 Not Found if submission_id doesn't exist
    """
    async with STATE_LOCK:
        if submission_id not in SUBMISSIONS_STATE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found",
            )
        
        state = SUBMISSIONS_STATE[submission_id]
    
    return StatusResponse(
        submission_id=submission_id,
        status=state.get("status", "unknown"),
        progress_percentage=state.get("progress_percentage"),
        current_phase=state.get("current_phase"),
        active_agents=state.get("active_agents"),
        estimated_completion=state.get("estimated_completion"),
        started_at=state.get("started_at"),
    )


@router.get(
    "/results/{submission_id}",
    response_model=ReviewResults,
    summary="Get review results",
    description="Retrieve completed review results and recommendations",
)
async def get_review_results(submission_id: str) -> ReviewResults:
    """
    Get completed review results
    
    Returns:
    - 200 OK with results if review is completed
    - 202 Accepted if review is still processing
    - 404 Not Found if submission_id doesn't exist
    """
    async with STATE_LOCK:
        if submission_id not in SUBMISSIONS_STATE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found",
            )
        
        state = SUBMISSIONS_STATE[submission_id]
    
    # Check if still processing
    if state.get("status") == "processing":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Review still in progress. Use /status endpoint to poll.",
        )
    
    # Check if failed
    if state.get("status") == "failed":
        return ReviewResults(
            submission_id=submission_id,
            status="failed",
            overall_score=0.0,
            approval_decision="rejected",
            dimensions={
                "security": 0.0,
                "scalability": 0.0,
                "reliability": 0.0,
                "data_architecture": 0.0,
                "cost_optimization": 0.0,
                "compliance": 0.0,
            },
            review_findings={},
            error_message=state.get("error_message"),
            completed_at=state.get("completed_at"),
        )
    
    # Return completed results
    results = state.get("results")
    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Results not found for completed submission",
        )
    
    return ReviewResults(**results)


@router.get(
    "/health",
    response_model=HealthCheck,
    summary="Health check",
    description="Check API service health",
)
async def health_check() -> HealthCheck:
    """
    Health check endpoint
    
    Returns service status and version
    """
    return HealthCheck(
        status="healthy",
        version=settings.api_version,
    )
