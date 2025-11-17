"""
Mock ADK implementation for Phase 1 local development.

This module provides mock implementations of the ADK (Agent Development Kit)
classes to allow the code to run locally without full Vertex AI setup.

In Phase 2, when Vertex AI is properly configured, these mocks will be replaced
with the real ADK from google_genai.adk.
"""

from typing import List, Optional, Any, Dict


class Tool:
    """Mock Tool class for ADK compatibility."""

    def __init__(
        self,
        name: str,
        description: str,
        func: callable
    ):
        """
        Initialize a mock tool.

        Args:
            name: Tool name
            description: Tool description
            func: Function to execute
        """
        self.name = name
        self.description = description
        self.func = func

    def __call__(self, *args, **kwargs):
        """Execute the tool function."""
        return self.func(*args, **kwargs)


class LlmAgent:
    """
    Mock LlmAgent class for Phase 1 development.

    This is a placeholder implementation that allows the code to run
    without actual LLM calls. In Phase 2, this will be replaced with
    the real LlmAgent from Vertex AI ADK.
    """

    def __init__(
        self,
        name: str,
        model: str,
        description: str = "",
        instruction: str = "",
        sub_agents: Optional[List] = None,
        tools: Optional[List[Tool]] = None
    ):
        """
        Initialize a mock LLM agent.

        Args:
            name: Agent name
            model: Model name (e.g., 'gemini-2.5-pro')
            description: Agent description
            instruction: Agent instruction prompt
            sub_agents: List of sub-agents
            tools: List of tools available to the agent
        """
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.sub_agents = sub_agents or []
        self.tools = tools or []

    def generate(self, prompt: str) -> str:
        """
        Mock generation method.

        In Phase 2, this will call the actual LLM.
        For Phase 1, it returns a placeholder response.

        Args:
            prompt: Input prompt

        Returns:
            Generated response (placeholder in Phase 1)
        """
        return f"[Mock Response for {self.name}] Received prompt: {prompt[:50]}..."

    def __repr__(self):
        """String representation."""
        return f"LlmAgent(name='{self.name}', model='{self.model}')"
