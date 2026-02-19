"""
EFC CMB Localization Study — Reference Implementation

Five-phase systematic localization of late-time cosmological signals
in modified gravity parameter space.

Reference: DOI 10.6084/m9.figshare.31368433
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


# Phase 1: Background Gate

@dataclass
class JointFitResult:
    """Single row of Phase 1 joint-fit table (Table 1)."""
    dataset: str
    chi2_lcdm: float
    chi2_efc: float
    alpha_bf: float
    delta_chi2: float

JOINT_FIT_DATA = [
    JointFitResult("Planck only",              1010.35, 1012.23,  0.035,  1.88),
    JointFitResult("Planck + SDSS DR12",       1016.91, 1015.60, -0.111, -1.31),
    JointFitResult("Planck + DESI 2024",       1025.65, 1028.63, -0.045,  2.98),
    JointFitResult("Planck + DESI + Pantheon+", 2432.71, 2430.61, -0.045, -2.10),
]

class BackgroundGate:
    """Phase 1: EFC background gate constraints.
    E2(a) = E2_LCDM(a) + alpha g(a)
    Result: alpha -> 0 under joint CMB+BAO+SNe, corr(alpha, H0) = 0.975.
    """
    def __init__(self):
        self.joint_fits = JOINT_FIT_DATA
        self.planck_mcmc_alpha = -0.32
        self.planck_mcmc_sigma = 0.40
        self.planck_mcmc_significance = 0.82
        self.corr_alpha_H0 = 0.975

    def logistic_gate(self, a, a_t=0.5, delta_a=0.05):
        """Logistic gate g(a) = [1 + exp(-(a - a_t)/delta_a)]^-1."""
        return 1.0 / (1.0 + np.exp(-(a - a_t) / delta_a))

    def E2_efc(self, a, alpha, Omega_m=0.315, Omega_L=0.685, a_t=0.5, delta_a=0.05):
        """EFC-modified E2(a) = Om a^-3 + OL + alpha g(a)."""
        E2_lcdm = Omega_m * a**(-3) + Omega_L
        return E2_lcdm + alpha * self.logistic_gate(a, a_t, delta_a)

    def is_background_empty(self, threshold_sigma=2.0):
        """True if no joint fit exceeds threshold."""
        return all(abs(jf.delta_chi2) < threshold_sigma**2 for jf in self.joint_fits)

    def joint_fit_summary(self):
        lines = ["Phase 1: Background Gate", "=" * 50,
                 f"{'Dataset':<30} {'alpha_bf':>8} {'dchi2':>8}"]
        for jf in self.joint_fits:
            lines.append(f"{jf.dataset:<30} {jf.alpha_bf:>+8.3f} {jf.delta_chi2:>+8.2f}")
        lines.append("-" * 50)
        lines.append(f"MCMC: alpha = {self.planck_mcmc_alpha} +/- {self.planck_mcmc_sigma}")
        lines.append(f"corr(alpha, H0) = {self.corr_alpha_H0}")
        lines.append(f"Background empty: {self.is_background_empty()}")
        return "\n".join(lines)


# Phase 2: Perturbation Sector

@dataclass
class PureMuPoint:
    """Pure mu scan at Sigma=1 (Table 2)."""
    mu: float; delta_sigma8_pct: float; delta_chi2_TT: float
    delta_chi2_lens: float; delta_chi2_full: float; verdict: str

@dataclass
class ValleyPoint:
    """Profiled mu-Sigma valley (Table 3)."""
    mu: float; sigma_star: float; delta_chi2_full: float
    delta_sigma8_pct: float; s8_relief_pct: float

@dataclass
class MinimizePoint:
    """Minimize with free cosmological parameters (Table 4)."""
    mu: float; sigma_mg: float; chi2_min: float
    delta_chi2: float; delta_chi2_highl: float; delta_chi2_lowlTT: float

PURE_MU_DATA = [
    PureMuPoint(0.90, -10.3, 18.5, 14.7, 33.2, "Excluded"),
    PureMuPoint(0.93,  -7.3, 11.5,  7.5, 19.0, "Excluded"),
    PureMuPoint(0.95,  -5.3,  7.6,  3.9, 11.5, "Excluded"),
    PureMuPoint(0.97,  -3.2,  4.1,  1.4,  5.6, "Marginal"),
    PureMuPoint(0.99,  -1.1,  1.2,  0.2,  1.4, "Viable"),
]

VALLEY_DATA = [
    ValleyPoint(0.92, 1.060, 4.56, -8.4, 100),
    ValleyPoint(0.93, 1.050, 3.45, -7.4,  93),
    ValleyPoint(0.94, 1.050, 2.49, -6.4,  81),
    ValleyPoint(0.95, 1.040, 1.61, -5.3,  67),
]

GR_REFERENCE_CHI2 = 1014.78

MINIMIZE_DATA = [
    MinimizePoint(0.94, 1.05, 1014.33, -0.45, -4.68, 2.97),
    MinimizePoint(0.95, 1.04, 1015.90,  1.13, -0.40, 0.93),
    MinimizePoint(0.92, 1.06, 1019.90,  5.12, -5.48, 5.91),
]

class MuSigmaValley:
    """Phase 2: mu-Sigma perturbation-sector constraints.
    Pure mu (Sigma=1) excluded by CMB lensing.
    Valley at (mu~0.94, Sigma~1.05), dchi2 = -0.45.
    """
    def __init__(self):
        self.pure_mu_scan = PURE_MU_DATA
        self.valley = VALLEY_DATA
        self.minimize_results = MINIMIZE_DATA
        self.gr_chi2 = GR_REFERENCE_CHI2
        self.sigma_lensing_fit = 1.047
        self.sigma_lensing_uncertainty = 0.013

    def interpolate_valley_sigma(self, mu):
        """Interpolate profiled Sigma*(mu)."""
        mus = np.array([v.mu for v in self.valley])
        sigmas = np.array([v.sigma_star for v in self.valley])
        return float(np.interp(mu, mus, sigmas))

    def delta_chi2(self, mu=0.94, sigma_mg=1.05):
        """Look up delta-chi2 at (mu, Sigma)."""
        for m in self.minimize_results:
            if abs(m.mu - mu) < 0.005 and abs(m.sigma_mg - sigma_mg) < 0.005:
                return m.delta_chi2
        return None

    def sweet_spot(self):
        """Return sweet-spot minimize result."""
        return self.minimize_results[0]


# Phase 3: A_L Degeneracy

@dataclass
class ALDiagnosticPoint:
    """A_L degeneracy diagnostic (Table 5)."""
    model: str; chi2_min: float; delta_chi2: float; AL_bf: float; dof: int

AL_DIAGNOSTIC_DATA = [
    ALDiagnosticPoint("GR reference",          1014.78,  0.00, 1.000, 0),
    ALDiagnosticPoint("GR + A_L free",         1010.36, -4.42, 1.042, 1),
    ALDiagnosticPoint("(mu,Sigma) + A_L=1",    1014.33, -0.45, 1.000, 2),
    ALDiagnosticPoint("(mu,Sigma) + A_L free", 1016.37,  1.59, 0.976, 3),
]

class ALDegeneracy:
    """Phase 3: A_L anomaly degeneracy diagnostics.
    Three tests: chi2, Fisher (cos=0.81), gradient (cos=0.93).
    Conclusion: (mu,Sigma) valley IS the A_L anomaly.
    """
    def __init__(self):
        self.diagnostic_data = AL_DIAGNOSTIC_DATA
        self.fisher_cos_flat_AL = 0.81
        self.gradient_cos_sigma_AL = 0.93

    def is_degenerate(self, threshold=0.80):
        return self.gradient_cos_sigma_AL > threshold

    def al_improvement_chi2(self):
        return self.diagnostic_data[1].delta_chi2

    def summary(self):
        return "\n".join([
            "Phase 3: A_L Degeneracy", "=" * 50,
            f"Fisher cos(e_flat, A_L) = {self.fisher_cos_flat_AL}",
            f"Gradient cos(Sigma, AL) = {self.gradient_cos_sigma_AL}",
            f"A_L alone dchi2         = {self.al_improvement_chi2():.2f}",
            "Conclusion: (mu,Sigma) valley IS the A_L anomaly.",
        ])


# Phase 4: Growth-Sector Sign Constraint

@dataclass
class B0FilterResult:
    """B0 bridge test filter (Table 6)."""
    name: str; direction: Optional[str]; delta_sigma8_pct: Optional[float]
    chi2: float; delta_chi2: Optional[float]; verdict: str

B0_FILTER_DATA = [
    B0FilterResult("LCDM",       None,        None,   66.62,  None,   "Reference"),
    B0FilterResult("F3 tanh",    "Weaken",    -0.54,  61.40, -5.22,  "> 2s improvement"),
    B0FilterResult("F2 gauss",   "Weaken",    -0.25,  63.62, -3.00,  "Improves"),
    B0FilterResult("F1 raised",  "Weaken",    -0.18,  64.45, -2.17,  "Improves"),
    B0FilterResult("F0 original","Weaken",     0.00,  66.61, -0.01,  "Neutral"),
    B0FilterResult("F1 raised",  "Strengthen", 16.8, 561.4,  494.7,  "Killed"),
]

class GrowthSignTest:
    """Phase 4: fsigma8 sign constraint (B0 bridge test).
    mu < 1 improves at > 2s (dchi2=-5.22). mu > 1 killed. Independent of A_L.
    """
    def __init__(self):
        self.filters = B0_FILTER_DATA
        self.alpha_eff = 0.06
        self.z_range = (0.38, 0.85)
        self.n_data_points = 7

    def best_filter(self):
        return self.filters[1]

    def sign_is_mu_less_than_1(self):
        w = any(f.direction == "Weaken" and f.delta_chi2 is not None
                and f.delta_chi2 < -2.0 for f in self.filters)
        s = any(f.direction == "Strengthen" and f.delta_chi2 is not None
                and f.delta_chi2 > 100 for f in self.filters)
        return w and s

    def best_improvement_sigma(self):
        b = self.best_filter()
        return np.sqrt(abs(b.delta_chi2)) if b.delta_chi2 else 0.0

    def sign_constraint_summary(self):
        lines = ["Phase 4: Growth Sign Constraint (B0)", "=" * 50,
                 f"{'Filter':<14} {'Dir':<12} {'chi2':>8} {'dchi2':>8} Verdict"]
        for f in self.filters:
            d = f"{f.delta_chi2:>+8.2f}" if f.delta_chi2 is not None else "       -"
            lines.append(f"{f.name:<14} {(f.direction or '-'):<12} {f.chi2:>8.2f} {d} {f.verdict}")
        lines.append(f"Sign: mu < 1 at {self.best_improvement_sigma():.1f}s")
        return "\n".join(lines)


# Surviving Signal Specification

@dataclass
class SurvivingSignalSpec:
    """Combined surviving signal specification from all five phases."""
    mu_value: float = 0.94
    mu_range: tuple = (0.93, 0.96)
    sigma_value: float = 1.05
    sigma_range: tuple = (1.03, 1.07)
    eta_slip: float = 1.12

    def gravitational_slip(self):
        return self.sigma_value / self.mu_value

    def theory_gap(self):
        return [
            "Wrong sign: Grid-AQUAL mu>1, cosmology needs mu<1",
            "No slip: single potential => eta=1, need eta~1.12",
            "Screening: k_Lambda=0.0014 h/Mpc too small, need ~0.05-0.1",
        ]

    def summary(self):
        lines = ["Surviving Signal Specification", "=" * 50,
                 f"mu    = {self.mu_value} (range: {self.mu_range})",
                 f"Sigma = {self.sigma_value} (range: {self.sigma_range})",
                 f"eta   = {self.gravitational_slip():.3f}",
                 "Sign: mu < 1 (weakened gravity)",
                 "Magnitude: ~6% effective weakening",
                 "Scales: k ~ 0.05-0.1 h/Mpc",
                 "Epoch: Late-time (z < 1)", "",
                 "Theory-observation gap:"]
        for g in self.theory_gap():
            lines.append(f"  - {g}")
        return "\n".join(lines)
