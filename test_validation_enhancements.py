#!/usr/bin/env python3
"""
Test script for validation enhancements:
1. Domain prefix checking (get-, try-, use-, my-, etc.)
2. Search collision detection
"""

import asyncio
import os
from dotenv import load_dotenv
from src.cli import run_validation

async def test_validation():
    """Test validation with prefix checking and collision detection."""
    load_dotenv()

    print("Testing Validation Enhancements")
    print("=" * 70)

    # Test data
    product_info = {
        'product': 'AI fitness tracking app',
        'audience': 'Health-conscious millennials',
        'personality': 'innovative',
        'industry': 'fitness'
    }

    # Test with a name that likely has .com taken
    test_names = "FitBot, HealthAI"

    print(f"\nValidating: {test_names}")
    print(f"Product: {product_info['product']}")
    print(f"Industry: {product_info['industry']}")
    print("\nRunning validation (this may take a minute)...\n")

    result = await run_validation(test_names, product_info)

    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(result)
    print("\n" + "=" * 70)

    # Check if results include expected features
    has_prefix_check = 'get' in result.lower() or 'try' in result.lower() or 'prefix' in result.lower()
    has_collision = 'collision' in result.lower() or 'search' in result.lower()

    print("\nFeature Check:")
    print(f"✓ Prefix variations: {'YES' if has_prefix_check else 'NO'}")
    print(f"✓ Collision detection: {'YES' if has_collision else 'NO'}")

if __name__ == '__main__':
    asyncio.run(test_validation())
