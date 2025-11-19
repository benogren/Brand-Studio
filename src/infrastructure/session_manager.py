"""
Session State Manager for Brand Studio.

Manages persistent session state across CLI commands using ADK's
DatabaseSessionService pattern from Day 3 coursework.

This allows the interactive workflow:
1. Generate names → save to session
2. User reviews → provide feedback
3. Validate names → save results
4. Generate story → complete workflow
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('brand_studio.session_manager')


class BrandSessionState:
    """
    Manages brand generation session state.

    Stores all workflow data in a structured format that persists
    across CLI command invocations.
    """

    def __init__(self, session_id: str):
        """
        Initialize session state.

        Args:
            session_id: Unique identifier for this brand generation session
        """
        self.session_id = session_id
        self.state: Dict[str, Any] = {
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'current_step': 'initial',  # initial, names_generated, validated, story_generated
            'product_info': {},
            'research_insights': {},
            'generated_names': [],
            'selected_names': [],
            'feedback_history': [],
            'validation_results': {},
            'seo_results': {},
            'brand_story': {}
        }

    def set_product_info(self, product: str, audience: str, personality: str, industry: str) -> None:
        """Store product information."""
        self.state['product_info'] = {
            'product': product,
            'audience': audience,
            'personality': personality,
            'industry': industry
        }
        self._update_timestamp()

    def set_research_insights(self, insights: Dict[str, Any]) -> None:
        """Store research insights."""
        self.state['research_insights'] = insights
        self._update_timestamp()

    def add_generated_names(self, names: List[Dict[str, Any]], replace: bool = False) -> None:
        """
        Add generated names to session.

        Args:
            names: List of name candidates
            replace: If True, replace existing names; if False, append
        """
        if replace:
            self.state['generated_names'] = names
        else:
            self.state['generated_names'].extend(names)

        self.state['current_step'] = 'names_generated'
        self._update_timestamp()

    def add_feedback(self, feedback: str, liked_names: Union[List[str], None] = None) -> None:
        """
        Add user feedback for name regeneration.

        Args:
            feedback: User's textual feedback
            liked_names: List of name strings the user liked
        """
        feedback_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'feedback': feedback,
            'liked_names': liked_names or []
        }
        self.state['feedback_history'].append(feedback_entry)
        self._update_timestamp()

    def set_selected_names(self, names: List[str]) -> None:
        """Set names selected for validation."""
        self.state['selected_names'] = names
        self._update_timestamp()

    def set_validation_results(self, results: Dict[str, Any]) -> None:
        """Store validation results."""
        self.state['validation_results'] = results
        self.state['current_step'] = 'validated'
        self._update_timestamp()

    def set_seo_results(self, results: Dict[str, Any]) -> None:
        """Store SEO optimization results."""
        self.state['seo_results'] = results
        self._update_timestamp()

    def set_brand_story(self, story: Dict[str, Any]) -> None:
        """Store brand story."""
        self.state['brand_story'] = story
        self.state['current_step'] = 'story_generated'
        self._update_timestamp()

    def get_current_step(self) -> str:
        """Get current workflow step."""
        return self.state['current_step']

    def get_product_info(self) -> Dict[str, Any]:
        """Get product information."""
        return self.state['product_info']

    def get_research_insights(self) -> Dict[str, Any]:
        """Get research insights."""
        return self.state['research_insights']

    def get_generated_names(self) -> List[Dict[str, Any]]:
        """Get all generated names."""
        return self.state['generated_names']

    def get_selected_names(self) -> List[str]:
        """Get selected names for validation."""
        return self.state['selected_names']

    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """Get feedback history."""
        return self.state['feedback_history']

    def get_validation_results(self) -> Dict[str, Any]:
        """Get validation results."""
        return self.state['validation_results']

    def get_seo_results(self) -> Dict[str, Any]:
        """Get SEO results."""
        return self.state['seo_results']

    def get_brand_story(self) -> Dict[str, Any]:
        """Get brand story."""
        return self.state['brand_story']

    def to_dict(self) -> Dict[str, Any]:
        """Export state as dictionary."""
        return self.state.copy()

    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.state['updated_at'] = datetime.utcnow().isoformat()


class SessionManager:
    """
    File-based session persistence manager.

    Uses JSON files to persist session state across CLI invocations,
    following the ADK DatabaseSessionService pattern but simplified
    for CLI use.
    """

    def __init__(self, storage_dir: Union[str, None] = None):
        """
        Initialize session manager.

        Args:
            storage_dir: Directory to store session files (default: .brand-sessions)
        """
        if storage_dir is None:
            storage_dir = '.brand-sessions'

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        logger.info(f"SessionManager initialized with storage: {self.storage_dir}")

    def create_session(self, session_id: str) -> BrandSessionState:
        """
        Create new session.

        Args:
            session_id: Unique session identifier

        Returns:
            New BrandSessionState instance
        """
        session = BrandSessionState(session_id)
        self.save_session(session)
        logger.info(f"Created new session: {session_id}")
        return session

    def load_session(self, session_id: str) -> Union[BrandSessionState, None]:
        """
        Load existing session.

        Args:
            session_id: Session identifier

        Returns:
            BrandSessionState if found, None otherwise
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if not session_file.exists():
            logger.warning(f"Session not found: {session_id}")
            return None

        try:
            with open(session_file, 'r') as f:
                state_dict = json.load(f)

            session = BrandSessionState(session_id)
            session.state = state_dict

            logger.info(f"Loaded session: {session_id} (step: {session.get_current_step()})")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def save_session(self, session: BrandSessionState) -> None:
        """
        Save session to disk.

        Args:
            session: Session state to save
        """
        session_file = self.storage_dir / f"{session.session_id}.json"

        try:
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)

            logger.debug(f"Saved session: {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            raise

    def list_sessions(self) -> List[str]:
        """
        List all session IDs.

        Returns:
            List of session IDs
        """
        session_files = self.storage_dir.glob("*.json")
        return [f.stem for f in session_files]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
            return True

        return False

    def get_or_create_session(self, session_id: str) -> BrandSessionState:
        """
        Get existing session or create new one.

        Args:
            session_id: Session identifier

        Returns:
            BrandSessionState instance
        """
        session = self.load_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session


# Global session manager instance
_session_manager: Union[SessionManager, None] = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
