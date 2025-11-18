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


def print_brand_names_simple(names: list):
    """
    Print brand names in simple list format for selection.

    Args:
        names: List of brand name dictionaries
    """
    if not names:
        print("No brand names generated.")
        return

    print(f"\nGENERATED BRAND NAMES ({len(names)} total)")
    print("=" * 70 + "\n")

    for i, name in enumerate(names, 1):
        print(f"{i:2d}. {name['brand_name']:20s} - {name['rationale'][:50]}...")


def get_user_selection(names: list, min_select: int = 5, max_select: int = 10) -> list:
    """
    Let user select their favorite brand names.

    Args:
        names: List of brand name dictionaries
        min_select: Minimum number of names to select
        max_select: Maximum number of names to select

    Returns:
        List of selected brand name dictionaries
    """
    print(f"\n{'=' * 70}")
    print(f"SELECT YOUR FAVORITE NAMES ({min_select}-{max_select} names)")
    print("=" * 70 + "\n")
    print(f"Enter the numbers of your favorite names (comma-separated)")
    print(f"Example: 1,5,7,12,18")
    print(f"Or type 'all' to select all names")
    print(f"Or type 'regenerate' to start over with new names\n")

    while True:
        selection_input = input(f"Your selection ({min_select}-{max_select} names): ").strip()

        if selection_input.lower() == 'regenerate':
            return 'regenerate'

        if selection_input.lower() == 'all':
            return names

        try:
            # Parse comma-separated numbers
            selected_indices = [int(x.strip()) for x in selection_input.split(',')]

            # Validate selection count
            if len(selected_indices) < min_select:
                print(f"  Error: Please select at least {min_select} names.\n")
                continue
            if len(selected_indices) > max_select:
                print(f"  Error: Please select at most {max_select} names.\n")
                continue

            # Validate indices are within range
            if any(idx < 1 or idx > len(names) for idx in selected_indices):
                print(f"  Error: Numbers must be between 1 and {len(names)}.\n")
                continue

            # Get selected names
            selected_names = [names[idx - 1] for idx in selected_indices]

            # Confirm selection
            print(f"\nYou selected {len(selected_names)} names:")
            for name in selected_names:
                print(f"  - {name['brand_name']}")

            confirm = input("\nConfirm selection? (y/n): ").strip().lower()
            if confirm == 'y':
                return selected_names
            else:
                print("\nLet's try again...\n")
                continue

        except ValueError:
            print("  Error: Please enter comma-separated numbers (e.g., 1,5,7,12).\n")
            continue


def run_phase3_validation(
    config: Dict[str, str],
    selected_names: List[Dict],
    brief: Dict[str, Any],
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run Phase 3 validation on selected names: domain, trademark, SEO, and enhanced taglines.

    Args:
        config: Configuration dictionary
        selected_names: List of selected brand name dictionaries
        brief: User brief
        verbose: Verbose output

    Returns:
        Dictionary with validation results
    """
    from src.tools.domain_checker import check_domain_availability
    from src.tools.trademark_checker import search_trademarks_uspto
    from src.agents.seo_agent import SEOAgent

    print("\n" + "=" * 70)
    print("PHASE 3: VALIDATING SELECTED NAMES")
    print("=" * 70 + "\n")

    results = {}

    # Initialize SEO agent
    seo_agent = SEOAgent(
        project_id=config['project_id'],
        location=config['location']
    )

    for i, name_dict in enumerate(selected_names, 1):
        brand_name = name_dict['brand_name']
        print(f"\n[{i}/{len(selected_names)}] Validating: {brand_name}")
        print("-" * 70)

        # Domain availability check
        print("  Checking domain availability...")
        domain_results = check_domain_availability(brand_name)

        # Trademark risk assessment
        print("  Checking trademark conflicts...")
        trademark_results = search_trademarks_uspto(brand_name)

        # SEO optimization
        print("  Optimizing for SEO...")
        seo_results = seo_agent.optimize_brand_seo(
            brand_name=brand_name,
            product_description=brief['product_description'],
            industry=brief['industry']
        )

        # Store results
        results[brand_name] = {
            'original_data': name_dict,
            'domain_availability': domain_results,
            'trademark_risk': trademark_results,
            'seo_optimization': seo_results
        }

        # Print summary
        available_domains = [ext for ext, avail in domain_results.items() if avail]
        print(f"  ✓ Domains available: {', '.join(available_domains) if available_domains else 'None'}")
        print(f"  ✓ Trademark risk: {trademark_results['risk_level']}")
        print(f"  ✓ SEO score: {seo_results['seo_score']}/100")

    return results


def print_validation_results(validation_results: Dict[str, Any]):
    """
    Print Phase 3 validation results in a formatted way.

    Args:
        validation_results: Dictionary with validation results
    """
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70 + "\n")

    for brand_name, results in validation_results.items():
        print(f"\n{brand_name}")
        print("-" * 70)

        # Domain availability
        domain_avail = results['domain_availability']
        print(f"Domain Availability:")

        # Group by extension for better display
        available_domains = []
        taken_domains = []

        for domain, available in sorted(domain_avail.items()):
            if available:
                available_domains.append(domain)
            else:
                taken_domains.append(domain)

        # Show available domains first (more important)
        if available_domains:
            print(f"  ✓ Available ({len(available_domains)}):")
            for domain in available_domains[:5]:  # Show first 5
                print(f"    • {domain}")
            if len(available_domains) > 5:
                print(f"    ... and {len(available_domains) - 5} more")

        # Show taken domains
        if taken_domains:
            print(f"  ✗ Taken ({len(taken_domains)}):")
            for domain in taken_domains[:3]:  # Show first 3
                print(f"    • {domain}")
            if len(taken_domains) > 3:
                print(f"    ... and {len(taken_domains) - 3} more")

        # Check if we should suggest alternatives
        base_domains = [d for d in domain_avail.keys() if not any(
            d.startswith(p) for p in ['get', 'try', 'your', 'my', 'hello', 'use']
        )]
        base_available = [d for d in base_domains if domain_avail[d]]

        if not base_available:
            # Suggest alternatives
            prefix_domains = [d for d in available_domains if any(
                d.startswith(p) for p in ['get', 'try', 'your', 'my', 'hello', 'use']
            )]
            if prefix_domains:
                print(f"\n  💡 Try these variations:")
                for domain in prefix_domains[:3]:
                    print(f"    • {domain}")

        # Trademark risk
        tm_risk = results['trademark_risk']
        risk_level = tm_risk['risk_level'].upper()
        risk_color = {
            'LOW': '✓',
            'MEDIUM': '⚠',
            'HIGH': '✗',
            'CRITICAL': '✗✗'
        }.get(risk_level, '?')
        print(f"\nTrademark Risk: {risk_color} {risk_level}")
        if tm_risk['conflicts_found'] > 0:
            print(f"  Conflicts found: {tm_risk['conflicts_found']}")

        # SEO optimization
        seo_opt = results['seo_optimization']
        print(f"\nSEO Score: {seo_opt['seo_score']}/100")
        print(f"Meta Title: {seo_opt['meta_title']}")
        print(f"Meta Description: {seo_opt['meta_description']}")
        print(f"Primary Keywords: {', '.join(seo_opt['primary_keywords'])}")

        # Enhanced taglines (from original + SEO)
        print(f"\nTagline: \"{results['original_data']['tagline']}\"")

        print()

    print("=" * 70)


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
    verbose: bool = False,
    enable_interactive_feedback: bool = True
) -> Dict[str, Any]:
    """
    Run full orchestrator workflow with interactive feedback.

    Args:
        config: Configuration dictionary
        brief: User brief
        verbose: Verbose output
        enable_interactive_feedback: Enable interactive feedback loop

    Returns:
        Workflow result dictionary
    """
    if verbose:
        print("Initializing Name Generator Agent...")

    # Initialize name generator agent
    name_generator = NameGeneratorAgent(
        project_id=config['project_id'],
        location=config['location']
    )

    if verbose:
        print("Initializing Orchestrator Agent...")

    # Initialize orchestrator with name generator
    orchestrator = BrandStudioOrchestrator(
        project_id=config['project_id'],
        location=config['location'],
        enable_cloud_logging=verbose,
        name_generator_agent=name_generator,
        enable_interactive_feedback=enable_interactive_feedback
    )

    if verbose:
        print("Executing brand creation workflow with interactive feedback...\n")

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
                'count': 20  # Start with 20 names for selection
            }
        else:
            # Interactive mode
            brief = get_user_brief_interactive()
            # Override count to 20 for initial generation
            brief['count'] = 20

        # Print user brief
        if not args.quiet:
            print_user_brief(brief, verbose=args.verbose)

        # Run orchestrator workflow with interactive feedback
        # The orchestrator will:
        # 1. Generate names with the name generator agent
        # 2. Collect user feedback interactively
        # 3. Refine names based on feedback (up to 3 iterations)
        # 4. Once approved, proceed to validation
        # 5. Run SEO optimization and story generation

        if args.verbose:
            print("\n" + "=" * 70)
            print("STARTING INTERACTIVE WORKFLOW")
            print("=" * 70)
            print("\nThe system will generate brand names and collect your feedback.")
            print("You can refine the names up to 3 times before proceeding to validation.\n")

        result = run_orchestrator_workflow(
            config=config,
            brief=brief,
            verbose=args.verbose,
            enable_interactive_feedback=True
        )

        # Check workflow status
        if result['status'] == 'completed':
            if not args.quiet:
                print("\n✓ Workflow completed successfully!")

                # Show feedback session info if available
                if 'feedback_session' in result:
                    session = result['feedback_session']
                    print(f"\n📊 Feedback Summary:")
                    print(f"  • Iterations: {session['iterations']}")
                    print(f"  • Feedback rounds: {session['feedback_count']}")
                    print(f"  • Approved names: {len(session['approved_names'])}")

                # Show detailed names with full metadata, validation, and SEO
                if result.get('brand_names_full'):
                    print(f"\n{'=' * 70}")
                    print(f"APPROVED BRAND NAMES ({len(result['brand_names_full'])} total)")
                    print("=" * 70 + "\n")

                    validation_results = result.get('validation_results', {})
                    seo_data = result.get('seo_data', {})
                    domain_avail = validation_results.get('domain_availability', {})
                    trademark = validation_results.get('trademark_results', {})
                    seo_scores = seo_data.get('seo_scores', {})

                    for i, name_data in enumerate(result['brand_names_full'], 1):
                        brand_name = name_data.get('brand_name', 'Unknown')
                        print(f"{i}. {brand_name}")
                        print(f"   Strategy: {name_data.get('naming_strategy', 'N/A')}")
                        print(f"   Rationale: {name_data.get('rationale', 'N/A')}")
                        print(f"   Tagline: \"{name_data.get('tagline', 'N/A')}\"")
                        print(f"   Syllables: {name_data.get('syllables', 'N/A')} | Memorable: {name_data.get('memorable_score', 'N/A')}/10")

                        # Domain availability
                        if brand_name in domain_avail:
                            domains = domain_avail[brand_name]
                            available = [ext for ext, avail in domains.items() if avail]
                            if available:
                                print(f"   Domains Available: {', '.join(available)}")
                            else:
                                print(f"   Domains Available: None")

                        # Trademark risk
                        if brand_name in trademark:
                            risk = trademark[brand_name]
                            risk_icon = "✓" if risk == "low" else ("⚠" if risk == "medium" else "✗")
                            print(f"   Trademark Risk: {risk_icon} {risk.upper()}")

                        # SEO score
                        if brand_name in seo_scores:
                            print(f"   SEO Score: {seo_scores[brand_name]}/100")

                        print()
                elif result.get('brand_names'):
                    print(f"\n✓ {len(result['brand_names'])} names approved and validated")
                    print(f"  Names: {', '.join(result['brand_names'][:5])}")
                    if len(result['brand_names']) > 5:
                        print(f"  ... and {len(result['brand_names']) - 5} more")

                # Show brand narratives if generated
                if result.get('brand_narratives'):
                    print(f"\n{'=' * 70}")
                    print(f"BRAND NARRATIVES ({len(result['brand_narratives'])} generated)")
                    print("=" * 70)

                    for i, narrative in enumerate(result['brand_narratives'], 1):
                        brand_name = narrative.get('brand_name', 'Unknown')
                        print(f"\n{i}. {brand_name}")
                        print("=" * 70)

                        # Tagline options
                        taglines = narrative.get('narrative_taglines', [])
                        if taglines:
                            print(f"\n   TAGLINE OPTIONS ({len(taglines)}):")
                            for j, tagline in enumerate(taglines, 1):
                                print(f"   {j}. \"{tagline}\"")

                        # Brand story
                        brand_story = narrative.get('brand_story', '')
                        if brand_story:
                            print(f"\n   BRAND STORY:")
                            # Wrap text at 70 characters
                            import textwrap
                            wrapped_story = textwrap.fill(
                                brand_story,
                                width=66,
                                initial_indent='   ',
                                subsequent_indent='   '
                            )
                            print(wrapped_story)

                        # Value proposition
                        value_prop = narrative.get('value_proposition', '')
                        if value_prop:
                            print(f"\n   VALUE PROPOSITION:")
                            print(f"   \"{value_prop}\"")

                        # Domain and trademark info
                        domain_status = narrative.get('domain_status', {})
                        if domain_status:
                            available = [ext for ext, avail in domain_status.items() if avail]
                            if available:
                                print(f"\n   Available Domains: {', '.join(available)}")

                        trademark_risk = narrative.get('trademark_risk')
                        if trademark_risk:
                            risk_icon = "✓" if trademark_risk == "low" else ("⚠" if trademark_risk == "medium" else "✗")
                            print(f"   Trademark Risk: {risk_icon} {trademark_risk.upper()}")

                        print()

                # Show workflow summary
                if result.get('workflow_summary'):
                    print(f"{result['workflow_summary']}")
                    print()

        elif result['status'] == 'validation_failed':
            print("\n⚠️  Validation failed after maximum attempts.")
            print("   The generated names did not meet trademark/domain requirements.")
            if not args.quiet:
                print(f"\n   Error: {result.get('error', 'Unknown error')}")

        else:
            print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
            if args.verbose:
                print(f"   Failed at stage: {result.get('failed_stage', 'unknown')}")

        # Save JSON output if requested
        if args.json:
            save_json_output(result, args.json, verbose=args.verbose)

        # Print success message
        if not args.quiet and result['status'] == 'completed':
            print("\n" + "=" * 70)
            print(f"✓ Brand naming workflow completed successfully!")
            print("=" * 70 + "\n")

        # Exit with appropriate status code
        if result['status'] == 'completed':
            sys.exit(0)
        else:
            sys.exit(1)

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
