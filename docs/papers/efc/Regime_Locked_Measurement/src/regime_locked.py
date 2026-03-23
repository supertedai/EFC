"""
Regime-Locked Measurement — Reference Implementation

Formal framework, blind-set taxonomy, alpha-score, meta-regime protocol,
six-domain demonstration, and falsification criteria.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Date: March 2026
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set


# =============================================================================
# Formal Framework (Section 2)
# =============================================================================

@dataclass
class Regime:
    """A regime R = (I, V, B, G) — Eq. (1)."""
    instrument: str
    validity_domain: str
    blind_set: List[str] = field(default_factory=list)
    gradient_sensitivity: str = ""

    def is_regime_locked(self, phenomenon: str) -> bool:
        """True if phenomenon is in validity domain."""
        return phenomenon in self.validity_domain


class RegimeAppropriateness:
    """Alpha-score: alpha(phi, R) = |phi ∩ V(R)| / |phi| in [0,1] — Eq. (3).

    In practice, alpha is estimated via proxies:
    - Residual structure fraction
    - Cross-regime recovery rate
    - Bayesian evidence ratio
    """
    @staticmethod
    def alpha(phi_in_V: float, phi_total: float) -> float:
        """Compute alpha score."""
        if phi_total <= 0:
            return 0.0
        return min(1.0, max(0.0, phi_in_V / phi_total))

    @staticmethod
    def best_regime(alphas: dict) -> str:
        """arg max_i alpha(phi, R_i)."""
        return max(alphas, key=alphas.get)

    @staticmethod
    def estimation_methods() -> list:
        return [
            "Residual structure fraction (higher -> lower alpha)",
            "Cross-regime recovery rate (higher -> more complete)",
            "Bayesian evidence ratio (log-Bayes factor)",
        ]


# =============================================================================
# Blind-Set Taxonomy (Section 2.2, Table 2)
# =============================================================================

@dataclass
class BlindSetType:
    """One type from the blind-set taxonomy."""
    code: str
    name: str
    character: str
    detection_strategy: str


BLIND_SET_TYPES = [
    BlindSetType("B_ont", "Ontological",
                 "Phenomenon outside instrument's physical reach",
                 "Requires fundamentally new instrument class"),
    BlindSetType("B_meth", "Methodological",
                 "Phenomenon excluded by framework assumptions",
                 "Cross-regime comparison; assumption audit"),
    BlindSetType("B_inst", "Instrumental",
                 "Phenomenon within reach but below sensitivity",
                 "Instrument upgrade; residual analysis"),
]


class BlindSetTaxonomy:
    """Three-type blind-set taxonomy (Table 2)."""
    def __init__(self):
        self.types = BLIND_SET_TYPES

    def get(self, code: str) -> Optional[BlindSetType]:
        for t in self.types:
            if t.code == code:
                return t
        return None

    def print_table(self):
        lines = [
            "Blind-Set Taxonomy (Table 2)",
            "=" * 70,
            f"{'Type':<10} {'Character':<35} {'Detection Strategy'}",
            "-" * 70,
        ]
        for t in self.types:
            lines.append(f"{t.code:<10} {t.character:<35} {t.detection_strategy}")
        return "\n".join(lines)


# =============================================================================
# Cross-Domain Demonstration (Section 3, Table 3)
# =============================================================================

@dataclass
class DomainDemo:
    """One domain from the six-domain demonstration."""
    domain: str
    instrument_sees: str
    instrument_misses: str
    b_type: str
    residual_signal: str


DOMAIN_DEMOS = [
    DomainDemo("Cosmology", "Model-predicted signals", "Alternative mechanisms", "meth",
               "Hubble tension as structured residual"),
    DomainDemo("AI Alignment", "Deviation from norms", "Convergence drift", "meth",
               "Persistent high-quality outputs not flagged"),
    DomainDemo("Cyber Security", "Known signatures", "Regime-boundary exploits", "meth",
               "SolarWinds, Stuxnet exploited trusted zones"),
    DomainDemo("Intelligence", "In-scope threats", "Out-of-doctrine threats", "meth",
               "Pre-9/11 cross-agency signals in each B"),
    DomainDemo("Economics", "In-regime behaviour", "Regime transitions", "inst",
               "2008 crisis: low-vol calibration blind at boundary"),
    DomainDemo("Consciousness", "Neural correlates", "Subjective experience", "ont",
               "Hard problem (Chalmers 1995)"),
]


class CrossDomainDemos:
    """Six-domain demonstration (Table 3)."""
    def __init__(self):
        self.demos = DOMAIN_DEMOS

    def summary(self):
        lines = [
            "Six-Domain Demonstration (Table 3)",
            "=" * 80,
            f"{'Domain':<16} {'Sees':<22} {'Misses':<24} {'B type'}",
            "-" * 80,
        ]
        for d in self.demos:
            lines.append(f"{d.domain:<16} {d.instrument_sees:<22} {d.instrument_misses:<24} {d.b_type}")
        return "\n".join(lines)


class CDVCAssessment:
    """Cross-Disciplinary Vector Convergence (Section 2.5, Eq. 4)."""
    def __init__(self):
        self.n_domains = 6
        self.threshold = 3

    def is_cdvc(self) -> bool:
        return self.n_domains >= self.threshold

    def conditions(self) -> list:
        return [
            "Independent generation: pattern from domain-specific mechanisms",
            "Predictive content: generates falsifiable predictions in >= 1 domain",
        ]

    def alternative(self) -> str:
        return "Shared cognitive bias (humans frame as seen vs unseen)"


# =============================================================================
# Meta-Regime Protocol (Section 4, Algorithm 1)
# =============================================================================

PROTOCOL_STEPS = [
    (1, "Regime Identification", "Characterise R = (I, V, B, G)"),
    (2, "Blind Set Elicitation", "Enumerate B_known; classify as B_ont/B_meth/B_inst"),
    (3, "Cross-Regime Check", "For each b in B_i, test if b in V_j for some j != i"),
    (4, "Residual Analysis", "Test residuals for structure -> B_inferred candidates"),
    (5, "Alpha-Scoring", "Estimate alpha; flag if below threshold; report B types"),
]


class MetaRegimeProtocol:
    """Five-step meta-regime evaluation protocol (Algorithm 1)."""
    def __init__(self):
        self.steps = PROTOCOL_STEPS

    def summary(self):
        lines = ["Meta-Regime Protocol (Algorithm 1)", "=" * 60]
        for num, name, action in self.steps:
            lines.append(f"  Step {num}: {name}")
            lines.append(f"          {action}")
        return "\n".join(lines)

    def worked_example_ai(self):
        return "\n".join([
            "Worked Example: AI Alignment",
            "=" * 50,
            "Step 1: Deviation-detection regime. V: violations. B: convergence drift.",
            "Step 2: B_known = convergence drift (B_meth). Detection: paradigm switch.",
            "Step 3: Detectable from interpretability regime (mechanistic probes).",
            "Step 4: Persistent high-quality responses -> B_inferred candidates.",
            "Step 5: alpha ~ 0.5-0.7 (heuristic). Gap closeable by paradigm expansion.",
        ])


# =============================================================================
# Falsification Criteria (Section 5)
# =============================================================================

FALSIFICATION = {
    "framework": [
        "B = empty demonstrated (no blind spots across boundaries)",
        "Six-domain convergence from shared methodological artefact",
    ],
    "protocol": [
        "Fails to detect planted blind spots in controlled setting",
        "Alpha fails to discriminate known-different regimes",
    ],
    "conjecture": [
        "General method reliably distinguishes S0/S1 from output alone",
    ],
}


# =============================================================================
# S0/S1 Conjecture (Section 2.8)
# =============================================================================

@dataclass
class S0S1Conjecture:
    """S0/S1 observational equivalence conjecture."""
    status: str = "Conjecture (open)"
    description: str = "At gradient extremes, different generative processes produce indistinguishable outputs"
    ai_s0: str = "Deep framework integration (high internal coherence)"
    ai_s1: str = "Superficial linguistic mirroring (high surface match, no coherence)"
    connection: str = "Identifiability problem in inverse problems / latent-variable models"
    resolution_approaches: list = field(default_factory=lambda: [
        "Additional observables that break the symmetry",
        "Mechanistic probes of generative process (interpretability/spectroscopy)",
    ])
