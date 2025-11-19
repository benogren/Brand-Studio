"""
Custom tools for AI Brand Studio agents.

This module contains ADK FunctionTool implementations:
- Domain Checker: Check domain availability (.com, .ai, .io, etc.)
- Trademark Search: Search USPTO trademark database
"""

# Export FunctionTool instances
from src.tools.domain_checker import (
    domain_checker_tool,
    check_domain_availability_tool,
    check_domain_availability,
)

from src.tools.trademark_checker import (
    trademark_checker_tool,
    search_trademarks_tool,
    search_trademarks_uspto,
)

__all__ = [
    # FunctionTool instances (for agent tools list)
    'domain_checker_tool',
    'trademark_checker_tool',
    # Wrapped functions (alternative access)
    'check_domain_availability_tool',
    'search_trademarks_tool',
    # Original functions (for direct use if needed)
    'check_domain_availability',
    'search_trademarks_uspto',
]
