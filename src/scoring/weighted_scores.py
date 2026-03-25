"""
Weighted Scores Module
Calculates weighted scores across review dimensions.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class WeightedScore:
    """Score with weight applied"""
    
    dimension: str
    raw_score: float
    weight: float
    weighted_score: float


class WeightedScoreCalculator:
    """Calculates weighted scores for review dimensions"""
    
    def __init__(self, weights: Dict[str, float]):
        """
        Initialize the calculator
        
        Args:
            weights: Dictionary mapping dimensions to their weights
        """
        self.weights = weights
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to approximately 1.0"""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, but sum to {total}")
    
    def calculate_weighted_score(self, dimension: str, raw_score: float) -> WeightedScore:
        """
        Calculate weighted score for a dimension
        
        Args:
            dimension: Name of the dimension
            raw_score: Raw score (0.0 to 1.0)
            
        Returns:
            WeightedScore object
        """
        if dimension not in self.weights:
            raise ValueError(f"Unknown dimension: {dimension}")
        
        weight = self.weights[dimension]
        weighted_score = raw_score * weight
        
        return WeightedScore(
            dimension=dimension,
            raw_score=raw_score,
            weight=weight,
            weighted_score=weighted_score
        )
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """
        Calculate overall score from dimension scores
        
        Args:
            dimension_scores: Dictionary mapping dimensions to raw scores
            
        Returns:
            Overall weighted score (0.0 to 1.0)
        """
        total = sum(
            self.calculate_weighted_score(dim, score).weighted_score
            for dim, score in dimension_scores.items()
        )
        return round(total, 2)
