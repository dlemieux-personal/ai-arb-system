"""
Graph Schema Module
Defines the Neo4j graph schema for architecture knowledge.
"""

from typing import Dict, List


class GraphSchema:
    """Defines Neo4j graph schema for architecture knowledge"""
    
    # Node labels
    ARCHITECTURE = "Architecture"
    PATTERN = "Pattern"
    BEST_PRACTICE = "BestPractice"
    TECHNOLOGY = "Technology"
    RISK = "Risk"
    REVIEW = "Review"
    FINDING = "Finding"
    
    # Relationship types
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    MITIGATES = "MITIGATES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    SIMILAR_TO = "SIMILAR_TO"
    REFERENCES = "REFERENCES"
    
    def get_node_properties(self, label: str) -> Dict[str, str]:
        """Get property definitions for a node label"""
        properties = {
            self.ARCHITECTURE: {
                'id': 'string',
                'name': 'string',
                'description': 'string',
                'created_at': 'datetime',
                'review_id': 'string',
            },
            self.PATTERN: {
                'id': 'string',
                'name': 'string',
                'description': 'string',
                'category': 'string',
            },
            self.BEST_PRACTICE: {
                'id': 'string',
                'title': 'string',
                'description': 'string',
                'domain': 'string',
            },
            self.TECHNOLOGY: {
                'name': 'string',
                'type': 'string',
                'description': 'string',
            },
            self.RISK: {
                'id': 'string',
                'description': 'string',
                'severity': 'string',
                'mitigation': 'string',
            },
            self.REVIEW: {
                'id': 'string',
                'submission_id': 'string',
                'status': 'string',
                'date': 'datetime',
            },
            self.FINDING: {
                'id': 'string',
                'type': 'string',
                'severity': 'string',
                'description': 'string',
            }
        }
        return properties.get(label, {})
