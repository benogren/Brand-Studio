"""
Cloud Logging integration for Brand Studio agents.

This module provides:
- Cloud Logging client setup and configuration
- LoggingPlugin for ADK agent integration
- Structured logging for agent actions and metrics
- Error logging with stack traces and context
- Performance metrics tracking
"""

import logging
import time
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from functools import wraps

try:
    from google.cloud import logging as cloud_logging
    from google.cloud.logging_v2.handlers import CloudLoggingHandler
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False
    print("Warning: google-cloud-logging not available. Using local logging only.")


class BrandStudioLogger:
    """
    Centralized logging for Brand Studio agents.

    Provides structured logging with Cloud Logging integration,
    fallback to local logging when Cloud Logging is unavailable.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        log_name: str = "brand-studio-agents",
        enable_cloud_logging: bool = True
    ):
        """
        Initialize the logger.

        Args:
            project_id: Google Cloud project ID (auto-detected if not provided)
            log_name: Name for the Cloud Logging log
            enable_cloud_logging: Whether to enable Cloud Logging (falls back to local if unavailable)
        """
        self.project_id = project_id
        self.log_name = log_name
        self.enable_cloud_logging = enable_cloud_logging and CLOUD_LOGGING_AVAILABLE

        # Setup Python standard logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        # Setup handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers (Cloud + Console)."""
        # Remove existing handlers
        self.logger.handlers.clear()

        # Add console handler (always)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Add Cloud Logging handler if enabled
        if self.enable_cloud_logging:
            try:
                client = cloud_logging.Client(project=self.project_id)
                cloud_handler = CloudLoggingHandler(client, name=self.log_name)
                cloud_handler.setLevel(logging.INFO)
                self.logger.addHandler(cloud_handler)
                self.logger.info("Cloud Logging enabled successfully")
            except Exception as e:
                self.logger.warning(f"Failed to setup Cloud Logging: {e}. Using local logging only.")
                self.enable_cloud_logging = False

    def log_agent_action(
        self,
        agent_name: str,
        action_type: str,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a structured agent action.

        Args:
            agent_name: Name of the agent (e.g., "orchestrator", "name_generator")
            action_type: Type of action (e.g., "generate_names", "validate_domains")
            inputs: Input parameters for the action
            outputs: Output/results from the action
            duration_ms: Time taken in milliseconds
            session_id: Session identifier for correlation
            metadata: Additional metadata
        """
        log_data = {
            "agent_name": agent_name,
            "action_type": action_type,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
        }

        if inputs:
            log_data["inputs"] = inputs
        if outputs:
            log_data["outputs"] = outputs
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
        if metadata:
            log_data["metadata"] = metadata

        self.logger.info(f"Agent Action: {agent_name}.{action_type}", extra=log_data)

    def log_error(
        self,
        agent_name: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """
        Log an error with full stack trace and context.

        Args:
            agent_name: Name of the agent where error occurred
            error: The exception object
            context: Additional context about the error
            session_id: Session identifier for correlation
        """
        error_data = {
            "agent_name": agent_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
        }

        if context:
            error_data["context"] = context

        self.logger.error(
            f"Error in {agent_name}: {type(error).__name__}: {str(error)}",
            extra=error_data,
            exc_info=True
        )

    def log_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        labels: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ):
        """
        Log a performance metric.

        Args:
            metric_name: Name of the metric (e.g., "response_time", "names_generated")
            value: Metric value
            unit: Unit of measurement (e.g., "ms", "count")
            labels: Additional labels for filtering
            session_id: Session identifier for correlation
        """
        metric_data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
        }

        if labels:
            metric_data["labels"] = labels

        self.logger.info(f"Metric: {metric_name}={value}{unit}", extra=metric_data)

    def info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log an error message."""
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, extra=kwargs)


# Global logger instance
_global_logger: Optional[BrandStudioLogger] = None


def get_logger(
    project_id: Optional[str] = None,
    enable_cloud_logging: bool = True
) -> BrandStudioLogger:
    """
    Get or create the global logger instance.

    Args:
        project_id: Google Cloud project ID
        enable_cloud_logging: Whether to enable Cloud Logging

    Returns:
        BrandStudioLogger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = BrandStudioLogger(
            project_id=project_id,
            enable_cloud_logging=enable_cloud_logging
        )

    return _global_logger


def track_performance(agent_name: str, action_type: str):
    """
    Decorator to track performance of agent methods.

    Usage:
        @track_performance("name_generator", "generate")
        def generate_names(self, brief: str):
            ...

    Args:
        agent_name: Name of the agent
        action_type: Type of action being performed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.log_agent_action(
                    agent_name=agent_name,
                    action_type=action_type,
                    duration_ms=duration_ms,
                    metadata={"status": "success"}
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.log_error(
                    agent_name=agent_name,
                    error=e,
                    context={
                        "action_type": action_type,
                        "duration_ms": duration_ms
                    }
                )
                raise

        return wrapper
    return decorator


# ADK LoggingPlugin integration (if ADK is available)
try:
    from google.genai.adk.plugins import LoggingPlugin as ADKLoggingPlugin

    class BrandStudioLoggingPlugin(ADKLoggingPlugin):
        """
        Custom LoggingPlugin for ADK agents.

        Integrates with BrandStudioLogger for consistent logging.
        """

        def __init__(self, agent_name: str, session_id: Optional[str] = None):
            """
            Initialize the logging plugin.

            Args:
                agent_name: Name of the agent using this plugin
                session_id: Session identifier for correlation
            """
            super().__init__()
            self.agent_name = agent_name
            self.session_id = session_id
            self.logger = get_logger()

        def on_agent_start(self, inputs: Dict[str, Any]):
            """Called when agent starts processing."""
            self.logger.log_agent_action(
                agent_name=self.agent_name,
                action_type="start",
                inputs=inputs,
                session_id=self.session_id
            )

        def on_agent_end(self, outputs: Dict[str, Any], duration_ms: float):
            """Called when agent completes processing."""
            self.logger.log_agent_action(
                agent_name=self.agent_name,
                action_type="complete",
                outputs=outputs,
                duration_ms=duration_ms,
                session_id=self.session_id
            )

        def on_agent_error(self, error: Exception):
            """Called when agent encounters an error."""
            self.logger.log_error(
                agent_name=self.agent_name,
                error=error,
                session_id=self.session_id
            )

    LOGGING_PLUGIN_AVAILABLE = True

except ImportError:
    LOGGING_PLUGIN_AVAILABLE = False
    BrandStudioLoggingPlugin = None
    print("Warning: ADK LoggingPlugin not available. Plugin integration disabled.")


__all__ = [
    "BrandStudioLogger",
    "get_logger",
    "track_performance",
    "BrandStudioLoggingPlugin",
    "CLOUD_LOGGING_AVAILABLE",
    "LOGGING_PLUGIN_AVAILABLE",
]
