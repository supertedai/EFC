"""
Grid State Function Implementation

The grid state function f(S) = f₀ exp(-S/ΔS) describes how any
projected observable varies with entropy parameter S.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class GridStateParameters:
    """Parameters for the grid state function."""
    f0: float  # Initial value
    delta_s: float  # Characteristic entropy scale

    def validate(self) -> bool:
        """Validate parameters are physical."""
        return self.f0 > 0 and self.delta_s > 0


class GridStateFunction:
    """
    Grid state function f(S) = f₀ exp(-S/ΔS).

    This is the fundamental solution describing how observables
    project from the pre-geometric grid onto physical space.

    Attributes:
        f0: Initial value at S=0
        delta_s: Characteristic entropy scale

    Example:
        gsf = GridStateFunction(f0=1.0, delta_s=0.5)
        value = gsf.evaluate(s=1.2)
        print(f"f(1.2) = {value}")
    """

    def __init__(self, f0: float = 1.0, delta_s: float = 1.0):
        """
        Initialize the grid state function.

        Args:
            f0: Initial value at S=0
            delta_s: Characteristic entropy scale (must be positive)
        """
        if delta_s <= 0:
            raise ValueError("delta_s must be positive")

        self.f0 = f0
        self.delta_s = delta_s
        self.params = GridStateParameters(f0=f0, delta_s=delta_s)

    def evaluate(self, s: float) -> float:
        """
        Evaluate f(S) at given entropy value.

        Args:
            s: Entropy parameter value

        Returns:
            f(S) = f₀ exp(-S/ΔS)
        """
        return self.f0 * math.exp(-s / self.delta_s)

    def evaluate_array(self, s_values: list[float]) -> list[float]:
        """
        Evaluate f(S) at multiple entropy values.

        Args:
            s_values: List of entropy parameter values

        Returns:
            List of f(S) values
        """
        return [self.evaluate(s) for s in s_values]

    def derivative(self, s: float) -> float:
        """
        Compute df/dS at given entropy value.

        Args:
            s: Entropy parameter value

        Returns:
            df/dS = -f(S)/ΔS
        """
        return -self.evaluate(s) / self.delta_s

    def log_derivative(self, s: float) -> float:
        """
        Compute d(ln f)/dS.

        This equals the negative of the beta function.

        Args:
            s: Entropy parameter value

        Returns:
            d(ln f)/dS = -1/ΔS (constant!)
        """
        return -1.0 / self.delta_s

    def inverse(self, f_value: float) -> Optional[float]:
        """
        Find S such that f(S) = f_value.

        Args:
            f_value: Target function value

        Returns:
            S value, or None if f_value <= 0 or f_value > f0
        """
        if f_value <= 0 or f_value > self.f0:
            return None

        return -self.delta_s * math.log(f_value / self.f0)

    def half_life(self) -> float:
        """
        Compute the entropy 'half-life' where f drops to f0/2.

        Returns:
            S_half = ΔS × ln(2)
        """
        return self.delta_s * math.log(2)

    def summary(self) -> str:
        """Get summary of function parameters."""
        return (
            f"Grid State Function: f(S) = {self.f0} × exp(-S/{self.delta_s})\n"
            f"  f₀ = {self.f0}\n"
            f"  ΔS = {self.delta_s}\n"
            f"  Half-life: S_half = {self.half_life():.4f}\n"
            f"  d(ln f)/dS = {self.log_derivative(0):.4f} (constant)"
        )


def create_from_observations(
    s_values: list[float],
    f_values: list[float]
) -> GridStateFunction:
    """
    Fit grid state function to observations.

    Uses linear regression on log(f) vs S.

    Args:
        s_values: Observed entropy values
        f_values: Observed function values

    Returns:
        Fitted GridStateFunction
    """
    if len(s_values) != len(f_values) or len(s_values) < 2:
        raise ValueError("Need at least 2 matching observations")

    # Linear regression on ln(f) = ln(f0) - S/ΔS
    log_f = [math.log(f) for f in f_values if f > 0]

    n = len(log_f)
    sum_s = sum(s_values[:n])
    sum_log_f = sum(log_f)
    sum_s2 = sum(s**2 for s in s_values[:n])
    sum_s_log_f = sum(s * lf for s, lf in zip(s_values[:n], log_f))

    # Solve for slope and intercept
    slope = (n * sum_s_log_f - sum_s * sum_log_f) / (n * sum_s2 - sum_s**2)
    intercept = (sum_log_f - slope * sum_s) / n

    delta_s = -1.0 / slope
    f0 = math.exp(intercept)

    return GridStateFunction(f0=f0, delta_s=delta_s)
