#!/usr/bin/env python3
"""
Interactive Chat Mode for AI Brand Studio.

Provides a conversational interface where users can interact with the
brand generation workflow through simple prompts instead of long commands.

Usage:
    python -m src.cli_chat
"""

import os
import sys
import asyncio
import warnings
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from src.agents.research_agent import create_research_agent
from src.agents.name_generator import create_name_generator_agent
from src.agents.validation_agent import create_validation_agent
from src.agents.story_agent import create_story_agent
from src.infrastructure.session_manager import get_session_manager, BrandSessionState

# Suppress ADK warnings for cleaner CLI output
warnings.filterwarnings('ignore', message='.*App name mismatch.*')
warnings.filterwarnings('ignore', message='.*non-text parts in the response.*')
warnings.filterwarnings('ignore', message='.*ADK LoggingPlugin not available.*')

# Configure logging to suppress ADK debug messages
logging.getLogger('google.adk').setLevel(logging.ERROR)


class SuppressStderr:
    """Context manager to suppress stderr output."""
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO - INTERACTIVE MODE")
    print("=" * 70)
    print("\nWelcome! I'll help you create a complete brand identity.")
    print("Just answer a few questions and I'll guide you through the process.\n")


def get_product_info() -> Dict[str, str]:
    """Get product information from user."""
    print("First, tell me about your product:\n")

    product = input("What does your product do? ").strip()
    while not product:
        print("Please provide a product description.")
        product = input("What does your product do? ").strip()

    audience = input("Who is it for? (press Enter for 'General consumers'): ").strip()
    if not audience:
        audience = "General consumers"

    print("\nChoose a brand personality:")
    print("  1. Playful")
    print("  2. Professional")
    print("  3. Innovative")
    print("  4. Luxury")

    personality_map = {'1': 'playful', '2': 'professional', '3': 'innovative', '4': 'luxury'}
    choice = input("Enter number (1-4, default=3): ").strip() or '3'
    personality = personality_map.get(choice, 'innovative')

    industry = input("Industry/category (press Enter for 'general'): ").strip() or 'general'

    return {
        'product': product,
        'audience': audience,
        'personality': personality,
        'industry': industry
    }


def extract_text_from_events(events) -> str:
    """Extract text content from agent events."""
    text_parts = []
    for event in events:
        if hasattr(event, 'content'):
            content = event.content
            if isinstance(content, str):
                text_parts.append(content)
            elif hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
        elif hasattr(event, 'text') and event.text:
            text_parts.append(event.text)
    return '\n\n'.join(text_parts)


async def run_research(product_info: Dict[str, str]) -> str:
    """Run research agent."""
    research_agent = create_research_agent()
    runner = InMemoryRunner(agent=research_agent)

    prompt = f"""
Analyze this product for brand naming:

Product: {product_info['product']}
Audience: {product_info['audience']}
Personality: {product_info['personality']}
Industry: {product_info['industry']}

Provide research insights in JSON format.
"""

    with SuppressStderr():
        events = await runner.run_debug(user_messages=prompt, quiet=True, verbose=False)
    return extract_text_from_events(events)


async def run_name_generation(product_info: Dict[str, str], count: int, feedback: str = None, kept_names: str = None) -> str:
    """Run name generator agent."""
    name_generator = create_name_generator_agent()
    runner = InMemoryRunner(agent=name_generator)

    if feedback:
        prompt = f"""
Generate {count} NEW brand names incorporating this feedback:

Previous names you liked: {kept_names or 'None'}
Your feedback: {feedback}

Product: {product_info['product']}
Personality: {product_info['personality']}
Industry: {product_info['industry']}

Return as JSON array with: name, strategy, rationale, strength_score
"""
    else:
        prompt = f"""
Generate {count} creative brand names for:

Product: {product_info['product']}
Personality: {product_info['personality']}
Industry: {product_info['industry']}

Return as JSON array with: name, strategy, rationale, strength_score
"""

    with SuppressStderr():
        events = await runner.run_debug(user_messages=prompt, quiet=True, verbose=False)
    return extract_text_from_events(events)


async def run_validation(names: str, product_info: Dict[str, str]) -> str:
    """Run validation agent with collision detection."""
    from src.agents.collision_agent import BrandCollisionAgent

    # Run domain and trademark validation
    validation_agent = create_validation_agent()
    runner = InMemoryRunner(agent=validation_agent)

    prompt = f"""
Validate these brand names:
{names}

Check:
1. Domain availability (.com, .ai, .io, and other TLDs)
2. If .com is unavailable, also check prefix variations (get-, try-, use-, my-, etc.)
3. Trademark conflicts using USPTO database
4. Calculate overall risk scores

Return validation results in JSON format with domain availability, trademark analysis, and recommendations.
"""

    with SuppressStderr():
        events = await runner.run_debug(user_messages=prompt, quiet=True, verbose=False)
    validation_output = extract_text_from_events(events)

    # Run collision detection for search results
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        collision_agent = BrandCollisionAgent(project_id=project_id)

        collision_results = []
        for name in names.split(','):
            name = name.strip()
            if name:
                collision_result = collision_agent.analyze_brand_collision(
                    brand_name=name,
                    industry=product_info.get('industry', 'general'),
                    product_description=product_info.get('product', '')
                )
                collision_results.append(f"\n\n**Search Collision Analysis for {name}:**\n{collision_result.get('risk_summary', 'No analysis available')}\n- Risk Level: {collision_result.get('collision_risk_level', 'unknown')}\n- Recommendation: {collision_result.get('recommendation', 'N/A')}")

        # Combine validation and collision results
        combined_output = validation_output + "\n\n" + "=" * 70 + "\n## SEARCH RESULT COLLISION ANALYSIS\n" + "=" * 70 + "\n".join(collision_results)
        return combined_output

    except Exception as e:
        logger.warning(f"Collision detection failed: {e}")
        return validation_output + f"\n\n(Note: Search collision analysis unavailable: {e})"


async def run_story(brand_name: str, product_info: Dict[str, str]) -> str:
    """Run story agent."""
    story_agent = create_story_agent()
    runner = InMemoryRunner(agent=story_agent)

    prompt = f"""
Create a complete brand story for:

Brand Name: {brand_name}
Product: {product_info['product']}
Personality: {product_info['personality']}
Industry: {product_info['industry']}

Generate:
1. Five tagline options (5-8 words each, memorable and action-oriented)
2. Brand story (200-300 words)
3. Value proposition statement (20-30 words, clear and compelling)

Return in JSON format.
"""

    with SuppressStderr():
        events = await runner.run_debug(user_messages=prompt, quiet=True, verbose=False)
    return extract_text_from_events(events)


def display_names(names_output: str):
    """Display generated names in a readable format."""
    print("\n" + "=" * 70)
    print("GENERATED NAMES")
    print("=" * 70 + "\n")
    print(names_output)
    print()


def main():
    """Main interactive mode."""
    load_dotenv()

    # Check config
    if not os.getenv('GOOGLE_CLOUD_PROJECT'):
        print("Error: GOOGLE_CLOUD_PROJECT not set in .env file")
        sys.exit(1)

    # Suppress initial ADK plugin warning
    with SuppressStderr():
        # Import agents to trigger ADK initialization warnings
        pass

    print_banner()

    # Get product info
    product_info = get_product_info()

    print("\n" + "-" * 70)
    print("Great! Let me start by researching your industry...")
    print("-" * 70 + "\n")

    # Run research
    research_output = asyncio.run(run_research(product_info))
    print("✓ Research complete")

    # Name generation loop
    all_names = []
    iteration = 1

    while True:
        print(f"\n{'='*70}")
        print(f"ROUND {iteration}: NAME GENERATION")
        print("=" * 70)

        if iteration == 1:
            count = input("\nHow many names would you like? (default=15): ").strip()
            count = int(count) if count.isdigit() else 15

            print(f"\nGenerating {count} brand names...")
            names_output = asyncio.run(run_name_generation(product_info, count))
        else:
            feedback = input("\nWhat feedback do you have? (e.g., 'More tech-focused', 'Shorter names'): ").strip()
            kept = input("Any names you liked? (comma-separated, or press Enter): ").strip()
            count = input("How many new names? (default=10): ").strip()
            count = int(count) if count.isdigit() else 10

            print(f"\nGenerating {count} new names based on your feedback...")
            names_output = asyncio.run(run_name_generation(product_info, count, feedback, kept))

        all_names.append(names_output)
        display_names(names_output)

        print("\nWhat would you like to do next?")
        print("  1. Generate more names with feedback")
        print("  2. Validate selected names")
        print("  3. Quit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == '1':
            iteration += 1
            continue
        elif choice == '2':
            break
        elif choice == '3':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("Invalid choice, continuing...")
            iteration += 1

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    names_to_validate = input("\nEnter names to validate (comma-separated): ").strip()

    if names_to_validate:
        print("\nValidating names (checking domains, trademarks, and search collisions)...")
        print("This may take a minute...\n")

        validation_output = asyncio.run(run_validation(names_to_validate, product_info))

        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70 + "\n")
        print(validation_output)
        print()

    # Ask if they want to continue to story
    print("\nWould you like to generate a brand story for one of these names?")
    choice = input("Enter 'y' to continue or 'n' to quit: ").strip().lower()

    if choice != 'y':
        print("\nGoodbye!")
        sys.exit(0)

    # Brand story
    print("\n" + "=" * 70)
    print("BRAND STORY")
    print("=" * 70)

    final_name = input("\nWhat's your final brand name choice? ").strip()

    if final_name:
        print(f"\nGenerating complete brand story for '{final_name}'...")
        print("This may take a minute...\n")

        story_output = asyncio.run(run_story(final_name, product_info))

        print("=" * 70)
        print(f"BRAND IDENTITY: {final_name}")
        print("=" * 70 + "\n")
        print(story_output)
        print()

    print("\n" + "=" * 70)
    print("✓ BRAND IDENTITY COMPLETE!")
    print("=" * 70)
    print(f"\nYour brand: {final_name}")
    print("\nThank you for using AI Brand Studio!")
    print()


if __name__ == '__main__':
    main()
