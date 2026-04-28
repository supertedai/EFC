"""efc_val_2026_006.py

Reference implementation for EFC-VAL-2026-006:
Interim Audit Corrigendum to VAL-005 — Stub-to-Real Data Transition,
VariantH Genuine Null, and the Open G2 Growth-Likelihood Question.

DOI: 10.6084/m9.figshare.32114530
Author (paper): Morten Magnusson, Symbiose Research
Implementation: auto-generated reference code

Key elements implemented:
  1. EFC VariantH growth-source model with corrected mu-clamp
  2. Symmetric prior U(-0.5, +0.5) for S0_bar (Tier-1 fix #1)
  3. Walker initialisation U(-0.15, +0.15) (Tier-1 fix #2)
  4. Delta-chi2 comparison between stub (DR1) and real (DR2) BAO
  5. Binomial bias test (5/5 null-biased, p ~ 0.03)
  6. Posterior robustness / null-test sigma-band helper
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Optional
from scipy import stats

# ---------------------------------------------------------------------------
# Constants extracted from the paper
# ---------------------------------------------------------------------------
ALPHA_PRIOR_OLD = (0.0, 0.5)          # Bias #1: one-sided
ALPHA_PRIOR_NEW = (-0.5, 0.5)         # Tier-1 fix #1: symmetric
WALKER_INIT_OLD = (0.01, 0.15)        # Bias #2
WALKER_INIT_NEW = (-0.15, 0.15)       # Tier-1 fix #2
MU_CLAMP_OLD = (0.5, 10.0)            # Bias #3
MU_CLAMP_NEW = (0.3, 10.0)            # Tier-1 fix #3
MAGIC_OFFSET_OLD = 1.0                # Bias #5
DESI_DR1_DELTA_CHI2 = -22.01          # Stub result
BOSS_DR12_DELTA_CHI2 = -7.77          # Unchanged
FS8_LOO_ALPHA_STUB = (-1.00, 0.46)    # (mean, std) stub
G2_PPC_PVALUE = 0.99                  # Open issue
N_BIASES = 5
BINOMIAL_P_NULL = 0.5


def log_prior_variant_h(s0_bar: float,
                        bounds: Tuple[float, float] = ALPHA_PRIOR_NEW
                        ) -> float:
    """Flat (uniform) log-prior on the EFC coupling amplitude S0_bar.

    Tier-1 fix #1: symmetric U(-0.5, +0.5) replaces old U(0, 0.5).
    Returns 0.0 inside bounds, -inf outside.
    """
    lo, hi = bounds
    if lo <= s0_bar <= hi:
        return 0.0
    return -np.inf


def init_walkers(n_walkers: int = 32, n_dim: int = 5, *,
                 s0_range: Tuple[float, float] = WALKER_INIT_NEW,
                 rng: Optional[np.random.Generator] = None
                 ) -> np.ndarray:
    """Initialise MCMC walkers for 5-param VariantH.

    Tier-1 fix #2: S0_bar initialised from U(-0.15, +0.15) so the
    ensemble straddles zero.

    Parameters dim order (paper convention):
      [H0, Omega_m, Omega_b, S0_bar, mu]
    """
    if rng is None:
        rng = np.random.default_rng(42)
    p0 = np.empty((n_walkers, n_dim))
    p0[:, 0] = rng.uniform(65, 75, n_walkers)        # H0
    p0[:, 1] = rng.uniform(0.28, 0.34, n_walkers)    # Omega_m
    p0[:, 2] = rng.uniform(0.04, 0.06, n_walkers)    # Omega_b
    p0[:, 3] = rng.uniform(*s0_range, n_walkers)      # S0_bar
    p0[:, 4] = rng.uniform(*MU_CLAMP_NEW, n_walkers)  # mu
    return p0


def growth_source_variant_h(a: np.ndarray, s0_bar: float, mu: float,
                            mu_clamp: Tuple[float, float] = MU_CLAMP_NEW
                            ) -> np.ndarray:
    """EFC VariantH growth-source term.

    S(a) = S0_bar * a^mu   (entropy-gradient coupling)

    mu is clamped to [mu_lo, mu_hi].  Tier-1 fix #3 lowers mu_lo
    from 0.5 to 0.3 to permit physical suppression solutions.
    """
    mu_eff = np.clip(mu, mu_clamp[0], mu_clamp[1])
    return s0_bar * np.power(a, mu_eff)


def delta_chi2_bao(chi2_efc: float, chi2_lcdm: float) -> float:
    """Compute Delta-chi2 = chi2_EFC - chi2_LCDM.

    Negative values favour EFC; ~0 means no signal.
    """
    return chi2_efc - chi2_lcdm


def binomial_bias_test(k: int = N_BIASES, n: int = N_BIASES,
                       p: float = BINOMIAL_P_NULL) -> float:
    """Exact binomial p-value for k-of-n biases in same direction.

    Paper: k=5, n=5, p=0.5  =>  p ~ 0.03125.
    """
    return stats.binom.pmf(k, n, p)


def posterior_robustness_sigma(delta_logL_samples: np.ndarray
                               ) -> Tuple[float, float]:
    """Return (mean, std) of Delta-log-L samples — the empirical
    sigma band that Tier-1 fix #4 wires into the daemon."""
    return float(np.mean(delta_logL_samples)), float(np.std(delta_logL_samples, ddof=1))


def forbidden_pattern_distance(d_values: np.ndarray, *,
                               apply_old_offset: bool = False
                               ) -> np.ndarray:
    """Compute forbidden-pattern distance metric.

    Tier-1 fix #5 removes the +1.0 magic offset that generated
    false WARNINGs in the both-positive case.
    """
    result = d_values.copy()
    if apply_old_offset:
        result = result + MAGIC_OFFSET_OLD  # old buggy behaviour
    return result


def classify_result(delta_chi2: float, threshold_strong: float = -15.0,
                    threshold_modest: float = -5.0) -> str:
    """Classify a Delta-chi2 value into paper status labels."""
    if delta_chi2 <= threshold_strong:
        return "STRONG"
    elif delta_chi2 <= threshold_modest:
        return "MODEST"
    elif abs(delta_chi2) < 2.0:
        return "NO_SIGNAL"
    else:
        return "WEAK"


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Binomial bias test
    p_val = binomial_bias_test()
    assert abs(p_val - 0.03125) < 1e-6, f"Binomial test failed: {p_val}"
    print(f"[PASS] Binomial bias test: p = {p_val:.5f}")

    # 2. Prior symmetry
    assert log_prior_variant_h(-0.3) == 0.0
    assert log_prior_variant_h(0.6) == -np.inf
    print("[PASS] Symmetric prior U(-0.5, +0.5)")

    # 3. Growth source at a=1 equals S0_bar
    s = growth_source_variant_h(np.array([1.0]), 0.1, 2.0)
    assert np.isclose(s[0], 0.1), s
    print("[PASS] Growth source S(a=1) = S0_bar")

    # 4. Walker init straddles zero
    p0 = init_walkers(1000)
    assert p0[:, 3].min() < 0 and p0[:, 3].max() > 0
    print("[PASS] Walker init straddles zero")

    # 5. Delta-chi2 classification
    assert classify_result(DESI_DR1_DELTA_CHI2) == "STRONG"
    assert classify_result(0.0) == "NO_SIGNAL"
    assert classify_result(BOSS_DR12_DELTA_CHI2) == "MODEST"
    print("[PASS] Result classification")

    print("\nAll self-tests passed.")
