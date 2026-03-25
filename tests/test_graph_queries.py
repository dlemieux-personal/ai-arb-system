"""
Test Graph Queries Module
Tests for Neo4j graph queries.
"""

import pytest
from unittest.mock import Mock, patch
from src.knowledge_graph.graph_queries import GraphQueries


class TestGraphQueries:
    """Tests for GraphQueries class"""
    
    def test_find_similar_architectures_query(self):
        """Test similar architectures query generation"""
        query = GraphQueries.find_similar_architectures("microservices")
        assert "MATCH" in query
        assert "SIMILAR_TO" in query
        assert "microservices" in query
    
    def test_find_best_practices_query(self):
        """Test best practices query generation"""
        query = GraphQueries.find_best_practices("security")
        assert "MATCH" in query
        assert "BestPractice" in query
        assert "security" in query
    
    def test_find_patterns_for_technology_query(self):
        """Test patterns for technology query generation"""
        query = GraphQueries.find_patterns_for_technology("kubernetes")
        assert "MATCH" in query
        assert "Pattern" in query
        assert "kubernetes" in query
    
    def test_find_risk_mitigations_query(self):
        """Test risk mitigations query generation"""
        query = GraphQueries.find_risk_mitigations("data breach")
        assert "MATCH" in query
        assert "Risk" in query
        assert "data breach" in query
