"""
Workflow pattern implementations for multi-agent orchestration.

This module contains:
- Parallel: Execute agents in parallel (research + name generation)
- Sequential: Execute agents in sequence (generation → validation → SEO → story)
- Loop: Loop refinement with max iterations (regenerate if validation fails)
"""

from src.workflows.parallel import ParallelWorkflow, execute_parallel
from src.workflows.sequential import (
    SequentialWorkflow,
    WorkflowStage,
    StageStatus,
    execute_sequential
)
from src.workflows.loop import LoopWorkflow, RetryWorkflow, execute_loop

__all__ = [
    # Parallel workflow
    'ParallelWorkflow',
    'execute_parallel',
    # Sequential workflow
    'SequentialWorkflow',
    'WorkflowStage',
    'StageStatus',
    'execute_sequential',
    # Loop workflow
    'LoopWorkflow',
    'RetryWorkflow',
    'execute_loop',
]
