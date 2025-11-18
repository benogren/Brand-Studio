"""
Sequential workflow execution pattern.

Enables ordered execution of dependent operations in a pipeline.
Use cases:
- Generation → Validation → SEO → Story (must execute in order)
- Ensure validation passes before proceeding to content generation
"""

import logging
from typing import List, Dict, Any, Callable, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger('brand_studio.workflows.sequential')


class StageStatus(Enum):
    """Status of a workflow stage."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStage:
    """
    Represents a single stage in a sequential workflow.

    Attributes:
        name: Stage identifier
        callable_func: Function to execute
        kwargs: Arguments to pass to function
        status: Current status
        result: Result from execution (if completed)
        error: Error message (if failed)
        start_time: Execution start time
        end_time: Execution end time
    """

    def __init__(
        self,
        name: str,
        callable_func: Callable,
        kwargs: Optional[Dict[str, Any]] = None,
        validation_func: Optional[Callable[[Any], bool]] = None,
        required: bool = True
    ):
        """
        Initialize workflow stage.

        Args:
            name: Stage identifier
            callable_func: Function to execute
            kwargs: Keyword arguments for function
            validation_func: Optional function to validate stage output (returns bool)
            required: Whether this stage is required (if False, failure skips stage)
        """
        self.name = name
        self.callable_func = callable_func
        self.kwargs = kwargs or {}
        self.validation_func = validation_func
        self.required = required
        self.status = StageStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def execute(self) -> Tuple[bool, Any]:
        """
        Execute the stage.

        Returns:
            Tuple of (success: bool, result: Any)
        """
        self.status = StageStatus.IN_PROGRESS
        self.start_time = datetime.utcnow()

        try:
            logger.info(f"Executing stage '{self.name}'")
            self.result = self.callable_func(**self.kwargs)
            self.end_time = datetime.utcnow()

            # Validate output if validation function provided
            if self.validation_func:
                if not self.validation_func(self.result):
                    self.status = StageStatus.FAILED
                    self.error = "Validation function returned False"
                    logger.error(f"Stage '{self.name}' validation failed")
                    return False, self.result

            self.status = StageStatus.COMPLETED
            duration = (self.end_time - self.start_time).total_seconds()
            logger.info(f"Stage '{self.name}' completed successfully in {duration:.2f}s")
            return True, self.result

        except Exception as e:
            self.end_time = datetime.utcnow()
            self.status = StageStatus.FAILED
            self.error = str(e)
            logger.error(f"Stage '{self.name}' failed: {e}", exc_info=True)
            return False, None

    def skip(self, reason: str = ""):
        """Mark stage as skipped."""
        self.status = StageStatus.SKIPPED
        self.error = reason
        logger.info(f"Stage '{self.name}' skipped: {reason}")


class SequentialWorkflow:
    """
    Sequential workflow executor for ordered pipeline execution.

    Executes stages in order, with support for:
    - Conditional execution based on previous stage results
    - Validation of stage outputs
    - Error handling and recovery
    - Stage skipping for non-required stages

    Example:
        >>> workflow = SequentialWorkflow([
        ...     WorkflowStage('generate', generator.generate, {'count': 20}),
        ...     WorkflowStage('validate', validator.validate, validation_func=lambda r: r['passed']),
        ...     WorkflowStage('optimize', optimizer.optimize)
        ... ])
        >>> results = workflow.execute()
        >>> if results['success']:
        ...     print(results['stage_results']['generate'])
    """

    def __init__(
        self,
        stages: List[WorkflowStage],
        stop_on_failure: bool = True,
        pass_results: bool = False
    ):
        """
        Initialize sequential workflow.

        Args:
            stages: List of WorkflowStage objects to execute in order
            stop_on_failure: Stop execution if a required stage fails (default: True)
            pass_results: Pass results from previous stages to next stage as 'previous_results' kwarg
        """
        self.stages = stages
        self.stop_on_failure = stop_on_failure
        self.pass_results = pass_results
        logger.info(
            f"Initialized SequentialWorkflow with {len(stages)} stages, "
            f"stop_on_failure={stop_on_failure}"
        )

    def execute(self) -> Dict[str, Any]:
        """
        Execute all stages in sequence.

        Returns:
            Dictionary with:
            - success: bool - Whether all required stages completed successfully
            - stage_results: Dict[str, Any] - Results from each stage
            - stage_statuses: Dict[str, str] - Status of each stage
            - failed_stage: Optional[str] - Name of failed stage (if any)
            - error: Optional[str] - Error message (if failed)
            - total_duration: float - Total execution time in seconds

        Example:
            >>> workflow = SequentialWorkflow(stages)
            >>> result = workflow.execute()
            >>> if result['success']:
            ...     names = result['stage_results']['generate']
            ...     validation = result['stage_results']['validate']
        """
        start_time = datetime.utcnow()
        stage_results = {}
        stage_statuses = {}
        failed_stage = None
        error_message = None

        logger.info(f"Starting sequential workflow with {len(self.stages)} stages")

        for stage in self.stages:
            # Pass previous results if enabled
            if self.pass_results and stage_results:
                stage.kwargs['previous_results'] = stage_results

            # Execute stage
            success, result = stage.execute()

            # Store results
            stage_results[stage.name] = result
            stage_statuses[stage.name] = stage.status.value

            # Handle failure
            if not success:
                if stage.required and self.stop_on_failure:
                    failed_stage = stage.name
                    error_message = stage.error
                    logger.error(
                        f"Required stage '{stage.name}' failed. Stopping workflow. "
                        f"Error: {stage.error}"
                    )
                    break
                elif not stage.required:
                    logger.warning(
                        f"Optional stage '{stage.name}' failed. Continuing workflow. "
                        f"Error: {stage.error}"
                    )
                    stage.skip(f"Failed (optional): {stage.error}")
                    stage_statuses[stage.name] = stage.status.value

        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()

        # Determine overall success
        success = failed_stage is None

        # Count completed stages
        completed_count = sum(
            1 for stage in self.stages
            if stage.status == StageStatus.COMPLETED
        )

        logger.info(
            f"Sequential workflow {'completed' if success else 'failed'}. "
            f"Duration: {total_duration:.2f}s. "
            f"Completed: {completed_count}/{len(self.stages)} stages."
        )

        return {
            'success': success,
            'stage_results': stage_results,
            'stage_statuses': stage_statuses,
            'failed_stage': failed_stage,
            'error': error_message,
            'total_duration': total_duration,
            'completed_stages': completed_count,
            'total_stages': len(self.stages)
        }

    def add_stage(self, stage: WorkflowStage) -> None:
        """Add a stage to the end of the workflow."""
        self.stages.append(stage)
        logger.debug(f"Added stage '{stage.name}' to workflow")

    def insert_stage(self, index: int, stage: WorkflowStage) -> None:
        """Insert a stage at a specific position."""
        self.stages.insert(index, stage)
        logger.debug(f"Inserted stage '{stage.name}' at position {index}")

    def get_stage_by_name(self, name: str) -> Optional[WorkflowStage]:
        """Get a stage by its name."""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None


# Convenience function for simple sequential execution
def execute_sequential(
    stages: List[Tuple[str, Callable, Dict[str, Any]]],
    stop_on_failure: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to execute stages sequentially.

    Args:
        stages: List of (name, callable, kwargs) tuples
        stop_on_failure: Stop if any stage fails

    Returns:
        Workflow execution results

    Example:
        >>> results = execute_sequential([
        ...     ('stage1', func1, {'arg': 'value'}),
        ...     ('stage2', func2, {'arg': 'value'})
        ... ])
    """
    workflow_stages = [
        WorkflowStage(name, func, kwargs)
        for name, func, kwargs in stages
    ]
    workflow = SequentialWorkflow(workflow_stages, stop_on_failure=stop_on_failure)
    return workflow.execute()
