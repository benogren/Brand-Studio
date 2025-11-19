"""
Agent implementations for AI Brand Studio.

This module contains all specialized agents migrated to ADK:
- Base ADK Agent: Factory helper for creating configured agents
- Research Agent: Researches industry trends with google_search tool
- Name Generator: Generates brand name candidates using RAG FunctionTool
- Validation Agent: Validates domain and trademark availability with FunctionTools
- SEO Optimizer: Analyzes and optimizes for SEO
- Story Generator: Creates brand narratives and marketing copy
- Orchestrator: Coordinates the multi-agent workflow (to be migrated)
"""

# ADK agent creation functions
from src.agents.base_adk_agent import create_brand_agent
from src.agents.research_agent import create_research_agent
from src.agents.name_generator import create_name_generator_agent
from src.agents.validation_agent import create_validation_agent
from src.agents.seo_agent import create_seo_agent
from src.agents.story_agent import create_story_agent
from src.agents.orchestrator import (
    create_brand_pipeline,
    create_refinement_loop,
    create_orchestrator
)

__all__ = [
    # Base factory
    'create_brand_agent',
    # Individual agent creators
    'create_research_agent',
    'create_name_generator_agent',
    'create_validation_agent',
    'create_seo_agent',
    'create_story_agent',
    # Orchestrator and workflow components
    'create_brand_pipeline',
    'create_refinement_loop',
    'create_orchestrator',
]
