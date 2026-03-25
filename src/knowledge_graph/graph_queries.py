"""
Graph Queries Module
Pre-built Cypher queries for architecture knowledge retrieval.
"""

from typing import Dict, List, Any


class GraphQueries:
    """Collection of Cypher queries for knowledge retrieval"""
    
    @staticmethod
    def find_similar_architectures(pattern: str, limit: int = 5) -> str:
        """
        Find similar past architectures
        
        Args:
            pattern: Pattern to search for
            limit: Maximum number of results
            
        Returns:
            Cypher query string
        """
        return f"""
            MATCH (a:Architecture)-[:SIMILAR_TO*..2]-(similar:Architecture)
            WHERE a.name CONTAINS '{pattern}'
            RETURN similar.id, similar.name, similar.description
            LIMIT {limit}
        """
    
    @staticmethod
    def find_best_practices(domain: str) -> str:
        """
        Find best practices for a domain
        
        Args:
            domain: Domain to search for
            
        Returns:
            Cypher query string
        """
        return f"""
            MATCH (bp:BestPractice)
            WHERE bp.domain = '{domain}'
            RETURN bp.id, bp.title, bp.description
        """
    
    @staticmethod
    def find_patterns_for_technology(tech: str) -> str:
        """
        Find architectural patterns for a technology
        
        Args:
            tech: Technology name
            
        Returns:
            Cypher query string
        """
        return f"""
            MATCH (t:Technology)-[:USED_IN]->(p:Pattern)
            WHERE t.name = '{tech}'
            RETURN p.id, p.name, p.description
        """
    
    @staticmethod
    def find_risk_mitigations(risk: str) -> str:
        """
        Find mitigations for a specific risk
        
        Args:
            risk: Risk description
            
        Returns:
            Cypher query string
        """
        return f"""
            MATCH (r:Risk)-[:MITIGATED_BY]->(bp:BestPractice)
            WHERE r.description CONTAINS '{risk}'
            RETURN r.id, r.severity, bp.title, bp.description
        """
