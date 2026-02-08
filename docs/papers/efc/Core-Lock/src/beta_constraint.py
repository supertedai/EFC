"""
Beta Constraint Implementation

The core constraint β_f(S) = -1/ΔS governs how all projected
observables must behave under RG-flow.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConstraintResult:
    """Result of beta constraint verification."""
    s_value: float
    expected_beta: float
    measured_beta: float
    deviation: float
    passes: bool
    tolerance: float


class BetaConstraint:
    """
    Beta constraint β_f(S) = -1/ΔS.

    This constraint determines the universal RG-flow behavior
    of any observable projected from the grid state.

    The beta function β_f = d(ln f)/dS must equal -1/ΔS
    for all physical observables.

    Example:
        beta = BetaConstraint(delta_s=0.5)
        value = beta.compute(s=1.0)
        print(f"β_f = {value}")  # Should be -2.0
    """

    def __init__(self, delta_s: float = 1.0):
        """
        Initialize the beta constraint.

        Args:
            delta_s: Characteristic entropy scale (must be positive)
        """
        if delta_s <= 0:
            raise ValueError("delta_s must be positive")

        self.delta_s = delta_s

    def compute(self, s: float = 0.0) -> float:
        """
        Compute β_f(S).

        Note: The beta function is actually independent of S!
        The s parameter is included for interface consistency.

        Args:
            s: Entropy value (unused, included for consistency)

        Returns:
            β_f = -1/ΔS
        """
        return -1.0 / self.delta_s

    @property
    def value(self) -> float:
        """The constant beta value."""
        return -1.0 / self.delta_s

    def verify(
        self,
        s_value: float,
        measured_beta: float,
        tolerance: float = 0.01
    ) -> ConstraintResult:
        """
        Verify if a measured beta value satisfies the constraint.

        Args:
            s_value: Entropy value where beta was measured
            measured_beta: Measured beta function value
            tolerance: Relative tolerance for passing

        Returns:
            ConstraintResult with verification outcome
        """
        expected = self.compute(s_value)
        deviation = abs(measured_beta - expected) / abs(expected)
        passes = deviation <= tolerance

        return ConstraintResult(
            s_value=s_value,
            expected_beta=expected,
            measured_beta=measured_beta,
            deviation=deviation,
            passes=passes,
            tolerance=tolerance,
        )

    def summary(self) -> str:
        """Get summary of the constraint."""
        return (
            f"Beta Constraint: β_f(S) = -1/ΔS = {self.value:.4f}\n"
            f"  ΔS = {self.delta_s}\n"
            f"  This constraint is independent of S"
        )


def verify_constraint(
    delta_s: float,
    measurements: list[tuple[float, float]],
    tolerance: float = 0.01
) -> tuple[bool, list[ConstraintResult]]:
    """
    Verify the beta constraint against multiple measurements.

    Args:
        delta_s: Expected characteristic entropy scale
        measurements: List of (s_value, measured_beta) tuples
        tolerance: Relative tolerance for passing

    Returns:
        Tuple of (all_pass, results)
    """
    constraint = BetaConstraint(delta_s=delta_s)
    results = []

    for s_value, measured_beta in measurements:
        result = constraint.verify(s_value, measured_beta, tolerance)
        results.append(result)

    all_pass = all(r.passes for r in results)
    return all_pass, results


def estimate_delta_s(
    beta_measurements: list[float],
    uncertainty: Optional[float] = None
) -> tuple[float, float]:
    """
    Estimate ΔS from beta function measurements.

    Since β = -1/ΔS, we have ΔS = -1/β.

    Args:
        beta_measurements: List of measured beta values
        uncertainty: Optional measurement uncertainty

    Returns:
        Tuple of (estimated_delta_s, uncertainty)
    """
    if not beta_measurements:
        raise ValueError("Need at least one measurement")

    # Average the measurements
    avg_beta = sum(beta_measurements) / len(beta_measurements)

    if avg_beta >= 0:
        raise ValueError("Beta must be negative for physical solutions")

    delta_s = -1.0 / avg_beta

    # Estimate uncertainty
    if uncertainty is not None:
        delta_uncertainty = uncertainty / (avg_beta ** 2)
    elif len(beta_measurements) > 1:
        variance = sum((b - avg_beta)**2 for b in beta_measurements) / (len(beta_measurements) - 1)
        std_beta = math.sqrt(variance)
        delta_uncertainty = std_beta / (avg_beta ** 2)
    else:
        delta_uncertainty = 0.0

    return delta_s, delta_uncertainty
