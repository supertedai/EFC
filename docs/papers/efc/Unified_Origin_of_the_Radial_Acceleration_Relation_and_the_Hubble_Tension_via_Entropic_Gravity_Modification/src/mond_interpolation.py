"""
MOND Interpolation Functions

The MOND paradigm introduces a universal acceleration scale a₀ = 1.2×10⁻¹⁰ m/s².
The interpolation function μ(x) connects Newtonian and deep-MOND regimes.
"""

import math
from dataclasses import dataclass
from typing import Optional


# MOND acceleration scale
A0_MOND = 1.2e-10  # m/s²


@dataclass
class MONDPoint:
    """A point on the MOND interpolation curve."""
    g_ratio: float      # g_bar / a₀
    mu: float           # Interpolation function value
    mu_inverse: float   # Gravitational enhancement
    ln_mu_inv: float    # ln(μ⁻¹)
    implied_aG: float   # Implied coupling coefficient


def mond_mu(x: float, form: str = "simple") -> float:
    """
    MOND interpolation function μ(x).

    Args:
        x: g_bar / a₀ ratio
        form: Interpolation form
            - "simple": μ = x/(1+x)
            - "standard": μ = x/√(1+x²)

    Returns:
        μ(x) value in [0, 1]

    Examples:
        >>> mond_mu(1.0)   # 0.5
        >>> mond_mu(5.0)   # 0.833
        >>> mond_mu(10.0)  # 0.909
    """
    if x < 0:
        raise ValueError(f"x must be non-negative, got {x}")

    if form == "simple":
        return x / (1 + x)
    elif form == "standard":
        return x / math.sqrt(1 + x * x)
    else:
        raise ValueError(f"Unknown form: {form}")


def compute_aG_from_mond(
    g_ratio: float,
    delta_phi: float = 1.71,
    form: str = "simple"
) -> float:
    """
    Compute gravitational coupling a_G from MOND interpolation.

    a_G = ln(μ⁻¹) / ΔΦ

    Args:
        g_ratio: g_bar / a₀ ratio
        delta_phi: Phase difference (default: 1.71)
        form: MOND interpolation form

    Returns:
        Implied gravitational coupling coefficient a_G

    Example:
        >>> compute_aG_from_mond(5.0)  # ~0.107
    """
    mu = mond_mu(g_ratio, form)
    mu_inv = 1.0 / mu
    return math.log(mu_inv) / delta_phi


def get_mond_point(
    g_ratio: float,
    delta_phi: float = 1.71,
    form: str = "simple"
) -> MONDPoint:
    """
    Get full MOND interpolation data for a g_bar/a₀ ratio.

    Args:
        g_ratio: g_bar / a₀ ratio
        delta_phi: Phase difference
        form: Interpolation form

    Returns:
        MONDPoint with all computed values
    """
    mu = mond_mu(g_ratio, form)
    mu_inv = 1.0 / mu
    ln_mu_inv = math.log(mu_inv)
    implied_aG = ln_mu_inv / delta_phi

    return MONDPoint(
        g_ratio=g_ratio,
        mu=mu,
        mu_inverse=mu_inv,
        ln_mu_inv=ln_mu_inv,
        implied_aG=implied_aG,
    )


class MONDInterpolator:
    """
    MOND interpolation calculator.

    Provides the connection between galaxy rotation data
    and the gravitational coupling coefficient a_G.

    Example:
        interp = MONDInterpolator()
        point = interp.get_point(g_ratio=5.0)
        print(f"a_G = {point.implied_aG:.3f}")  # 0.107
    """

    STANDARD_RATIOS = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]

    def __init__(
        self,
        delta_phi: float = 1.71,
        form: str = "simple"
    ):
        """
        Initialize the interpolator.

        Args:
            delta_phi: Phase difference
            form: Interpolation form ("simple" or "standard")
        """
        self.delta_phi = delta_phi
        self.form = form

    def mu(self, g_ratio: float) -> float:
        """Get μ(x) for given g_bar/a₀."""
        return mond_mu(g_ratio, self.form)

    def aG(self, g_ratio: float) -> float:
        """Get implied a_G for given g_bar/a₀."""
        return compute_aG_from_mond(g_ratio, self.delta_phi, self.form)

    def get_point(self, g_ratio: float) -> MONDPoint:
        """Get full data point."""
        return get_mond_point(g_ratio, self.delta_phi, self.form)

    def get_table(self, ratios: Optional[list[float]] = None) -> list[MONDPoint]:
        """
        Generate table of MOND values.

        Args:
            ratios: List of g_bar/a₀ values (default: standard set)

        Returns:
            List of MONDPoint objects
        """
        if ratios is None:
            ratios = self.STANDARD_RATIOS
        return [self.get_point(r) for r in ratios]

    def transition_zone_aG(self) -> float:
        """
        Get a_G at the transition zone (g_bar/a₀ = 5).

        This is where cosmic-scale structures typically reside.
        """
        return self.aG(5.0)

    def summary(self) -> str:
        """Get summary table."""
        lines = [
            f"MOND Interpolation Table (ΔΦ = {self.delta_phi})",
            "=" * 50,
            f"{'g/a₀':>8} {'μ':>8} {'μ⁻¹':>8} {'ln(μ⁻¹)':>10} {'a_G':>8}",
            "-" * 50,
        ]

        for r in self.STANDARD_RATIOS:
            p = self.get_point(r)
            lines.append(
                f"{p.g_ratio:>8.1f} {p.mu:>8.3f} {p.mu_inverse:>8.3f} "
                f"{p.ln_mu_inv:>10.3f} {p.implied_aG:>8.3f}"
            )

        lines.append("-" * 50)
        lines.append(f"Transition zone (g/a₀=5): a_G = {self.transition_zone_aG():.3f}")

        return "\n".join(lines)
