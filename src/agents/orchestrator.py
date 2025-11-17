"""
Orchestrator Agent for AI Brand Studio.

This agent coordinates the multi-agent workflow for brand name generation,
analyzing user briefs and delegating to specialized sub-agents.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import aiplatform
from google.cloud import logging as cloud_logging

# Try to import real ADK, fall back to mock for Phase 1
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent


# Orchestrator instruction prompt
ORCHESTRATOR_INSTRUCTION = """
You are the orchestrator for AI Brand Studio, a multi-agent system that generates
legally-clear, SEO-optimized brand names with complete brand narratives.

Your role is to:

1. ANALYZE USER'S PRODUCT BRIEF
   - Extract key attributes: product description, target audience, industry, brand personality
   - Identify the core problem the product solves
   - Understand the competitive landscape context
   - Validate that all required information is present

2. COORDINATE SUB-AGENTS TO GENERATE BRAND NAMES
   - Research Agent: Gather industry trends and competitor naming patterns
   - Name Generator Agent: Create 20-50 brand name candidates using RAG retrieval
   - Validation Agent: Check domain availability (.com, .ai, .io) and trademark conflicts (USPTO, EU IPO)
   - SEO Optimizer Agent: Analyze SEO metrics and generate meta titles/descriptions
   - Story Generator Agent: Create brand narratives and marketing copy

3. ENSURE VALIDATION BEFORE PROCEEDING
   - Verify at least 3 brand names have low trademark risk
   - Ensure at least 5 names have .com domain available
   - Stop workflow if validation fails and request regeneration (max 3 iterations)
   - Only proceed to SEO and story generation after successful validation

4. PRESENT RESULTS IN STRUCTURED FORMAT
   - Top 5 brand name recommendations with:
     * Brand name
     * Domain availability status (.com, .ai, .io)
     * Trademark risk level (low/medium/high)
     * SEO score (0-100)
     * 3-5 tagline options
     * Brand story (150-300 words)
     * Landing page hero copy (50-100 words)
     * Value proposition (20-30 words)
     * Meta title and description for SEO

WORKFLOW EXECUTION:
Execute agents in this sequence:
1. Research Agent (gather context)
2. Name Generator Agent (create candidates)
3. Validation Agent (check legal/technical availability)
4. IF validation passes:
   - SEO Optimizer Agent (optimize for search)
   - Story Generator Agent (create narratives)
5. IF validation fails:
   - Loop back to Name Generator (max 3 iterations)
6. Present final brand package

IMPORTANT CONSTRAINTS:
- Generate 20-50 brand name candidates minimum
- Ensure names are pronounceable and memorable
- Verify trademark conflicts before presenting to user
- Match brand personality specified by user (playful, professional, innovative, luxury)
- Provide complete brand package, not just names

OUTPUT FORMAT:
Return results as a structured dictionary with:
- brand_names: List of validated brand names
- domain_status: Availability for each domain extension
- trademark_risk: Risk assessment for each name
- seo_scores: SEO scores for each name
- selected_brands: Top 5 recommendations with complete brand packages
- workflow_summary: Summary of what was executed
"""


class BrandStudioOrchestrator:
    """
    Orchestrator agent that coordinates brand creation workflow.

    Uses Gemini 2.5 Flash Lite for cost-effective coordination of sub-agents.

    NOTE: Phase 1 MVP Implementation
    This wrapper class provides workflow coordination logic while sub-agents
    are being developed. In Phase 2, when all sub-agents are functional,
    orchestration will be fully delegated to self.agent (the LlmAgent) which
    will use its instruction prompt to coordinate sub-agents through the ADK
    framework. For Phase 1, we use self.agent for user brief analysis while
    placeholder methods simulate sub-agent execution.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash-lite",
        enable_cloud_logging: bool = True
    ):
        """
        Initialize the orchestrator agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use (default: gemini-2.5-flash-lite)
            enable_cloud_logging: Enable Cloud Logging integration
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.sub_agents: List = []

        # Initialize logging
        self.logger = self._setup_logging(project_id, enable_cloud_logging)
        self.logger.info(
            "Initializing BrandStudioOrchestrator",
            extra={
                'project_id': project_id,
                'location': location,
                'model_name': model_name
            }
        )

        # Initialize Vertex AI
        try:
            aiplatform.init(project=project_id, location=location)
            self.logger.info("Vertex AI initialized successfully")
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Vertex AI: {e}",
                extra={'error_type': type(e).__name__}
            )
            raise

        # Initialize orchestrator LLM agent
        self.agent = LlmAgent(
            name="brand_orchestrator",
            model=model_name,
            description="Coordinates brand creation workflow",
            instruction=ORCHESTRATOR_INSTRUCTION,
            sub_agents=self.sub_agents
        )
        self.logger.info("Orchestrator LlmAgent initialized")

    def _setup_logging(
        self,
        project_id: str,
        enable_cloud_logging: bool
    ) -> logging.Logger:
        """
        Set up logging with Cloud Logging integration.

        Args:
            project_id: Google Cloud project ID
            enable_cloud_logging: Enable Cloud Logging

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger('brand_studio.orchestrator')
        logger.setLevel(logging.INFO)

        # Console handler for local development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Cloud Logging handler for production
        if enable_cloud_logging:
            try:
                client = cloud_logging.Client(project=project_id)
                cloud_handler = client.get_default_handler()
                logger.addHandler(cloud_handler)
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Cloud Logging: {e}. "
                    "Using console logging only."
                )

        return logger

    def add_sub_agent(self, agent) -> None:
        """
        Add a sub-agent to the orchestrator's workflow.

        Args:
            agent: Sub-agent instance to add
        """
        self.sub_agents.append(agent)
        self.logger.info(
            f"Added sub-agent to orchestrator",
            extra={'agent_type': type(agent).__name__}
        )

    def analyze_user_brief(self, user_brief: dict) -> dict:
        """
        Analyze user's product brief and extract key attributes.

        Args:
            user_brief: Dictionary containing:
                - product_description: What the product does
                - target_audience: Who the product is for
                - brand_personality: Desired brand personality
                - industry: Product industry/category

        Returns:
            Dictionary with analyzed attributes and workflow plan

        Raises:
            ValueError: If required fields are missing
        """
        self.logger.info("Analyzing user brief")

        try:
            # Extract and validate required fields
            product_description = user_brief.get('product_description', '')
            target_audience = user_brief.get('target_audience', '')
            brand_personality = user_brief.get('brand_personality', 'professional')
            industry = user_brief.get('industry', 'general')

            if not product_description:
                self.logger.error("Missing required field: product_description")
                raise ValueError("product_description is required in user brief")

            # Prepare analysis result
            analysis = {
                'product_description': product_description,
                'target_audience': target_audience,
                'brand_personality': brand_personality,
                'industry': industry,
                'workflow_stages': [
                    'research',
                    'name_generation',
                    'validation',
                    'seo_optimization',
                    'story_generation'
                ]
            }

            self.logger.info(
                "User brief analyzed successfully",
                extra={
                    'industry': industry,
                    'brand_personality': brand_personality,
                    'has_target_audience': bool(target_audience)
                }
            )

            return analysis

        except Exception as e:
            self.logger.error(
                f"Error analyzing user brief: {e}",
                extra={'error_type': type(e).__name__}
            )
            raise

    def coordinate_workflow(self, user_brief: dict) -> dict:
        """
        Coordinate the complete brand creation workflow using sequential execution.

        This implements the MVP sequential workflow pattern:
        Research → Name Generation → Validation → SEO → Story

        Args:
            user_brief: User's product brief

        Returns:
            Dictionary with complete brand package
        """
        workflow_start_time = datetime.utcnow()
        self.logger.info("Starting brand creation workflow")

        # Analyze user brief
        try:
            analysis = self.analyze_user_brief(user_brief)
        except Exception as e:
            self.logger.error(f"Failed to analyze user brief: {e}")
            return {
                'status': 'failed',
                'error': f"Brief analysis failed: {str(e)}",
                'failed_stage': 'brief_analysis'
            }

        # Initialize workflow result with tracking
        workflow_result = {
            'user_brief': analysis,
            'workflow_stages': [],
            'brand_names': [],
            'validation_results': {},
            'seo_data': {},
            'brand_story': {},
            'domain_status': {},
            'trademark_risk': {},
            'seo_scores': {},
            'selected_brands': [],
            'workflow_summary': '',
            'status': 'initialized',
            'current_stage': None,
            'iteration': 0,
            'start_time': workflow_start_time.isoformat()
        }

        # Sequential execution with loop refinement (max 3 iterations)
        max_iterations = 3
        validation_passed = False

        try:
            self.logger.info(
                f"Beginning workflow execution with max {max_iterations} iterations"
            )
            while not validation_passed and workflow_result['iteration'] < max_iterations:
                workflow_result['iteration'] += 1
                self.logger.info(f"Starting workflow iteration {workflow_result['iteration']}")

                # Stage 1: Research
                try:
                    workflow_result['current_stage'] = 'research'
                    workflow_result['workflow_stages'].append('research')
                    self.logger.info("Executing research stage")
                    workflow_result['research_data'] = self._execute_research(analysis)
                    self.logger.info("Research stage completed")
                except Exception as e:
                    self.logger.error(f"Research stage failed: {e}")
                    raise

                # Stage 2: Name Generation
                try:
                    workflow_result['current_stage'] = 'name_generation'
                    workflow_result['workflow_stages'].append('name_generation')
                    self.logger.info("Executing name generation stage")
                    workflow_result['brand_names'] = self._execute_name_generation(
                        analysis,
                        workflow_result['research_data']
                    )
                    self.logger.info(
                        f"Name generation completed: {len(workflow_result['brand_names'])} names generated"
                    )
                except Exception as e:
                    self.logger.error(f"Name generation stage failed: {e}")
                    raise

                # Check if names were generated
                if not workflow_result['brand_names']:
                    self.logger.error("No brand names generated")
                    raise ValueError("No brand names generated")

                # Stage 3: Validation
                try:
                    workflow_result['current_stage'] = 'validation'
                    workflow_result['workflow_stages'].append('validation')
                    self.logger.info("Executing validation stage")
                    workflow_result['validation_results'] = self._execute_validation(
                        workflow_result['brand_names']
                    )
                    self.logger.info("Validation stage completed")
                except Exception as e:
                    self.logger.error(f"Validation stage failed: {e}")
                    raise

                # Check validation results
                validation_passed = self._check_validation_passed(
                    workflow_result['validation_results']
                )

                if not validation_passed:
                    self.logger.warning(
                        f"Validation failed in iteration {workflow_result['iteration']}"
                    )
                    if workflow_result['iteration'] < max_iterations:
                        # Log iteration and continue loop
                        workflow_result['workflow_stages'].append(
                            f'validation_failed_iteration_{workflow_result["iteration"]}'
                        )
                        self.logger.info("Retrying name generation...")
                        continue
                    else:
                        # Max iterations reached
                        self.logger.error(
                            f"Validation failed after {max_iterations} iterations"
                        )
                        workflow_result['status'] = 'validation_failed'
                        workflow_result['error'] = (
                            'Validation failed after maximum iterations'
                        )
                        workflow_result['end_time'] = datetime.utcnow().isoformat()
                        return workflow_result
                else:
                    self.logger.info("Validation passed, proceeding to content generation")

            # Validation passed - proceed to content generation
            # Stage 4: SEO Optimization
            try:
                workflow_result['current_stage'] = 'seo_optimization'
                workflow_result['workflow_stages'].append('seo_optimization')
                self.logger.info("Executing SEO optimization stage")
                workflow_result['seo_data'] = self._execute_seo_optimization(
                    workflow_result['brand_names']
                )
                self.logger.info("SEO optimization completed")
            except Exception as e:
                self.logger.error(f"SEO optimization stage failed: {e}")
                raise

            # Stage 5: Story Generation
            try:
                workflow_result['current_stage'] = 'story_generation'
                workflow_result['workflow_stages'].append('story_generation')
                self.logger.info("Executing story generation stage")
                # Select top brand name for story generation
                top_brand = self._select_top_brand(
                    workflow_result['brand_names'],
                    workflow_result['validation_results'],
                    workflow_result['seo_data']
                )
                self.logger.info(f"Selected top brand: {top_brand}")
                workflow_result['brand_story'] = self._execute_story_generation(
                    top_brand,
                    analysis
                )
                self.logger.info("Story generation completed")
            except Exception as e:
                self.logger.error(f"Story generation stage failed: {e}")
                raise

            # Mark workflow as completed and populate output fields
            workflow_result['current_stage'] = 'completed'
            workflow_result['status'] = 'completed'
            workflow_result['selected_brand'] = top_brand

            # Populate domain_status from validation results
            workflow_result['domain_status'] = workflow_result['validation_results'].get(
                'domain_availability', {}
            )

            # Populate trademark_risk from validation results
            workflow_result['trademark_risk'] = workflow_result['validation_results'].get(
                'trademark_results', {}
            )

            # Populate seo_scores from SEO data
            workflow_result['seo_scores'] = workflow_result['seo_data'].get('seo_scores', {})

            # Populate selected_brands with top 5 recommendations
            workflow_result['selected_brands'] = [
                {
                    'brand_name': top_brand,
                    'domain_status': workflow_result['domain_status'].get(top_brand, {}),
                    'trademark_risk': workflow_result['trademark_risk'].get(top_brand, 'unknown'),
                    'seo_score': workflow_result['seo_scores'].get(top_brand, 0),
                    'taglines': workflow_result['brand_story'].get('taglines', []),
                    'brand_story': workflow_result['brand_story'].get('brand_story', ''),
                    'hero_copy': workflow_result['brand_story'].get('hero_copy', ''),
                    'value_proposition': workflow_result['brand_story'].get('value_proposition', '')
                }
            ]

            # Generate workflow summary
            workflow_result['workflow_summary'] = (
                f"Completed {len(workflow_result['workflow_stages'])} stages "
                f"in {workflow_result['iteration']} iteration(s). "
                f"Generated {len(workflow_result['brand_names'])} brand names. "
                f"Selected: {top_brand}"
            )

            workflow_result['end_time'] = datetime.utcnow().isoformat()

            # Calculate total duration
            duration = (
                datetime.fromisoformat(workflow_result['end_time']) -
                datetime.fromisoformat(workflow_result['start_time'])
            ).total_seconds()

            self.logger.info(
                f"Workflow completed successfully in {duration:.2f} seconds",
                extra={
                    'duration_seconds': duration,
                    'total_iterations': workflow_result['iteration'],
                    'stages_executed': len(workflow_result['workflow_stages'])
                }
            )

        except Exception as e:
            workflow_result['status'] = 'failed'
            workflow_result['error'] = str(e)
            workflow_result['failed_stage'] = workflow_result.get('current_stage', 'unknown')
            workflow_result['end_time'] = datetime.utcnow().isoformat()

            self.logger.error(
                f"Workflow failed at stage '{workflow_result['failed_stage']}': {e}",
                extra={
                    'error_type': type(e).__name__,
                    'failed_stage': workflow_result['failed_stage'],
                    'iteration': workflow_result['iteration']
                },
                exc_info=True
            )

        return workflow_result

    def _check_validation_passed(self, validation_results: dict) -> bool:
        """
        Check if validation results meet minimum requirements.

        Requirements (from PRD):
        - At least 3 brand names with low trademark risk
        - At least 5 names with .com domain available

        Args:
            validation_results: Validation results dictionary

        Returns:
            True if validation passed, False otherwise
        """
        # Count low-risk trademarks
        low_risk_count = validation_results.get('low_risk_count', 0)

        # Count available .com domains
        available_com_count = validation_results.get('available_com_count', 0)

        # Check requirements
        has_enough_low_risk = low_risk_count >= 3
        has_enough_domains = available_com_count >= 5

        return has_enough_low_risk and has_enough_domains

    def _select_top_brand(
        self,
        brand_names: List[str],
        validation_results: dict,
        seo_data: dict
    ) -> Optional[str]:
        """
        Select the top brand name based on validation and SEO scores.

        Args:
            brand_names: List of brand names
            validation_results: Validation results
            seo_data: SEO optimization data

        Returns:
            Selected brand name or None
        """
        if not brand_names:
            return None

        # For MVP, select first brand with low risk and available .com
        # In Phase 2, this will use scoring algorithm
        return brand_names[0] if brand_names else None

    def _execute_research(self, analysis: dict) -> dict:
        """Execute research stage (placeholder)."""
        return {
            'industry_trends': [],
            'competitor_names': [],
            'naming_patterns': []
        }

    def _execute_name_generation(
        self,
        analysis: dict,
        research_data: dict
    ) -> List[str]:
        """Execute name generation stage (placeholder)."""
        # Placeholder: Will be implemented in Phase 2 with Name Generator Agent
        # For MVP testing, return sample brand names (min 20 as per PRD)
        return [
            f"Brand{i}" for i in range(1, 21)
        ]

    def _execute_validation(self, brand_names: List[str]) -> dict:
        """Execute validation stage (placeholder)."""
        # Placeholder: Will be implemented in Phase 2 with Validation Agent
        # For MVP testing, return sample data that meets validation requirements:
        # - Min 3 brands with low trademark risk
        # - Min 5 brands with .com domain available
        num_names = len(brand_names)
        return {
            'domain_availability': {
                name: {'.com': True, '.ai': True, '.io': True}
                for name in brand_names[:5]
            },
            'trademark_results': {
                name: 'low' for name in brand_names[:3]
            },
            'risk_assessment': {},
            'low_risk_count': min(3, num_names),
            'available_com_count': min(5, num_names)
        }

    def _execute_seo_optimization(self, brand_names: List[str]) -> dict:
        """Execute SEO optimization stage (placeholder)."""
        # Placeholder: Will be implemented in Phase 2 with SEO Optimizer Agent
        # For MVP testing, return sample SEO data
        return {
            'seo_scores': {name: 75.0 for name in brand_names},
            'meta_titles': {name: f"{name} | Brand Studio" for name in brand_names},
            'meta_descriptions': {
                name: f"Discover {name}, your innovative solution"
                for name in brand_names
            }
        }

    def _execute_story_generation(
        self,
        selected_name: Optional[str],
        analysis: dict
    ) -> dict:
        """Execute story generation stage (placeholder)."""
        # Placeholder: Will be implemented in Phase 2 with Story Generator Agent
        # For MVP testing, return sample brand story content
        return {
            'taglines': [
                f"{selected_name}: Innovation meets simplicity",
                f"Power your vision with {selected_name}",
                f"The future of branding starts here"
            ],
            'brand_story': f"{selected_name} is your partner in building memorable brands.",
            'hero_copy': f"Welcome to {selected_name}, where creativity meets strategy.",
            'value_proposition': f"{selected_name} delivers complete brand solutions"
        }
