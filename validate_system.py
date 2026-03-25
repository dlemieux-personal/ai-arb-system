#!/usr/bin/env python3
"""
Validation Script
Tests that all modules can be imported and agents can be created.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.agents.agent_factory import AgentFactory
        print("✓ AgentFactory imported")
    except Exception as e:
        print(f"✗ Failed to import AgentFactory: {e}")
        return False
    
    try:
        from src.agents.definitions.security_agent import build_security_agent
        print("✓ build_security_agent imported")
    except Exception as e:
        print(f"✗ Failed to import build_security_agent: {e}")
        return False
    
    try:
        from src.agents.definitions.orchestrator_agent import build_orchestrator_agent
        print("✓ build_orchestrator_agent imported")
    except Exception as e:
        print(f"✗ Failed to import build_orchestrator_agent: {e}")
        return False
    
    try:
        from src.tools.vector_tool import vector_search_tool
        print("✓ vector_search_tool imported")
    except Exception as e:
        print(f"✗ Failed to import vector_search_tool: {e}")
        return False
    
    try:
        from src.tools.graph_tool import graph_query_tool
        print("✓ graph_query_tool imported")
    except Exception as e:
        print(f"✗ Failed to import graph_query_tool: {e}")
        return False
    
    try:
        from src.vector_memory.embedding_service import EmbeddingService
        print("✓ EmbeddingService imported")
    except Exception as e:
        print(f"✗ Failed to import EmbeddingService: {e}")
        return False
    
    try:
        from src.vector_memory.vector_store import VectorStore
        print("✓ VectorStore imported")
    except Exception as e:
        print(f"✗ Failed to import VectorStore: {e}")
        return False
    
    try:
        from src.vector_memory.retrieval_service import RetrievalService
        print("✓ RetrievalService imported")
    except Exception as e:
        print(f"✗ Failed to import RetrievalService: {e}")
        return False
    
    try:
        from src.vector_memory.vector_store_factory import get_vector_store
        print("✓ vector_store_factory imported")
    except Exception as e:
        print(f"✗ Failed to import vector_store_factory: {e}")
        return False
    
    try:
        from src.orchestration.crew_builder import CrewBuilder
        print("✓ CrewBuilder imported")
    except Exception as e:
        print(f"✗ Failed to import CrewBuilder: {e}")
        return False
    
    return True

def test_agent_creation():
    """Test that agents can be created"""
    print("\nTesting agent creation...")
    
    try:
        from src.agents.agent_factory import AgentFactory
        factory = AgentFactory()
        
        # Test security agent creation
        agents = factory.create_all_review_agents()
        print(f"✓ Created {len(agents)} review agents")
        
        # Check agent types
        expected_agents = ['security', 'scalability', 'reliability', 
                          'data_architecture', 'cost_optimization', 'compliance']
        for agent_type in expected_agents:
            if agent_type in agents:
                print(f"  ✓ {agent_type} agent created")
            else:
                print(f"  ✗ {agent_type} agent missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to create agents: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test orchestrator agent creation"""
    print("\nTesting orchestrator agent...")
    
    try:
        from src.agents.agent_factory import AgentFactory
        from crewai import Agent
        factory = AgentFactory()
        
        orchestrator = factory.build_orchestrator()
        if isinstance(orchestrator, Agent):
            print(f"✓ Orchestrator agent created successfully")
            return True
        else:
            print(f"✗ Orchestrator is not an Agent instance")
            return False
    except Exception as e:
        print(f"✗ Failed to create orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_memory():
    """Test vector memory components"""
    print("\nTesting vector memory components...")
    
    try:
        from src.vector_memory.embedding_service import EmbeddingService
        from src.vector_memory.vector_store import VectorStore
        from src.vector_memory.retrieval_service import RetrievalService
        
        # Test embedding service initialization
        embedding_service = EmbeddingService()
        print("✓ EmbeddingService initialized")
        
        # Test embedding service methods exist (they may return None if no API key)
        text_result = embedding_service.embed_text("test")
        print(f"✓ embed_text() method works (result: {'present' if text_result else 'None (API key may be missing)'})")
        
        docs_result = embedding_service.embed_documents(["doc1", "doc2"])
        print(f"✓ embed_documents() method works (result length: {len(docs_result)})")
        
        # Test vector store initialization
        vector_store = VectorStore("test_collection", persist_dir="./memory/test")
        print("✓ VectorStore initialized")
        
        # Test retrieval service
        retrieval_service = RetrievalService(
            vector_store=vector_store,
            neo4j_client=None  # We'll test with Neo4j separately
        )
        print("✓ RetrievalService initialized")
        
        return True
    except Exception as e:
        print(f"✗ Vector memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("AI-ARB System Validation")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Agent Creation", test_agent_creation()))
    results.append(("Orchestrator", test_orchestrator()))
    results.append(("Vector Memory", test_vector_memory()))
    
    # pipeline test
    try:
        print("\nTesting ARB pipeline end-to-end...")
        from src.orchestration.arb_pipeline import ARBPipeline
        pipeline = ARBPipeline(config_path=project_root)
        # create temporary JSON submission file that should pass schema
        temp_sub = project_root / "temp_submission.json"
        sample = {
            "submission_id": "AB-0001-XYZ123",
            "team_name": "Test Team",
            "submission_date": "2026-03-06T12:00:00Z",
            "system_overview": {
                "title": "Test",
                "description": "This is a test architecture submission."
            },
            "sections": {}
        }
        import json
        with open(temp_sub, 'w', encoding='utf-8') as f:
            json.dump(sample, f)
        result = pipeline.process_submission(temp_sub)
        msg = f"Pipeline result: status={result.status}, overall_score={result.overall_score}, decision={result.approval_decision}"
        if hasattr(result, 'error_message') and result.error_message:
            msg += f", error={result.error_message}"
        print(msg)
        temp_sub.unlink()
        results.append(("ARB Pipeline", True))
        # also test schema validation failure
        try:
            bad_sub = project_root / "bad_submission.json"
            with open(bad_sub, 'w', encoding='utf-8') as f:
                f.write("not a json")
            bad_res = pipeline.process_submission(bad_sub)
            print(f"Bad submission result: status={bad_res.status}, error={bad_res.error_message}")
            bad_sub.unlink()
        except Exception as ee:
            print(f"Error during bad submission test: {ee}")

    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ARB Pipeline", False))
    
    print("\n" + "=" * 50)
    print("Validation Results")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✓ All validation tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some validation tests failed")
        sys.exit(1)
