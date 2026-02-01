"""
Effective Gravitational Coupling

Calculates G_eff for different regimes.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GravityRegime(Enum):
    """Regime for gravitational coupling."""
    BACKGROUND = "background"
    STRUCTURE = "structure"


@dataclass
class GEffectiveResult:
    """Result of G_eff calculation."""
    regime: GravityRegime
    G0: float           # Base gravitational constant (normalized to 1)
    G_eff: float        # Effective gravitational constant
    enhancement: float  # G_eff / G0
    aG: float          # Coupling coefficient
    delta_phi: float   # Phase difference


def compute_g_effective(
    regime: GravityRegime,
    aG: float = 0.094,
    delta_phi: float = 1.71,
    G0: float = 1.0
) -> GEffectiveResult:
    """
    Compute effective gravitational coupling for a regime.

    G_eff = G0                      (background)
    G_eff = G0 exp(aG · ΔΦ)         (structure)

    Args:
        regime: Background or structure
        aG: Gravitational coupling coefficient
        delta_phi: Entropy phase difference
        G0: Base gravitational constant (default: 1.0, normalized)

    Returns:
        GEffectiveResult with all values
    """
    if regime == GravityRegime.BACKGROUND:
        G_eff = G0
    else:  # STRUCTURE
        G_eff = G0 * math.exp(aG * delta_phi)

    return GEffectiveResult(
        regime=regime,
        G0=G0,
        G_eff=G_eff,
        enhancement=G_eff / G0,
        aG=aG,
        delta_phi=delta_phi,
    )


def compute_enhancement(aG: float = 0.094, delta_phi: float = 1.71) -> float:
    """
    Compute gravitational enhancement factor.

    G_eff / G0 = exp(aG · ΔΦ)

    Args:
        aG: Coupling coefficient
        delta_phi: Phase difference

    Returns:
        Enhancement factor
    """
    return math.exp(aG * delta_phi)


def derive_aG_from_enhancement(
    enhancement: float,
    delta_phi: float = 1.71
) -> float:
    """
    Derive aG from observed enhancement.

    aG = ln(G_eff / G0) / ΔΦ

    Args:
        enhancement: G_eff / G0
        delta_phi: Phase difference

    Returns:
        Coupling coefficient aG
    """
    if enhancement <= 0:
        raise ValueError("Enhancement must be positive")
    return math.log(enhancement) / delta_phi


class GEffectiveCalculator:
    """
    Calculator for regime-dependent gravitational coupling.

    The key insight: Background and structure see different G.

    Example:
        calc = GEffectiveCalculator(aG=0.094)

        G_bg = calc.compute(GravityRegime.BACKGROUND)
        G_st = calc.compute(GravityRegime.STRUCTURE)

        print(f"Enhancement: {G_st.enhancement:.3f}")  # 1.175
    """

    def __init__(
        self,
        aG: float = 0.094,
        delta_phi: float = 1.71,
        G0: float = 1.0
    ):
        """
        Initialize calculator.

        Args:
            aG: Gravitational coupling coefficient
            delta_phi: Entropy phase difference
            G0: Base gravitational constant
        """
        self.aG = aG
        self.delta_phi = delta_phi
        self.G0 = G0

    def compute(self, regime: GravityRegime) -> GEffectiveResult:
        """Compute G_eff for a regime."""
        return compute_g_effective(regime, self.aG, self.delta_phi, self.G0)

    def enhancement(self) -> float:
        """Get structure enhancement factor."""
        return compute_enhancement(self.aG, self.delta_phi)

    def background(self) -> GEffectiveResult:
        """Get background G_eff."""
        return self.compute(GravityRegime.BACKGROUND)

    def structure(self) -> GEffectiveResult:
        """Get structure G_eff."""
        return self.compute(GravityRegime.STRUCTURE)

    def summary(self) -> str:
        """Get summary of G_eff calculations."""
        bg = self.background()
        st = self.structure()

        return (
            f"Effective Gravitational Coupling\n"
            f"{'=' * 40}\n"
            f"Parameters:\n"
            f"  a_G = {self.aG}\n"
            f"  ΔΦ = {self.delta_phi}\n"
            f"  G₀ = {self.G0}\n"
            f"\n"
            f"Results:\n"
            f"  Background: G_eff = G₀ = {bg.G_eff:.4f}\n"
            f"  Structure:  G_eff = G₀ × {st.enhancement:.4f} = {st.G_eff:.4f}\n"
            f"\n"
            f"Enhancement factor: {st.enhancement:.4f} ({(st.enhancement-1)*100:.1f}%)\n"
        )
