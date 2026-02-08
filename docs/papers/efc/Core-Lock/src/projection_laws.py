"""
Projection Laws Implementation

Projection laws describe how observables emerge from the
pre-geometric grid state.
"""

import math
from dataclasses import dataclass
from typing import Callable, Optional

from .grid_state_function import GridStateFunction


@dataclass
class ProjectionResult:
    """Result of a projection computation."""
    observable: str
    s_value: float
    projected_value: float
    phase: Optional[float] = None


class ProjectionLaw:
    """
    Projection law for an observable.

    Describes how a physical observable emerges from the
    grid state through projection.

    The basic projection is: O(S) = A × f(S) + B
    where f(S) is the grid state function.

    Example:
        gsf = GridStateFunction(f0=1.0, delta_s=0.5)
        proj = ProjectionLaw("velocity", gsf, amplitude=100.0, offset=10.0)
        result = proj.project(s=1.0)
    """

    def __init__(
        self,
        observable: str,
        grid_state: GridStateFunction,
        amplitude: float = 1.0,
        offset: float = 0.0,
        exponent: float = 1.0,
    ):
        """
        Initialize a projection law.

        Args:
            observable: Name of the projected observable
            grid_state: The underlying grid state function
            amplitude: Multiplicative coefficient A
            offset: Additive constant B
            exponent: Power law exponent (default 1.0)
        """
        self.observable = observable
        self.grid_state = grid_state
        self.amplitude = amplitude
        self.offset = offset
        self.exponent = exponent

    def project(self, s: float) -> ProjectionResult:
        """
        Project the observable at given entropy.

        O(S) = A × f(S)^n + B

        Args:
            s: Entropy parameter value

        Returns:
            ProjectionResult with projected value
        """
        f_value = self.grid_state.evaluate(s)
        projected = self.amplitude * (f_value ** self.exponent) + self.offset

        return ProjectionResult(
            observable=self.observable,
            s_value=s,
            projected_value=projected,
        )

    def project_with_phase(self, s: float) -> ProjectionResult:
        """
        Project the observable including phase information.

        Phase: Φ(S) = ∫dS'/f(S')

        For the standard grid state, this integrates to:
        Φ(S) = (ΔS/f₀) × [exp(S/ΔS) - 1]

        Args:
            s: Entropy parameter value

        Returns:
            ProjectionResult with projected value and phase
        """
        f_value = self.grid_state.evaluate(s)
        projected = self.amplitude * (f_value ** self.exponent) + self.offset

        # Compute phase integral
        delta_s = self.grid_state.delta_s
        f0 = self.grid_state.f0
        phase = (delta_s / f0) * (math.exp(s / delta_s) - 1)

        return ProjectionResult(
            observable=self.observable,
            s_value=s,
            projected_value=projected,
            phase=phase,
        )

    def derivative(self, s: float) -> float:
        """
        Compute dO/dS at given entropy.

        Args:
            s: Entropy parameter value

        Returns:
            Derivative of observable with respect to S
        """
        f_value = self.grid_state.evaluate(s)
        df_ds = self.grid_state.derivative(s)

        return self.amplitude * self.exponent * (f_value ** (self.exponent - 1)) * df_ds

    def log_derivative(self, s: float) -> float:
        """
        Compute d(ln O)/dS at given entropy.

        Args:
            s: Entropy parameter value

        Returns:
            Logarithmic derivative
        """
        result = self.project(s)
        deriv = self.derivative(s)

        if result.projected_value == 0:
            return float('inf')

        return deriv / result.projected_value


def project_observable(
    observable: str,
    s_values: list[float],
    f0: float = 1.0,
    delta_s: float = 1.0,
    amplitude: float = 1.0,
    offset: float = 0.0,
) -> list[ProjectionResult]:
    """
    Project an observable over a range of entropy values.

    Args:
        observable: Name of the observable
        s_values: List of entropy values
        f0: Initial grid state value
        delta_s: Characteristic entropy scale
        amplitude: Projection amplitude
        offset: Projection offset

    Returns:
        List of ProjectionResult objects
    """
    gsf = GridStateFunction(f0=f0, delta_s=delta_s)
    law = ProjectionLaw(observable, gsf, amplitude=amplitude, offset=offset)

    return [law.project(s) for s in s_values]


def verify_projection_consistency(
    projections: list[ProjectionResult],
    delta_s: float,
    tolerance: float = 0.01
) -> tuple[bool, float]:
    """
    Verify that projections are consistent with the beta constraint.

    The log-derivative of any projection should relate to -1/ΔS.

    Args:
        projections: List of projection results
        delta_s: Expected entropy scale
        tolerance: Relative tolerance

    Returns:
        Tuple of (is_consistent, max_deviation)
    """
    if len(projections) < 2:
        return True, 0.0

    expected_log_deriv = -1.0 / delta_s
    max_deviation = 0.0

    for i in range(1, len(projections)):
        p1 = projections[i - 1]
        p2 = projections[i]

        if p1.projected_value > 0 and p2.projected_value > 0:
            ds = p2.s_value - p1.s_value
            if ds != 0:
                measured = math.log(p2.projected_value / p1.projected_value) / ds
                deviation = abs(measured - expected_log_deriv) / abs(expected_log_deriv)
                max_deviation = max(max_deviation, deviation)

    return max_deviation <= tolerance, max_deviation
