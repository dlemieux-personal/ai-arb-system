"""
Review Tasks Module
Defines tasks for agent execution during the review process.
"""

from typing import Optional, Dict, Any


class ReviewTask:
    """Base class for review tasks"""
    
    def __init__(self, agent_type: str, submission_id: str):
        """
        Initialize a review task
        
        Args:
            agent_type: Type of agent performing the review
            submission_id: ID of the submission being reviewed
        """
        self.agent_type = agent_type
        self.submission_id = submission_id
    
    def get_task_description(self) -> str:
        """Get the task description for the agent"""
        # TODO: Implement task description logic
        raise NotImplementedError()


class SecurityReviewTask(ReviewTask):
    """Task for security review"""
    
    def get_task_description(self) -> str:
        return f"Review the security architecture of submission {self.submission_id}"


class ScalabilityReviewTask(ReviewTask):
    """Task for scalability review"""
    
    def get_task_description(self) -> str:
        return f"Review the scalability design of submission {self.submission_id}"


class ReliabilityReviewTask(ReviewTask):
    """Task for reliability review"""
    
    def get_task_description(self) -> str:
        return f"Review the reliability mechanisms of submission {self.submission_id}"


class DataArchitectureReviewTask(ReviewTask):
    """Task for data architecture review"""
    
    def get_task_description(self) -> str:
        return f"Review the data architecture of submission {self.submission_id}"


class CostOptimizationReviewTask(ReviewTask):
    """Task for cost optimization review"""
    
    def get_task_description(self) -> str:
        return f"Review the cost optimization of submission {self.submission_id}"


class ComplianceReviewTask(ReviewTask):
    """Task for compliance review"""
    
    def get_task_description(self) -> str:
        return f"Review the compliance posture of submission {self.submission_id}"
