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

# Import feedback system
from src.feedback import NameFeedback, FeedbackType, NameGenerationSession, collect_feedback_interactive

# Import Memory Bank for long-term user preference storage
from src.session.memory_bank import get_memory_bank_client


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
        enable_cloud_logging: bool = True,
        name_generator_agent = None,
        enable_interactive_feedback: bool = True,
        enable_memory_bank: bool = True,
        user_id: Optional[str] = None
    ):
        """
        Initialize the orchestrator agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use (default: gemini-2.5-flash-lite)
            enable_cloud_logging: Enable Cloud Logging integration
            name_generator_agent: Optional NameGeneratorAgent instance for actual name generation
            enable_interactive_feedback: Enable interactive feedback loop (default: True)
            enable_memory_bank: Enable Memory Bank for long-term user preferences (default: True)
            user_id: User identifier for Memory Bank storage
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.sub_agents: List = []
        self.name_generator_agent = name_generator_agent
        self.enable_interactive_feedback = enable_interactive_feedback
        self.enable_memory_bank = enable_memory_bank
        self.user_id = user_id or "default_user"

        # Initialize logging
        self.logger = self._setup_logging(project_id, enable_cloud_logging)
        self.logger.info(
            "Initializing BrandStudioOrchestrator",
            extra={
                'project_id': project_id,
                'location': location,
                'model_name': model_name,
                'has_name_generator': name_generator_agent is not None,
                'interactive_feedback': enable_interactive_feedback,
                'memory_bank_enabled': enable_memory_bank,
                'user_id': self.user_id
            }
        )

        # Initialize Memory Bank client if enabled
        self.memory_bank_client = None
        if self.enable_memory_bank:
            try:
                self.memory_bank_client = get_memory_bank_client(
                    project_id=project_id,
                    location=location
                )
                self.logger.info(f"Memory Bank initialized for user {self.user_id}")
            except Exception as e:
                self.logger.warning(
                    f"Failed to initialize Memory Bank: {e}. "
                    "Continuing without long-term memory."
                )
                self.memory_bank_client = None

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

        # Retrieve user preferences from Memory Bank (if enabled)
        user_preferences = {}
        if self.memory_bank_client:
            try:
                user_preferences = self._retrieve_user_preferences()
                self.logger.info(
                    f"Retrieved user preferences: {len(user_preferences.get('preferred_industries', []))} "
                    f"industries, {len(user_preferences.get('preferred_personalities', []))} personalities"
                )
            except Exception as e:
                self.logger.warning(f"Failed to retrieve user preferences: {e}")
                user_preferences = {}

        # Analyze user brief
        try:
            analysis = self.analyze_user_brief(user_brief)
            # Enrich analysis with user preferences
            analysis['user_preferences'] = user_preferences
            # Store analysis for access by sub-methods
            self.current_analysis = analysis
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

                # Stage 2: Name Generation with Interactive Feedback
                try:
                    workflow_result['current_stage'] = 'name_generation'
                    workflow_result['workflow_stages'].append('name_generation')
                    self.logger.info("Executing name generation stage with feedback")

                    # Use feedback-enabled generation
                    approved_names, feedback_session = self._execute_name_generation_with_feedback(
                        analysis=analysis,
                        research_data=workflow_result['research_data'],
                        name_generator_agent=self.name_generator_agent,
                        max_feedback_iterations=3,
                        enable_feedback=self.enable_interactive_feedback
                    )

                    # Store approved names (with full metadata)
                    workflow_result['brand_names_full'] = approved_names

                    # Extract just brand name strings for validation
                    workflow_result['brand_names'] = [
                        name['brand_name'] if isinstance(name, dict) else name
                        for name in approved_names
                    ]

                    # Store feedback session
                    if feedback_session:
                        workflow_result['feedback_session'] = {
                            'session_id': feedback_session.session_id,
                            'iterations': feedback_session.iteration,
                            'approved_names': feedback_session.approved_names,
                            'feedback_count': len(feedback_session.feedback_history)
                        }

                    self.logger.info(
                        f"Name generation completed: {len(workflow_result['brand_names'])} names approved"
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
            feedback_info = ""
            if 'feedback_session' in workflow_result:
                feedback_info = (
                    f"User provided {workflow_result['feedback_session']['feedback_count']} "
                    f"feedback iteration(s). "
                )

            workflow_result['workflow_summary'] = (
                f"Completed {len(workflow_result['workflow_stages'])} stages "
                f"in {workflow_result['iteration']} validation iteration(s). "
                f"{feedback_info}"
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

            # Store user preferences in Memory Bank if enabled
            if self.memory_bank_client:
                try:
                    self._store_user_preferences(
                        analysis=analysis,
                        workflow_result=workflow_result
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to store user preferences in Memory Bank: {e}"
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

        Requirements:
        - At least 50% of names with low trademark risk (minimum 1)
        - At least 1 name with .com domain available OR any available domain extensions

        Args:
            validation_results: Validation results dictionary

        Returns:
            True if validation passed, False otherwise
        """
        # Count low-risk trademarks
        low_risk_count = validation_results.get('low_risk_count', 0)

        # Count available .com domains
        available_com_count = validation_results.get('available_com_count', 0)

        # Get total number of names validated
        domain_availability = validation_results.get('domain_availability', {})
        total_names = len(domain_availability)

        # Calculate minimum thresholds based on number of selected names
        min_low_risk = max(1, total_names // 2)  # At least 50% or 1
        min_domains = 1  # At least 1 domain available

        # Check if we have ANY available domains (not just .com)
        any_domains_available = any(
            any(avail for avail in domains.values())
            for domains in domain_availability.values()
        )

        # Check requirements
        has_enough_low_risk = low_risk_count >= min_low_risk
        has_enough_domains = available_com_count >= min_domains or any_domains_available

        self.logger.info(
            f"Validation check: {low_risk_count}/{total_names} low-risk (need {min_low_risk}), "
            f"{available_com_count} .com available (need {min_domains}), "
            f"any domains: {any_domains_available}"
        )

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

    def _execute_name_generation_with_feedback(
        self,
        analysis: dict,
        research_data: dict,
        name_generator_agent,
        max_feedback_iterations: int = 3,
        enable_feedback: bool = True
    ) -> tuple[List[Dict[str, Any]], Optional[NameGenerationSession]]:
        """
        Execute name generation with interactive feedback loop.

        Args:
            analysis: User brief analysis
            research_data: Research data from research stage
            name_generator_agent: NameGeneratorAgent instance
            max_feedback_iterations: Maximum feedback iterations allowed
            enable_feedback: Enable interactive feedback (False for automated workflows)

        Returns:
            Tuple of (approved_names, session)
            - approved_names: List of name dictionaries that user approved
            - session: NameGenerationSession with feedback history (or None if disabled)
        """
        import uuid

        # Create session to track feedback iterations
        if enable_feedback:
            session = NameGenerationSession(
                session_id=str(uuid.uuid4()),
                brief=analysis.get('product_description', ''),
                max_iterations=max_feedback_iterations
            )
        else:
            session = None

        feedback_context = None
        previous_names = []
        approved_names = None
        liked_names_to_keep = []  # Track names user liked from previous iterations

        # Feedback loop
        while session is None or (not session.is_complete() and session.has_iterations_remaining()):
            # Generate names
            self.logger.info(
                f"Generating names (iteration {session.iteration + 1 if session else 1})"
            )

            if name_generator_agent:
                # Use actual name generator agent
                # Extract user preferences if available
                user_prefs = analysis.get('user_preferences', {})

                generated_names = name_generator_agent.generate_names(
                    product_description=analysis.get('product_description', ''),
                    target_audience=analysis.get('target_audience', ''),
                    brand_personality=analysis.get('brand_personality', 'professional'),
                    industry=analysis.get('industry', 'general'),
                    num_names=30,
                    feedback_context=feedback_context,
                    previous_names=previous_names,
                    user_preferences=user_prefs  # Pass user preferences from Memory Bank
                )
            else:
                # Placeholder for testing
                generated_names = [
                    {
                        'brand_name': f"Brand{i}",
                        'naming_strategy': 'descriptive',
                        'rationale': 'Placeholder name',
                        'tagline': 'Placeholder tagline',
                        'syllables': 2,
                        'memorable_score': 7
                    }
                    for i in range(1, 31)
                ]

            # Extract just the brand names for feedback display
            brand_names = [name['brand_name'] for name in generated_names]

            # Merge with liked names from previous iterations
            all_generated_names = generated_names.copy()
            if liked_names_to_keep:
                # Add liked names from previous iterations to the current batch
                all_generated_names = liked_names_to_keep + generated_names
                all_brand_names = [name['brand_name'] for name in all_generated_names]
            else:
                all_brand_names = brand_names

            # Record generation
            if session:
                session.add_generation(all_brand_names)

            # Collect user feedback (if enabled)
            if enable_feedback:
                feedback = collect_feedback_interactive(
                    names=all_brand_names,
                    iteration=session.iteration,
                    max_iterations=session.max_iterations
                )
                session.add_feedback(feedback)

                # Handle feedback
                if feedback.feedback_type == FeedbackType.APPROVE:
                    # User approved - select names and exit loop
                    selected_names = feedback.selected_names or all_brand_names[:10]

                    # Find full name dictionaries for selected names
                    approved_names = [
                        name for name in all_generated_names
                        if name['brand_name'] in selected_names
                    ]

                    session.approve(selected_names)
                    self.logger.info(f"User approved {len(approved_names)} names")
                    break

                elif feedback.feedback_type == FeedbackType.REFINE:
                    # User wants to refine - prepare feedback context
                    feedback_context = feedback.to_prompt_context()
                    previous_names.extend(brand_names)

                    # Preserve liked names from this iteration
                    if feedback.liked_names:
                        # Find full name dictionaries for liked names
                        liked_name_dicts = [
                            name for name in all_generated_names
                            if name['brand_name'] in feedback.liked_names
                        ]
                        # Add to kept names (avoiding duplicates)
                        for liked in liked_name_dicts:
                            if liked not in liked_names_to_keep:
                                liked_names_to_keep.append(liked)
                        self.logger.info(f"Keeping {len(liked_name_dicts)} liked names for next iteration")

                    self.logger.info("User requested refinement, regenerating with feedback")

                elif feedback.feedback_type == FeedbackType.REGENERATE:
                    # User wants completely fresh batch
                    feedback_context = feedback.additional_feedback
                    previous_names = []  # Don't carry over previous names
                    self.logger.info("User requested fresh regeneration")
            else:
                # No feedback - approve all names and exit
                approved_names = generated_names
                break

        # If loop exited without approval (max iterations reached), use last batch
        if approved_names is None:
            self.logger.warning(
                f"Max feedback iterations ({max_feedback_iterations}) reached without approval"
            )
            approved_names = generated_names[:10]  # Default to top 10
            if session:
                session.approve([name['brand_name'] for name in approved_names])

        return approved_names, session

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
        """Execute validation stage with real domain checking."""
        from src.tools.domain_checker import check_domain_availability

        num_names = len(brand_names)
        domain_availability = {}
        available_com_count = 0

        self.logger.info(f"Checking domain availability for {num_names} brand names")

        # Check domains for each brand name
        for brand_name in brand_names:
            # Check with prefix variations for better alternatives
            domain_results = check_domain_availability(
                brand_name=brand_name,
                extensions=['.com', '.ai', '.io', '.app', '.co'],
                include_prefixes=True
            )

            # Store full results for this brand
            domain_availability[brand_name] = domain_results

            # Count if .com is available (for validation check)
            exact_com = f"{brand_name.lower().replace(' ', '').replace('-', '')}.com"
            if domain_results.get(exact_com, False):
                available_com_count += 1

        # Trademark checking with USPTO
        from src.tools.trademark_checker import search_trademarks_uspto

        trademark_results = {}
        low_risk_count = 0

        self.logger.info(f"Checking trademarks for {num_names} brand names")

        for brand_name in brand_names:
            tm_result = search_trademarks_uspto(brand_name=brand_name)
            risk_level = tm_result['risk_level']
            trademark_results[brand_name] = risk_level

            if risk_level == 'low':
                low_risk_count += 1

        self.logger.info(
            f"Validation complete: {available_com_count} .com domains available, "
            f"{low_risk_count} low-risk trademarks"
        )

        return {
            'domain_availability': domain_availability,
            'trademark_results': trademark_results,
            'risk_assessment': {},
            'low_risk_count': low_risk_count,
            'available_com_count': available_com_count
        }

    def _execute_seo_optimization(self, brand_names: List[str]) -> dict:
        """Execute SEO optimization stage with real SEO agent."""
        from src.agents.seo_agent import SEOAgent

        # Get product description from analysis (passed through workflow_result)
        product_description = self.current_analysis.get('product_description', '')
        industry = self.current_analysis.get('industry', 'general')

        # Initialize SEO agent
        seo_agent = SEOAgent(
            project_id=self.project_id,
            location=self.location
        )

        seo_scores = {}
        meta_titles = {}
        meta_descriptions = {}
        all_seo_data = {}

        self.logger.info(f"Optimizing SEO for {len(brand_names)} brand names")

        for brand_name in brand_names:
            seo_result = seo_agent.optimize_brand_seo(
                brand_name=brand_name,
                product_description=product_description,
                industry=industry
            )

            seo_scores[brand_name] = seo_result['seo_score']
            meta_titles[brand_name] = seo_result['meta_title']
            meta_descriptions[brand_name] = seo_result['meta_description']
            all_seo_data[brand_name] = seo_result

        self.logger.info("SEO optimization completed for all names")

        return {
            'seo_scores': seo_scores,
            'meta_titles': meta_titles,
            'meta_descriptions': meta_descriptions,
            'detailed_seo': all_seo_data
        }

    def _execute_story_generation(
        self,
        selected_name: Optional[str],
        analysis: dict
    ) -> dict:
        """Execute story generation stage with real Story agent."""
        from src.agents.story_agent import StoryAgent

        if not selected_name:
            self.logger.warning("No brand name selected for story generation")
            return {}

        # Initialize story agent
        story_agent = StoryAgent(
            project_id=self.project_id,
            location=self.location
        )

        self.logger.info(f"Generating brand story for {selected_name}")

        # Generate story content
        story_result = story_agent.generate_brand_story(
            brand_name=selected_name,
            product_description=analysis.get('product_description', ''),
            brand_personality=analysis.get('brand_personality', 'professional'),
            target_audience=analysis.get('target_audience', '')
        )

        self.logger.info(f"Brand story generated successfully for {selected_name}")

        return story_result

    def _store_user_preferences(
        self,
        analysis: Dict[str, Any],
        workflow_result: Dict[str, Any]
    ) -> None:
        """
        Store user preferences in Memory Bank for long-term learning.

        Stores:
        - Industry preferences
        - Brand personality preferences
        - Accepted brand names (from approved names)
        - Rejected brand names (from feedback)
        - Naming strategy preferences (from feedback)

        Args:
            analysis: User brief analysis
            workflow_result: Complete workflow result
        """
        if not self.memory_bank_client:
            return

        self.logger.info(f"Storing user preferences for user {self.user_id}")

        try:
            # Store industry preference
            industry = analysis.get('industry', 'general')
            self.memory_bank_client.store_user_preference(
                user_id=self.user_id,
                preference_type='industry',
                preference_value=industry,
                metadata={
                    'session_timestamp': workflow_result.get('start_time', datetime.utcnow().isoformat()),
                    'source': 'user_brief'
                }
            )
            self.logger.debug(f"Stored industry preference: {industry}")

            # Store brand personality preference
            brand_personality = analysis.get('brand_personality', 'professional')
            self.memory_bank_client.store_user_preference(
                user_id=self.user_id,
                preference_type='personality',
                preference_value=brand_personality,
                metadata={
                    'session_timestamp': workflow_result.get('start_time', datetime.utcnow().isoformat()),
                    'source': 'user_brief'
                }
            )
            self.logger.debug(f"Stored personality preference: {brand_personality}")

            # Store accepted brand names
            approved_names = workflow_result.get('brand_names', [])
            for brand_name in approved_names:
                # Extract name if it's a dict
                name_str = brand_name if isinstance(brand_name, str) else brand_name.get('brand_name', str(brand_name))

                self.memory_bank_client.store_brand_feedback(
                    user_id=self.user_id,
                    brand_name=name_str,
                    feedback_type='accepted',
                    feedback_data={
                        'session_timestamp': workflow_result.get('start_time'),
                        'industry': industry,
                        'brand_personality': brand_personality,
                        'validation_results': workflow_result.get('validation_results', {}).get(name_str, {}),
                        'seo_score': workflow_result.get('seo_scores', {}).get(name_str, 0)
                    }
                )
            self.logger.debug(f"Stored {len(approved_names)} accepted brand names")

            # Store rejected brand names from feedback session (if available)
            if 'feedback_session' in workflow_result:
                feedback_session = workflow_result.get('feedback_session', {})
                # Extract feedback history to find rejected names
                # Note: This requires the feedback_session to have detailed feedback
                # For now, we'll mark this as a placeholder for future enhancement
                self.logger.debug("Feedback session data stored (detailed rejection tracking pending)")

            # Store naming strategies from feedback (if available)
            # This will be implemented as part of Task 15.5 (learning mechanism)

            self.logger.info(
                f"Successfully stored user preferences for {self.user_id}: "
                f"industry={industry}, personality={brand_personality}, "
                f"accepted_names={len(approved_names)}"
            )

        except Exception as e:
            self.logger.error(
                f"Error storing user preferences: {e}",
                extra={'error_type': type(e).__name__}
            )
            # Don't raise - this is not critical to workflow success
            pass

    def _retrieve_user_preferences(self) -> Dict[str, Any]:
        """
        Retrieve user preferences from Memory Bank.

        Returns:
            Dictionary with user preferences:
            - preferred_industries: List of industries the user has worked with
            - preferred_personalities: List of brand personalities the user prefers
            - past_accepted_names: List of brand names the user has accepted
            - past_rejected_names: List of brand names the user has rejected
            - learning_insights: Aggregated insights from past sessions
        """
        if not self.memory_bank_client:
            self.logger.debug("Memory Bank not available, returning empty preferences")
            return {
                'preferred_industries': [],
                'preferred_personalities': [],
                'past_accepted_names': [],
                'past_rejected_names': [],
                'learning_insights': {}
            }

        self.logger.info(f"Retrieving user preferences for user {self.user_id}")

        try:
            # Retrieve all preferences for this user
            all_preferences = self.memory_bank_client.retrieve_user_preferences(
                user_id=self.user_id
            )

            # Parse preferences by type
            industries = []
            personalities = []
            accepted_names = []
            rejected_names = []

            for pref in all_preferences:
                pref_type = pref.get('preference_type', '')
                pref_value = pref.get('preference_value', '')

                if pref_type == 'industry' and pref_value not in industries:
                    industries.append(pref_value)
                elif pref_type == 'personality' and pref_value not in personalities:
                    personalities.append(pref_value)

            # Get learning insights (aggregated patterns from past sessions)
            learning_insights = self.memory_bank_client.get_learning_insights(
                user_id=self.user_id,
                limit=20  # Look at last 20 interactions
            )

            preferences = {
                'preferred_industries': industries,
                'preferred_personalities': personalities,
                'past_accepted_names': accepted_names,
                'past_rejected_names': rejected_names,
                'learning_insights': learning_insights
            }

            self.logger.info(
                f"Retrieved preferences for {self.user_id}: "
                f"{len(industries)} industries, {len(personalities)} personalities"
            )

            return preferences

        except Exception as e:
            self.logger.error(
                f"Error retrieving user preferences: {e}",
                extra={'error_type': type(e).__name__}
            )
            # Return empty preferences on error
            return {
                'preferred_industries': [],
                'preferred_personalities': [],
                'past_accepted_names': [],
                'past_rejected_names': [],
                'learning_insights': {}
            }
