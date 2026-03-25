"""
Recommendation Data Models
Data structures for architectural improvement recommendations.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    CRITICAL = 1  # Must be addressed immediately
    HIGH = 2      # Should be addressed in next phase
    MEDIUM = 3    # Should be considered for improvement
    LOW = 4       # Nice to have, consider for future


class ImplementationEffort(Enum):
    """Effort estimation for implementation"""
    TRIVIAL = 1      # <1 day
    SMALL = 2        # 1-3 days
    MEDIUM = 3       # 1-2 weeks
    LARGE = 4        # 2-4 weeks
    XLARGE = 5       # >1 month


@dataclass
class Recommendation:
    """Individual architectural recommendation"""
    
    id: str                                    # Unique identifier
    domain: str                                # Review domain (security, scalability, etc.)
    title: str                                 # Short recommendation title
    description: str                           # Detailed description of the issue and solution
    affected_component: str                    # Which component(s) are affected
    priority: RecommendationPriority          # Priority level
    effort: ImplementationEffort              # Implementation effort estimate
    impact: str                                # Expected impact (e.g., "90% reduction in vulnerabilities")
    rationale: str                             # Why this recommendation is important
    precedent: Optional[str] = None           # Reference to similar architecture/pattern
    implementation_steps: List[str] = field(default_factory=list)  # How to implement
    success_criteria: List[str] = field(default_factory=list)      # How to measure success
    estimated_timeline: Optional[str] = None  # Timeline for implementation


@dataclass
class ActionItem:
    """Concrete action item derived from recommendations"""
    
    id: str
    title: str
    description: str
    priority: RecommendationPriority
    effort: ImplementationEffort
    related_recommendations: List[str]        # Recommendation IDs this addresses
    owners: List[str] = field(default_factory=list)  # Who should own this
    dependencies: List[str] = field(default_factory=list)  # Other action items needed first
    success_criteria: List[str] = field(default_factory=list)
    timeline: Optional[str] = None


@dataclass
class RecommendationSummary:
    """Summary of all recommendations"""
    
    total_recommendations: int
    by_priority: dict                         # Count by priority level
    by_domain: dict                           # Count by domain
    critical_count: int                       # Number of critical items
    high_count: int                           # Number of high priority items
    estimated_total_effort: str               # Total effort estimate
    quick_wins: List[Recommendation]          # Recommendations with low effort, high impact
    phase_1_items: List[Recommendation]       # Phase 1 improvements
    phase_2_items: List[Recommendation]       # Phase 2 improvements
    long_term_items: List[Recommendation]     # Long-term improvements


@dataclass
class RecommendationOutput:
    """Complete recommendation output"""
    
    submission_id: str
    recommendations: List[Recommendation]
    action_items: List[ActionItem]
    summary: RecommendationSummary
    orchestrator_summary: str                 # Executive summary from orchestrator
    markdown_report: str                      # Formatted for PR comments
