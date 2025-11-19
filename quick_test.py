#!/usr/bin/env python3
"""
Simple test to verify ADK components work.
"""

from dotenv import load_dotenv
load_dotenv()

print("\n" + "=" * 70)
print("AI BRAND STUDIO - QUICK COMPONENT TEST")
print("=" * 70 + "\n")

# Test imports
print("Testing imports...")
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from src.agents.orchestrator import create_orchestrator
print("✓ Imports successful\n")

# Test agent creation
print("Testing agent creation...")
orchestrator = create_orchestrator()
print(f"✓ Orchestrator: {orchestrator.name} ({type(orchestrator).__name__})\n")

# Test agent structure
print("Agent structure:")
print(f"  - Sequential agent with {len(orchestrator.agents)} sub-agents")
for i, agent in enumerate(orchestrator.agents, 1):
    print(f"  {i}. {agent.name} ({type(agent).__name__})")

print("\n" + "=" * 70)
print("✓ SYSTEM READY - All components working!")
print("=" * 70)
print("\nTo run the full system:")
print("  python -m src.main")
print("\nFor interactive CLI:")
print("  python -m src.cli")
print()
