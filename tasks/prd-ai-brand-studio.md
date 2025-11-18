---
version: 1
fidelity_mode: strict
agents:
  developer: developer-fidelity
  reviewer: quality-reviewer-fidelity
scope_preservation: true
additions_allowed: none
document_metadata:
  source_type: user_requirements
  creation_date: 2025-11-17
  fidelity_level: absolute
  scope_changes: none
codebase_analyzed: true
validated: true
---

# AI Brand Studio - Product Requirements Document

## Problem Statement

Early-stage founders and marketing teams face significant challenges in brand naming:
- **Time-consuming:** Average 20+ hours spent on naming and validation
- **Legal risks:** 67% of startups rebrand within the first year due to trademark conflicts
- **Fragmented process:** Requires checking multiple databases (trademarks, domains, SEO tools)
- **Inconsistent branding:** Name often doesn't align with tagline, story, or marketing copy
- **No context:** Generic generators don't understand industry-specific naming patterns

**Current solutions (Namelix, Business Name Generator, domain checkers) lack:**
- Integrated trademark + domain + SEO validation
- Industry-aware name generation using RAG
- Complete brand package (name + story + marketing copy)
- Multi-agent orchestration for comprehensive brand creation

## Explicit Requirements

### Core Functionality (P0 - MVP)

1. **Multi-Agent System with 6 Specialized Agents:**
   - Orchestrator Agent: Coordinates brand creation workflow
   - Research Agent: Researches industry trends and competitor brands using Google Search
   - Name Generator Agent: Generates 20-50 brand name candidates using RAG retrieval
   - Validation Agent: Checks domain availability and trademark conflicts (USPTO, EU IPO)
   - SEO Optimizer Agent: Analyzes SEO metrics and generates meta titles/descriptions
   - Story Generator Agent: Creates brand narratives and marketing copy

2. **RAG (Retrieval-Augmented Generation) Implementation:**
   - Vector database with 5,000+ successful brand names (Product Hunt, Fortune 500, Y Combinator)
   - Vertex AI Vector Search for embedding storage and retrieval
   - Text-embedding-004 model for embedding generation
   - Metadata schema: brand_name, industry, category, year_founded, naming_strategy, syllables

3. **Legal & Technical Validation:**
   - Real-time domain availability checking (.com, .ai, .io extensions)
   - USPTO trademark database search for conflict detection
   - EU IPO trademark database search
   - Risk level assessment (low/medium/high) for each name
   - Social media handle availability checking (Twitter, Instagram, LinkedIn)

4. **Name Generation:**
   - Generate 20-50 brand name candidates per session
   - Multiple naming strategies: portmanteau, descriptive, invented, acronyms
   - Industry-specific names using RAG retrieval
   - Customizable brand personality: playful, professional, innovative, luxury

5. **Complete Brand Package Output:**
   - Final brand name with variations
   - 3-5 tagline options (5-8 words each)
   - Brand story/narrative (150-300 words)
   - Landing page hero section copy (50-100 words)
   - Value proposition statement (20-30 words)
   - Meta descriptions and titles for SEO
   - Domain availability status for .com, .ai, .io
   - Trademark risk assessment

### Session & Memory Management (P1)

6. **Session Management:**
   - DatabaseSessionService using Cloud SQL (PostgreSQL)
   - Persist conversation context within sessions
   - Track user inputs, generated names, and selections
   - Session metadata storage

7. **Long-term Memory:**
   - Vertex AI Memory Bank for user preferences across sessions
   - Learn from accepted/rejected name suggestions
   - Store user's industry preferences and brand personality choices

8. **Context Compaction:**
   - Summarize long brainstorming sessions to manage context limits
   - Maintain essential information while reducing token usage

### Workflow Patterns (P1)

9. **Parallel Execution:**
   - Research and initial generation happen simultaneously
   - Validation checks (domain + trademark) run in parallel

10. **Sequential Pipeline:**
    - Generation → Validation → SEO → Story (must execute in order)
    - Ensure validation passes before proceeding to content generation

11. **Loop Refinement:**
    - If validation fails (high trademark risk or no domains available), regenerate names
    - Maximum 3 iterations to prevent infinite loops

### Infrastructure & Deployment (P1)

12. **Google Cloud Stack:**
    - Vertex AI Agent Engine for agent runtime
    - Gemini 2.5 Flash (orchestrator, research, validation, SEO agents)
    - Gemini 2.5 Pro (name generator, story generator for creative tasks)
    - Cloud SQL PostgreSQL for session storage
    - Vertex AI Vector Search for RAG implementation
    - Cloud Storage for datasets and logs
    - Secret Manager for API keys
    - Cloud Logging and Monitoring for observability

13. **Custom Tools Implementation:**
    - Domain availability checker (whois integration)
    - USPTO trademark search tool
    - EU IPO trademark search tool
    - Social media handle checker (Twitter, Instagram, LinkedIn)
    - SEO analyzer (keyword volume, pronounceability, memorability scoring)
    - Brand story generator tool

14. **Built-in Tools:**
    - Google Search for competitive research (Research Agent)

### Testing & Evaluation (P2)

15. **Agent Evaluation Suite:**
    - 10+ test cases with sample brand briefs
    - Evaluation criteria: name quality score, validation accuracy, content quality, performance metrics
    - Target: >90% success rate, <2 minutes per complete brand package
    - Test scenarios: healthcare AI app, fintech startup, e-commerce SaaS

16. **Observability:**
    - Cloud Logging integration for agent traces
    - Performance metrics tracking
    - Error tracking and debugging support

## Scope Boundaries

### Explicitly Included

- Multi-agent system with 6 specialized agents (orchestrator, research, name generator, validation, SEO, story)
- RAG implementation using Vertex AI Vector Search with 5,000+ brand name corpus
- Domain availability checking (.com, .ai, .io)
- Trademark conflict detection (USPTO, EU IPO)
- Social media handle availability checking (Twitter, Instagram, LinkedIn)
- SEO optimization (meta titles, descriptions, keyword analysis)
- Complete brand package generation (name, taglines, story, hero copy, value proposition)
- Session management using Cloud SQL PostgreSQL
- Long-term memory using Vertex AI Memory Bank
- Context compaction for long conversations
- Parallel, sequential, and loop workflow patterns
- Custom tools: domain checker, trademark search, SEO analyzer, social handle checker
- Built-in tool: Google Search for research
- Agent evaluation test suite
- Cloud Logging and Monitoring for observability
- Deployment to Vertex AI Agent Engine
- Gemini 2.5 Flash and Pro model usage

### Explicitly Excluded

- Logo generation (no Imagen/DALL-E integration)
- A2A (Agent-to-Agent) protocol integration
- Multi-user collaboration features (team voting, comments)
- Advanced analytics dashboard (usage metrics, A/B testing)
- Export formats: PDF brand guidelines, PowerPoint presentations, Figma brand kits
- User authentication and authorization (beyond basic API access)
- Payment processing or subscription management
- Custom domain name suggestion algorithms (beyond standard generation)
- Brand name trademark filing services
- Legal counsel or trademark attorney recommendations

### Assumptions & Clarifications

- **MVP Focus:** Core brand generation functionality prioritized to meet December 1, 2025 deadline
- **Prioritization:** Features marked P0 (must-have), P1 (should-have), P2 (nice-to-have)
- **Security:** Standard Google Cloud security practices (Secret Manager for API keys, secure API calls, no special compliance requirements)
- **Target Users:** Early-stage founders and marketing teams at startups and small businesses
- **Timeline:** 4-phase implementation roadmap (Phase 1: Foundation, Phase 2: Core Features, Phase 3: Content & Polish, Phase 4: Deployment)
- **Cost Constraints:** Stay within Google Cloud free tier where possible (~$4-5/month estimated)
- **Data Sources:** Product Hunt, USPTO, Fortune 500, Y Combinator startup names
- **Disclaimer Required:** "Always verify trademark status with legal counsel" for liability protection

## Success Criteria

- **Time Savings:** Generate complete brand package in <10 minutes (vs. 20+ hours manually)
- **Legal Safety:** Identify and flag all potential trademark conflicts with >95% accuracy
- **Domain Availability:** >80% of top 5 suggestions have .com domain available
- **Name Quality:** Generate 20-50 relevant, industry-appropriate brand names per session
- **Complete Deliverable:** Every successful generation includes name + taglines + story + hero copy + SEO metadata
- **Performance:** End-to-end brand package generation completes in <2 minutes
- **Evaluation Success:** >90% of test cases pass with acceptable quality scores
- **Deployment:** Successfully deployed to Vertex AI Agent Engine
- **Observability:** All agent actions logged to Cloud Logging with trace IDs

## Testing Requirements

### Evaluation Test Cases (from specification section 9)

1. **Healthcare AI App:** Mental wellness app for Gen Z users
   - Expected: 15-50 names, 5+ available .com domains, 3+ low-risk trademarks, SEO score >70
   - Validation: taglines present, brand story 150-300 words

2. **Fintech Startup:** Expense tracking for freelancers
   - Expected: 15+ names, 5+ available .com domains, 3+ low-risk trademarks
   - Validation: names contain finance-related keywords

3. **E-commerce SaaS:** Inventory management platform
   - Expected: 15+ names, 5+ low-risk trademarks, pronounceable names
   - Validation: professional tone matching

### Performance Testing

- **Response Time:** <2 minutes for complete brand package
- **Accuracy:** Domain checker >95% accuracy, trademark risk assessment verified against USPTO data
- **Reliability:** <1% error rate (no failed generations due to system errors)
- **RAG Relevance:** >85% of retrieved brand examples rated as industry-relevant

### Test Execution

- Use ADK evaluation framework: `adk eval brand_studio_agent tests/integration.evalset.json`
- Custom evaluation metrics: name quality score (0-100), validation accuracy (pass/fail), content quality score (0-100)
- Human evaluation for tagline catchiness and brand story coherence

## Security Requirements

### Standard Security Practices

- **API Key Management:** Store all API keys (Namecheap, USPTO, social media APIs) in Google Cloud Secret Manager
- **Database Security:** Use Cloud SQL with SSL connections, no public IP exposure
- **Data Privacy:** Session data stored in Cloud SQL with proper access controls
- **Authentication:** API Gateway (Cloud Run) with rate limiting for deployed agent
- **Secrets:** Never commit API keys or credentials to repository (use .env.example template)
- **Input Validation:** Sanitize user inputs to prevent injection attacks
- **HTTPS Only:** All external API calls and user-facing endpoints use HTTPS

### Out of Scope

- User authentication/authorization (assumed single-user or trusted environment for MVP)
- GDPR/CCPA compliance features
- Data encryption at rest (rely on Google Cloud defaults)
- Advanced threat detection or WAF

## Technical Considerations

### Existing Patterns (New Project - from Specification)

**This is a new project with no existing codebase.** The following patterns are defined by the specification:

### Multi-Agent Architecture

- **Orchestrator Pattern:** Central LLM agent coordinates 5 sub-agents
- **Agent Models:**
  - Gemini 2.5 Flash Lite: Orchestrator, Research, Validation, SEO (faster, cost-effective)
  - Gemini 2.5 Pro: Name Generator, Story Generator (more powerful for creative tasks)
- **Workflow Types:**
  - Parallel: Research + Name Generation (independent tasks)
  - Sequential: Generation → Validation → SEO → Story (dependent pipeline)
  - Loop: Regenerate names if validation fails (max 3 iterations)

### RAG Implementation Pattern

- **Vector Database:** Vertex AI Vector Search with 768-dimension embeddings
- **Embedding Model:** text-embedding-004
- **Retrieval Strategy:** K-NN search (k=50) with industry filters
- **Data Sources:** Product Hunt (50K names), USPTO trademarks, Fortune 500, Y Combinator
- **Metadata Schema:** brand_name, industry, category, year_founded, naming_strategy, syllables, domain, trademark_status

### Database Schema (Cloud SQL PostgreSQL)

**Sessions Table:**
```sql
session_id (VARCHAR 255, PK), user_id, application_id, created_at, updated_at, metadata (JSONB)
```

**Events Table:**
```sql
event_id (SERIAL, PK), session_id (FK), author (user/agent), content (TEXT), timestamp, event_type, metadata (JSONB)
```

**Generated Brands Table:**
```sql
id (SERIAL, PK), session_id (FK), brand_name, tagline, story, domain_status (JSONB), trademark_risk, seo_score, user_selected, created_at, metadata (JSONB)
```

### Custom Tools Pattern

- **Domain Checker:** python-whois library, check .com/.ai/.io extensions, return availability + domain string
- **Trademark Search:** USPTO TESS API or uspto.report API, search by name + optional Nice classification
- **SEO Analyzer:** Calculate length score, pronounceability (vowel ratio), memorability, keyword density
- **Social Handle Checker:** API integrations for Twitter, Instagram, LinkedIn availability

### Integration Points

- **Google Search Tool:** Built-in tool for Research Agent to find competitor names and industry trends
- **Vertex AI Embeddings:** text-embedding-004 for RAG query and corpus embedding
- **Cloud SQL:** DatabaseSessionService for conversation state persistence
- **Memory Bank:** Vertex AI Memory Bank collection for cross-session user preferences
- **Cloud Logging:** LoggingPlugin for agent traces and debugging

### Testing Infrastructure

- **ADK Evaluation Framework:** Use `adk eval` command with .evalset.json files
- **Test Structure:** JSON format with user_content, expected_output criteria
- **Metrics:** Custom evaluators for name_quality_score, validation_accuracy, content_quality_score
- **Assertions:** num_names (min/max), domain_available_com (min count), trademark_risk_low (min count), seo_score_avg (min)

### Deployment Pattern

- **Target Platform:** Vertex AI Agent Engine (required for 5-point bonus)
- **Configuration:** `.agent_engine_config.json` with min_instances=0 (scale to zero), max_instances=5
- **Resource Limits:** 2 CPU, 4Gi memory, 600s timeout
- **Deployment Command:** `adk deploy agent_engine --project=PROJECT_ID --region=us-central1 brand_studio_agent`

### Cost Optimization

- **Free Tier Usage:** Cloud SQL f1-micro, 5GB Cloud Storage, 50GB Cloud Logging
- **Model Selection:** Use Flash Lite for non-creative tasks, Pro only for name/story generation
- **Scale to Zero:** min_instances=0 to avoid idle compute costs
- **Estimated Cost:** ~$4-5/month for 100 brand generations (within budget constraints)

## Implementation Notes

### Fidelity Requirements (MANDATORY)

- Implement ONLY what's explicitly specified in this PRD
- Do not add features, tests, or security beyond requirements
- Question ambiguities rather than making assumptions
- Preserve all requirement constraints and limitations
- Use fidelity-preserving agents for all implementation work

### Prioritization (MVP-First Approach)

**P0 (Must-Have for MVP):**
- 6-agent multi-agent system with orchestrator
- Basic name generation (20-50 candidates)
- Domain availability checking (.com, .ai, .io)
- Trademark search (USPTO minimum)
- Social media handle checking
- Basic brand package (name + 1 tagline + story)

**P1 (Should-Have for Complete Product):**
- RAG implementation with Vertex AI Vector Search
- Full brand package (multiple taglines, hero copy, value prop, SEO metadata)
- Session management with Cloud SQL
- Memory Bank integration
- Context compaction
- SEO optimization agent
- Parallel/Sequential/Loop workflows
- EU IPO trademark search
- Deployment to Agent Engine

**P2 (Nice-to-Have, Time Permitting):**
- Full evaluation test suite (10+ cases)
- Advanced observability and logging
- Multiple naming strategies (portmanteau, acronyms, etc.)
- Advanced SEO metrics (keyword volume, search intent)

### Phased Implementation Roadmap

**Phase 1: Foundation**
- Setup Google Cloud project, enable APIs
- Create Cloud SQL database
- Implement Orchestrator Agent (basic)
- Implement Name Generator Agent (no RAG initially)
- Create domain availability checker tool
- Basic CLI for testing

**Phase 2: Core Features**
- Curate brand name dataset (5,000+ names)
- Setup Vertex AI Vector Search index
- Implement RAG retrieval in Name Generator
- Build Validation Agent (trademark + domain)
- Implement Research Agent
- Add session management

**Phase 3: Content & Polish**
- Implement SEO Optimizer Agent
- Build Story Generator Agent
- Add Memory Bank for preferences
- Create evaluation test suite
- Run evaluations and fix issues
- Improve prompt engineering

**Phase 4: Deployment**
- Deploy to Vertex AI Agent Engine
- Create demo video
- Finalize documentation
- Submit to competition

### Next Steps

1. Use `/prd:2:gen-tasks prd-ai-brand-studio.md` to convert this PRD into executable task list
2. Use developer-fidelity agent for implementation planning
3. Use quality-reviewer-fidelity agent for validation against this PRD
4. Follow strict scope preservation throughout implementation
5. Prioritize P0 features first, then P1, then P2 if time permits

## Open Questions

- **Namecheap API Access:** Do we have API credentials for bulk domain checking? (Fallback: python-whois library)
- **USPTO API Limits:** What are rate limits for trademark search API? (May need caching strategy)
- **Social Media API Access:** Twitter/Instagram/LinkedIn API credentials available? (May defer if APIs unavailable)
- **Dataset Curation:** Should we manually curate the initial 1,000 brand names or scrape Product Hunt directly?
- **Nice Classification:** Do we need to ask users for their industry category (Nice class) for trademark search specificity?
- **Domain Alternatives:** If .com unavailable, should agent suggest alternative TLDs automatically or require user input?

## Environment Setup Guide

### Prerequisites

- Python 3.9 or higher (tested with 3.14.0)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (gcloud CLI)
- Git
- A Google Cloud account with billing enabled

### Quick Setup for Local Testing

For local testing with Google AI API (no full Google Cloud required):

```bash
# 1. Clone repository and setup Python environment
git clone <repository-url>
cd Brand-Agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure minimal environment variables
cp .env.example .env
# Edit .env with:
GOOGLE_CLOUD_PROJECT=test-project-local
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
LOG_LEVEL=INFO
ENABLE_TRACING=false
MAX_NAME_CANDIDATES=50
MIN_NAME_CANDIDATES=20
MAX_LOOP_ITERATIONS=3
DOMAIN_CACHE_TTL_SECONDS=300

# 3. Test that it works
python -m src.cli --help
```

### Full Google Cloud Setup (Production)

#### Option A: Automated Setup (Recommended)

```bash
./scripts/setup_gcp.sh
```

This script will:
1. Create or configure your Google Cloud project
2. Enable all required APIs (Vertex AI, Cloud SQL, Vector Search, Secret Manager, Logging)
3. Set up Application Default Credentials
4. Configure default region (us-central1)

#### Option B: Manual Setup

1. **Create a Google Cloud Project:**
   ```bash
   export PROJECT_ID="your-project-id"
   gcloud projects create $PROJECT_ID
   gcloud config set project $PROJECT_ID
   ```

2. **Enable Billing:**
   - Visit https://console.cloud.google.com/billing
   - Link billing account to your project

3. **Enable Required APIs:**
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     storage.googleapis.com \
     sql-component.googleapis.com \
     sqladmin.googleapis.com \
     logging.googleapis.com \
     monitoring.googleapis.com \
     cloudtrace.googleapis.com \
     secretmanager.googleapis.com
   ```

4. **Set Default Region:**
   ```bash
   gcloud config set compute/region us-central1
   ```

5. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

### Database Setup (Optional for Phase 1)

#### Cloud SQL PostgreSQL Instance

Run the automated setup script:

```bash
./scripts/setup_cloud_sql.sh
```

This creates:
- Cloud SQL PostgreSQL instance (f1-micro tier for free tier)
- `brandstudio` database
- Database user with password
- Connection details for .env configuration

#### Local Development with Cloud SQL Proxy

```bash
# Download Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy

# Run the proxy
./cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_NAME

# Update .env with local connection
DATABASE_URL=postgresql://brandstudio-user:PASSWORD@localhost:5432/brandstudio
```

### Secret Manager Configuration

Configure API keys securely in Google Cloud Secret Manager:

```bash
./scripts/setup_secrets.sh
```

Prompts for (all optional for Phase 1):
- **Namecheap API Key** - for domain availability checking
- **USPTO API Key** - for trademark search
- **Twitter/X API credentials** - for social media handle checking
- **Instagram API Key** - for handle checking
- **LinkedIn API Key** - for handle checking
- **Database Password** - for Cloud SQL access

### Environment Variables Reference

**Minimal .env (Phase 1 - Local Testing):**
```bash
GOOGLE_CLOUD_PROJECT=test-project-local
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
LOG_LEVEL=INFO
```

**Full .env (Phase 2+ - Production Ready):**
```bash
GOOGLE_CLOUD_PROJECT=my-real-gcp-project
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
DATABASE_URL=postgresql://user:pass@localhost:5432/brandstudio
VECTOR_SEARCH_INDEX_ENDPOINT=projects/.../indexEndpoints/...
VECTOR_SEARCH_DEPLOYED_INDEX_ID=brand_names_deployed
LOG_LEVEL=INFO
ENABLE_TRACING=true

# Optional API Keys (stored in Secret Manager for production)
NAMECHEAP_API_KEY=your-key  # Optional, falls back to python-whois
USPTO_API_KEY=your-key      # Optional, falls back to simulation
TWITTER_API_KEY=your-key    # Optional
INSTAGRAM_API_KEY=your-key  # Optional
LINKEDIN_API_KEY=your-key   # Optional
```

## Current Implementation Status

### ✅ Phase 1: Foundation (100% Complete)

**Completed Features:**
- [x] Project structure and Google Cloud setup
- [x] Orchestrator Agent (basic coordination with Gemini 2.5 Flash)
- [x] Domain Availability Checker (enhanced: 10 TLDs + 6 prefix variations)
- [x] Name Generator Agent (working with Google AI API)
- [x] Basic CLI for testing (interactive and command-line modes)
- [x] Environment configuration and secrets management

**Enhancement: Extended Domain Checking (User-Requested)**
- Original spec: .com, .ai, .io (3 TLDs)
- **Current: 10 TLDs** - .com, .ai, .io, .so, .app, .co, .is, .me, .net, .to
- **6 prefix variations** - get, try, your, my, hello, use
- Smart alternative suggestions when base domains are taken

### 🚀 Phase 3: Interactive Workflow (Implemented Ahead of Schedule)

**Major Enhancement: Interactive 3-Phase Workflow (User-Requested)**

**Why Changed:** Original Phase 3 validated ALL 20-30 generated names, which was:
- ⏰ Slow (5-10 minutes)
- 💸 Expensive (~90 API calls)
- 🚫 Wasteful (validating names users might not like)

**New Workflow:**
1. **Generate 20 names** - AI creates initial brand candidates
2. **User selects 5-10 favorites** - Interactive selection
3. **Validate selected only** - Domain, trademark, SEO checks on picks
4. **Regenerate if needed** - Not satisfied? Try again with context preserved

**Benefits:**
- ⚡ **70% faster** - Validate 5-10 instead of 20-30 names
- 💰 **70% cheaper** - ~15-30 API calls vs ~90
- ♻️ **Iterative** - Regenerate with context preserved
- 🎯 **User-driven** - Control what gets validated

**Completed Features:**
- [x] SEO Optimizer Agent (Gemini 2.5 Flash)
- [x] Interactive selection interface
- [x] Selective validation (domain + trademark + SEO)
- [x] Regeneration loop with context preservation
- [x] Enhanced results display with grouping
- [x] USPTO TSDR API integration (with fallback to simulation)

### 🔄 Phase 2: Core Features (In Progress)

**Not Yet Started:**
- [ ] Task 6.0: Curate Brand Name Dataset (5,000+ brands)
- [ ] Task 7.0: Setup Vertex AI Vector Search for RAG
- [ ] Task 8.0: Integrate RAG into Name Generator
- [ ] Task 9.0: Implement Validation Agent (coordination layer)
- [ ] Task 10.0: Social Media Handle Checker
- [ ] Task 11.0: Research Agent
- [ ] Task 12.0: Session Management with Cloud SQL

### ⏭️ Phase 3 & 4: Remaining Tasks

**Phase 3 Remaining:**
- [ ] Task 14.0: Story Generator Agent
- [ ] Task 15.0: Vertex AI Memory Bank
- [ ] Task 16.0: Workflow Patterns (Parallel, Sequential, Loop)
- [ ] Task 17.0: Context Compaction
- [ ] Task 18.0: Agent Evaluation Test Suite
- [ ] Task 19.0: Improve Agent Prompt Engineering
- [ ] Task 20.0: Observability with Cloud Logging

**Phase 4: Deployment**
- [ ] Task 21.0: Vertex AI Agent Engine Deployment
- [ ] Task 22.0: Complete Feature Documentation
- [ ] Task 23.0: Demo Video and Kaggle Submission

## Usage Guide

### Running the Application

#### Interactive Mode (Recommended)

```bash
# Activate virtual environment
cd /Users/benogren/Desktop/projects/Brand-Agent
source venv/bin/activate

# Start interactive mode
python -m src.cli
```

**What happens:**

**Phase 1 - Generate:**
```
Generating 20 brand names...

GENERATED BRAND NAMES (20 total)
======================================================================
 1. MealMind             - Intelligent meal planning...
 2. NutriNest            - Warm, family-oriented brand...
 ...
 20. KitchenIQ           - Smart kitchen solutions...
```

**Phase 2 - Select:**
```
SELECT YOUR FAVORITE NAMES (5-10 names)
======================================================================
Enter the numbers of your favorite names (comma-separated)
Example: 1,5,7,12,18
Or type 'regenerate' to start over with new names

Your selection (5-10 names): 1,2,5,7,12

You selected 5 names:
  - MealMind
  - NutriNest
  - PlateWise
  - FamilyFeast
  - KitchenIQ

Confirm selection? (y/n): y
```

**Phase 3 - Validate:**
```
PHASE 3: VALIDATING SELECTED NAMES
======================================================================

[1/5] Validating: MealMind
----------------------------------------------------------------------
  Checking domain availability...
  Checking trademark conflicts...
  Optimizing for SEO...
  ✓ Domains available: mealmind.com, mealmind.ai, mealmind.io
  ✓ Trademark risk: low
  ✓ SEO score: 87/100

[Results for other 4 names...]
```

#### Command-Line Mode

```bash
# Direct command-line with automatic interactive workflow
python -m src.cli \
  --product "AI-powered meal planning app for busy parents" \
  --audience "Parents aged 28-40" \
  --personality professional \
  --industry food_tech

# Quick generation with minimal output
python -m src.cli \
  --product "Healthcare telemedicine app" \
  --personality professional \
  --quiet

# Save to JSON file
python -m src.cli \
  --product "E-commerce sustainable fashion marketplace" \
  --personality playful \
  --json output.json
```

#### CLI Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--product, -p` | Product description (required in direct mode) | `--product "AI app"` |
| `--audience, -a` | Target audience | `--audience "Millennials"` |
| `--personality, -P` | Brand tone (playful/professional/innovative/luxury) | `--personality innovative` |
| `--industry, -i` | Industry category | `--industry tech` |
| `--count, -c` | Number of names (20-50) | `--count 25` |
| `--verbose, -v` | Detailed output | `--verbose` |
| `--quiet, -q` | Minimal output (names only) | `--quiet` |
| `--json, -j` | Save to JSON file | `--json results.json` |

### Testing the Application

```bash
# Run comprehensive Phase 2 tests
python test_phase2.py

# This tests:
# - Research Agent
# - RAG Brand Retrieval
# - Validation Agent (domain + trademark)
# - SEO Optimizer
# - Brand Story Generator (real LLM)
# - Session Management
# - Integrated Name Generation
```

### Performance Expectations

- **Name Generation**: ~10-15 seconds for 20 names
- **Validation**: ~2-3 seconds per name (domain + trademark)
- **Story Generation**: ~5-8 seconds (real LLM)
- **Full Test Suite**: ~30-40 seconds
- **Interactive Workflow**: 1-3 minutes total (vs 5-10 min old workflow)

## Deployment Guide

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    VERTEX AI AGENT ENGINE                 │
│  ┌───────────────────────────────────────────────────┐   │
│  │   Orchestrator Agent (gemini-2.5-flash)          │   │
│  │   ├── Research Agent                              │   │
│  │   ├── Name Generator Agent (gemini-2.5-pro)      │   │
│  │   ├── Validation Agent                            │   │
│  │   ├── SEO Optimizer Agent                         │   │
│  │   └── Story Generator Agent (gemini-2.5-pro)     │   │
│  └───────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────┘
                 │
        ┌────────┴────────┬────────────────┬────────────┐
        ↓                 ↓                ↓            ↓
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐
│ CLOUD SQL    │  │ VECTOR       │  │ CLOUD    │  │ CLOUD  │
│ (PostgreSQL) │  │ SEARCH       │  │ STORAGE  │  │ LOGGING│
│              │  │              │  │          │  │        │
│ - Sessions   │  │ - Brand DB   │  │ -Datasets│  │ -Traces│
│ - Events     │  │ - Embeddings │  │ - Exports│  │ -Metrics│
└──────────────┘  └──────────────┘  └──────────┘  └────────┘
```

### Step-by-Step Deployment Process

#### Step 1: Initial Google Cloud Setup (10-15 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-username/Brand-Agent.git
cd Brand-Agent

# 2. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run GCP setup script
./scripts/setup_gcp.sh
```

This script will:
- ✅ Enable required Google Cloud APIs
- ✅ Create Cloud Storage bucket
- ✅ Set up service accounts with proper IAM roles
- ✅ Configure authentication
- ✅ Generate `.env` file

#### Step 2: Cloud SQL Database Setup (Optional, 15-20 minutes)

```bash
# Run database migrations
./scripts/run_migrations.py
```

Creates:
- Sessions table
- Events table
- Generated brands table
- Brand stories table
- Indexes and constraints

**Note**: For Phase 2 testing, file-based session storage works fine.

#### Step 3: Vector Search Setup (30-45 minutes)

```bash
# Generate embeddings and create Vector Search index
python scripts/setup_vector_search.py
```

This script:
1. Generates embeddings for brand names dataset
2. Uploads embeddings to Cloud Storage
3. Creates Vertex AI Vector Search index
4. Deploys index to endpoint

**What's created:**
- Embeddings file in Cloud Storage
- Vector Search index (768 dimensions)
- Index endpoint for queries
- Configuration saved to `.env`

#### Step 4: Test Locally with Production Config (5 minutes)

```bash
# Run Phase 2 tests with production config
python test_phase2.py

# Test CLI with production RAG
python -m src.cli --product "AI fitness app" --count 10
```

Verify that:
- ✅ All tests pass
- ✅ Names are generated successfully
- ✅ Domain and trademark validation works
- ✅ Cloud Logging is capturing events

#### Step 5: Deploy to Vertex AI Agent Engine (10-15 minutes)

```bash
# Deploy the multi-agent system
./scripts/deploy.sh
```

This script:
1. ✅ Runs tests before deployment
2. ✅ Packages source code and dependencies
3. ✅ Deploys to Vertex AI Agent Engine
4. ✅ Creates agent endpoint
5. ✅ Tests deployed agent

**Deployment config** (`.agent_engine_config.json`):
- Min instances: 0 (scale to zero)
- Max instances: 5 (auto-scaling)
- Resources: 2 CPU, 4GB memory
- Timeout: 600s (10 minutes)

#### Step 6: Test Deployed Agent (5 minutes)

```bash
# Test via gcloud CLI
gcloud ai agents query brand_studio_agent \
  --region=us-central1 \
  --query="I need a brand name for an AI-powered fitness app"

# View deployment info
cat deployment/deployment_info.json
```

#### Step 7: Run Evaluation Suite (10 minutes)

```bash
# Run comprehensive evaluation tests
adk eval brand_studio_agent tests/integration.evalset.json \
  --config_file_path=tests/eval_config.json \
  --print_detailed_results
```

**Success criteria:**
- ✅ 80%+ test cases passing
- ✅ Average name quality score >75/100
- ✅ Domain availability >50%
- ✅ Response time <2 minutes

### Monitoring and Observability

#### Cloud Logging

```bash
# View agent logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Agent" \
  --limit=50 \
  --format=json

# View specific events
gcloud logging read "jsonPayload.event_type=agent_event" \
  --limit=20
```

Or use **Cloud Console**: https://console.cloud.google.com/logs

#### Cost Monitoring

Set up billing alerts:

```bash
# Create billing alert at $10
gcloud alpha billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Brand Studio Budget" \
  --budget-amount=10USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

### Cost Estimation

#### Free Tier (First Month)
- Vertex AI Agent Engine: 10 agents free
- Cloud SQL: f1-micro instance free (us-central1)
- Cloud Storage: 5 GB free
- Cloud Logging: 50 GB free

#### Expected Monthly Costs

**Light Usage (100 generations/month):**

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Gemini 2.5 Flash | 500K tokens | ~$1.25 |
| Gemini 2.5 Pro | 100K tokens | ~$2.50 |
| Vector Search | 1M queries | $0.00 (free tier) |
| Cloud SQL | f1-micro | $0.00 (free tier) |
| Cloud Storage | 2 GB | $0.00 (free tier) |
| Cloud Logging | 10 GB | $0.00 (free tier) |
| **Total** | | **~$4-5/month** |

**Scale Pricing (1000 generations/month):**

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Gemini Models | 5M tokens | ~$35 |
| Vector Search | 10M queries | ~$10 |
| Cloud SQL | db-n1-standard-1 | ~$50 |
| Cloud Storage | 20 GB | ~$0.50 |
| **Total** | | **~$95/month** |

## Troubleshooting

### Common Issues

#### "Vertex AI 404 NOT_FOUND" warning
**This is normal!** The app automatically falls back to Google AI API. You can safely ignore this.

#### "GOOGLE_CLOUD_PROJECT environment variable is required"
**Solution:** Add to `.env`:
```bash
GOOGLE_CLOUD_PROJECT=test-project-local
```

#### "Could not automatically determine credentials"
**For Phase 1 (placeholder mode):** This is fine! The CLI will use placeholder data.

**For Phase 2 (real LLM calls):** Run:
```bash
gcloud auth application-default login
```

#### "Database connection failed"
**For Phase 1:** Comment out `DATABASE_URL` - database features aren't used yet.

**For Phase 2:** Verify your Cloud SQL instance is running:
```bash
gcloud sql instances list
```

#### Vector Search index creation timeout
**Solution:**
- Vector Search index creation is asynchronous and takes 30-45 minutes
- Check status: `gcloud ai indexes list --region=us-central1`
- Script will wait automatically

#### Agent deployment fails
**Solution:**
- Check `.agent_engine_config.json` is valid JSON
- Ensure all dependencies in `requirements.txt`
- Verify service account has `roles/aiplatform.user`
- Check logs: `gcloud logging read "resource.type=aiplatform.googleapis.com" --limit=50`

## Documentation References

### Key Documentation Files

- **README.md** - Project overview, setup instructions, usage guide
- **QUICKSTART.md** - Quick start guide with interactive workflow details
- **DEPLOYMENT.md** - Complete deployment guide for Vertex AI Agent Engine
- **INTERACTIVE_WORKFLOW.md** - Detailed interactive workflow documentation
- **RUN_LOCALLY.md** - Local running guide
- **ENV_SETUP_GUIDE.md** - Environment variable setup guide
- **PHASE3_SUMMARY.md** - Phase 3 implementation summary
- **ENHANCED_DOMAIN_CHECKING.md** - Enhanced domain checking features
- **USPTO_API_RECOMMENDATIONS.md** - USPTO TSDR API integration guide

### Project Structure

```
Brand-Agent/
├── src/
│   ├── agents/          # All AI agents
│   │   ├── orchestrator.py
│   │   ├── name_generator.py
│   │   ├── research_agent.py
│   │   ├── validation_agent.py
│   │   ├── seo_agent.py
│   │   └── story_agent.py
│   ├── tools/           # Utilities
│   │   ├── domain_checker.py
│   │   └── trademark_checker.py
│   ├── rag/             # RAG brand retrieval
│   ├── data/            # Brand dataset
│   ├── database/        # Session management
│   └── cli.py           # Main interface
├── test_phase2.py       # Comprehensive tests
├── .env                 # Your config
└── scripts/             # Setup and deployment scripts
```

## Document Status

✅ **PRD Complete and Validated:** This document has been consolidated and contains all necessary information:
- All required sections are present and complete
- Codebase analysis findings have been incorporated (new project - technical patterns from spec)
- YAML front-matter is complete and accurate with fidelity settings
- Requirements address the user's original problem (brand naming challenges)
- Scope boundaries are clearly defined with explicit inclusions and exclusions
- MVP-first prioritization (P0/P1/P2) to meet December 1, 2025 deadline
- Social media handle checking included (exception to section 13 exclusions)
- All section 13 optional enhancements excluded except social handles
- Standard security practices defined, no enhanced requirements
- **NEW: Consolidated setup, deployment, and usage documentation**
- **NEW: Current implementation status and progress tracking**
- **NEW: Interactive workflow documentation and benefits**
- **NEW: Comprehensive troubleshooting guide**
- **NEW: Cost estimation and monitoring guidance**
- Ready for handoff to task generation via `/prd:2:gen-tasks prd-ai-brand-studio.md`
