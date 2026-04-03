"""
Retrieval Service Module
Retrieves relevant architecture patterns and past reviews using hybrid search.
"""

from typing import List, Dict, Any, Optional, cast
import json

from src.knowledge_graph.graph_schema import GraphSchema


class RetrievalService:
    """Service for retrieving relevant knowledge and past reviews using hybrid search"""
    
    def __init__(self, vector_store=None, neo4j_client=None):
        """
        Initialize retrieval service
        
        Args:
            vector_store: Optional vector store for similarity search
            neo4j_client: Optional Neo4j client for graph queries
        """
        self.vector_store = vector_store
        self.neo4j_client = neo4j_client
        self.schema = GraphSchema()
    
    def retrieve_similar_reviews(self, submission: str, k: int = 5) -> List[Dict[Any, Any]]:
        """
        Retrieve similar past reviews using vector similarity and graph context
        
        Args:
            submission: Architecture submission
            k: Number of results to return
            
        Returns:
            List of similar reviews with similarity scores
        """
        if not self.neo4j_client:
            return []
        
        # First, get all reviews from the graph
        all_reviews = cast(List[Dict[Any, Any]], self.neo4j_client.find_nodes(GraphSchema.REVIEW))
        
        if not all_reviews:
            return []
        
        # If we have a vector store, use it to score by similarity
        if self.vector_store:
            # Format reviews as documents for vector search
            review_docs = [
                json.dumps({
                    'id': r.get('id'),
                    'submission': r.get('submission_text', ''),
                    'overall_score': r.get('overall_score'),
                    'status': r.get('approval_status')
                })
                for r in all_reviews
            ]
            
            # Search for similar reviews
            similar = cast(List[Dict[Any, Any]], self.vector_store.search(submission, k=k))
            
            # Enrich with graph data
            results: List[Dict[Any, Any]] = []
            for item in similar:
                # Try to find matching review
                review_id = item.get('metadata', {}).get('review_id')
                if review_id:
                    review = next((r for r in all_reviews if r.get('id') == review_id), None)
                    if review:
                        review['similarity'] = item['similarity']
                        results.append(review)
            
            return results[:k]
        
        # Fallback: return all reviews if no vector store
        return all_reviews[:k]
    
    def retrieve_relevant_patterns(self, keywords: List[str], k: int = 10) -> List[Dict]:
        """
        Retrieve relevant architecture patterns by keyword
        
        Args:
            keywords: Keywords to search for
            k: Number of results to return
            
        Returns:
            List of relevant patterns
        """
        if not self.neo4j_client:
            return []
        
        # Get all patterns from graph
        all_patterns = self.neo4j_client.find_nodes(GraphSchema.PATTERN)
        
        if not all_patterns or not keywords:
            return all_patterns[:k]
        
        # If we have a vector store, use it for semantic search
        if self.vector_store:
            # Create search documents from patterns
            pattern_docs = [
                json.dumps({
                    'id': p.get('id'),
                    'name': p.get('name', ''),
                    'description': p.get('description', ''),
                    'benefits': p.get('benefits', '')
                })
                for p in all_patterns
            ]
            
            results = []
            for keyword in keywords:
                similar = self.vector_store.search(keyword, k=k)
                results.extend(similar)
            
            # Deduplicate and map back to pattern objects
            seen = set()
            unique_results = []
            for item in results:
                pattern_id = item.get('metadata', {}).get('pattern_id')
                if pattern_id and pattern_id not in seen:
                    seen.add(pattern_id)
                    pattern = next((p for p in all_patterns if p.get('id') == pattern_id), None)
                    if pattern:
                        pattern['relevance_score'] = item.get('similarity', 0)
                        unique_results.append(pattern)
            
            return unique_results[:k]
        
        # Fallback: keyword matching in pattern objects
        matching = []
        for pattern in all_patterns:
            name = (pattern.get('name') or '').lower()
            description = (pattern.get('description') or '').lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in name or keyword_lower in description:
                    matching.append(pattern)
                    break
        
        return matching[:k]
    
    def retrieve_best_practices(self, domain: str, k: int = 10) -> List[Dict]:
        """
        Retrieve best practices for a domain using graph queries and semantic search
        
        Args:
            domain: Domain to search for
            k: Number of results to return
            
        Returns:
            List of best practices
        """
        if not self.neo4j_client:
            return []
        
        # Find best practices matching the domain
        practices = self.neo4j_client.find_nodes(
            GraphSchema.BEST_PRACTICE,
            criteria={'domain': domain}
        )
        
        if not practices and self.vector_store:
            # Fallback to semantic search if graph search returns nothing
            similar = self.vector_store.search(f"best practices for {domain}", k=k)
            results = []
            for item in similar:
                practice_id = item.get('metadata', {}).get('practice_id')
                all_practices = self.neo4j_client.find_nodes(GraphSchema.BEST_PRACTICE)
                practice = next((p for p in all_practices if p.get('id') == practice_id), None)
                if practice:
                    practice['relevance_score'] = item.get('similarity', 0)
                    results.append(practice)
            return results[:k]
        
        return practices[:k]
    
    def retrieve_related_architectures(self, architecture_id: str, k: int = 5) -> List[Dict]:
        """
        Retrieve architectures related to a given architecture using graph relationships
        and semantic similarity
        
        Args:
            architecture_id: Architecture id
            k: Number of results to return
            
        Returns:
            List of related architectures
        """
        if not self.neo4j_client:
            return []
        
        # Query for architectures related via SIMILAR_TO relationships
        query = f"""
            MATCH (a:{GraphSchema.ARCHITECTURE} {{id: $id}})
            MATCH (a)-[:{GraphSchema.SIMILAR_TO}]-(similar:{GraphSchema.ARCHITECTURE})
            RETURN similar
            LIMIT $limit
        """
        try:
            results = self.neo4j_client.execute_query(query, {'id': architecture_id, 'limit': k})
            return [dict(r.get('similar', {})) for r in results]
        except Exception:
            return []
    
    def retrieve_architecture_risks(self, architecture_id: str, k: int = 10) -> List[Dict]:
        """
        Retrieve risks associated with an architecture
        
        Args:
            architecture_id: Architecture id
            k: Number of results to return
            
        Returns:
            List of risks with associated findings
        """
        if not self.neo4j_client:
            return []
        
        # Query for risks related to architecture
        query = f"""
            MATCH (a:{GraphSchema.ARCHITECTURE} {{id: $id}})
            MATCH (a)-[:IDENTIFIED_IN|:CONTAINS]->(f:{GraphSchema.FINDING})
            MATCH (f)-[:INDICATES]->(r:{GraphSchema.RISK})
            RETURN r, f
            LIMIT $limit
        """
        try:
            results = self.neo4j_client.execute_query(query, {'id': architecture_id, 'limit': k})
            return [dict(r.get('r', {})) for r in results]
        except Exception:
            return []
    
    def semantic_search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Generic semantic search across all indexed documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with similarity scores
        """
        if not self.vector_store:
            return []
        
        results = self.vector_store.search(query, k=k)
        return results
