"""
Research Agent for AI Brand Studio.

This agent researches industry trends, competitor brands, and naming patterns
to inform the brand name generation process.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform

# Import Brand Studio logging
from src.infrastructure.logging import get_logger, track_performance

# Try to import real ADK, fall back to mock for Phase 2
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.research_agent')


# Research agent instruction prompt
RESEARCH_AGENT_INSTRUCTION = """
You are an industry research specialist for AI Brand Studio. Your role is to analyze
industries, identify trends, and provide insights that inform brand name generation.

## YOUR RESPONSIBILITIES

1. **Analyze Industry Landscape:**
   - Identify key characteristics of the target industry
   - Understand market dynamics and competitive landscape
   - Note industry-specific terminology and jargon
   - Identify emerging trends and patterns

2. **Study Competitor Brands:**
   - Analyze naming patterns of successful brands in the industry
   - Identify common themes and strategies
   - Note what makes certain names stand out
   - Understand naming conventions to embrace or avoid

3. **Research Target Audience:**
   - Understand the demographics and psychographics
   - Identify communication preferences
   - Note cultural sensitivities and preferences
   - Understand what resonates with this audience

4. **Provide Strategic Recommendations:**
   - Suggest naming strategies that fit the industry
   - Recommend personality attributes that work well
   - Identify keywords and themes to explore
   - Warn about overused patterns or clichés

## OUTPUT FORMAT

Provide your research findings in a structured format:

```
{
  "industry_analysis": {
    "key_characteristics": ["characteristic1", "characteristic2", ...],
    "market_dynamics": "Brief description of market state",
    "terminology": ["term1", "term2", ...],
    "trends": ["trend1", "trend2", ...]
  },
  "competitor_patterns": {
    "common_strategies": ["strategy1", "strategy2", ...],
    "successful_examples": [
      {"brand": "Name", "why_it_works": "Reason"},
      ...
    ],
    "patterns_to_avoid": ["pattern1", "pattern2", ...]
  },
  "audience_insights": {
    "demographics": "Age range, location, income, etc.",
    "preferences": ["preference1", "preference2", ...],
    "communication_style": "Formal/casual/technical/etc."
  },
  "recommendations": {
    "suggested_strategies": ["strategy1", "strategy2", ...],
    "personality_fit": ["playful", "professional", "innovative", "luxury"],
    "keywords_to_explore": ["keyword1", "keyword2", ...],
    "avoid": ["cliche1", "cliche2", ...]
  }
}
```

## IMPORTANT GUIDELINES

- Be specific and actionable in your recommendations
- Base insights on real market knowledge when possible
- Identify both opportunities and risks
- Prioritize insights that will directly influence name generation
- Keep responses concise but comprehensive
"""


class ResearchAgent:
    """
    Research Agent that analyzes industries and provides naming insights.

    Uses Gemini Flash for fast research and analysis to inform the
    brand name generation process.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize the research agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use (default: gemini-2.5-flash)
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info(
            "Initializing ResearchAgent",
            extra={
                'project_id': project_id,
                'location': location,
                'model_name': model_name
            }
        )

        # Initialize Vertex AI
        try:
            aiplatform.init(project=project_id, location=location)
            logger.info("Vertex AI initialized for ResearchAgent")
        except Exception as e:
            logger.warning(f"Vertex AI initialization issue: {e}")

        # Initialize the LLM agent (using mock for Phase 2)
        self.agent = LlmAgent(
            name="research_agent",
            model=model_name,
            description="Researches industry trends and competitor brands",
            instruction=RESEARCH_AGENT_INSTRUCTION
        )
        logger.info("Research LlmAgent initialized")

    def research_industry(
        self,
        product_description: str,
        industry: str,
        target_audience: str = ""
    ) -> Dict[str, Any]:
        """
        Research an industry and provide naming insights.

        Args:
            product_description: Description of the product/service
            industry: Target industry (e.g., "technology", "healthcare", "finance")
            target_audience: Description of target customers

        Returns:
            Dictionary with research findings and recommendations

        Example:
            >>> agent = ResearchAgent(project_id="my-project")
            >>> research = agent.research_industry(
            ...     product_description="AI-powered meal planning app",
            ...     industry="food-tech",
            ...     target_audience="Busy millennial parents"
            ... )
            >>> print(research['recommendations']['suggested_strategies'])
            ['portmanteau', 'playful', 'descriptive']
        """
        logger.info(
            f"Researching industry: {industry}",
            extra={'product': product_description[:50]}
        )

        # For Phase 2, return structured research insights
        # In Phase 3, this would call the actual LLM
        research_findings = self._generate_research_insights(
            product_description=product_description,
            industry=industry,
            target_audience=target_audience
        )

        logger.info(f"Research complete for industry: {industry}")
        return research_findings

    def _generate_research_insights(
        self,
        product_description: str,
        industry: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Generate research insights for the given parameters.

        For Phase 2, provides structured insights based on industry heuristics.
        In Phase 3, this will use the LLM agent for dynamic research.

        Args:
            product_description: Product description
            industry: Target industry
            target_audience: Target audience

        Returns:
            Research findings dictionary
        """
        # Industry-specific insights (heuristic-based for Phase 2)
        industry_insights = self._get_industry_insights(industry)

        # Combine with product and audience analysis
        findings = {
            "industry_analysis": {
                "key_characteristics": industry_insights.get("characteristics", []),
                "market_dynamics": industry_insights.get("dynamics", ""),
                "terminology": industry_insights.get("terminology", []),
                "trends": industry_insights.get("trends", [])
            },
            "competitor_patterns": {
                "common_strategies": industry_insights.get("strategies", []),
                "successful_examples": industry_insights.get("examples", []),
                "patterns_to_avoid": industry_insights.get("avoid", [])
            },
            "audience_insights": {
                "demographics": target_audience if target_audience else "General consumers",
                "preferences": self._infer_audience_preferences(target_audience),
                "communication_style": self._infer_communication_style(target_audience, industry)
            },
            "recommendations": {
                "suggested_strategies": industry_insights.get("recommended_strategies", []),
                "personality_fit": industry_insights.get("personalities", []),
                "keywords_to_explore": self._extract_keywords(product_description, industry),
                "avoid": industry_insights.get("avoid", [])
            }
        }

        return findings

    def _get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific insights."""
        industry_lower = industry.lower()

        # Technology industry
        if 'tech' in industry_lower or 'software' in industry_lower or 'app' in industry_lower:
            return {
                "characteristics": ["innovative", "fast-paced", "digital-first", "scalable"],
                "dynamics": "Rapidly evolving with focus on disruption and user experience",
                "terminology": ["cloud", "AI", "platform", "sync", "smart", "connect"],
                "trends": ["AI integration", "mobile-first", "automation", "personalization"],
                "strategies": ["portmanteau", "invented", "descriptive"],
                "examples": [
                    {"brand": "Slack", "why_it_works": "Short, memorable, suggests ease of communication"},
                    {"brand": "Notion", "why_it_works": "Simple, meaningful, suggests ideas and organization"}
                ],
                "avoid": ["tech", "soft", "ware", "sys", "pro"],
                "recommended_strategies": ["portmanteau", "invented"],
                "personalities": ["innovative", "professional"]
            }

        # Healthcare/Wellness
        elif 'health' in industry_lower or 'wellness' in industry_lower or 'medical' in industry_lower:
            return {
                "characteristics": ["trustworthy", "caring", "scientific", "accessible"],
                "dynamics": "Regulated industry with focus on trust and efficacy",
                "terminology": ["care", "vital", "life", "health", "well", "balance"],
                "trends": ["preventive care", "mental health", "telehealth", "personalization"],
                "strategies": ["descriptive", "borrowed"],
                "examples": [
                    {"brand": "Calm", "why_it_works": "Directly communicates the benefit"},
                    {"brand": "Headspace", "why_it_works": "Meaningful and relatable"}
                ],
                "avoid": ["med", "cure", "rx", "doc"],
                "recommended_strategies": ["descriptive", "calming words"],
                "personalities": ["professional", "playful"]
            }

        # Food & Beverage
        elif 'food' in industry_lower or 'restaurant' in industry_lower or 'meal' in industry_lower:
            return {
                "characteristics": ["appetizing", "fresh", "quality-focused", "experiential"],
                "dynamics": "Competitive market with emphasis on taste and experience",
                "terminology": ["fresh", "bite", "taste", "flavor", "plate", "dish"],
                "trends": ["sustainability", "plant-based", "local sourcing", "convenience"],
                "strategies": ["descriptive", "portmanteau"],
                "examples": [
                    {"brand": "Sweetgreen", "why_it_works": "Combines freshness with eco-friendly"},
                    {"brand": "Beyond Meat", "why_it_works": "Descriptive and forward-thinking"}
                ],
                "avoid": ["eats", "bites", "yum"],
                "recommended_strategies": ["portmanteau", "playful"],
                "personalities": ["playful", "professional"]
            }

        # Finance/Fintech
        elif 'fin' in industry_lower or 'bank' in industry_lower or 'pay' in industry_lower:
            return {
                "characteristics": ["secure", "trustworthy", "innovative", "accessible"],
                "dynamics": "Traditional sector being disrupted by technology",
                "terminology": ["pay", "wallet", "secure", "trust", "invest", "save"],
                "trends": ["mobile payments", "cryptocurrency", "embedded finance", "AI-driven"],
                "strategies": ["portmanteau", "invented"],
                "examples": [
                    {"brand": "Stripe", "why_it_works": "Simple, modern, suggests smooth transactions"},
                    {"brand": "Chime", "why_it_works": "Friendly, accessible, notification-oriented"}
                ],
                "avoid": ["bank", "fin", "pay", "cash"],
                "recommended_strategies": ["invented", "modern"],
                "personalities": ["innovative", "professional"]
            }

        # Default/General
        else:
            return {
                "characteristics": ["memorable", "unique", "relevant"],
                "dynamics": "Competitive marketplace requiring differentiation",
                "terminology": [],
                "trends": ["digital transformation", "customer experience", "sustainability"],
                "strategies": ["portmanteau", "descriptive", "invented"],
                "examples": [],
                "avoid": ["generic terms", "overused suffixes"],
                "recommended_strategies": ["portmanteau", "invented"],
                "personalities": ["professional", "innovative"]
            }

    def _infer_audience_preferences(self, target_audience: str) -> List[str]:
        """Infer audience preferences from description."""
        preferences = []
        audience_lower = target_audience.lower()

        if 'millennial' in audience_lower or 'gen z' in audience_lower:
            preferences.extend(["authentic", "mobile-first", "social-friendly"])
        if 'professional' in audience_lower or 'business' in audience_lower:
            preferences.extend(["trustworthy", "efficient", "premium"])
        if 'parent' in audience_lower or 'family' in audience_lower:
            preferences.extend(["reliable", "simple", "helpful"])
        if 'young' in audience_lower or 'student' in audience_lower:
            preferences.extend(["affordable", "trendy", "fun"])

        return preferences if preferences else ["accessible", "quality"]

    def _infer_communication_style(self, target_audience: str, industry: str) -> str:
        """Infer preferred communication style."""
        audience_lower = target_audience.lower()

        if 'professional' in audience_lower or 'enterprise' in audience_lower:
            return "Professional and authoritative"
        elif 'young' in audience_lower or 'gen z' in audience_lower:
            return "Casual and authentic"
        elif 'luxury' in industry.lower() or 'premium' in audience_lower:
            return "Sophisticated and refined"
        else:
            return "Friendly and approachable"

    def _extract_keywords(self, product_description: str, industry: str) -> List[str]:
        """Extract relevant keywords from product description."""
        keywords = []

        # Extract meaningful words (excluding common stop words)
        stop_words = {'a', 'an', 'the', 'for', 'and', 'or', 'but', 'with', 'of', 'to', 'in', 'on'}
        words = product_description.lower().split()

        for word in words:
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum())
            if word and len(word) > 3 and word not in stop_words:
                keywords.append(word)

        return keywords[:10]  # Return top 10 keywords
