#!/usr/bin/env python3
"""
Quick test script for RAG integration in Name Generator.

Tests:
1. Name Generator initializes with RAG client
2. RAG retrieval works before generation
3. Fallback works when RAG fails
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test RAG integration
def test_rag_integration():
    """Test RAG integration in name generator."""

    print("=" * 80)
    print("Testing RAG Integration in Name Generator")
    print("=" * 80)

    # Import name generator
    try:
        from src.agents.name_generator import NameGeneratorAgent
        print("✓ Name Generator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Name Generator: {e}")
        return False

    # Initialize name generator
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'test-project')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    try:
        generator = NameGeneratorAgent(
            project_id=project_id,
            location=location,
            model_name="gemini-2.0-flash-exp"
        )
        print(f"✓ Name Generator initialized")
        print(f"  - RAG Client Available: {generator.rag_client is not None}")
    except Exception as e:
        print(f"✗ Failed to initialize Name Generator: {e}")
        return False

    # Test RAG retrieval (if client available)
    if generator.rag_client:
        print("\n" + "-" * 80)
        print("Testing RAG Retrieval")
        print("-" * 80)

        try:
            rag_examples = generator._retrieve_similar_brands(
                product_description="AI-powered meal planning app for busy parents",
                industry="food-tech"
            )
            print(f"✓ RAG retrieval successful")
            print(f"  - Retrieved {len(rag_examples)} similar brands")

            if rag_examples:
                print("\n  Sample brands retrieved:")
                for example in rag_examples[:5]:
                    print(f"    - {example['brand_name']} ({example['industry']})")
        except Exception as e:
            print(f"✗ RAG retrieval failed: {e}")
            print("  (This is expected if Vector Search endpoint is not deployed)")
    else:
        print("\n⚠ RAG client not available - will use non-RAG generation")

    # Test name generation (with RAG fallback)
    print("\n" + "-" * 80)
    print("Testing Name Generation with RAG Integration")
    print("-" * 80)

    try:
        names = generator.generate_names(
            product_description="AI-powered meal planning app for busy parents",
            target_audience="Parents aged 28-40",
            brand_personality="playful",
            industry="food-tech",
            num_names=5  # Small number for testing
        )

        print(f"✓ Name generation successful")
        print(f"  - Generated {len(names)} names")

        if names:
            print("\n  Generated names:")
            for name in names[:5]:
                print(f"    - {name.get('brand_name', 'Unknown')} ({name.get('naming_strategy', 'Unknown')})")
    except Exception as e:
        print(f"✗ Name generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("RAG Integration Test Complete!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = test_rag_integration()
    sys.exit(0 if success else 1)
