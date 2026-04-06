"""
Foundations of Energy-Flow Cosmology (EFC).

Implements the core equations and regime architecture of EFC:
- Effective gravitational coupling: mu(a) = 1 + beta * S(a)
- Regime Response Surface: mu(k, S) = 1 + R(k, S)
- Four-level regime architecture: L0 (Latent), L1 (Stable Active),
  L2 (Complex Active), L3 (Residual)
- Methodological principles of Entropy-Bounded Empiricism

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RegimeLevel(Enum):
    """Four-level regime architecture for EFC validity domains.

    L0: Latent -- pre-activation, entropy below threshold.
    L1: Stable Active -- high confidence, reliable predictions.
    L2: Complex Active -- requires uncertainty quantification.
    L3: Residual -- historical retrieval only.
    """
    L0 = "L0_Latent"
    L1 = "L1_Stable_Active"
    L2 = "L2_Complex_Active"
    L3 = "L3_Residual"


@dataclass
class RegimeLevelSpec:
    """Specification for a single regime level.

    Attributes:
        level: The regime level enum.
        description: Human-readable description.
        S_range: Entropy range (min, max) for this level.
        validity: What predictions are valid in this regime.
    """
    level: RegimeLevel
    description: str
    S_range: Tuple[float, float]
    validity: str


@dataclass
class EFCParameters:
    """Core parameters of the EFC framework.

    Attributes:
        beta: Coupling strength for entropy modification.
        S_threshold: Entropy activation threshold for L0->L1 transition.
        k_ref: Reference wavenumber for the response surface.
    """
    beta: float = 0.12
    S_threshold: float = 0.1
    k_ref: float = 1.0


class EffectiveGravitationalCoupling:
    """Computes the effective gravitational coupling mu(a) = 1 + beta * S(a).

    The core equation of EFC: gravitational coupling is modified by
    the local entropy field, producing scale-dependent deviations
    from standard GR.

    Attributes:
        beta: Coupling strength parameter.
    """

    def __init__(self, beta: float = 0.12):
        self.beta = beta

    def mu(self, S: float) -> float:
        """Compute effective gravitational coupling.

        Args:
            S: Local entropy value.

        Returns:
            mu = G_eff / G = 1 + beta * S
        """
        return 1.0 + self.beta * S

    def G_eff(self, S: float, G: float = 1.0) -> float:
        """Compute effective gravitational constant.

        Args:
            S: Local entropy value.
            G: Newton's gravitational constant (normalised to 1).

        Returns:
            G_eff = G * mu(S)
        """
        return G * self.mu(S)

    def regime_response_surface(self, k: float, S: float) -> float:
        """Compute the Regime Response Surface mu(k, S) = 1 + R(k, S).

        The two-dimensional surface encodes how gravitational coupling
        varies across wavenumber k and entropy S.

        Args:
            k: Wavenumber (spatial scale).
            S: Entropy value.

        Returns:
            mu(k, S)
        """
        # R(k, S) = beta * S * exp(-k^2 / 2)
        R = self.beta * S * math.exp(-k * k / 2.0)
        return 1.0 + R


class EFCFoundations:
    """Top-level class for the Foundations of EFC framework.

    Encapsulates the regime architecture, core equations, and
    methodological principles of Entropy-Bounded Empiricism.

    Attributes:
        params: Core EFC parameters.
        coupling: Effective gravitational coupling calculator.
        regime_specs: Specifications for each regime level.
    """

    METHODOLOGICAL_PRINCIPLES = [
        "Regime-bounded inference",
        "Pre-registration of predictions",
        "No post-hoc parameter fitting",
        "Causal ordering enforcement",
        "Cross-scale consistency requirements",
    ]

    def __init__(self, params: Optional[EFCParameters] = None):
        self.params = params or EFCParameters()
        self.coupling = EffectiveGravitationalCoupling(beta=self.params.beta)
        self.regime_specs = self._build_regime_specs()

    def _build_regime_specs(self) -> Dict[RegimeLevel, RegimeLevelSpec]:
        """Construct the four-level regime architecture."""
        return {
            RegimeLevel.L0: RegimeLevelSpec(
                level=RegimeLevel.L0,
                description="Latent: pre-activation, entropy below threshold.",
                S_range=(0.0, self.params.S_threshold),
                validity="Pre-activation, entropy below threshold",
            ),
            RegimeLevel.L1: RegimeLevelSpec(
                level=RegimeLevel.L1,
                description="Stable Active: high confidence, reliable predictions.",
                S_range=(self.params.S_threshold, 0.4),
                validity="High confidence, reliable predictions",
            ),
            RegimeLevel.L2: RegimeLevelSpec(
                level=RegimeLevel.L2,
                description="Complex Active: requires uncertainty quantification.",
                S_range=(0.4, 0.7),
                validity="Requires uncertainty quantification",
            ),
            RegimeLevel.L3: RegimeLevelSpec(
                level=RegimeLevel.L3,
                description="Residual: historical retrieval only.",
                S_range=(0.7, 1.0),
                validity="Historical retrieval only",
            ),
        }

    def classify_regime(self, S: float) -> RegimeLevel:
        """Classify an entropy value into a regime level.

        Args:
            S: Entropy value (0-1).

        Returns:
            The corresponding RegimeLevel.
        """
        for level, spec in self.regime_specs.items():
            lo, hi = spec.S_range
            if lo <= S < hi:
                return level
        return RegimeLevel.L3

    def evaluate_coupling(self, S: float) -> Dict[str, float]:
        """Evaluate the effective coupling at a given entropy.

        Args:
            S: Entropy value.

        Returns:
            Dictionary with mu, G_eff, and regime level.
        """
        mu = self.coupling.mu(S)
        regime = self.classify_regime(S)
        return {
            "S": S,
            "mu": mu,
            "G_eff_over_G": mu,
            "regime": regime.value,
        }

    def scan_entropy(self, S_values: List[float]) -> List[Dict]:
        """Evaluate the coupling across a range of entropy values.

        Args:
            S_values: List of entropy values to evaluate.

        Returns:
            List of evaluation dictionaries.
        """
        return [self.evaluate_coupling(S) for S in S_values]

    def response_surface_grid(
        self, k_range: Tuple[float, float, int], S_range: Tuple[float, float, int]
    ) -> List[Dict[str, float]]:
        """Compute the response surface on a (k, S) grid.

        Args:
            k_range: (k_min, k_max, n_k) tuple.
            S_range: (S_min, S_max, n_S) tuple.

        Returns:
            List of dicts with k, S, mu values.
        """
        k_min, k_max, n_k = k_range
        S_min, S_max, n_S = S_range
        results = []
        for i in range(n_k):
            k = k_min + (k_max - k_min) * i / max(n_k - 1, 1)
            for j in range(n_S):
                S = S_min + (S_max - S_min) * j / max(n_S - 1, 1)
                mu = self.coupling.regime_response_surface(k, S)
                results.append({"k": round(k, 4), "S": round(S, 4), "mu": round(mu, 6)})
        return results

    def summary(self) -> Dict:
        """Return a summary of the framework state."""
        return {
            "beta": self.params.beta,
            "S_threshold": self.params.S_threshold,
            "regime_levels": {
                level.value: {
                    "S_range": spec.S_range,
                    "validity": spec.validity,
                }
                for level, spec in self.regime_specs.items()
            },
            "methodological_principles": self.METHODOLOGICAL_PRINCIPLES,
        }


if __name__ == "__main__":
    efc = EFCFoundations()
    result = efc.evaluate_coupling(0.25)
    assert result["mu"] == 1.0 + 0.12 * 0.25
    assert efc.classify_regime(0.05) == RegimeLevel.L0
    assert efc.classify_regime(0.25) == RegimeLevel.L1
    print("EFC Foundations module OK")
