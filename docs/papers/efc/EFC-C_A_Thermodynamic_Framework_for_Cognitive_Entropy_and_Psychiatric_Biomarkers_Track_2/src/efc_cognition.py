"""EFC-C: Cognitive Entropy — Python implementation.

Models the brain as an open thermodynamic system with entropy-gradient
dynamics. Produces S_dot_neural (scalar biomarker) and nabla S_dot
(gradient tensor) for psychiatric classification.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940505
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class NeuralEntropyProduction:
    """Total neural entropy production rate S_dot_neural. Eq. (1).

    S_dot_neural = sum_i integral(s_dot_i dV) over regions R_i

    Attributes:
        region_names: Names of brain regions.
        s_dot_values: Entropy production rate density for each region.
    """
    region_names: List[str] = field(default_factory=list)
    s_dot_values: List[float] = field(default_factory=list)

    @property
    def s_dot_neural(self) -> float:
        """Total neural entropy production rate."""
        return sum(self.s_dot_values)

    def regional_fractions(self) -> Dict[str, float]:
        """Fraction of total entropy produced by each region."""
        total = self.s_dot_neural
        if total == 0:
            return {}
        return {name: s / total for name, s in zip(self.region_names, self.s_dot_values)}

    def hub_periphery_ratio(self, hub_regions: List[str], periph_regions: List[str]) -> float:
        """Compute hub-to-periphery entropy ratio (analogous to kappa)."""
        region_map = dict(zip(self.region_names, self.s_dot_values))
        hub_mean = sum(region_map.get(r, 0) for r in hub_regions) / max(len(hub_regions), 1)
        periph_mean = sum(region_map.get(r, 0) for r in periph_regions) / max(len(periph_regions), 1)
        return hub_mean / periph_mean if periph_mean > 0 else float('inf')


@dataclass
class EntropyGradient:
    """Entropy gradient tensor nabla S_dot.

    Encodes the directional structure of entropy flow across the connectome.
    """
    source_regions: List[str] = field(default_factory=list)
    target_regions: List[str] = field(default_factory=list)
    gradient_values: List[float] = field(default_factory=list)

    def net_flow_direction(self) -> str:
        """Determine dominant flow direction."""
        pos = sum(1 for g in self.gradient_values if g > 0)
        neg = sum(1 for g in self.gradient_values if g < 0)
        if pos > neg:
            return "centrifugal (hub -> periphery)"
        elif neg > pos:
            return "centripetal (periphery -> hub)"
        return "balanced"


@dataclass
class CentrifugalGradient:
    """Prediction P1: Centrifugal entropy gradient.

    Entropy production highest in integrative hub regions (DMN, salience)
    and flows directionally toward primary sensory cortices.
    """

    @staticmethod
    def healthy_gradient() -> Dict[str, float]:
        """Expected relative entropy production in healthy resting state."""
        return {
            "DMN (mPFC, PCC)": 1.0,
            "Salience (aINS, dACC)": 0.85,
            "Frontoparietal (dlPFC)": 0.75,
            "Attention (IPS, FEF)": 0.60,
            "Sensorimotor (M1, S1)": 0.40,
            "Primary visual (V1)": 0.30,
            "Primary auditory (A1)": 0.30,
        }

    @staticmethod
    def empirical_support() -> List[str]:
        return [
            "Lempel-Ziv complexity highest in association cortices and DMN (Rosas+ 2023)",
            "MSE at coarse scales highest in DMN hubs",
            "Brain entropy positively correlated with intelligence in association cortices",
            "Centrifugal entropy score kappa > 1 across 6 atlases (Magnusson 2026, 31940370)",
        ]


@dataclass
class DisorderSignature:
    """Prediction P2: Disorder-specific gradient signatures.

    Psychiatric disorders correspond to characteristic deformations of
    the healthy centrifugal gradient: Delta nabla S = nabla S_patient - nabla S_healthy.
    """
    disorder: str
    gradient_deviation: Dict[str, float] = field(default_factory=dict)
    observed_evidence: str = ""

    @staticmethod
    def schizophrenia() -> 'DisorderSignature':
        return DisorderSignature(
            disorder="Schizophrenia",
            gradient_deviation={
                "Frontal (anterior)": +0.3,
                "DMN hubs": -0.2,
                "Temporal": +0.1,
                "Sensorimotor": 0.0,
            },
            observed_evidence="Increased frontal MFE, prefrontal-temporal dysconnection (Noroozi+ 2025)"
        )

    @staticmethod
    def mdd() -> 'DisorderSignature':
        return DisorderSignature(
            disorder="Major Depressive Disorder",
            gradient_deviation={
                "Frontal (left)": -0.3,
                "DMN hubs": -0.1,
                "Posterior": +0.2,
                "Sensorimotor": 0.0,
            },
            observed_evidence="Lower MSE in left frontal, reduced EEG microstate complexity (Pan+ 2025)"
        )

    @staticmethod
    def adhd() -> 'DisorderSignature':
        return DisorderSignature(
            disorder="ADHD",
            gradient_deviation={
                "Frontal": -0.1,
                "DMN hubs": -0.2,
                "Attention": +0.1,
                "Sensorimotor": +0.1,
            },
            observed_evidence="Fragmented gradient topology (predicted; not yet directly tested)"
        )

    def gradient_type(self) -> str:
        """Classify the type of gradient deformation."""
        anterior = sum(v for k, v in self.gradient_deviation.items() if "Front" in k or "anterior" in k)
        posterior = sum(v for k, v in self.gradient_deviation.items() if "Post" in k or "Temporal" in k)
        if anterior > 0.1:
            return "Anterior excess (elevated frontal entropy)"
        elif posterior > 0.1:
            return "Posterior bias"
        else:
            return "Fragmented topology"


@dataclass
class EntropyThreshold:
    """Prediction P3: Entropy threshold S_dot* for cognitive function.

    Onset of productive cognition requires S_dot_neural > S_dot_star.
    Below threshold, coordinated cognition degrades.
    """
    s_dot_star: float = 0.0  # System-dependent; derivable from connectivity matrices

    def is_above_threshold(self, s_dot_neural: float) -> bool:
        return s_dot_neural > self.s_dot_star

    def cognitive_state(self, s_dot_neural: float) -> str:
        if s_dot_neural > self.s_dot_star * 1.5:
            return "Enhanced (e.g. psychedelic, flow state)"
        elif s_dot_neural > self.s_dot_star:
            return "Normal waking consciousness"
        elif s_dot_neural > self.s_dot_star * 0.5:
            return "Reduced (drowsy, sedated)"
        else:
            return "Unresponsive / minimal consciousness"

    @staticmethod
    def empirical_support() -> str:
        return "Loss of Lempel-Ziv complexity below critical level reliably predicts unresponsive states (Carhart-Harris 2018)"


@dataclass
class FrameworkComparison:
    """Comparison of EFC-C with EBH, FEP, and IIT (Table 1)."""

    @staticmethod
    def comparison_table() -> List[Dict]:
        return [
            {"framework": "EBH", "magnitude": True, "topology": False, "gradient_dir": False, "psychiatric": "Partial"},
            {"framework": "Free Energy Principle", "magnitude": "Implicit", "topology": False, "gradient_dir": False, "psychiatric": "Indirect"},
            {"framework": "IIT", "magnitude": False, "topology": True, "gradient_dir": False, "psychiatric": "Indirect"},
            {"framework": "EFC-C", "magnitude": True, "topology": True, "gradient_dir": True, "psychiatric": "Direct"},
        ]

    @staticmethod
    def key_distinction() -> str:
        return "EBH is the scalar projection of the more complete EFC-C tensor field. EFC-C adds gradient direction and topology as measurable quantities."


# Convenience functions
def compute_s_dot_neural(s_dot_values: List[float]) -> float:
    """Compute total neural entropy production rate."""
    return sum(s_dot_values)

def compute_gradient_deviation(patient_values: List[float], healthy_values: List[float]) -> List[float]:
    """Compute Delta nabla S = nabla S_patient - nabla S_healthy. Eq. (2)."""
    return [p - h for p, h in zip(patient_values, healthy_values)]
