#!/usr/bin/env python3
"""
Deploy AI Brand Studio agent to Vertex AI Agent Engine using ADK Python API.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform
from src.agents.orchestrator import create_orchestrator

def main():
    """Deploy agent to Vertex AI Agent Engine."""

    # Get configuration from environment
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        print("ERROR: GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    print(f"Deploying AI Brand Studio Agent to Vertex AI")
    print(f"Project: {project_id}")
    print(f"Location: {location}")
    print("-" * 60)

    # Initialize Vertex AI
    print("\n1. Initializing Vertex AI...")
    aiplatform.init(project=project_id, location=location)
    print("   ✓ Vertex AI initialized")

    # Create orchestrator agent
    print("\n2. Creating orchestrator agent...")
    orchestrator = create_orchestrator()
    print(f"   ✓ Agent created: {orchestrator.name}")

    # Deploy using Reasoning Engine
    print("\n3. Deploying to Vertex AI Reasoning Engine...")
    print("   This may take 5-10 minutes...")

    try:
        from google.cloud.aiplatform import reasoning_engines

        # Create reasoning engine
        reasoning_engine = reasoning_engines.ReasoningEngine.create(
            reasoning_engine=orchestrator,
            requirements=[
                "google-genai>=1.50.0",
                "google-adk>=1.18.0",
                "python-whois>=0.8.0",
                "requests>=2.31.0",
                "python-dotenv>=1.0.0",
            ],
            display_name="brand-studio-agent",
            description="AI Brand Studio - Multi-agent brand identity creation system",
            extra_packages=[str(project_root / "src")],
        )

        print(f"\n✓ Deployment successful!")
        print(f"\nReasoning Engine Details:")
        print(f"  Resource Name: {reasoning_engine.resource_name}")
        print(f"  Display Name: {reasoning_engine.display_name}")
        print(f"  Location: {location}")
        print(f"\nYou can now query your agent using:")
        print(f"  reasoning_engine.query(input='Create a brand for a fitness app')")

        # Save deployment info
        deployment_info = {
            "resource_name": reasoning_engine.resource_name,
            "display_name": reasoning_engine.display_name,
            "project_id": project_id,
            "location": location,
        }

        import json
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)

        print(f"\n✓ Deployment info saved to deployment_info.json")

    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
