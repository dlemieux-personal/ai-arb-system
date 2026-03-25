#!/usr/bin/env python3
"""
AcmeTech Retrieval Demo
Demonstrates retrieval of AcmeTech's architectural data using hybrid search.
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.vector_memory.retrieval_service import RetrievalService
from src.vector_memory.vector_store_factory import get_vector_store
from src.knowledge_graph.graph_client_factory import get_neo4j_client


def demo_acmetech_retrieval():
    """Demonstrate retrieval of AcmeTech architectural data"""

    print("\n" + "="*70)
    print("ACMETECH ARCHITECTURAL RETRIEVAL DEMO")
    print("="*70)

    # Initialize components
    neo4j_client = get_neo4j_client()
    vector_store = get_vector_store()

    print(f"\n✓ Components initialized:")
    print(f"  Neo4j client: {neo4j_client is not None}")
    print(f"  Vector store: {vector_store is not None}")

    if not neo4j_client or not vector_store:
        print("\n✗ Components not available")
        return

    retrieval_service = RetrievalService(
        vector_store=vector_store,
        neo4j_client=neo4j_client
    )

    # Test queries relevant to AcmeTech's e-commerce architecture
    test_queries = [
        {
            "query": "How should we design a scalable e-commerce platform?",
            "description": "General scalability question"
        },
        {
            "query": "What are the benefits of microservices for order processing?",
            "description": "Microservices-specific question"
        },
        {
            "query": "How to handle inventory consistency in distributed systems?",
            "description": "Best practice question"
        },
        {
            "query": "Event-driven architecture patterns for high-throughput systems",
            "description": "Event-driven patterns"
        },
        {
            "query": "Serverless computing for cost optimization in cloud",
            "description": "Serverless and cost optimization"
        },
        {
            "query": "API Gateway pattern for microservices",
            "description": "API Gateway pattern"
        }
    ]

    print(f"\n--- Testing Semantic Search ---")

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Query: '{test_case['query']}'")

        results = retrieval_service.semantic_search(test_case['query'], k=3)

        if results:
            print(f"   ✓ Found {len(results)} relevant documents:")
            for j, result in enumerate(results, 1):
                similarity = result.get('similarity', 0)
                metadata = result.get('metadata', {})
                doc_type = metadata.get('type', 'unknown')
                title = metadata.get('title', metadata.get('name', 'Unknown'))

                print(f"     [{j}] {doc_type.upper()}: {title}")
                print(f"         Similarity: {similarity:.3f}")
                print(f"         Preview: {result['document'][:80]}...")
        else:
            print("   ✗ No results found")

    # Test graph-based retrieval
    print(f"\n--- Testing Graph-Based Retrieval ---")

    # Retrieve patterns
    print(f"\nRetrieving architectural patterns from knowledge graph...")
    patterns = neo4j_client.find_nodes("Pattern")
    if patterns:
        print(f"✓ Found {len(patterns)} patterns in knowledge graph:")
        for pattern in patterns[:3]:
            print(f"  - {pattern.get('name', 'Unknown')}: {pattern.get('description', '')[:60]}...")
    else:
        print("✗ No patterns found in knowledge graph")

    # Retrieve architectures
    print(f"\nRetrieving architectures from knowledge graph...")
    architectures = neo4j_client.find_nodes("Architecture")
    if architectures:
        print(f"✓ Found {len(architectures)} architectures in knowledge graph:")
        for arch in architectures[:3]:
            print(f"  - {arch.get('name', 'Unknown')}: {arch.get('description', '')[:60]}...")
    else:
        print("✗ No architectures found in knowledge graph")

    # Test hybrid retrieval methods
    print(f"\n--- Testing Hybrid Retrieval Methods ---")

    # Retrieve similar reviews (should find AcmeTech architectures)
    sample_submission = """
    We are designing a modern e-commerce platform using microservices architecture.
    Our system needs to handle high-volume order processing, inventory management,
    and shipping logistics. We're considering event-driven patterns and cloud-native
    technologies for scalability.
    """

    print(f"\nRetrieving similar reviews for sample submission...")
    similar_reviews = retrieval_service.retrieve_similar_reviews(sample_submission, k=3)
    if similar_reviews:
        print(f"✓ Found {len(similar_reviews)} similar reviews:")
        for review in similar_reviews:
            print(f"  - {review.get('name', 'Unknown')}")
    else:
        print("✗ No similar reviews found")

    # Retrieve relevant patterns
    keywords = ["microservices", "scalability", "event-driven"]
    print(f"\nRetrieving patterns for keywords: {keywords}")
    patterns = retrieval_service.retrieve_relevant_patterns(keywords, k=3)
    if patterns:
        print(f"✓ Found {len(patterns)} relevant patterns:")
        for pattern in patterns:
            print(f"  - {pattern.get('name', 'Unknown')}")
    else:
        print("✗ No relevant patterns found")

    # Retrieve best practices
    print(f"\nRetrieving best practices for 'scalability' domain...")
    practices = retrieval_service.retrieve_best_practices("scalability", k=3)
    if practices:
        print(f"✓ Found {len(practices)} best practices:")
        for practice in practices:
            print(f"  - {practice.get('title', 'Unknown')}")
    else:
        print("✗ No best practices found")

    # Test ARB pipeline with AcmeTech data
    print(f"\n--- Testing ARB Pipeline with AcmeTech Data ---")

    try:
        from src.orchestration.arb_pipeline import ARBPipeline

        # Load one of the AcmeTech submissions
        submission_file = Path("./submissions/acmetech/acmetech-arch-005.json")
        if submission_file.exists():
            pipeline = ARBPipeline()

            print(f"Processing AcmeTech AI-Powered Supply Chain submission...")
            result = pipeline.process_submission(str(submission_file))

            print(f"✓ Pipeline result:")
            print(f"  Status: {result.status}")
            print(f"  Overall Score: {result.overall_score}")
            print(f"  Approval Decision: {result.approval_decision}")
            print(f"  Review Dimensions: {len(result.review_dimensions) if result.review_dimensions else 0}")
        else:
            print("✗ AcmeTech submission file not found")

    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")

    print(f"\n" + "="*70)
    print("✓ ACMETECH RETRIEVAL DEMO COMPLETED")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_acmetech_retrieval()
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
