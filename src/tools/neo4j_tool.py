"""
Neo4j Graph Tool
Provides a tool for executing Cypher queries against a Neo4j knowledge graph.
"""

import os
from typing import Dict, Any, Optional

from crewai.tools import tool

# load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from neo4j import GraphDatabase, exceptions
except ImportError:
    GraphDatabase = None
    exceptions = None


def _get_driver():
    """Return a Neo4j driver if configuration is available, else None."""
    if GraphDatabase is None:
        return None
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pwd = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pwd):
        return None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        return driver
    except Exception:
        return None


@tool("Run Cypher Query")
def neo4j_query_tool(query: str, parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Execute a Cypher query against the Neo4j database.

    Args:
        query: The Cypher query string to run.
        parameters: Optional dictionary of query parameters.

    Returns:
        A string summarizing the results or an error message.
    """
    driver = _get_driver()
    if driver is None:
        return "Neo4j connection not configured. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD."

    try:
        with driver.session() as session:
            result = session.run(query, parameters or {})
            records = [dict(rec) for rec in result]
            if records:
                formatted = "\n".join(str(r) for r in records)
                return f"Query returned {len(records)} records:\n{formatted}"
            else:
                return "Query executed successfully; no records returned."
    except Exception as e:
        return f"Error executing Neo4j query: {e}"
