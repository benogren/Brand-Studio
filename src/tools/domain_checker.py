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
import requests
from typing import Dict, Optional, List, Set
from datetime import datetime, timedelta
import whois
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# Configure logger
logger = logging.getLogger('brand_studio.domain_checker')

# Namecheap API configuration
NAMECHEAP_API_ENDPOINT = "https://api.namecheap.com/xml.response"

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


def _check_namecheap_availability(domain: str) -> Optional[bool]:
    """
    Check domain availability using Namecheap API.

    Args:
        domain: Full domain name (e.g., 'example.com')

    Returns:
        True if available, False if taken, None if API call failed

    Note:
        Requires NAMECHEAP_API_KEY, NAMECHEAP_API_USER, and NAMECHEAP_USERNAME
        environment variables to be set.
    """
    try:
        # Get Namecheap credentials from environment
        api_key = os.getenv('NAMECHEAP_API_KEY')
        api_user = os.getenv('NAMECHEAP_API_USER')
        username = os.getenv('NAMECHEAP_USERNAME')
        client_ip = os.getenv('NAMECHEAP_CLIENT_IP', '0.0.0.0')

        # If credentials not available, return None to fall back to WHOIS
        if not all([api_key, api_user, username]):
            logger.debug("Namecheap credentials not configured, skipping API check")
            return None

        logger.debug(f"Checking {domain} via Namecheap API")

        # Build Namecheap API request
        params = {
            'ApiUser': api_user,
            'ApiKey': api_key,
            'UserName': username,
            'Command': 'namecheap.domains.check',
            'ClientIp': client_ip,
            'DomainList': domain
        }

        # Make API request
        response = requests.get(NAMECHEAP_API_ENDPOINT, params=params, timeout=5)
        response.raise_for_status()

        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)

        # Namecheap uses namespace in all elements
        # Format: {http://api.namecheap.com/xml.response}DomainCheckResult
        namespace = {'nc': 'http://api.namecheap.com/xml.response'}

        # Find the DomainCheckResult element for this domain
        domain_result = root.find(f".//nc:DomainCheckResult[@Domain='{domain}']", namespace)

        if domain_result is not None:
            available = domain_result.get('Available', '').lower() == 'true'
            logger.debug(f"Namecheap API: {domain} is {'available' if available else 'taken'}")
            return available

        # Fallback: try without namespace filtering (search all DomainCheckResult elements)
        for elem in root.iter():
            if elem.tag.endswith('DomainCheckResult') and elem.get('Domain') == domain:
                available = elem.get('Available', '').lower() == 'true'
                logger.debug(f"Namecheap API: {domain} is {'available' if available else 'taken'}")
                return available

        logger.warning(f"Could not parse Namecheap response for {domain}")
        return None

    except requests.RequestException as e:
        logger.debug(f"Namecheap API request failed for {domain}: {e}")
        return None
    except Exception as e:
        logger.debug(f"Namecheap API error for {domain}: {e}")
        return None


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

    Special handling:
    - Prefixes (get-, try-, etc.) are ONLY applied to .com domains
    - Names ending in "AI" get special .ai domain handling:
      - For "NameAI": checks nameai.com, nameai.io, name.ai (without the AI suffix)
      - Does NOT check nameai.ai (redundant)

    Args:
        brand_name: Brand name to check (will be converted to domain format)
        extensions: List of domain extensions to check (default: all 10 TLDs)
        include_prefixes: If True, also check prefix variations (only for .com)

    Returns:
        Dictionary mapping domain names to availability status:
        {
            'brandname.com': True,   # Available
            'brandname.ai': False,   # Taken
            'getbrandname.com': True # Available (if include_prefixes=True, .com only)
        }

    Examples:
        >>> check_domain_availability('MyBrand')
        {'mybrand.com': True, 'mybrand.ai': False, 'mybrand.io': True, ...}

        >>> check_domain_availability('NameAI', extensions=['.com', '.ai', '.io'])
        {'nameai.com': True, 'name.ai': True, 'nameai.io': False}
        # Note: nameai.ai is NOT checked (redundant)

        >>> check_domain_availability('TestBrand', extensions=['.com', '.ai'], include_prefixes=True)
        {'testbrand.com': False, 'gettestbrand.com': True, 'testbrand.ai': True}
        # Note: Prefixes only apply to .com, not .ai
    """
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS

    # Convert brand name to domain format (lowercase, remove spaces/special chars)
    domain_base = brand_name.lower().replace(' ', '').replace('-', '')

    # Detect if name ends with "ai" (case-insensitive)
    ends_with_ai = domain_base.endswith('ai') and len(domain_base) > 2

    # Build list of domain names to check
    domain_names = []

    # Add base brand name with all extensions
    for ext in extensions:
        # Special handling for .ai extension when name ends with "ai"
        if ext == '.ai' and ends_with_ai:
            # Remove the "ai" suffix and add .ai extension
            # e.g., "nameai" becomes "name.ai"
            # This avoids checking "nameai.ai" which is redundant
            base_without_ai = domain_base[:-2]
            domain_names.append(f"{base_without_ai}{ext}")
        else:
            # Normal case: just append extension
            domain_names.append(f"{domain_base}{ext}")

    # Add prefix variations if requested (ONLY for .com)
    if include_prefixes:
        for prefix in DOMAIN_PREFIXES:
            # Only add .com prefix variations
            domain_names.append(f"{prefix}{domain_base}.com")

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
    Check availability of a single domain.

    Tries Namecheap API first (if configured), then falls back to WHOIS.

    Args:
        domain: Full domain name (e.g., 'example.com')

    Returns:
        True if domain is available, False if taken

    Note:
        On lookup failure or exception, assumes domain is available
        (defensive approach to avoid false negatives that could eliminate
        valid name candidates).
    """
    # First, try Namecheap API if configured
    namecheap_result = _check_namecheap_availability(domain)
    if namecheap_result is not None:
        return namecheap_result

    # Fall back to WHOIS
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


# ADK FunctionTool Registration

def check_domain_availability_tool(
    brand_name: str,
    include_prefixes: bool = False
) -> Dict[str, bool]:
    """
    ADK FunctionTool for checking domain availability across multiple TLDs.

    This tool checks if domains are available for registration across popular
    extensions including .com, .ai, .io, .so, .app, .co, .is, .me, .net, and .to.

    Args:
        brand_name: Brand name to check (converted to domain format)
        include_prefixes: If True, also check prefix variations like get-, try-, etc. (only .com)

    Returns:
        Dictionary mapping domain names to availability:
        {
            'brandname.com': True,   # Available
            'brandname.ai': False,   # Taken
            'brandname.io': True     # Available
        }

    Example:
        >>> result = check_domain_availability_tool("MyBrand", extensions=[".com", ".ai", ".io"])
        >>> print(result)
        {'mybrand.com': True, 'mybrand.ai': False, 'mybrand.io': True}
    """
    logger.info(f"Domain checker tool called for '{brand_name}'")

    # Call the underlying check_domain_availability function
    # Always use default extensions (all 10 TLDs)
    return check_domain_availability(
        brand_name=brand_name,
        extensions=None,  # Use default extensions
        include_prefixes=include_prefixes
    )


# Create the FunctionTool instance for use in agents
domain_checker_tool = FunctionTool(check_domain_availability_tool)


# Legacy function for backward compatibility
def create_domain_checker_tool():
    """
    Create and return an ADK-compatible tool for domain availability checking.

    DEPRECATED: Use domain_checker_tool directly instead.

    Returns:
        FunctionTool instance that can be used by ADK agents
    """
    return domain_checker_tool
