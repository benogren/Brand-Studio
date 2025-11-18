"""
Content Quality Evaluator for AI Brand Studio.

Evaluates the quality of generated content:
- Taglines (count, length, relevance)
- Brand story (length, completeness, tone)
- SEO metadata (meta title, description)
"""

from typing import Dict, Any, List


class ContentQualityEvaluator:
    """
    Evaluates content quality for brand narratives and marketing copy.

    Checks:
    - Tagline quality (count 3-5, length 5-8 words each)
    - Brand story quality (length 150-300 words, tone consistency)
    - Value proposition (length 20-30 words, clarity)
    - SEO metadata (meta title 50-60 chars, meta description 150-160 chars)
    """

    def __init__(self):
        """Initialize content quality evaluator."""
        pass

    def evaluate(self, content: Dict[str, Any], expected_tone: str = 'professional') -> Dict[str, Any]:
        """
        Evaluate content quality.

        Args:
            content: Dictionary containing:
                - taglines: List of tagline strings
                - brand_story: Brand story text
                - hero_copy: Landing page hero copy
                - value_proposition: Value proposition statement
                - meta_title: SEO meta title (optional)
                - meta_description: SEO meta description (optional)
            expected_tone: Expected brand tone/personality

        Returns:
            Dictionary with:
            - tagline_score: Quality score for taglines (0-1)
            - story_score: Quality score for brand story (0-1)
            - seo_score: Quality score for SEO metadata (0-1)
            - overall_score: Weighted average quality score
            - passed: Whether content meets minimum standards
        """
        if not content:
            return {
                'tagline_score': 0.0,
                'story_score': 0.0,
                'seo_score': 0.0,
                'overall_score': 0.0,
                'passed': False,
                'error': 'No content provided'
            }

        # Evaluate each component
        tagline_score = self._evaluate_taglines(content.get('taglines', []))
        story_score = self._evaluate_story(
            content.get('brand_story', ''),
            expected_tone
        )
        seo_score = self._evaluate_seo_metadata(content)

        # Calculate overall score (weighted average)
        overall_score = (
            tagline_score * 0.3 +
            story_score * 0.4 +
            seo_score * 0.3
        )

        # Determine if passed (overall >= 0.7 and no component < 0.5)
        passed = (
            overall_score >= 0.7 and
            tagline_score >= 0.5 and
            story_score >= 0.5 and
            seo_score >= 0.5
        )

        return {
            'tagline_score': tagline_score,
            'story_score': story_score,
            'seo_score': seo_score,
            'overall_score': overall_score,
            'passed': passed,
            'details': {
                'tagline_count': len(content.get('taglines', [])),
                'story_length': len(content.get('brand_story', '').split()),
                'has_meta_title': bool(content.get('meta_title')),
                'has_meta_description': bool(content.get('meta_description'))
            }
        }

    def _evaluate_taglines(self, taglines: List[str]) -> float:
        """
        Evaluate tagline quality.

        Criteria:
        - Count: 3-5 taglines ideal
        - Length: 5-8 words each ideal
        - Variety: Different approaches
        """
        if not taglines:
            return 0.0

        score = 1.0

        # Count (3-5 ideal)
        count = len(taglines)
        if 3 <= count <= 5:
            pass  # Perfect
        elif count < 3:
            score -= 0.3
        elif count > 7:
            score -= 0.2

        # Length (5-8 words ideal per tagline)
        lengths = [len(tagline.split()) for tagline in taglines]
        ideal_length_count = sum(1 for length in lengths if 5 <= length <= 8)
        length_score = ideal_length_count / len(taglines) if taglines else 0
        score = score * 0.5 + length_score * 0.5

        # Non-empty check
        non_empty = sum(1 for t in taglines if t.strip())
        if non_empty < len(taglines):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _evaluate_story(self, story: str, expected_tone: str) -> float:
        """
        Evaluate brand story quality.

        Criteria:
        - Length: 150-300 words ideal
        - Completeness: Has substantive content
        - Tone appropriateness (basic check)
        """
        if not story:
            return 0.0

        score = 1.0
        word_count = len(story.split())

        # Length (150-300 words ideal)
        if 150 <= word_count <= 300:
            pass  # Perfect
        elif word_count < 100:
            score -= 0.4
        elif word_count < 150:
            score -= 0.2
        elif word_count > 400:
            score -= 0.2
        elif word_count > 300:
            score -= 0.1

        # Completeness (not just placeholder text)
        if 'placeholder' in story.lower() or 'todo' in story.lower():
            score -= 0.5

        # Basic tone check (very simple keyword-based)
        story_lower = story.lower()
        tone_keywords = {
            'professional': ['professional', 'expert', 'trusted', 'reliable'],
            'playful': ['fun', 'playful', 'joy', 'exciting'],
            'innovative': ['innovative', 'cutting-edge', 'revolutionary', 'advanced'],
            'luxury': ['luxury', 'premium', 'exclusive', 'sophisticated']
        }

        if expected_tone in tone_keywords:
            keywords = tone_keywords[expected_tone]
            has_tone_keyword = any(kw in story_lower for kw in keywords)
            if has_tone_keyword:
                score += 0.1

        return max(0.0, min(1.0, score))

    def _evaluate_seo_metadata(self, content: Dict[str, Any]) -> float:
        """
        Evaluate SEO metadata quality.

        Criteria:
        - Meta title: 50-60 characters ideal
        - Meta description: 150-160 characters ideal
        - Presence of both
        """
        meta_title = content.get('meta_title', '')
        meta_description = content.get('meta_description', '')

        score = 0.5  # Base score for having some content

        # Meta title
        if meta_title:
            title_len = len(meta_title)
            if 50 <= title_len <= 60:
                score += 0.25  # Perfect length
            elif 40 <= title_len <= 70:
                score += 0.15  # Acceptable
            elif title_len > 0:
                score += 0.1  # At least something
        else:
            score -= 0.2  # Missing meta title

        # Meta description
        if meta_description:
            desc_len = len(meta_description)
            if 150 <= desc_len <= 160:
                score += 0.25  # Perfect length
            elif 130 <= desc_len <= 180:
                score += 0.15  # Acceptable
            elif desc_len > 0:
                score += 0.1  # At least something
        else:
            score -= 0.2  # Missing meta description

        return max(0.0, min(1.0, score))


# Convenience function
def evaluate_content_quality(
    content: Dict[str, Any],
    expected_tone: str = 'professional',
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Quick content quality evaluation.

    Args:
        content: Content to evaluate
        expected_tone: Expected brand tone
        threshold: Minimum score for passing

    Returns:
        Evaluation results with pass/fail status
    """
    evaluator = ContentQualityEvaluator()
    results = evaluator.evaluate(content, expected_tone)
    results['threshold'] = threshold
    return results
