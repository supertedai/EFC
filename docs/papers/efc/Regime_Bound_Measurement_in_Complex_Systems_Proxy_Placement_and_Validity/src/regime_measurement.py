"""
Regime-Bound Measurement in Complex Systems — Reference Implementation

Five operative concepts, nine theses, 13 testable predictions,
two case studies (cosmology + AI evaluation).

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Date: Working paper — March 7, 2026
"""

from dataclasses import dataclass, field
from typing import List, Optional


# =============================================================================
# Core Concepts (Section 2)
# =============================================================================

@dataclass
class CoreConcept:
    """One of the five operative concepts."""
    name: str
    definition: str
    failure_mode: str
    test: str
    cosmology_example: str = ""
    ai_example: str = ""


CORE_CONCEPTS = [
    CoreConcept(
        "Regime",
        "Bounded domain where consistent inferential rules hold",
        "Conflation: pooling across regime boundaries",
        "Residuals by regime differ significantly",
        "FLOW/TRANSITION/LATENT over S-hat(z)",
        "Formal academic vs conversational/adversarial inputs",
    ),
    CoreConcept(
        "Proxy",
        "Mediating variable with defined visibility and declared blindness",
        "Opacity: treating proxy as direct read",
        "Proxy substitution produces systematic drift",
        "S-hat(z): blind to local environments",
        "BLEU: blind to semantic adequacy, pragmatic coherence",
    ),
    CoreConcept(
        "Placement",
        "Position across physical, instrument, interpretive space",
        "Incompatibility: comparing across placement dimensions",
        "Placement-matching reduces apparent conflict",
        "CMB (z~1100) vs SNIa (z<0.1): all three dimensions incompatible",
        "Human rater vs automated metric",
    ),
    CoreConcept(
        "Episenter",
        "Weighted privileged variables organising what appears central",
        "Universalism: undeclared single episenter",
        "Episenter shift produces structured redistribution",
        "z-space vs S-space: different residual structures",
        "Accuracy vs calibration error: different model rankings",
    ),
    CoreConcept(
        "Compression",
        "Structural reduction from phenomenon to output",
        "Neglect: scalar treated as complete representation",
        "Lost dimensions have predictable footprint",
        "P(k) discards phase information",
        "Scalar benchmark score discards variance, tail behaviour",
    ),
]


class CoreConcepts:
    """Container for the five operative concepts (Table 1)."""
    def __init__(self):
        self.concepts = CORE_CONCEPTS

    def get(self, name: str) -> Optional[CoreConcept]:
        for c in self.concepts:
            if c.name.lower() == name.lower():
                return c
        return None

    def structural_chain(self) -> list:
        return [
            ("regime", "scope"),
            ("proxy + placement", "access"),
            ("episenter", "organisation"),
            ("compression", "reduction"),
            ("output", "observed datum"),
        ]

    def print_reference_table(self):
        lines = [
            "Five Core Concepts (Table 1)",
            "=" * 80,
            f"{'Concept':<14} {'Definition':<40} {'Failure Mode':<30}",
            "-" * 80,
        ]
        for c in self.concepts:
            lines.append(f"{c.name:<14} {c.definition[:40]:<40} {c.failure_mode[:30]:<30}")
        lines.append("")
        lines.append("Structural chain:")
        chain = " -> ".join(f"{step} ({role})" for step, role in self.structural_chain())
        lines.append(f"  {chain}")
        return "\n".join(lines)


# =============================================================================
# Theses and Derived Predictions (Section 3)
# =============================================================================

NINE_THESES = [
    "Measurement is not direct readout",
    "Proxy creates both visibility and blindness",
    "Measurement placement is a primary question",
    "Episenter is produced, not given",
    "Conflicts may be regime conflicts",
    "Validity is regime-conditioned",
    "Analysis of the analysis is part of the analysis",
    "Measurement is compression",
    "A fragment carries holistic structure under four conditions",
]

FIVE_PREDICTIONS = [
    ("P1", "Consistent response at shared coordinates"),
    ("P2", "Systematic proxy-substitution drift"),
    ("P3", "Regime-resolution of conflicts"),
    ("P4", "Cartographic null results"),
    ("P5", "Episenter-shift redistribution"),
]


# =============================================================================
# Prediction Register (Section 8)
# =============================================================================

@dataclass
class Prediction:
    """One entry from the 13-prediction register (Table 8)."""
    id: str
    domain: str
    prediction: str
    status: str
    test_protocol: str = ""
    current_evidence: str = ""


PREDICTION_REGISTER = [
    Prediction("C1", "Cosmology", "Probe consistency at (k,S)", "PARTIAL",
               "Map DESI DR2 + f sigma8 onto (k,S)", "p=0.020, N=10, secondary"),
    Prediction("C2", "Cosmology", "Proxy substitution drift direction", "Pending",
               "S-hat(z) vs morphology proxy on SDSS/GAMA"),
    Prediction("C3", "Cosmology", "Boundary clustering (primary)", "ACTIVE",
               "Axiom 0 v2 on DESI Year-5 (N>=30)", "DESI z=1.0 dist=0.000 (anecdotal)"),
    Prediction("C4", "Cosmology", "H0 within-regime variance", "ACTIVE",
               "Stratify H0 by S-hat-regime"),
    Prediction("C5", "Cosmology", "LATENT residual sign coherence", "PARTIAL",
               "Runs-test + sign-coherence + variance ratio", "8/9 positive"),
    Prediction("C6", "Cosmology", "Proxy divergence at TRANSITION", "Pending",
               "Matched model pairs on chi2_BAO"),
    Prediction("A1", "AI", "Boundary variance increase", "Meth.",
               "Sample at graduated OOD distance"),
    Prediction("A2", "AI", "Episenter shift redistribution", "Meth.",
               "Accuracy vs calibration error on MMLU"),
    Prediction("A3", "AI", "Cross-regime rank correlation", "ACTIVE",
               "MMLU vs MT-Bench/adversarial NLI"),
    Prediction("A4", "AI", "Explainability-validity decoupling", "Meth.",
               "SHAP coherence vs OOD performance"),
    Prediction("A5", "AI", "Validity profile utility", "Pending",
               "Production incident dataset"),
    Prediction("F1", "Both", "Proxy drift directionality", "ACTIVE",
               "Proxy swap experiments both domains"),
    Prediction("F2", "Both", "Regime-ID resolution frequency", "Meth.",
               "Systematic conflict taxonomy"),
]


class PredictionRegister:
    """Complete prediction register (13 predictions, Table 8)."""
    def __init__(self):
        self.predictions = PREDICTION_REGISTER

    def by_domain(self, domain: str) -> list:
        return [p for p in self.predictions if p.domain == domain]

    def by_status(self, status: str) -> list:
        return [p for p in self.predictions if p.status == status]

    def summary(self):
        lines = [
            "Prediction Register (13 predictions)",
            "=" * 70,
            f"{'ID':<5} {'Domain':<10} {'Prediction':<40} {'Status':<8}",
            "-" * 70,
        ]
        for p in self.predictions:
            lines.append(f"{p.id:<5} {p.domain:<10} {p.prediction:<40} {p.status:<8}")
        lines.append("-" * 70)
        counts = {}
        for p in self.predictions:
            counts[p.status] = counts.get(p.status, 0) + 1
        lines.append("Status counts: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
        return "\n".join(lines)


# =============================================================================
# Case 1: Cosmology — Axiom 0 Results (Section 4)
# =============================================================================

@dataclass
class AxiomZeroResults:
    """Axiom 0 test results (Table 3)."""
    n_data: int = 10
    primary_statistic: str = "Mean distance to nearest regime boundary"
    primary_p: float = 1.0
    primary_interpretation: str = "Degenerate: deterministic mapping with N=10"
    secondary_statistic: str = "Sign coherence (TRANSITION + LATENT)"
    sign_coherence_p: float = 0.020
    sign_coherence_count: str = "8/9 positive"
    secondary_interpretation: str = "Consistent with EFC but not confirmatory"

    def notable_points(self) -> list:
        return [
            {"point": "DESI z=1.0", "distance": 0.000, "note": "Exactly on FLOW/TRANSITION boundary"},
            {"point": "eBOSS LRG z=0.51", "distance": 0.019, "note": "2.0 sigma"},
            {"point": "f sigma8 z=0.7", "distance": None, "note": "2.0 sigma, in TRANSITION regime"},
        ]

    def summary(self):
        lines = [
            "Axiom 0 Test Results (Table 3)",
            "=" * 50,
            f"N = {self.n_data} BAO deviations",
            f"Primary: {self.primary_statistic}",
            f"  p = {self.primary_p} ({self.primary_interpretation})",
            f"Secondary: {self.secondary_statistic}",
            f"  p = {self.sign_coherence_p} ({self.sign_coherence_count})",
            "Notable:",
        ]
        for pt in self.notable_points():
            d = f"dist={pt['distance']}" if pt['distance'] is not None else ""
            lines.append(f"  {pt['point']}: {d} {pt['note']}")
        return "\n".join(lines)


# =============================================================================
# Case 1: EFC Structural Regimes
# =============================================================================

@dataclass
class EFCRegime:
    """One EFC structural regime (Table 2)."""
    name: str
    tertile: str
    character: str
    expected_response: str


EFC_REGIMES = [
    EFCRegime("FLOW", "Bottom", "High rho_SFR; active energy redistribution", "High response amplitude, higher variance"),
    EFCRegime("TRANSITION", "Middle", "Near-boundary dynamics; moderate rho_SFR", "Intermediate; high boundary sensitivity"),
    EFCRegime("LATENT", "Top", "Low rho_SFR; suppressed response", "Near-null signal; coherent sign structure"),
]


# =============================================================================
# Case 1: Hubble Tension Placement Analysis (Table 4)
# =============================================================================

@dataclass
class PlacementConfig:
    """Placement configuration for one H0 measurement."""
    name: str
    z: str
    regime: str
    instrument: str
    interpretive: str
    compression: str


HUBBLE_PLACEMENTS = [
    PlacementConfig("CMB", "z ~ 1100", "FLOW", "CMB anisotropy power spectrum",
                    "FLRW extrapolation from z=1100", "Full CMB power spectrum -> H0"),
    PlacementConfig("SNIa", "z < 0.1", "LATENT", "SNIa distance modulus ladder",
                    "Local calibration + FLRW", "Full distance ladder -> H0"),
]


# =============================================================================
# Case 2: AI Evaluation Metrics (Table 6)
# =============================================================================

@dataclass
class AIMetricProxy:
    """Proxy structure of an AI evaluation metric (Table 6)."""
    metric: str
    target: str
    visibility: str
    blindness: str


AI_METRIC_PROXIES = [
    AIMetricProxy("BLEU/ROUGE", "Translation/summarisation quality",
                  "n-gram overlap; reliable in formal single-reference regimes",
                  "Semantic adequacy, pragmatic coherence, multi-reference validity"),
    AIMetricProxy("Accuracy/F1", "Classification correctness",
                  "Mean correctness on i.i.d. held-out set",
                  "Calibration, tail behaviour, failure mode distribution, OOD performance"),
    AIMetricProxy("Perplexity", "LM quality",
                  "Log-likelihood on test set; sensitive to distributional fit",
                  "Downstream task performance, factual accuracy, long-context coherence"),
    AIMetricProxy("Human preference", "Overall output quality",
                  "Captures pragmatic and contextual quality; regime-flexible",
                  "Rater variance, annotation protocol dependence, demographic coverage"),
    AIMetricProxy("SHAP/attention", "Feature attribution (explainability)",
                  "Local attribution for single inference; mechanistically informative",
                  "Global validity, calibration, cross-regime reliability, output accuracy"),
]


# =============================================================================
# Validity Profile (Section 5.7)
# =============================================================================

@dataclass
class ValidityProfile:
    """Validity-aware evaluation profile."""
    model: str = ""
    evaluation_regime: str = ""
    primary_metric: str = ""
    proxy_target: str = ""
    declared_blindness: list = field(default_factory=list)
    regime_validity: str = ""
    transfer_validity: str = "unknown"
    episenter: str = ""
    alternatives_assessed: list = field(default_factory=list)
    compression_loss: list = field(default_factory=list)

    def template(self):
        return "\n".join([
            "Validity Profile (minimal structure)",
            "=" * 50,
            f"Model: {self.model or '[identifier]'}",
            f"Evaluation regime: {self.evaluation_regime or '[input dist + task + annotation + deployment]'}",
            f"Primary metric: {self.primary_metric or '[name]'} — proxy for {self.proxy_target or '[target]'}",
            f"  Declared blindness: {', '.join(self.declared_blindness) or '[list]'}",
            f"Regime-validity: {self.regime_validity or 'valid within specified regime'}",
            f"Transfer validity: {self.transfer_validity}",
            f"Episenter: {self.episenter or '[primary metric]'}",
            f"  Alternatives: {', '.join(self.alternatives_assessed) or '[list with divergence]'}",
            f"Compression loss: {', '.join(self.compression_loss) or '[list of dimensions not captured]'}",
        ])


# =============================================================================
# Structural Chain
# =============================================================================

class StructuralChain:
    """The core structural chain (Section 2.7)."""
    STEPS = [
        ("regime", "scope", "All other concepts are regime-scoped"),
        ("proxy + placement", "access", "Proxy implements placement; changes available proxy set"),
        ("episenter", "organisation", "Organises what compression retains"),
        ("compression", "reduction", "Produces observed output"),
        ("output", "observed datum", "Product of structured chain of mediation"),
    ]

    def display(self):
        parts = [f"{step} ({role})" for step, role, _ in self.STEPS]
        return " -> ".join(parts)

    def detail(self):
        lines = ["Structural Chain (Section 2.7)", "=" * 60]
        for step, role, desc in self.STEPS:
            lines.append(f"  {step:<22} [{role}] {desc}")
        return "\n".join(lines)


# =============================================================================
# Framework-Breaking Outcomes (Section 8.4)
# =============================================================================

FBREAK = [
    ("F-BREAK 1", "Regime-random residuals", "Regime structure hypothesis falsified"),
    ("F-BREAK 2", "Proxy-substitution drift is random", "Proxy theory falsified"),
    ("F-BREAK 3", "Episenter shift produces random redistribution", "Episenter theory falsified"),
    ("F-BREAK 4", "Hubble tension survives full regime-compatibility test", "Regime-mismatch explanation falsified"),
    ("F-BREAK 5", "Null results are regime-random", "Cartographic null prediction falsified"),
]
