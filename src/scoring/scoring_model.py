"""
Scoring Model Module
Core scoring logic for evaluating architectures.
"""

from dataclasses import dataclass
from typing import Dict, Any
import yaml
from pathlib import Path


@dataclass
class DimensionScore:
    """Score for a single review dimension"""
    
    dimension: str
    score: float  # 0.0 to 1.0
    weight: float
    findings: str
    critical_issues: list[str]


@dataclass
class ArchitectureScore:
    """Overall architecture evaluation score"""
    
    submission_id: str
    overall_score: float  # 0.0 to 1.0
    dimension_scores: Dict[str, DimensionScore]
    recommendation: str  # approved, conditional, rejected
    rationale: str


class ScoringModel:
    """Main scoring model for architecture evaluation"""
    
    def __init__(self, weights_path: Path, thresholds_path: Path):
        """
        Initialize the scoring model
        
        Args:
            weights_path: Path to scoring weights YAML file
            thresholds_path: Path to thresholds YAML file
        """
        self.weights_path = weights_path
        self.thresholds_path = thresholds_path
        self.weights = self._load_weights()
        self.thresholds = self._load_thresholds()
    
    def _load_weights(self) -> Dict[str, float]:
        """Load scoring weights from YAML"""
        with open(self.weights_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return {dim: config['review_dimensions'][dim]['weight'] 
                for dim in config['review_dimensions']}
    
    def _load_thresholds(self) -> Dict[str, Any]:
        """Load thresholds from YAML"""
        with open(self.thresholds_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """
        Calculate overall score from dimension scores
        
        Args:
            dimension_scores: Dictionary mapping dimension names to scores
            
        Returns:
            Overall score (0.0 to 1.0)
        """
        total_weighted_score = sum(
            dimension_scores.get(dim, 0) * self.weights.get(dim, 0)
            for dim in self.weights.keys()
        )
        return round(total_weighted_score, 2)
    
    def determine_recommendation(self, overall_score: float) -> str:
        """
        Determine approval recommendation based on score
        
        Args:
            overall_score: Overall architecture score
            
        Returns:
            Recommendation: 'approved', 'conditional', or 'rejected'
        """
        thresholds = self.thresholds['thresholds']['overall_score']
        
        if overall_score >= thresholds['approved']['minimum']:
            return 'approved'
        elif overall_score >= thresholds['conditional_approval']['minimum']:
            return 'conditional'
        else:
            return 'rejected'
