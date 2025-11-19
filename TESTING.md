# Testing Guide - AI Brand Studio

This guide covers testing strategies for the ADK-based multi-agent system.

## Table of Contents

- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [ADK Evaluation Framework](#adk-evaluation-framework)
- [Performance Testing](#performance-testing)
- [Manual Testing](#manual-testing)

## Unit Testing

### Running Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_name_generator.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Structure

```
tests/
├── test_orchestrator.py         # Orchestrator workflow tests
├── test_name_generator.py       # Name generation tests
├── test_validation_agent.py     # Validation logic tests
├── test_domain_checker.py       # Domain checking tool tests
├── test_trademark_checker.py    # Trademark checking tool tests
├── test_context_compaction.py   # Context management tests
└── test_logging.py              # Logging integration tests
```

### Writing Tests

Example test for an agent:

```python
import pytest
from src.agents.name_generator import create_name_generator

def test_name_generator_creation():
    """Test that name generator agent is created correctly."""
    agent = create_name_generator()
    assert agent.name == "NameGenerator"
    assert agent.tools is not None

def test_name_generation_flow():
    """Test name generation with sample input."""
    from google.adk.runners import InMemoryRunner
    
    agent = create_name_generator()
    runner = InMemoryRunner(agent=agent)
    
    result = runner.run(
        "Generate brand names for an AI-powered fitness app"
    )
    
    assert result is not None
    # Add specific assertions based on expected output
```

## Integration Testing

### Test Scenarios

Integration tests validate the entire multi-agent workflow:

```bash
pytest tests/integration/ -v
```

Key scenarios:
1. **Full Pipeline**: Research → Names → Validation → SEO → Story
2. **Refinement Loop**: Name generation with validation feedback
3. **Error Handling**: Agent failures and recovery
4. **Tool Integration**: Domain/trademark checking accuracy

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific scenario
pytest tests/integration/test_full_pipeline.py

# Skip slow tests
pytest -m "not slow"
```

## ADK Evaluation Framework

The ADK evaluation framework provides comprehensive agent testing with metrics and quality scores.

### Evaluation Configuration

**File**: `tests/eval_config.json`

```json
{
  "evaluation_criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  },
  "custom_evaluators": [
    {
      "name": "name_quality_evaluator",
      "weight": 0.3
    },
    {
      "name": "validation_accuracy_evaluator",
      "weight": 0.3
    }
  ],
  "thresholds": {
    "minimum_passing_score": 0.7,
    "excellent_score": 0.9
  }
}
```

### Evaluation Test Sets

**File**: `tests/integration.evalset.json`

Contains 12 comprehensive test cases covering:
- Healthcare apps (mental wellness, telemedicine)
- Fintech apps (expense tracking, crypto wallets)
- E-commerce (inventory management, sustainable fashion)
- Food tech (meal planning)
- Education (kids learning apps)
- B2B SaaS (sales platforms)
- Lifestyle (fitness, productivity, travel)

### Running Evaluations

```bash
# Run all evaluation tests
adk eval brand_studio_agent tests/integration.evalset.json \
  --config_file_path=tests/eval_config.json \
  --print_detailed_results

# Run specific test cases
adk eval brand_studio_agent \
  tests/integration.evalset.json:healthcare_mental_wellness_app,fintech_expense_tracker \
  --config_file_path=tests/eval_config.json

# Save results to Cloud Storage
adk eval brand_studio_agent tests/integration.evalset.json \
  --config_file_path=tests/eval_config.json \
  --eval_storage_uri=gs://your-bucket/eval-results
```

### Understanding Evaluation Metrics

#### Built-in Metrics

1. **tool_trajectory_avg_score** (target: 1.0)
   - Measures correct tool usage and sequencing
   - 1.0 = perfect tool execution
   - <0.8 = tool usage issues

2. **response_match_score** (target: 0.8)
   - Compares output against expected results
   - Uses semantic similarity and structure matching
   - 0.8+ = high-quality outputs

#### Custom Evaluators

1. **name_quality_evaluator**
   
   Evaluates brand names across 4 dimensions:
   - **Pronounceability** (0-1): Vowel ratio, consonant clusters, length
   - **Memorability** (0-1): Distinctiveness, phonetic patterns
   - **Industry Relevance** (0-1): Keyword matching
   - **Uniqueness** (0-1): Avoids generic terms
   
   Example usage:
   ```python
   from tests.evaluators.name_quality import evaluate_name_quality
   
   names = ["FitFlow", "HealthHub", "WellnessAI"]
   result = evaluate_name_quality(
       names=names,
       industry="fitness",
       threshold=0.7
   )
   print(f"Overall score: {result['overall_score']}")
   print(f"Pass rate: {result['pass_rate']}")
   ```

2. **validation_accuracy_evaluator**
   
   Measures domain/trademark check accuracy:
   - **Domain check success rate** (target: 95%+)
   - **Trademark check success rate** (target: 95%+)
   - **Validation completeness** (target: 90%+)
   
   Example usage:
   ```python
   from tests.evaluators.validation_accuracy import evaluate_validation_accuracy
   
   validation_results = {
       "domain_availability": {
           "FitFlow": {"com": "available", "ai": "taken"},
           "HealthHub": {"com": "taken", "io": "available"}
       },
       "trademark_results": {
           "FitFlow": {"risk_level": "low"},
           "HealthHub": {"risk_level": "high"}
       }
   }
   
   result = evaluate_validation_accuracy(validation_results)
   print(f"Overall accuracy: {result['overall_accuracy']}")
   ```

### Interpreting Results

Evaluation output example:

```
========================================
Evaluation Results
========================================

Test Case: healthcare_mental_wellness_app
  ✓ tool_trajectory_avg_score: 1.0 (passed)
  ✓ response_match_score: 0.85 (passed)
  ✓ name_quality_evaluator: 0.78 (passed)
  ✓ validation_accuracy_evaluator: 0.96 (passed)
  
  Overall Score: 0.88 (EXCELLENT)
  
  Details:
  - Generated 32 brand names
  - 28 names passed quality threshold (87.5% pass rate)
  - 5 domains available (.com)
  - 12 names with low trademark risk
  - SEO score average: 74/100

Test Case: fintech_expense_tracker
  ...

========================================
Summary
========================================
Total Tests: 12
Passed: 11 (91.7%)
Failed: 1 (8.3%)
Average Score: 0.84
```

### Creating Custom Evaluators

Create a new evaluator in `tests/evaluators/`:

```python
class CustomEvaluator:
    """Custom evaluator for specific metrics."""
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
    
    def evaluate(self, agent_output: dict) -> dict:
        """
        Evaluate agent output.
        
        Returns:
            dict with 'score' (0-1) and 'passed' (bool)
        """
        # Your evaluation logic here
        score = self._calculate_score(agent_output)
        
        return {
            'score': score,
            'passed': score >= self.threshold,
            'details': {...}
        }
```

Register in `tests/eval_config.json`:

```json
{
  "custom_evaluators": [
    {
      "name": "custom_evaluator",
      "module": "tests.evaluators.custom_evaluator",
      "class": "CustomEvaluator",
      "weight": 0.2
    }
  ]
}
```

## Performance Testing

### Latency Testing

Measure end-to-end latency:

```python
import time
from google.adk.runners import InMemoryRunner
from src.agents.orchestrator import create_orchestrator

orchestrator = create_orchestrator()
runner = InMemoryRunner(agent=orchestrator)

start = time.time()
result = runner.run("Create a brand for a fitness app")
duration = time.time() - start

print(f"Total duration: {duration:.2f}s")
```

### Load Testing

Test concurrent requests (requires deployment):

```python
import asyncio
from google.cloud import aiplatform

async def test_load(num_requests=10):
    agent_engine = aiplatform.ReasoningEngine("brand-studio-agent")
    
    async def make_request(i):
        start = time.time()
        response = await agent_engine.query_async(
            f"Create a brand for app #{i}"
        )
        duration = time.time() - start
        return duration
    
    tasks = [make_request(i) for i in range(num_requests)]
    durations = await asyncio.gather(*tasks)
    
    print(f"Average latency: {sum(durations)/len(durations):.2f}s")
    print(f"Max latency: {max(durations):.2f}s")
    print(f"Min latency: {min(durations):.2f}s")

asyncio.run(test_load())
```

## Manual Testing

### Using ADK Web UI

Launch interactive interface:

```bash
adk web brand_studio_agent --log_level DEBUG --reload
```

Access at: http://localhost:8000

Features:
- **Interactive Testing**: Send queries and see real-time responses
- **Execution Logs**: View detailed agent execution traces
- **Tool Inspection**: See tool calls and outputs
- **Eval Set Creation**: Save conversations as test cases
- **Workflow Visualization**: See agent orchestration flow

### Testing CLI

```bash
# Interactive mode
python -m src.cli

# Direct input
python -m src.cli \
  --product "AI fitness coaching app" \
  --audience "Fitness enthusiasts 25-40" \
  --personality innovative \
  --json output.json \
  --verbose

# Review output
cat output.json | jq
```

### Testing Individual Agents

Test agents in isolation:

```python
from google.adk.runners import InMemoryRunner
from src.agents.research_agent import create_research_agent

# Test research agent
research_agent = create_research_agent()
runner = InMemoryRunner(agent=research_agent)

result = runner.run(
    "Research the fitness coaching industry for Gen Z audience"
)
print(result)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run unit tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Run ADK evaluations
      env:
        GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT }}
      run: |
        adk eval brand_studio_agent tests/integration.evalset.json \
          --config_file_path=tests/eval_config.json
```

## Test Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: All critical paths covered
- **ADK Evaluations**: 90%+ pass rate
- **Performance**: <60s end-to-end latency (P95)

## Troubleshooting Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Authentication Failures**
   ```bash
   gcloud auth application-default login
   ```

3. **Rate Limiting**
   - Add delays between test runs
   - Use mock responses for unit tests
   - Test with fewer eval cases during development

## Best Practices

1. **Use Fixtures**: Create reusable test fixtures for common setups
2. **Mock External Calls**: Mock API calls for faster, reliable tests
3. **Test Edge Cases**: Include error conditions and edge cases
4. **Maintain Eval Sets**: Keep evaluation test cases up to date
5. **Monitor Metrics**: Track evaluation scores over time
6. **Document Tests**: Add docstrings explaining test purpose

## Additional Resources

- [ADK Evaluation Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
