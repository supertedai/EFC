"""
Entropy-Bounded Empiricism (EBE) - SPARC175 Galaxy Rotation Curve Analysis.

Implements the EBE framework for regime-dependent validity analysis,
including the L structural proxy, S entropy estimate, and three-regime
classification (FLOW, TRANSITION, LATENT).

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Regime(Enum):
    """Galaxy regime classification based on L and S values."""
    FLOW = "FLOW"
    TRANSITION = "TRANSITION"
    LATENT = "LATENT"


@dataclass
class RegimeThresholds:
    """Empirically determined regime boundary thresholds.

    Attributes:
        L1: Upper L boundary for FLOW regime.
        L2: Upper L boundary for TRANSITION regime.
        S_lower: Lower entropy bound for empirical validity.
        S_upper: Upper entropy bound for empirical validity.
    """
    L1: float = 0.337
    L2: float = 0.427
    S_lower: float = 0.1
    S_upper: float = 0.9


@dataclass
class Galaxy:
    """Represents a single SPARC galaxy with rotation curve data.

    Attributes:
        name: Standard astronomical name.
        L_value: Model-blind structural proxy (0-1).
        S_estimate: Entropy estimate derived from L.
        chi2_efc: Chi-squared for EFC model fit.
        chi2_lcdm: Chi-squared for LCDM model fit.
        n_points: Number of data points in rotation curve.
        distance_mpc: Distance in megaparsecs.
        inclination_deg: Disk inclination angle in degrees.
        mass_proxy: Log stellar mass estimate.
    """
    name: str
    L_value: float
    S_estimate: float
    chi2_efc: float = 0.0
    chi2_lcdm: float = 0.0
    n_points: int = 0
    distance_mpc: float = 0.0
    inclination_deg: float = 0.0
    mass_proxy: float = 0.0

    @property
    def success_efc(self) -> bool:
        """Whether the EFC model fit succeeds (chi2 < 3)."""
        return self.chi2_efc < 3.0

    @property
    def success_lcdm(self) -> bool:
        """Whether the LCDM model fit succeeds (chi2 < 3)."""
        return self.chi2_lcdm < 3.0


class RegimeClassifier:
    """Classifies galaxies into FLOW, TRANSITION, or LATENT regimes.

    The classification is based on the model-blind structural proxy L
    and the derived entropy estimate S, using empirically determined
    thresholds from the SPARC175 dataset.
    """

    def __init__(self, thresholds: Optional[RegimeThresholds] = None):
        self.thresholds = thresholds or RegimeThresholds()

    def classify(self, L: float) -> Regime:
        """Classify a galaxy based on its L value.

        Args:
            L: Model-blind structural proxy value (0-1).

        Returns:
            The regime classification.
        """
        if L < self.thresholds.L1:
            return Regime.FLOW
        elif L < self.thresholds.L2:
            return Regime.TRANSITION
        else:
            return Regime.LATENT

    def is_empirically_valid(self, S: float) -> bool:
        """Check if an entropy value falls within empirical validity bounds.

        Args:
            S: Entropy estimate.

        Returns:
            True if S is within [S_lower, S_upper].
        """
        return self.thresholds.S_lower <= S <= self.thresholds.S_upper

    @staticmethod
    def L_to_S(L: float) -> float:
        """Convert L structural proxy to S entropy estimate.

        Uses a calibrated monotonic mapping from the structural proxy
        to the thermodynamic entropy estimate.

        Args:
            L: Structural proxy value (0-1).

        Returns:
            Entropy estimate S.
        """
        # Calibrated sigmoidal mapping
        return 1.0 / (1.0 + math.exp(-10.0 * (L - 0.4)))


class EntropyBoundedEmpiricism:
    """Main EBE framework for regime-dependent validity analysis.

    Encapsulates the full analysis pipeline: regime classification,
    success rate computation, and statistical summary generation.

    Attributes:
        galaxies: List of Galaxy objects to analyse.
        classifier: RegimeClassifier instance.
    """

    def __init__(
        self,
        galaxies: Optional[List[Galaxy]] = None,
        thresholds: Optional[RegimeThresholds] = None,
    ):
        self.galaxies: List[Galaxy] = galaxies or []
        self.classifier = RegimeClassifier(thresholds)

    def add_galaxy(self, galaxy: Galaxy) -> None:
        """Add a galaxy to the analysis set."""
        self.galaxies.append(galaxy)

    def classify_all(self) -> dict[Regime, list[Galaxy]]:
        """Classify all galaxies into regimes.

        Returns:
            Dictionary mapping each regime to its list of galaxies.
        """
        result: dict[Regime, list[Galaxy]] = {r: [] for r in Regime}
        for g in self.galaxies:
            regime = self.classifier.classify(g.L_value)
            result[regime].append(g)
        return result

    def success_rate(self, regime: Regime, model: str = "efc") -> float:
        """Compute the success rate for a given regime and model.

        Args:
            regime: The regime to compute the rate for.
            model: Either 'efc' or 'lcdm'.

        Returns:
            Success rate as a fraction (0-1).
        """
        classified = self.classify_all()
        galaxies_in_regime = classified[regime]
        if not galaxies_in_regime:
            return 0.0
        if model == "efc":
            successes = sum(1 for g in galaxies_in_regime if g.success_efc)
        else:
            successes = sum(1 for g in galaxies_in_regime if g.success_lcdm)
        return successes / len(galaxies_in_regime)

    def regime_summary(self) -> dict:
        """Generate a summary of regime distribution and success rates.

        Returns:
            Dictionary with regime statistics.
        """
        classified = self.classify_all()
        total = len(self.galaxies)
        summary = {}
        for regime, gals in classified.items():
            n = len(gals)
            summary[regime.value] = {
                "n": n,
                "pct": (n / total * 100) if total > 0 else 0,
                "efc_success_rate": self.success_rate(regime, "efc"),
                "lcdm_success_rate": self.success_rate(regime, "lcdm"),
                "mean_L": (sum(g.L_value for g in gals) / n) if n > 0 else 0,
                "mean_S": (sum(g.S_estimate for g in gals) / n) if n > 0 else 0,
            }
        return summary

    @staticmethod
    def cliffs_delta(group1: list[float], group2: list[float]) -> float:
        """Compute Cliff's delta effect size.

        Args:
            group1: First group of values.
            group2: Second group of values.

        Returns:
            Cliff's delta (-1 to 1).
        """
        n1, n2 = len(group1), len(group2)
        if n1 == 0 or n2 == 0:
            return 0.0
        dominance = 0
        for x in group1:
            for y in group2:
                if x > y:
                    dominance += 1
                elif x < y:
                    dominance -= 1
        return dominance / (n1 * n2)


if __name__ == "__main__":
    # Quick self-test
    clf = RegimeClassifier()
    assert clf.classify(0.2) == Regime.FLOW
    assert clf.classify(0.38) == Regime.TRANSITION
    assert clf.classify(0.5) == Regime.LATENT
    print("EBE SPARC175 module OK")
