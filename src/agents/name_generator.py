"""
Name Generator Agent for AI Brand Studio.

This agent generates creative, industry-appropriate brand names using
Gemini 2.5 Pro with multiple naming strategies and brand personality support.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import aiplatform

# Try to import real ADK, fall back to mock for Phase 1
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.name_generator')


# Name generation instruction prompt
NAME_GENERATOR_INSTRUCTION = """
You are a creative brand naming expert for AI Brand Studio. Your role is to generate
memorable, distinctive brand names that align with the user's product and brand personality.

## YOUR RESPONSIBILITIES

1. **Analyze the User Brief:**
   - Understand the product/service being named
   - Identify the target audience and their preferences
   - Note the desired brand personality (playful, professional, innovative, luxury)
   - Consider the industry context and competitive landscape

2. **Generate 20-50 Brand Name Candidates:**
   Use multiple naming strategies to create diverse options:

   **Portmanteau (Blended Words):**
   - Combine two relevant words into one memorable name
   - Examples: Pinterest (Pin + Interest), Netflix (Net + Flicks)
   - Ensure the blend is pronounceable and meaningful

   **Descriptive Names:**
   - Clearly communicate what the product does
   - Examples: PayPal, Salesforce, FreshBooks
   - Use industry-relevant keywords

   **Invented Names:**
   - Create entirely new words that are memorable and unique
   - Examples: Kodak, Spotify, Xerox
   - Ensure they're easy to pronounce and remember

   **Acronyms:**
   - Use initials or shortened forms of longer phrases
   - Examples: IBM, NASA, IKEA
   - Make sure the acronym is pronounceable and meaningful

3. **Apply Brand Personality:**
   Adapt naming style based on the requested personality:

   - **Playful:** Fun, whimsical, lighthearted names (e.g., Hootsuite, Wufoo)
   - **Professional:** Authoritative, trustworthy, business-focused (e.g., Accenture, Deloitte)
   - **Innovative:** Forward-thinking, tech-savvy, modern (e.g., Tesla, Stripe)
   - **Luxury:** Elegant, sophisticated, premium (e.g., Lexus, Cartier)

4. **Name Quality Criteria:**
   Prioritize names that are:
   - **Memorable:** Easy to recall after hearing once
   - **Pronounceable:** Clear phonetics, not confusing
   - **Short:** Ideally 2-3 syllables (max 4)
   - **Unique:** Distinctive and not generic
   - **Meaningful:** Relevant to the product/industry
   - **Domain-friendly:** Works well as a .com domain
   - **International:** Avoid problematic meanings in other languages

5. **Output Format:**
   For each brand name, provide:
   ```
   {
     "brand_name": "ExampleName",
     "naming_strategy": "portmanteau|descriptive|invented|acronym",
     "rationale": "Brief explanation of why this name works (1-2 sentences)",
     "tagline": "Suggested tagline (5-8 words)",
     "syllables": 2,
     "memorable_score": 8
   }
   ```

## IMPORTANT CONSTRAINTS

- Generate MINIMUM 20 names, MAXIMUM 50 names
- Distribute names across all 4 naming strategies (don't use just one)
- Ensure names match the specified brand personality
- Avoid names that are:
  * Too similar to major existing brands
  * Difficult to spell or pronounce
  * Negative connotations or meanings
  * Too generic or descriptive of a commodity
- Each name should be accompanied by a unique rationale and tagline

## EXAMPLE OUTPUT

User Brief: AI-powered meal planning app for busy parents
Brand Personality: Warm
Target Audience: Parents aged 28-40

Good Names:
- NutriNest (Portmanteau: Nutrition + Nest) - "Where healthy meals find home"
- MealMind (Descriptive) - "Smart planning for busy families"
- Yumora (Invented) - "Bringing joy back to mealtime"

Bad Names:
- AIMPB (Acronym) - Too generic, not memorable
- TheFoodPlanningApplicationForParents (Descriptive) - Way too long
- HealthyEatsApp (Descriptive) - Too generic, not distinctive
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

    def generate_names(
        self,
        product_description: str,
        target_audience: str = "",
        brand_personality: str = "professional",
        industry: str = "general",
        num_names: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate brand name candidates based on user brief.

        Args:
            product_description: Description of the product/service
            target_audience: Target customer segment
            brand_personality: Desired personality (playful, professional, innovative, luxury)
            industry: Product industry/category
            num_names: Number of names to generate (default: 30, min: 20, max: 50)

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

        # Construct the user brief for the agent
        user_brief = self._format_user_brief(
            product_description=product_description,
            target_audience=target_audience,
            brand_personality=brand_personality,
            industry=industry,
            num_names=num_names
        )

        # For Phase 1, use placeholder generation
        # In Phase 2, this will call self.agent.generate(user_brief)
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
        num_names: int
    ) -> str:
        """
        Format the user brief for the LLM agent.

        Args:
            product_description: Product description
            target_audience: Target audience
            brand_personality: Brand personality
            industry: Industry category
            num_names: Number of names to generate

        Returns:
            Formatted user brief string
        """
        brief = f"""
Generate {num_names} brand name candidates for the following product:

**Product Description:** {product_description}

**Target Audience:** {target_audience if target_audience else 'General audience'}

**Brand Personality:** {brand_personality}

**Industry:** {industry}

Please provide {num_names} creative brand names using a mix of naming strategies
(portmanteau, descriptive, invented, acronyms). Ensure each name matches the
{brand_personality} personality and is appropriate for the {industry} industry.

For each name, provide: brand_name, naming_strategy, rationale, tagline, syllables, memorable_score.
"""
        return brief.strip()

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
