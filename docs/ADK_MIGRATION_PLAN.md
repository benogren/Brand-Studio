# ADK Migration Plan - Detailed Task Breakdown

**Based on:** ADK_ALIGNMENT_AUDIT.md
**Purpose:** Executable task plan for migrating to ADK compliance
**Status:** Planning Document - Not Yet Implemented

---

## Overview

This document provides a detailed, actionable task breakdown for migrating the Brand Studio implementation to ADK compliance. Tasks are organized by phase and include specific file changes, code examples, and acceptance criteria.

---

## Phase 1: Critical Foundation

**Timeline:** Week 1-2
**Priority:** 🔴 CRITICAL
**Goal:** Replace mock ADK with real ADK, adopt workflow patterns

### Task 1.1: Setup Real ADK Dependencies

**Files to Modify:**
- `requirements.txt`
- `.env`
- `pyproject.toml`

**Steps:**
1. Update `requirements.txt`:
   ```txt
   # Remove or comment out mock dependencies
   # Add real ADK
   google-adk>=0.1.0
   google-generativeai>=0.3.0
   opentelemetry-instrumentation-google-genai
   ```

2. Update `.env.example` and `.env`:
   ```bash
   # Add for real ADK
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=1  # Use Vertex AI instead of AI Studio
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Acceptance Criteria:**
- ✅ Can import `from google.adk.agents import Agent`
- ✅ No import errors for ADK modules
- ✅ Environment variables set correctly

**Testing:**
```python
# Test import
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
print("✅ Real ADK imported successfully")
```

---

### Task 1.2: Create Real ADK Agent Base Class

**Files to Create:**
- `src/agents/base_adk_agent.py`

**Purpose:** Wrapper for consistent ADK agent creation

**Implementation:**
```python
"""
Base ADK Agent utilities for Brand Studio.

Provides helpers for creating properly configured ADK agents.
"""

import os
from typing import List, Optional, Callable, Any
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types


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
```

**Acceptance Criteria:**
- ✅ Can create agents using helper
- ✅ Agents properly configured with retry logic
- ✅ Callbacks work correctly

---

### Task 1.3: Migrate Research Agent to Real ADK

**Files to Modify:**
- `src/agents/research_agent.py`

**Changes:**
```python
# OLD (Mock ADK):
from src.utils.mock_adk import LlmAgent

class ResearchAgent:
    def __init__(self, project_id, location, model_name):
        self.agent = LlmAgent(...)

# NEW (Real ADK):
from google.adk.tools import google_search
from src.agents.base_adk_agent import create_brand_agent

def create_research_agent() -> Agent:
    """Create ADK-compliant research agent."""
    return create_brand_agent(
        name="ResearchAgent",
        instruction=RESEARCH_AGENT_INSTRUCTION,
        model_name="gemini-2.5-flash-lite",
        tools=[google_search],
        output_key="research_findings"
    )
```

**Acceptance Criteria:**
- ✅ Agent uses real ADK Agent class
- ✅ Uses google_search tool from ADK
- ✅ Returns properly formatted outputs
- ✅ No references to mock ADK

---

### Task 1.4: Migrate Name Generator to Real ADK with FunctionTool

**Files to Modify:**
- `src/agents/name_generator.py`
- `src/rag/brand_retrieval.py` (wrap as FunctionTool)

**Changes:**
```python
# Create FunctionTool for RAG
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

def retrieve_similar_brands(
    industry: str,
    keywords: list,
    k: int = 50,
    tool_context: ToolContext = None
) -> dict:
    """Retrieve similar brands using RAG."""
    # Original RAG logic
    vector_client = VectorSearchClient(...)
    results = vector_client.search(...)
    return {"similar_brands": results}

# Wrap as FunctionTool
rag_tool = FunctionTool(retrieve_similar_brands)

# Create agent
def create_name_generator_agent() -> Agent:
    return create_brand_agent(
        name="NameGeneratorAgent",
        instruction=NAME_GENERATOR_INSTRUCTION,
        model_name="gemini-2.5-pro",
        tools=[rag_tool],
        output_key="generated_names"
    )
```

**Acceptance Criteria:**
- ✅ RAG wrapped as FunctionTool
- ✅ Agent uses real ADK
- ✅ Tool properly integrated
- ✅ Can access ToolContext if needed

---

### Task 1.5: Migrate Validation Agent to Real ADK

**Files to Modify:**
- `src/agents/validation_agent.py`
- `src/tools/domain_checker.py` (wrap as FunctionTool)
- `src/tools/trademark_checker.py` (wrap as FunctionTool)

**Changes:**
```python
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# Wrap domain checker
def check_domains_adk(
    brand_name: str,
    tlds: list = [".com", ".ai", ".io"],
    tool_context: ToolContext = None
) -> dict:
    """Check domain availability."""
    # Original logic from domain_checker.py
    results = check_domain_availability(brand_name, tlds)
    return results

domain_tool = FunctionTool(check_domains_adk)

# Wrap trademark checker
def check_trademarks_adk(
    brand_name: str,
    tool_context: ToolContext = None
) -> dict:
    """Check trademark conflicts."""
    # Original logic
    results = search_trademarks_uspto(brand_name)
    return results

trademark_tool = FunctionTool(check_trademarks_adk)

# Create validation agent
def create_validation_agent() -> Agent:
    return create_brand_agent(
        name="ValidationAgent",
        instruction=VALIDATION_AGENT_INSTRUCTION,
        model_name="gemini-2.5-flash",
        tools=[domain_tool, trademark_tool],
        output_key="validation_results"
    )
```

**Acceptance Criteria:**
- ✅ All tools wrapped as FunctionTool
- ✅ Agent uses real ADK
- ✅ Tool schemas auto-generated
- ✅ Validation logic preserved

---

### Task 1.6: Migrate SEO & Story Agents

**Files to Modify:**
- `src/agents/seo_agent.py`
- `src/agents/story_agent.py`

**Similar pattern to previous agents:**
```python
# SEO Agent
def create_seo_agent() -> Agent:
    return create_brand_agent(
        name="SEOAgent",
        instruction=SEO_AGENT_INSTRUCTION,
        model_name="gemini-2.5-flash",
        output_key="seo_analysis"
    )

# Story Agent
def create_story_agent() -> Agent:
    return create_brand_agent(
        name="StoryAgent",
        instruction=STORY_AGENT_INSTRUCTION,
        model_name="gemini-2.5-pro",
        output_key="brand_story"
    )
```

**Acceptance Criteria:**
- ✅ Both agents migrated to real ADK
- ✅ Instructions preserved
- ✅ Output keys defined

---

### Task 1.7: Refactor Orchestrator with Workflow Patterns

**Files to Modify:**
- `src/agents/orchestrator.py` (MAJOR REFACTOR)

**Implementation:**
```python
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool
from src.agents.base_adk_agent import create_brand_agent

def create_brand_pipeline() -> SequentialAgent:
    """
    Create sequential brand creation pipeline.

    Workflow:
    Research → Name Generation → Validation → SEO → Story
    """
    # Create all agents
    research_agent = create_research_agent()
    name_agent = create_name_generator_agent()
    validation_agent = create_validation_agent()
    seo_agent = create_seo_agent()
    story_agent = create_story_agent()

    # Create sequential pipeline
    pipeline = SequentialAgent(
        name="brand_creation_pipeline",
        agents=[
            research_agent,
            name_agent,
            validation_agent,
            seo_agent,
            story_agent
        ]
    )

    return pipeline


def create_refinement_loop(pipeline: SequentialAgent) -> LoopAgent:
    """
    Wrap pipeline in loop for iterative refinement.

    Loops until validation passes or max 3 iterations.
    """
    def check_validation_passed(result: dict) -> bool:
        """Check if validation criteria met."""
        validation = result.get("validation_results", {})
        # Check if at least 50% names have low risk and 1+ domain
        # ... validation logic
        return validation.get("passed", False)

    loop_agent = LoopAgent(
        name="brand_refinement_loop",
        agent=pipeline,
        max_iterations=3,
        loop_condition_fn=check_validation_passed
    )

    return loop_agent


def create_orchestrator() -> Agent:
    """
    Create main orchestrator agent.

    Uses sub-agents via AgentTool for dynamic orchestration.
    """
    # Create workflow components
    pipeline = create_brand_pipeline()
    refinement_loop = create_refinement_loop(pipeline)

    # Create orchestrator with sub-agents as tools
    orchestrator = create_brand_agent(
        name="BrandStudioOrchestrator",
        instruction=ORCHESTRATOR_INSTRUCTION,
        model_name="gemini-2.5-flash-lite",
        sub_agents=[refinement_loop]  # Uses AgentTool automatically
    )

    return orchestrator
```

**Acceptance Criteria:**
- ✅ Uses SequentialAgent for pipeline
- ✅ Uses LoopAgent for refinement
- ✅ Uses AgentTool for sub-agent delegation
- ✅ No custom workflow logic
- ✅ Validation logic preserved

---

### Task 1.8: Remove Mock ADK

**Files to Delete:**
- `src/utils/mock_adk.py`

**Files to Update:**
- Remove all imports of `from src.utils.mock_adk import LlmAgent`
- Replace with `from google.adk.agents import Agent`

**Verification:**
```bash
# Search for any remaining mock imports
grep -r "from src.utils.mock_adk" src/
# Should return nothing
```

**Acceptance Criteria:**
- ✅ mock_adk.py deleted
- ✅ No imports of mock ADK anywhere
- ✅ All agents use real ADK

---

### Task 1.9: Update Main Entry Point

**Files to Modify:**
- `src/main.py`
- `src/cli.py`

**Changes:**
```python
# main.py
from src.agents.orchestrator import create_orchestrator
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

def main():
    # Create orchestrator
    orchestrator = create_orchestrator()

    # Create runner
    runner = Runner(
        agent=orchestrator,
        session_service=DatabaseSessionService(
            db_url="sqlite:///brand_studio.db"
        )
    )

    # Run query
    result = runner.run(
        message="Generate healthcare app brand names",
        user_id="user123",
        session_id="session_001"
    )

    return result
```

**Acceptance Criteria:**
- ✅ Uses Runner from ADK
- ✅ Proper session service integration
- ✅ Clean entry point

---

## Phase 2: Tools & Memory

**Timeline:** Week 3
**Priority:** 🟡 MEDIUM
**Goal:** Adopt ADK tool patterns and memory management

### Task 2.1: Wrap All Tools with FunctionTool

**Files to Modify:**
- All files in `src/tools/`

**Pattern:**
```python
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# Original function
def my_tool_logic(param1: str, param2: int) -> dict:
    # ... existing logic
    return results

# Wrapped version
def my_tool_adk(
    param1: str,
    param2: int,
    tool_context: ToolContext = None
) -> dict:
    """Tool description for LLM."""
    # Can now access session state
    if tool_context:
        user_prefs = tool_context.state.get("user:preferences")

    # Call original logic
    results = my_tool_logic(param1, param2)
    return results

# Export as FunctionTool
my_tool = FunctionTool(my_tool_adk)
```

**Files:**
- `src/tools/domain_checker.py` ✅ (done in 1.5)
- `src/tools/trademark_checker.py` ✅ (done in 1.5)
- `src/tools/social_handles.py`
- `src/tools/seo_analyzer.py`
- `src/tools/brand_story.py`

**Acceptance Criteria:**
- ✅ All tools wrapped with FunctionTool
- ✅ All tools have ToolContext parameter
- ✅ Tools can access session state

---

### Task 2.2: Replace SessionManager with DatabaseSessionService

**Files to Delete:**
- `src/database/session_manager.py`

**Files to Modify:**
- `src/main.py`
- `src/cli.py`
- Any files using SessionManager

**Implementation:**
```python
from google.adk.sessions import DatabaseSessionService

# Create service
session_service = DatabaseSessionService(
    db_url="sqlite:///brand_studio_sessions.db"
)

# Use in Runner
runner = Runner(
    agent=orchestrator,
    session_service=session_service
)
```

**Data Migration:**
```python
# Optional: Migrate existing .sessions/ data to SQLite
import json
import sqlite3
from pathlib import Path

def migrate_file_sessions_to_db():
    """Migrate old file-based sessions to DatabaseSessionService."""
    sessions_dir = Path(".sessions")
    if not sessions_dir.exists():
        return

    # ... migration logic
```

**Acceptance Criteria:**
- ✅ SessionManager deleted
- ✅ Using DatabaseSessionService
- ✅ Existing session data migrated (if applicable)
- ✅ Sessions persist in SQLite

---

### Task 2.3: Adopt ADK Memory Tools

**Files to Modify:**
- `src/session/memory_bank.py` (refactor)
- `src/agents/orchestrator.py` (add memory tools)

**Implementation:**
```python
from google.adk.tools import preload_memory, load_memory

# Add automatic memory callback
async def save_to_memory_callback(callback_context):
    """Automatically save session to memory after each turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Update orchestrator
orchestrator = create_brand_agent(
    name="BrandStudioOrchestrator",
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[preload_memory],  # Add memory tool
    after_agent_callback=save_to_memory_callback,  # Auto-save
    ...
)
```

**Acceptance Criteria:**
- ✅ Uses preload_memory or load_memory
- ✅ Automatic memory saving via callback
- ✅ Memory persists across sessions
- ✅ Can retrieve past preferences

---

### Task 2.4: Wrap Agents in App with Context Compaction

**Files to Modify:**
- `src/main.py`
- `src/cli.py`

**Implementation:**
```python
from google.adk.apps.app import App, EventsCompactionConfig

# Create app with compaction
app = App(
    name="brand_studio",
    root_agent=orchestrator,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,  # Compact every 5 turns
        overlap_size=1          # Keep 1 previous turn
    )
)

# Use app in runner
runner = Runner(
    app=app,  # Use app instead of agent
    session_service=session_service,
    memory_service=memory_service
)
```

**Acceptance Criteria:**
- ✅ Agents wrapped in App
- ✅ Context compaction configured
- ✅ Compaction triggers correctly
- ✅ Token usage reduced in long conversations

---

## Phase 3: Observability & Evaluation

**Timeline:** Week 4
**Priority:** 🟡 MEDIUM
**Goal:** Add ADK observability and evaluation

### Task 3.1: Integrate LoggingPlugin

**Files to Modify:**
- `src/main.py`
- `src/cli.py`

**Implementation:**
```python
from google.adk.plugins.logging_plugin import LoggingPlugin
from src.infrastructure.logging import get_logger  # Keep custom logger

# Use both
runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service,
    plugins=[LoggingPlugin()]  # Add ADK logging
)

# Custom logger still available
custom_logger = get_logger()
custom_logger.log_agent_action(...)
```

**Acceptance Criteria:**
- ✅ LoggingPlugin integrated
- ✅ Automatic logs captured
- ✅ Custom logger still works
- ✅ Compatible with ADK web UI

---

### Task 3.2: Create ADK Evaluation Test Suite

**Files to Create:**
- `tests/integration.evalset.json`
- `tests/eval_config.json`
- `tests/evaluators/name_quality_evaluator.py`
- `tests/evaluators/validation_accuracy_evaluator.py`

**eval_config.json:**
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

**integration.evalset.json:**
```json
{
  "eval_set_id": "brand_studio_integration_tests",
  "eval_cases": [
    {
      "eval_id": "healthcare_app_generation",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Generate brand names for a healthcare app for seniors"}]
          },
          "final_response": {
            "parts": [{"text": "Expected response pattern..."}]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "ResearchAgent",
                "args": {"query": "healthcare seniors"}
              },
              {
                "name": "NameGeneratorAgent",
                "args": {"industry": "healthcare", "target_audience": "seniors"}
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Running Evaluation:**
```bash
adk eval brand_studio_agent tests/integration.evalset.json \
  --config_file_path=tests/eval_config.json \
  --print_detailed_results
```

**Acceptance Criteria:**
- ✅ Evaluation files created
- ✅ Test cases defined
- ✅ `adk eval` runs successfully
- ✅ Pass/fail metrics work

---

### Task 3.3: Enable ADK Web UI Debugging

**Files to Modify:**
- Documentation

**Setup:**
```bash
# Start web UI
adk web --log_level DEBUG

# Open browser to http://localhost:8000
# Select agent and test
```

**Acceptance Criteria:**
- ✅ Can run `adk web`
- ✅ Agents appear in dropdown
- ✅ Can test agents interactively
- ✅ Can create eval sets from UI

---

## Phase 4: Deployment Readiness

**Timeline:** Week 5
**Priority:** 🔴 HIGH
**Goal:** Make project deployable to Agent Engine

### Task 4.1: Create Deployment Configuration

**Files to Create:**
- `.agent_engine_config.json`
- `scripts/deploy.sh`
- `scripts/setup_gcp.sh`

**.agent_engine_config.json:**
```json
{
    "min_instances": 0,
    "max_instances": 5,
    "resource_limits": {
        "cpu": "2",
        "memory": "4Gi"
    },
    "timeout": "600s"
}
```

**scripts/deploy.sh:**
```bash
#!/bin/bash
set -e

# Check environment
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT not set"
    exit 1
fi

# Deploy to Agent Engine
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  brand_studio_agent \
  --agent_engine_config_file=.agent_engine_config.json

echo "✅ Deployment complete!"
```

**Acceptance Criteria:**
- ✅ Config files created
- ✅ Deployment script works
- ✅ Setup script enables APIs

---

### Task 4.2: Restructure for Deployment

**Current structure:**
```
src/
├── agents/
├── tools/
├── rag/
└── ...
```

**Deployment structure:**
```
brand_studio_agent/
├── agent.py           # Entry point with root_agent
├── requirements.txt   # Pinned versions
├── .env              # Environment config
├── .agent_engine_config.json
└── tools/            # Custom tools
```

**agent.py:**
```python
"""
Brand Studio Agent - Production Entry Point

This file is the root agent definition for deployment.
"""

import os
import vertexai
from google.adk.agents import Agent
from orchestrator import create_orchestrator

# Initialize Vertex AI
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

# Create and export root agent
root_agent = create_orchestrator()
```

**Acceptance Criteria:**
- ✅ Deployment structure created
- ✅ agent.py exports root_agent
- ✅ Requirements pinned
- ✅ Ready for `adk deploy`

---

### Task 4.3: Test Deployment

**Steps:**
1. Deploy to Agent Engine:
   ```bash
   ./scripts/deploy.sh
   ```

2. Test deployed agent:
   ```python
   import vertexai
   from vertexai import agent_engines

   vertexai.init(project='your-project', location='us-central1')

   # List agents
   agents = list(agent_engines.list())
   print(f"Found {len(agents)} deployed agents")

   # Get agent
   agent = agents[0]

   # Test
   async for event in agent.async_stream_query(
       message="Generate healthcare app brand names",
       user_id="test_user"
   ):
       print(event)
   ```

3. Monitor in Cloud Console

4. Cleanup:
   ```python
   agent_engines.delete(
       resource_name=agent.resource_name,
       force=True
   )
   ```

**Acceptance Criteria:**
- ✅ Deployment succeeds
- ✅ Agent responds correctly
- ✅ Logs appear in Cloud Logging
- ✅ Can cleanup successfully

---

## Testing Strategy

### Unit Tests (Per Task)

Each task should include:
- Unit tests for new code
- Integration tests for modified code
- Regression tests for existing functionality

### Integration Tests (Per Phase)

End of each phase:
- Run full workflow tests
- Verify all agents work together
- Check memory/session persistence
- Validate tool functionality

### End-to-End Tests (Final)

Before production:
- Complete brand generation workflow
- Multiple user sessions
- Long conversations (context compaction)
- Cross-session memory retrieval
- ADK evaluation suite (all tests pass)

---

## Rollback Procedures

### Git Strategy

1. Create migration branch:
   ```bash
   git checkout -b adk-migration/phase-1
   ```

2. Commit after each task:
   ```bash
   git commit -m "Task 1.1: Setup real ADK dependencies"
   ```

3. Tag each phase:
   ```bash
   git tag -a phase-1-complete -m "Phase 1: Critical Foundation Complete"
   ```

### Rollback Steps

If issues arise:
```bash
# Rollback to last working state
git checkout <previous-tag>

# Or revert specific commit
git revert <commit-hash>
```

### Feature Flags

Consider adding feature flags for gradual rollout:
```python
USE_REAL_ADK = os.getenv("USE_REAL_ADK", "false") == "true"

if USE_REAL_ADK:
    from google.adk.agents import Agent
else:
    from src.utils.mock_adk import LlmAgent as Agent
```

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] All agents use real ADK
- [ ] No mock ADK imports
- [ ] Workflow patterns implemented
- [ ] All tests passing
- [ ] No regression in functionality

### Phase 2 Success Criteria
- [ ] All tools wrapped with FunctionTool
- [ ] DatabaseSessionService integrated
- [ ] Memory tools working
- [ ] Context compaction active

### Phase 3 Success Criteria
- [ ] LoggingPlugin integrated
- [ ] ADK web UI working
- [ ] Evaluation suite created
- [ ] All eval tests passing

### Phase 4 Success Criteria
- [ ] Deployment config created
- [ ] Successfully deployed to Agent Engine
- [ ] Production testing complete
- [ ] Monitoring setup

---

## Resources

### Documentation
- [ADK Documentation](https://google.github.io/adk-docs/)
- [Agent Patterns Guide](https://google.github.io/adk-docs/agents/)
- [Deployment Guide](https://google.github.io/adk-docs/deploy/)
- Coursework in `/coursework` directory

### Support
- [ADK GitHub Issues](https://github.com/google/adk)
- [Kaggle Discord](https://www.kaggle.com/discussions)
- Course examples in `/coursework/*.py`

---

## Next Steps

1. **Review this plan** with team
2. **Setup project board** to track tasks
3. **Start Phase 1, Task 1.1** (Setup Real ADK)
4. **Commit frequently** with clear messages
5. **Test thoroughly** at each step
6. **Document learnings** for future reference

---

**Document Version:** 1.0
**Last Updated:** November 18, 2025
**Author:** Claude Code
**Status:** ✅ Ready for Implementation
