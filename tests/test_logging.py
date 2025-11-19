"""
Test suite for Brand Studio logging infrastructure.

Tests Cloud Logging integration, structured logging, error logging,
and performance metrics tracking.
"""

import unittest
import time
from datetime import datetime
from src.infrastructure.logging import (
    BrandStudioLogger,
    get_logger,
    track_performance,
    CLOUD_LOGGING_AVAILABLE
)


class TestBrandStudioLogger(unittest.TestCase):
    """Test BrandStudioLogger functionality."""

    def setUp(self):
        """Set up test logger."""
        # Disable cloud logging for unit tests (use local only)
        self.logger = BrandStudioLogger(
            project_id="test-project",
            log_name="test-brand-studio",
            enable_cloud_logging=False
        )

    def test_logger_initialization(self):
        """Test logger initializes correctly."""
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.log_name, "test-brand-studio")
        self.assertFalse(self.logger.enable_cloud_logging)

    def test_log_agent_action(self):
        """Test structured agent action logging."""
        try:
            self.logger.log_agent_action(
                agent_name="test_agent",
                action_type="test_action",
                inputs={"param1": "value1"},
                outputs={"result": "success"},
                duration_ms=123.45,
                session_id="test-session-123",
                metadata={"test": "data"}
            )
            # If no exception, test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_agent_action raised exception: {e}")

    def test_log_error(self):
        """Test error logging with stack trace."""
        try:
            # Create a test exception
            try:
                raise ValueError("Test error for logging")
            except ValueError as e:
                self.logger.log_error(
                    agent_name="test_agent",
                    error=e,
                    context={"test_context": "value"},
                    session_id="test-session-123"
                )
            # If no exception during logging, test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_error raised exception: {e}")

    def test_log_metric(self):
        """Test performance metric logging."""
        try:
            self.logger.log_metric(
                metric_name="test_metric",
                value=42.5,
                unit="ms",
                labels={"env": "test"},
                session_id="test-session-123"
            )
            # If no exception, test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_metric raised exception: {e}")

    def test_standard_logging_methods(self):
        """Test standard logging methods (info, warning, error, debug)."""
        try:
            self.logger.info("Test info message", test_field="value")
            self.logger.warning("Test warning message")
            self.logger.error("Test error message")
            self.logger.debug("Test debug message")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Standard logging methods raised exception: {e}")


class TestGetLogger(unittest.TestCase):
    """Test get_logger singleton functionality."""

    def test_get_logger_returns_instance(self):
        """Test get_logger returns a BrandStudioLogger instance."""
        logger = get_logger(enable_cloud_logging=False)
        self.assertIsInstance(logger, BrandStudioLogger)

    def test_get_logger_singleton(self):
        """Test get_logger returns the same instance."""
        logger1 = get_logger(enable_cloud_logging=False)
        logger2 = get_logger(enable_cloud_logging=False)
        self.assertIs(logger1, logger2)


class TestTrackPerformance(unittest.TestCase):
    """Test @track_performance decorator."""

    def setUp(self):
        """Set up test logger."""
        # Ensure logger is initialized without cloud logging
        self.logger = get_logger(enable_cloud_logging=False)

    def test_decorator_tracks_success(self):
        """Test decorator tracks successful function execution."""
        @track_performance("test_agent", "test_action")
        def test_function(x, y):
            time.sleep(0.1)  # Simulate work
            return x + y

        result = test_function(2, 3)
        self.assertEqual(result, 5)

    def test_decorator_tracks_error(self):
        """Test decorator tracks errors and re-raises."""
        @track_performance("test_agent", "test_action")
        def failing_function():
            raise ValueError("Intentional test error")

        with self.assertRaises(ValueError):
            failing_function()


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete logging scenarios."""

    def setUp(self):
        """Set up test logger."""
        self.logger = get_logger(enable_cloud_logging=False)

    def test_complete_workflow_logging(self):
        """Test logging a complete agent workflow."""
        session_id = f"test-session-{datetime.utcnow().isoformat()}"

        # 1. Log agent initialization
        self.logger.log_agent_action(
            agent_name="orchestrator",
            action_type="initialize",
            metadata={"version": "1.0"},
            session_id=session_id
        )

        # 2. Log name generation
        start_time = time.time()
        # Simulate work
        time.sleep(0.05)
        duration_ms = (time.time() - start_time) * 1000

        self.logger.log_agent_action(
            agent_name="name_generator",
            action_type="generate",
            inputs={"industry": "tech"},
            outputs={"num_names": 20},
            duration_ms=duration_ms,
            session_id=session_id
        )

        # 3. Log validation
        self.logger.log_agent_action(
            agent_name="validation_agent",
            action_type="validate",
            inputs={"brand_name": "TestBrand"},
            outputs={"domain_available": True, "trademark_risk": "low"},
            duration_ms=150.5,
            session_id=session_id
        )

        # 4. Log metrics
        self.logger.log_metric(
            metric_name="workflow_duration",
            value=500.0,
            unit="ms",
            session_id=session_id
        )

        # If no exceptions, test passes
        self.assertTrue(True)

    def test_error_scenario_logging(self):
        """Test logging during error scenarios."""
        session_id = f"test-error-session-{datetime.utcnow().isoformat()}"

        try:
            # Simulate an error during name generation
            raise RuntimeError("Failed to connect to RAG database")
        except RuntimeError as e:
            self.logger.log_error(
                agent_name="name_generator",
                error=e,
                context={
                    "action": "rag_retrieval",
                    "rag_endpoint": "test-endpoint"
                },
                session_id=session_id
            )

        # If error was logged without exceptions, test passes
        self.assertTrue(True)


def run_manual_logging_test():
    """
    Manual test to verify logs are written correctly.
    Run this to see actual log output.
    """
    print("\n" + "="*60)
    print("MANUAL LOGGING TEST - Verify Log Output")
    print("="*60 + "\n")

    logger = get_logger(enable_cloud_logging=False)
    session_id = f"manual-test-{datetime.utcnow().isoformat()}"

    print("1. Testing agent action logging...")
    logger.log_agent_action(
        agent_name="orchestrator",
        action_type="test_manual",
        inputs={"test": "input"},
        outputs={"test": "output"},
        duration_ms=123.45,
        session_id=session_id
    )

    print("2. Testing error logging...")
    try:
        raise ValueError("Intentional test error")
    except ValueError as e:
        logger.log_error(
            agent_name="test_agent",
            error=e,
            context={"manual_test": True},
            session_id=session_id
        )

    print("3. Testing metric logging...")
    logger.log_metric(
        metric_name="test_metric",
        value=99.9,
        unit="ms",
        labels={"type": "manual_test"},
        session_id=session_id
    )

    print("4. Testing performance decorator...")
    @track_performance("test_agent", "decorated_action")
    def test_decorated():
        time.sleep(0.1)
        return "success"

    result = test_decorated()
    print(f"   Decorated function returned: {result}")

    print("\n" + "="*60)
    print("MANUAL TEST COMPLETE")
    print("Check console output above for log messages")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60 + "\n")
    unittest.main(argv=[''], verbosity=2, exit=False)

    # Run manual test
    run_manual_logging_test()
