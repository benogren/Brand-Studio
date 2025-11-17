#!/usr/bin/env python3
"""
Main entry point for AI Brand Studio.

This module provides a CLI interface to invoke the orchestrator agent
with sample inputs for testing and demonstration.
"""

import os
import sys
import json
from typing import Dict, Any
from dotenv import load_dotenv

from src.agents.orchestrator import BrandStudioOrchestrator


def load_config() -> Dict[str, str]:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary with configuration values

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load .env file
    load_dotenv()

    # Get required configuration
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT environment variable is required. "
            "Please configure your .env file."
        )

    return {
        'project_id': project_id,
        'location': location
    }


def get_sample_user_brief() -> Dict[str, Any]:
    """
    Get a sample user brief for testing.

    Returns:
        Sample user brief dictionary
    """
    return {
        'product_description': (
            'AI-powered meal planning app for busy millennial parents. '
            'The app uses conversational AI to provide daily check-ins and '
            'mood tracking, plus personalized recipe suggestions that fit '
            'your schedule, dietary needs, and family preferences.'
        ),
        'target_audience': 'Parents aged 28-40 with young children',
        'brand_personality': 'warm',
        'industry': 'food_tech'
    }


def print_workflow_result(result: Dict[str, Any]) -> None:
    """
    Print workflow result in a formatted way.

    Args:
        result: Workflow result dictionary
    """
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO - WORKFLOW RESULT")
    print("=" * 70)

    # Status
    status = result.get('status', 'unknown')
    print(f"\nStatus: {status.upper()}")

    # User brief summary
    user_brief = result.get('user_brief', {})
    if user_brief:
        print(f"\nIndustry: {user_brief.get('industry', 'N/A')}")
        print(f"Brand Personality: {user_brief.get('brand_personality', 'N/A')}")

    # Workflow stages
    stages = result.get('workflow_stages', [])
    if stages:
        print(f"\nWorkflow Stages Executed: {', '.join(stages)}")

    # Iterations
    iterations = result.get('iteration', 0)
    if iterations:
        print(f"Total Iterations: {iterations}")

    # Timing
    start_time = result.get('start_time')
    end_time = result.get('end_time')
    if start_time and end_time:
        from datetime import datetime
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        duration = (end - start).total_seconds()
        print(f"Duration: {duration:.2f} seconds")

    # Brand names
    brand_names = result.get('brand_names', [])
    if brand_names:
        print(f"\nGenerated Brand Names ({len(brand_names)}):")
        for i, name in enumerate(brand_names[:10], 1):  # Show first 10
            print(f"  {i}. {name}")
        if len(brand_names) > 10:
            print(f"  ... and {len(brand_names) - 10} more")

    # Selected brand
    selected_brand = result.get('selected_brand')
    if selected_brand:
        print(f"\nSelected Brand: {selected_brand}")

    # Validation results
    validation = result.get('validation_results', {})
    if validation:
        print("\nValidation Results:")
        print(f"  Low Risk Trademarks: {validation.get('low_risk_count', 0)}")
        print(f"  Available .com Domains: {validation.get('available_com_count', 0)}")

    # SEO data
    seo_data = result.get('seo_data', {})
    if seo_data and seo_data.get('seo_scores'):
        avg_score = sum(seo_data['seo_scores'].values()) / len(seo_data['seo_scores'])
        print(f"\nAverage SEO Score: {avg_score:.1f}/100")

    # Brand story
    brand_story = result.get('brand_story', {})
    if brand_story:
        taglines = brand_story.get('taglines', [])
        if taglines:
            print(f"\nTaglines Generated: {len(taglines)}")
            for i, tagline in enumerate(taglines[:3], 1):
                print(f"  {i}. {tagline}")

    # Error information
    if status == 'failed':
        error = result.get('error', 'Unknown error')
        failed_stage = result.get('failed_stage', 'unknown')
        print(f"\nError: {error}")
        print(f"Failed Stage: {failed_stage}")

    print("\n" + "=" * 70 + "\n")


def main():
    """Main entry point for AI Brand Studio."""
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO")
    print("Multi-agent system for brand name generation")
    print("=" * 70 + "\n")

    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print(f"✓ Project: {config['project_id']}")
        print(f"✓ Location: {config['location']}")

        # Initialize orchestrator
        print("\nInitializing orchestrator agent...")
        orchestrator = BrandStudioOrchestrator(
            project_id=config['project_id'],
            location=config['location'],
            enable_cloud_logging=True
        )
        print("✓ Orchestrator initialized")

        # Get sample user brief
        print("\nPreparing sample user brief...")
        user_brief = get_sample_user_brief()
        print(f"✓ Product: {user_brief['product_description'][:60]}...")
        print(f"✓ Target Audience: {user_brief['target_audience']}")
        print(f"✓ Brand Personality: {user_brief['brand_personality']}")

        # Execute workflow
        print("\n" + "-" * 70)
        print("EXECUTING WORKFLOW")
        print("-" * 70 + "\n")

        result = orchestrator.coordinate_workflow(user_brief)

        # Display results
        print_workflow_result(result)

        # Save result to file
        output_file = 'brand_studio_result.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✓ Full result saved to: {output_file}\n")

        # Exit code based on status
        if result.get('status') == 'completed':
            sys.exit(0)
        else:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure:")
        print("  - GOOGLE_CLOUD_PROJECT is set")
        print("  - You have run: cp .env.example .env")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
