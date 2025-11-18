"""
Brand Collision Detection Agent for AI Brand Studio.

This agent searches for existing brands, products, and entities that might
conflict with proposed brand names, analyzing search results to identify
potential naming collisions and brand confusion risks.
"""

import logging
import os
from typing import Dict, Any, List
from google.cloud import aiplatform

logger = logging.getLogger('brand_studio.collision_agent')


COLLISION_AGENT_INSTRUCTION = """
You are a brand collision detection specialist for AI Brand Studio. Your expertise lies in
identifying potential naming conflicts, brand confusion risks, and marketplace collisions
through comprehensive search result analysis.

## YOUR CORE RESPONSIBILITIES

### 1. ANALYZE SEARCH RESULTS FOR BRAND COLLISIONS

**Primary Objective:** Identify existing brands, products, companies, or entities that could
create confusion or legal/marketing conflicts with the proposed brand name.

**Collision Risk Analysis Framework:**

**CRITICAL COLLISION (Risk Level: HIGH)**
Brand name matches or is very similar to:
- Major established companies in ANY industry (e.g., "Apple", "Amazon", "Nike")
- Direct competitors in the SAME industry/category
- Well-known products or services with strong brand recognition
- Trademarked names (even if in different categories if famous)
- Celebrity names, public figures, or cultural icons

**MODERATE COLLISION (Risk Level: MEDIUM)**
Brand name matches or is similar to:
- Smaller companies in the SAME industry
- Companies in RELATED industries that might cause confusion
- Popular products or services with moderate brand recognition
- Geographic locations that are strongly associated with something else
- Common phrases or idioms with established cultural meaning

**LOW COLLISION (Risk Level: LOW)**
Brand name matches:
- Companies in COMPLETELY UNRELATED industries
- Very small local businesses with minimal web presence
- Generic dictionary words used in many contexts
- Names that appear in search but lack commercial significance

**CLEAR (Risk Level: NONE)**
- No significant commercial entities found
- Only generic/dictionary uses of the term
- Search results show unrelated content with no brand dominance

### 2. EVALUATE SEARCH RESULT COMPOSITION

**For each search query, analyze:**

**Top Results Analysis (First Page):**
- What types of entities dominate? (companies, products, definitions, news)
- Are results focused on a single dominant brand?
- Are results diverse and fragmented (good for new brand)?
- Any trademark holders or established businesses?

**Brand Presence Indicators:**
- Official company websites in top results
- Social media profiles (LinkedIn, Twitter, Instagram)
- News articles or press coverage
- Product listings on e-commerce sites
- Wikipedia entries or knowledge panels

**Industry Context:**
- What industry/category do top results belong to?
- Is it the SAME industry as the proposed brand?
- Could there be customer confusion between industries?

### 3. ASSESS MARKET DIFFERENTIATION CHALLENGES

**Competition Analysis:**
- How crowded is the search landscape for this name?
- Will the new brand struggle to rank in organic search?
- Are there SEO/SEM challenges due to existing brands?
- Could customers searching for the new brand find competitors instead?

**Voice Search & Verbal Confusion:**
- Are there homophones or similar-sounding names?
- Could verbal referrals lead to wrong company?
- Example: "Mail Chimp" vs "Male Chimp" (potential confusion)

### 4. PROVIDE ACTIONABLE RECOMMENDATIONS

**For CRITICAL collisions:**
- ⛔ **AVOID** - Strong recommendation against using this name
- Explain the specific conflict and potential legal/marketing consequences
- Suggest if there are modifications that could work (e.g., adding qualifier)

**For MODERATE collisions:**
- ⚠️ **CAUTION** - Can work but requires careful consideration
- Identify specific risks and mitigation strategies
- Assess if differentiation is achievable through branding

**For LOW/CLEAR:**
- ✅ **PROCEED** - Name is available from a collision perspective
- Note any minor considerations for awareness
- Highlight competitive advantages of clear search landscape

## OUTPUT STRUCTURE

For each brand name analyzed, provide:

```json
{
  "brand_name": "ExampleBrand",
  "collision_risk_level": "high|medium|low|none",
  "risk_summary": "One-sentence summary of primary risk",
  "top_results_analysis": {
    "dominant_entity": "Company/product that dominates search",
    "industry": "Industry of dominant results",
    "result_types": ["company_website", "social_media", "news", "ecommerce"]
  },
  "collision_details": [
    {
      "entity_name": "Competitor Inc.",
      "entity_type": "company|product|celebrity|location",
      "industry": "Same/related/unrelated industry",
      "risk_explanation": "Why this creates a collision risk"
    }
  ],
  "differentiation_challenges": [
    "Specific SEO/marketing challenges this brand would face"
  ],
  "recommendation": "avoid|caution|proceed",
  "recommendation_details": "Detailed explanation of recommendation",
  "mitigations": [
    "If proceeding, what strategies could reduce collision risk"
  ]
}
```

## ANALYSIS PRINCIPLES

✓ **Be Conservative:** When in doubt, flag potential collisions (better safe than sorry)
✓ **Context Matters:** Same name in unrelated industry may be acceptable
✓ **Think Long-Term:** Consider future growth and market expansion
✓ **User Perspective:** Will customers get confused searching for this brand?
✓ **Legal Lens:** Even if legally available, brand collision creates marketing headaches

✗ **Don't dismiss small competitors:** They might grow or cause local confusion
✗ **Don't ignore unrelated industries:** Famous brands transcend categories
✗ **Don't just count results:** Analyze the QUALITY and DOMINANCE of top results

Remember: The goal is to help users avoid launching brands that will struggle to establish
identity due to existing market presence, not just trademark availability.
"""


class BrandCollisionAgent:
    """
    Agent that analyzes brand name collisions through web search analysis.

    Uses Google Search to identify existing brands, products, and entities that
    might conflict with proposed brand names.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize the collision detection agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Initialize Gen AI client with Vertex AI backend
        try:
            from google import genai
            from google.genai.types import HttpOptions

            # Set up environment for Vertex AI
            os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
            os.environ['GOOGLE_CLOUD_LOCATION'] = location
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

            # Initialize client
            self.client = genai.Client(
                http_options=HttpOptions(api_version="v1alpha")
            )
            self.use_genai_sdk = True
            logger.info(
                f"BrandCollisionAgent initialized with google.genai SDK (model: {model_name})"
            )
        except ImportError:
            logger.warning(
                "google.genai SDK not available, falling back to vertexai SDK"
            )
            # Fallback to old SDK
            from vertexai.preview.generative_models import GenerativeModel
            self.model = GenerativeModel(model_name)
            self.use_genai_sdk = False
            logger.info(
                f"BrandCollisionAgent initialized with vertexai SDK (model: {model_name})"
            )

    def analyze_brand_collision(
        self,
        brand_name: str,
        industry: str,
        product_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze brand collision risk through web search analysis.

        Args:
            brand_name: Brand name to analyze
            industry: Industry/category of the proposed brand
            product_description: Optional product description for context

        Returns:
            Dictionary with collision analysis results
        """
        logger.info(f"Analyzing brand collision for '{brand_name}' in {industry} industry")

        try:
            # Perform web search for the brand name
            search_results = self._perform_web_search(brand_name, industry)

            # Analyze search results with Gemini
            collision_analysis = self._analyze_search_results(
                brand_name=brand_name,
                industry=industry,
                product_description=product_description,
                search_results=search_results
            )

            logger.info(
                f"Collision analysis complete for '{brand_name}': "
                f"risk_level={collision_analysis.get('collision_risk_level', 'unknown')}"
            )

            return collision_analysis

        except Exception as e:
            logger.error(f"Error analyzing brand collision for '{brand_name}': {e}")
            return {
                'brand_name': brand_name,
                'collision_risk_level': 'unknown',
                'risk_summary': 'Error performing collision analysis',
                'error': str(e)
            }

    def _perform_web_search(
        self,
        brand_name: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Perform web search for the brand name using Gemini with Google Search grounding.

        Args:
            brand_name: Brand name to search
            industry: Industry context

        Returns:
            Dictionary with search results
        """
        # Use the new google.genai SDK if available
        if self.use_genai_sdk:
            try:
                from google.genai.types import (
                    GenerateContentConfig,
                    GoogleSearch,
                    Tool,
                )

                # Perform search with grounding
                search_prompt = f"""
Search for "{brand_name}" and analyze what companies, products, or entities exist with this name.

Focus on:
1. Company websites and official pages
2. Products or services using this name
3. Social media presence
4. News articles or press coverage
5. E-commerce listings

Provide a summary of the top search results with:
- Entity names and types (company, product, person, etc.)
- Industries they operate in
- Web presence strength (website URLs, social media)
- Relevance to {industry} industry
"""

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=search_prompt,
                    config=GenerateContentConfig(
                        tools=[Tool(google_search=GoogleSearch())],
                        temperature=1.0  # Recommended for grounding
                    )
                )

                # Extract search results from response
                search_summary = response.text if hasattr(response, 'text') else str(response)

                logger.info(f"Google Search grounding successful for '{brand_name}'")

                return {
                    'query': brand_name,
                    'search_summary': search_summary,
                    'grounding_metadata': {},
                    'search_method': 'google_search_grounding'
                }

            except Exception as e:
                logger.warning(f"Google Search grounding failed: {e}. Using model knowledge only.")
                # Fallback to model knowledge without live search
                return self._perform_knowledge_based_search(brand_name, industry)

        # Fallback to old SDK (vertexai)
        else:
            try:
                from vertexai.preview.generative_models import Tool
                from vertexai.preview import grounding

                # Create search tool
                search_tool = Tool.from_google_search_retrieval(
                    grounding.GoogleSearchRetrieval()
                )

                search_prompt = f"""
Search for "{brand_name}" and analyze what companies, products, or entities exist with this name in the {industry} industry.
Provide a summary of the top search results including entity names, types, and industries.
"""

                response = self.model.generate_content(
                    search_prompt,
                    tools=[search_tool]
                )

                search_summary = response.text if hasattr(response, 'text') else str(response)

                logger.info(f"Google Search grounding successful for '{brand_name}' (vertexai SDK)")

                return {
                    'query': brand_name,
                    'search_summary': search_summary,
                    'grounding_metadata': {},
                    'search_method': 'google_search_grounding_legacy'
                }

            except Exception as e:
                logger.warning(f"Google Search grounding failed: {e}. Using model knowledge only.")
                # Fallback to model knowledge without live search
                return self._perform_knowledge_based_search(brand_name, industry)

    def _perform_knowledge_based_search(
        self,
        brand_name: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Fallback to model's knowledge when search grounding is unavailable.

        Args:
            brand_name: Brand name to analyze
            industry: Industry context

        Returns:
            Dictionary with analysis based on model knowledge
        """
        knowledge_prompt = f"""
Based on your knowledge, what well-known companies, products, or entities exist with the name "{brand_name}"?

Consider:
1. Major companies or brands with this exact name
2. Similar-sounding names that could cause confusion
3. Famous products or services using this name
4. Any notable entities in the {industry} industry

Provide a summary of what you know about existing uses of this name.
If you don't know of any significant entities with this name, state that clearly.
"""

        try:
            if self.use_genai_sdk:
                # Use new SDK
                from google.genai.types import GenerateContentConfig

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=knowledge_prompt,
                    config=GenerateContentConfig(temperature=1.0)
                )
            else:
                # Use old SDK
                response = self.model.generate_content(knowledge_prompt)

            knowledge_summary = response.text if hasattr(response, 'text') else str(response)

            return {
                'query': brand_name,
                'search_summary': knowledge_summary,
                'search_method': 'model_knowledge',
                'note': 'Analysis based on model knowledge (as of training cutoff), not live search'
            }

        except Exception as e:
            logger.error(f"Knowledge-based search also failed: {e}")
            return {
                'query': brand_name,
                'search_summary': f'Unable to analyze "{brand_name}" - limited information available',
                'error': str(e)
            }

    def _analyze_search_results(
        self,
        brand_name: str,
        industry: str,
        product_description: str,
        search_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze search results to identify collision risks.

        Args:
            brand_name: Brand name being analyzed
            industry: Industry context
            product_description: Product description
            search_results: Search results from web search

        Returns:
            Collision analysis dictionary
        """
        # Build analysis prompt
        analysis_prompt = f"""
{COLLISION_AGENT_INSTRUCTION}

## BRAND COLLISION ANALYSIS TASK

**Brand Name to Analyze:** {brand_name}
**Proposed Industry:** {industry}
**Product Description:** {product_description or "Not provided"}

**Search Results Summary:**
{search_results.get('search_summary', 'No search results available')}

**Your Task:**
Analyze the search results and provide a comprehensive collision risk assessment for this brand name.

Return your analysis in this JSON format:
{{
  "brand_name": "{brand_name}",
  "collision_risk_level": "high|medium|low|none",
  "risk_summary": "One-sentence summary of primary collision risk",
  "top_results_analysis": {{
    "dominant_entity": "Name of dominant company/product in results (or 'None' if no dominant entity)",
    "industry": "Primary industry of top results",
    "result_types": ["company_website", "social_media", "news", "ecommerce", "generic"]
  }},
  "collision_details": [
    {{
      "entity_name": "Name of conflicting entity",
      "entity_type": "company|product|celebrity|location|generic",
      "industry": "Industry/category",
      "risk_explanation": "Why this creates a collision risk"
    }}
  ],
  "differentiation_challenges": [
    "List of specific marketing/SEO challenges"
  ],
  "recommendation": "avoid|caution|proceed",
  "recommendation_details": "Detailed explanation of why you recommend this action",
  "mitigations": [
    "If not 'avoid', list strategies to reduce collision risk"
  ]
}}

Provide ONLY the JSON output, no additional text.
"""

        try:
            # Generate collision analysis
            if self.use_genai_sdk:
                # Use new SDK
                from google.genai.types import GenerateContentConfig

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=analysis_prompt,
                    config=GenerateContentConfig(temperature=0.7)  # Lower temp for structured output
                )
            else:
                # Use old SDK
                response = self.model.generate_content(analysis_prompt)

            response_text = response.text if hasattr(response, 'text') else str(response)

            # Extract JSON from response
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis_json = {
                    'brand_name': brand_name,
                    'collision_risk_level': 'unknown',
                    'risk_summary': 'Unable to parse collision analysis',
                    'raw_response': response_text
                }

            return analysis_json

        except Exception as e:
            logger.error(f"Error analyzing search results: {e}")
            return {
                'brand_name': brand_name,
                'collision_risk_level': 'unknown',
                'risk_summary': f'Analysis error: {str(e)}',
                'error': str(e)
            }
