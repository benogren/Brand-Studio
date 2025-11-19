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
        kept_list = []
        if kept_names:
            kept_list = [name.strip() for name in kept_names.split(',') if name.strip()]

        if kept_list:
            prompt = f"""
IMPORTANT: Keep these names that the user liked:
{', '.join(kept_list)}

Now generate {count} ADDITIONAL brand names to supplement the kept names, incorporating this feedback:

User feedback: {feedback}

Product: {product_info['product']}
Personality: {product_info['personality']}
Industry: {product_info['industry']}

Return as JSON array with ALL names (kept ones + new ones) with: name, strategy, rationale, strength_score
Mark the kept names with "kept": true in the JSON.
"""
        else:
            prompt = f"""
Generate {count} NEW brand names incorporating this feedback:

User feedback: {feedback}

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


async def run_validation(names: str, product_info: Dict[str, str]) -> Dict[str, Any]:
    """Run validation agent with collision detection. Returns structured data."""
    from src.agents.collision_agent import BrandCollisionAgent
    import json
    import re

    # Sanitize brand names - remove or warn about special characters
    sanitized_names = []
    original_names = [n.strip() for n in names.split(',')]

    for name in original_names:
        # Check for special characters that might cause issues
        if any(char in name for char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '+', '[', ']', '{', '}', '|', '\\', ';', ':', '"', "'", '<', '>', '?', '/']):
            print(f"\n⚠️  Warning: '{name}' contains special characters that may not be valid in domains.")
            print(f"   Domains typically only allow letters, numbers, and hyphens.")
            sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
            if sanitized and sanitized.strip():
                print(f"   Using sanitized version: '{sanitized.strip()}'")
                sanitized_names.append(sanitized.strip())
            else:
                print(f"   Skipping '{name}' - no valid characters remaining after sanitization.\n")
        else:
            sanitized_names.append(name)

    if not sanitized_names:
        return {
            'validation_data': [{'raw_output': 'No valid brand names to validate after sanitization.'}],
            'collision_data': [],
            'raw_validation_output': 'No valid brand names to validate.'
        }

    # Run domain and trademark validation
    validation_agent = create_validation_agent()
    runner = InMemoryRunner(agent=validation_agent)

    prompt = f"""
Validate these brand names:
{', '.join(sanitized_names)}

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

    # Try to parse JSON from validation output
    validation_data = []
    try:
        # Extract JSON from markdown code blocks or raw text
        json_match = re.search(r'```json\s*(.*?)\s*```', validation_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
        else:
            parsed = json.loads(validation_output)

        # Handle both single object and array
        if isinstance(parsed, dict):
            validation_data = [parsed]
        else:
            validation_data = parsed
    except:
        # If parsing fails, just store the raw text
        validation_data = [{"raw_output": validation_output}]

    # Run collision detection for search results (use sanitized names)
    collision_data = []
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        collision_agent = BrandCollisionAgent(project_id=project_id)

        for name in sanitized_names:
            if name:
                collision_result = collision_agent.analyze_brand_collision(
                    brand_name=name,
                    industry=product_info.get('industry', 'general'),
                    product_description=product_info.get('product', '')
                )
                collision_data.append({
                    'brand_name': name,
                    'collision_result': collision_result
                })
    except Exception as e:
        logger.warning(f"Collision detection failed: {e}")

    return {
        'validation_data': validation_data,
        'collision_data': collision_data,
        'raw_validation_output': validation_output
    }


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


def display_validation_results(validation_results: Dict[str, Any]):
    """Display detailed validation results in a structured format."""
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70 + "\n")

    validation_data = validation_results.get('validation_data', [])
    collision_data = validation_results.get('collision_data', [])

    # Display each validated name
    for i, val_data in enumerate(validation_data, 1):
        if 'raw_output' in val_data:
            # Fallback: just display raw output if parsing failed
            print(val_data['raw_output'])
            continue

        brand_name = val_data.get('brand_name', f'Name #{i}')
        status = val_data.get('validation_status', 'UNKNOWN')
        score = val_data.get('overall_score', 0)

        # Header
        print(f"{'='*70}")
        print(f"BRAND NAME: {brand_name}")
        print(f"Status: {status} | Overall Score: {score}/100")
        print(f"{'='*70}\n")

        # Domain Availability
        domain_info = val_data.get('domain_availability', {})
        if domain_info:
            print("📍 DOMAIN AVAILABILITY:")
            print("-" * 70)
            best_available = domain_info.get('best_available', 'N/A')
            print(f"   Best Available: {best_available}")
            print(f"   Domain Score: {domain_info.get('domain_score', 0)}/50\n")

            # Separate base domains and prefix variations
            base_domains = {}
            prefix_domains = {}

            for domain, available in domain_info.items():
                if domain not in ['best_available', 'domain_score']:
                    # Check if it's a prefixed domain (contains common prefixes)
                    domain_lower = domain.lower()
                    is_prefix = any(domain_lower.startswith(prefix) for prefix in ['get', 'try', 'use', 'my', 'hello', 'your'])

                    if is_prefix:
                        prefix_domains[domain] = available
                    else:
                        base_domains[domain] = available

            # Show base TLDs first
            if base_domains:
                print("   Base Domains:")
                for tld, available in base_domains.items():
                    status_icon = "✅" if available else "❌"
                    status_text = "Available" if available else "Unavailable"
                    print(f"   {status_icon} {tld:25s} {status_text}")

            # Show prefix variations
            if prefix_domains:
                print("\n   Prefix Variations (.com):")
                for domain, available in prefix_domains.items():
                    status_icon = "✅" if available else "❌"
                    status_text = "Available" if available else "Unavailable"
                    print(f"   {status_icon} {domain:25s} {status_text}")

            print()

        # Trademark Analysis
        trademark_info = val_data.get('trademark_analysis', {})
        if trademark_info:
            print("⚖️  TRADEMARK ANALYSIS:")
            print("-" * 70)
            risk_level = trademark_info.get('risk_level', 'unknown').upper()
            conflicts_found = trademark_info.get('conflicts_found', 0)
            trademark_score = trademark_info.get('trademark_score', 0)

            risk_icon = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
            print(f"   Risk Level: {risk_icon} {risk_level}")
            print(f"   Conflicts Found: {conflicts_found}")
            print(f"   Trademark Score: {trademark_score}/50\n")

            exact_matches = trademark_info.get('exact_matches', [])
            if exact_matches:
                print(f"   ⚠️  Exact Matches:")
                for match in exact_matches:
                    print(f"      - {match}")

            similar_marks = trademark_info.get('similar_marks', [])
            if similar_marks:
                print(f"   ⚠️  Similar Marks:")
                for mark in similar_marks:
                    print(f"      - {mark}")

            print()

        # Recommendation
        recommendation = val_data.get('recommendation', 'N/A')
        action_required = val_data.get('action_required', 'N/A')
        if recommendation:
            print("💡 RECOMMENDATION:")
            print("-" * 70)
            print(f"   {recommendation}")
            if action_required:
                print(f"\n   Action Required: {action_required}")
            print()

        print()

    # Display collision detection results
    if collision_data:
        print("\n" + "=" * 70)
        print("SEARCH COLLISION ANALYSIS")
        print("=" * 70 + "\n")

        for collision_entry in collision_data:
            brand_name = collision_entry.get('brand_name', 'Unknown')
            collision_result = collision_entry.get('collision_result', {})

            print(f"{'='*70}")
            print(f"BRAND: {brand_name}")
            print(f"{'='*70}\n")

            risk_level = collision_result.get('collision_risk_level', 'unknown').upper()
            risk_summary = collision_result.get('risk_summary', 'No analysis available')
            recommendation = collision_result.get('recommendation', 'N/A')

            risk_icon = "🟢" if risk_level == "NONE" or risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
            print(f"🔍 Risk Level: {risk_icon} {risk_level}\n")
            print(f"📊 Risk Summary:")
            print(f"   {risk_summary}\n")
            print(f"💡 Recommendation:")
            print(f"   {recommendation}\n")
            print()

    print("=" * 70)


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

            if kept:
                print(f"\nKeeping your liked names and generating {count} additional names based on your feedback...")
            else:
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

    # Validation and post-validation loop
    validation_results = None
    while True:
        print("\n" + "=" * 70)
        print("VALIDATION")
        print("=" * 70)

        names_to_validate = input("\nEnter names to validate (comma-separated): ").strip()

        if not names_to_validate:
            print("⚠️  No names entered. Please enter at least one name to validate.\n")
            continue

        print("\nValidating names (checking domains, trademarks, and search collisions)...")
        print("This may take a minute...\n")

        validation_results = asyncio.run(run_validation(names_to_validate, product_info))
        display_validation_results(validation_results)

        # Post-validation options
        print("\nWhat would you like to do next?")
        print("  1. Generate more names with feedback")
        print("  2. Validate different names")
        print("  3. Continue to brand story")
        print("  4. Quit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == '1':
            # Go back to name generation with feedback
            iteration += 1

            # Name generation loop (same as the initial generation loop)
            while True:
                print(f"\n{'='*70}")
                print(f"ROUND {iteration}: NAME GENERATION WITH FEEDBACK")
                print("=" * 70)

                feedback = input("\nWhat feedback do you have? (e.g., 'More tech-focused', 'Shorter names'): ").strip()
                kept = input("Any names you liked from validation? (comma-separated, or press Enter): ").strip()
                count = input("How many new names? (default=10): ").strip()
                count = int(count) if count.isdigit() else 10

                if kept:
                    print(f"\nKeeping your liked names and generating {count} additional names based on your feedback...")
                else:
                    print(f"\nGenerating {count} new names based on your feedback...")

                names_output = asyncio.run(run_name_generation(product_info, count, feedback, kept))
                all_names.append(names_output)
                display_names(names_output)

                # Show name generation menu options
                print("\nWhat would you like to do next?")
                print("  1. Generate more names with feedback")
                print("  2. Validate selected names")
                print("  3. Quit")

                name_choice = input("\nEnter choice (1-3): ").strip()

                if name_choice == '1':
                    iteration += 1
                    continue  # Continue name generation loop
                elif name_choice == '2':
                    break  # Break to go back to validation loop
                elif name_choice == '3':
                    print("\nGoodbye!")
                    sys.exit(0)
                else:
                    print("Invalid choice, continuing...")
                    iteration += 1
                    continue

            # After breaking from name generation, continue to validation loop
            continue

        elif choice == '2':
            # Validate different names
            continue

        elif choice == '3':
            # Continue to story
            break

        elif choice == '4':
            print("\nGoodbye!")
            sys.exit(0)

        else:
            print("Invalid choice. Please try again.")
            continue

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
