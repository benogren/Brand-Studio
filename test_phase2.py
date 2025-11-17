"""
Phase 2 Testing Script for AI Brand Studio.

This script tests all Phase 2 features including:
- Research Agent
- RAG System
- Validation Agent
- SEO Optimizer
- Brand Story Generator
- Session Management
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def test_research_agent():
    """Test the Research Agent."""
    print_section("TEST 1: Research Agent")

    from src.agents.research_agent import ResearchAgent

    agent = ResearchAgent(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )

    research = agent.research_industry(
        product_description="AI-powered fitness coaching app with personalized workout plans",
        industry="health-tech",
        target_audience="Fitness enthusiasts aged 25-40"
    )

    print("Research Results:")
    print(f"  Industry: {research['industry_analysis']['key_characteristics']}")
    print(f"  Trends: {research['industry_analysis']['trends']}")
    print(f"  Recommended Strategies: {research['recommendations']['suggested_strategies']}")
    print(f"  Personalities: {research['recommendations']['personality_fit']}")
    print(f"  Keywords: {research['recommendations']['keywords_to_explore'][:5]}")

    return research


def test_rag_system():
    """Test the RAG Brand Retrieval System."""
    print_section("TEST 2: RAG Brand Retrieval System")

    from src.rag.brand_retrieval import get_brand_retrieval
    from src.data.brand_names_dataset import get_dataset_stats

    # Dataset stats
    stats = get_dataset_stats()
    print("Dataset Statistics:")
    print(f"  Total Brands: {stats['total_brands']}")
    print(f"  Industries: {list(stats['industry_breakdown'].keys())}")

    # Retrieval test
    retrieval = get_brand_retrieval()
    results = retrieval.retrieve_similar_brands(
        query="fitness and wellness app",
        top_k=5,
        industry_filter="health"
    )

    print("\nTop 5 Similar Brands (Health Industry):")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['brand_name']} - {result['metadata']['category']}")
        print(f"     Strategy: {result['metadata']['naming_strategy']}, Score: {result['similarity_score']:.3f}")

    return results


def test_validation_agent():
    """Test the Validation Agent."""
    print_section("TEST 3: Validation Agent")

    from src.agents.validation_agent import ValidationAgent

    agent = ValidationAgent(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )

    # Test multiple brand names
    test_names = ['FitFlow', 'HealthSync', 'MyWorkoutAI']

    print("Validating Brand Names:")
    for name in test_names:
        result = agent.validate_brand_name(name)

        print(f"\n  {name}:")
        print(f"    Status: {result['validation_status'].upper()}")
        print(f"    Score: {result['overall_score']}/100")
        print(f"    Domains: .com={result['domain_check']['com_available']}, "
              f".ai={result['domain_check']['ai_available']}, "
              f".io={result['domain_check']['io_available']}")
        print(f"    Trademark Risk: {result['trademark_check']['risk_level']}")
        print(f"    Recommendation: {result['recommendation']}")
        if result['concerns']:
            print(f"    Concerns: {', '.join(result['concerns'])}")

    return test_names[0]  # Return first name for further testing


def test_seo_agent(brand_name):
    """Test the SEO Optimizer Agent."""
    print_section("TEST 4: SEO Optimizer Agent")

    from src.agents.seo_agent import SEOAgent

    agent = SEOAgent(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )

    seo_result = agent.optimize_brand_seo(
        brand_name=brand_name,
        product_description="AI-powered fitness coaching with personalized workout plans",
        industry="health-tech"
    )

    print(f"SEO Optimization for '{brand_name}':")
    print(f"  SEO Score: {seo_result['seo_score']}/100")
    print(f"  Meta Title: {seo_result['meta_title']}")
    print(f"  Meta Description: {seo_result['meta_description']}")
    print(f"  Primary Keywords: {', '.join(seo_result['primary_keywords'])}")
    print(f"  Secondary Keywords: {', '.join(seo_result['secondary_keywords'][:3])}")
    print(f"  Content Opportunities:")
    for topic in seo_result['content_opportunities']:
        print(f"    - {topic}")

    return seo_result


def test_story_agent(brand_name):
    """Test the Brand Story Generator Agent."""
    print_section("TEST 5: Brand Story Generator Agent")

    from src.agents.story_agent import StoryAgent

    agent = StoryAgent(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )

    print(f"Generating Brand Story for '{brand_name}'...")
    print("(This may take a moment as it uses real LLM generation)\n")

    story = agent.generate_brand_story(
        brand_name=brand_name,
        product_description="AI-powered fitness coaching with personalized workout plans",
        brand_personality="innovative",
        target_audience="Fitness enthusiasts aged 25-40"
    )

    print("Generated Brand Story:")
    print("\nTagline Options:")
    for i, tagline in enumerate(story['taglines'], 1):
        print(f"  {i}. {tagline}")

    print(f"\nBrand Story:\n{story['brand_story'][:300]}...")

    print(f"\nHero Copy:\n{story['hero_copy'][:200]}...")

    print(f"\nValue Proposition:\n{story['value_proposition']}")

    return story


def test_session_manager(brand_name):
    """Test the Session Manager."""
    print_section("TEST 6: Session Management")

    from src.database.session_manager import get_session_manager

    sm = get_session_manager()

    # Create a new session
    session_id = sm.create_session(user_id="test_user_phase2")
    print(f"Created Session: {session_id}")

    # Add events
    sm.add_event(session_id, "message", "User requested fitness app brand names", "user")
    sm.add_event(session_id, "generation", f"Generated brand name: {brand_name}", "agent")
    print("Added 2 events to session")

    # Add generated brands
    brand_data = {
        "brand_name": brand_name,
        "naming_strategy": "portmanteau",
        "tagline": "Where fitness meets innovation",
        "validation_status": "clear",
        "validation_score": 90,
        "seo_score": 85
    }
    sm.add_generated_brand(session_id, brand_data)
    print(f"Added brand '{brand_name}' to session")

    # Get session statistics
    stats = sm.get_statistics()
    print(f"\nSession Statistics:")
    print(f"  Total Sessions: {stats['total_sessions']}")
    print(f"  Total Brands Generated: {stats['total_brands_generated']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Storage Location: {stats['storage_location']}")

    # List sessions
    sessions = sm.list_sessions(limit=5)
    print(f"\nRecent Sessions ({len(sessions)}):")
    for s in sessions:
        print(f"  - {s['session_id'][:8]}... User: {s['user_id']}, "
              f"Brands: {s['brand_count']}, Events: {s['event_count']}")

    return session_id


def test_name_generator_with_all_features():
    """Test Name Generator with all Phase 2 enhancements."""
    print_section("TEST 7: Integrated Name Generation (All Features)")

    from src.agents.name_generator import NameGeneratorAgent

    agent = NameGeneratorAgent(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )

    print("Generating brand names with real LLM...")
    print("(Using Google AI API - this may take 10-15 seconds)\n")

    names = agent.generate_names(
        product_description="AI-powered fitness coaching with personalized workout plans",
        target_audience="Fitness enthusiasts aged 25-40",
        brand_personality="innovative",
        industry="health-tech",
        num_names=10
    )

    print(f"Generated {len(names)} Brand Names:\n")
    for i, name in enumerate(names[:5], 1):  # Show first 5
        print(f"{i}. {name['brand_name']}")
        print(f"   Strategy: {name['naming_strategy']}")
        print(f"   Tagline: {name['tagline']}")
        print(f"   Rationale: {name['rationale'][:80]}...")
        print()

    print(f"... and {len(names) - 5} more names")

    return names


def run_all_tests():
    """Run all Phase 2 tests."""
    print("\n" + "=" * 70)
    print(" AI BRAND STUDIO - PHASE 2 TESTING")
    print("=" * 70)
    print("\nTesting all Phase 2 features:")
    print("  - Research Agent")
    print("  - RAG Brand Retrieval")
    print("  - Validation Agent")
    print("  - SEO Optimizer")
    print("  - Brand Story Generator")
    print("  - Session Management")
    print("  - Integrated Name Generation")

    try:
        # Test 1: Research Agent
        research = test_research_agent()

        # Test 2: RAG System
        rag_results = test_rag_system()

        # Test 3: Validation Agent
        validated_name = test_validation_agent()

        # Test 4: SEO Agent
        seo_result = test_seo_agent(validated_name)

        # Test 5: Story Agent
        story = test_story_agent(validated_name)

        # Test 6: Session Manager
        session_id = test_session_manager(validated_name)

        # Test 7: Integrated Name Generation
        generated_names = test_name_generator_with_all_features()

        # Final Summary
        print_section("TESTING COMPLETE - ALL TESTS PASSED! ✓")
        print("Phase 2 Features Status:")
        print("  ✓ Research Agent - Working")
        print("  ✓ RAG Brand Retrieval - Working")
        print("  ✓ Validation Agent - Working")
        print("  ✓ SEO Optimizer - Working")
        print("  ✓ Brand Story Generator - Working")
        print("  ✓ Session Management - Working")
        print("  ✓ Name Generation with LLM - Working")
        print("\n🎉 All Phase 2 features are operational!")

    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
