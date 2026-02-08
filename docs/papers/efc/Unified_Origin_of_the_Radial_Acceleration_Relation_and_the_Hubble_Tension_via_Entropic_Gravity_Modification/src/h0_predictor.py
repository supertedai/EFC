"""
H₀ Predictor

Predicts the Hubble constant from the gravitational coupling coefficient
using the Friedmann constraint a_H₀ = ½ a_G.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class H0Prediction:
    """Result of an H₀ prediction."""
    h0_cmb: float           # CMB H₀ value
    h0_predicted: float     # Predicted local H₀
    h0_observed: float      # Observed local H₀
    aG: float               # Gravitational coupling
    aH0: float              # H₀ coupling (= ½ aG)
    delta_phi: float        # Phase difference
    deviation_percent: float  # Prediction error


def predict_h0(
    h0_cmb: float,
    aG: float,
    delta_phi: float = 1.71,
    h0_observed: Optional[float] = 73.0
) -> H0Prediction:
    """
    Predict local H₀ from CMB value and gravitational coupling.

    Uses the Friedmann constraint: a_H₀ = ½ a_G

    H₀_pred = H₀_CMB × exp(a_H₀ × ΔΦ)
            = H₀_CMB × exp(½ a_G × ΔΦ)

    Args:
        h0_cmb: CMB H₀ value (km/s/Mpc)
        aG: Gravitational coupling coefficient
        delta_phi: Phase difference (default: 1.71)
        h0_observed: Observed local H₀ for comparison

    Returns:
        H0Prediction with all values

    Example:
        >>> result = predict_h0(h0_cmb=67.4, aG=0.107)
        >>> print(f"H₀ = {result.h0_predicted:.1f}")  # 73.9
    """
    # Friedmann constraint: a_H₀ = ½ a_G
    aH0 = aG / 2

    # Prediction
    h0_pred = h0_cmb * math.exp(aH0 * delta_phi)

    # Deviation
    deviation = 0.0
    if h0_observed is not None and h0_observed > 0:
        deviation = abs(h0_pred - h0_observed) / h0_observed * 100

    return H0Prediction(
        h0_cmb=h0_cmb,
        h0_predicted=h0_pred,
        h0_observed=h0_observed or 0,
        aG=aG,
        aH0=aH0,
        delta_phi=delta_phi,
        deviation_percent=deviation,
    )


def derive_aG_from_h0_tension(
    h0_local: float,
    h0_cmb: float,
    delta_phi: float = 1.71
) -> float:
    """
    Derive gravitational coupling from H₀ tension.

    a_G = 2 × ln(H₀_local / H₀_CMB) / ΔΦ

    Args:
        h0_local: Local H₀ measurement
        h0_cmb: CMB H₀ measurement
        delta_phi: Phase difference

    Returns:
        Gravitational coupling a_G

    Example:
        >>> derive_aG_from_h0_tension(73.0, 67.4)  # ~0.094
    """
    if h0_local <= 0 or h0_cmb <= 0:
        raise ValueError("H₀ values must be positive")

    ln_ratio = math.log(h0_local / h0_cmb)
    aH0 = ln_ratio / delta_phi
    return 2 * aH0  # a_G = 2 × a_H₀


class H0Predictor:
    """
    H₀ prediction from entropy-driven gravity modification.

    Key insight: The Friedmann equation H² ∝ G_eff implies
    that a_H₀ = ½ a_G (NOT fitted!).

    Example:
        predictor = H0Predictor(h0_cmb=67.4)

        # From MOND
        result = predictor.predict(aG=0.107)
        print(f"Predicted: {result.h0_predicted:.1f}")

        # Derive a_G from tension
        aG = predictor.derive_aG(h0_local=73.0)
        print(f"a_G from tension: {aG:.3f}")
    """

    def __init__(
        self,
        h0_cmb: float = 67.4,
        h0_local: float = 73.0,
        delta_phi: float = 1.71
    ):
        """
        Initialize predictor.

        Args:
            h0_cmb: CMB H₀ (Planck, default: 67.4)
            h0_local: Local H₀ (SH0ES, default: 73.0)
            delta_phi: Phase difference
        """
        self.h0_cmb = h0_cmb
        self.h0_local = h0_local
        self.delta_phi = delta_phi

    def predict(self, aG: float) -> H0Prediction:
        """Predict H₀ from gravitational coupling."""
        return predict_h0(
            self.h0_cmb, aG, self.delta_phi, self.h0_local
        )

    def derive_aG(self, h0_local: Optional[float] = None) -> float:
        """Derive a_G from H₀ tension."""
        local = h0_local if h0_local is not None else self.h0_local
        return derive_aG_from_h0_tension(local, self.h0_cmb, self.delta_phi)

    def tension_summary(self) -> str:
        """Get summary of H₀ tension analysis."""
        aG = self.derive_aG()
        aH0 = aG / 2

        return (
            f"H₀ Tension Analysis\n"
            f"{'=' * 40}\n"
            f"Inputs:\n"
            f"  H₀ (CMB/Planck): {self.h0_cmb} km/s/Mpc\n"
            f"  H₀ (Local/SH0ES): {self.h0_local} km/s/Mpc\n"
            f"  ΔΦ: {self.delta_phi}\n"
            f"\n"
            f"Derived:\n"
            f"  ln(H₀_local/H₀_CMB) = {math.log(self.h0_local/self.h0_cmb):.4f}\n"
            f"  a_H₀ = {aH0:.4f}\n"
            f"  a_G = 2 × a_H₀ = {aG:.4f}\n"
        )

    def prediction_summary(self, aG: float) -> str:
        """Get summary of H₀ prediction."""
        result = self.predict(aG)

        return (
            f"H₀ Prediction\n"
            f"{'=' * 40}\n"
            f"Input:\n"
            f"  a_G = {aG:.4f}\n"
            f"  a_H₀ = ½ a_G = {result.aH0:.4f}\n"
            f"  ΔΦ = {result.delta_phi}\n"
            f"\n"
            f"Prediction:\n"
            f"  H₀_pred = {self.h0_cmb} × exp({result.aH0:.4f} × {result.delta_phi})\n"
            f"  H₀_pred = {result.h0_predicted:.1f} km/s/Mpc\n"
            f"\n"
            f"Comparison:\n"
            f"  H₀_observed = {result.h0_observed:.1f} km/s/Mpc\n"
            f"  Deviation = {result.deviation_percent:.1f}%\n"
        )
