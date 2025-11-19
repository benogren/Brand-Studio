"""
Base ADK agent factory for Brand Studio.

Provides helper functions to create properly configured ADK agents with retry logic,
model configuration, and callback support.
"""

from typing import Optional, List, Callable
from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini


def create_brand_agent(
    name: str,
    instruction: str,
    model_name: str = "gemini-2.5-flash-lite",
    tools: Optional[List] = None,
    sub_agents: Optional[List] = None,
    output_key: Optional[str] = None,
    after_agent_callback: Optional[Callable] = None,
) -> Agent:
    """
    Create a properly configured ADK agent for Brand Studio.

    Args:
        name: Agent name
        instruction: Agent instruction prompt
        model_name: Gemini model to use
        tools: List of tools (FunctionTool, AgentTool, etc.)
        sub_agents: List of sub-agents for orchestration
        output_key: Key to store outputs in workflow
        after_agent_callback: Callback function after agent execution

    Returns:
        Configured Agent instance
    """
    # Configure retry options
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    # Create Gemini model
    model = Gemini(
        model=model_name,
        retry_options=retry_config
    )

    # Build tools list
    agent_tools = tools or []
    if sub_agents:
        from google.adk.tools import AgentTool
        agent_tools.extend([AgentTool(agent) for agent in sub_agents])

    # Create agent
    agent = Agent(
        name=name,
        model=model,
        instruction=instruction,
        tools=agent_tools,
        output_key=output_key,
    )

    # Add callback if provided
    if after_agent_callback:
        agent.after_agent_callback = after_agent_callback

    return agent
