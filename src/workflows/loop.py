"""
Loop refinement workflow pattern.

Enables iterative improvement with controlled iteration limits.
Use cases:
- Regenerate brand names if validation fails (max 3 iterations)
- Retry operations with feedback incorporation
- Iterative refinement until success criteria met
"""

import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger('brand_studio.workflows.loop')


class LoopWorkflow:
    """
    Loop refinement workflow executor for iterative improvement.

    Executes a callable repeatedly until either:
    - Success criteria is met (validation_func returns True)
    - Maximum iterations reached
    - Fatal error occurs

    Example:
        >>> workflow = LoopWorkflow(
        ...     callable_func=generator.generate,
        ...     validation_func=lambda r: r['validation_passed'],
        ...     max_iterations=3
        ... )
        >>> result = workflow.execute({'initial_arg': 'value'})
        >>> if result['success']:
        ...     print(f"Succeeded after {result['iteration']} iterations")
    """

    def __init__(
        self,
        callable_func: Callable,
        validation_func: Callable[[Any], bool],
        max_iterations: int = 3,
        refinement_func: Optional[Callable[[Any, int], Dict[str, Any]]] = None
    ):
        """
        Initialize loop refinement workflow.

        Args:
            callable_func: Function to execute in each iteration
            validation_func: Function that validates output (returns True if criteria met)
            max_iterations: Maximum number of iterations before giving up (default: 3)
            refinement_func: Optional function to refine kwargs based on previous result
                             Signature: (previous_result, iteration) -> updated_kwargs
        """
        self.callable_func = callable_func
        self.validation_func = validation_func
        self.max_iterations = max_iterations
        self.refinement_func = refinement_func

        logger.info(
            f"Initialized LoopWorkflow with max {max_iterations} iterations"
        )

    def execute(self, initial_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute loop workflow until success or max iterations.

        Args:
            initial_kwargs: Initial keyword arguments for callable_func

        Returns:
            Dictionary with:
            - success: bool - Whether validation passed
            - result: Any - Final result from successful iteration or last attempt
            - iteration: int - Number of iterations executed
            - validation_passed: bool - Whether validation criteria met
            - all_results: List[Any] - Results from all iterations
            - total_duration: float - Total execution time in seconds
            - error: Optional[str] - Error message if failed

        Example:
            >>> result = workflow.execute({'count': 20, 'style': 'professional'})
            >>> if result['success']:
            ...     final_names = result['result']
        """
        start_time = datetime.utcnow()
        kwargs = initial_kwargs or {}
        all_results = []
        iteration = 0
        last_result = None
        validation_passed = False
        error_message = None

        logger.info("Starting loop workflow execution")

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Loop iteration {iteration}/{self.max_iterations}")

            try:
                # Execute callable
                result = self.callable_func(**kwargs)
                all_results.append(result)
                last_result = result

                # Validate result
                validation_passed = self.validation_func(result)

                if validation_passed:
                    logger.info(
                        f"Validation passed on iteration {iteration}. "
                        "Loop completed successfully."
                    )
                    break
                else:
                    logger.warning(
                        f"Validation failed on iteration {iteration}. "
                        f"{'Retrying...' if iteration < self.max_iterations else 'Max iterations reached.'}"
                    )

                    # Refine kwargs for next iteration if refinement function provided
                    if self.refinement_func and iteration < self.max_iterations:
                        try:
                            refinement_kwargs = self.refinement_func(result, iteration)
                            kwargs.update(refinement_kwargs)
                            logger.debug(
                                f"Refined kwargs for iteration {iteration + 1}: "
                                f"{list(refinement_kwargs.keys())}"
                            )
                        except Exception as e:
                            logger.error(f"Refinement function failed: {e}")
                            # Continue with existing kwargs

            except Exception as e:
                logger.error(
                    f"Error in iteration {iteration}: {e}",
                    exc_info=True
                )
                error_message = str(e)
                # Don't break - try remaining iterations unless this is a fatal error
                if "fatal" in str(e).lower():
                    logger.error("Fatal error detected. Stopping loop.")
                    break

        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()

        success = validation_passed

        logger.info(
            f"Loop workflow {'completed successfully' if success else 'failed'}. "
            f"Iterations: {iteration}/{self.max_iterations}. "
            f"Duration: {total_duration:.2f}s"
        )

        return {
            'success': success,
            'result': last_result,
            'iteration': iteration,
            'validation_passed': validation_passed,
            'all_results': all_results,
            'total_duration': total_duration,
            'max_iterations_reached': iteration >= self.max_iterations and not success,
            'error': error_message
        }


class RetryWorkflow:
    """
    Simple retry workflow for operations that may fail temporarily.

    Retries a callable with exponential backoff until success or max retries.

    Example:
        >>> workflow = RetryWorkflow(
        ...     callable_func=api_client.call,
        ...     max_retries=3,
        ...     backoff_factor=2.0
        ... )
        >>> result = workflow.execute({'endpoint': '/data'})
    """

    def __init__(
        self,
        callable_func: Callable,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        initial_delay: float = 1.0
    ):
        """
        Initialize retry workflow.

        Args:
            callable_func: Function to retry
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for delay between retries
            initial_delay: Initial delay in seconds before first retry
        """
        self.callable_func = callable_func
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay

        logger.info(
            f"Initialized RetryWorkflow with {max_retries} retries, "
            f"{backoff_factor}x backoff"
        )

    def execute(self, kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute with retries.

        Args:
            kwargs: Keyword arguments for callable

        Returns:
            Dictionary with success status and result or error
        """
        import time

        kwargs = kwargs or {}
        attempt = 0
        delay = self.initial_delay
        last_error = None

        while attempt <= self.max_retries:
            attempt += 1

            try:
                logger.info(f"Attempt {attempt}/{self.max_retries + 1}")
                result = self.callable_func(**kwargs)
                logger.info(f"Succeeded on attempt {attempt}")
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt,
                    'error': None
                }

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed: {e}")

                if attempt <= self.max_retries:
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= self.backoff_factor

        logger.error(f"All {self.max_retries + 1} attempts failed")
        return {
            'success': False,
            'result': None,
            'attempts': attempt,
            'error': last_error
        }


# Convenience function for simple loop execution
def execute_loop(
    callable_func: Callable,
    validation_func: Callable[[Any], bool],
    initial_kwargs: Optional[Dict[str, Any]] = None,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Convenience function to execute loop workflow.

    Args:
        callable_func: Function to execute
        validation_func: Validation function
        initial_kwargs: Initial arguments
        max_iterations: Maximum iterations

    Returns:
        Workflow execution results

    Example:
        >>> result = execute_loop(
        ...     callable_func=generator.generate,
        ...     validation_func=lambda r: len(r) >= 10,
        ...     initial_kwargs={'style': 'tech'},
        ...     max_iterations=3
        ... )
    """
    workflow = LoopWorkflow(
        callable_func=callable_func,
        validation_func=validation_func,
        max_iterations=max_iterations
    )
    return workflow.execute(initial_kwargs)
