"""
Domain Availability Checker Tool.

This module provides domain availability checking functionality using
the python-whois library to check multiple domain extensions including
.com, .ai, .io, .so, .app, .co, .is, .me, .net, and .to.

Also supports prefix variations like get[name].com, try[name].com, etc.
"""

import logging
import time
import sys
import os
from typing import Dict, Optional, List, Set
from datetime import datetime, timedelta
import whois

# Configure logger
logger = logging.getLogger('brand_studio.domain_checker')

# Default domain extensions to check
DEFAULT_EXTENSIONS = ['.com', '.ai', '.io', '.so', '.app', '.co', '.is', '.me', '.net', '.to']

# Domain name prefixes for variations
DOMAIN_PREFIXES = ['get', 'try', 'your', 'my', 'hello', 'use']


class DomainCache:
    """
    Simple in-memory cache for domain availability results.

    Caches results for 5 minutes to reduce WHOIS API calls and improve performance.
    """

    def __init__(self, ttl_minutes: int = 5):
        """
        Initialize the cache.

        Args:
            ttl_minutes: Time-to-live for cache entries in minutes (default: 5)
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        logger.info(f"Initialized DomainCache with {ttl_minutes} minute TTL")

    def get(self, domain: str) -> Optional[Dict]:
        """
        Get cached result for a domain.

        Args:
            domain: Domain name to look up

        Returns:
            Cached result dictionary or None if not cached or expired
        """
        if domain not in self.cache:
            return None

        cached_entry = self.cache[domain]
        cached_time = cached_entry['cached_at']

        # Check if cache entry has expired
        if datetime.utcnow() - cached_time > self.ttl:
            logger.debug(f"Cache expired for {domain}")
            del self.cache[domain]
            return None

        logger.debug(f"Cache hit for {domain}")
        return cached_entry['result']

    def set(self, domain: str, result: Dict) -> None:
        """
        Store result in cache.

        Args:
            domain: Domain name
            result: Availability result to cache
        """
        self.cache[domain] = {
            'result': result,
            'cached_at': datetime.utcnow()
        }
        logger.debug(f"Cached result for {domain}")


# Global cache instance
_domain_cache = DomainCache(ttl_minutes=5)


def check_domain_availability(
    brand_name: str,
    extensions: Optional[List[str]] = None,
    include_prefixes: bool = False
) -> Dict[str, bool]:
    """
    Check domain availability for a brand name across multiple extensions.

    Uses python-whois library to query WHOIS databases for multiple TLDs including
    .com, .ai, .io, .so, .app, .co, .is, .me, .net, and .to. Can also check prefix
    variations like get[name].com, try[name].com, etc.

    Args:
        brand_name: Brand name to check (will be converted to domain format)
        extensions: List of domain extensions to check (default: all 10 TLDs)
        include_prefixes: If True, also check prefix variations (get-, try-, etc.)

    Returns:
        Dictionary mapping domain names to availability status:
        {
            'brandname.com': True,   # Available
            'brandname.ai': False,   # Taken
            'getbrandname.com': True # Available (if include_prefixes=True)
        }

    Examples:
        >>> check_domain_availability('MyBrand')
        {'mybrand.com': True, 'mybrand.ai': False, 'mybrand.io': True, ...}

        >>> check_domain_availability('TestBrand', extensions=['.com'], include_prefixes=True)
        {'testbrand.com': False, 'gettestbrand.com': True, 'trytestbrand.com': True, ...}
    """
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS

    # Convert brand name to domain format (lowercase, remove spaces/special chars)
    domain_base = brand_name.lower().replace(' ', '').replace('-', '')

    # Build list of domain names to check
    domain_names = []

    # Add base brand name with all extensions
    for ext in extensions:
        domain_names.append(f"{domain_base}{ext}")

    # Add prefix variations if requested
    if include_prefixes:
        for prefix in DOMAIN_PREFIXES:
            for ext in extensions:
                domain_names.append(f"{prefix}{domain_base}{ext}")

    results = {}

    logger.info(
        f"Checking domain availability for '{brand_name}' "
        f"across {len(extensions)} extensions "
        f"({'with' if include_prefixes else 'without'} prefix variations)"
    )

    for domain in domain_names:
        # Check cache first
        cached_result = _domain_cache.get(domain)
        if cached_result is not None:
            results[domain] = cached_result[domain]
            continue

        # Perform WHOIS lookup
        is_available = _check_single_domain(domain)
        results[domain] = is_available

        # Cache the result for this single domain
        _domain_cache.set(domain, {domain: is_available})

        # Small delay to avoid rate limiting
        if len(domain_names) > 10:
            time.sleep(0.05)  # 50ms delay for large batches

    available_count = sum(results.values())
    logger.info(
        f"Domain check complete for '{brand_name}': "
        f"{available_count} of {len(results)} available"
    )

    return results


def _check_single_domain(domain: str) -> bool:
    """
    Check availability of a single domain using WHOIS.

    Args:
        domain: Full domain name (e.g., 'example.com')

    Returns:
        True if domain is available, False if taken

    Note:
        On WHOIS lookup failure or exception, assumes domain is available
        (defensive approach to avoid false negatives that could eliminate
        valid name candidates).
    """
    try:
        logger.debug(f"Performing WHOIS lookup for {domain}")

        # Suppress stderr from whois library to avoid cluttering output
        old_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

        try:
            # Query WHOIS database
            domain_info = whois.whois(domain)
        finally:
            # Restore stderr
            sys.stderr.close()
            sys.stderr = old_stderr

        # Check if domain is registered
        # A registered domain will have registrar, creation_date, or status fields
        if domain_info.registrar or domain_info.creation_date or domain_info.status:
            logger.debug(f"{domain} is registered (taken)")
            return False
        else:
            logger.debug(f"{domain} is not registered (available)")
            return True

    except Exception as e:
        # Restore stderr in case of exception
        if sys.stderr != old_stderr:
            try:
                sys.stderr.close()
            except:
                pass
            sys.stderr = old_stderr

        # WHOIS lookup failed - could mean domain is available or service error
        # Check if it's a "domain not found" error (domain is available)
        error_str = str(e).lower()
        if 'not found' in error_str or 'no match' in error_str:
            logger.debug(f"{domain} is available (not found in WHOIS)")
            return True

        # Other errors - assume available to avoid false negatives
        # Only log at debug level to avoid cluttering output
        logger.debug(
            f"WHOIS lookup error for {domain}: {e}. Assuming available."
        )
        return True


def batch_check_domains(
    brand_names: List[str],
    extensions: Optional[List[str]] = None
) -> Dict[str, Dict[str, bool]]:
    """
    Check domain availability for multiple brand names.

    Args:
        brand_names: List of brand names to check
        extensions: List of domain extensions to check (default: ['.com', '.ai', '.io'])

    Returns:
        Dictionary mapping brand names to their domain availability results:
        {
            'Brand1': {'brand1.com': True, 'brand1.ai': False, 'brand1.io': True},
            'Brand2': {'brand2.com': False, 'brand2.ai': True, 'brand2.io': True}
        }

    Examples:
        >>> batch_check_domains(['Brand1', 'Brand2'])
        {
            'Brand1': {'brand1.com': True, 'brand1.ai': False, 'brand1.io': True},
            'Brand2': {'brand2.com': False, 'brand2.ai': True, 'brand2.io': True}
        }
    """
    logger.info(f"Starting batch domain check for {len(brand_names)} brand names")

    results = {}
    for brand_name in brand_names:
        results[brand_name] = check_domain_availability(brand_name, extensions)

        # Small delay to avoid rate limiting
        time.sleep(0.1)

    logger.info(f"Batch domain check complete for {len(brand_names)} brands")
    return results


def get_available_alternatives(
    brand_name: str,
    extensions: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Get available domain alternatives with prefix variations.

    Args:
        brand_name: Brand name to check
        extensions: List of extensions (default: ['.com'])

    Returns:
        Dictionary with 'base' and 'variations' keys:
        {
            'base': {'brandname.com': True, 'brandname.ai': False, ...},
            'variations': {'getbrandname.com': True, 'trybrandname.com': False, ...}
        }
    """
    if extensions is None:
        extensions = ['.com']  # Default to .com for alternatives

    # Check base domains
    base_results = check_domain_availability(brand_name, extensions, include_prefixes=False)

    # Check prefix variations
    variation_results = {}
    domain_base = brand_name.lower().replace(' ', '').replace('-', '')

    for prefix in DOMAIN_PREFIXES:
        for ext in extensions:
            domain = f"{prefix}{domain_base}{ext}"

            # Check cache first
            cached_result = _domain_cache.get(domain)
            if cached_result is not None:
                variation_results[domain] = cached_result[domain]
                continue

            # Perform WHOIS lookup
            is_available = _check_single_domain(domain)
            variation_results[domain] = is_available

            # Cache the result
            _domain_cache.set(domain, {domain: is_available})

            # Small delay
            time.sleep(0.05)

    return {
        'base': base_results,
        'variations': variation_results
    }


def clear_cache() -> None:
    """Clear the domain availability cache."""
    global _domain_cache
    _domain_cache = DomainCache(ttl_minutes=5)
    logger.info("Domain cache cleared")


# ADK Tool Registration
def create_domain_checker_tool():
    """
    Create and return an ADK-compatible tool for domain availability checking.

    Returns:
        Tool instance that can be used by ADK agents

    Example:
        >>> from src.tools.domain_checker import create_domain_checker_tool
        >>> domain_tool = create_domain_checker_tool()
        >>> # Use with agent
        >>> agent = LlmAgent(
        ...     name="validation_agent",
        ...     tools=[domain_tool],
        ...     ...
        ... )
    """
    # Try to import real ADK, fall back to mock for Phase 1
    try:
        from google_genai.adk import Tool
    except ImportError:
        from src.utils.mock_adk import Tool

    return Tool(
        name="check_domain_availability",
        description=(
            "Check domain availability for brand names across .com, .ai, and .io extensions. "
            "Returns availability status for each domain extension. "
            "Automatically handles WHOIS errors and caches results for 5 minutes."
        ),
        func=check_domain_availability
    )
