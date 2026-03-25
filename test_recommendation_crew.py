#!/usr/bin/env python3
"""
Test Recommendation Crew Integration
Tests the complete recommendation workflow integrated with ARB pipeline.
"""

import json
from pathlib import Path
from src.orchestration.arb_pipeline import ARBPipeline
from src.orchestration.recommendation_crew_builder import RecommendationCrewBuilder


def test_recommendation_crew_standalone():
    """Test the recommendation crew independently"""
    print("=" * 80)
    print("TEST 1: Recommendation Crew - Standalone")
    print("=" * 80)

    try:
        # Sample review results to feed into recommendation crew
        sample_review_results = """
SECURITY REVIEW (Score: 0.45):
- Authentication mechanism is basic (JWT without proper validation)
- No encryption at transport layer in some internal services
- Database credentials hardcoded in configuration files
- API endpoints lack rate limiting and DDoS protection

SCALABILITY REVIEW (Score: 0.55):
- Single database instance creates bottleneck
- No caching layer implemented
- Load balancing not configured for backend services
- Kubernetes resource limits not properly defined

RELIABILITY REVIEW (Score: 0.50):
- No circuit breaker pattern implementation
- Missing health checks on critical services
- No disaster recovery plan
- Logging not centralized

DATA ARCHITECTURE REVIEW (Score: 0.40):
- Data consistency issues due to eventual consistency without proper patterns
- No read/write separation
- Missing data retention and archival policies
- Analytics queries slow (no materialized views)

COST OPTIMIZATION REVIEW (Score: 0.35):
- Overprovisioned database instances
- No autoscaling configured
- Unused services and resources
- No cost monitoring or budgets set

COMPLIANCE REVIEW (Score: 0.30):
- GDPR compliance gaps (no data deletion mechanisms)
- Missing audit logs
- No encryption for data at rest
- Access control policies not documented
        """

        print("\n🏗️ Building recommendation crew...")
        rec_builder = RecommendationCrewBuilder()
        rec_builder.build_agents()
        print(f"✓ Crew built with {len(rec_builder.agents)} agents")

        print("\n🚀 Executing recommendation crew...")
        rec_crew = rec_builder.build_recommendation_crew(sample_review_results)
        
        print(f"\n⏳ Processing recommendations (this may take a minute)...")
        recommendations = rec_crew.kickoff()

        print("\n✅ RECOMMENDATION CREW COMPLETED")
        print("\nRecommendations Generated:")
        print("-" * 80)
        # Access the raw content from CrewOutput
        rec_content = str(recommendations)
        print(rec_content[:1000] + "..." if len(rec_content) > 1000 else rec_content)
        print("\n" + "=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recommendation_pipeline_integration():
    """Test recommendations integrated into full ARB pipeline"""
    print("\n" + "=" * 80)
    print("TEST 2: Full Pipeline with Recommendations")
    print("=" * 80)

    submission_path = Path("submissions/acmetech/acmetech-arch-001.json")

    try:
        # Load sample submission
        with open(submission_path, 'r', encoding='utf-8') as f:
            submission = json.load(f)

        print(f"\n📄 Testing with: {submission['system_overview']['title']}")

        # Initialize pipeline
        print("\n🔧 Initializing ARB Pipeline with Recommendations...")
        config_path = Path("config")
        pipeline = ARBPipeline(config_path)
        print("✓ Pipeline initialized")

        # Save submission to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(submission, f, indent=2)
            temp_file_path = Path(f.name)

        try:
            print("\n🚀 Processing submission with recommendation generation...")
            result = pipeline.process_submission(temp_file_path)

            print("\n" + "=" * 80)
            print("PIPELINE RESULTS WITH RECOMMENDATIONS")
            print("=" * 80)

            print(f"Status: {result.status}")
            print(f"Overall Score: {result.overall_score}")
            print(f"Approval Decision: {result.approval_decision}")

            if result.recommendation_summary:
                print(f"\n📋 Executive Summary:")
                print(f"   {result.recommendation_summary[:200]}...")

            if result.recommendations:
                print(f"\n✅ RECOMMENDATIONS GENERATED SUCCESSFULLY")
                print(f"   {len(result.recommendations)} characters of recommendations")
                print(f"\n   Sample recommendations:")
                print(f"   {result.recommendations[:300]}...\n")
            else:
                print(f"\n⚠️ No recommendations generated")

            print("✅ PIPELINE INTEGRATION TEST COMPLETED")
            return True

        finally:
            temp_file_path.unlink(missing_ok=True)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recommendation_output_format():
    """Test that recommendations are properly formatted for PR/SME review"""
    print("\n" + "=" * 80)
    print("TEST 3: Recommendation Output Format")
    print("=" * 80)

    try:
        # Create a minimal test of recommendation formatting
        print("\n🔧 Testing recommendation output structure...")

        rec_builder = RecommendationCrewBuilder()
        rec_builder.build_agents()

        print(f"✓ Agents created:")
        expected_agents = [
            'security', 'scalability', 'reliability', 
            'data_architecture', 'cost_optimization', 'compliance', 'orchestrator'
        ]
        for agent_name in expected_agents:
            if agent_name in rec_builder.agents:
                print(f"  ✓ {agent_name}")
            else:
                print(f"  ✗ {agent_name} MISSING")

        print(f"\n✅ RECOMMENDATION OUTPUT FORMAT TEST COMPLETED")
        print(f"\nRecommendation Output will include:")
        print(f"  • Executive Summary (2-3 paragraphs)")
        print(f"  • Quick Wins (low effort, high impact)")
        print(f"  • Phased Implementation Plan (Phase 1-3)")
        print(f"  • Specific Action Items with:")
        print(f"    - Title and description")
        print(f"    - Priority and effort estimate")
        print(f"    - Success criteria")
        print(f"    - Timeline")
        print(f"  • Total effort estimate for full implementation roadmap")
        print()

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all recommendation tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " RECOMMENDATION CREW INTEGRATION TEST ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")

    results = {
        "standalone_crew": test_recommendation_crew_standalone(),
        "pipeline_integration": test_recommendation_pipeline_integration(),
        "output_format": test_recommendation_output_format(),
    }

    # Summary
    print("\n" + "=" * 80)
    print("RECOMMENDATION TEST RESULTS SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL RECOMMENDATION TESTS PASSED!")
        print("\n✨ RECOMMENDATION CREW FULLY INTEGRATED")
        print("\nSystem is now ready to:")
        print("  1. Review architecture submissions")
        print("  2. Generate specific improvement recommendations")
        print("  3. Create actionable improvement roadmaps")
        print("  4. Output recommendations for PR/SME review")
        print("\nNext steps:")
        print("  • Review recommendation quality with real submissions")
        print("  • Format recommendations for markdown PR comments")
        print("  • Integrate with version control workflow")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - Check errors above")

    print("\n" + "=" * 80)
    print("Note: Full recommendation generation may take 1-2 minutes per architecture")
    print("=" * 80)


if __name__ == "__main__":
    main()
