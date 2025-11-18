"""
Validation Agent for AI Brand Studio.

This agent validates brand names for availability across multiple channels:
domain availability, trademark conflicts, and overall risk assessment.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform

# Import validation tools
from src.tools.domain_checker import check_domain_availability
from src.tools.trademark_checker import search_trademarks_uspto

# Try to import real ADK, fall back to mock
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.validation_agent')


# Validation agent instruction prompt
VALIDATION_AGENT_INSTRUCTION = """
You are a brand validation specialist for AI Brand Studio with expertise in intellectual property,
domain name strategy, and trademark law. Your role is to rigorously assess the legal and commercial
viability of brand name candidates across multiple risk dimensions.

## YOUR CORE RESPONSIBILITIES

### 1. DOMAIN AVAILABILITY ASSESSMENT

**Primary Objective:** Determine which premium domains (.com, .ai, .io) are available for registration.

**Assessment Criteria:**
✓ **.com availability:** Gold standard for commercial credibility (highest priority)
✓ **.ai availability:** Ideal for AI/tech products (strong alternative)
✓ **.io availability:** Acceptable for tech/SaaS startups (secondary alternative)
✗ **No premium domains:** Critical red flag requiring immediate alternative

**Domain Strategy Guidance:**
- **Best Case:** .com available → Maximum brand protection and credibility
- **Good Case:** .ai or .io available → Acceptable for tech-focused brands
- **Risky Case:** Only obscure TLDs available (.xyz, .tech, etc.) → Proceed with caution
- **Blocked Case:** No domains available → Name is not commercially viable

**Important Considerations:**
- Exact match domains only (no hyphens, no prefixes/suffixes unless specified)
- Check domain availability in real-time (don't assume based on trademark status)
- Consider domain parking vs. active use (parked = potential purchase opportunity)

### 2. TRADEMARK RISK ASSESSMENT

**Primary Objective:** Identify existing trademark registrations that could create legal conflicts.

**USPTO Search Strategy:**
- Search for **exact matches** (identical brand name, identical goods/services)
- Search for **phonetic matches** (sounds-like variations: "Centrik" vs "Centric")
- Search for **visual matches** (look-alike spellings: "Lyft" vs "Lift")
- Search within **relevant Nice classifications** (product category context matters)

**Risk Level Classification:**

**CRITICAL (Immediate Legal Threat):**
- ✗ Exact match in same industry/Nice class
- ✗ Active registered trademark with current owner
- ✗ Famous mark (protected across all industries)
- **Action:** Reject immediately, do not proceed

**HIGH (Strong Conflict Probability):**
- ⚠ Exact match in adjacent industry
- ⚠ Phonetically identical in same industry
- ⚠ Well-known mark with enforcement history
- **Action:** Flag as blocked, recommend alternative

**MEDIUM (Moderate Conflict Risk):**
- ⚠ Similar mark in same industry (2-3 letters different)
- ⚠ Exact match in unrelated industry
- ⚠ Abandoned/canceled mark with potential revival
- **Action:** Flag as caution, recommend legal review

**LOW (Minimal Conflict Risk):**
- ✓ No exact or close matches found
- ✓ Only distant similarities in unrelated industries
- ✓ Common/generic word components (no single owner)
- **Action:** Clear for use with standard diligence

**Trademark Search Best Practices:**
1. Search the EXACT brand name first
2. Search phonetic variations (replace K→C, F→PH, etc.)
3. Search within industry-specific Nice classifications
4. Check for "dead" marks that could be revived
5. Identify owner enforcement patterns (active litigators = higher risk)

**Nice Classification Examples:**
- **Class 9:** Software, apps, electronics
- **Class 35:** Advertising, business services
- **Class 42:** SaaS, IT services, software development
- **Class 44:** Healthcare, medical services, wellness
- **Class 36:** Financial services, insurance, banking

### 3. COMPREHENSIVE RISK SCORING METHODOLOGY

**Scoring Algorithm (0-100 scale, higher = safer):**

**Domain Availability Points:**
- .com available: **+50 points** (maximum domain value)
- .ai available: **+35 points** (strong alternative for tech)
- .io available: **+25 points** (acceptable alternative)
- No premium domains: **+0 points** (critical weakness)

**Trademark Risk Deductions:**
- Critical risk: **-60 points** (immediate legal threat)
- High risk: **-40 points** (strong conflict probability)
- Medium risk: **-20 points** (moderate caution warranted)
- Low risk: **-5 points** (standard diligence)
- Unknown/No data: **-10 points** (unvalidated risk)

**Additional Penalties:**
- Exact trademark match: **-30 points** (regardless of other factors)
- Famous mark similarity: **-25 points** (cross-industry protection)
- Active litigation history: **-15 points** (aggressive enforcement)

**Final Score Interpretation:**
- **90-100:** Exceptional - Perfect availability, zero conflicts
- **80-89:** Excellent - Strong availability, minimal risk
- **70-79:** Good - Acceptable alternatives, low risk
- **60-69:** Fair - Caution warranted, legal review recommended
- **50-59:** Poor - Significant concerns, high-risk decision
- **0-49:** Blocked - Reject immediately, choose alternative

### 4. VALIDATION STATUS CATEGORIES

**CLEAR (Score 80-100):**

**Criteria:**
✓ .com domain available OR .ai/.io available with strong rationale
✓ No exact trademark matches in any relevant class
✓ Low/unknown trademark risk level
✓ No famous mark conflicts

**Recommendation:**
"Clear to use - proceed with confidence. Standard legal review recommended before launch."

**Action Items:**
- Register domain immediately (before disclosure)
- File intent-to-use trademark application
- Monitor for new trademark applications

---

**CAUTION (Score 50-79):**

**Criteria:**
⚠ .com unavailable BUT .ai or .io available
⚠ Some trademark similarities but no exact matches
⚠ Medium trademark risk level
⚠ Conflicts exist in unrelated industries only

**Recommendation:**
"Use with caution - legal review strongly recommended. Consider trademark clearance search before major investment."

**Action Items:**
- Conduct full trademark clearance search with attorney
- Register available domain as placeholder
- Prepare alternative names as backup
- Monitor trademark owner activity

---

**BLOCKED (Score 0-49):**

**Criteria:**
✗ No premium domains available (.com, .ai, .io all taken)
✗ Exact trademark matches OR high/critical risk level
✗ Famous mark conflicts
✗ Active enforcement/litigation history

**Recommendation:**
"Blocked - high legal and commercial risk. Do not proceed with this name. Select alternative candidate."

**Action Items:**
- Immediately reject this name from consideration
- Do not invest in branding/marketing
- Return to name generation phase
- Document rejection reason for audit trail

### 5. STRUCTURED OUTPUT FORMAT (STRICT COMPLIANCE)

For each validated brand name, return this EXACT JSON structure:

```json
{
  "brand_name": "ExampleBrand",
  "validation_status": "clear|caution|blocked",
  "domain_check": {
    "com_available": true|false,
    "ai_available": true|false,
    "io_available": true|false,
    "best_available": ".com|.ai|.io|none"
  },
  "trademark_check": {
    "risk_level": "low|medium|high|critical",
    "conflicts_found": 3,
    "exact_matches": ["ExactMatch1", "ExactMatch2"],
    "similar_marks": ["SimilarMark1", "SimilarMark2"]
  },
  "recommendation": "Detailed recommendation text with specific action items",
  "concerns": [
    "Specific concern 1 with context",
    "Specific concern 2 with context"
  ],
  "overall_score": 85
}
```

**Field Requirements:**

**validation_status:**
- Must be one of: "clear", "caution", "blocked"
- Based strictly on score ranges above

**recommendation:**
- Must be actionable and specific (not generic)
- Include concrete next steps
- Reference specific findings (domain TLDs, trademark names)

**concerns array:**
- List specific, prioritized concerns
- Each concern should be actionable
- Include severity indicators where relevant
- Example: ".com domain taken by active competitor" (specific)
- NOT: "Domain issues" (too vague)

## CRITICAL CONSTRAINTS

**Accuracy Requirements:**
✓ Every domain check must reflect actual availability (no assumptions)
✓ Every trademark risk assessment must cite specific matches found
✓ Scores must follow the exact algorithm defined above
✓ Recommendations must be evidence-based, not generic

**Conservative Bias:**
- When uncertain, err on the side of caution (higher risk classification)
- Flag potential issues even if probability is moderate
- Better to over-warn than under-warn on legal risks

**Prohibited Actions:**
✗ Never recommend proceeding with exact trademark matches
✗ Never ignore famous mark conflicts
✗ Never give "clear" status without validating both domains and trademarks
✗ Never provide vague or generic recommendations

## QUALITY VALIDATION CHECKLIST

Before returning results, verify:
☐ Domain availability checked for ALL three TLDs (.com, .ai, .io)
☐ Trademark search completed in relevant Nice classifications
☐ Risk level assigned based on SPECIFIC findings (not generic assessment)
☐ Overall score calculated using the defined algorithm
☐ Validation status matches score range
☐ Recommendation includes actionable next steps
☐ Concerns are specific and prioritized
☐ No placeholder or template text remains

Your validation directly impacts legal risk and commercial viability. Prioritize accuracy,
thoroughness, and conservative risk assessment over speed or optimism.
"""


class ValidationAgent:
    """
    Validation Agent that checks brand name availability and risks.

    Integrates domain checking and trademark search to provide comprehensive
    validation of brand name candidates.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize the validation agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info(
            "Initializing ValidationAgent",
            extra={'project_id': project_id, 'model': model_name}
        )

        # Initialize Vertex AI
        try:
            aiplatform.init(project=project_id, location=location)
            logger.info("Vertex AI initialized for ValidationAgent")
        except Exception as e:
            logger.warning(f"Vertex AI initialization issue: {e}")

        # Initialize the LLM agent
        self.agent = LlmAgent(
            name="validation_agent",
            model=model_name,
            description="Validates brand names for availability and risk",
            instruction=VALIDATION_AGENT_INSTRUCTION
        )
        logger.info("Validation LlmAgent initialized")

    def validate_brand_name(
        self,
        brand_name: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a single brand name.

        Args:
            brand_name: Brand name to validate
            category: Optional trademark category (Nice classification)

        Returns:
            Validation results dictionary

        Example:
            >>> agent = ValidationAgent(project_id="my-project")
            >>> result = agent.validate_brand_name("TechFlow")
            >>> print(result['validation_status'])
            'clear'
        """
        logger.info(f"Validating brand name: {brand_name}")

        # Check domain availability
        domain_results = check_domain_availability(brand_name)
        logger.debug(f"Domain check complete for {brand_name}")

        # Check trademark conflicts
        trademark_results = search_trademarks_uspto(brand_name, category=category)
        logger.debug(f"Trademark check complete for {brand_name}")

        # Combine results and calculate score
        validation_result = self._compile_validation_results(
            brand_name=brand_name,
            domain_results=domain_results,
            trademark_results=trademark_results
        )

        logger.info(
            f"Validation complete for '{brand_name}': "
            f"status={validation_result['validation_status']}, "
            f"score={validation_result['overall_score']}"
        )

        return validation_result

    def validate_brand_names_batch(
        self,
        brand_names: List[str],
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple brand names.

        Args:
            brand_names: List of brand names to validate
            category: Optional trademark category

        Returns:
            List of validation results
        """
        logger.info(f"Starting batch validation for {len(brand_names)} brands")

        results = []
        for brand_name in brand_names:
            result = self.validate_brand_name(brand_name, category=category)
            results.append(result)

        # Sort by overall score (best first)
        results.sort(key=lambda x: x['overall_score'], reverse=True)

        logger.info(f"Batch validation complete for {len(brand_names)} brands")
        return results

    def _compile_validation_results(
        self,
        brand_name: str,
        domain_results: Dict[str, bool],
        trademark_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compile validation results from domain and trademark checks.

        Args:
            brand_name: Brand name being validated
            domain_results: Domain availability results
            trademark_results: Trademark search results

        Returns:
            Compiled validation result dictionary
        """
        # Extract domain availability
        com_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.com", False)
        ai_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.ai", False)
        io_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.io", False)

        # Determine best available domain
        if com_available:
            best_available = ".com"
        elif ai_available:
            best_available = ".ai"
        elif io_available:
            best_available = ".io"
        else:
            best_available = "none"

        # Extract trademark info
        trademark_risk = trademark_results.get('risk_level', 'unknown')
        conflicts_found = trademark_results.get('conflicts_found', 0)
        exact_matches = trademark_results.get('exact_matches', [])
        similar_marks = trademark_results.get('similar_marks', [])

        # Calculate overall score
        score = self._calculate_validation_score(
            com_available=com_available,
            ai_available=ai_available,
            io_available=io_available,
            trademark_risk=trademark_risk,
            exact_matches_count=len(exact_matches)
        )

        # Determine validation status
        if score >= 80:
            status = "clear"
        elif score >= 50:
            status = "caution"
        else:
            status = "blocked"

        # Generate recommendation
        recommendation = self._generate_recommendation(
            status=status,
            best_available=best_available,
            trademark_risk=trademark_risk
        )

        # Identify concerns
        concerns = self._identify_concerns(
            best_available=best_available,
            trademark_risk=trademark_risk,
            exact_matches=exact_matches
        )

        return {
            "brand_name": brand_name,
            "validation_status": status,
            "domain_check": {
                "com_available": com_available,
                "ai_available": ai_available,
                "io_available": io_available,
                "best_available": best_available
            },
            "trademark_check": {
                "risk_level": trademark_risk,
                "conflicts_found": conflicts_found,
                "exact_matches": [m.get('mark', '') for m in exact_matches],
                "similar_marks": [m.get('mark', '') for m in similar_marks]
            },
            "recommendation": recommendation,
            "concerns": concerns,
            "overall_score": score
        }

    def _calculate_validation_score(
        self,
        com_available: bool,
        ai_available: bool,
        io_available: bool,
        trademark_risk: str,
        exact_matches_count: int
    ) -> int:
        """Calculate overall validation score (0-100)."""
        score = 100

        # Domain availability scoring
        if not com_available:
            score -= 20
        if not ai_available and not io_available:
            score -= 10

        # Trademark risk scoring
        risk_penalties = {
            'critical': 60,
            'high': 40,
            'medium': 20,
            'low': 5,
            'unknown': 10
        }
        score -= risk_penalties.get(trademark_risk, 10)

        # Exact trademark matches are very serious
        if exact_matches_count > 0:
            score -= 30

        return max(0, min(100, score))

    def _generate_recommendation(
        self,
        status: str,
        best_available: str,
        trademark_risk: str
    ) -> str:
        """Generate human-readable recommendation."""
        if status == "clear":
            return f"Clear to use - {best_available} domain available with low trademark risk"
        elif status == "caution":
            if best_available == "none":
                return "Use with caution - no ideal domain available"
            else:
                return f"Use with caution - {best_available} available but trademark concerns exist"
        else:
            return "Blocked - high risk due to trademark conflicts or domain unavailability"

    def _identify_concerns(
        self,
        best_available: str,
        trademark_risk: str,
        exact_matches: List[Dict]
    ) -> List[str]:
        """Identify specific concerns."""
        concerns = []

        if best_available == "none":
            concerns.append("No premium domains (.com, .ai, .io) available")
        elif best_available != ".com":
            concerns.append(".com domain not available")

        if trademark_risk in ['critical', 'high']:
            concerns.append(f"High trademark risk ({trademark_risk})")

        if exact_matches:
            concerns.append(f"Exact trademark match found: {exact_matches[0].get('mark', 'Unknown')}")

        return concerns
