"""
Tests for the orchestrator agent.

This module tests the orchestrator's ability to coordinate workflows
and manage sub-agents.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.agents.orchestrator import BrandStudioOrchestrator


class EchoAgent:
    """
    Simple echo agent for testing coordination.

    This agent echoes back any input it receives, useful for verifying
    that the orchestrator can properly delegate to sub-agents.
    """

    def __init__(self, name: str):
        """
        Initialize the echo agent.

        Args:
            name: Name of the agent
        """
        self.name = name
        self.call_count = 0
        self.last_input = None

    def execute(self, input_data: dict) -> dict:
        """
        Echo back the input data.

        Args:
            input_data: Input to echo

        Returns:
            Dictionary with echoed data
        """
        self.call_count += 1
        self.last_input = input_data

        return {
            'agent_name': self.name,
            'input_received': input_data,
            'call_count': self.call_count,
            'status': 'success'
        }


class TestOrchestratorBasic:
    """Test basic orchestrator functionality."""

    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly."""
        # Mock Vertex AI initialization to avoid GCP dependencies
        import sys
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    location='us-central1',
                    enable_cloud_logging=False
                )

                assert orchestrator.project_id == 'test-project'
                assert orchestrator.location == 'us-central1'
                assert orchestrator.model_name == 'gemini-2.5-flash-lite'
                assert len(orchestrator.sub_agents) == 0

    def test_add_sub_agent(self):
        """Test adding sub-agents to orchestrator."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                # Create echo agents
                echo1 = EchoAgent('echo1')
                echo2 = EchoAgent('echo2')

                # Add sub-agents
                orchestrator.add_sub_agent(echo1)
                orchestrator.add_sub_agent(echo2)

                assert len(orchestrator.sub_agents) == 2
                assert orchestrator.sub_agents[0].name == 'echo1'
                assert orchestrator.sub_agents[1].name == 'echo2'

    def test_analyze_user_brief_valid(self):
        """Test analyzing a valid user brief."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                user_brief = {
                    'product_description': 'AI meal planning app',
                    'target_audience': 'Parents aged 28-40',
                    'brand_personality': 'warm',
                    'industry': 'food_tech'
                }

                analysis = orchestrator.analyze_user_brief(user_brief)

                assert analysis['product_description'] == 'AI meal planning app'
                assert analysis['target_audience'] == 'Parents aged 28-40'
                assert analysis['brand_personality'] == 'warm'
                assert analysis['industry'] == 'food_tech'
                assert 'workflow_stages' in analysis
                assert len(analysis['workflow_stages']) == 5

    def test_analyze_user_brief_missing_required(self):
        """Test analyzing user brief with missing required field."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                # Missing product_description
                user_brief = {
                    'target_audience': 'Parents aged 28-40',
                    'brand_personality': 'warm'
                }

                with pytest.raises(ValueError) as exc_info:
                    orchestrator.analyze_user_brief(user_brief)

                assert 'product_description is required' in str(exc_info.value)

    def test_analyze_user_brief_defaults(self):
        """Test that default values are applied for optional fields."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                # Only required field
                user_brief = {
                    'product_description': 'AI meal planning app'
                }

                analysis = orchestrator.analyze_user_brief(user_brief)

                assert analysis['brand_personality'] == 'professional'  # default
                assert analysis['industry'] == 'general'  # default
                assert analysis['target_audience'] == ''  # empty but present


class TestOrchestratorCoordination:
    """Test orchestrator coordination with echo agents."""

    def test_echo_agent_basic(self):
        """Test that echo agent works as expected."""
        echo = EchoAgent('test_echo')

        result = echo.execute({'test': 'data'})

        assert result['agent_name'] == 'test_echo'
        assert result['input_received'] == {'test': 'data'}
        assert result['call_count'] == 1
        assert result['status'] == 'success'
        assert echo.last_input == {'test': 'data'}

    def test_echo_agent_multiple_calls(self):
        """Test echo agent tracks multiple calls."""
        echo = EchoAgent('test_echo')

        echo.execute({'call': 1})
        echo.execute({'call': 2})
        result = echo.execute({'call': 3})

        assert result['call_count'] == 3
        assert echo.last_input == {'call': 3}

    def test_orchestrator_with_echo_agents(self):
        """Test orchestrator coordination with multiple echo agents."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                # Create and add echo agents
                research_echo = EchoAgent('research')
                generator_echo = EchoAgent('generator')
                validator_echo = EchoAgent('validator')

                orchestrator.add_sub_agent(research_echo)
                orchestrator.add_sub_agent(generator_echo)
                orchestrator.add_sub_agent(validator_echo)

                # Verify agents were added
                assert len(orchestrator.sub_agents) == 3

                # Test that each agent can be called independently
                for agent in orchestrator.sub_agents:
                    result = agent.execute({'test': agent.name})
                    assert result['status'] == 'success'
                    assert result['agent_name'] == agent.name
                    assert agent.call_count == 1


class TestOrchestratorWorkflow:
    """Test orchestrator workflow execution."""

    def test_workflow_result_structure(self):
        """Test that workflow returns expected structure."""
        from unittest.mock import patch

        with patch('google.cloud.aiplatform.init'):
            with patch('google.cloud.logging.Client'):
                orchestrator = BrandStudioOrchestrator(
                    project_id='test-project',
                    enable_cloud_logging=False
                )

                user_brief = {
                    'product_description': 'Test product'
                }

                result = orchestrator.coordinate_workflow(user_brief)

                # Check result structure
                assert 'status' in result
                assert 'user_brief' in result
                assert 'workflow_stages' in result
                assert 'brand_names' in result
                assert 'iteration' in result
                assert 'start_time' in result

                # Workflow should complete (even though placeholder agents return empty results)
                assert result['status'] in ['completed', 'failed', 'validation_failed']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
