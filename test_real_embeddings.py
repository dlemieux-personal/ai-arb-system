#!/usr/bin/env python3
"""
Real OpenAI Embeddings Test
Tests embedding generation with actual OpenAI API key.
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.vector_memory.embedding_service import EmbeddingService


def test_real_embeddings():
    """Test real embedding generation with OpenAI API"""
    print("\n" + "="*60)
    print("REAL OPENAI EMBEDDINGS TEST")
    print("="*60)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n✗ OPENAI_API_KEY not found in environment")
        print("  Please add OPENAI_API_KEY to .env file")
        return False
    
    print(f"\n✓ OPENAI_API_KEY found: {api_key[:20]}...{api_key[-10:]}")
    
    # Initialize service
    service = EmbeddingService()
    print(f"✓ EmbeddingService initialized WITH OpenAI client")
    print(f"  Model: {service.model}")
    print(f"  Client available: {service.client is not None}")
    
    if service.client is None:
        print("\n✗ OpenAI client not initialized")
        return False
    
    # Test single embedding
    print("\n--- Testing Single Text Embedding ---")
    test_text = "Microservices architecture with Kubernetes orchestration"
    print(f"Text: '{test_text}'")
    
    embedding = service.embed_text(test_text)
    
    if embedding is None:
        print("✗ Failed to generate embedding")
        return False
    
    print(f"✓ Successfully generated embedding!")
    print(f"  Dimension: {len(embedding)}")
    print(f"  First 5 values: {[f'{v:.6f}' for v in embedding[:5]]}")
    print(f"  Magnitude: {sum(v**2 for v in embedding)**0.5:.4f}")
    
    # Test batch embeddings
    print("\n--- Testing Batch Embeddings ---")
    documents = [
        "Event-driven architecture using Apache Kafka",
        "Serverless computing with AWS Lambda functions",
        "Monolithic architecture with Spring Boot framework",
        "GraphQL API design patterns and best practices",
        "Circuit breaker pattern for fault tolerance"
    ]
    
    print(f"Embedding {len(documents)} documents...")
    embeddings = service.embed_documents(documents)
    
    successful = sum(1 for e in embeddings if e is not None)
    failed = len(embeddings) - successful
    
    print(f"✓ Generated {successful}/{len(documents)} embeddings successfully")
    
    if failed > 0:
        print(f"⚠ {failed} documents failed to embed")
    
    for i, (doc, emb) in enumerate(zip(documents, embeddings), 1):
        if emb:
            magnitude = sum(v**2 for v in emb)**0.5
            print(f"  [{i}] Dim={len(emb)}, Mag={magnitude:.4f} - '{doc[:50]}...'")
        else:
            print(f"  [{i}] FAILED - '{doc[:50]}...'")
    
    # Test similarity between embeddings
    print("\n--- Testing Embedding Similarity ---")
    
    if embeddings[0] and embeddings[1]:
        # Compute cosine similarity
        import math
        
        def cosine_similarity(a, b):
            """Compute cosine similarity between two vectors"""
            dot_product = sum(x * y for x, y in zip(a, b))
            mag_a = math.sqrt(sum(x**2 for x in a))
            mag_b = math.sqrt(sum(y**2 for y in b))
            if mag_a == 0 or mag_b == 0:
                return 0
            return dot_product / (mag_a * mag_b)
        
        # Compare different pairs
        pairs = [
            (0, 1, "Event-driven vs Serverless"),
            (0, 2, "Event-driven vs Monolithic"),
            (2, 4, "Monolithic vs Circuit Breaker"),
            (3, 4, "GraphQL vs Circuit Breaker")
        ]
        
        for idx1, idx2, label in pairs:
            similarity = cosine_similarity(embeddings[idx1], embeddings[idx2])
            print(f"  {label:40} Similarity: {similarity:.4f}")
    
    print("\n" + "="*60)
    print("✓ REAL EMBEDDINGS TEST COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_real_embeddings()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
