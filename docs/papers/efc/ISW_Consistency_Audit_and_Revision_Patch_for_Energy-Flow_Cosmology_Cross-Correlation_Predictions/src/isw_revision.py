#!/usr/bin/env python3
"""
ISW Revision Patch - Reference Implementation

Reference implementation for the revised ISW cross-correlation predictions
following the ISW Consistency Audit v1.1.

Paper: "ISW Paper Revision Patch: Proposed Corrections to ISW Cross-Correlation
       Predictions for EFC with DESI DR1 Tracers"
DOI: 10.6084/m9.figshare.31329082
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ISWChannel(Enum):
    """ISW channel interpretation."""
    GROWTH_DRIVEN = "growth_driven"
    POTENTIAL_DRIVEN = "potential_driven"


@dataclass
class MuParameters:
    """μ(a) parameterisation (unchanged from original)."""
    beta: float = 0.16
    a_t: float = 0.55
    sigma: float = 0.25

    def mu(self, a: float) -> float:
        """
        Compute μ(a) = 1 + β × exp[-(a - a_t)² / (2σ²)]

        Parameters
        ----------
        a : float
            Scale factor

        Returns
        -------
        float
            μ(a) value
        """
        return 1.0 + self.beta * np.exp(-(a - self.a_t)**2 / (2 * self.sigma**2))

    def dmu_dlna(self, a: float) -> float:
        """
        Compute dμ/d ln a (needed for potential-driven channel).

        Parameters
        ----------
        a : float
            Scale factor

        Returns
        -------
        float
            dμ/d ln a value
        """
        delta = a - self.a_t
        return -self.beta * (a * delta / self.sigma**2) * np.exp(-delta**2 / (2 * self.sigma**2))


@dataclass
class TracerPrediction:
    """ISW prediction for a single tracer."""
    name: str
    z_eff: float
    A_ISW_original: float
    A_ISW_revised: float
    original_status: str = "withdrawn"
    cancellation_index: Optional[float] = None

    @property
    def suppression_original(self) -> float:
        """Original claimed suppression relative to ΛCDM."""
        return (1 - self.A_ISW_original) * 100

    @property
    def suppression_revised(self) -> float:
        """Revised suppression relative to ΛCDM."""
        return (1 - self.A_ISW_revised) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "z_eff": self.z_eff,
            "A_ISW_original": self.A_ISW_original,
            "A_ISW_revised": self.A_ISW_revised,
            "original_status": self.original_status,
            "suppression_original_percent": self.suppression_original,
            "suppression_revised_percent": self.suppression_revised
        }


class RevisedISWPredictions:
    """
    Revised ISW predictions following the Consistency Audit.

    Key changes:
    - A_ISW is nearly z-independent (0.87–0.92)
    - Suppression is ~11% relative to ΛCDM, not 44–85%
    - Cancellation metric C is not applicable under growth-driven ISW
    """

    def __init__(self):
        self._predictions = self._load_predictions()
        self.mu_params = MuParameters()

    def _load_predictions(self) -> Dict[str, TracerPrediction]:
        """Load revised predictions from Table 2."""
        data = [
            ("LRGz0", 0.510, 0.56, 0.87),
            ("LRGz1", 0.706, 0.43, 0.87),
            ("LRGz2", 0.930, 0.33, 0.89),
            ("LRG+ELG", 0.930, 0.29, 0.89),
            ("ELG", 1.317, 0.15, 0.92),
            ("QSO", 1.491, 0.20, 0.90),
        ]

        predictions = {}
        for name, z_eff, A_orig, A_rev in data:
            predictions[name] = TracerPrediction(
                name=name,
                z_eff=z_eff,
                A_ISW_original=A_orig,
                A_ISW_revised=A_rev
            )
        return predictions

    @property
    def tracers(self) -> List[str]:
        """List of tracer names."""
        return list(self._predictions.keys())

    def get_original(self, tracer: str) -> float:
        """Get original (withdrawn) A_ISW value."""
        return self._predictions[tracer].A_ISW_original

    def get_revised(self, tracer: str) -> float:
        """Get revised A_ISW value."""
        return self._predictions[tracer].A_ISW_revised

    def get_prediction(self, tracer: str) -> TracerPrediction:
        """Get full prediction for a tracer."""
        return self._predictions[tracer]

    @property
    def mean_revised(self) -> float:
        """Mean revised A_ISW across all tracers."""
        return np.mean([p.A_ISW_revised for p in self._predictions.values()])

    @property
    def std_revised(self) -> float:
        """Standard deviation of revised A_ISW."""
        return np.std([p.A_ISW_revised for p in self._predictions.values()])

    def summary(self) -> Dict:
        """
        Get summary of revised predictions.

        Returns
        -------
        Dict
            Summary statistics
        """
        revised_values = [p.A_ISW_revised for p in self._predictions.values()]
        original_values = [p.A_ISW_original for p in self._predictions.values()]

        return {
            "A_ISW_revised_mean": np.mean(revised_values),
            "A_ISW_revised_std": np.std(revised_values),
            "A_ISW_revised_range": [min(revised_values), max(revised_values)],
            "A_ISW_original_mean": np.mean(original_values),
            "A_ISW_original_range": [min(original_values), max(original_values)],
            "suppression_revised_percent": (1 - np.mean(revised_values)) * 100,
            "suppression_original_percent": (1 - np.mean(original_values)) * 100,
            "z_dependence": "negligible" if np.std(revised_values) < 0.05 else "significant"
        }

    def comparison_table(self) -> str:
        """
        Generate comparison table of original vs revised predictions.

        Returns
        -------
        str
            Formatted table
        """
        lines = [
            "Tracer    z_eff   Original  Revised   Change",
            "-" * 50
        ]

        for tracer in self.tracers:
            p = self._predictions[tracer]
            change = p.A_ISW_revised - p.A_ISW_original
            lines.append(
                f"{p.name:8s}  {p.z_eff:.3f}   {p.A_ISW_original:.2f}      "
                f"{p.A_ISW_revised:.2f}      {change:+.2f}"
            )

        return "\n".join(lines)


class ChannelComparison:
    """
    Compare growth-driven and potential-driven ISW channels.

    The key insight from the Audit is that these give qualitatively
    different predictions that distinguish EFC interpretations.
    """

    def __init__(self):
        self.mu_params = MuParameters()
        self._growth_driven_A = 0.89
        self._growth_driven_uncertainty = 0.03

    @property
    def growth_driven(self) -> float:
        """Growth-driven A_ISW prediction."""
        return self._growth_driven_A

    @property
    def growth_driven_uncertainty(self) -> float:
        """Uncertainty on growth-driven prediction."""
        return self._growth_driven_uncertainty

    def potential_driven_prediction(self, z_eff: float) -> str:
        """
        Potential-driven prediction at given redshift.

        Parameters
        ----------
        z_eff : float
            Effective redshift

        Returns
        -------
        str
            Qualitative prediction
        """
        if z_eff >= 0.6:
            return "Anti-correlation (A < 0)"
        else:
            return "Positive but enhanced"

    def comparison_summary(self) -> Dict:
        """
        Summary comparison of channels.

        Returns
        -------
        Dict
            Channel comparison
        """
        return {
            "growth_driven": {
                "potential_relation": "Φ ∝ D(a)/a",
                "mu_role": "μ affects ISW only through D(a) and f(a)",
                "isw_source": "S ∝ H(a)(D/a)(1-f)",
                "A_ISW": f"{self._growth_driven_A:.2f} ± {self._growth_driven_uncertainty:.2f}",
                "z_dependence": "negligible",
                "cancellation_metric": "not applicable"
            },
            "potential_driven": {
                "potential_relation": "Φ ∝ μ(a)·D(a)/a",
                "additional_term": "dμ/d ln a in ISW kernel",
                "prediction_low_z": "Positive A_ISW",
                "prediction_high_z": "Anti-correlation (A < 0) for z > 0.6",
                "status": "Disfavoured by positive ISW detections"
            }
        }


@dataclass
class FalsificationCriteria:
    """
    Revised falsification criteria for EFC ISW predictions.
    """

    # Revised criteria
    exclusion_threshold: float = 1.00
    exclusion_uncertainty: float = 0.05
    exclusion_significance: str = "> 2σ"

    # Positive evidence
    positive_evidence_threshold: float = 0.9

    # Original criteria (now deprecated)
    original_C_threshold: float = 0.7
    original_A_threshold: float = 0.5

    def is_excluded(self, A_ISW_observed: float, uncertainty: float) -> Tuple[bool, str]:
        """
        Check if EFC is excluded by observation.

        Parameters
        ----------
        A_ISW_observed : float
            Observed A_ISW value
        uncertainty : float
            Measurement uncertainty

        Returns
        -------
        Tuple[bool, str]
            (excluded, explanation)
        """
        if abs(A_ISW_observed - 1.0) < self.exclusion_uncertainty + uncertainty:
            return True, f"A_ISW = {A_ISW_observed:.2f} ± {uncertainty:.2f} consistent with ΛCDM; EFC excluded at {self.exclusion_significance}"
        return False, "EFC not excluded"

    def is_positive_evidence(self, A_ISW_observed: float) -> Tuple[bool, str]:
        """
        Check if observation provides positive evidence for EFC.

        Parameters
        ----------
        A_ISW_observed : float
            Observed A_ISW value

        Returns
        -------
        Tuple[bool, str]
            (positive_evidence, explanation)
        """
        if A_ISW_observed < self.positive_evidence_threshold:
            return True, f"A_ISW = {A_ISW_observed:.2f} < 0.9 constitutes positive evidence for EFC"
        return False, "No positive evidence (within ΛCDM expectations)"

    def summary(self) -> Dict:
        """Get summary of falsification criteria."""
        return {
            "revised": {
                "exclusion": f"A_ISW = {self.exclusion_threshold:.2f} ± {self.exclusion_uncertainty:.2f} across all bins",
                "exclusion_level": self.exclusion_significance,
                "positive_evidence": f"A_ISW < {self.positive_evidence_threshold:.1f} across multiple bins",
                "key_discriminator": "Uniform 11% suppression in multi-tracer stack"
            },
            "original_deprecated": {
                "C_threshold": self.original_C_threshold,
                "A_threshold": self.original_A_threshold,
                "note": "No longer applicable under growth-driven interpretation"
            }
        }


class ValidationLedgerUpdate:
    """
    Track validation ledger changes from v1.6 to v1.7.
    """

    @staticmethod
    def changes() -> Dict:
        """Get ledger changes."""
        return {
            "version_from": "v1.6",
            "version_to": "v1.7",
            "field_changes": {
                "Status": {
                    "from": "Completed (no observational conflict)",
                    "to": "Under revision"
                },
                "A_ISW": {
                    "from": "0.29–0.56 (bias-calibrated)",
                    "to": "0.87–0.92 (growth-driven, self-consistent)"
                },
                "C": {
                    "from": "0.59–0.96",
                    "to": "Not applicable (growth-driven)"
                },
                "Falsification": {
                    "from": "C > 0.7, A < 0.5 at z_t",
                    "to": "A_ISW = 1.00 ± 0.05 across all bins"
                },
                "Key_discriminator": {
                    "from": "Tomographic C gradient",
                    "to": "Uniform 11% suppression in multi-tracer stack"
                }
            }
        }


# Convenience functions
def get_revised_prediction(tracer: str) -> float:
    """Get revised A_ISW for a tracer."""
    return RevisedISWPredictions().get_revised(tracer)


def get_all_predictions() -> Dict[str, float]:
    """Get all revised predictions."""
    pred = RevisedISWPredictions()
    return {t: pred.get_revised(t) for t in pred.tracers}


def check_falsification(A_ISW_observed: float, uncertainty: float = 0.05) -> str:
    """Check falsification status."""
    criteria = FalsificationCriteria()
    excluded, msg = criteria.is_excluded(A_ISW_observed, uncertainty)
    if excluded:
        return msg
    positive, msg = criteria.is_positive_evidence(A_ISW_observed)
    return msg


if __name__ == "__main__":
    # Quick demonstration
    print("ISW Revision Patch - Quick Summary")
    print("=" * 50)

    predictions = RevisedISWPredictions()
    print(predictions.comparison_table())

    print("\n" + "=" * 50)
    summary = predictions.summary()
    print(f"Revised mean A_ISW: {summary['A_ISW_revised_mean']:.2f} ± {summary['A_ISW_revised_std']:.2f}")
    print(f"Suppression: {summary['suppression_revised_percent']:.1f}%")
    print(f"z-dependence: {summary['z_dependence']}")
