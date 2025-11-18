"""
Interactive feedback system for brand name generation.

Allows users to provide iterative feedback on generated names
and refine results before proceeding to validation.
"""

from src.feedback.name_feedback import (
    NameFeedback,
    FeedbackType,
    NameGenerationSession,
    collect_feedback_interactive,
    collect_post_validation_choice
)

__all__ = [
    'NameFeedback',
    'FeedbackType',
    'NameGenerationSession',
    'collect_feedback_interactive',
    'collect_post_validation_choice'
]
