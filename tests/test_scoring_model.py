"""
Test Scoring Model Module
Tests for scoring and evaluation logic.
"""

import pytest
from pathlib import Path
from src.scoring.scoring_model import ScoringModel, ArchitectureScore


class TestScoringModel:
    """Tests for ScoringModel class"""
    
    @pytest.fixture
    def scoring_model(self):
        """Fixture for initializing scoring model"""
        weights_path = Path(__file__).parent.parent / "config" / "scoring_weights.yaml"
        thresholds_path = Path(__file__).parent.parent / "config" / "review_thresholds.yaml"
        return ScoringModel(weights_path, thresholds_path)
    
    def test_calculate_overall_score(self, scoring_model):
        """Test overall score calculation"""
        dimension_scores = {
            'security': 0.85,
            'scalability': 0.90,
            'reliability': 0.80,
            'data_architecture': 0.75,
            'cost_optimization': 0.70,
            'compliance': 0.88
        }
        
        overall_score = scoring_model.calculate_overall_score(dimension_scores)
        assert 0.0 <= overall_score <= 1.0
    
    def test_determine_recommendation_approved(self, scoring_model):
        """Test recommendation determination for approved"""
        recommendation = scoring_model.determine_recommendation(0.85)
        assert recommendation == 'approved'
    
    def test_determine_recommendation_conditional(self, scoring_model):
        """Test recommendation determination for conditional approval"""
        recommendation = scoring_model.determine_recommendation(0.72)
        assert recommendation == 'conditional'
    
    def test_determine_recommendation_rejected(self, scoring_model):
        """Test recommendation determination for rejected"""
        recommendation = scoring_model.determine_recommendation(0.50)
        assert recommendation == 'rejected'
