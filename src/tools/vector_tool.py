"""
Vector Search Tool
Provides semantic search capabilities using vector embeddings.
"""

from crewai.tools import tool
from typing import Optional, List, Dict, Any
import json

# Import the retrieval service
try:
    from src.vector_memory.vector_store_factory import get_vector_store
    from src.vector_memory.embedding_service import EmbeddingService
    from src.knowledge_graph.graph_client_factory import get_neo4j_client
    from src.vector_memory.retrieval_service import RetrievalService
    RETRIEVAL_AVAILABLE = True
except ImportError:
    RETRIEVAL_AVAILABLE = False


@tool("Search Knowledge Base")
def vector_search_tool(query: str, search_type: str = "general", limit: int = 5) -> str:
    """
    Search the knowledge base using semantic similarity.
    
    This tool performs vector-based semantic search across all indexed knowledge,
    including architecture patterns, best practices, and previous architectural decisions.
    Use this tool to find relevant precedents and guidance for your review.
    
    Args:
        query: The search query describing what architectural knowledge you need.
               Examples: "microservices patterns", "scaling database performance",
                        "security best practices"
        search_type: Type of search - 'general', 'patterns', 'practices', or 'reviews'
                    (default: 'general' searches all types)
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        Relevant architectural knowledge, patterns, and best practices matching the query.
        Results include similarity scores (0-1) and metadata.
    """
    if not RETRIEVAL_AVAILABLE:
        return "Semantic search not available - retrieval service not configured."
    
    try:
        # Initialize retrieval service
        vector_store = get_vector_store()
        neo4j_client = get_neo4j_client()
        retrieval = RetrievalService(vector_store=vector_store, neo4j_client=neo4j_client)
        
        if not vector_store or vector_store.collection is None:
            return "Vector store not available - no indexed documents found."
        
        # Perform semantic search
        results = retrieval.semantic_search(query, k=limit)
        
        if not results:
            return f"No relevant knowledge found for query: '{query}'"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            similarity = result.get('similarity', 0)
            doc = result['document']
            metadata = result.get('metadata', {})
            
            # Format based on metadata type
            if metadata.get('type') == 'architecture':
                formatted_results.append(
                    f"[{i}] ARCHITECTURE: {metadata.get('title', 'Unknown')}\n"
                    f"    Similarity: {similarity:.2%}\n"
                    f"    Type: {metadata.get('architecture_type', 'N/A')}\n"
                    f"    Score: {metadata.get('score', 'N/A')}\n"
                    f"    Description: {doc[:150]}..."
                )
            elif metadata.get('type') == 'pattern':
                formatted_results.append(
                    f"[{i}] PATTERN: {metadata.get('name', 'Unknown')}\n"
                    f"    Similarity: {similarity:.2%}\n"
                    f"    Domain: {metadata.get('domain', 'N/A')}\n"
                    f"    Description: {doc[:150]}..."
                )
            elif metadata.get('type') == 'practice':
                formatted_results.append(
                    f"[{i}] BEST PRACTICE: {metadata.get('name', 'Unknown')}\n"
                    f"    Similarity: {similarity:.2%}\n"
                    f"    Domain: {metadata.get('domain', 'N/A')}\n"
                    f"    Description: {doc[:150]}..."
                )
            else:
                formatted_results.append(
                    f"[{i}] Result (Similarity: {similarity:.2%})\n"
                    f"    {doc[:200]}..."
                )
        
        return "\n\n".join(formatted_results) if formatted_results else "No results found."
        
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"
