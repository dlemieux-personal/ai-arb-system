"""
Test Neo4j Tool
Verifies basic behavior of the Neo4j query tool.
"""

import os
from src.tools.neo4j_tool import neo4j_query_tool


def test_neo4j_tool_no_config(monkeypatch):
    """If environment variables are missing, tool should indicate not configured."""
    # ensure env vars are not set
    for var in ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']:
        monkeypatch.delenv(var, raising=False)
    # decorator returns Tool object; call underlying function directly
    result = neo4j_query_tool.func("MATCH (n) RETURN n LIMIT 1")
    assert "not configured" in result.lower()


def test_neo4j_tool_bad_query(monkeypatch):
    """When driver is unavailable, gracefully handle import error."""
    # simulate missing neo4j driver by monkeypatching GraphDatabase to None
    import src.tools.neo4j_tool as nt
    monkeypatch.setattr(nt, 'GraphDatabase', None)
    result = neo4j_query_tool.func("MATCH (n) RETURN n LIMIT 1")
    assert "not configured" in result.lower()
