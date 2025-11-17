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

## Document Status

✅ **PRD Complete and Validated:** This document has been validated and contains all necessary information:
- All required sections are present and complete
- Codebase analysis findings have been incorporated (new project - technical patterns from spec)
- YAML front-matter is complete and accurate with fidelity settings
- Requirements address the user's original problem (brand naming challenges)
- Scope boundaries are clearly defined with explicit inclusions and exclusions
- MVP-first prioritization (P0/P1/P2) to meet December 1, 2025 deadline
- Social media handle checking included (exception to section 13 exclusions)
- All section 13 optional enhancements excluded except social handles
- Standard security practices defined, no enhanced requirements
- Ready for handoff to task generation via `/prd:2:gen-tasks prd-ai-brand-studio.md`
