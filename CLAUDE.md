# AI Brand Studio - Agent Architecture Guide

This document provides a comprehensive guide to the ADK-based multi-agent architecture.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Agent Design Patterns](#agent-design-patterns)
- [Workflow Orchestration](#workflow-orchestration)
- [Tools and Functions](#tools-and-functions)
- [Memory and Context Management](#memory-and-context-management)
- [Observability](#observability)
- [Development Guide](#development-guide)

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     App (Context Compaction)                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              BrandStudioOrchestrator                     ││
│  │              (SequentialAgent)                          ││
│  │                                                          ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ││
│  │  │   Research   │→ │ Refinement   │→ │  SEO Agent   │  ││
│  │  │    Agent     │  │     Loop     │  └──────────────┘  ││
│  │  └──────────────┘  │ (LoopAgent)  │         ↓          ││
│  │                    │              │  ┌──────────────┐  ││
│  │                    │  ┌────────┐  │  │ Story Agent  │  ││
│  │                    │  │ Name   │←┐│  └──────────────┘  ││
│  │                    │  │ Gen    │ ││                     ││
│  │                    │  └────────┘ ││                     ││
│  │                    │      ↓       ││                     ││
│  │                    │  ┌────────┐ ││                     ││
│  │                    │  │Validate│ ││                     ││
│  │                    │  └────────┘ ││                     ││
│  │                    │      ↓       ││                     ││
│  │                    │  Loop ≤ 3x  ││                     ││
│  │                    └──────────────┘│                     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  Plugins: [LoggingPlugin]                                   │
└─────────────────────────────────────────────────────────────┘
          ↓
    InMemoryRunner
```

### Technology Stack

- **Framework**: Google Agent Development Kit (ADK) v1.18.0
- **LLM**: Gemini 2.5 Flash Lite (default)
- **Orchestration**: SequentialAgent + LoopAgent patterns
- **Tools**: FunctionTool wrappers for domain/trademark checking
- **RAG**: Custom brand knowledge retrieval
- **Observability**: ADK LoggingPlugin + Custom BrandStudioLogger

## Agent Design Patterns

### 1. Sequential Agent Pattern

Used for: Main orchestration pipeline

**Implementation**: `src/agents/orchestrator.py`

```python
from google.adk.agents import SequentialAgent

def create_brand_pipeline(
    research_agent,
    refinement_loop,
    seo_agent,
    story_agent
):
    """Create sequential workflow."""
    return SequentialAgent(
        name="BrandPipeline",
        agents=[
            research_agent,
            refinement_loop,
            seo_agent,
            story_agent
        ]
    )
```

**Advantages**:
- Linear, predictable flow
- Easy to debug and trace
- Built-in state passing between agents

### 2. Loop Agent Pattern

Used for: Iterative refinement (name generation + validation)

**Implementation**: `src/agents/orchestrator.py`

```python
from google.adk.agents import LoopAgent

def create_refinement_loop(
    name_generator,
    validation_agent,
    max_iterations=3
):
    """Create iterative refinement loop."""
    return LoopAgent(
        name="RefinementLoop",
        agents=[name_generator, validation_agent],
        max_iterations=max_iterations
    )
```

**Advantages**:
- Automatic iteration handling
- Quality improvement through feedback
- Configurable exit conditions

### 3. Base Agent Factory Pattern

Used for: Creating consistently configured agents

**Implementation**: `src/agents/base_adk_agent.py`

```python
def create_brand_agent(
    name: str,
    instruction: str,
    model_name: str = "gemini-2.5-flash-lite",
    tools: List = None,
    sub_agents: List = None
) -> Agent:
    """Factory for creating ADK agents with standard config."""
    
    # Configure retry logic
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    # Create model
    model = Gemini(
        model=model_name,
        retry_options=retry_config
    )
    
    # Create agent
    return Agent(
        name=name,
        model=model,
        instruction=instruction,
        tools=tools or []
    )
```

**Advantages**:
- Consistent retry configuration
- Centralized model management
- Easy to modify global settings

## Workflow Orchestration

### Main Orchestration Flow

**File**: `src/agents/orchestrator.py:create_orchestrator()`

```python
def create_orchestrator() -> SequentialAgent:
    """
    Create the main orchestrator agent.
    
    Flow:
    1. Research: Industry analysis and competitive landscape
    2. Refinement Loop: Name generation + validation (≤3 iterations)
    3. SEO: Meta optimization and keyword targeting
    4. Story: Brand narrative and positioning
    """
    # Create individual agents
    research = create_research_agent()
    name_gen = create_name_generator()
    validator = create_validation_agent()
    seo = create_seo_agent()
    story = create_story_agent()
    
    # Create refinement loop
    refinement_loop = LoopAgent(
        name="RefinementLoop",
        agents=[name_gen, validator],
        max_iterations=3
    )
    
    # Create main pipeline
    orchestrator = SequentialAgent(
        name="BrandStudioOrchestrator",
        agents=[research, refinement_loop, seo, story]
    )
    
    return orchestrator
```

### Agent Responsibilities

#### Research Agent
- **Purpose**: Industry analysis and competitive insights
- **Tools**: `google_search` (built-in ADK tool)
- **Output**: Market trends, competitor analysis, target audience insights

#### Name Generator
- **Purpose**: Generate 20-50 brand name candidates
- **Tools**: RAG retrieval (`brand_retrieval_tool`)
- **Output**: List of creative, relevant brand names

#### Validation Agent
- **Purpose**: Check domain availability and trademark clearance
- **Tools**: `domain_checker_tool`, `trademark_checker_tool`
- **Output**: Validation results with availability status and risk levels

#### SEO Agent
- **Purpose**: Optimize for search engines
- **Tools**: None (uses LLM reasoning)
- **Output**: Meta title, description, keywords, SEO score

#### Story Agent
- **Purpose**: Create brand narrative
- **Tools**: None (uses LLM reasoning)
- **Output**: Brand story, taglines, positioning statements

## Tools and Functions

### FunctionTool Pattern

All custom tools use the ADK `FunctionTool` wrapper with `ToolContext`:

```python
from google.adk.tools import FunctionTool, ToolContext

def check_domain_availability(
    name: str,
    context: ToolContext  # Required for session access
) -> dict:
    """
    Check domain availability for a brand name.
    
    Args:
        name: Brand name to check
        context: ADK tool context (provides session state)
    
    Returns:
        dict: Availability status for .com, .ai, .io domains
    """
    # Implementation
    results = {}
    for tld in ['.com', '.ai', '.io']:
        results[tld] = check_tld_availability(name, tld)
    
    return results

# Wrap as FunctionTool
domain_checker_tool = FunctionTool(check_domain_availability)
```

### Available Tools

1. **domain_checker_tool**
   - File: `src/tools/domain_checker.py`
   - Checks: .com, .ai, .io, .co availability
   - Rate limiting: Yes

2. **trademark_checker_tool**
   - File: `src/tools/trademark_checker.py`
   - Source: USPTO database search
   - Returns: Risk level (low, medium, high, critical)

3. **brand_retrieval_tool**
   - File: `src/rag/brand_retrieval.py`
   - Purpose: RAG-enhanced name generation
   - Index: Brand naming examples and patterns

4. **google_search** (Built-in ADK)
   - Used by: Research agent
   - Purpose: Web search for industry insights

### Creating Custom Tools

```python
# 1. Define function with ToolContext
def my_custom_tool(
    param1: str,
    param2: int,
    context: ToolContext
) -> dict:
    """
    Tool description for LLM.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        context: Tool context (auto-provided)
    
    Returns:
        dict: Result data
    """
    # Access session if needed
    session_id = context.session_id
    
    # Implementation
    result = do_work(param1, param2)
    
    return {"result": result}

# 2. Wrap as FunctionTool
my_tool = FunctionTool(my_custom_tool)

# 3. Add to agent
agent = create_brand_agent(
    name="MyAgent",
    instruction="Use my_custom_tool when needed",
    tools=[my_tool]
)
```

## Memory and Context Management

### Context Compaction

Prevents context overflow in long conversations:

```python
from google.adk.apps.app import App, EventsCompactionConfig

app = App(
    name="BrandStudioApp",
    root_agent=orchestrator,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,  # Compact every 5 invocations
        overlap_size=1,         # Keep 1 previous turn for context
    )
)
```

**How it works**:
- Every 5 agent invocations, context is summarized
- Keeps last 1 turn for continuity
- Prevents token limit errors
- Maintains conversation coherence

### Session Management

Current implementation uses `InMemoryRunner` (stateless):

```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(app=app)
result = runner.run(user_prompt)
```

**For persistent sessions** (future enhancement):

```python
from google.adk.runners import DatabaseSessionService
from google.adk.runners import InMemoryRunner

# Create session service
session_service = DatabaseSessionService(
    db_url="sqlite:///sessions.db"
)

# Create runner with sessions
runner = InMemoryRunner(
    app=app,
    session_service=session_service
)

# Run with session ID
result = runner.run(
    user_prompt,
    session_id="user-123"
)
```

### Memory Tools (Deferred)

ADK provides memory tools for long-term context:

```python
from google.adk.tools import preload_memory, load_memory

# Preload context at start
preload_memory(
    session_id="user-123",
    content="User preferences: likes playful brand names..."
)

# Load context during execution
context = load_memory(session_id="user-123")
```

Not yet implemented - will be added when `DatabaseSessionService` is integrated.

## Observability

### Logging Architecture

Two-layer logging system:

1. **ADK LoggingPlugin**: Built-in observability
2. **BrandStudioLogger**: Custom structured logging

```python
from google.adk.plugins.logging_plugin import LoggingPlugin
from src.infrastructure.logging import get_logger

# ADK logging (automatic)
app = App(
    name="BrandStudioApp",
    root_agent=orchestrator,
    plugins=[LoggingPlugin()]
)

# Custom logging
logger = get_logger()
logger.log_agent_action(
    agent_name="name_generator",
    action_type="generate",
    duration_ms=1234,
    session_id="xyz"
)
```

### Log Levels

- **DEBUG**: Detailed execution traces
- **INFO**: Normal operations (default)
- **WARNING**: Recoverable issues
- **ERROR**: Failures requiring attention

### Monitoring Metrics

Custom logger tracks:
- Agent execution duration
- Tool call success/failure rates
- Context compaction events
- Error rates by agent

Access via Cloud Logging:

```bash
gcloud logging read "resource.type=ml_job" \
  --filter="labels.agent_name=BrandStudioOrchestrator" \
  --limit=100
```

## Development Guide

### Adding a New Agent

1. **Create agent file**: `src/agents/my_agent.py`

```python
from src.agents.base_adk_agent import create_brand_agent

def create_my_agent():
    """Create my custom agent."""
    return create_brand_agent(
        name="MyAgent",
        instruction="""
        You are a specialized agent for [purpose].
        
        Your task is to:
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        
        Output format: [description]
        """,
        model_name="gemini-2.5-flash-lite",
        tools=[...],  # Optional tools
    )
```

2. **Export from __init__.py**:

```python
# src/agents/__init__.py
from src.agents.my_agent import create_my_agent

__all__ = [..., 'create_my_agent']
```

3. **Add to orchestrator** (if needed):

```python
# src/agents/orchestrator.py
my_agent = create_my_agent()

orchestrator = SequentialAgent(
    name="BrandStudioOrchestrator",
    agents=[research, my_agent, refinement_loop, seo, story]
)
```

4. **Write tests**:

```python
# tests/test_my_agent.py
def test_my_agent_creation():
    agent = create_my_agent()
    assert agent.name == "MyAgent"

def test_my_agent_execution():
    from google.adk.runners import InMemoryRunner
    
    agent = create_my_agent()
    runner = InMemoryRunner(agent=agent)
    result = runner.run("Test input")
    
    assert result is not None
```

### Modifying Agent Instructions

Agent behavior is controlled by instruction prompts:

```python
instruction = """
You are a brand name generator specialized in [industry].

TASK:
Generate 20-50 creative brand names based on the user's brief.

GUIDELINES:
- Names should be memorable and pronounceable
- Avoid generic terms like "app", "tech", "hub"
- Consider the target audience and brand personality
- Include a mix of invented words and compound names

OUTPUT FORMAT:
Return a JSON array of brand names:
{
  "names": ["Name1", "Name2", ...],
  "reasoning": "Brief explanation of naming approach"
}
"""
```

**Tips**:
- Be specific about task and format
- Use structured output (JSON) for consistency
- Include examples if helpful
- Set clear constraints

### Testing Changes

```bash
# Unit tests
pytest tests/test_my_agent.py -v

# Integration test
python -m src.main

# ADK evaluation
adk eval brand_studio_agent tests/integration.evalset.json

# Interactive debugging
adk web brand_studio_agent --log_level DEBUG
```

### Debugging Tips

1. **Enable verbose logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use ADK web UI**:
   ```bash
   adk web brand_studio_agent --log_level DEBUG
   ```

3. **Inspect intermediate outputs**:
   ```python
   # Add callbacks to agents
   def after_agent_callback(agent, result):
       print(f"{agent.name} result: {result}")
   
   agent.after_agent_callback = after_agent_callback
   ```

4. **Check tool execution**:
   ```python
   # Test tool directly
   from src.tools.domain_checker import check_domain_availability
   result = check_domain_availability("testname", context=None)
   ```

## Best Practices

### Agent Design

1. **Single Responsibility**: Each agent should have one clear purpose
2. **Clear Instructions**: Be explicit about task, format, and constraints
3. **Error Handling**: Agents should handle failures gracefully
4. **Output Structure**: Use JSON for structured data

### Tool Development

1. **ToolContext**: Always include `context: ToolContext` parameter
2. **Type Hints**: Use type hints for all parameters
3. **Docstrings**: Document purpose, args, and returns
4. **Error Handling**: Return error info in result dict, don't raise exceptions
5. **Rate Limiting**: Implement rate limiting for external APIs

### Orchestration

1. **Keep It Simple**: Start with SequentialAgent, add complexity only when needed
2. **Limit Loops**: Set max_iterations to prevent infinite loops
3. **State Management**: Pass data between agents via output_key
4. **Testing**: Test each agent independently, then test the full pipeline

### Performance

1. **Model Selection**: Use faster models (flash-lite) for simple tasks
2. **Context Compaction**: Enable for long conversations
3. **Parallel Execution**: Use async patterns for independent operations
4. **Caching**: Cache expensive operations (RAG lookups, API calls)

## Architecture Evolution

### Current State (Phase 3 Complete)
- ✅ ADK agent migration complete
- ✅ Sequential and loop orchestration
- ✅ FunctionTool wrappers
- ✅ LoggingPlugin integration
- ✅ Context compaction enabled
- ✅ Deployment-ready structure

### Future Enhancements

#### Phase 4+ (Optional)
- [ ] DatabaseSessionService for persistent sessions
- [ ] Memory tools for long-term context
- [ ] Parallel agent execution for independent tasks
- [ ] Custom evaluation metrics
- [ ] A2A (agent-to-agent) communication
- [ ] Multi-modal inputs (images, documents)

#### Advanced Patterns

1. **Parallel Agent Execution**:
   ```python
   from google.adk.agents import ParallelAgent
   
   parallel = ParallelAgent(
       name="ParallelAnalysis",
       agents=[seo_agent, story_agent]
   )
   ```

2. **Conditional Routing**:
   ```python
   def router_function(context):
       if context.get("industry") == "healthcare":
           return healthcare_agent
       return general_agent
   
   router = ConditionalAgent(
       name="Router",
       router_function=router_function,
       agents=[healthcare_agent, general_agent]
   )
   ```

3. **Human-in-the-Loop**:
   ```python
   def human_approval_required(result):
       # Show result to human
       approved = get_human_input(result)
       return approved
   
   agent.after_agent_callback = human_approval_required
   ```

## References

- **ADK Documentation**: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit
- **Gemini API**: https://ai.google.dev/docs
- **Migration Plan**: `docs/ADK_MIGRATION_PLAN.md`
- **Testing Guide**: `TESTING.md`
