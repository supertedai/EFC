"""
Uncertainty Propagator

Handles uncertainty propagation through proxy chains,
supporting both independent and correlated error sources.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Callable
import math


@dataclass
class UncertaintySource:
    """
    Single uncertainty source.

    Attributes:
        name: Source identifier (e.g., "distance", "inclination")
        sigma: Uncertainty value (fractional or absolute)
        is_fractional: If True, sigma is fractional; if False, absolute
        layer: Epistemic layer where this uncertainty enters
        correlation_group: Group ID for correlated sources
    """
    name: str
    sigma: float
    is_fractional: bool = True
    layer: str = "L1"
    correlation_group: Optional[str] = None


@dataclass
class PropagationResult:
    """Result of uncertainty propagation."""
    total_sigma: float
    breakdown: Dict[str, float]
    dominant_source: str
    correlation_contribution: float


class UncertaintyPropagator:
    """
    Propagates uncertainties through measurement chains.

    Supports:
    - Quadrature addition (independent sources)
    - Correlated error propagation
    - Fractional and absolute uncertainties
    - Layer-specific uncertainty tracking

    Example:
        prop = UncertaintyPropagator()

        # Add uncertainty sources
        prop.add_source("distance", sigma=0.10, is_fractional=True)
        prop.add_source("inclination", sigma=0.05, is_fractional=True)
        prop.add_source("mass_to_light", sigma=0.15, is_fractional=True)

        # Propagate to get total
        result = prop.propagate()
        print(f"Total: {result.total_sigma:.3f}")
        print(f"Dominant: {result.dominant_source}")
    """

    def __init__(self):
        self.sources: List[UncertaintySource] = []
        self.correlations: Dict[Tuple[str, str], float] = {}

    def add_source(
        self,
        name: str,
        sigma: float,
        is_fractional: bool = True,
        layer: str = "L1",
        correlation_group: Optional[str] = None,
    ) -> "UncertaintyPropagator":
        """
        Add an uncertainty source.

        Args:
            name: Source identifier
            sigma: Uncertainty value
            is_fractional: True if fractional uncertainty
            layer: Epistemic layer
            correlation_group: Group for correlated sources

        Returns:
            Self for chaining
        """
        source = UncertaintySource(
            name=name,
            sigma=sigma,
            is_fractional=is_fractional,
            layer=layer,
            correlation_group=correlation_group,
        )
        self.sources.append(source)
        return self

    def set_correlation(self, source1: str, source2: str, rho: float) -> None:
        """
        Set correlation coefficient between two sources.

        Args:
            source1: First source name
            source2: Second source name
            rho: Correlation coefficient (-1 to 1)
        """
        if not -1 <= rho <= 1:
            raise ValueError("Correlation must be between -1 and 1")

        # Store in sorted order for consistency
        key = tuple(sorted([source1, source2]))
        self.correlations[key] = rho

    def propagate(self, value: float = 1.0) -> PropagationResult:
        """
        Propagate uncertainties to get total.

        Args:
            value: Reference value for fractional uncertainties

        Returns:
            PropagationResult with breakdown
        """
        if not self.sources:
            return PropagationResult(
                total_sigma=0.0,
                breakdown={},
                dominant_source="none",
                correlation_contribution=0.0,
            )

        # Convert all to absolute uncertainties
        abs_sigmas = {}
        for src in self.sources:
            if src.is_fractional:
                abs_sigmas[src.name] = src.sigma * value
            else:
                abs_sigmas[src.name] = src.sigma

        # Quadrature sum
        sum_sq = sum(s**2 for s in abs_sigmas.values())

        # Add correlation terms
        corr_contribution = 0.0
        for (s1, s2), rho in self.correlations.items():
            if s1 in abs_sigmas and s2 in abs_sigmas:
                term = 2 * rho * abs_sigmas[s1] * abs_sigmas[s2]
                sum_sq += term
                corr_contribution += term

        # Handle same-group correlations (assume rho=1 within group)
        groups: Dict[str, List[str]] = {}
        for src in self.sources:
            if src.correlation_group:
                if src.correlation_group not in groups:
                    groups[src.correlation_group] = []
                groups[src.correlation_group].append(src.name)

        for group_members in groups.values():
            if len(group_members) > 1:
                for i, n1 in enumerate(group_members):
                    for n2 in group_members[i+1:]:
                        key = tuple(sorted([n1, n2]))
                        if key not in self.correlations:
                            term = 2 * abs_sigmas[n1] * abs_sigmas[n2]
                            sum_sq += term
                            corr_contribution += term

        total = math.sqrt(max(sum_sq, 0))

        # Find dominant source
        dominant = max(abs_sigmas.keys(), key=lambda k: abs_sigmas[k])

        return PropagationResult(
            total_sigma=total,
            breakdown=abs_sigmas,
            dominant_source=dominant,
            correlation_contribution=corr_contribution,
        )

    def by_layer(self) -> Dict[str, float]:
        """
        Get uncertainty contribution by epistemic layer.
        """
        layer_sigmas: Dict[str, List[float]] = {}

        for src in self.sources:
            if src.layer not in layer_sigmas:
                layer_sigmas[src.layer] = []
            layer_sigmas[src.layer].append(src.sigma)

        return {
            layer: math.sqrt(sum(s**2 for s in sigmas))
            for layer, sigmas in layer_sigmas.items()
        }

    def sensitivity(self, source_name: str, delta: float = 0.01) -> float:
        """
        Calculate sensitivity of total to a specific source.

        Args:
            source_name: Source to test
            delta: Fractional change to apply

        Returns:
            Fractional change in total per fractional change in source
        """
        # Get baseline
        baseline = self.propagate()

        # Perturb source
        for src in self.sources:
            if src.name == source_name:
                original = src.sigma
                src.sigma *= (1 + delta)
                perturbed = self.propagate()
                src.sigma = original

                if baseline.total_sigma > 0:
                    return (perturbed.total_sigma - baseline.total_sigma) / (
                        baseline.total_sigma * delta
                    )

        return 0.0

    def summary(self) -> str:
        """Generate human-readable summary."""
        result = self.propagate()

        lines = [
            "Uncertainty Budget",
            "=" * 40,
            "",
            "Sources:",
        ]

        for src in self.sources:
            frac = "(fractional)" if src.is_fractional else "(absolute)"
            lines.append(f"  {src.name}: σ = {src.sigma:.4f} {frac} [{src.layer}]")

        lines.extend([
            "",
            "Breakdown:",
        ])

        for name, sigma in sorted(
            result.breakdown.items(),
            key=lambda x: -x[1]
        ):
            pct = (sigma / result.total_sigma * 100) if result.total_sigma > 0 else 0
            lines.append(f"  {name}: {sigma:.4f} ({pct:.1f}%)")

        lines.extend([
            "",
            f"Total σ: {result.total_sigma:.4f}",
            f"Dominant source: {result.dominant_source}",
        ])

        if result.correlation_contribution != 0:
            lines.append(
                f"Correlation contribution: {result.correlation_contribution:.4f}"
            )

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all sources and correlations."""
        self.sources = []
        self.correlations = {}


def propagate_through_function(
    func: Callable,
    values: Dict[str, float],
    uncertainties: Dict[str, float],
    delta: float = 1e-6,
) -> Tuple[float, float]:
    """
    Propagate uncertainties through an arbitrary function using numerical derivatives.

    Args:
        func: Function to propagate through
        values: Dictionary of parameter values
        uncertainties: Dictionary of parameter uncertainties
        delta: Fractional step for numerical derivative

    Returns:
        Tuple of (function value, propagated uncertainty)
    """
    # Calculate base value
    base_value = func(**values)

    # Calculate partial derivatives numerically
    partials = {}
    for param, val in values.items():
        if param in uncertainties:
            step = abs(val * delta) if val != 0 else delta

            values_plus = values.copy()
            values_plus[param] = val + step
            f_plus = func(**values_plus)

            values_minus = values.copy()
            values_minus[param] = val - step
            f_minus = func(**values_minus)

            partials[param] = (f_plus - f_minus) / (2 * step)

    # Propagate uncertainties
    sum_sq = sum(
        (partials.get(p, 0) * uncertainties[p])**2
        for p in uncertainties
    )

    total_uncertainty = math.sqrt(sum_sq)

    return base_value, total_uncertainty
