"""
Retrieval Context Tool
Provides agent context from retrieved knowledge before task execution.
"""

from crewai.tools import tool
from typing import Optional, List, Dict, Any, cast
import json

try:
    from src.vector_memory.vector_store_factory import get_vector_store
    from src.knowledge_graph.graph_client_factory import get_neo4j_client
    from src.vector_memory.retrieval_service import RetrievalService
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False


class RetrievalContextManager:
    """Manages retrieval context for agent tasks"""
    
    def __init__(self, submission_text: str = ""):
        """
        Initialize context manager with submission text
        
        Args:
            submission_text: The architecture submission being reviewed
        """
        self.submission_text = submission_text
        self.retrieval_service = None
        self.cached_context: Dict[str, Any] = {}
        
        if CONTEXT_AVAILABLE:
            try:
                vector_store = get_vector_store()
                neo4j_client = get_neo4j_client()
                self.retrieval_service = RetrievalService(
                    vector_store=vector_store,
                    neo4j_client=neo4j_client
                )
                self.neo4j_client = neo4j_client  # Store for availability checking
            except Exception as e:
                print(f"Warning: Could not initialize retrieval service: {e}")
                self.neo4j_client = None
    
    def get_context_for_domain(self, domain: str, context_type: str = "mixed") -> str:
        """
        Get relevant context for a specific review domain
        
        Args:
            domain: The review domain (security, scalability, reliability, data, cost, compliance)
            context_type: Type of context to retrieve (mixed, patterns, practices, examples)
            
        Returns:
            Formatted context string with relevant knowledge
        """
        if not self.retrieval_service:
            return ""
        
        cache_key = f"{domain}_{context_type}"
        if cache_key in self.cached_context:
            return cast(str, self.cached_context[cache_key])
        
        context_parts: List[str] = []
        
        # Get best practices for the domain (fallback to semantic search if Neo4j unavailable)
        try:
            if self.neo4j_client:
                practices = self.retrieval_service.retrieve_best_practices(domain, k=3)
                if practices:
                    context_parts.append("## Best Practices for This Domain\n")
                    for i, practice in enumerate(practices, 1):
                        context_parts.append(
                            f"{i}. {practice.get('title', 'Unknown')}\\n"
                            f"   {practice.get('description', 'N/A')}\n"
                        )
            else:
                # Fallback: Use semantic search for domain-related content
                search_query = f"{domain} best practices architecture patterns"
                results = self.retrieval_service.semantic_search(search_query, k=3)
                if results:
                    context_parts.append("## Relevant Knowledge for This Domain\n")
                    for i, result in enumerate(results, 1):
                        metadata = result.get('metadata', {})
                        title = metadata.get('title', 'Unknown')
                        doc_type = metadata.get('type', 'document')
                        context_parts.append(
                            f"{i}. [{doc_type.title()}] {title}\\n"
                            f"   {result.get('document', '')[:150]}...\n"
                        )
        except Exception as e:
            pass  # Silently fail if service unavailable
        
        # Get relevant patterns (fallback to semantic search if Neo4j unavailable)
        try:
            if self.neo4j_client:
                keywords = domain.split() + ['architecture', 'pattern', 'best practice']
                patterns = self.retrieval_service.retrieve_relevant_patterns(keywords, k=3)
                if patterns:
                    context_parts.append("\\n## Relevant Patterns\n")
                    for i, pattern in enumerate(patterns, 1):
                        context_parts.append(
                            f"{i}. {pattern.get('name', 'Unknown')}\\n"
                            f"   {pattern.get('description', 'N/A')}\n"
                        )
            else:
                # Fallback: Use semantic search for patterns
                search_query = f"{domain} patterns architecture"
                results = self.retrieval_service.semantic_search(search_query, k=2)
                if results:
                    context_parts.append("\\n## Relevant Patterns and Examples\n")
                    for i, result in enumerate(results, 1):
                        metadata = result.get('metadata', {})
                        title = metadata.get('title', 'Unknown')
                        context_parts.append(
                            f"{i}. {title}\\n"
                            f"   {result.get('document', '')[:150]}...\n"
                        )
        except Exception as e:
            pass
        
        # Get similar past reviews for reference (only if Neo4j available)
        try:
            if self.submission_text and self.neo4j_client:
                similar = self.retrieval_service.retrieve_similar_reviews(
                    self.submission_text,
                    k=2
                )
                if similar:
                    context_parts.append("\\n## Similar Past Reviews\n")
                    for i, review in enumerate(similar, 1):
                        score = review.get('overall_score', 'N/A')
                        status = review.get('approval_status', 'N/A')
                        context_parts.append(
                            f"{i}. Previous Review Score: {score}, Status: {status}\n"
                        )
        except Exception as e:
            pass
        
        context = "\\n".join(context_parts) if context_parts else ""
        self.cached_context[cache_key] = context
        return context
    
    def get_all_context(self) -> Dict[str, str]:
        """
        Get context for all review domains
        
        Returns:
            Dictionary mapping domains to their context
        """
        domains = ['security', 'scalability', 'reliability', 'data', 'cost_optimization', 'compliance']
        context_map = {}
        
        for domain in domains:
            context_map[domain] = self.get_context_for_domain(domain)
        
        return context_map


@tool("Get Review Context")
def retrieval_context_tool(domain: str = "general") -> str:
    """
    Retrieve contextual knowledge for a specific review domain.
    
    Use this tool at the BEGINNING of your review to understand relevant patterns,
    best practices, and precedents for your evaluation domain.
    
    Args:
        domain: The review domain - one of: security, scalability, reliability, 
               data, cost, compliance, or 'general' for all
               
    Returns:
        Curated knowledge about patterns, practices, and precedents for the domain
    """
    # This is a factory tool - actual context should be retrieved through
    # RetrievalContextManager initialized with submission text
    return (
        "Context retrieval tool is available. Use get_retrieval_context() "
        "to initialize context with submission text, or use vector_search_tool "
        "and graph_query_tool for specific queries."
    )


def get_retrieval_context(submission_text: str = "") -> RetrievalContextManager:
    """
    Factory function to create a retrieval context manager
    
    Args:
        submission_text: The architecture submission being reviewed
        
    Returns:
        Initialized RetrievalContextManager for retrieving domain-specific context
    """
    return RetrievalContextManager(submission_text)
