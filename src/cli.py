#!/usr/bin/env python3
"""
Interactive Chat Mode for AI Brand Studio.

Provides a conversational interface where users can interact with the
brand generation workflow through simple prompts instead of long commands.

Usage:
    python -m src.cli_chat
"""

# IMPORTANT: Set up warning filters BEFORE any other imports
import warnings
warnings.filterwarnings('ignore', message='.*App name mismatch.*')
warnings.filterwarnings('ignore', message='.*non-text parts in the response.*')
warnings.filterwarnings('ignore', message='.*ADK LoggingPlugin not available.*')
warnings.filterwarnings('ignore', message='.*function_call.*')

import os
import sys
import asyncio
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from src.agents.research_agent import create_research_agent
from src.agents.name_generator import create_name_generator_agent
from src.agents.validation_agent import create_validation_agent
from src.agents.story_agent import create_story_agent
from src.infrastructure.session_manager import get_session_manager, BrandSessionState

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


def create_runner_for_agent(agent, app_name: str = None):
    """
    Create an InMemoryRunner with proper App wrapper to avoid name mismatch warnings.

    Args:
        agent: The ADK agent to wrap
        app_name: Optional app name (defaults to agent name)

    Returns:
        InMemoryRunner instance
    """
    if app_name is None:
        app_name = getattr(agent, 'name', 'BrandStudioAgent')

    app = App(
        name=app_name,
        root_agent=agent
    )

    return InMemoryRunner(app=app)


def print_banner():
    """Print welcome banner."""
    print("\n")
    print("=" * 80)
    print(r"""
    ___    ____   ____                      __   _____ __            ___
   /   |  /  _/  / __ )_________  ____  ____/ /  / ___// /___  ______/ (_)___
  / /| |  / /   / __  / ___/ __ \/ __ \/ __  /   \__ \/ __/ / / / __  / / __ \
 / ___ |_/ /   / /_/ / /  / /_/ / / / / /_/ /   ___/ / /_/ /_/ / /_/ / / /_/ /
/_/  |_/___/  /_____/_/   \__,_/_/ /_/\__,_/   /____/\__/\__,_/\__,_/_/\____/

    """)
    print("=" * 80)
    print("\nWelcome! I'll help you create a complete brand identity.")
    print("Just answer a few questions and I'll guide you through the process.\n")


def get_product_info() -> Dict[str, str]:
    """Get product information from user."""
    print("First, tell me about your product:\n")

    product = input("What does your product do? ").strip()
    while not product:
        print("Please provide a product description.")
        product = input("What does your product do? ").strip()

    audience = input("Great! Who is this product for? (e.g., 'busy professionals', 'Gen Z users', etc.): ").strip()
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

    industry = input("What industry/category is this for? (e.g., 'fitness', 'fintech', 'healthcare'): ").strip() or 'general'

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
    with SuppressStderr():
        research_agent = create_research_agent()
        runner = create_runner_for_agent(research_agent, "ResearchApp")

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
    with SuppressStderr():
        name_generator = create_name_generator_agent()
        runner = create_runner_for_agent(name_generator, "NameGeneratorApp")

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


async def run_validation(names: str, product_info: Dict[str, str], skip_collision: bool = False) -> Dict[str, Any]:
    """Run validation agent with optional collision detection. Returns structured data."""
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
    with SuppressStderr():
        validation_agent = create_validation_agent()
        runner = create_runner_for_agent(validation_agent, "ValidationApp")

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

    # Run validation with suppressed warnings
    with SuppressStderr():
        try:
            events = await runner.run_debug(user_messages=prompt, quiet=True, verbose=False)
        except Exception as e:
            print(f"\n⚠️  Error running validation agent: {e}\n")
            return {
                'validation_data': [{'raw_output': f'Validation failed: {str(e)}'}],
                'collision_data': [],
                'raw_validation_output': f'Error: {str(e)}'
            }

    validation_output = extract_text_from_events(events)

    # Check if we got any output
    if not validation_output or not validation_output.strip():
        print("\n⚠️  Warning: Validation agent returned empty response.")
        print("    This may be due to API issues or rate limits.\n")
        return {
            'validation_data': [{'raw_output': 'Validation agent returned no results. This may be due to API rate limits or configuration issues.'}],
            'collision_data': [],
            'raw_validation_output': 'Empty response from validation agent'
        }

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
    quota_exhausted = False

    # Skip collision detection if user requested it
    if skip_collision:
        return {
            'validation_data': validation_data,
            'collision_data': [],
            'raw_validation_output': validation_output
        }

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

                # Check if we hit quota limits
                if 'error' in collision_result:
                    error_msg = str(collision_result.get('error', ''))
                    if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg or 'quota' in error_msg.lower():
                        quota_exhausted = True
                        print(f"\n⚠️  API quota limit reached. Skipping remaining collision checks.")
                        print(f"   You can still see domain and trademark validation results below.\n")
                        break

                collision_data.append({
                    'brand_name': name,
                    'collision_result': collision_result
                })
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg or 'quota' in error_msg.lower():
            quota_exhausted = True
            print(f"\n⚠️  API quota limit reached. Collision detection skipped.")
            print(f"   You can still see domain and trademark validation results below.\n")
        else:
            print(f"\n⚠️  Collision detection failed: {e}")

    return {
        'validation_data': validation_data,
        'collision_data': collision_data,
        'raw_validation_output': validation_output
    }


async def run_story(brand_name: str, product_info: Dict[str, str]) -> str:
    """Run story agent."""
    with SuppressStderr():
        story_agent = create_story_agent()
        runner = create_runner_for_agent(story_agent, "StoryApp")

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


def display_research(research_output: str):
    """Display research findings in a readable format."""
    import json
    import re

    print("\n" + "=" * 80)
    print("INDUSTRY RESEARCH INSIGHTS")
    print("=" * 80 + "\n")

    # Try to parse JSON from the output
    try:
        # Extract JSON from markdown code blocks or raw text
        json_match = re.search(r'```json\s*(.*?)\s*```', research_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
        else:
            parsed = json.loads(research_output)

        # Display Industry Analysis
        industry = parsed.get('industry_analysis', {})
        if industry:
            print("🔍 INDUSTRY ANALYSIS")
            print("─" * 80)

            if industry.get('market_dynamics'):
                print(f"\nMarket Dynamics:\n   {industry['market_dynamics']}")

            if industry.get('key_characteristics'):
                print(f"\nKey Characteristics:")
                for char in industry['key_characteristics']:
                    print(f"   • {char}")

            if industry.get('trends'):
                print(f"\nEmerging Trends:")
                for trend in industry['trends']:
                    print(f"   • {trend}")

            if industry.get('terminology'):
                print(f"\nIndustry Terminology:")
                print(f"   {', '.join(industry['terminology'][:10])}")
            print()

        # Display Competitor Patterns
        competitors = parsed.get('competitor_patterns', {})
        if competitors:
            print("\n🏆 COMPETITOR NAMING PATTERNS")
            print("─" * 80)

            if competitors.get('common_strategies'):
                print(f"\nCommon Strategies:")
                for strategy in competitors['common_strategies']:
                    print(f"   • {strategy}")

            if competitors.get('successful_examples'):
                print(f"\nSuccessful Examples:")
                for example in competitors['successful_examples'][:5]:
                    brand = example.get('brand', 'N/A')
                    reason = example.get('why_it_works', 'N/A')
                    print(f"   • {brand}: {reason}")

            if competitors.get('patterns_to_avoid'):
                print(f"\nPatterns to Avoid:")
                for pattern in competitors['patterns_to_avoid']:
                    print(f"   ⚠️  {pattern}")
            print()

        # Display Audience Insights
        audience = parsed.get('audience_insights', {})
        if audience:
            print("\n👥 TARGET AUDIENCE INSIGHTS")
            print("─" * 80)

            if audience.get('demographics'):
                print(f"\nDemographics:\n   {audience['demographics']}")

            if audience.get('preferences'):
                print(f"\nPreferences:")
                for pref in audience['preferences']:
                    print(f"   • {pref}")

            if audience.get('communication_style'):
                print(f"\nCommunication Style:\n   {audience['communication_style']}")
            print()

        # Display Recommendations
        recommendations = parsed.get('recommendations', {})
        if recommendations:
            print("\n💡 STRATEGIC RECOMMENDATIONS")
            print("─" * 80)

            if recommendations.get('suggested_strategies'):
                print(f"\nSuggested Naming Strategies:")
                for strategy in recommendations['suggested_strategies']:
                    print(f"   ✓ {strategy}")

            if recommendations.get('keywords_to_explore'):
                print(f"\nKeywords to Explore:")
                print(f"   {', '.join(recommendations['keywords_to_explore'][:15])}")

            if recommendations.get('personality_fit'):
                print(f"\nBest Personality Fit:")
                print(f"   {', '.join([p.title() for p in recommendations['personality_fit']])}")

            if recommendations.get('avoid'):
                print(f"\nAvoid:")
                for avoid in recommendations['avoid']:
                    print(f"   ✗ {avoid}")
            print()

        print("=" * 80)

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # If parsing fails, fall back to raw output
        print("⚠️  Could not parse research format. Showing raw output:\n")
        if research_output and research_output.strip():
            print(research_output)
        else:
            print("⚠️  Research agent returned empty response.")
            print("    This may happen if the google_search tool is unavailable.")
            print("    Continuing with name generation using general knowledge...")
        print()


def display_names(names_output: str):
    """Display generated names in a readable format."""
    import json
    import re

    print("\n" + "=" * 80)
    print("GENERATED NAMES")
    print("=" * 80 + "\n")

    # Try to parse JSON from the output
    try:
        # Extract JSON from markdown code blocks or raw text
        json_match = re.search(r'```json\s*(.*?)\s*```', names_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
        else:
            parsed = json.loads(names_output)

        # Get the names array
        names_list = parsed.get('generated_names', [])

        if not names_list:
            # Fallback to raw output
            print(names_output)
            return

        # Display each name in a formatted way
        for i, name_data in enumerate(names_list, 1):
            name = name_data.get('name', 'Unknown')
            strategy = name_data.get('strategy', 'N/A')
            rationale = name_data.get('rationale', 'N/A')
            score = name_data.get('strength_score', 0)
            kept = name_data.get('kept', False)

            # Add visual indicator for kept names
            kept_indicator = " ⭐ [KEPT]" if kept else ""

            # Create score bar
            score_bar = "█" * (score // 10) + "░" * (10 - score // 10)

            print(f"{'─' * 80}")
            print(f"{i}. {name}{kept_indicator}")
            print(f"{'─' * 80}")
            print(f"   Strategy:  {strategy.title()}")
            print(f"   Score:     [{score_bar}] {score}/100")
            print(f"   Rationale: {rationale}")
            print()

        print("─" * 80)
        print(f"Total: {len(names_list)} brand names generated")
        print("─" * 80)

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # If parsing fails, fall back to raw output
        print("⚠️  Could not parse names format. Showing raw output:\n")
        print(names_output)
        print()


def display_story(story_output: str, brand_name: str):
    """Display brand story in a readable format."""
    import json
    import re

    print("\n" + "=" * 80)
    print(f"BRAND IDENTITY: {brand_name}")
    print("=" * 80 + "\n")

    # Try to parse JSON from the output
    try:
        # Extract JSON from markdown code blocks or raw text
        json_match = re.search(r'```json\s*(.*?)\s*```', story_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
        else:
            parsed = json.loads(story_output)

        # Display Taglines
        taglines = parsed.get('taglines', [])
        if taglines:
            print("✨ TAGLINE OPTIONS")
            print("─" * 80)
            print()

            for i, tagline_data in enumerate(taglines, 1):
                # Handle both string and dict formats
                if isinstance(tagline_data, dict):
                    tagline = tagline_data.get('tagline', str(tagline_data))
                    strategy = tagline_data.get('strategy', '')
                    rationale = tagline_data.get('rationale', '')

                    print(f"   {i}. \"{tagline}\"")
                    if strategy:
                        print(f"      Strategy: {strategy.replace('_', ' ').title()}")
                    if rationale:
                        import textwrap
                        wrapped_rationale = textwrap.fill(rationale, width=70, initial_indent='      ', subsequent_indent='      ')
                        print(f"{wrapped_rationale}")
                    print()
                else:
                    # Simple string tagline
                    print(f"   {i}. \"{tagline_data}\"")
                    print()

            print()

        # Display Value Proposition
        value_prop = parsed.get('value_proposition', '')
        if value_prop:
            print("🎯 VALUE PROPOSITION")
            print("─" * 80)
            print(f"\n   {value_prop}\n")
            print()

        # Display Brand Story
        brand_story = parsed.get('brand_story', '')
        if brand_story:
            print("📖 BRAND STORY")
            print("─" * 80)
            print()
            # Wrap text nicely at 76 characters
            import textwrap
            wrapped_story = textwrap.fill(brand_story, width=76, initial_indent='   ', subsequent_indent='   ')
            print(wrapped_story)
            print()

        # Display additional fields if present
        positioning = parsed.get('positioning_statement', '')
        if positioning:
            print("\n🎪 POSITIONING STATEMENT")
            print("─" * 80)
            wrapped_positioning = textwrap.fill(positioning, width=76, initial_indent='   ', subsequent_indent='   ')
            print(f"\n{wrapped_positioning}\n")

        target_audience = parsed.get('target_audience', '')
        if target_audience:
            print("\n👥 TARGET AUDIENCE")
            print("─" * 80)
            print(f"\n   {target_audience}\n")

        brand_voice = parsed.get('brand_voice', '')
        if brand_voice:
            print("\n🗣️  BRAND VOICE")
            print("─" * 80)
            print(f"\n   {brand_voice}\n")

        print("=" * 80)

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # If parsing fails, fall back to raw output
        print("⚠️  Could not parse story format. Showing raw output:\n")
        print(story_output)
        print()


def display_validation_results(validation_results: Dict[str, Any]):
    """Display detailed validation results in a structured format."""
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80 + "\n")

    validation_data = validation_results.get('validation_data', [])
    collision_data = validation_results.get('collision_data', [])

    # Check if we got raw text output instead of structured data
    if validation_data and len(validation_data) == 1 and 'raw_output' in validation_data[0]:
        raw_output = validation_data[0]['raw_output']

        # Try to parse and format the markdown/text output
        import re

        # Split by name sections (looking for ### headers)
        name_sections = re.split(r'###\s+(.+?)\s+Validation Results', raw_output)

        if len(name_sections) > 1:
            # We have structured markdown output
            for i in range(1, len(name_sections), 2):
                if i + 1 < len(name_sections):
                    name = name_sections[i].strip()
                    content = name_sections[i + 1].strip()

                    print(f"{'='*80}")
                    print(f"BRAND NAME: {name}")
                    print(f"{'='*80}\n")

                    # Parse and display sections
                    lines = content.split('\n')
                    current_section = None

                    for line in lines:
                        line = line.strip()
                        if not line or line == '---':
                            continue

                        # Detect section headers
                        if line.startswith('**Domain Availability:**'):
                            print("📍 DOMAIN AVAILABILITY:")
                            print("─" * 80)
                            current_section = 'domain'
                        elif line.startswith('**Trademark Analysis:**'):
                            print("\n⚖️  TRADEMARK ANALYSIS:")
                            print("─" * 80)
                            current_section = 'trademark'
                        elif line.startswith('**Overall Score:**'):
                            score_match = re.search(r'(\d+)/100', line)
                            if score_match:
                                score = int(score_match.group(1))
                                score_bar = "█" * (score // 10) + "░" * (10 - score // 10)
                                print(f"\n📊 OVERALL SCORE: [{score_bar}] {score}/100")
                        elif line.startswith('**Validation Status:**'):
                            status = line.replace('**Validation Status:**', '').strip()
                            status_icon = "✅" if status == "AVAILABLE" else "⚠️" if status == "CAUTION" else "❌"
                            print(f"   Status: {status_icon} {status}")
                        elif line.startswith('**Recommendation:**'):
                            rec_text = line.replace('**Recommendation:**', '').strip().strip('"')
                            print(f"\n💡 RECOMMENDATION:")
                            print("─" * 80)
                            import textwrap
                            wrapped = textwrap.fill(rec_text, width=76, initial_indent='   ', subsequent_indent='   ')
                            print(wrapped)
                        elif line.startswith('**Action Required:**'):
                            action = line.replace('**Action Required:**', '').strip()
                            print(f"\n⚡ ACTION REQUIRED: {action}")
                        elif line.startswith('*'):
                            # Bullet point
                            clean_line = line.lstrip('*').strip()
                            print(f"   • {clean_line}")

                    print("\n")
        else:
            # Just display the raw output in a nicer format
            print(raw_output)
            print()

        # Still show collision data if available
        if collision_data:
            print("\n" + "=" * 80)
            print("SEARCH COLLISION ANALYSIS")
            print("=" * 80 + "\n")

            for collision_entry in collision_data:
                brand_name = collision_entry.get('brand_name', 'Unknown')
                collision_result = collision_entry.get('collision_result', {})

                print(f"{'='*80}")
                print(f"BRAND: {brand_name}")
                print(f"{'='*80}\n")

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

        print("=" * 80)
        return

    # Display each validated name
    for i, val_data in enumerate(validation_data, 1):
        if 'raw_output' in val_data:
            # Fallback: just display raw output if parsing failed
            print(val_data['raw_output'])
            continue

        brand_name = val_data.get('brand_name', f'Name #{i}')
        status = val_data.get('validation_status', 'UNKNOWN')
        score = val_data.get('overall_score', 0)

        # Create overall score bar
        overall_score_bar = "█" * (score // 10) + "░" * (10 - score // 10)

        # Status icon
        status_icon = "✅" if status == "AVAILABLE" else "⚠️" if status == "CAUTION" else "❌"

        # Header
        print(f"{'='*80}")
        print(f"{status_icon} BRAND NAME: {brand_name}")
        print(f"Status: {status}")
        print(f"Overall Score: [{overall_score_bar}] {score}/100")
        print(f"{'='*80}\n")

        # Domain Availability
        domain_info = val_data.get('domain_availability', {})
        if domain_info:
            print("📍 DOMAIN AVAILABILITY:")
            print("-" * 80)
            best_available = domain_info.get('best_available', 'N/A')
            domain_score = domain_info.get('domain_score', 0)
            domain_score_bar = "█" * (domain_score // 5) + "░" * (10 - domain_score // 5)

            print(f"   Best Available: {best_available}")
            print(f"   Domain Score: [{domain_score_bar}] {domain_score}/50\n")

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
            print("-" * 80)
            risk_level = trademark_info.get('risk_level', 'unknown').upper()
            conflicts_found = trademark_info.get('conflicts_found', 0)
            trademark_score = trademark_info.get('trademark_score', 0)
            trademark_score_bar = "█" * (trademark_score // 5) + "░" * (10 - trademark_score // 5)

            risk_icon = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
            print(f"   Risk Level: {risk_icon} {risk_level}")
            print(f"   Conflicts Found: {conflicts_found}")
            print(f"   Trademark Score: [{trademark_score_bar}] {trademark_score}/50\n")

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
            print("-" * 80)
            print(f"   {recommendation}")
            if action_required:
                print(f"\n   Action Required: {action_required}")
            print()

        print()

    # Display collision detection results
    if collision_data:
        print("\n" + "=" * 80)
        print("SEARCH COLLISION ANALYSIS")
        print("=" * 80 + "\n")

        for collision_entry in collision_data:
            brand_name = collision_entry.get('brand_name', 'Unknown')
            collision_result = collision_entry.get('collision_result', {})

            print(f"{'='*80}")
            print(f"BRAND: {brand_name}")
            print(f"{'='*80}\n")

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

    print("=" * 80)


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

    print("\n" + "-" * 80)
    print("Great! Let me start by researching your industry...")
    print("-" * 80 + "\n")

    # Run research
    try:
        research_output = asyncio.run(run_research(product_info))

        # Display research findings
        display_research(research_output)
        print("\n✓ Research complete")
    except Exception as e:
        print(f"\n⚠️  Research phase encountered an issue: {str(e)}")
        print("    Continuing with name generation using general knowledge...")
        print()

    # Name generation loop
    all_names = []
    iteration = 1

    while True:
        print(f"\n{'='*80}")
        print(f"ROUND {iteration}: NAME GENERATION")
        print("=" * 80)

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

        print("=" * 80)
        print("\n 🤖 What would you like to do next?")
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
        print("\n" + "=" * 80)
        print("VALIDATION")
        print("=" * 80)

        names_to_validate = input("\nEnter names to validate (comma-separated): ").strip()

        if not names_to_validate:
            print("⚠️  No names entered. Please enter at least one name to validate.\n")
            continue

        # Ask if user wants collision detection (it's slow and rate-limited)
        skip_collision = input("\nSkip collision detection? (faster, avoids rate limits) [y/N]: ").strip().lower()

        if skip_collision == 'y':
            print("\nValidating names (checking domains and trademarks only)...")
            print("This may take a minute... ☕️ \n")
        else:
            print("\nValidating names (checking domains, trademarks, and search collisions)...")
            print("This may take a minute... grab a cup of coffee ☕️ \n")

        validation_results = asyncio.run(run_validation(names_to_validate, product_info, skip_collision=(skip_collision == 'y')))
        display_validation_results(validation_results)

        # Post-validation options
        print("=" * 80)
        print("\n 🤖 What would you like to do next?")
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
                print(f"\n{'='*80}")
                print(f"ROUND {iteration}: NAME GENERATION WITH FEEDBACK")
                print("=" * 80)

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
                print("=" * 80)
                print("\n 🤖 What would you like to do next?")
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
    print("\n" + "=" * 80)
    print("BRAND STORY")
    print("=" * 80)

    final_name = input("\nWhat's your final brand name choice? ").strip()

    if final_name:
        print(f"\nGenerating complete brand story for '{final_name}'...")
        print("This may take a minute... stand up and stretch a little 🚶‍♂️ \n")

        story_output = asyncio.run(run_story(final_name, product_info))

        # Display the story in formatted way
        display_story(story_output, final_name)

    print("\n" + "=" * 80)
    print("✓ BRAND IDENTITY COMPLETE!")
    print("=" * 80)
    print(f"\nYour brand: {final_name}")
    print("\nThank you for using AI Brand Studio!")
    print()


if __name__ == '__main__':
    main()
