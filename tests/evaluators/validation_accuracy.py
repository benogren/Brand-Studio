"""
Validation Accuracy Evaluator for AI Brand Studio.

Evaluates the accuracy of domain availability and trademark checking.
"""

from typing import Dict, Any, List


class ValidationAccuracyEvaluator:
    """
    Evaluates validation accuracy for domain and trademark checks.

    Checks:
    - Domain check success rate (no failures/errors)
    - Trademark check success rate
    - Risk assessment consistency
    - Validation completeness
    """

    def __init__(self, min_success_rate: float = 0.95):
        """
        Initialize evaluator.

        Args:
            min_success_rate: Minimum acceptable success rate (default: 0.95)
        """
        self.min_success_rate = min_success_rate

    def evaluate(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate validation accuracy.

        Args:
            validation_results: Results from validation agent containing:
                - domain_availability: Dict mapping names to domain status
                - trademark_results: Dict mapping names to trademark info
                - validation_errors: List of any errors encountered

        Returns:
            Dictionary with:
            - domain_check_success_rate: Success rate for domain checks
            - trademark_check_success_rate: Success rate for trademark checks
            - overall_accuracy: Combined accuracy score
            - validation_completeness: % of names fully validated
            - passed: Whether evaluation meets minimum standards
        """
        if not validation_results:
            return {
                'domain_check_success_rate': 0.0,
                'trademark_check_success_rate': 0.0,
                'overall_accuracy': 0.0,
                'validation_completeness': 0.0,
                'passed': False,
                'error': 'No validation results provided'
            }

        domain_availability = validation_results.get('domain_availability', {})
        trademark_results = validation_results.get('trademark_results', {})
        validation_errors = validation_results.get('validation_errors', [])

        # Calculate domain check success rate
        domain_check_success_rate = self._calculate_domain_success_rate(
            domain_availability
        )

        # Calculate trademark check success rate
        trademark_check_success_rate = self._calculate_trademark_success_rate(
            trademark_results
        )

        # Calculate overall accuracy
        overall_accuracy = (
            domain_check_success_rate + trademark_check_success_rate
        ) / 2

        # Calculate validation completeness
        total_names = max(len(domain_availability), len(trademark_results))
        if total_names > 0:
            fully_validated = sum(
                1 for name in domain_availability.keys()
                if name in trademark_results
            )
            validation_completeness = fully_validated / total_names
        else:
            validation_completeness = 0.0

        # Determine if passed
        passed = (
            domain_check_success_rate >= self.min_success_rate and
            trademark_check_success_rate >= self.min_success_rate and
            validation_completeness >= 0.90
        )

        return {
            'domain_check_success_rate': domain_check_success_rate,
            'trademark_check_success_rate': trademark_check_success_rate,
            'overall_accuracy': overall_accuracy,
            'validation_completeness': validation_completeness,
            'total_names_checked': total_names,
            'validation_errors_count': len(validation_errors),
            'passed': passed,
            'min_success_rate_required': self.min_success_rate
        }

    def _calculate_domain_success_rate(
        self,
        domain_availability: Dict[str, Any]
    ) -> float:
        """
        Calculate success rate for domain checks.

        A successful check means:
        - Got a result (available or taken)
        - No errors or failures
        """
        if not domain_availability:
            return 0.0

        successful_checks = 0
        total_checks = len(domain_availability)

        for name, status in domain_availability.items():
            # Check if we got a valid result
            if isinstance(status, dict):
                # Has actual domain data
                if any(
                    tld_status in ['available', 'taken']
                    for tld_status in status.values()
                ):
                    successful_checks += 1
            elif status in ['available', 'taken']:
                # Simple status string
                successful_checks += 1

        return successful_checks / total_checks if total_checks > 0 else 0.0

    def _calculate_trademark_success_rate(
        self,
        trademark_results: Dict[str, Any]
    ) -> float:
        """
        Calculate success rate for trademark checks.

        A successful check means:
        - Got a risk assessment
        - No errors or failures
        """
        if not trademark_results:
            return 0.0

        successful_checks = 0
        total_checks = len(trademark_results)

        for name, result in trademark_results.items():
            # Check if we got a valid risk assessment
            if isinstance(result, dict):
                if 'risk_level' in result or 'risk' in result:
                    successful_checks += 1
            elif isinstance(result, str) and result in ['low', 'medium', 'high', 'critical']:
                successful_checks += 1

        return successful_checks / total_checks if total_checks > 0 else 0.0


# Convenience function
def evaluate_validation_accuracy(
    validation_results: Dict[str, Any],
    min_success_rate: float = 0.95
) -> Dict[str, Any]:
    """
    Quick validation accuracy evaluation.

    Args:
        validation_results: Validation results from agent
        min_success_rate: Minimum acceptable success rate

    Returns:
        Evaluation results with pass/fail status
    """
    evaluator = ValidationAccuracyEvaluator(min_success_rate=min_success_rate)
    return evaluator.evaluate(validation_results)
