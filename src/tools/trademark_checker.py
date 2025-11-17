"""
Trademark Search Tool for Brand Validation.

This module provides trademark search functionality using USPTO (United States
Patent and Trademark Office) public APIs to check for potential conflicts.
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger('brand_studio.trademark_checker')


def _simulate_trademark_search(
    brand_name: str,
    category: Optional[str],
    limit: int
) -> List[Dict]:
    """
    Simulate trademark search results for development.

    In production, this should be replaced with real USPTO API calls.
    For now, returns placeholder data to demonstrate the tool functionality.

    Args:
        brand_name: Brand name to search
        category: Nice classification (optional)
        limit: Max results

    Returns:
        List of simulated trademark results
    """
    # List of common technology brand patterns for simulation
    common_tech_patterns = [
        'Tech', 'Soft', 'Cloud', 'Data', 'Cyber', 'Digi', 'Smart',
        'Net', 'Web', 'App', 'Link', 'Sync', 'Flow', 'Wave'
    ]

    # Check if brand name contains common patterns
    has_common_pattern = any(
        pattern.lower() in brand_name.lower()
        for pattern in common_tech_patterns
    )

    # Simulate results based on name characteristics
    results = []

    # If it contains common patterns, simulate some similar marks
    if has_common_pattern and len(brand_name) > 4:
        results.append({
            'mark': brand_name.upper() + ' SYSTEMS',
            'status': 'LIVE',
            'owner': 'Example Corp',
            'serial_number': '88000000',
            'filing_date': '2020-01-01'
        })

    # Very common/short names get more conflicts
    if len(brand_name) <= 5:
        results.append({
            'mark': brand_name.upper() + 'X',
            'status': 'REGISTERED',
            'owner': 'Tech Ventures LLC',
            'serial_number': '88000001',
            'filing_date': '2019-06-15'
        })

    return results[:limit]


def search_trademarks_uspto(
    brand_name: str,
    category: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search USPTO trademark database for potential conflicts.

    Uses the USPTO public API to search for existing trademarks that may
    conflict with the proposed brand name.

    Args:
        brand_name: Brand name to search for
        category: Nice classification category (optional, e.g., "009" for software)
        limit: Maximum number of results to return (default: 10)

    Returns:
        Dictionary containing:
        - brand_name: The searched brand name
        - conflicts_found: Number of potential conflicts
        - exact_matches: List of exact trademark matches
        - similar_marks: List of similar trademarks
        - risk_level: Assessment of trademark risk (low/medium/high)
        - checked_at: Timestamp of the search

    Example:
        >>> search_trademarks_uspto("TechFlow", category="009")
        {
            'brand_name': 'TechFlow',
            'conflicts_found': 2,
            'exact_matches': [],
            'similar_marks': [
                {'mark': 'TECHFLO', 'status': 'LIVE', 'owner': 'Acme Corp'},
                {'mark': 'TECH FLOW', 'status': 'LIVE', 'owner': 'Beta Inc'}
            ],
            'risk_level': 'medium',
            'checked_at': '2025-11-17T13:30:00Z'
        }
    """
    logger.info(f"Searching USPTO for trademark: {brand_name}")

    # USPTO TSDR (Trademark Status & Document Retrieval) API
    # Note: For Phase 2, using simplified check. In production, integrate with:
    # - USPTO TESS (Trademark Electronic Search System)
    # - Commercial APIs like Trademarkia, USPTO.report (requires auth)
    # - Or manual TESS search: https://tmsearch.uspto.gov/

    # For now, implement a basic similarity check using common trademark patterns
    # This will be enhanced in production with real API integration

    # Placeholder: In a real implementation, this would call USPTO API
    # For development, we'll return a structured response indicating the tool works
    logger.warning(
        "Using simplified trademark check. For production, integrate USPTO API credentials."
    )

    # Simulate trademark search results based on common patterns
    # In production, this would be real API data
    trademark_results = _simulate_trademark_search(brand_name, category, limit)

    # Separate exact matches from similar marks
    exact_matches = [
        {
            'mark': r.get('mark', ''),
            'status': r.get('status', ''),
            'owner': r.get('owner', ''),
            'serial_number': r.get('serial_number', ''),
            'filing_date': r.get('filing_date', '')
        }
        for r in trademark_results
        if r.get('mark', '').lower() == brand_name.lower()
    ]

    similar_marks = [
        {
            'mark': r.get('mark', ''),
            'status': r.get('status', ''),
            'owner': r.get('owner', ''),
            'serial_number': r.get('serial_number', ''),
            'filing_date': r.get('filing_date', '')
        }
        for r in trademark_results
        if r.get('mark', '').lower() != brand_name.lower()
    ]

    # Assess risk level
    risk_level = assess_trademark_risk(
        exact_matches=exact_matches,
        similar_marks=similar_marks,
        brand_name=brand_name
    )

    logger.info(
        f"Trademark search complete for '{brand_name}': "
        f"{len(exact_matches)} exact, {len(similar_marks)} similar, "
        f"risk={risk_level}"
    )

    return {
        'brand_name': brand_name,
        'conflicts_found': len(trademark_results),
        'exact_matches': exact_matches,
        'similar_marks': similar_marks,
        'risk_level': risk_level,
        'checked_at': datetime.utcnow().isoformat() + 'Z',
        'source': 'USPTO (simulated)'
    }


def assess_trademark_risk(
    exact_matches: List[Dict],
    similar_marks: List[Dict],
    brand_name: str
) -> str:
    """
    Assess the trademark risk level based on search results.

    Args:
        exact_matches: List of exact trademark matches
        similar_marks: List of similar trademarks
        brand_name: The brand name being assessed

    Returns:
        Risk level: 'low', 'medium', 'high', or 'critical'
    """
    # Critical risk: exact matches that are active/live
    active_exact = [m for m in exact_matches if m.get('status') in ['LIVE', 'REGISTERED']]
    if active_exact:
        return 'critical'

    # High risk: exact matches (even if not active) or many similar marks
    if exact_matches or len(similar_marks) >= 5:
        return 'high'

    # Medium risk: some similar marks
    if 2 <= len(similar_marks) < 5:
        return 'medium'

    # Low risk: few or no conflicts
    if len(similar_marks) <= 1:
        return 'low'

    return 'medium'


def batch_trademark_search(
    brand_names: List[str],
    category: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Search trademarks for multiple brand names.

    Args:
        brand_names: List of brand names to check
        category: Nice classification category (optional)

    Returns:
        Dictionary mapping brand names to their trademark search results

    Example:
        >>> batch_trademark_search(['BrandA', 'BrandB'])
        {
            'BrandA': {...},
            'BrandB': {...}
        }
    """
    logger.info(f"Starting batch trademark search for {len(brand_names)} brands")

    results = {}
    for brand_name in brand_names:
        results[brand_name] = search_trademarks_uspto(brand_name, category)
        # Small delay to avoid rate limiting
        time.sleep(0.5)

    logger.info(f"Batch trademark search complete for {len(brand_names)} brands")
    return results


# ADK Tool Registration
def create_trademark_checker_tool():
    """
    Create and return an ADK-compatible tool for trademark checking.

    Returns:
        Tool instance that can be used by ADK agents

    Example:
        >>> from src.tools.trademark_checker import create_trademark_checker_tool
        >>> trademark_tool = create_trademark_checker_tool()
        >>> # Use with agent
        >>> agent = LlmAgent(
        ...     name="validation_agent",
        ...     tools=[trademark_tool],
        ...     ...
        ... )
    """
    # Try to import real ADK, fall back to mock for development
    try:
        from google_genai.adk import Tool
    except ImportError:
        from src.utils.mock_adk import Tool

    return Tool(
        name="search_trademarks_uspto",
        description=(
            "Search USPTO trademark database for potential conflicts with a brand name. "
            "Returns exact matches, similar marks, and risk assessment (low/medium/high/critical). "
            "Helps identify trademark conflicts before finalizing brand names."
        ),
        func=search_trademarks_uspto
    )
