"""
Tests for Memory Bank integration and persistence.

Verifies that user preferences and feedback are correctly stored
and retrieved across multiple sessions.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from src.session.memory_bank import MemoryBankClient, get_memory_bank_client


@pytest.fixture
def temp_memory_dir():
    """Create temporary directory for Memory Bank file storage."""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def memory_client(temp_memory_dir):
    """Create Memory Bank client for testing."""
    # Use test project ID to trigger file-based fallback
    client = MemoryBankClient(
        project_id="test-project-memory",
        location="us-central1"
    )
    return client


class TestMemoryBankPersistence:
    """Test Memory Bank persistence across sessions."""

    def test_store_and_retrieve_user_preference(self, memory_client):
        """Test basic preference storage and retrieval."""
        user_id = "test_user_001"

        # Store industry preference
        result = memory_client.store_user_preference(
            user_id=user_id,
            preference_type="industry",
            preference_value="healthcare",
            metadata={"source": "test"}
        )
        assert result is True

        # Retrieve preferences
        preferences = memory_client.retrieve_user_preferences(user_id)
        assert len(preferences) > 0
        assert any(
            p.get('preference_type') == 'industry' and
            p.get('preference_value') == 'healthcare'
            for p in preferences
        )

    def test_store_multiple_preferences(self, memory_client):
        """Test storing multiple preferences for the same user."""
        user_id = "test_user_002"

        # Store multiple preferences
        preferences_to_store = [
            ("industry", "fintech"),
            ("industry", "healthcare"),
            ("personality", "professional"),
            ("personality", "innovative"),
            ("naming_strategy", "portmanteau"),
        ]

        for pref_type, pref_value in preferences_to_store:
            memory_client.store_user_preference(
                user_id=user_id,
                preference_type=pref_type,
                preference_value=pref_value
            )

        # Retrieve all preferences
        preferences = memory_client.retrieve_user_preferences(user_id)
        assert len(preferences) >= len(preferences_to_store)

        # Verify each preference exists
        for pref_type, pref_value in preferences_to_store:
            assert any(
                p.get('preference_type') == pref_type and
                p.get('preference_value') == pref_value
                for p in preferences
            )

    def test_filter_preferences_by_type(self, memory_client):
        """Test filtering preferences by type."""
        user_id = "test_user_003"

        # Store mixed preferences
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="industry",
            preference_value="tech"
        )
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="personality",
            preference_value="playful"
        )

        # Filter by industry
        industry_prefs = memory_client.retrieve_user_preferences(
            user_id=user_id,
            preference_type="industry"
        )
        assert len(industry_prefs) > 0
        assert all(p.get('preference_type') == 'industry' for p in industry_prefs)

    def test_store_brand_feedback(self, memory_client):
        """Test storing brand name feedback."""
        user_id = "test_user_004"

        # Store accepted brand feedback
        result = memory_client.store_brand_feedback(
            user_id=user_id,
            brand_name="HealthFlow",
            feedback_type="accepted",
            feedback_data={
                "industry": "healthcare",
                "brand_personality": "professional",
                "seo_score": 85
            }
        )
        assert result is True

        # Store rejected brand feedback
        result = memory_client.store_brand_feedback(
            user_id=user_id,
            brand_name="BadName123",
            feedback_type="rejected",
            feedback_data={
                "industry": "healthcare",
                "disliked_patterns": ["numbers", "generic"]
            }
        )
        assert result is True

    def test_learning_insights_extraction(self, memory_client):
        """Test learning insights from stored preferences."""
        user_id = "test_user_005"

        # Store preferences
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="industry",
            preference_value="fintech"
        )
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="personality",
            preference_value="professional"
        )
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="naming_strategy",
            preference_value="portmanteau"
        )

        # Get learning insights
        insights = memory_client.get_learning_insights(user_id)

        assert "preferred_industries" in insights
        assert "preferred_personalities" in insights
        assert "liked_naming_strategies" in insights
        assert "fintech" in insights["preferred_industries"]
        assert "professional" in insights["preferred_personalities"]
        assert "portmanteau" in insights["liked_naming_strategies"]

    def test_persistence_across_sessions(self, memory_client, temp_memory_dir):
        """Test that data persists across client instances."""
        user_id = "test_user_006"

        # Session 1: Store preferences
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="industry",
            preference_value="e-commerce"
        )

        # Simulate new session by creating new client
        new_client = MemoryBankClient(
            project_id="test-project-memory",
            location="us-central1"
        )

        # Session 2: Retrieve preferences
        preferences = new_client.retrieve_user_preferences(user_id)

        assert len(preferences) > 0
        assert any(
            p.get('preference_type') == 'industry' and
            p.get('preference_value') == 'e-commerce'
            for p in preferences
        )

    def test_clear_user_memories(self, memory_client):
        """Test clearing all memories for a user."""
        user_id = "test_user_007"

        # Store some preferences
        memory_client.store_user_preference(
            user_id=user_id,
            preference_type="industry",
            preference_value="retail"
        )

        # Verify preferences exist
        preferences = memory_client.retrieve_user_preferences(user_id)
        assert len(preferences) > 0

        # Clear memories
        result = memory_client.clear_user_memories(user_id)
        assert result is True

        # Verify preferences are cleared
        preferences = memory_client.retrieve_user_preferences(user_id)
        assert len(preferences) == 0

    def test_extract_naming_themes_from_feedback(self, memory_client):
        """Test theme extraction from brand feedback."""
        user_id = "test_user_008"

        # Store multiple accepted brand names with feedback
        accepted_brands = [
            ("FlowHealth", {"industry": "healthcare", "seo_score": 92}),
            ("MediFlow", {"industry": "healthcare", "seo_score": 88}),
            ("HealthSync", {"industry": "healthcare", "seo_score": 85}),
        ]

        for brand_name, feedback_data in accepted_brands:
            memory_client.store_brand_feedback(
                user_id=user_id,
                brand_name=brand_name,
                feedback_type="accepted",
                feedback_data=feedback_data
            )

        # Get learning insights (which extracts themes)
        insights = memory_client.get_learning_insights(user_id, limit=10)

        # Verify themes are extracted
        assert "common_themes" in insights
        # Should detect high SEO preference and healthcare focus
        themes = insights["common_themes"]
        assert any("SEO" in theme or "healthcare" in theme for theme in themes)

    def test_multiple_users_isolation(self, memory_client):
        """Test that data from different users is isolated."""
        user1_id = "test_user_009"
        user2_id = "test_user_010"

        # Store preferences for user 1
        memory_client.store_user_preference(
            user_id=user1_id,
            preference_type="industry",
            preference_value="tech"
        )

        # Store preferences for user 2
        memory_client.store_user_preference(
            user_id=user2_id,
            preference_type="industry",
            preference_value="fashion"
        )

        # Retrieve preferences for each user
        user1_prefs = memory_client.retrieve_user_preferences(user1_id)
        user2_prefs = memory_client.retrieve_user_preferences(user2_id)

        # Verify isolation
        assert any(p.get('preference_value') == 'tech' for p in user1_prefs)
        assert not any(p.get('preference_value') == 'fashion' for p in user1_prefs)

        assert any(p.get('preference_value') == 'fashion' for p in user2_prefs)
        assert not any(p.get('preference_value') == 'tech' for p in user2_prefs)


class TestMemoryBankSingleton:
    """Test Memory Bank singleton pattern."""

    def test_singleton_returns_same_instance(self, temp_memory_dir):
        """Test that get_memory_bank_client returns singleton."""
        client1 = get_memory_bank_client(
            project_id="test-project-singleton",
            location="us-central1"
        )
        client2 = get_memory_bank_client()

        # Should return the same instance
        assert client1 is client2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
