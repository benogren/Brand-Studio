"""
Name Quality Evaluator for AI Brand Studio.

Evaluates generated brand names across multiple quality dimensions:
- Pronounceability: How easy the name is to pronounce
- Memorability: How memorable and distinctive the name is
- Industry Relevance: How well the name fits the target industry
- Uniqueness: How unique and non-generic the name is
"""

import re
from typing import Dict, Any, List


class NameQualityEvaluator:
    """
    Evaluates brand name quality across multiple dimensions.

    Scoring criteria:
    - Pronounceability (0-1): Vowel ratio, consonant clusters, length
    - Memorability (0-1): Length, distinctiveness, phonetic patterns
    - Industry Relevance (0-1): Keyword matching, semantic appropriateness
    - Uniqueness (0-1): Non-generic, avoids common words

    Overall quality score: Weighted average of all dimensions
    """

    # Common generic words to penalize
    GENERIC_WORDS = {
        'app', 'tech', 'pro', 'max', 'plus', 'hub', 'link', 'base',
        'cloud', 'system', 'platform', 'solution', 'service', 'digital',
        'online', 'web', 'net', 'soft', 'ware', 'corp', 'inc', 'llc'
    }

    # Industry-specific keywords for relevance scoring
    INDUSTRY_KEYWORDS = {
        'healthcare': ['health', 'med', 'care', 'doc', 'clinic', 'patient', 'cure', 'well', 'vita'],
        'fintech': ['fin', 'pay', 'bank', 'money', 'cash', 'invest', 'wealth', 'cap', 'fund'],
        'ecommerce': ['shop', 'cart', 'store', 'market', 'buy', 'sell', 'commerce', 'trade'],
        'food': ['food', 'meal', 'eat', 'cook', 'dish', 'recipe', 'nutri', 'taste'],
        'fitness': ['fit', 'gym', 'work', 'train', 'muscle', 'strength', 'health', 'active'],
        'education': ['learn', 'edu', 'teach', 'school', 'class', 'study', 'know'],
        'tech': ['tech', 'data', 'code', 'dev', 'byte', 'bit', 'cloud', 'net']
    }

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize evaluator with custom weights.

        Args:
            weights: Custom dimension weights (default: equal weights)
        """
        self.weights = weights or {
            'pronounceable': 0.25,
            'memorable': 0.25,
            'industry_relevant': 0.25,
            'unique': 0.25
        }

    def evaluate(self, names: List[str], industry: str = 'general') -> Dict[str, Any]:
        """
        Evaluate a list of brand names.

        Args:
            names: List of brand name strings
            industry: Target industry for relevance scoring

        Returns:
            Dictionary with:
            - overall_score: Weighted average quality score (0-1)
            - dimension_scores: Scores for each dimension
            - per_name_scores: Individual scores for each name
            - pass_rate: Percentage of names above threshold (0.7)
        """
        if not names:
            return {
                'overall_score': 0.0,
                'dimension_scores': {},
                'per_name_scores': [],
                'pass_rate': 0.0
            }

        per_name_scores = []

        for name in names:
            scores = {
                'name': name,
                'pronounceable': self._score_pronounceability(name),
                'memorable': self._score_memorability(name),
                'industry_relevant': self._score_industry_relevance(name, industry),
                'unique': self._score_uniqueness(name)
            }
            scores['overall'] = sum(
                scores[dim] * self.weights[dim]
                for dim in self.weights
            )
            per_name_scores.append(scores)

        # Calculate aggregate dimension scores
        dimension_scores = {
            dim: sum(s[dim] for s in per_name_scores) / len(per_name_scores)
            for dim in ['pronounceable', 'memorable', 'industry_relevant', 'unique']
        }

        overall_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in self.weights
        )

        # Calculate pass rate (names with overall score >= 0.7)
        passing_names = sum(1 for s in per_name_scores if s['overall'] >= 0.7)
        pass_rate = passing_names / len(names) if names else 0.0

        return {
            'overall_score': overall_score,
            'dimension_scores': dimension_scores,
            'per_name_scores': per_name_scores,
            'pass_rate': pass_rate,
            'total_names': len(names),
            'passing_names': passing_names
        }

    def _score_pronounceability(self, name: str) -> float:
        """
        Score pronounceability based on phonetic patterns.

        Factors:
        - Vowel ratio (30-50% ideal)
        - Consonant clusters (penalize 3+ consonants)
        - Length (4-12 characters ideal)
        """
        name_lower = name.lower()
        score = 1.0

        # Vowel ratio
        vowels = sum(1 for c in name_lower if c in 'aeiou')
        vowel_ratio = vowels / len(name_lower) if name_lower else 0
        if 0.3 <= vowel_ratio <= 0.5:
            pass  # Ideal range
        elif vowel_ratio < 0.2 or vowel_ratio > 0.6:
            score -= 0.3
        else:
            score -= 0.15

        # Consonant clusters
        consonant_cluster_pattern = r'[^aeiou]{3,}'
        if re.search(consonant_cluster_pattern, name_lower):
            score -= 0.2

        # Length
        if 4 <= len(name) <= 12:
            pass  # Ideal range
        elif len(name) < 4 or len(name) > 15:
            score -= 0.3
        else:
            score -= 0.15

        return max(0.0, min(1.0, score))

    def _score_memorability(self, name: str) -> float:
        """
        Score memorability based on distinctiveness and patterns.

        Factors:
        - Length (shorter is more memorable)
        - Unique patterns (alliteration, rhyming)
        - Distinctiveness
        """
        score = 1.0

        # Length (6-10 characters ideal for memorability)
        if 6 <= len(name) <= 10:
            score += 0.1
        elif len(name) > 15:
            score -= 0.3

        # Alliteration (same first letter in parts)
        parts = re.findall(r'[A-Z][a-z]+', name)
        if len(parts) >= 2:
            first_letters = [p[0].lower() for p in parts]
            if len(set(first_letters)) < len(first_letters):
                score += 0.15  # Has alliteration

        # Mixed case (CamelCase is more distinctive)
        if any(c.isupper() for c in name[1:]):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _score_industry_relevance(self, name: str, industry: str) -> float:
        """
        Score industry relevance based on keyword matching.

        Args:
            name: Brand name
            industry: Target industry

        Returns:
            Relevance score (0-1)
        """
        name_lower = name.lower()
        score = 0.5  # Base score for neutrality

        # Get industry keywords
        keywords = self.INDUSTRY_KEYWORDS.get(industry, [])
        if not keywords:
            return score  # Neutral for unknown industries

        # Check for keyword presence
        matches = sum(1 for kw in keywords if kw in name_lower)
        if matches > 0:
            score = min(1.0, 0.7 + (matches * 0.15))

        return score

    def _score_uniqueness(self, name: str) -> float:
        """
        Score uniqueness by penalizing generic words.

        Args:
            name: Brand name

        Returns:
            Uniqueness score (0-1)
        """
        name_lower = name.lower()
        score = 1.0

        # Penalize generic words
        generic_count = sum(
            1 for word in self.GENERIC_WORDS
            if word in name_lower
        )

        if generic_count > 0:
            score -= (generic_count * 0.3)

        # Penalize common patterns
        if re.match(r'^[A-Z][a-z]+[0-9]+$', name):  # Like "App123"
            score -= 0.4

        # Penalize very short generic names
        if len(name) <= 3 and name_lower in {'app', 'web', 'net', 'pro'}:
            score -= 0.5

        return max(0.0, score)


# Convenience function for quick evaluation
def evaluate_name_quality(
    names: List[str],
    industry: str = 'general',
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Quick evaluation of name quality.

    Args:
        names: List of brand names
        industry: Target industry
        threshold: Minimum score for passing (default: 0.7)

    Returns:
        Evaluation results with pass/fail status
    """
    evaluator = NameQualityEvaluator()
    results = evaluator.evaluate(names, industry)
    results['threshold'] = threshold
    results['passed'] = results['overall_score'] >= threshold
    return results
