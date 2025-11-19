#!/usr/bin/env python3
"""
Main entry point for AI Brand Studio.

This module provides a CLI interface using ADK Runner to execute
the orchestrator agent for brand generation.
"""

import os
import sys
import json
from typing import Dict, Any
from dotenv import load_dotenv

# ADK imports
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.plugins.logging_plugin import LoggingPlugin

# Brand Studio imports
from src.agents.orchestrator import create_orchestrator


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


def get_sample_user_brief() -> str:
    """
    Get a sample user brief for testing.

    Returns:
        Sample user brief as a prompt string
    """
    return """
Create a brand identity for the following product:

Product Description: AI-powered meal planning app for busy millennial parents.
The app uses conversational AI to provide daily check-ins and mood tracking,
plus personalized recipe suggestions that fit your schedule, dietary needs,
and family preferences.

Target Audience: Parents aged 28-40 with young children

Brand Personality: Warm, approachable, helpful

Industry: Food Tech / Health & Wellness

Please generate:
1. Research insights about the industry and competitive landscape
2. 20-50 creative brand name candidates
3. Validation results for domain/trademark availability
4. SEO optimization including meta title and description
5. Brand story with taglines and positioning
"""


def print_runner_result(result: Any) -> None:
    """
    Print ADK Runner result in a formatted way.

    Args:
        result: Runner result (can be string or dict)
    """
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO - BRAND IDENTITY GENERATED")
    print("=" * 70)

    if isinstance(result, str):
        print("\n" + result)
    elif isinstance(result, dict):
        print("\n" + json.dumps(result, indent=2))
    else:
        print("\n" + str(result))

    print("\n" + "=" * 70)


def main():
    """Main entry point for AI Brand Studio using ADK Runner."""
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO")
    print("Multi-agent system for brand name generation")
    print("Powered by Google ADK")
    print("=" * 70 + "\n")

    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print(f"✓ Project: {config['project_id']}")
        print(f"✓ Location: {config['location']}")

        # Create orchestrator using ADK
        print("\nInitializing ADK orchestrator...")
        orchestrator = create_orchestrator()
        print("✓ Orchestrator initialized with ADK workflow patterns")
        print(f"  - Research → [Name+Validation Loop] → SEO → Story")

        # Create runner - use agent directly without App wrapper for simpler session handling
        print("\nCreating ADK InMemoryRunner...")
        runner = InMemoryRunner(agent=orchestrator)
        print("✓ Runner ready")

        # Get sample user brief
        print("\nPreparing sample user brief...")
        user_brief = get_sample_user_brief()
        print("✓ Sample brief loaded (meal planning app for parents)")

        # Execute workflow using Runner
        print("\n" + "-" * 70)
        print("EXECUTING WORKFLOW")
        print("-" * 70 + "\n")

        # Use run_debug (async method)
        import asyncio

        async def run_agent():
            events = await runner.run_debug(
                user_messages=user_brief,
                quiet=False,
                verbose=True
            )
            return events

        try:
            events = asyncio.run(run_agent())

            # Extract final result from events
            result = None
            for event in events:
                if hasattr(event, 'content') and event.content:
                    result = event.content

            if result is None:
                result = "No response generated"

        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Display results
        print_runner_result(result)

        # Save result to file
        output_file = 'brand_studio_result.json'
        with open(output_file, 'w') as f:
            if isinstance(result, str):
                json.dump({"result": result}, f, indent=2)
            elif isinstance(result, dict):
                json.dump(result, f, indent=2)
            else:
                json.dump({"result": str(result)}, f, indent=2)

        print(f"\n✓ Full result saved to: {output_file}\n")

        sys.exit(0)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure:")
        print("  - GOOGLE_CLOUD_PROJECT is set")
        print("  - GOOGLE_CLOUD_LOCATION is set (default: us-central1)")
        print("  - GOOGLE_GENAI_USE_VERTEXAI is set to 1")
        print("\nRun: cp .env.example .env")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
