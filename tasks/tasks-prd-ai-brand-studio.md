---
version: 1
fidelity_mode: strict
source_prd: tasks/prd-ai-brand-studio.md
agents:
  developer: developer-fidelity
  reviewer: quality-reviewer-fidelity
scope_preservation: true
additions_allowed: none
specification_metadata:
  source_file: tasks/prd-ai-brand-studio.md
  conversion_date: 2025-11-17
  fidelity_level: absolute
  scope_changes: none
validated: true
---

# AI Brand Studio - Implementation Tasks

## Relevant Files

*This is a new project with no existing codebase. All files below need to be created.*

### Project Structure Files to Create

- `requirements.txt` - Python dependencies (google-cloud-aiplatform, psycopg2, python-whois, requests, etc.)
- `.env.example` - Template for environment variables (no secrets)
- `.gitignore` - Ignore .env, __pycache__, venv, etc.
- `pyproject.toml` or `setup.py` - Project metadata and configuration
- `.agent_engine_config.json` - Vertex AI Agent Engine deployment configuration

### Core Agent Files (src/agents/)

- `src/agents/__init__.py` - Package initialization
- `src/agents/orchestrator.py` - Orchestrator Agent using Gemini 2.5 Flash
- `src/agents/research_agent.py` - Research Agent with Google Search tool
- `src/agents/name_generator.py` - Name Generator Agent with RAG using Gemini 2.5 Pro
- `src/agents/validation_agent.py` - Validation Agent for domain/trademark checking
- `src/agents/seo_optimizer.py` - SEO Optimizer Agent
- `src/agents/story_generator.py` - Story Generator Agent using Gemini 2.5 Pro

### Custom Tools Files (src/tools/)

- `src/tools/__init__.py` - Package initialization
- `src/tools/domain_checker.py` - Domain availability checker (whois integration)
- `src/tools/trademark_search.py` - USPTO and EU IPO trademark search
- `src/tools/social_handles.py` - Social media handle checker (Twitter, Instagram, LinkedIn)
- `src/tools/seo_analyzer.py` - SEO metrics calculator (length, pronounceability, memorability)
- `src/tools/brand_story.py` - Brand story generation helper

### RAG Implementation Files (src/rag/)

- `src/rag/__init__.py` - Package initialization
- `src/rag/vector_search.py` - Vertex AI Vector Search client and retrieval logic
- `src/rag/embeddings.py` - Text-embedding-004 integration
- `src/rag/brand_corpus.py` - Brand name corpus loader and metadata handler

### Session Management Files (src/session/)

- `src/session/__init__.py` - Package initialization
- `src/session/database.py` - Cloud SQL PostgreSQL connection and session service
- `src/session/models.py` - Database schema definitions (sessions, events, generated_brands tables)
- `src/session/memory_bank.py` - Vertex AI Memory Bank integration for long-term memory

### Workflow Files (src/workflows/)

- `src/workflows/__init__.py` - Package initialization
- `src/workflows/parallel.py` - Parallel workflow pattern implementation
- `src/workflows/sequential.py` - Sequential pipeline workflow
- `src/workflows/loop.py` - Loop refinement workflow with max iterations

### Infrastructure Files (src/infrastructure/)

- `src/infrastructure/__init__.py` - Package initialization
- `src/infrastructure/gcp_setup.py` - Google Cloud project setup automation
- `src/infrastructure/secrets.py` - Secret Manager integration for API keys
- `src/infrastructure/logging.py` - Cloud Logging integration and LoggingPlugin

### Data Files (data/)

- `data/brand_names.json` - Curated brand name corpus (5,000+ brands)
- `data/embeddings/` - Directory for generated embeddings
- `data/scripts/curate_brands.py` - Script to curate brands from Product Hunt, Fortune 500, Y Combinator

### Testing Files (tests/)

- `tests/__init__.py` - Package initialization
- `tests/integration.evalset.json` - ADK evaluation test cases (healthcare, fintech, e-commerce)
- `tests/eval_config.json` - Evaluation configuration
- `tests/test_domain_checker.py` - Unit tests for domain checker
- `tests/test_trademark_search.py` - Unit tests for trademark search
- `tests/test_seo_analyzer.py` - Unit tests for SEO analyzer
- `tests/test_agents.py` - Integration tests for agent workflows
- `tests/evaluators/name_quality.py` - Custom evaluator for name quality score
- `tests/evaluators/validation_accuracy.py` - Custom evaluator for validation accuracy
- `tests/evaluators/content_quality.py` - Custom evaluator for content quality

### CLI and Deployment Files

- `src/main.py` - Main entry point for CLI testing
- `src/cli.py` - CLI interface for user interaction
- `scripts/deploy.sh` - Deployment script for Vertex AI Agent Engine
- `scripts/setup_gcp.sh` - Google Cloud setup automation script
- `scripts/setup_vector_search.py` - Vector Search index creation script

### Database Migration Files (migrations/)

- `migrations/001_create_sessions_table.sql` - SQL migration for sessions table
- `migrations/002_create_events_table.sql` - SQL migration for events table
- `migrations/003_create_generated_brands_table.sql` - SQL migration for generated_brands table

### Documentation Files

- `README.md` - Project overview, setup instructions, usage guide
- `docs/setup.md` - Detailed setup instructions for Google Cloud and local development
- `docs/architecture.md` - Multi-agent architecture documentation
- `docs/api.md` - API documentation for custom tools
- `docs/deployment.md` - Deployment guide for Vertex AI Agent Engine
- `TESTING.md` - Testing guide with commands and evaluation criteria
- `CLAUDE.md` - Claude-specific development notes and context

### Integration Points

- **Google Search Tool:** Built-in ADK tool, no custom implementation needed
- **Vertex AI Embeddings:** Use google-cloud-aiplatform SDK for text-embedding-004
- **Cloud SQL:** Use psycopg2 or SQLAlchemy for PostgreSQL connections
- **Memory Bank:** Use Vertex AI Memory Bank API
- **Cloud Logging:** Use google-cloud-logging SDK and LoggingPlugin

### Notes

- All API keys stored in Google Cloud Secret Manager (no .env commits)
- Use ADK framework for agent orchestration and evaluation
- Follow Python best practices: type hints, docstrings, error handling
- Implement input validation to prevent injection attacks
- All external API calls must use HTTPS
- Follow 4-phase implementation roadmap: Foundation → Core → Polish → Deployment

## Tasks

### Phase 1: Foundation

- [x] 1.0 Setup Project Structure and Google Cloud Infrastructure
  - [x] 1.1 Initialize Python project with requirements.txt and pyproject.toml
  - [x] 1.2 Create .env.example with all required environment variables (GOOGLE_CLOUD_PROJECT, DATABASE_URL, etc.)
  - [x] 1.3 Setup .gitignore to exclude .env, __pycache__, venv, *.pyc, .DS_Store
  - [x] 1.4 Create Google Cloud project and enable required APIs (Vertex AI, Cloud SQL, Vector Search, Secret Manager, Logging)
  - [x] 1.5 Setup Cloud SQL PostgreSQL instance (f1-micro tier for free tier)
  - [x] 1.6 Create database migrations for sessions, events, and generated_brands tables
  - [x] 1.7 Configure Secret Manager for API key storage (Namecheap, USPTO, social media APIs)
  - [x] 1.8 Create src/ directory structure (agents/, tools/, rag/, session/, workflows/, infrastructure/)

- [x] 2.0 Implement Basic Orchestrator Agent
  - [x] 2.1 Create src/agents/orchestrator.py with LlmAgent using gemini-2.5-flash-lite
  - [x] 2.2 Write orchestrator instruction prompt to analyze user brief and coordinate sub-agents
  - [x] 2.3 Implement basic workflow coordination (sequential execution for MVP)
  - [x] 2.4 Add error handling and logging for orchestrator actions
  - [x] 2.5 Create src/main.py entry point to invoke orchestrator with sample input
  - [x] 2.6 Test orchestrator agent with basic "echo" sub-agent to verify coordination

- [x] 3.0 Implement Domain Availability Checker Tool
  - [x] 3.1 Create src/tools/domain_checker.py with check_domain_availability function
  - [x] 3.2 Integrate python-whois library to check .com, .ai, .io domains
  - [x] 3.3 Implement error handling for WHOIS lookup failures (assume available on exception)
  - [x] 3.4 Add caching mechanism (5-minute cache) to reduce API calls
  - [x] 3.5 Write unit tests in tests/test_domain_checker.py
  - [x] 3.6 Register domain checker as ADK tool for agent use

- [x] 4.0 Implement Basic Name Generator Agent (No RAG)
  - [x] 4.1 Create src/agents/name_generator.py with LlmAgent using gemini-2.5-pro
  - [x] 4.2 Write name generation prompt to create 20-50 brand names based on user brief
  - [x] 4.3 Implement support for brand personality customization (playful, professional, innovative, luxury)
  - [x] 4.4 Add multiple naming strategies in prompt: portmanteau, descriptive, invented, acronyms
  - [x] 4.5 Ensure output format includes brand name, rationale, and suggested tagline
  - [x] 4.6 Test name generator with sample inputs (healthcare app, fintech, e-commerce)

- [x] 5.0 Create Basic CLI for Testing
  - [x] 5.1 Create src/cli.py with argparse or click for command-line interaction
  - [x] 5.2 Add command to accept user brief (product description, target audience, brand personality)
  - [x] 5.3 Integrate orchestrator agent invocation from CLI
  - [x] 5.4 Display generated brand names in formatted output
  - [x] 5.5 Add verbose mode for debugging (show agent traces)
  - [x] 5.6 Test CLI with end-to-end workflow: input → orchestrator → name generator → output

### Phase 2: Core Features

- [ ] 6.0 Curate Brand Name Dataset
  - [ ] 6.1 Create data/scripts/curate_brands.py to collect brand names
  - [ ] 6.2 Scrape/collect 1,000+ brands from Product Hunt (via API or manual curation)
  - [ ] 6.3 Add 500+ Fortune 500 company names with metadata
  - [ ] 6.4 Add 500+ Y Combinator startup names
  - [ ] 6.5 Add 3,000+ additional brands from other sources (TechCrunch, curated lists)
  - [ ] 6.6 Create data/brand_names.json with metadata schema (brand_name, industry, category, year_founded, naming_strategy, syllables)
  - [ ] 6.7 Validate dataset completeness (5,000+ brands minimum)

- [ ] 7.0 Setup Vertex AI Vector Search for RAG
  - [ ] 7.1 Create src/rag/embeddings.py to generate embeddings using text-embedding-004
  - [ ] 7.2 Generate embeddings for all 5,000+ brands in dataset (batch processing)
  - [ ] 7.3 Create scripts/setup_vector_search.py to create Vertex AI Vector Search index
  - [ ] 7.4 Configure index with 768 dimensions, DOT_PRODUCT_DISTANCE, TREE_AH algorithm
  - [ ] 7.5 Upload embeddings and metadata to Cloud Storage bucket
  - [ ] 7.6 Deploy index to endpoint (public endpoint enabled)
  - [ ] 7.7 Test index with sample queries to verify retrieval accuracy

- [ ] 8.0 Integrate RAG into Name Generator Agent
  - [ ] 8.1 Create src/rag/vector_search.py with query method for K-NN search (k=50)
  - [ ] 8.2 Add industry filter to retrieval queries (metadata filtering)
  - [ ] 8.3 Update name_generator.py to call RAG retrieval before generation
  - [ ] 8.4 Augment generation prompt with retrieved similar brand examples
  - [ ] 8.5 Add fallback to non-RAG generation if retrieval fails
  - [ ] 8.6 Test RAG-enhanced name generation vs. baseline (quality comparison)

- [ ] 9.0 Implement Validation Agent
  - [ ] 9.1 Create src/agents/validation_agent.py with LlmAgent using gemini-2.5-flash-lite
  - [ ] 9.2 Integrate domain_checker tool for .com, .ai, .io availability
  - [ ] 9.3 Create src/tools/trademark_search.py for USPTO trademark search
  - [ ] 9.4 Add EU IPO trademark search to trademark_search.py
  - [ ] 9.5 Implement risk assessment logic (low/medium/high based on exact matches and similar marks)
  - [ ] 9.6 Write validation agent instruction to flag conflicts and assign risk scores
  - [ ] 9.7 Test validation agent with known trademarked names (e.g., "Apple", "Google")

- [ ] 10.0 Implement Social Media Handle Checker
  - [ ] 10.1 Create src/tools/social_handles.py with API integrations for Twitter, Instagram, LinkedIn
  - [ ] 10.2 Implement fallback to web scraping if APIs unavailable (check username availability pages)
  - [ ] 10.3 Add rate limiting and caching to avoid hitting API limits
  - [ ] 10.4 Return availability status for each platform (available/taken/unknown)
  - [ ] 10.5 Write unit tests in tests/ for social handle checker
  - [ ] 10.6 Integrate social handle checker into validation agent workflow

- [ ] 11.0 Implement Research Agent
  - [ ] 11.1 Create src/agents/research_agent.py with LlmAgent using gemini-2.5-flash-lite
  - [ ] 11.2 Integrate Google Search built-in tool for competitor research
  - [ ] 11.3 Write research agent instruction to find industry trends, competitor names, naming patterns
  - [ ] 11.4 Add RAG retrieval of similar brands to research output
  - [ ] 11.5 Format research results for use by name generator agent
  - [ ] 11.6 Test research agent with different industries (healthcare, fintech, e-commerce)

- [ ] 12.0 Implement Session Management with Cloud SQL
  - [ ] 12.1 Create src/session/database.py with PostgreSQL connection pool using psycopg2
  - [ ] 12.2 Create src/session/models.py with ORM models or raw SQL for sessions, events, generated_brands tables
  - [ ] 12.3 Implement DatabaseSessionService following ADK session management patterns
  - [ ] 12.4 Add methods to persist user inputs, generated names, and selections
  - [ ] 12.5 Implement session retrieval for conversation continuity
  - [ ] 12.6 Add session metadata storage (user preferences, brand personality)
  - [ ] 12.7 Test session persistence across multiple CLI invocations

### Phase 3: Content & Polish

- [ ] 13.0 Implement SEO Optimizer Agent
  - [ ] 13.1 Create src/agents/seo_optimizer.py with LlmAgent using gemini-2.5-flash-lite
  - [ ] 13.2 Create src/tools/seo_analyzer.py with SEO metric calculations
  - [ ] 13.3 Implement length_score (ideal 5-10 characters, 2-3 syllables)
  - [ ] 13.4 Implement pronounceability_score (vowel ratio heuristic ~40%)
  - [ ] 13.5 Implement memorability_score (unique letter patterns, no hard-to-type chars)
  - [ ] 13.6 Write SEO agent instruction to generate meta titles (50-60 chars) and descriptions (150-160 chars)
  - [ ] 13.7 Calculate overall SEO score (0-100) as weighted average of metrics
  - [ ] 13.8 Test SEO analyzer with known brand names (Stripe, Airbnb, etc.)

- [ ] 14.0 Implement Story Generator Agent
  - [ ] 14.1 Create src/agents/story_generator.py with LlmAgent using gemini-2.5-pro
  - [ ] 14.2 Write story generation prompt to create 3-5 tagline options (5-8 words each)
  - [ ] 14.3 Add brand story generation (150-300 words) matching user's brand personality
  - [ ] 14.4 Generate landing page hero section copy (50-100 words, conversion-focused)
  - [ ] 14.5 Create value proposition statement (20-30 words, clear and compelling)
  - [ ] 14.6 Add tone consistency checker (match professional/playful/innovative/luxury)
  - [ ] 14.7 Test story generator with different brand personalities and industries

- [ ] 15.0 Integrate Vertex AI Memory Bank for Long-term Memory
  - [ ] 15.1 Create src/session/memory_bank.py with Memory Bank API client
  - [ ] 15.2 Create Memory Bank collection for brand_studio_memories
  - [ ] 15.3 Store user preferences: industry, brand personality, accepted/rejected names
  - [ ] 15.4 Implement retrieval of user preferences in orchestrator agent
  - [ ] 15.5 Add learning mechanism to improve suggestions based on past feedback
  - [ ] 15.6 Test memory persistence across multiple sessions with same user_id

- [ ] 16.0 Implement Workflow Patterns (Parallel, Sequential, Loop)
  - [ ] 16.1 Create src/workflows/parallel.py for parallel execution (research + initial name generation)
  - [ ] 16.2 Create src/workflows/sequential.py for pipeline (generation → validation → SEO → story)
  - [ ] 16.3 Create src/workflows/loop.py for loop refinement (regenerate if validation fails, max 3 iterations)
  - [ ] 16.4 Update orchestrator.py to use workflow patterns based on stage
  - [ ] 16.5 Add workflow state management and error recovery
  - [ ] 16.6 Test workflow patterns with edge cases (all names fail validation, etc.)

- [ ] 17.0 Implement Context Compaction
  - [ ] 17.1 Add context compaction logic to session management
  - [ ] 17.2 Summarize conversation history when context exceeds token limit
  - [ ] 17.3 Preserve essential information (user brief, selected names, key feedback)
  - [ ] 17.4 Implement summarization using Gemini model
  - [ ] 17.5 Test context compaction with long brainstorming sessions (20+ turns)

- [ ] 18.0 Create Agent Evaluation Test Suite
  - [ ] 18.1 Create tests/integration.evalset.json with 3 test cases (healthcare, fintech, e-commerce)
  - [ ] 18.2 Define expected outputs: num_names (15-50), domain_available_com (5+), trademark_risk_low (3+), seo_score_avg (70+)
  - [ ] 18.3 Create tests/evaluators/name_quality.py custom evaluator (pronounceability, memorability, industry relevance, uniqueness)
  - [ ] 18.4 Create tests/evaluators/validation_accuracy.py to verify domain/trademark checking
  - [ ] 18.5 Create tests/evaluators/content_quality.py for tagline and story evaluation
  - [ ] 18.6 Run evaluations using `adk eval brand_studio_agent tests/integration.evalset.json`
  - [ ] 18.7 Iterate on agent prompts and logic until >90% test cases pass

- [ ] 19.0 Improve Agent Prompt Engineering
  - [ ] 19.1 Refine orchestrator prompt for better sub-agent coordination
  - [ ] 19.2 Enhance name generator prompt to produce more creative, industry-relevant names
  - [ ] 19.3 Improve validation agent prompt to better assess trademark risk
  - [ ] 19.4 Optimize SEO agent prompt for actionable keyword suggestions
  - [ ] 19.5 Polish story generator prompt for authentic, non-cliché brand narratives
  - [ ] 19.6 Add few-shot examples to prompts where beneficial
  - [ ] 19.7 Test prompt improvements against evaluation suite

- [ ] 20.0 Implement Observability with Cloud Logging
  - [ ] 20.1 Create src/infrastructure/logging.py with Cloud Logging client
  - [ ] 20.2 Integrate LoggingPlugin into all agents
  - [ ] 20.3 Add structured logging for agent actions (agent_name, action_type, inputs, outputs, duration)
  - [ ] 20.4 Log errors with full stack traces and context
  - [ ] 20.5 Add performance metrics tracking (response time per agent, total workflow duration)
  - [ ] 20.6 Create log queries in Cloud Console for debugging (filter by session_id, agent_name)
  - [ ] 20.7 Test observability by intentionally triggering errors and verifying logs

### Phase 4: Deployment

- [ ] 21.0 Prepare for Vertex AI Agent Engine Deployment
  - [ ] 21.1 Create .agent_engine_config.json with deployment settings (min_instances=0, max_instances=5, 2 CPU, 4Gi memory, 600s timeout)
  - [ ] 21.2 Add environment variables to config (GOOGLE_GENAI_USE_VERTEXAI=1, LOG_LEVEL=INFO)
  - [ ] 21.3 Ensure all dependencies are in requirements.txt with pinned versions
  - [ ] 21.4 Create scripts/deploy.sh to automate ADK deployment command
  - [ ] 21.5 Test deployment to Vertex AI Agent Engine: `adk deploy agent_engine --project=$PROJECT_ID --region=us-central1 brand_studio_agent`
  - [ ] 21.6 Verify deployed agent is accessible and functional (test with sample input)
  - [ ] 21.7 Monitor deployment logs and costs in Cloud Console

- [ ] 22.0 Complete Feature Documentation
  - [ ] 22.1 Update README.md with project overview, problem statement, value proposition
  - [ ] 22.2 Add setup instructions to README.md (Google Cloud setup, local development, environment variables)
  - [ ] 22.3 Document usage examples in README.md (CLI commands, sample inputs/outputs)
  - [ ] 22.4 Create docs/architecture.md with multi-agent system diagram and workflow patterns
  - [ ] 22.5 Create docs/api.md with custom tool documentation (domain checker, trademark search, SEO analyzer)
  - [ ] 22.6 Create docs/deployment.md with Vertex AI Agent Engine deployment guide
  - [ ] 22.7 Create TESTING.md with test commands, evaluation criteria, and how to run tests
  - [ ] 22.8 Update CLAUDE.md with development notes, project context, and fidelity requirements
  - [ ] 22.9 Add disclaimer to documentation: "Always verify trademark status with legal counsel"
  - [ ] 22.10 Review all documentation for completeness, accuracy, and clarity

- [ ] 23.0 Create Demo Video and Finalize Submission
  - [ ] 23.1 Record demo video showing end-to-end brand generation workflow (<3 minutes)
  - [ ] 23.2 Include in video: problem statement, agent system, RAG in action, validation results, complete brand package output
  - [ ] 23.3 Upload video to YouTube and add URL to README.md
  - [ ] 23.4 Write project writeup (<1500 words) for Kaggle submission
  - [ ] 23.5 Prepare submission materials: title, subtitle, card/thumbnail image
  - [ ] 23.6 Verify all requirements met: 6+ key concepts, Gemini models, Agent Engine deployment, YouTube video
  - [ ] 23.7 Submit to Kaggle competition before December 1, 2025, 11:59 AM PT

## Task Dependencies

**Critical Path:**
1. Phase 1 must complete before Phase 2 (foundation required for core features)
2. RAG setup (Tasks 6-8) must complete before advanced name generation
3. All agents (Tasks 2, 4, 9, 11, 13, 14) must be implemented before workflow integration (Task 16)
4. Evaluation suite (Task 18) can only run after all agents are functional
5. Deployment (Task 21) requires all features complete and tested

**Parallel Opportunities:**
- Tasks 3 (domain checker), 10 (social handles), 13 (SEO analyzer) can be developed in parallel
- Tasks 6 (dataset curation) and 7 (Vector Search setup) can overlap
- Documentation (Task 22) can be written incrementally throughout development

## Fidelity Checklist

Before marking tasks complete, verify:

- ✅ Implements ONLY requirements specified in PRD (no scope expansion)
- ✅ Uses specified models: Gemini 2.5 Flash (orchestrator, research, validation, SEO), Gemini 2.5 Pro (name generator, story)
- ✅ Checks specified domains: .com, .ai, .io (not other TLDs unless explicitly added)
- ✅ Searches specified trademark databases: USPTO and EU IPO (not others)
- ✅ Checks specified social platforms: Twitter, Instagram, LinkedIn (not others unless explicitly added)
- ✅ Generates specified brand package components: name, 3-5 taglines, story (150-300 words), hero copy (50-100 words), value prop (20-30 words), SEO metadata
- ✅ Uses specified database schema: sessions, events, generated_brands tables as defined in PRD
- ✅ Stays within specified cost constraints: ~$4-5/month for 100 generations
- ✅ No features from "Explicitly Excluded" section implemented (logo generation, A2A protocol, etc.)

## Next Steps

1. Review this task list with the user for approval
2. Begin Phase 1: Foundation tasks
3. Follow one sub-task at a time protocol (wait for user approval after each sub-task)
4. Mark tasks complete immediately after finishing
5. Commit changes after each completed parent task (all sub-tasks done + tests pass)
6. Use developer-fidelity agent for implementation
7. Use quality-reviewer-fidelity agent for validation against PRD

## Notes

- All code must include type hints, docstrings, and error handling
- Follow Python best practices and PEP 8 style guide
- Use Google Cloud Secret Manager for all API keys (never commit secrets)
- Test each component independently before integration
- Run evaluation suite regularly to catch regressions
- Document all assumptions and open questions in code comments
- Prioritize P0 features first, then P1, then P2 if time permits
