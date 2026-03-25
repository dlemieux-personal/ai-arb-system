#!/usr/bin/env python3
"""
Neo4j Graph Demo
Demonstrates creating nodes and relationships in the Neo4j knowledge graph.
"""

import os
from dotenv import load_dotenv

from src.knowledge_graph.neo4j_client import Neo4jClient
from src.knowledge_graph.graph_client_factory import create_neo4j_client


def demo():
    """Run interactive demo of Neo4j operations."""
    
    print("=" * 60)
    print("Neo4j Knowledge Graph Demo")
    print("=" * 60)
    
    # Try to create a client from environment
    client = create_neo4j_client()
    
    if client is None:
        print("\n⚠ Neo4j connection not configured.")
        print("Make sure to set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD")
        print("\nExample from .env.example:")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=your_password")
        return
    
    print("\n✓ Connected to Neo4j database")
    
    try:
        # Create some nodes
        print("\n--- Creating Nodes ---")
        
        print("\nCreating architecture node...")
        arch = client.create_architecture(
            "Microservices E-Commerce Platform",
            "A distributed system for online retail with multiple services"
        )
        print(f"  ✓ Created: {arch.get('id')}")
        
        print("Creating pattern nodes...")
        pattern1 = client.create_pattern(
            "Microservices",
            "Decompose monolithic application into loosely coupled services",
            "Architectural"
        )
        print(f"  ✓ Pattern 1: {pattern1.get('id')}")
        
        pattern2 = client.create_pattern(
            "API Gateway",
            "Single entry point for client requests to microservices",
            "Architectural"
        )
        print(f"  ✓ Pattern 2: {pattern2.get('id')}")
        
        print("Creating best practice nodes...")
        bp1 = client.create_best_practice(
            "Service Independence",
            "Each service should be independently deployable and scalable",
            "scalability"
        )
        print(f"  ✓ BestPractice 1: {bp1.get('id')}")
        
        bp2 = client.create_best_practice(
            "API Security",
            "Implement OAuth 2.0 or similar for API authentication",
            "security"
        )
        print(f"  ✓ BestPractice 2: {bp2.get('id')}")
        
        # Create relationships
        print("\n--- Creating Relationships ---")
        
        if arch.get('id') and pattern1.get('id'):
            success = client.create_relationship(
                "Architecture", arch['id'],
                "IMPLEMENTS",
                "Pattern", pattern1['id']
            )
            print(f"  ✓ Architecture IMPLEMENTS Microservices: {success}")
        
        if arch.get('id') and pattern2.get('id'):
            success = client.create_relationship(
                "Architecture", arch['id'],
                "USES",
                "Pattern", pattern2['id']
            )
            print(f"  ✓ Architecture USES API Gateway: {success}")
        
        if pattern1.get('id') and bp1.get('id'):
            success = client.create_relationship(
                "Pattern", pattern1['id'],
                "REFERENCES",
                "BestPractice", bp1['id']
            )
            print(f"  ✓ Microservices REFERENCES Service Independence: {success}")
        
        # Query nodes
        print("\n--- Querying Nodes ---")
        
        print("\nAll Architectures:")
        archs = client.find_nodes("Architecture")
        for a in archs:
            print(f"  - {a.get('name')} (id: {a.get('id')})")
        
        print("\nAll Patterns:")
        patterns = client.find_nodes("Pattern")
        for p in patterns:
            print(f"  - {p.get('name')} (category: {p.get('category')})")
        
        print("\nBest Practices for 'security':")
        security_bps = client.find_nodes("BestPractice", {'domain': 'security'})
        for bp in security_bps:
            print(f"  - {bp.get('title')}")
        
        # Retrieve single node
        if arch.get('id'):
            print(f"\nRetrieve Architecture by ID:")
            retrieved = client.get_node("Architecture", arch['id'])
            if retrieved:
                print(f"  ✓ Found: {retrieved.get('name')}")
            else:
                print(f"  ✗ Not found")
        
        # Update a node
        if arch.get('id'):
            print(f"\nUpdating Architecture...")
            updated = client.update_node(
                "Architecture",
                arch['id'],
                {'description': "Updated: A distributed system optimized for high scalability"}
            )
            print(f"  ✓ Updated: {updated.get('description')}")
        
        print("\n" + "=" * 60)
        print("✓ Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if client:
            client.close()
            print("\n✓ Connection closed")


if __name__ == "__main__":
    load_dotenv()
    demo()
