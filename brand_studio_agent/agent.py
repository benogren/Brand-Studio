"""
AI Brand Studio - Production Agent Entry Point

This module exports the root_agent for deployment to Google Agent Engine.
"""

import os
import sys

# Add parent directory to path to import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.orchestrator import create_orchestrator

# Create and export the root agent for deployment
root_agent = create_orchestrator()

# Export for ADK
__all__ = ['root_agent']
