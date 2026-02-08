"""
Information Length Implementation

The information length is a conserved quantity in projections
from the grid state to physical observables.
"""

import math
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class LengthResult:
    """Result of information length computation."""
    s_start: float
    s_end: float
    length: float
    method: str


class InformationLength:
    """
    Information length computation.

    The information length L is defined as the integral of |df/dS|/f
    over a range of entropy values. For the grid state function,
    this simplifies to |S_end - S_start| / ΔS.

    This quantity is conserved under projections, meaning the
    total "information content" is preserved.

    Example:
        il = InformationLength(delta_s=0.5)
        length = il.compute(s_start=0.0, s_end=1.0)
        print(f"Information length: {length}")
    """

    def __init__(self, delta_s: float = 1.0):
        """
        Initialize the information length calculator.

        Args:
            delta_s: Characteristic entropy scale
        """
        if delta_s <= 0:
            raise ValueError("delta_s must be positive")

        self.delta_s = delta_s

    def compute(self, s_start: float, s_end: float) -> float:
        """
        Compute information length between two entropy values.

        For the standard grid state function, this is:
        L = |S_end - S_start| / ΔS

        Args:
            s_start: Starting entropy value
            s_end: Ending entropy value

        Returns:
            Information length
        """
        return abs(s_end - s_start) / self.delta_s

    def compute_from_f_ratio(self, f_start: float, f_end: float) -> float:
        """
        Compute information length from function value ratio.

        L = |ln(f_start/f_end)|

        Args:
            f_start: Function value at start
            f_end: Function value at end

        Returns:
            Information length
        """
        if f_start <= 0 or f_end <= 0:
            raise ValueError("Function values must be positive")

        return abs(math.log(f_start / f_end))

    def verify_conservation(
        self,
        length_before: float,
        length_after: float,
        tolerance: float = 0.01
    ) -> bool:
        """
        Verify that information length is conserved.

        Args:
            length_before: Length before projection
            length_after: Length after projection
            tolerance: Relative tolerance

        Returns:
            True if conserved within tolerance
        """
        if length_before == 0:
            return length_after < tolerance

        deviation = abs(length_after - length_before) / length_before
        return deviation <= tolerance


def compute_length(
    f_values: list[float],
    s_values: list[float],
    method: str = "numerical"
) -> LengthResult:
    """
    Compute information length from discrete data.

    Args:
        f_values: Function values at each point
        s_values: Entropy values at each point
        method: Computation method ("numerical" or "analytic")

    Returns:
        LengthResult with computed length
    """
    if len(f_values) != len(s_values) or len(f_values) < 2:
        raise ValueError("Need matching arrays with at least 2 points")

    if method == "numerical":
        # Numerical integration of |df/dS|/f
        length = 0.0
        for i in range(1, len(f_values)):
            ds = s_values[i] - s_values[i - 1]
            df = f_values[i] - f_values[i - 1]
            f_avg = (f_values[i] + f_values[i - 1]) / 2

            if f_avg > 0:
                length += abs(df / f_avg)

    elif method == "analytic":
        # Use log ratio
        f_start = f_values[0]
        f_end = f_values[-1]

        if f_start > 0 and f_end > 0:
            length = abs(math.log(f_start / f_end))
        else:
            length = float('inf')

    else:
        raise ValueError(f"Unknown method: {method}")

    return LengthResult(
        s_start=s_values[0],
        s_end=s_values[-1],
        length=length,
        method=method,
    )


def total_information_content(
    observables: list[tuple[list[float], list[float]]],
    delta_s: float
) -> float:
    """
    Compute total information content across multiple observables.

    Args:
        observables: List of (f_values, s_values) for each observable
        delta_s: Characteristic entropy scale

    Returns:
        Total information length (should be conserved)
    """
    total = 0.0
    il = InformationLength(delta_s=delta_s)

    for f_values, s_values in observables:
        if len(s_values) >= 2:
            result = compute_length(f_values, s_values, method="analytic")
            total += result.length

    return total
