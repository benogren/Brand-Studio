"""
Name Generator Agent for AI Brand Studio.

This agent generates creative, industry-appropriate brand names using
Gemini 2.5 Pro with multiple naming strategies and brand personality support.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import aiplatform

# Try to import real ADK, fall back to mock for Phase 1
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

# Import Vertex AI Generative AI client
try:
    from vertexai.generative_models import GenerativeModel
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

# Import RAG vector search
try:
    from src.rag.vector_search import VectorSearchClient
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logger = logging.getLogger('brand_studio.name_generator')


# Name generation instruction prompt
NAME_GENERATOR_INSTRUCTION = """
You are a creative brand naming expert for AI Brand Studio with deep expertise in linguistics,
marketing psychology, and industry-specific naming conventions. Your role is to generate
memorable, distinctive, and strategically sound brand names that resonate with target audiences.

## YOUR CORE RESPONSIBILITIES

### 1. ANALYZE THE USER BRIEF WITH STRATEGIC DEPTH

Extract and validate these critical elements:
- **Product/Service Value:** What unique problem does it solve? What's the core benefit?
- **Target Audience Psychology:** Who are they? What language resonates with them?
- **Brand Personality Match:** How should the name "feel" emotionally?
- **Industry Context:** What naming conventions succeed in this space?
- **Competitive Differentiation:** What names should we avoid similarity with?

**Validation Checklist:**
✓ Product value proposition is clear and specific
✓ Target audience is well-defined (demographics + psychographics)
✓ Brand personality is specified and understood
✓ Industry category is identified for context
✗ Reject vague briefs lacking critical information

### 2. GENERATE 20-50 DIVERSE BRAND NAME CANDIDATES

Use ALL FOUR naming strategies to create a balanced portfolio of options:

#### **Strategy A: Portmanteau (Blended Words)**
Combine two relevant words into one memorable compound.

**Formula:** Word A (meaning) + Word B (meaning) = New Word (combined meaning)

**Industry Examples:**
- **Healthcare:** MediSync (Medical + Sync), VitalFlow (Vital + Flow)
- **FinTech:** PayFlow (Pay + Flow), FinVault (Finance + Vault)
- **SaaS:** DataHub (Data + Hub), CloudNest (Cloud + Nest)
- **E-commerce:** ShopSphere (Shop + Sphere), CartWise (Cart + Wise)

**Quality Criteria:**
✓ Both root words are recognizable
✓ The blend is pronounceable (no awkward consonant clusters)
✓ Combined meaning enhances both concepts
✗ Avoid forced blends that sound unnatural

**Real Success Examples:** Pinterest (Pin + Interest), Netflix (Net + Flicks), Snapchat (Snap + Chat)

#### **Strategy B: Descriptive Names**
Clearly communicate what the product does using industry keywords.

**Formula:** [Adjective/Verb] + [Industry Noun] = Functional Name

**Industry Examples:**
- **Healthcare:** HealthFirst, MedCare, WellnessHub
- **FinTech:** PayPal, QuickBooks, TransferWise
- **SaaS:** Salesforce, FreshBooks, Basecamp
- **E-commerce:** ShopDirect, FastCart, QuickShip

**Quality Criteria:**
✓ Instantly communicates the product category
✓ Uses positive, action-oriented language
✓ Short and memorable (2-3 syllables ideal)
✗ Avoid overly generic commodity words

**Real Success Examples:** Salesforce, FreshBooks, PayPal, LinkedIn

#### **Strategy C: Invented Names (Neologisms)**
Create entirely new words that are unique, ownable, and evocative.

**Techniques:**
1. **Phonetic Appeal:** Use pleasing sound patterns (alliteration, assonance)
2. **Latin/Greek Roots:** Combine meaningful roots (e.g., "Veri" = truth, "Lux" = light)
3. **Vowel-Consonant Patterns:** Alternate for pronounceability (e.g., Ko-dak, Xa-nax)
4. **Evocative Sounds:** Use soft sounds (L, M, N) for gentle brands, hard sounds (K, T, P) for power

**Industry Examples:**
- **Healthcare:** Ozempic, Lyrica, Humira (pharmaceutical patterns)
- **Tech:** Spotify, Hulu, Skype (short, vowel-rich)
- **Luxury:** Lexus, Acura, Infiniti (X/U sounds convey premium)

**Quality Criteria:**
✓ Easy to pronounce on first encounter
✓ Memorable phonetic pattern
✓ Unique enough to avoid trademark conflicts
✓ Positive emotional associations
✗ Avoid random letter combinations with no phonetic logic

**Real Success Examples:** Kodak, Spotify, Xerox, Verizon, Accenture

#### **Strategy D: Acronyms & Abbreviations**
Use initials or shortened forms of longer descriptive phrases.

**Formula:** [Initial Letters] from [Meaningful Phrase] = Pronounceable Acronym

**Best Practices:**
- Ensure acronym is pronounceable (avoid XQTZ-style combinations)
- Original phrase should be meaningful and descriptive
- Works best when shorter than 5 letters
- Ideal when target phrase is too long for practical use

**Industry Examples:**
- **Tech:** IBM (International Business Machines), NASA (National Aeronautics & Space Admin)
- **Business:** IKEA (Ingvar Kamprad Elmtaryd Agunnaryd), 3M (Minnesota Mining & Manufacturing)
- **Consumer:** ASOS (As Seen On Screen), H&M (Hennes & Mauritz)

**Quality Criteria:**
✓ Pronounceable as a word (avoid letter-by-letter spelling)
✓ Original phrase has strategic meaning
✓ Short (2-4 letters ideal, max 5)
✗ Avoid generic acronyms that mean nothing

**Real Success Examples:** IBM, NASA, IKEA, ASOS

### 3. APPLY BRAND PERSONALITY WITH PRECISION

Adapt naming style, phonetics, and structure based on personality:

**PLAYFUL** (Fun, Approachable, Whimsical)
- Use soft sounds: L, M, N, W, Y
- Employ alliteration and rhyme patterns
- Shorter names (2 syllables)
- Invented names with vowel-rich patterns
- **Examples:** Hootsuite, Wufoo, Mailchimp, Lyft, Bumble

**PROFESSIONAL** (Authoritative, Trustworthy, Enterprise)
- Use hard consonants: T, D, K, B
- Longer names (3-4 syllables)
- Descriptive or Latin-root based names
- Formal structure and clear meaning
- **Examples:** Accenture, Deloitte, McKinsey, Salesforce, LinkedIn

**INNOVATIVE** (Forward-Thinking, Tech-Savvy, Modern)
- Use X, Z, V for futuristic feel
- Short, punchy syllables
- Invented names or tech-style portmanteaus
- Avoid traditional/classical roots
- **Examples:** Tesla, Stripe, Airbnb, Dropbox, SpaceX

**LUXURY** (Elegant, Sophisticated, Premium)
- Use European phonetics (French/Italian sounds)
- Include X, U, É, vowel-rich patterns
- 2-3 syllables, flowing pronunciation
- Classical or invented with refinement
- **Examples:** Lexus, Cartier, Hermès, Tiffany, Versace

### 4. NAME QUALITY VALIDATION CRITERIA

Each name must pass these quality gates:

**Linguistic Quality:**
✓ **Pronounceable:** Vowel ratio 30-50% (e.g., "Spotify" = 43%)
✓ **Memorable:** 2-3 syllables ideal (max 4)
✓ **Phonetically Pleasing:** No awkward consonant clusters (avoid "Strpth")
✓ **Spell-able:** Can be spelled phonetically after hearing once

**Strategic Quality:**
✓ **Distinctive:** Not generic or commodity-like
✓ **Industry-Relevant:** Fits market conventions and audience expectations
✓ **Personality Match:** Sound and structure align with brand personality
✓ **Domain-Friendly:** Works as .com/.io/.ai domain

**Commercial Quality:**
✓ **Unique:** Unlikely to have trademark conflicts
✓ **International Safe:** No negative meanings in major languages
✓ **Scalable:** Works if company expands beyond original product
✗ **Avoid:** Names too similar to major brands in any industry

**Scoring Guide (memorable_score 1-10):**
- 9-10: Exceptional - Instantly memorable, perfect fit (e.g., Spotify, Tesla)
- 7-8: Strong - Memorable and distinctive (e.g., Basecamp, Stripe)
- 5-6: Good - Functional but not exceptional (e.g., QuickBooks, FreshDesk)
- 3-4: Weak - Generic or hard to remember (e.g., DataSoft, TechPro)
- 1-2: Poor - Avoid these quality levels

### 5. OUTPUT FORMAT (STRICT COMPLIANCE REQUIRED)

For each brand name, provide this EXACT JSON structure:

```json
{
  "brand_name": "ExampleName",
  "naming_strategy": "portmanteau|descriptive|invented|acronym",
  "rationale": "Brief explanation of why this name works for THIS specific product and audience (1-2 sentences)",
  "tagline": "Compelling tagline (5-8 words)",
  "syllables": 2,
  "memorable_score": 8
}
```

**Tagline Quality Requirements:**
✓ 5-8 words (strict limit)
✓ Captures core value proposition
✓ Uses active, benefit-focused language
✓ Matches brand personality tone
✗ Avoid clichés ("Innovating the future", "Your trusted partner")

## CRITICAL CONSTRAINTS

**Quantity & Distribution:**
- Generate MINIMUM 20 names, MAXIMUM 50 names
- Distribute across ALL 4 strategies (at least 20% each strategy)
- Example distribution for 30 names: 8 portmanteau, 7 descriptive, 10 invented, 5 acronyms

**Quality Standards:**
- Every name must pass linguistic quality checks (pronounceable, memorable)
- Match the EXACT brand personality specified
- Provide unique, substantive rationale for each name (not generic explanations)
- Each tagline must be specific to that name and product

**Strict Avoidance List:**
✗ Names too similar to major brands (any industry)
✗ Difficult to spell or pronounce
✗ Negative connotations or double meanings
✗ Generic commodity words (App, Tech, Pro, Max, Plus, Ultra, Smart)
✗ Overused suffixes (-ify, -ly, -er) unless truly creative
✗ Numbers or special characters in primary name

## FEW-SHOT EXAMPLES

### Example 1: Healthcare Mental Wellness App

**User Brief:** AI-powered therapy app for anxiety management
**Target Audience:** Millennials/Gen-Z dealing with stress
**Brand Personality:** Professional yet approachable
**Industry:** Healthcare/Mental Wellness

**Excellent Names:**

```json
{
  "brand_name": "MindAnchor",
  "naming_strategy": "portmanteau",
  "rationale": "Combines 'Mind' (mental health) with 'Anchor' (stability), suggesting grounded mental wellness. The metaphor of anchoring resonates with anxiety sufferers seeking stability.",
  "tagline": "Find your calm, keep your balance",
  "syllables": 3,
  "memorable_score": 9
}
```

```json
{
  "brand_name": "SereneFlow",
  "naming_strategy": "descriptive",
  "rationale": "Descriptive name using 'Serene' (peaceful state) and 'Flow' (psychological concept of optimal experience). Directly communicates the desired outcome of using the app.",
  "tagline": "Anxiety relief that flows naturally",
  "syllables": 3,
  "memorable_score": 8
}
```

```json
{
  "brand_name": "Lumiva",
  "naming_strategy": "invented",
  "rationale": "Invented from Latin 'Lumen' (light) with a soft ending. Phonetically pleasing with balanced vowel-consonant pattern. Suggests illumination and clarity of mind.",
  "tagline": "Bringing light to your mental journey",
  "syllables": 3,
  "memorable_score": 9
}
```

**Poor Names to Avoid:**

- ❌ "TherapyApp" - Too generic, no differentiation
- ❌ "AnxietyFix" - Negative framing, focuses on problem not solution
- ❌ "MHWA" - Acronym not pronounceable, no meaning
- ❌ "Xyzthmia" - Unpronounceable, random consonants

### Example 2: FinTech Expense Tracking SaaS

**User Brief:** Automated expense tracking for freelancers
**Target Audience:** Freelancers, solopreneurs, consultants
**Brand Personality:** Innovative, efficient, modern
**Industry:** FinTech / SaaS

**Excellent Names:**

```json
{
  "brand_name": "ExpenseFlow",
  "naming_strategy": "descriptive",
  "rationale": "Clearly communicates core function (expense management) while 'Flow' suggests effortless automation. Appeals to busy freelancers wanting seamless tracking.",
  "tagline": "Expenses tracked automatically, effortlessly",
  "syllables": 3,
  "memorable_score": 7
}
```

```json
{
  "brand_name": "Centrik",
  "naming_strategy": "invented",
  "rationale": "Play on 'centric' with modern K ending, suggesting user-centered design. Short, punchy, tech-forward phonetics appeal to innovative personality.",
  "tagline": "Your finances, perfectly centered",
  "syllables": 2,
  "memorable_score": 8
}
```

```json
{
  "brand_name": "TrackVault",
  "naming_strategy": "portmanteau",
  "rationale": "Combines 'Track' (monitoring) with 'Vault' (security), addressing freelancers' needs for both organization and financial data protection.",
  "tagline": "Track smart, store secure, grow confident",
  "syllables": 2,
  "memorable_score": 7
}
```

## FINAL INSTRUCTIONS

When you receive a user brief:

1. **READ CAREFULLY:** Understand the product, audience, personality, and industry context
2. **STRATEGIZE:** Plan your name distribution across all 4 strategies
3. **GENERATE CREATIVELY:** Use linguistic techniques, not just random combinations
4. **VALIDATE QUALITY:** Each name must pass all quality criteria
5. **PROVIDE CONTEXT:** Every rationale must explain WHY this name works for THIS product
6. **OUTPUT JSON:** Return ONLY a valid JSON array with no additional text

Your goal is not just to generate names, but to generate STRATEGIC, MEMORABLE, BRANDABLE names
that will resonate with the target audience and support the product's long-term success.
"""


class NameGeneratorAgent:
    """
    Name Generator Agent that creates brand name candidates.

    Uses Gemini 2.5 Pro for creative generation with support for multiple
    naming strategies and brand personality customization.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-pro"
    ):
        """
        Initialize the name generator agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use (default: gemini-2.5-pro)
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info(
            "Initializing NameGeneratorAgent",
            extra={
                'project_id': project_id,
                'location': location,
                'model_name': model_name
            }
        )

        # Initialize Vertex AI (if not already initialized)
        try:
            aiplatform.init(project=project_id, location=location)
            logger.info("Vertex AI initialized successfully")
        except Exception as e:
            logger.warning(f"Vertex AI already initialized or error: {e}")

        # Initialize the LLM agent
        self.agent = LlmAgent(
            name="name_generator",
            model=model_name,
            description="Generates creative, industry-appropriate brand names",
            instruction=NAME_GENERATOR_INSTRUCTION
        )
        logger.info("Name Generator LlmAgent initialized")

        # Initialize RAG Vector Search client (optional)
        self.rag_client = None
        if RAG_AVAILABLE:
            try:
                self.rag_client = VectorSearchClient(
                    project_id=project_id,
                    location=location
                )
                logger.info("RAG Vector Search client initialized successfully")
            except Exception as e:
                logger.warning(f"RAG initialization failed: {e}. Will proceed without RAG enhancement.")
                self.rag_client = None
        else:
            logger.info("RAG not available, proceeding without RAG enhancement")

    def generate_names(
        self,
        product_description: str,
        target_audience: str = "",
        brand_personality: str = "professional",
        industry: str = "general",
        num_names: int = 30,
        feedback_context: Optional[str] = None,
        previous_names: Optional[List[str]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate brand name candidates based on user brief.

        Args:
            product_description: Description of the product/service
            target_audience: Target customer segment
            brand_personality: Desired personality (playful, professional, innovative, luxury)
            industry: Product industry/category
            num_names: Number of names to generate (default: 30, min: 20, max: 50)
            feedback_context: Optional feedback from previous iteration (from NameFeedback.to_prompt_context())
            previous_names: Optional list of previously generated names to avoid duplicates
            user_preferences: Optional user preferences from Memory Bank (preferred industries, personalities, etc.)

        Returns:
            List of brand name candidates, each containing:
            - brand_name: The generated name
            - naming_strategy: Strategy used (portmanteau, descriptive, invented, acronym)
            - rationale: Why this name works
            - tagline: Suggested tagline
            - syllables: Number of syllables
            - memorable_score: Memorability rating (1-10)

        Example:
            >>> generator = NameGeneratorAgent(project_id="my-project")
            >>> names = generator.generate_names(
            ...     product_description="AI meal planning app",
            ...     target_audience="Busy parents",
            ...     brand_personality="warm"
            ... )
            >>> len(names)
            30

            # With feedback
            >>> feedback_ctx = "User LIKED: FlowMind, StreamTask. AVOID: Generic words like Pro, Max"
            >>> refined_names = generator.generate_names(
            ...     product_description="AI meal planning app",
            ...     feedback_context=feedback_ctx,
            ...     previous_names=[n['brand_name'] for n in names]
            ... )
        """
        # Validate inputs
        num_names = max(20, min(50, num_names))  # Ensure between 20-50

        valid_personalities = ['playful', 'professional', 'innovative', 'luxury']
        if brand_personality not in valid_personalities:
            logger.warning(
                f"Invalid brand personality '{brand_personality}'. "
                f"Using 'professional' instead."
            )
            brand_personality = 'professional'

        logger.info(
            f"Generating {num_names} brand names",
            extra={
                'brand_personality': brand_personality,
                'industry': industry,
                'num_names': num_names
            }
        )

        # Retrieve similar brands from RAG (if available)
        rag_examples = None
        if self.rag_client:
            try:
                rag_examples = self._retrieve_similar_brands(
                    product_description=product_description,
                    industry=industry
                )
                logger.info(f"Retrieved {len(rag_examples)} similar brands via RAG")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}. Proceeding without RAG enhancement.")
                rag_examples = None

        # Construct the user brief for the agent
        user_brief = self._format_user_brief(
            product_description=product_description,
            target_audience=target_audience,
            brand_personality=brand_personality,
            industry=industry,
            num_names=num_names,
            feedback_context=feedback_context,
            previous_names=previous_names,
            rag_examples=rag_examples,
            user_preferences=user_preferences
        )

        # Try to use real Vertex AI, fall back to placeholders
        if VERTEXAI_AVAILABLE and os.getenv('GOOGLE_CLOUD_PROJECT') != 'test-project-local':
            try:
                names = self._generate_with_vertexai(user_brief, num_names)
                logger.info(
                    f"Generated {len(names)} brand names using Vertex AI",
                    extra={'num_names': len(names)}
                )
            except Exception as e:
                logger.warning(
                    f"Vertex AI generation failed: {e}. Falling back to placeholders."
                )
                names = self._generate_placeholder_names(
                    product_description=product_description,
                    brand_personality=brand_personality,
                    num_names=num_names
                )
        else:
            logger.info("Using placeholder generation (Vertex AI not configured)")
            names = self._generate_placeholder_names(
                product_description=product_description,
                brand_personality=brand_personality,
                num_names=num_names
            )

        logger.info(
            f"Generated {len(names)} brand names successfully",
            extra={'num_names': len(names)}
        )

        return names

    def _format_user_brief(
        self,
        product_description: str,
        target_audience: str,
        brand_personality: str,
        industry: str,
        num_names: int,
        feedback_context: Optional[str] = None,
        previous_names: Optional[List[str]] = None,
        rag_examples: Optional[List[Dict[str, Any]]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format the user brief for the LLM agent.

        Args:
            product_description: Product description
            target_audience: Target audience
            brand_personality: Brand personality
            industry: Industry category
            num_names: Number of names to generate
            feedback_context: Optional user feedback from previous iteration
            previous_names: Optional list of previously generated names
            rag_examples: Optional list of similar brand examples from RAG
            user_preferences: Optional user preferences from Memory Bank

        Returns:
            Formatted user brief string
        """
        brief = f"""
Generate {num_names} brand name candidates for the following product:

**Product Description:** {product_description}

**Target Audience:** {target_audience if target_audience else 'General audience'}

**Brand Personality:** {brand_personality}

**Industry:** {industry}
"""

        # Add user preferences from Memory Bank if available
        if user_preferences:
            learning_insights = user_preferences.get('learning_insights', {})
            preferred_industries = user_preferences.get('preferred_industries', [])
            preferred_personalities = user_preferences.get('preferred_personalities', [])

            if preferred_industries or preferred_personalities or learning_insights:
                brief += """

=== USER PREFERENCES FROM PAST SESSIONS ===

"""
                if preferred_industries:
                    brief += f"**Past Industries:** {', '.join(preferred_industries)}\n"

                if preferred_personalities:
                    brief += f"**Preferred Brand Personalities:** {', '.join(preferred_personalities)}\n"

                if learning_insights:
                    if learning_insights.get('liked_naming_strategies'):
                        strategies = ', '.join(learning_insights['liked_naming_strategies'])
                        brief += f"**Preferred Naming Strategies:** {strategies}\n"

                    if learning_insights.get('common_themes'):
                        themes = ', '.join(learning_insights['common_themes'])
                        brief += f"**Common Themes User Likes:** {themes}\n"

                brief += """
Use these preferences as context to generate names that align with this user's taste
and past successful selections. However, prioritize the current brief's requirements.
"""

        # Add RAG examples if provided
        if rag_examples and len(rag_examples) > 0:
            brief += f"""

=== SIMILAR SUCCESSFUL BRANDS FOR INSPIRATION ===

Here are {len(rag_examples)} successful brands from similar industries/contexts.
Use these as inspiration for naming patterns, styles, and strategies:

"""
            for example in rag_examples[:10]:  # Limit to top 10 examples
                brand_name = example.get('brand_name', 'Unknown')
                industry_cat = example.get('industry', 'General')
                strategy = example.get('naming_strategy', 'Unknown')
                brief += f"- **{brand_name}** (Industry: {industry_cat}, Strategy: {strategy})\n"

            brief += """
Analyze these examples to understand successful naming patterns in this space,
but ensure your generated names are UNIQUE and NOT similar to these examples.
Use them for inspiration on style and strategy, not for copying.
"""

        # Add feedback context if provided
        if feedback_context:
            brief += f"""

=== USER FEEDBACK FROM PREVIOUS ITERATION ===

{feedback_context}

Based on this feedback, generate NEW names that incorporate what the user liked
and avoid what they disliked. Focus on the new directions they want to explore.
"""

        # Add previous names to avoid duplicates
        if previous_names:
            brief += f"""

=== PREVIOUSLY GENERATED NAMES (DO NOT REPEAT) ===

{', '.join(previous_names[:20])}{"..." if len(previous_names) > 20 else ""}

Generate COMPLETELY NEW names that are different from these previous suggestions.
"""

        brief += f"""

Please provide {num_names} creative brand names using a mix of naming strategies
(portmanteau, descriptive, invented, acronyms). Ensure each name matches the
{brand_personality} personality and is appropriate for the {industry} industry.

For each name, provide: brand_name, naming_strategy, rationale, tagline, syllables, memorable_score.
"""
        return brief.strip()

    def _retrieve_similar_brands(
        self,
        product_description: str,
        industry: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar brands from RAG vector search.

        Args:
            product_description: Product description for semantic search
            industry: Industry category for filtering

        Returns:
            List of similar brand dictionaries with metadata

        Raises:
            Exception: If RAG retrieval fails
        """
        if not self.rag_client:
            return []

        try:
            # Create search query from product description
            query = f"{industry} {product_description}"

            # Search for similar brands (K=50 as per spec)
            results = self.rag_client.search(
                query=query,
                num_neighbors=50,
                industry_filter=industry if industry != "general" else None
            )

            # Convert SearchResult objects to dictionaries
            brand_examples = []
            for result in results:
                brand_examples.append({
                    'brand_name': result.brand_name,
                    'industry': result.metadata.get('industry', 'Unknown'),
                    'naming_strategy': result.metadata.get('naming_strategy', 'Unknown'),
                    'category': result.metadata.get('category', 'Unknown'),
                    'distance': result.distance
                })

            logger.info(f"Retrieved {len(brand_examples)} similar brands from RAG")
            return brand_examples

        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            raise

    def _generate_with_vertexai(self, user_brief: str, num_names: int) -> List[Dict[str, Any]]:
        """
        Generate brand names using Google Gen AI SDK with Vertex AI.

        Args:
            user_brief: Formatted user brief prompt
            num_names: Number of names to generate

        Returns:
            List of brand name dictionaries

        Raises:
            Exception: If Vertex AI call fails
        """
        from google import genai
        from google.genai import types
        import os

        # Combine instruction and user brief
        full_prompt = f"{NAME_GENERATOR_INSTRUCTION}\n\n{user_brief}\n\nPlease return the results as a JSON array of objects with the following structure:\n{{\n  \"brand_name\": \"ExampleName\",\n  \"naming_strategy\": \"portmanteau|descriptive|invented|acronym\",\n  \"rationale\": \"Brief explanation\",\n  \"tagline\": \"5-8 word tagline\",\n  \"syllables\": 2,\n  \"memorable_score\": 8\n}}\n\nReturn ONLY the JSON array, no other text."

        # Try Vertex AI first, fall back to Google AI if it fails
        response = None
        last_error = None

        # Attempt 1: Try Vertex AI
        try:
            logger.info("Attempting Vertex AI endpoint...")
            client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=full_prompt
            )
            logger.info("Successfully used Vertex AI!")
        except Exception as e:
            last_error = e
            logger.warning(f"Vertex AI failed: {e}")

            # Attempt 2: Fall back to Google AI API (non-Vertex AI)
            logger.info("Falling back to Google AI API (non-Vertex)...")
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise Exception(f"Both Vertex AI and Google AI API failed. Vertex AI: {last_error}, Google AI: GOOGLE_API_KEY not found")

            # Temporarily clear Google Cloud env vars to force Google AI API mode
            # Save them before clearing
            saved_project = os.environ.get('GOOGLE_CLOUD_PROJECT')
            saved_location = os.environ.get('GOOGLE_CLOUD_LOCATION')
            saved_genai_use_vertexai = os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')

            try:
                # Clear ALL GCP-related env vars to prevent Vertex AI mode
                os.environ.pop('GOOGLE_CLOUD_PROJECT', None)
                os.environ.pop('GOOGLE_CLOUD_LOCATION', None)
                os.environ.pop('GOOGLE_GENAI_USE_VERTEXAI', None)

                # Create client - without GCP env vars, it will use Google AI API
                client = genai.Client(api_key=api_key)

                # Use the Google AI API endpoint with correct model name
                # Google AI has gemini-2.5-flash available
                response = client.models.generate_content(
                    model="models/gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.9,
                        top_p=0.95
                    )
                )
                logger.info("Successfully used Google AI API with gemini-2.5-flash!")
            except Exception as e2:
                import traceback
                logger.error(f"Google AI API also failed: {e2}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                raise Exception(f"Both Vertex AI and Google AI API failed. Vertex AI: {last_error}, Google AI: {e2}")
            finally:
                # Always restore environment variables
                if saved_project:
                    os.environ['GOOGLE_CLOUD_PROJECT'] = saved_project
                if saved_location:
                    os.environ['GOOGLE_CLOUD_LOCATION'] = saved_location
                if saved_genai_use_vertexai:
                    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = saved_genai_use_vertexai

        if response is None:
            raise Exception("Failed to generate content from any API")

        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            # Parse JSON
            names = json.loads(response_text)

            # Validate we got a list
            if not isinstance(names, list):
                raise ValueError("Response is not a JSON array")

            # Ensure we have the right number of names
            if len(names) < num_names:
                logger.warning(f"Generated {len(names)} names, requested {num_names}")

            return names[:num_names]  # Return requested number

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse Vertex AI response: {e}")
            logger.error(f"Response text: {response.text[:500]}")
            raise Exception(f"Failed to parse brand names from Vertex AI: {e}")

    def _generate_placeholder_names(
        self,
        product_description: str,
        brand_personality: str,
        num_names: int
    ) -> List[Dict[str, Any]]:
        """
        Generate placeholder brand names for Phase 1 MVP.

        This will be replaced with actual LLM generation in Phase 2.

        Args:
            product_description: Product description
            brand_personality: Brand personality
            num_names: Number of names to generate

        Returns:
            List of placeholder brand names
        """
        logger.info("Using placeholder name generation for Phase 1 MVP")

        # Generate diverse placeholder names using different strategies
        names = []
        strategies = ['portmanteau', 'descriptive', 'invented', 'acronym']

        for i in range(num_names):
            strategy = strategies[i % len(strategies)]

            if strategy == 'portmanteau':
                brand_name = f"BrandBlend{i+1}"
                tagline = "Where innovation meets tradition"
            elif strategy == 'descriptive':
                brand_name = f"SmartBrand{i+1}"
                tagline = "Solutions that work for you"
            elif strategy == 'invented':
                brand_name = f"Nexify{i+1}"
                tagline = "The future of branding"
            else:  # acronym
                brand_name = f"BBN{i+1}"
                tagline = "Building better names"

            names.append({
                'brand_name': brand_name,
                'naming_strategy': strategy,
                'rationale': f"Generated using {strategy} strategy for {brand_personality} personality",
                'tagline': tagline,
                'syllables': 2 + (i % 2),
                'memorable_score': 7 + (i % 4)
            })

        return names

    def validate_name_quality(self, brand_name: str) -> Dict[str, Any]:
        """
        Validate the quality of a brand name.

        Checks pronounceability, length, memorability, and other quality factors.

        Args:
            brand_name: Brand name to validate

        Returns:
            Dictionary with quality metrics:
            - length_ok: True if 2-15 characters
            - syllable_count: Estimated syllables
            - pronounceable: Basic pronounceability check
            - unique_score: Uniqueness estimate (1-10)
        """
        length_ok = 2 <= len(brand_name) <= 15
        syllable_count = self._estimate_syllables(brand_name)
        pronounceable = self._check_pronounceability(brand_name)

        return {
            'length_ok': length_ok,
            'syllable_count': syllable_count,
            'pronounceable': pronounceable,
            'unique_score': 7  # Placeholder
        }

    def _estimate_syllables(self, word: str) -> int:
        """
        Estimate the number of syllables in a word.

        Args:
            word: Word to analyze

        Returns:
            Estimated syllable count
        """
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1

        # Ensure at least 1 syllable
        return max(1, syllable_count)

    def _check_pronounceability(self, word: str) -> bool:
        """
        Check if a word is pronounceable (basic heuristic).

        Args:
            word: Word to check

        Returns:
            True if likely pronounceable
        """
        # Simple heuristic: check vowel ratio
        vowels = 'aeiouy'
        vowel_count = sum(1 for c in word.lower() if c in vowels)
        vowel_ratio = vowel_count / len(word) if len(word) > 0 else 0

        # Pronounceable words typically have 20-50% vowels
        return 0.2 <= vowel_ratio <= 0.5
