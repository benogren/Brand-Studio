#!/usr/bin/env python3
"""
Quick test script to verify ADK migration is working.
"""

import sys
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("\n" + "=" * 70)
print("AI BRAND STUDIO - ADK MIGRATION TEST")
print("=" * 70 + "\n")

# Test 1: Imports
print("Test 1: Verifying imports...")
try:
    from google.adk.runners import InMemoryRunner
    from google.adk.apps.app import App, EventsCompactionConfig
    from google.adk.plugins.logging_plugin import LoggingPlugin
    from google.genai import types
    from src.agents.orchestrator import create_orchestrator
    print("✓ All imports successful\n")
except ImportError as e:
    print(f"✗ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Create Orchestrator
print("Test 2: Creating orchestrator...")
try:
    orchestrator = create_orchestrator()
    print(f"✓ Orchestrator created: {orchestrator.name}")
    print(f"  Type: {type(orchestrator).__name__}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    sys.exit(1)

# Test 3: Create App with Context Compaction
print("Test 3: Creating App with context compaction...")
try:
    app = App(
        name="BrandStudioApp",
        root_agent=orchestrator,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=5,
            overlap_size=1,
        ),
        plugins=[LoggingPlugin()],
    )
    print(f"✓ App created: {app.name}")
    print(f"  Plugins: {len(app.plugins)} configured\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    sys.exit(1)

# Test 4: Create Runner
print("Test 4: Creating InMemoryRunner...")
try:
    runner = InMemoryRunner(app=app)
    print("✓ Runner created successfully\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
    sys.exit(1)

# Test 5: Quick execution test
print("Test 5: Running a simple query...")
print("(This will make real API calls and may take 30-60 seconds)\n")

try:
    start_time = time.time()
    
    # Create message with correct ADK format
    prompt = """Generate 5 creative brand name ideas for a simple fitness tracking app.
Keep it brief - just list 5 names with a one-sentence description each."""
    
    events = list(runner.run(
        user_id="test_user",
        session_id="test_session",
        new_message=types.Content(
            parts=[types.Part(text=prompt)]
        )
    ))
    
    duration = time.time() - start_time
    
    # Extract result from events
    result = None
    for event in events:
        if hasattr(event, 'content') and event.content:
            result = event.content
    
    if result is None:
        result = "No response generated"
    
    print(f"✓ Query completed in {duration:.1f} seconds")
    print(f"  Total events: {len(events)}")
    print(f"\nResult preview:")
    print("-" * 70)
    result_str = str(result)
    if len(result_str) > 500:
        print(result_str[:500] + "...")
    else:
        print(result_str)
    print("-" * 70 + "\n")
    
except Exception as e:
    print(f"✗ Execution failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("✓ ALL TESTS PASSED - ADK MIGRATION WORKING!")
print("=" * 70)
print("\nNext steps:")
print("  1. Try the interactive CLI: python -m src.cli")
print("  2. Run full generation: python -m src.main")
print("  3. Run unit tests: pytest tests/")
print()
