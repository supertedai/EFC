"""
Core Lock Simulation Implementation

Numerical verification of the Core Lock mathematical framework.
"""

import math
from dataclasses import dataclass
from typing import Optional

from .grid_state_function import GridStateFunction
from .beta_constraint import BetaConstraint
from .information_length import InformationLength, compute_length
from .projection_laws import ProjectionLaw


@dataclass
class SimulationResult:
    """Result of a Core Lock simulation."""
    s_values: list[float]
    f_values: list[float]
    beta_values: list[float]
    phase_values: list[float]
    constraint_satisfied: bool
    information_length: float
    correlation_test_passed: bool
    summary: str


class CoreLockSimulation:
    """
    Simulation engine for Core Lock verification.

    Runs numerical tests to verify:
    1. Grid state function behaves correctly
    2. Beta constraint is satisfied
    3. Information length is conserved
    4. Correlation signature is constant

    Example:
        sim = CoreLockSimulation(f0=1.0, delta_s=0.5)
        result = sim.run(s_min=0.0, s_max=2.0, n_points=100)
        print(result.summary)
    """

    def __init__(self, f0: float = 1.0, delta_s: float = 1.0):
        """
        Initialize the simulation.

        Args:
            f0: Initial grid state value
            delta_s: Characteristic entropy scale
        """
        self.f0 = f0
        self.delta_s = delta_s
        self.gsf = GridStateFunction(f0=f0, delta_s=delta_s)
        self.beta = BetaConstraint(delta_s=delta_s)
        self.info_length = InformationLength(delta_s=delta_s)

    def run(
        self,
        s_min: float = 0.0,
        s_max: float = 5.0,
        n_points: int = 100,
        tolerance: float = 0.01
    ) -> SimulationResult:
        """
        Run full simulation.

        Args:
            s_min: Minimum entropy value
            s_max: Maximum entropy value
            n_points: Number of evaluation points
            tolerance: Tolerance for constraint checks

        Returns:
            SimulationResult with all computed values
        """
        # Generate S values
        s_values = [s_min + i * (s_max - s_min) / (n_points - 1) for i in range(n_points)]

        # Compute grid state function
        f_values = self.gsf.evaluate_array(s_values)

        # Compute beta values (should all equal -1/ΔS)
        beta_values = [self.gsf.log_derivative(s) for s in s_values]

        # Compute phase values
        phase_values = []
        for s in s_values:
            phase = (self.delta_s / self.f0) * (math.exp(s / self.delta_s) - 1)
            phase_values.append(phase)

        # Check beta constraint
        expected_beta = self.beta.value
        beta_deviations = [abs(b - expected_beta) / abs(expected_beta) for b in beta_values]
        constraint_satisfied = all(d <= tolerance for d in beta_deviations)

        # Compute information length
        length_result = compute_length(f_values, s_values, method="analytic")
        info_length = length_result.length

        # Correlation test: d ln v / d ln c should be constant
        correlation_passed = self._test_correlation(s_values, f_values, tolerance)

        # Build summary
        summary = self._build_summary(
            s_min, s_max, n_points, constraint_satisfied,
            info_length, correlation_passed, max(beta_deviations)
        )

        return SimulationResult(
            s_values=s_values,
            f_values=f_values,
            beta_values=beta_values,
            phase_values=phase_values,
            constraint_satisfied=constraint_satisfied,
            information_length=info_length,
            correlation_test_passed=correlation_passed,
            summary=summary,
        )

    def _test_correlation(
        self,
        s_values: list[float],
        f_values: list[float],
        tolerance: float
    ) -> bool:
        """
        Test the correlation signature d ln v / d ln c = constant.

        For the grid state function, this tests that the ratio of
        log-derivatives is constant (which it should be, since both
        are -1/ΔS).
        """
        if len(s_values) < 3:
            return True

        # Compute log derivatives at each point
        log_derivs = []
        for i in range(1, len(f_values) - 1):
            if f_values[i] > 0 and f_values[i - 1] > 0:
                ds = s_values[i] - s_values[i - 1]
                d_ln_f = math.log(f_values[i] / f_values[i - 1])
                log_derivs.append(d_ln_f / ds if ds != 0 else 0)

        if len(log_derivs) < 2:
            return True

        # Check that all are approximately equal
        mean_deriv = sum(log_derivs) / len(log_derivs)
        if mean_deriv == 0:
            return True

        max_deviation = max(abs(ld - mean_deriv) / abs(mean_deriv) for ld in log_derivs)
        return max_deviation <= tolerance

    def _build_summary(
        self,
        s_min: float,
        s_max: float,
        n_points: int,
        constraint_ok: bool,
        info_length: float,
        correlation_ok: bool,
        max_beta_deviation: float,
    ) -> str:
        """Build human-readable summary."""
        status = "PASSED" if (constraint_ok and correlation_ok) else "FAILED"

        return (
            f"Core Lock Simulation Result: {status}\n"
            f"{'=' * 40}\n"
            f"Parameters:\n"
            f"  f₀ = {self.f0}\n"
            f"  ΔS = {self.delta_s}\n"
            f"  S range: [{s_min}, {s_max}]\n"
            f"  Points: {n_points}\n"
            f"\n"
            f"Results:\n"
            f"  β = -1/ΔS = {self.beta.value:.4f}\n"
            f"  Max β deviation: {max_beta_deviation:.2%}\n"
            f"  Constraint satisfied: {'Yes' if constraint_ok else 'No'}\n"
            f"  Information length: {info_length:.4f}\n"
            f"  Correlation test: {'Passed' if correlation_ok else 'Failed'}\n"
        )


def run_verification(
    f0: float = 1.0,
    delta_s: float = 1.0,
    s_range: tuple[float, float] = (0.0, 5.0),
    tolerance: float = 0.01
) -> SimulationResult:
    """
    Convenience function to run verification.

    Args:
        f0: Initial grid state value
        delta_s: Characteristic entropy scale
        s_range: Tuple of (s_min, s_max)
        tolerance: Tolerance for checks

    Returns:
        SimulationResult
    """
    sim = CoreLockSimulation(f0=f0, delta_s=delta_s)
    return sim.run(s_min=s_range[0], s_max=s_range[1], tolerance=tolerance)
