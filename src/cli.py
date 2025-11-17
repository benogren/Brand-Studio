#!/usr/bin/env python3
"""
Interactive CLI for AI Brand Studio.

This module provides a command-line interface for generating brand names
using the multi-agent orchestrator system.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from src.agents.orchestrator import BrandStudioOrchestrator
from src.agents.name_generator import NameGeneratorAgent


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='AI Brand Studio - Generate legally-clear, SEO-optimized brand names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m src.cli

  # Direct input
  python -m src.cli --product "AI meal planning app" --audience "Busy parents" --personality warm

  # Verbose mode with JSON output
  python -m src.cli --product "Fintech app" --verbose --json output.json

  # Custom number of names
  python -m src.cli --product "Healthcare app" --count 40
        """
    )

    # Product information
    parser.add_argument(
        '--product',
        '-p',
        type=str,
        help='Product description (what does your product do?)'
    )

    parser.add_argument(
        '--audience',
        '-a',
        type=str,
        default='',
        help='Target audience (who is this product for?)'
    )

    parser.add_argument(
        '--personality',
        '-P',
        type=str,
        choices=['playful', 'professional', 'innovative', 'luxury'],
        default='professional',
        help='Brand personality (default: professional)'
    )

    parser.add_argument(
        '--industry',
        '-i',
        type=str,
        default='general',
        help='Industry/category (e.g., healthcare, fintech, food_tech)'
    )

    # Generation options
    parser.add_argument(
        '--count',
        '-c',
        type=int,
        default=30,
        help='Number of brand names to generate (20-50, default: 30)'
    )

    # Output options
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output (show agent traces and debugging info)'
    )

    parser.add_argument(
        '--json',
        '-j',
        type=str,
        metavar='FILE',
        help='Save full results to JSON file'
    )

    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Minimal output (only brand names)'
    )

    # Configuration
    parser.add_argument(
        '--project-id',
        type=str,
        help='Google Cloud project ID (overrides .env)'
    )

    parser.add_argument(
        '--location',
        type=str,
        default='us-central1',
        help='Google Cloud location (default: us-central1)'
    )

    return parser


def load_config(args: argparse.Namespace) -> Dict[str, str]:
    """
    Load configuration from environment and command-line arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Dictionary with configuration values

    Raises:
        ValueError: If required configuration is missing
    """
    # Load .env file
    load_dotenv()

    # Get project ID from args or environment
    project_id = args.project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
    location = args.location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        raise ValueError(
            "Google Cloud project ID is required. "
            "Set GOOGLE_CLOUD_PROJECT in .env or use --project-id flag."
        )

    return {
        'project_id': project_id,
        'location': location
    }


def get_user_brief_interactive() -> Dict[str, Any]:
    """
    Collect user brief through interactive prompts.

    Returns:
        Dictionary with user brief information
    """
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO - INTERACTIVE MODE")
    print("=" * 70 + "\n")

    # Product description (required)
    while True:
        product = input("Product description (what does it do?): ").strip()
        if product:
            break
        print("  Error: Product description is required.\n")

    # Target audience (optional)
    audience = input("Target audience (who is it for?) [optional]: ").strip()

    # Brand personality
    print("\nBrand personality options:")
    print("  1. Playful (fun, whimsical, lighthearted)")
    print("  2. Professional (authoritative, trustworthy)")
    print("  3. Innovative (forward-thinking, tech-savvy)")
    print("  4. Luxury (elegant, sophisticated, premium)")

    while True:
        choice = input("Select personality (1-4) [default: 2]: ").strip()
        if not choice:
            personality = 'professional'
            break
        elif choice in ['1', '2', '3', '4']:
            personalities = ['playful', 'professional', 'innovative', 'luxury']
            personality = personalities[int(choice) - 1]
            break
        else:
            print("  Error: Please enter 1, 2, 3, or 4.\n")

    # Industry (optional)
    industry = input("Industry/category [default: general]: ").strip() or 'general'

    # Number of names
    while True:
        count_input = input("Number of brand names to generate (20-50) [default: 30]: ").strip()
        if not count_input:
            count = 30
            break
        try:
            count = int(count_input)
            if 20 <= count <= 50:
                break
            else:
                print("  Error: Please enter a number between 20 and 50.\n")
        except ValueError:
            print("  Error: Please enter a valid number.\n")

    return {
        'product_description': product,
        'target_audience': audience,
        'brand_personality': personality,
        'industry': industry,
        'count': count
    }


def print_header(verbose: bool = False):
    """
    Print CLI header.

    Args:
        verbose: Whether verbose mode is enabled
    """
    print("\n" + "=" * 70)
    print("AI BRAND STUDIO")
    print("Multi-agent system for brand name generation")
    if verbose:
        print("VERBOSE MODE ENABLED")
    print("=" * 70 + "\n")


def print_user_brief(brief: Dict[str, Any], verbose: bool = False):
    """
    Print the user brief summary.

    Args:
        brief: User brief dictionary
        verbose: Whether to show verbose output
    """
    print("USER BRIEF")
    print("-" * 70)
    print(f"Product: {brief['product_description']}")
    if brief.get('target_audience'):
        print(f"Audience: {brief['target_audience']}")
    print(f"Personality: {brief['brand_personality']}")
    print(f"Industry: {brief['industry']}")
    if verbose:
        print(f"Requested Names: {brief.get('count', 30)}")
    print()


def print_brand_names(names: list, quiet: bool = False, verbose: bool = False):
    """
    Print generated brand names in formatted output.

    Args:
        names: List of brand name dictionaries
        quiet: Minimal output mode
        verbose: Show detailed information
    """
    if not names:
        print("No brand names generated.")
        return

    print(f"\nGENERATED BRAND NAMES ({len(names)} total)")
    print("=" * 70 + "\n")

    if quiet:
        # Minimal output - just the names
        for name in names:
            print(name['brand_name'])
    else:
        # Full formatted output
        for i, name in enumerate(names, 1):
            print(f"{i}. {name['brand_name']}")

            if verbose:
                print(f"   Strategy: {name['naming_strategy']}")
                print(f"   Syllables: {name['syllables']}")
                print(f"   Memorable Score: {name['memorable_score']}/10")

            print(f"   Rationale: {name['rationale']}")
            print(f"   Tagline: \"{name['tagline']}\"")
            print()


def print_workflow_summary(result: Dict[str, Any], verbose: bool = False):
    """
    Print workflow execution summary.

    Args:
        result: Workflow result dictionary
        verbose: Show detailed information
    """
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)

    status = result.get('status', 'unknown')
    print(f"\nStatus: {status.upper()}")

    if verbose:
        # Show detailed workflow information
        stages = result.get('workflow_stages', [])
        if stages:
            print(f"Stages Executed: {', '.join(stages)}")

        iterations = result.get('iteration', 0)
        if iterations:
            print(f"Iterations: {iterations}")

        # Timing information
        start_time = result.get('start_time')
        end_time = result.get('end_time')
        if start_time and end_time:
            from datetime import datetime
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = (end - start).total_seconds()
            print(f"Duration: {duration:.2f} seconds")

    # Summary from workflow
    summary = result.get('workflow_summary', '')
    if summary:
        print(f"\n{summary}")

    print()


def save_json_output(data: Dict[str, Any], filepath: str, verbose: bool = False):
    """
    Save results to JSON file.

    Args:
        data: Data to save
        filepath: Output file path
        verbose: Show verbose output
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        if verbose:
            print(f"Results saved to: {filepath}")
    except Exception as e:
        print(f"Error saving JSON output: {e}", file=sys.stderr)


def run_name_generator_only(
    config: Dict[str, str],
    brief: Dict[str, Any],
    verbose: bool = False
) -> list:
    """
    Run name generator agent directly (without orchestrator).

    Args:
        config: Configuration dictionary
        brief: User brief
        verbose: Verbose output

    Returns:
        List of generated brand names
    """
    if verbose:
        print("Initializing Name Generator Agent...")

    generator = NameGeneratorAgent(
        project_id=config['project_id'],
        location=config['location']
    )

    if verbose:
        print(f"Generating {brief.get('count', 30)} brand names...\n")

    names = generator.generate_names(
        product_description=brief['product_description'],
        target_audience=brief.get('target_audience', ''),
        brand_personality=brief['brand_personality'],
        industry=brief['industry'],
        num_names=brief.get('count', 30)
    )

    return names


def run_orchestrator_workflow(
    config: Dict[str, str],
    brief: Dict[str, Any],
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run full orchestrator workflow.

    Args:
        config: Configuration dictionary
        brief: User brief
        verbose: Verbose output

    Returns:
        Workflow result dictionary
    """
    if verbose:
        print("Initializing Orchestrator Agent...")

    orchestrator = BrandStudioOrchestrator(
        project_id=config['project_id'],
        location=config['location'],
        enable_cloud_logging=verbose
    )

    if verbose:
        print("Executing brand creation workflow...\n")

    result = orchestrator.coordinate_workflow(brief)

    return result


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args)

        # Print header
        if not args.quiet:
            print_header(verbose=args.verbose)

        # Get user brief
        if args.product:
            # Use command-line arguments
            brief = {
                'product_description': args.product,
                'target_audience': args.audience,
                'brand_personality': args.personality,
                'industry': args.industry,
                'count': args.count
            }
        else:
            # Interactive mode
            brief = get_user_brief_interactive()

        # Print user brief
        if not args.quiet:
            print_user_brief(brief, verbose=args.verbose)

        # Generate brand names
        # For Phase 1, use name generator directly
        # In Phase 2, switch to orchestrator workflow
        if args.verbose:
            print("=" * 70)
            print("EXECUTION")
            print("=" * 70 + "\n")

        names = run_name_generator_only(config, brief, verbose=args.verbose)

        # Print results
        print_brand_names(names, quiet=args.quiet, verbose=args.verbose)

        # Create result structure for JSON output
        result = {
            'user_brief': brief,
            'brand_names': names,
            'generated_at': datetime.utcnow().isoformat(),
            'status': 'completed'
        }

        # Save JSON output if requested
        if args.json:
            save_json_output(result, args.json, verbose=args.verbose)

        # Print success message
        if not args.quiet:
            print("=" * 70)
            print(f"✓ Successfully generated {len(names)} brand names")
            print("=" * 70 + "\n")

        sys.exit(0)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease check your .env file or use --project-id flag.", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
