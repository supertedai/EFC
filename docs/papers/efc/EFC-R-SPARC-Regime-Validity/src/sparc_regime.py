"""
EFC-R SPARC Regime Validity
============================
Classes implementing the EFC-R framework for regime-dependent validity
analysis of galaxy rotation curves from the SPARC database.

Key equation: E_total = E_flow + E_latent

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GalaxyRegime:
    """A single galaxy with regime classification.

    Parameters
    ----------
    name : str
        Galaxy identifier from SPARC catalogue.
    morphology : str
        Morphological type: 'LSB', 'dwarf_irregular', 'spiral', 'barred_disturbed'.
    chi2_efc : float
        Reduced chi-squared for EFC fit.
    chi2_lcdm : float
        Reduced chi-squared for LCDM fit.
    entropy_gradient : float
        Mean entropy gradient (kpc^-1).
    alpha : float
        Regime parameter alpha (0 = fully latent, 1 = fully flow-dominated).
    efc_success : bool
        Whether EFC provides a better fit than LCDM.
    """

    name: str
    morphology: str
    chi2_efc: float
    chi2_lcdm: float
    entropy_gradient: float
    alpha: float = 1.0
    efc_success: bool = True

    @property
    def chi2_ratio(self) -> float:
        """Ratio chi2_efc / chi2_lcdm.  < 1 favours EFC."""
        if self.chi2_lcdm == 0:
            return float("inf")
        return self.chi2_efc / self.chi2_lcdm

    @property
    def regime_label(self) -> str:
        """Human-readable regime label based on alpha."""
        if self.alpha >= 0.8:
            return "flow-dominated"
        elif self.alpha >= 0.4:
            return "mixed"
        else:
            return "latent-dominated"


@dataclass
class EFCRDecomposition:
    """Energy decomposition: E_total = E_flow + E_latent.

    Parameters
    ----------
    E_total : float
        Total energy (arbitrary units).
    alpha : float
        Flow fraction (0-1).  E_flow = alpha * E_total.
    """

    E_total: float
    alpha: float = 1.0

    @property
    def E_flow(self) -> float:
        return self.alpha * self.E_total

    @property
    def E_latent(self) -> float:
        return (1.0 - self.alpha) * self.E_total

    def regime_transition(self, new_alpha: float) -> "EFCRDecomposition":
        """Return a new decomposition with a different alpha."""
        return EFCRDecomposition(E_total=self.E_total, alpha=new_alpha)


@dataclass
class SPARCAnalyzer:
    """Analyze a sample of SPARC galaxies under EFC-R."""

    galaxies: List[GalaxyRegime] = field(default_factory=list)

    def success_rate(self, morphology: Optional[str] = None) -> float:
        """Fraction of galaxies where EFC is preferred."""
        subset = self.galaxies
        if morphology is not None:
            subset = [g for g in self.galaxies if g.morphology == morphology]
        if not subset:
            return 0.0
        return sum(1 for g in subset if g.efc_success) / len(subset)

    def mean_chi2_efc(self) -> float:
        if not self.galaxies:
            return 0.0
        return sum(g.chi2_efc for g in self.galaxies) / len(self.galaxies)

    def mean_chi2_lcdm(self) -> float:
        if not self.galaxies:
            return 0.0
        return sum(g.chi2_lcdm for g in self.galaxies) / len(self.galaxies)

    def mean_entropy_gradient(self) -> float:
        if not self.galaxies:
            return 0.0
        return sum(g.entropy_gradient for g in self.galaxies) / len(self.galaxies)

    def morphology_breakdown(self) -> dict:
        """Success rates grouped by morphology type."""
        types = sorted(set(g.morphology for g in self.galaxies))
        return {t: self.success_rate(t) for t in types}

    def spearman_rank_proxy(self) -> float:
        """Simplified rank-correlation proxy between structural complexity
        (encoded as morphology ordinal) and chi2 ratio."""
        ordinal = {"LSB": 1, "dwarf_irregular": 2, "spiral": 3, "barred_disturbed": 4}
        pairs = []
        for g in self.galaxies:
            o = ordinal.get(g.morphology, 2)
            pairs.append((o, g.chi2_ratio))
        if len(pairs) < 3:
            return 0.0
        # Spearman via ranks
        n = len(pairs)
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]

        def _rank(vals):
            order = sorted(range(len(vals)), key=lambda i: vals[i])
            ranks = [0.0] * len(vals)
            for r, i in enumerate(order):
                ranks[i] = r + 1.0
            return ranks

        rx = _rank(xs)
        ry = _rank(ys)
        d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
        rho = 1 - 6 * d2 / (n * (n ** 2 - 1))
        return rho

    def summary(self) -> dict:
        return {
            "n_galaxies": len(self.galaxies),
            "overall_success_rate": self.success_rate(),
            "mean_chi2_efc": self.mean_chi2_efc(),
            "mean_chi2_lcdm": self.mean_chi2_lcdm(),
            "mean_entropy_gradient": self.mean_entropy_gradient(),
            "morphology_breakdown": self.morphology_breakdown(),
            "spearman_rho_proxy": round(self.spearman_rank_proxy(), 3),
        }
