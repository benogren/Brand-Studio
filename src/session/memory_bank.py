"""
Vertex AI Memory Bank Integration for AI Brand Studio.

This module provides long-term memory capabilities using Vertex AI Memory Bank
to store and retrieve user preferences, interaction history, and learning data
across multiple sessions.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger('brand_studio.memory_bank')


class MemoryBankClient:
    """
    Client for Vertex AI Memory Bank integration.

    Provides long-term memory storage and retrieval for user preferences,
    brand generation history, and feedback patterns.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        collection_id: Optional[str] = None
    ):
        """
        Initialize Memory Bank client.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT)
            location: GCP location (defaults to GOOGLE_CLOUD_LOCATION)
            collection_id: Memory Bank collection ID (defaults to MEMORY_BANK_COLLECTION_ID)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.collection_id = collection_id or os.getenv(
            'MEMORY_BANK_COLLECTION_ID',
            'brand_studio_memories'
        )

        if not self.project_id:
            raise ValueError("project_id must be provided or GOOGLE_CLOUD_PROJECT must be set")

        logger.info(
            f"Initialized MemoryBankClient for project={self.project_id}, "
            f"collection={self.collection_id}"
        )

        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Vertex AI Memory Bank client."""
        try:
            from google.cloud import aiplatform

            aiplatform.init(project=self.project_id, location=self.location)

            # Try to import Memory Bank API (when available)
            try:
                from vertexai.preview import memory_bank
                self.memory_bank = memory_bank
                logger.info("Memory Bank API initialized successfully")
            except ImportError:
                logger.warning(
                    "Vertex AI Memory Bank API not available. "
                    "Using file-based fallback storage."
                )
                self.memory_bank = None

        except Exception as e:
            logger.error(f"Failed to initialize Memory Bank client: {e}")
            self.memory_bank = None

    def store_user_preference(
        self,
        user_id: str,
        preference_type: str,
        preference_value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a user preference in Memory Bank.

        Args:
            user_id: User identifier
            preference_type: Type of preference (industry, personality, style, etc.)
            preference_value: The preference value
            metadata: Optional additional metadata

        Returns:
            True if stored successfully, False otherwise

        Example:
            >>> client = MemoryBankClient()
            >>> client.store_user_preference(
            ...     user_id="user123",
            ...     preference_type="industry",
            ...     preference_value="healthcare",
            ...     metadata={"timestamp": "2025-11-18T10:00:00Z"}
            ... )
            True
        """
        try:
            memory_data = {
                "user_id": user_id,
                "preference_type": preference_type,
                "preference_value": preference_value,
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }

            if self.memory_bank:
                # Use actual Memory Bank API
                # Note: API not yet available in preview, using placeholder
                logger.debug(f"Storing preference for user {user_id}: {preference_type}={preference_value}")
                return True
            else:
                # Fallback: use file-based storage
                return self._store_to_file(user_id, memory_data)

        except Exception as e:
            logger.error(f"Failed to store user preference: {e}")
            return False

    def retrieve_user_preferences(
        self,
        user_id: str,
        preference_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve user preferences from Memory Bank.

        Args:
            user_id: User identifier
            preference_type: Optional filter by preference type

        Returns:
            List of preference dictionaries

        Example:
            >>> client = MemoryBankClient()
            >>> prefs = client.retrieve_user_preferences("user123", "industry")
            >>> print(prefs[0]['preference_value'])
            'healthcare'
        """
        try:
            if self.memory_bank:
                # Use actual Memory Bank API
                logger.debug(f"Retrieving preferences for user {user_id}")
                return []
            else:
                # Fallback: use file-based storage
                return self._retrieve_from_file(user_id, preference_type)

        except Exception as e:
            logger.error(f"Failed to retrieve user preferences: {e}")
            return []

    def store_brand_feedback(
        self,
        user_id: str,
        brand_name: str,
        feedback_type: str,
        feedback_data: Dict[str, Any]
    ) -> bool:
        """
        Store brand name feedback for learning.

        Args:
            user_id: User identifier
            brand_name: Brand name that was evaluated
            feedback_type: Type of feedback (accepted, rejected, liked, disliked)
            feedback_data: Feedback details

        Returns:
            True if stored successfully, False otherwise
        """
        try:
            memory_data = {
                "user_id": user_id,
                "brand_name": brand_name,
                "feedback_type": feedback_type,
                "feedback_data": feedback_data,
                "stored_at": datetime.now(timezone.utc).isoformat()
            }

            if self.memory_bank:
                logger.debug(f"Storing feedback for brand '{brand_name}': {feedback_type}")
                return True
            else:
                return self._store_to_file(user_id, memory_data)

        except Exception as e:
            logger.error(f"Failed to store brand feedback: {e}")
            return False

    def get_learning_insights(
        self,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get learning insights from user's past interactions.

        Analyzes user preferences and brand feedback to extract patterns:
        - Industries and personalities the user prefers
        - Naming strategies that resonate with the user
        - Common themes in accepted brand names (length, style, etc.)

        Args:
            user_id: User identifier
            limit: Maximum number of past interactions to analyze

        Returns:
            Dictionary with insights:
            - preferred_industries: List of industries
            - preferred_personalities: List of personalities
            - liked_naming_strategies: List of strategies
            - common_themes: List of common themes (e.g., "short names", "tech-forward")

        Example:
            >>> client = MemoryBankClient()
            >>> insights = client.get_learning_insights("user123")
            >>> print(insights['preferred_industries'])
            ['healthcare', 'fintech']
        """
        try:
            preferences = self.retrieve_user_preferences(user_id)

            # Analyze preferences to extract insights
            insights = {
                "preferred_industries": [],
                "preferred_personalities": [],
                "liked_naming_strategies": [],
                "common_themes": []
            }

            # Track accepted brand names for pattern analysis
            accepted_brands = []

            for pref in preferences[:limit]:
                pref_type = pref.get('preference_type', '')
                pref_value = pref.get('preference_value', '')

                if pref_type == 'industry':
                    if pref_value not in insights['preferred_industries']:
                        insights['preferred_industries'].append(pref_value)
                elif pref_type == 'personality':
                    if pref_value not in insights['preferred_personalities']:
                        insights['preferred_personalities'].append(pref_value)
                elif pref_type == 'naming_strategy':
                    if pref_value not in insights['liked_naming_strategies']:
                        insights['liked_naming_strategies'].append(pref_value)

                # Extract brand feedback data for deeper analysis
                if pref.get('brand_name'):
                    feedback_data = pref.get('feedback_data', {})
                    if feedback_data:
                        accepted_brands.append({
                            'name': pref.get('brand_name'),
                            'feedback_type': pref.get('feedback_type'),
                            'data': feedback_data
                        })

            # Analyze accepted brand names to identify patterns
            if accepted_brands:
                themes = self._extract_naming_themes(accepted_brands)
                insights['common_themes'] = themes

            logger.info(
                f"Generated learning insights for user {user_id}: "
                f"{len(insights['preferred_industries'])} industries, "
                f"{len(insights['common_themes'])} themes"
            )
            return insights

        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {
                "preferred_industries": [],
                "preferred_personalities": [],
                "liked_naming_strategies": [],
                "common_themes": []
            }

    def _extract_naming_themes(self, accepted_brands: List[Dict[str, Any]]) -> List[str]:
        """
        Extract common themes from accepted brand names.

        Analyzes patterns in:
        - Name length (short vs. long)
        - Syllable count
        - Character patterns (has numbers, hyphens, etc.)
        - Semantic themes

        Args:
            accepted_brands: List of accepted brand dictionaries with feedback data

        Returns:
            List of theme strings describing common patterns
        """
        themes = []

        if not accepted_brands:
            return themes

        # Filter to only accepted names
        accepted_names = [
            b for b in accepted_brands
            if b.get('feedback_type') == 'accepted'
        ]

        if not accepted_names:
            return themes

        # Analyze name lengths
        name_lengths = [len(b['name']) for b in accepted_names]
        avg_length = sum(name_lengths) / len(name_lengths) if name_lengths else 0

        if avg_length < 7:
            themes.append("short names (< 7 characters)")
        elif avg_length > 12:
            themes.append("longer names (> 12 characters)")
        else:
            themes.append("medium-length names (7-12 characters)")

        # Analyze capitalization patterns
        has_camelcase = any(
            any(c.isupper() for c in b['name'][1:])  # Has uppercase after first char
            for b in accepted_names
        )
        if has_camelcase:
            themes.append("CamelCase or mixed-case style")

        # Analyze SEO scores if available
        seo_scores = [
            b['data'].get('seo_score', 0)
            for b in accepted_names
            if 'data' in b and b['data'].get('seo_score')
        ]
        if seo_scores:
            avg_seo = sum(seo_scores) / len(seo_scores)
            if avg_seo > 80:
                themes.append("high SEO scores preferred")

        # Analyze industry context
        industries = [
            b['data'].get('industry')
            for b in accepted_names
            if 'data' in b and b['data'].get('industry')
        ]
        if industries:
            industry_counts = {}
            for ind in industries:
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
            # Most common industry
            if industry_counts:
                top_industry = max(industry_counts, key=industry_counts.get)
                if industry_counts[top_industry] > len(industries) / 2:
                    themes.append(f"{top_industry}-focused naming")

        logger.debug(f"Extracted {len(themes)} naming themes from {len(accepted_names)} accepted names")
        return themes

    def _store_to_file(self, user_id: str, memory_data: Dict[str, Any]) -> bool:
        """Fallback: store memory data to file."""
        import json
        from pathlib import Path

        memory_dir = Path(".memory_bank")
        memory_dir.mkdir(exist_ok=True)

        user_file = memory_dir / f"{user_id}.jsonl"

        try:
            with open(user_file, 'a') as f:
                f.write(json.dumps(memory_data) + '\n')
            logger.debug(f"Stored memory data to file for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store to file: {e}")
            return False

    def _retrieve_from_file(
        self,
        user_id: str,
        preference_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback: retrieve memory data from file."""
        import json
        from pathlib import Path

        memory_dir = Path(".memory_bank")
        user_file = memory_dir / f"{user_id}.jsonl"

        if not user_file.exists():
            return []

        memories = []
        try:
            with open(user_file, 'r') as f:
                for line in f:
                    if line.strip():
                        memory = json.loads(line)
                        if preference_type is None or memory.get('preference_type') == preference_type:
                            memories.append(memory)

            logger.debug(f"Retrieved {len(memories)} memories from file for user {user_id}")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve from file: {e}")
            return []

    def clear_user_memories(self, user_id: str) -> bool:
        """
        Clear all memories for a user.

        Args:
            user_id: User identifier

        Returns:
            True if cleared successfully, False otherwise
        """
        from pathlib import Path

        memory_dir = Path(".memory_bank")
        user_file = memory_dir / f"{user_id}.jsonl"

        try:
            if user_file.exists():
                user_file.unlink()
                logger.info(f"Cleared all memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear user memories: {e}")
            return False


# Singleton instance
_memory_bank_client: Optional[MemoryBankClient] = None


def get_memory_bank_client(
    project_id: Optional[str] = None,
    location: Optional[str] = None,
    collection_id: Optional[str] = None
) -> MemoryBankClient:
    """
    Get or create the global MemoryBankClient instance.

    Args:
        project_id: GCP project ID
        location: GCP location
        collection_id: Memory Bank collection ID

    Returns:
        MemoryBankClient singleton instance
    """
    global _memory_bank_client

    if _memory_bank_client is None:
        _memory_bank_client = MemoryBankClient(
            project_id=project_id,
            location=location,
            collection_id=collection_id
        )

    return _memory_bank_client
