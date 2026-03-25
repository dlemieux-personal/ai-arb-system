"""
Graph Query Tool
Provides relationship and connectivity analysis using knowledge graph queries.
"""

from crewai.tools import tool
from typing import Optional, List, Dict, Any
import json

# Import the retrieval and graph services
try:
    from src.knowledge_graph.graph_client_factory import get_neo4j_client
    from src.vector_memory.vector_store_factory import get_vector_store
    from src.vector_memory.retrieval_service import RetrievalService
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


@tool("Query Knowledge Graph")
def graph_query_tool(query: str, query_type: str = "general") -> str:
    """
    Query the knowledge graph to explore architectural relationships and insights.
    
    This tool retrieves structured architectural knowledge from the graph, including
    patterns, best practices, similar past architectures, and risk factors.
    Use this to find precedents and guidance relevant to your review.
    
    Args:
        query: The description of what you want to explore.
               Examples: "microservices architectures", "event-driven patterns",
                        "API gateway best practices", "risks for scalability"
        query_type: Type of query - 'patterns', 'practices', 'similar', 'risks', 
                   or 'general' (default: 'general' retrieves best practices)
        
    Returns:
        Structured information about architectural patterns, practices, and relationships
    """
    if not GRAPH_AVAILABLE:
        return "Graph queries not available - Neo4j service not configured."
    
    try:
        # Initialize retrieval service
        neo4j_client = get_neo4j_client()
        vector_store = get_vector_store()
        retrieval = RetrievalService(vector_store=vector_store, neo4j_client=neo4j_client)
        
        if not neo4j_client:
            return "Neo4j graph database not available."
        
        results = []
        
        # Execute different queries based on type
        if query_type == "patterns" or query_type == "general":
            # Extract keywords from query
            keywords = query.lower().split()
            patterns = retrieval.retrieve_relevant_patterns(keywords, k=5)
            if patterns:
                results.append("\n=== RELEVANT PATTERNS ===")
                for i, pattern in enumerate(patterns, 1):
                    results.append(
                        f"[{i}] {pattern.get('name', 'Unknown Pattern')}\n"
                        f"    Description: {pattern.get('description', 'N/A')}\n"
                        f"    Domain: {pattern.get('category', 'N/A')}"
                    )
        
        if query_type == "practices" or query_type == "general":
            # Extract domain from query
            domains = ['architecture', 'scalability', 'reliability', 'security', 'data', 'cost']
            matching_domain = None
            for domain in domains:
                if domain in query.lower():
                    matching_domain = domain
                    break
            
            if matching_domain:
                practices = retrieval.retrieve_best_practices(matching_domain, k=5)
                if practices:
                    results.append("\n=== BEST PRACTICES ===")
                    for i, practice in enumerate(practices, 1):
                        results.append(
                            f"[{i}] {practice.get('title', 'Unknown Practice')}\n"
                            f"    Description: {practice.get('description', 'N/A')}\n"
                            f"    Domain: {practice.get('domain', 'N/A')}"
                        )
        
        if query_type == "general":
            # Also get general architecture notes
            from src.knowledge_graph.graph_schema import GraphSchema
            archs = neo4j_client.find_nodes(GraphSchema.ARCHITECTURE)
            if archs:
                results.append("\n=== REFERENCE ARCHITECTURES ===")
                for i, arch in enumerate(archs[:3], 1):
                    results.append(
                        f"[{i}] {arch.get('name', 'Unknown')}\n"
                        f"    {arch.get('description', 'N/A')[:100]}..."
                    )
        
        if results:
            return "\n".join(results)
        else:
            return f"No graph results found for query: '{query}'. Try searching for specific patterns or practices."
        
    except Exception as e:
        return f"Error querying knowledge graph: {str(e)}"
