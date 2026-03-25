"""
Approval Logic Module
Implements decision logic for architecture approval.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ApprovalDecision:
    """Architecture approval decision"""
    
    status: str  # 'approved', 'conditional', 'rejected'
    overall_score: float
    rationale: str
    escalation_required: bool
    escalation_reason: str = None


class ApprovalEngine:
    """Implements approval decision logic"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        """
        Initialize the approval engine
        
        Args:
            thresholds: Threshold configuration
        """
        self.thresholds = thresholds
    
    def make_decision(self, 
                     overall_score: float,
                     dimension_scores: Dict[str, float],
                     critical_findings: Dict[str, list]) -> ApprovalDecision:
        """
        Make approval decision
        
        Args:
            overall_score: Overall architecture score
            dimension_scores: Individual dimension scores
            critical_findings: Critical findings by dimension
            
        Returns:
            ApprovalDecision object
        """
        # Check for critical compliance failures
        if critical_findings.get('compliance', []):
            return ApprovalDecision(
                status='rejected',
                overall_score=overall_score,
                rationale='Critical compliance issues identified',
                escalation_required=True,
                escalation_reason='Compliance team review required'
            )
        
        # Check overall score thresholds
        thresholds = self.thresholds['thresholds']['overall_score']
        
        if overall_score >= thresholds['approved']['minimum']:
            return ApprovalDecision(
                status='approved',
                overall_score=overall_score,
                rationale='Architecture meets approval criteria',
                escalation_required=False
            )
        elif overall_score >= thresholds['conditional_approval']['minimum']:
            return ApprovalDecision(
                status='conditional',
                overall_score=overall_score,
                rationale='Architecture approved with recommended remediation',
                escalation_required=False
            )
        else:
            return ApprovalDecision(
                status='rejected',
                overall_score=overall_score,
                rationale='Architecture does not meet minimum quality standards',
                escalation_required=True,
                escalation_reason='Architecture team review required'
            )
