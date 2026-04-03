"""
Graph Client Factory
Provides utilities for creating and managing Neo4j client instances.
"""

import os
from typing import Optional

from src.knowledge_graph.neo4j_client import Neo4jClient


def create_neo4j_client() -> Optional[Neo4jClient]:
    """
    Create a Neo4j client from environment variables.
    
    Requires:
    - NEO4J_URI: Connection URI (e.g., bolt://localhost:7687)
    - NEO4J_USER: Username
    - NEO4J_PASSWORD: Password
    
    Returns:
        Neo4jClient instance or None if configuration is missing
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    
    if not all([uri, user, password]):
        return None
    
    try:
        return Neo4jClient(uri or '', user or '', password or '')
    except Exception:
        return None


# Global client instance (can be initialized once and reused)
_client: Optional[Neo4jClient] = None


def get_neo4j_client() -> Optional[Neo4jClient]:
    """
    Get or create the global Neo4j client instance.
    
    Returns:
        Neo4jClient instance or None
    """
    global _client
    if _client is None:
        _client = create_neo4j_client()
    return _client


def close_neo4j_client():
    """Close the global Neo4j client instance."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
