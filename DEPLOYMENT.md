# AI Brand Studio - Deployment Guide

## Deployment Status

**Status:** ✅ Deployment-Ready
**Target Platform:** Vertex AI Agent Engine
**Configuration:** Complete
**Date Prepared:** November 19, 2024

---

## Deployment Configuration

### Files Prepared

1. **`brand_studio_agent/agent.py`** - Production agent entry point
   - Exports `root_agent` (BrandStudioOrchestrator)
   - Configured with all sub-agents and tools

2. **`brand_studio_agent/.agent_engine_config.json`** - Resource configuration
   - Auto-scaling: 0-5 instances
   - Resources: 2 CPU, 4Gi memory
   - Timeouts: 600s request, 300s idle
   - Health checks enabled

3. **`brand_studio_agent/requirements.txt`** - Production dependencies
   ```
   google-adk>=1.18.0
   google-genai>=1.50.0
   python-whois>=0.8.0
   ```

4. **`brand_studio_agent/.env`** - Environment configuration
   ```bash
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=1
   ```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│         Vertex AI Agent Engine                   │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │   Brand Studio Orchestrator (root)     │    │
│  │                                          │    │
│  │   ┌──────────┐  ┌──────────┐           │    │
│  │   │ Research │  │ Loop:    │           │    │
│  │   │  Agent   │  │ Name Gen │           │    │
│  │   └──────────┘  │ +Validate│           │    │
│  │                  └──────────┘           │    │
│  │                                          │    │
│  │   ┌──────────┐  ┌──────────┐           │    │
│  │   │   SEO    │  │  Story   │           │    │
│  │   │  Agent   │  │  Agent   │           │    │
│  │   └──────────┘  └──────────┘           │    │
│  └────────────────────────────────────────┘    │
│                                                  │
│  Tools: Domain Checker, Trademark, RAG          │
│  Model: Gemini 2.0 Flash (via Vertex AI)       │
└─────────────────────────────────────────────────┘
```

---

## Deployment Commands

### Prerequisites

```bash
# 1. Install ADK CLI (if not already installed)
pip install google-adk

# 2. Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# 3. Set project
export GOOGLE_CLOUD_PROJECT=brand-agent-478519
gcloud config set project $GOOGLE_CLOUD_PROJECT

# 4. Enable required APIs
gcloud services enable aiplatform.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

### Deploy to Agent Engine

```bash
# From project root, deploy the agent
cd brand_studio_agent

# Deploy using ADK CLI
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  brand_studio_agent \
  --agent_engine_config_file=.agent_engine_config.json

# Monitor deployment
gcloud ai agents list \
  --region=us-central1 \
  --project=$GOOGLE_CLOUD_PROJECT
```

### Expected Output

```
Deploying agent to Vertex AI Agent Engine...
✓ Validating agent configuration
✓ Building container image
✓ Pushing to Artifact Registry
✓ Deploying to Agent Engine
✓ Creating endpoint

Deployment successful!

Agent Details:
  Name: brand-studio-agent
  Region: us-central1
  Endpoint: https://us-central1-aiplatform.googleapis.com/v1/projects/brand-agent-478519/locations/us-central1/agents/brand-studio-agent
  Status: ACTIVE
```

---

## Testing Deployed Agent

### Via Python SDK

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(
    project="brand-agent-478519",
    location="us-central1"
)

# Get agent
agent = aiplatform.Agent("brand-studio-agent")

# Query agent
response = agent.query(
    content="Create a brand for an AI-powered fitness coaching app"
)

print(response.text)
```

### Via REST API

```bash
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/brand-agent-478519/locations/us-central1/agents/brand-studio-agent:query" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Create a brand for an AI-powered fitness app"
  }'
```

---

## Resource Configuration Details

### Auto-Scaling Settings

- **Min Instances:** 0 (scales to zero when idle = cost-effective)
- **Max Instances:** 5 (handles concurrent requests)
- **Scale Down Delay:** 300s (5 minutes after idle)
- **Target CPU:** 70% utilization
- **Target Memory:** 80% utilization

### Resource Allocation Per Instance

- **CPU:** 2 cores
- **Memory:** 4 GiB
- **Timeout:** 600s (10 minutes for complex brand generation)

### Health Checks

- **Enabled:** Yes
- **Check Interval:** 30s
- **Timeout:** 10s
- **Unhealthy Threshold:** 3 consecutive failures

---

## Cost Estimation

### Monthly Cost (with auto-scaling to zero)

| Component | Usage | Cost Estimate |
|-----------|-------|---------------|
| Gemini 2.0 Flash API | ~500K tokens/month | $1.25 |
| Agent Engine Runtime | ~10 hours active | $2.50 |
| Cloud Logging | 10 GB | $0 (free tier) |
| Cloud Storage | 5 GB | $0 (free tier) |
| **Total** | | **~$4/month** |

**Note:** With min_instances=0, costs are minimal when agent is not actively serving requests.

---

## Monitoring & Observability

### Cloud Logging

View logs:
```bash
gcloud logging read \
  "resource.type=ml_job AND resource.labels.job_id=brand-studio-agent" \
  --limit=100 \
  --format=json
```

### Agent Metrics

Track performance:
```bash
gcloud monitoring dashboards create \
  --config-from-file=monitoring-dashboard.json
```

Key metrics tracked:
- Request latency (P50, P95, P99)
- Agent invocations per minute
- Tool call success rates
- Error rates by agent
- Context compaction events

---

## Deployment Verification Checklist

- [x] Agent code structured correctly (`brand_studio_agent/agent.py`)
- [x] `root_agent` exported properly
- [x] Multi-agent orchestration configured (SequentialAgent + LoopAgent)
- [x] All 5 sub-agents created and tested
- [x] Custom tools integrated (domain, trademark, RAG)
- [x] Context compaction configured
- [x] Observability logging implemented
- [x] Resource configuration optimized
- [x] Environment variables set
- [x] Dependencies documented
- [x] Health checks enabled
- [x] Auto-scaling configured
- [x] Cost optimization (min_instances=0)

---

## Production Readiness

### ✅ Complete

1. **Multi-Agent System:** SequentialAgent + LoopAgent + 5 specialized agents
2. **Tools:** Domain checker, Trademark checker, RAG retrieval
3. **State Management:** Session management with file-based persistence
4. **Context Engineering:** EventsCompactionConfig for long conversations
5. **Observability:** Cloud Logging integration with structured metrics
6. **Testing:** 12+ evaluation test cases with custom evaluators
7. **Documentation:** Comprehensive guides (README, CLAUDE.md, TESTING.md)
8. **Deployment Config:** Production-ready configuration files

### 📊 Capstone Requirements Met

- [x] Multi-agent system (Sequential + Loop + 5 agents)
- [x] Custom tools (3 tools)
- [x] Built-in tools (Google Search)
- [x] Sessions & State Management
- [x] Context Compaction
- [x] Observability (Logging + Metrics)
- [x] Agent Evaluation (12+ test cases)
- [x] Deployment Configuration (ready to deploy)
- [x] Gemini Models (Gemini 2.0 Flash)

---

## Troubleshooting

### Common Issues

**Issue:** ADK CLI not found
```bash
# Solution: Install ADK with CLI support
pip install google-adk[cli]
```

**Issue:** Authentication errors
```bash
# Solution: Refresh credentials
gcloud auth login
gcloud auth application-default login
```

**Issue:** API not enabled
```bash
# Solution: Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

**Issue:** Insufficient permissions
```bash
# Solution: Grant necessary roles
gcloud projects add-iam-policy-binding brand-agent-478519 \
  --member="user:ben@benogren.com" \
  --role="roles/aiplatform.admin"
```

---

## Next Steps

1. **Deploy:** Run deployment commands above
2. **Test:** Verify agent responds correctly to queries
3. **Monitor:** Set up logging and monitoring dashboards
4. **Optimize:** Adjust resources based on actual usage patterns
5. **Scale:** Increase max_instances if needed for production load

---

## Support & Documentation

- **ADK Documentation:** https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit
- **Agent Engine Guide:** https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine
- **Project README:** `/README.md`
- **Architecture Guide:** `/CLAUDE.md`
- **Testing Guide:** `/TESTING.md`

---

**Deployment Prepared By:** AI Brand Studio Development Team
**Last Updated:** November 19, 2024
**Version:** 1.0.0
