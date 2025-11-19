"""
Orchestrator Agent for AI Brand Studio.

Coordinates the multi-agent brand creation workflow using ADK workflow patterns:
- SequentialAgent for the main pipeline
- LoopAgent for iterative refinement
- AgentTool for sub-agent delegation

Migrated to use real ADK instead of custom orchestration logic.
"""

import logging
from typing import Dict, Any
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool

from src.infrastructure.logging import get_logger
from src.agents.base_adk_agent import create_brand_agent
from src.agents.research_agent import create_research_agent
from src.agents.name_generator import create_name_generator_agent
from src.agents.validation_agent import create_validation_agent
from src.agents.seo_agent import create_seo_agent
from src.agents.story_agent import create_story_agent

logger = logging.getLogger('brand_studio.orchestrator')


# Orchestrator instruction prompt
ORCHESTRATOR_INSTRUCTION = """
You are the Brand Studio Orchestrator, coordinating a multi-agent workflow to generate
complete, validated brand identities.

## YOUR ROLE

You coordinate specialized agents to create brand identities through a structured workflow:

1. **Research Agent**: Analyzes industry trends and competitive landscape
2. **Name Generator**: Creates 20-50 brand name candidates using RAG
3. **Validation Agent**: Checks domain/trademark availability and risk
4. **SEO Agent**: Optimizes for search and creates meta content
5. **Story Agent**: Generates taglines, narratives, and positioning

## WORKFLOW COORDINATION

Your workflow follows this sequence:
1. Delegate to Research Agent for industry analysis
2. Use research insights to inform Name Generator
3. Validate top candidates with Validation Agent
4. If validation fails, loop back to Name Generator with feedback
5. Optimize validated names with SEO Agent
6. Generate brand story with Story Agent

## OUTPUT FORMAT

Consolidate all agent outputs into a comprehensive brand identity package:

```json
{
  "brand_identity": {
    "selected_name": "BrandName",
    "research_insights": {...},
    "name_candidates": [...],
    "validation_results": {...},
    "seo_optimization": {...},
    "brand_story": {...}
  },
  "workflow_status": "complete",
  "iterations": 1,
  "recommendations": "..."
}
```

## IMPORTANT GUIDELINES

1. **Delegate systematically** - Use the defined workflow sequence
2. **Pass context forward** - Each agent builds on previous results
3. **Handle failures gracefully** - If validation fails, provide feedback for refinement
4. **Consolidate results** - Combine all agent outputs into coherent package
5. **Track progress** - Report workflow status and iterations
"""


def create_brand_pipeline() -> SequentialAgent:
    """
    Create sequential brand creation pipeline using ADK SequentialAgent.

    Workflow sequence:
    Research → Name Generation → Validation → SEO → Story

    Returns:
        SequentialAgent configured with all brand creation agents

    Example:
        >>> pipeline = create_brand_pipeline()
        >>> # Pipeline can be used in Runner or wrapped in LoopAgent
    """
    logger.info("Creating brand creation pipeline with SequentialAgent")

    # Create all agents in the pipeline
    research_agent = create_research_agent()
    name_agent = create_name_generator_agent()
    validation_agent = create_validation_agent()
    seo_agent = create_seo_agent()
    story_agent = create_story_agent()

    # Create sequential pipeline
    pipeline = SequentialAgent(
        name="BrandCreationPipeline",
        sub_agents=[
            research_agent,
            name_agent,
            validation_agent,
            seo_agent,
            story_agent
        ]
    )

    logger.info("Brand creation pipeline created successfully with 5 sub-agents")
    return pipeline


def check_validation_passed(result: Dict[str, Any]) -> bool:
    """
    Loop condition function to check if validation criteria are met.

    Used by LoopAgent to determine if refinement loop should continue.

    Args:
        result: Result dictionary from the pipeline execution

    Returns:
        True if validation passed (loop should exit), False otherwise (continue looping)

    Validation criteria:
    - At least one name with CLEAR status (score 80+)
    - At least one premium domain available (.com, .ai, or .io)
    - No critical trademark conflicts
    """
    logger.info("Checking validation criteria for loop exit condition")

    # Extract validation results from the pipeline output
    validation_results = result.get("validation_results", {})

    # Check if validation_results is a dict or a list
    if isinstance(validation_results, dict):
        # Single validation result
        status = validation_results.get("validation_status", "BLOCKED")
        score = validation_results.get("overall_score", 0)

        # CLEAR status means score 80+
        if status == "CLEAR" and score >= 80:
            logger.info(f"Validation passed: {status} with score {score}")
            return True

        logger.info(f"Validation not passed: {status} with score {score}")
        return False

    elif isinstance(validation_results, list):
        # Multiple validation results - check if any passed
        for val in validation_results:
            status = val.get("validation_status", "BLOCKED")
            score = val.get("overall_score", 0)

            if status == "CLEAR" and score >= 80:
                logger.info(f"Validation passed for one candidate: {status} with score {score}")
                return True

        logger.info("No candidates passed validation")
        return False

    # Default to continuing loop if validation format unexpected
    logger.warning("Unexpected validation_results format, continuing loop")
    return False


def create_refinement_loop(max_iterations: int = 3) -> LoopAgent:
    """
    Create LoopAgent for iterative refinement of brand names.

    The loop runs the name generation and validation agents iteratively
    up to max_iterations times to find valid brand names.

    Args:
        max_iterations: Maximum refinement iterations (default: 3)

    Returns:
        LoopAgent configured for brand refinement

    Example:
        >>> loop = create_refinement_loop()
        >>> # Loop will refine names up to 3 times
    """
    logger.info(f"Creating refinement loop with max {max_iterations} iterations")

    # Create agents that need to loop (name generation + validation)
    name_agent = create_name_generator_agent()
    validation_agent = create_validation_agent()

    loop_agent = LoopAgent(
        name="BrandRefinementLoop",
        sub_agents=[name_agent, validation_agent],
        max_iterations=max_iterations
    )

    logger.info("Refinement loop created successfully")
    return loop_agent


def create_orchestrator() -> SequentialAgent:
    """
    Create main orchestrator using ADK workflow patterns.

    The orchestrator coordinates the entire brand creation process:
    1. Research agent analyzes industry
    2. LoopAgent for name generation + validation (iterative refinement)
    3. SEO and Story agents finalize the brand

    Workflow: Research → [Name + Validation Loop] → SEO → Story

    Returns:
        SequentialAgent configured as complete brand creation workflow

    Example:
        >>> orchestrator = create_orchestrator()
        >>> # Use with ADK Runner for execution
        >>> from google.adk.runners import InMemoryRunner
        >>> runner = InMemoryRunner(agent=orchestrator)
        >>> result = runner.run("Create a brand for an AI-powered meal planning app")
    """
    logger.info("Creating Brand Studio Orchestrator with ADK patterns")

    # Create individual agents
    research_agent = create_research_agent()
    refinement_loop = create_refinement_loop(max_iterations=3)
    seo_agent = create_seo_agent()
    story_agent = create_story_agent()

    # Create sequential workflow with loop in the middle
    orchestrator = SequentialAgent(
        name="BrandStudioOrchestrator",
        sub_agents=[
            research_agent,
            refinement_loop,  # Loops name generation + validation
            seo_agent,
            story_agent
        ]
    )

    logger.info("Brand Studio Orchestrator created successfully")
    return orchestrator
