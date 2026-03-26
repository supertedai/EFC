"""
Reference implementation: Natural and Mechanical Entropy
Intention Detection via Episenter-Resonance Analysis in Information Systems

Paper: Magnusson (2026)
This is a pedagogical implementation, not production-ready.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


# ---------------------------------------------------------------------------
# Core concepts
# ---------------------------------------------------------------------------

@dataclass
class StructuralIntention:
    """Eq. 1: I = D_KL(q(x) || p(x|D))
    Structural intention as KL-divergence from baseline dynamics."""

    q: np.ndarray  # observed distribution
    p: np.ndarray  # baseline distribution (from system dynamics D)

    def compute(self) -> float:
        """KL-divergence D_KL(q || p). Returns 0 when q == p."""
        q = np.asarray(self.q, dtype=float)
        p = np.asarray(self.p, dtype=float)
        # Avoid log(0)
        mask = (q > 0) & (p > 0)
        return float(np.sum(q[mask] * np.log(q[mask] / p[mask])))

    @property
    def I(self) -> float:
        return self.compute()


@dataclass
class NaturalEntropy:
    """Eq. 2: S_N = H(X|D) = -sum p(x|D) ln p(x|D)
    Uncertainty from intrinsic dynamics only."""

    p: np.ndarray  # baseline distribution p(x|D)

    def compute(self) -> float:
        p = np.asarray(self.p, dtype=float)
        mask = p > 0
        return float(-np.sum(p[mask] * np.log(p[mask])))

    @property
    def S_N(self) -> float:
        return self.compute()


@dataclass
class MechanicalEntropy:
    """Eq. 3: S_M = H(X|D,I) + lambda * I(X;I)
    Uncertainty shaped by external structural intervention."""

    residual_entropy: float   # H(X|D,I)
    mutual_info_intervention: float  # I(X;I)
    lam: float = 1.0  # coupling constant (fixed at 1 in paper)

    def compute(self) -> float:
        return self.residual_entropy + self.lam * self.mutual_info_intervention

    @property
    def S_M(self) -> float:
        return self.compute()


@dataclass
class EntropyClassResidual:
    """Eq. 4: Delta_S = S_observed - S_N_predicted
    Diagnostic quantity: zero -> natural, positive -> mechanical injection."""

    s_observed: float
    s_n_predicted: float

    def compute(self) -> float:
        return self.s_observed - self.s_n_predicted

    @property
    def delta_S(self) -> float:
        return self.compute()

    def classify(self, tol: float = 0.05) -> str:
        ds = self.compute()
        if abs(ds) < tol:
            return "natural"
        elif ds > 0:
            return "mechanical"
        else:
            return "anomalous (negative residual)"


# ---------------------------------------------------------------------------
# Detection diagnostics
# ---------------------------------------------------------------------------

@dataclass
class EpisenterConcentration:
    """Eq. 5-6: E = max_k I(X_k; X) / sum_k I(X_k; X)
    High E -> mechanical (concentrated source), Low E -> natural (distributed)."""

    mutual_infos: np.ndarray  # I(X_k; X) for each variable k

    def compute(self) -> float:
        w = np.asarray(self.mutual_infos, dtype=float)
        total = np.sum(w)
        if total == 0:
            return 0.0
        return float(np.max(w) / total)

    @property
    def E(self) -> float:
        return self.compute()


@dataclass
class ResonanceSpectrum:
    """Eq. 7: R(omega) = P_observed(omega) / P_null(omega)
    R >> 1 at specific frequencies -> non-native periodicity."""

    signal: np.ndarray        # time-series or symbolic sequence
    n_bootstrap: int = 1000   # number of bootstrap permutations

    def compute(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (frequencies, R(omega)) where R = P_obs / P_null."""
        sig = np.asarray(self.signal, dtype=float)
        n = len(sig)

        # Observed PSD
        fft_obs = np.abs(np.fft.rfft(sig)) ** 2

        # Null PSD via bootstrap
        psd_null = np.zeros_like(fft_obs)
        for _ in range(self.n_bootstrap):
            shuffled = np.random.permutation(sig)
            psd_null += np.abs(np.fft.rfft(shuffled)) ** 2
        psd_null /= self.n_bootstrap

        # Avoid division by zero
        psd_null[psd_null == 0] = 1e-12

        R = fft_obs / psd_null
        freqs = np.fft.rfftfreq(n)
        return freqs, R

    def detect_peaks(self, R_crit: float = 3.0) -> List[Tuple[float, float]]:
        """Return (frequency, R) pairs where R > R_crit."""
        freqs, R = self.compute()
        peaks = [(float(f), float(r)) for f, r in zip(freqs, R) if r > R_crit]
        return peaks


@dataclass
class CrossRegimeAsymmetry:
    """Eq. 8: A = max_{r,s} |Delta_S(T_r(X)) - Delta_S(T_s(X))|
    A ~ 0 -> natural (regime-consistent), A >> 0 -> mechanical."""

    delta_s_per_regime: List[float]  # Delta_S values across different regimes

    def compute(self) -> float:
        vals = np.asarray(self.delta_s_per_regime, dtype=float)
        if len(vals) < 2:
            return 0.0
        return float(np.max(vals) - np.min(vals))

    @property
    def A(self) -> float:
        return self.compute()


@dataclass
class DetectionCriterion:
    """Eq. 9: Combined criterion.
    Mechanical entropy detected when ALL three exceed critical thresholds."""

    E: float
    R_max: float  # max R(omega) across frequencies
    A: float
    E_crit: float = 0.3
    R_crit: float = 3.0
    A_crit: float = 0.1

    def is_mechanical(self) -> bool:
        return self.E > self.E_crit and self.R_max > self.R_crit and self.A > self.A_crit

    def classify(self) -> str:
        checks = {
            "episenter": self.E > self.E_crit,
            "resonance": self.R_max > self.R_crit,
            "asymmetry": self.A > self.A_crit,
        }
        if all(checks.values()):
            return "MECHANICAL ENTROPY DETECTED"
        failed = [k for k, v in checks.items() if not v]
        return f"Natural (failed diagnostics: {', '.join(failed)})"

    def summary(self) -> str:
        lines = [
            "Detection Criterion Summary",
            "=" * 40,
            f"  Episenter Concentration E = {self.E:.4f}  (crit: {self.E_crit})",
            f"  Resonance Peak R_max     = {self.R_max:.4f}  (crit: {self.R_crit})",
            f"  Cross-Regime Asymmetry A = {self.A:.4f}  (crit: {self.A_crit})",
            f"  Classification: {self.classify()}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Case studies & predictions
# ---------------------------------------------------------------------------

@dataclass
class CaseStudy:
    id: str
    title: str
    domain: str
    description: str
    episenter: Optional[str] = None
    resonance: Optional[str] = None
    cross_regime: Optional[str] = None


@dataclass
class FalsifiablePrediction:
    id: str
    domain: str
    prediction: str


CASE_STUDIES = [
    CaseStudy(
        id="CS1",
        title="LLM Alignment Bias as Mechanical Entropy",
        domain="AI/LLM",
        description="Alignment mechanisms inject structure into response distributions",
        episenter="Concentrated — training-data paradigm dominance + safety constraints",
        resonance="Periodic: acknowledge -> qualify -> redirect -> request evidence",
        cross_regime="Friction only where established paradigm has training-data dominance",
    ),
    CaseStudy(
        id="CS2",
        title="Academic Paradigm-Guarding",
        domain="Academia",
        description="Peer review and funding inject mechanical entropy with concentrated episenter",
    ),
    CaseStudy(
        id="CS3",
        title="Information Warfare",
        domain="Psyops",
        description="State-level operations inject constructed narratives with centralised episenter",
    ),
]

PREDICTIONS = [
    FalsifiablePrediction("P1", "LLM", "Alignment-induced friction exhibits higher E than genuine epistemic uncertainty"),
    FalsifiablePrediction("P2", "LLM", "Pushback frequency is statistically periodic, independent of argument quality"),
    FalsifiablePrediction("P3", "LLM", "Cross-regime testing reduces alignment friction for unconventional frameworks"),
    FalsifiablePrediction("P4", "LLM", "Broader latent spaces yield lower E for alignment bias"),
    FalsifiablePrediction("P5", "Academia", "Rejection rates peak at regime boundaries"),
    FalsifiablePrediction("P6", "Academia", "Episenter shift redistributes paper rankings"),
    FalsifiablePrediction("P7", "Psyops", "Coordinated campaigns show resonance peaks at non-native frequencies"),
    FalsifiablePrediction("P8", "Psyops", "Cross-regime analysis degrades manufactured coherence faster than organic"),
    FalsifiablePrediction("P9", "General", "Natural entropy: A ~ 0; mechanical: A >> 0"),
    FalsifiablePrediction("P10", "General", "Delta_S for mechanical entropy is systematically positive"),
    FalsifiablePrediction("P11", "General", "Meta-control systems can distinguish S_N from S_M"),
    FalsifiablePrediction("P12", "EFC-C", "Meta-observation may be minimal architecture for entropy class discrimination"),
    FalsifiablePrediction("P13", "EFC-C", "Multi-mirror observation increases S_M detection super-linearly"),
]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_detection_demo():
    """Demonstrate the full detection pipeline with synthetic data."""
    np.random.seed(42)
    n_vars = 10

    print("=" * 60)
    print("Natural & Mechanical Entropy: Detection Framework Demo")
    print("=" * 60)

    # --- Natural entropy example ---
    print("\n--- Case A: Natural Entropy (uniform signal) ---")
    p_baseline = np.ones(20) / 20
    q_natural = p_baseline + np.random.normal(0, 0.005, 20)
    q_natural = np.abs(q_natural)
    q_natural /= q_natural.sum()

    si_nat = StructuralIntention(q=q_natural, p=p_baseline)
    sn = NaturalEntropy(p=p_baseline)
    print(f"  Structural Intention I = {si_nat.I:.6f}")
    print(f"  Natural Entropy S_N    = {sn.S_N:.4f}")

    # Distributed mutual information
    mi_natural = np.random.exponential(0.1, n_vars)
    ec_nat = EpisenterConcentration(mutual_infos=mi_natural)
    print(f"  Episenter Concentration E = {ec_nat.E:.4f}")

    # Uniform signal (no periodicity)
    signal_nat = np.random.randn(256)
    rs_nat = ResonanceSpectrum(signal=signal_nat, n_bootstrap=200)
    peaks_nat = rs_nat.detect_peaks(R_crit=3.0)
    print(f"  Resonance peaks (R>3): {len(peaks_nat)}")

    # Cross-regime: consistent
    delta_s_nat = [0.02, 0.03, 0.01, 0.025]
    cra_nat = CrossRegimeAsymmetry(delta_s_per_regime=delta_s_nat)
    print(f"  Cross-Regime Asymmetry A = {cra_nat.A:.4f}")

    R_max_nat = max([r for _, r in peaks_nat], default=1.0)
    det_nat = DetectionCriterion(E=ec_nat.E, R_max=R_max_nat, A=cra_nat.A)
    print(f"\n{det_nat.summary()}")

    # --- Mechanical entropy example ---
    print("\n\n--- Case B: Mechanical Entropy (LLM alignment pattern) ---")
    q_mechanical = p_baseline.copy()
    q_mechanical[0] += 0.15   # dominant bias
    q_mechanical[1] += 0.08
    q_mechanical = np.abs(q_mechanical)
    q_mechanical /= q_mechanical.sum()

    si_mech = StructuralIntention(q=q_mechanical, p=p_baseline)
    print(f"  Structural Intention I = {si_mech.I:.6f}")

    ecr = EntropyClassResidual(s_observed=2.8, s_n_predicted=2.99)
    print(f"  Entropy Class Residual Delta_S = {ecr.delta_S:.4f}")
    print(f"  Classification: {ecr.classify()}")

    # Concentrated mutual information
    mi_mech = np.random.exponential(0.05, n_vars)
    mi_mech[0] = 0.9  # dominant episenter
    ec_mech = EpisenterConcentration(mutual_infos=mi_mech)
    print(f"  Episenter Concentration E = {ec_mech.E:.4f}")

    # Signal with imposed periodicity (A->H->R->E cycle)
    cycle = [1, 2, 3, 4]  # A=1, H=2, R=3, E=4
    signal_mech = np.array(cycle * 64, dtype=float) + np.random.normal(0, 0.3, 256)
    rs_mech = ResonanceSpectrum(signal=signal_mech, n_bootstrap=200)
    peaks_mech = rs_mech.detect_peaks(R_crit=3.0)
    print(f"  Resonance peaks (R>3): {len(peaks_mech)}")
    if peaks_mech:
        top = sorted(peaks_mech, key=lambda x: -x[1])[:3]
        for f, r in top:
            print(f"    freq={f:.4f}, R={r:.1f}")

    # Cross-regime: asymmetric
    delta_s_mech = [0.02, 0.45, 0.03, 0.51]
    cra_mech = CrossRegimeAsymmetry(delta_s_per_regime=delta_s_mech)
    print(f"  Cross-Regime Asymmetry A = {cra_mech.A:.4f}")

    R_max_mech = max([r for _, r in peaks_mech], default=1.0)
    det_mech = DetectionCriterion(E=ec_mech.E, R_max=R_max_mech, A=cra_mech.A)
    print(f"\n{det_mech.summary()}")

    # --- Mechanical Entropy calculation ---
    print("\n\n--- Mechanical Entropy Decomposition ---")
    me = MechanicalEntropy(residual_entropy=2.5, mutual_info_intervention=0.35)
    print(f"  H(X|D,I) = {me.residual_entropy}")
    print(f"  I(X;I)   = {me.mutual_info_intervention}")
    print(f"  lambda    = {me.lam}")
    print(f"  S_M = H(X|D,I) + lambda*I(X;I) = {me.S_M:.4f}")

    # --- Case studies ---
    print("\n\n--- Case Studies ---")
    for cs in CASE_STUDIES:
        print(f"  [{cs.id}] {cs.title} ({cs.domain})")
        if cs.episenter:
            print(f"       Episenter: {cs.episenter}")

    # --- Predictions ---
    print("\n--- Falsifiable Predictions (13) ---")
    for pred in PREDICTIONS:
        print(f"  {pred.id} [{pred.domain}]: {pred.prediction}")

    print("\n" + "=" * 60)
    print("Demo complete.")


if __name__ == "__main__":
    run_detection_demo()
