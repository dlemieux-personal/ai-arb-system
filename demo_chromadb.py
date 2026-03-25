#!/usr/bin/env python3
"""
ChromaDB Integration Demo
Demonstrates embedding generation and vector storage with retrieval.
"""

import os
import sys
import json
from pathlib import Path
# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_memory.embedding_service import EmbeddingService
from src.vector_memory.vector_store import VectorStore
from src.vector_memory.vector_store_factory import get_vector_store
from src.vector_memory.retrieval_service import RetrievalService
from src.knowledge_graph.graph_client_factory import get_neo4j_client


def demo_embedding_service():
    """Demonstrate embedding service"""
    print("\n" + "="*60)
    print("EMBEDDING SERVICE DEMO")
    print("="*60)
    
    service = EmbeddingService()
    
    if service.client is None:
        print("⚠ OpenAI API key not configured, using stubs for demonstration")
        print("Set OPENAI_API_KEY environment variable to enable real embeddings")
        return
    
    # Test single text embedding
    text = "Microservices architecture with Kubernetes orchestration"
    embedding = service.embed_text(text)
    
    if embedding:
        print(f"\n✓ Successfully embedded text: '{text}'")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print(f"\n✗ Failed to embed text")
    
    # Test batch embedding
    documents = [
        "Event-driven architecture using Kafka",
        "Serverless computing with AWS Lambda",
        "Monolithic architecture with Spring Boot",
        "GraphQL API design patterns"
    ]
    
    embeddings = service.embed_documents(documents)
    successful = sum(1 for e in embeddings if e is not None)
    
    print(f"\n✓ Batch embedded {successful}/{len(documents)} documents")
    for i, (doc, emb) in enumerate(zip(documents, embeddings)):
        if emb:
            print(f"  [{i+1}] '{doc}' - dim {len(emb)}")


def demo_vector_store():
    """Demonstrate vector store operations"""
    print("\n" + "="*60)
    print("VECTOR STORE DEMO")
    print("="*60)
    
    # Create vector store
    store = VectorStore(
        collection_name="architecture_reviews_demo",
        persist_dir="./memory/embeddings_demo"
    )
    
    print(f"\n✓ Vector store initialized")
    print(f"  Collection: {store.collection_name}")
    print(f"  Persist dir: {store.persist_dir}")
    print(f"  Client available: {store.client is not None}")
    
    if store.collection is None:
        print("\n⚠ ChromaDB not available - skipping operations")
        return
    
    # Sample architectural patterns for storage
    patterns = [
        {
            "text": "Microservices architecture decouples services for independent scaling",
            "metadata": {"type": "pattern", "name": "Microservices", "domain": "architecture"}
        },
        {
            "text": "Event-driven architecture enables asynchronous communication between services",
            "metadata": {"type": "pattern", "name": "Event-Driven", "domain": "architecture"}
        },
        {
            "text": "Event sourcing maintains complete audit trail of all state changes",
            "metadata": {"type": "pattern", "name": "Event Sourcing", "domain": "data"}
        },
        {
            "text": "CQRS separates read and write models for better scalability",
            "metadata": {"type": "pattern", "name": "CQRS", "domain": "architecture"}
        },
        {
            "text": "Circuit breaker pattern prevents cascading failures in distributed systems",
            "metadata": {"type": "pattern", "name": "Circuit Breaker", "domain": "reliability"}
        }
    ]
    
    # Add documents
    print(f"\nAdding {len(patterns)} documents to vector store...")
    docs = [p["text"] for p in patterns]
    metas = [p["metadata"] for p in patterns]
    store.add_documents(docs, metadatas=metas)
    print(f"✓ Added {len(patterns)} documents")
    
    # Search operations
    search_queries = [
        "How should I design a scalable system?",
        "Tell me about fault tolerance",
        "Event-based systems"
    ]
    
    print(f"\nPerforming {len(search_queries)} semantic searches...")
    for query in search_queries:
        results = store.search(query, k=3)
        print(f"\n  Query: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                similarity = result.get('similarity', 0)
                doc_text = result['document'][:60] + "..." if len(result['document']) > 60 else result['document']
                print(f"    [{i}] Similarity: {similarity:.2f} - {doc_text}")
        else:
            print(f"    No results found")


def demo_retrieval_service():
    """Demonstrate retrieval service with Neo4j and vector integration"""
    print("\n" + "="*60)
    print("RETRIEVAL SERVICE DEMO")
    print("="*60)
    
    # Initialize components
    neo4j_client = get_neo4j_client()
    vector_store = get_vector_store()
    
    print(f"\n✓ Retrieval service initialized")
    print(f"  Neo4j client: {neo4j_client is not None}")
    print(f"  Vector store: {vector_store is not None}")
    
    if neo4j_client is None:
        print("\n⚠ Neo4j not available - skipping Neo4j operations")
        return
    
    service = RetrievalService(
        vector_store=vector_store,
        neo4j_client=neo4j_client
    )
    
    # Demonstrate semantic search
    if vector_store and vector_store.collection:
        query = "scalability and performance architecture"
        print(f"\nSemantic search for: '{query}'")
        
        results = service.semantic_search(query, k=3)
        if results:
            print(f"✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  [{i}] Similarity: {result.get('similarity', 0):.2f}")
                print(f"      {result['document'][:70]}...")
        else:
            print("No results found")
    
    # Demonstrate graph-based retrieval
    print(f"\nGraph-based retrieval:")
    
    # Try to retrieve patterns from graph
    from src.knowledge_graph.graph_schema import GraphSchema
    patterns = neo4j_client.find_nodes(GraphSchema.PATTERN)
    
    if patterns:
        print(f"✓ Found {len(patterns)} patterns in knowledge graph:")
        for p in patterns[:3]:
            print(f"  - {p.get('name', 'Unknown')} ({p.get('domain', 'N/A')})")
    else:
        print("No patterns found in knowledge graph")
    
    # Demonstrate architecture retrieval
    architectures = neo4j_client.find_nodes(GraphSchema.ARCHITECTURE)
    if architectures:
        print(f"✓ Found {len(architectures)} architectures in knowledge graph:")
        for arch in architectures[:3]:
            score = arch.get('overall_score', 'N/A')
            print(f"  - {arch.get('name', 'Unknown')} (Score: {score})")
    else:
        print("No architectures found in knowledge graph")


def demo_end_to_end():
    """Demonstrate end-to-end workflow"""
    print("\n" + "="*60)
    print("END-TO-END WORKFLOW DEMO")
    print("="*60)
    
    # Create embedding service
    embedding_service = EmbeddingService()
    
    # Create vector store
    vector_store = VectorStore(
        collection_name="architecture_reviews_e2e",
        persist_dir="./memory/embeddings_e2e",
        embedding_service=embedding_service
    )
    
    # Initialize Neo4j client
    neo4j_client = get_neo4j_client()
    
    # Create retrieval service
    retrieval_service = RetrievalService(
        vector_store=vector_store,
        neo4j_client=neo4j_client
    )
    
    print("\n✓ Full pipeline initialized")
    print(f"  Embedding model: {embedding_service.model}")
    print(f"  Vector collection: {vector_store.collection_name}")
    print(f"  Neo4j available: {neo4j_client is not None}")
    
    # Test workflow
    submission = """
    Our team is designing a microservices architecture for a financial platform.
    We need high availability, fault tolerance, and the ability to scale services independently.
    We're considering event-driven patterns for communication between services.
    """
    
    print(f"\nProcessing submission:")
    print(f"  '{submission[:100]}...'")
    
    # Retrieve similar reviews
    similar_reviews = retrieval_service.retrieve_similar_reviews(submission, k=3)
    print(f"\n✓ Retrieved similar reviews: {len(similar_reviews)}")
    
    # Retrieve relevant patterns
    keywords = ["microservices", "scalability", "fault tolerance"]
    patterns = retrieval_service.retrieve_relevant_patterns(keywords, k=3)
    print(f"✓ Retrieved relevant patterns: {len(patterns)}")
    
    if patterns:
        for p in patterns[:2]:
            print(f"  - {p.get('name', 'Unknown')}")
    
    # Retrieve best practices
    best_practices = retrieval_service.retrieve_best_practices("architecture", k=3)
    print(f"✓ Retrieved best practices: {len(best_practices)}")


def main():
    """Run all demos"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║      CHROMADB & EMBEDDING INTEGRATION DEMONSTRATION      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        # Check environment
        print("\nEnvironment Check:")
        openai_key = bool(os.getenv('OPENAI_API_KEY'))
        chroma_dir = os.getenv('CHROMADB_PERSIST_DIR', './memory/embeddings_cache')
        
        print(f"  OPENAI_API_KEY: {'✓' if openai_key else '✗'}")
        print(f"  CHROMADB_PERSIST_DIR: {chroma_dir}")
        
        # Run demos
        demo_embedding_service()
        demo_vector_store()
        demo_retrieval_service()
        demo_end_to_end()
        
        print("\n" + "="*60)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
