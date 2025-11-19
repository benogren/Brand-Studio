# AI Brand Studio

**Interactive AI-powered brand identity creation through conversational chat**

Powered by Google Agent Development Kit (ADK) and Gemini models.

[![Deployment Status](https://img.shields.io/badge/Deployment-Ready-success)](DEPLOYMENT.md)
[![ADK Version](https://img.shields.io/badge/ADK-1.18.0-blue)](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)](https://ai.google.dev/gemini-api/docs)

## Overview

AI Brand Studio creates complete brand identities through a simple conversational interface. Just answer a few questions and the system guides you through:

- **Research** - Automatic industry analysis and competitive insights
- **Name Generation** - Creative brand names with multiple strategies
- **Iterative Refinement** - Provide feedback and regenerate until perfect
- **Validation** - Domain availability, trademark clearance, SEO analysis
- **Brand Story** - Taglines, brand narrative, and value proposition

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your GOOGLE_CLOUD_PROJECT

# 3. Run the interactive brand studio
python -m src.cli
```

That's it! The system will guide you through everything.

## How It Works

### Interactive Conversation Flow

```
1. Tell us about your product
   → What does it do?
   → Who is it for?
   → Brand personality?
   → Industry?

2. We research your industry automatically
   → ✓ Research complete

3. Generate brand names
   → How many names? (default: 15)
   → [Names displayed with rationale]
   
4. Your choice:
   → Generate more with feedback?
   → Validate selected names?
   → Quit?

5. Provide feedback (optional)
   → What feedback? "More tech-focused"
   → Names you liked? "KinetiCore, FlowFit"
   → [New names generated]

6. Validate names
   → Enter names: "Name1, Name2, Name3"
   → [Checking domains, trademarks, SEO...]
   → [Results displayed]

7. Create brand story
   → Final name? "KinetiCore"
   → [Generating taglines, story, value prop...]
   → ✓ Brand identity complete!
```

## Example Session

```
$ python -m src.cli

AI BRAND STUDIO - INTERACTIVE MODE
====================================

Welcome! I'll help you create a complete brand identity.

What does your product do? AI fitness tracking app
Who is it for? Health-conscious millennials  
Choose personality: 3 (innovative)
Industry: fitness

Researching your industry...
✓ Research complete

Generating 15 brand names...

GENERATED NAMES
- KinetiCore (portmanteau: kinetic + core)
- FlowMetrics (descriptive: flow state + metrics)
- SynapseRun (invented: brain + movement)
[... 12 more names ...]

What next?
  1. Generate more with feedback
  2. Validate names
  3. Quit

Choice: 2

Enter names to validate: KinetiCore, FlowMetrics

Validating...
✓ KinetiCore
  - kineticore.com: Available
  - kineticore.ai: Available  
  - Trademark: Low risk
  - SEO: Strong potential

Continue to brand story? y

Final name: KinetiCore

BRAND IDENTITY: KinetiCore
- Taglines: "Move Smarter, Live Stronger" [+ 4 more]
- Brand Story: [200-300 word narrative]
- Value Prop: "AI-powered fitness tracking..."

✓ Complete!
```

## Architecture

Built with Google ADK multi-agent system:

```
         Interactive CLI
              │
              ▼
    ┌─────────────────┐
    │ Research Agent  │ → Industry analysis
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Name Generator  │ → Creative names
    └────────┬────────┘
             │
       User Feedback? ──┐
             │          │
             │    ┌─────▼─────┐
             │    │ Regenerate│
             │    └─────┬─────┘
             │          │
             ▼◄─────────┘
    ┌─────────────────┐
    │ Validation      │ → Domain + Trademark + SEO
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Story Agent     │ → Taglines + Story + Value Prop
    └─────────────────┘
```

### Agents

- **Research Agent** - Analyzes trends, competitors, terminology
- **Name Generator** - Uses multiple strategies: portmanteau, invented, descriptive, acronym
- **Validation Agent** - Checks domains (10+ TLDs), trademarks (USPTO), SEO potential
- **Story Agent** - Creates brand narrative, taglines, positioning

### Tools

- **Domain Checker** - WHOIS lookups for .com, .ai, .io, .so, .app, .co, .is, .me, .net, .to
- **Trademark Checker** - USPTO database search with risk assessment
- **RAG Retrieval** - Similar brand database for inspiration

## Configuration

### Required Environment Variables

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=1
```

### Optional

```bash
GOOGLE_CLOUD_LOCATION=us-central1
NAMECHEAP_API_KEY=your-key     # Enhanced domain checks
USPTO_API_KEY=your-key          # Enhanced trademark search
```

## Features

### Iterative Refinement

- Generate names
- Provide feedback: "More playful", "Shorter", "Tech-focused"
- Keep names you like
- Generate more based on feedback
- Repeat unlimited times

### Comprehensive Validation

- **Domain**: Checks 10+ TLDs
- **Trademark**: USPTO database search
- **SEO**: Keyword analysis
- **Search**: Collision detection

### Complete Brand Identity

- 5 tagline options (5-8 words, action-oriented)
- Brand story (200-300 words)
- Value proposition (20-30 words)

## Project Structure

```
Brand-Agent/
├── src/
│   ├── cli.py                 # Main interactive CLI ⭐
│   ├── agents/                # ADK agents
│   │   ├── research_agent.py
│   │   ├── name_generator.py
│   │   ├── validation_agent.py
│   │   └── story_agent.py
│   ├── tools/                 # Agent tools
│   │   ├── domain_checker.py
│   │   ├── trademark_checker.py
│   │   └── rag_retrieval.py
│   └── infrastructure/
│       └── session_manager.py
├── coursework/                # ADK learning materials
├── tests/
└── requirements.txt
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Agents

```python
from src.agents.base_adk_agent import create_brand_agent

agent = create_brand_agent(
    name="MyAgent",
    instruction="Your instructions...",
    tools=[my_tool]
)
```

### Adding New Tools

```python
from google.adk.tools import FunctionTool

def my_tool(param: str) -> dict:
    """Tool description for LLM."""
    return {"result": "data"}

tool = FunctionTool(my_tool)
```

## Troubleshooting

**"GOOGLE_CLOUD_PROJECT not set"**
- Check `.env` file has `GOOGLE_CLOUD_PROJECT=your-project-id`

**Authentication errors**
```bash
gcloud auth application-default login
```

**Domain/trademark checks failing**
- Public APIs may be rate-limited
- System continues with simulated results for development

## Deployment

### Deployment-Ready Configuration

This project is configured for deployment to **Vertex AI Agent Engine**:

✅ **Deployment Status:** Ready
✅ **Configuration:** Complete
✅ **Verification:** All checks passed

```bash
# Verify deployment readiness
python verify_deployment_ready.py

# Deploy to Vertex AI Agent Engine
cd brand_studio_agent
# See DEPLOYMENT.md for detailed deployment instructions
```

**Deployment Features:**
- Auto-scaling (0-5 instances)
- Resource optimization (2 CPU, 4Gi memory)
- Health checks enabled
- Cloud Logging integration
- Production-ready configuration

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment guide.

## Documentation

- `DEPLOYMENT.md` - Production deployment guide ⭐ NEW
- `TESTING.md` - Testing strategies and evaluation
- `CLAUDE.md` - Agent architecture and patterns
- `coursework/` - ADK learning materials (Days 1-5)

## Tech Stack

- **Google ADK** - Agent Development Kit
- **Gemini 2.0** - Language models
- **Python WHOIS** - Domain availability
- **USPTO API** - Trademark search

## License

MIT

---

**Start creating your brand identity:**
```bash
python -m src.cli
```
