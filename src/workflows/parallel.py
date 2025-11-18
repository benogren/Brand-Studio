"""
Parallel workflow execution pattern.

Enables concurrent execution of independent operations to improve performance.
Use cases:
- Research + Initial name generation can happen simultaneously
- Domain + Trademark validation can run in parallel
"""

import logging
import asyncio
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger('brand_studio.workflows.parallel')


class ParallelWorkflow:
    """
    Parallel workflow executor for concurrent operations.

    Executes multiple independent operations concurrently using either:
    - ThreadPoolExecutor for I/O-bound tasks (API calls, database queries)
    - asyncio for async operations (if needed)

    Example:
        >>> workflow = ParallelWorkflow(max_workers=3)
        >>> results = workflow.execute([
        ...     ('research', research_agent.execute, {'query': 'healthcare'}),
        ...     ('generation', name_generator.generate, {'count': 20})
        ... ])
        >>> research_data = results['research']
        >>> names = results['generation']
    """

    def __init__(self, max_workers: int = 5, timeout: Optional[float] = 300.0):
        """
        Initialize parallel workflow executor.

        Args:
            max_workers: Maximum number of concurrent workers
            timeout: Maximum time in seconds to wait for all tasks (default: 5 minutes)
        """
        self.max_workers = max_workers
        self.timeout = timeout
        logger.info(f"Initialized ParallelWorkflow with {max_workers} workers, {timeout}s timeout")

    def execute(
        self,
        tasks: List[tuple[str, Callable, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in parallel.

        Args:
            tasks: List of (task_name, callable, kwargs) tuples
                - task_name: Identifier for the task (used as key in results)
                - callable: Function to execute
                - kwargs: Keyword arguments to pass to the callable

        Returns:
            Dictionary mapping task_name to result

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If any task fails (will include task_name in error)

        Example:
            >>> tasks = [
            ...     ('research', agent.research, {'industry': 'tech'}),
            ...     ('validation', checker.validate, {'names': ['Brand1']})
            ... ]
            >>> results = workflow.execute(tasks)
            >>> print(results['research'])
        """
        start_time = datetime.utcnow()
        results = {}
        errors = {}

        logger.info(f"Starting parallel execution of {len(tasks)} tasks")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task_name, callable_func, kwargs in tasks:
                future = executor.submit(self._execute_task, task_name, callable_func, kwargs)
                future_to_task[future] = task_name

            # Collect results as they complete
            try:
                for future in as_completed(future_to_task, timeout=self.timeout):
                    task_name = future_to_task[future]
                    try:
                        result = future.result()
                        results[task_name] = result
                        logger.info(f"Task '{task_name}' completed successfully")
                    except Exception as e:
                        error_msg = f"Task '{task_name}' failed: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        errors[task_name] = str(e)

            except TimeoutError:
                logger.error(f"Parallel execution timed out after {self.timeout}s")
                # Cancel remaining tasks
                for future in future_to_task:
                    future.cancel()
                raise TimeoutError(
                    f"Parallel execution exceeded timeout of {self.timeout}s. "
                    f"Completed: {len(results)}/{len(tasks)}"
                )

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Check if any tasks failed
        if errors:
            error_summary = "; ".join([f"{name}: {err}" for name, err in errors.items()])
            logger.error(
                f"Parallel execution completed with errors in {duration:.2f}s. "
                f"Successful: {len(results)}/{len(tasks)}. Errors: {error_summary}"
            )
            raise Exception(
                f"Parallel execution had {len(errors)} failures: {error_summary}"
            )

        logger.info(
            f"Parallel execution completed successfully in {duration:.2f}s. "
            f"All {len(tasks)} tasks succeeded."
        )

        return results

    def _execute_task(
        self,
        task_name: str,
        callable_func: Callable,
        kwargs: Dict[str, Any]
    ) -> Any:
        """
        Execute a single task with error handling.

        Args:
            task_name: Name of the task
            callable_func: Function to execute
            kwargs: Keyword arguments

        Returns:
            Task result

        Raises:
            Exception: If task execution fails
        """
        try:
            logger.debug(f"Executing task '{task_name}'")
            result = callable_func(**kwargs)
            logger.debug(f"Task '{task_name}' returned result")
            return result
        except Exception as e:
            logger.error(f"Task '{task_name}' raised exception: {e}")
            raise

    def execute_batch(
        self,
        batch_tasks: List[List[tuple[str, Callable, Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple batches of parallel tasks sequentially.

        Each batch runs in parallel, but batches execute sequentially.
        Useful when later batches depend on results from earlier batches.

        Args:
            batch_tasks: List of task batches, where each batch is a list of tasks

        Returns:
            List of result dictionaries, one per batch

        Example:
            >>> batch1 = [('research', research_fn, {}), ('init', init_fn, {})]
            >>> batch2 = [('validate1', val_fn, {}), ('validate2', val_fn, {})]
            >>> results = workflow.execute_batch([batch1, batch2])
            >>> research_result = results[0]['research']
            >>> validation_results = results[1]
        """
        logger.info(f"Executing {len(batch_tasks)} batches sequentially")
        batch_results = []

        for batch_idx, tasks in enumerate(batch_tasks):
            logger.info(f"Executing batch {batch_idx + 1}/{len(batch_tasks)} with {len(tasks)} tasks")
            results = self.execute(tasks)
            batch_results.append(results)

        logger.info(f"All {len(batch_tasks)} batches completed")
        return batch_results


# Convenience function for simple parallel execution
def execute_parallel(
    tasks: List[tuple[str, Callable, Dict[str, Any]]],
    max_workers: int = 5,
    timeout: float = 300.0
) -> Dict[str, Any]:
    """
    Convenience function to execute tasks in parallel.

    Args:
        tasks: List of (task_name, callable, kwargs) tuples
        max_workers: Maximum concurrent workers
        timeout: Timeout in seconds

    Returns:
        Dictionary mapping task names to results

    Example:
        >>> results = execute_parallel([
        ...     ('task1', func1, {'arg': 'value'}),
        ...     ('task2', func2, {'arg': 'value'})
        ... ])
    """
    workflow = ParallelWorkflow(max_workers=max_workers, timeout=timeout)
    return workflow.execute(tasks)
