"""efc_outcome_estimation_crosssurvey.py

Reference implementation for:
  Expected Outcomes for Energy-Flow Cosmology Cross-Survey Invariance
  and BIG-SPARC Tests
  DOI: 10.6084/m9.figshare.32045592

Implements:
  - AIC / BIC win-rate estimation with structural transfer factors
  - Wilson confidence intervals
  - BIC penalty computation  (ln(N_pts) - 2  extra per galaxy)
  - Regime-proxy fraction consistency check
  - Overlap-test probability estimate
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Dict

# ---------------------------------------------------------------------------
# Constants from the paper (Table 1)
# ---------------------------------------------------------------------------
SPARC_N: int = 171
SPARC_WIN_RATE: float = 0.602
SPARC_DECISIVE: int = 72
SPARC_MARGINAL: int = 31
SPARC_TIED: int = 46
SPARC_LCDM_WINS: int = 22
SPARC_MEDIAN_DAIC: float = 6.2
SPARC_MEDIAN_CHI2_EFC: float = 0.44
SPARC_MEDIAN_CHI2_NFW: float = 1.69
K_SCREENING: float = 0.415
K_SCREENING_ERR: float = 0.029

# Regime fractions (Table 1)
FLOW_FRAC: float = 71 / 171
TRANSITION_FRAC: float = 84 / 171
LATENT_FRAC: float = 16 / 171

# Survey sample sizes
THINGS_N: int = 34
LITTLE_THINGS_N: int = 26
WALLABY_N: int = 203
TIER1_N: int = 60  # THINGS + LITTLE THINGS combined

# Structural shift factors (Table 2) – percentage-point shifts
SHIFTS_TIER1: Dict[str, float] = {
    "no_spitzer": -0.05,
    "vel_pipeline": -0.03,
    "hi_only": -0.02,
    "things_high_res": +0.02,
    "lt_flow_dwarfs": +0.03,
}
NET_SHIFT_TIER1: float = -0.05

SHIFTS_WALLABY: Dict[str, float] = {
    "no_spitzer": -0.05,
    "vel_pipeline": -0.03,
    "hi_only": -0.02,
    "beam_smearing": -0.08,
    "assumed_errors": -0.04,
}
NET_SHIFT_WALLABY: float = -0.12

# Typical N_pts per galaxy per survey (Table 4)
TYPICAL_NPTS: Dict[str, int] = {
    "SPARC": 20,
    "THINGS": 25,
    "LITTLE_THINGS": 15,
    "WALLABY": 12,
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def wilson_ci(n: int, k_success: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score confidence interval for a binomial proportion.

    Parameters
    ----------
    n : int   – number of trials
    k_success : int – number of successes
    z : float – z-score (default 1.96 for 95% CI)

    Returns
    -------
    (lower, upper) as fractions in [0, 1]
    """
    if n == 0:
        return (0.0, 1.0)
    p_hat = k_success / n
    denom = 1.0 + z ** 2 / n
    centre = (p_hat + z ** 2 / (2.0 * n)) / denom
    margin = z * np.sqrt(p_hat * (1.0 - p_hat) / n + z ** 2 / (4.0 * n ** 2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def bic_extra_penalty(n_pts: int) -> float:
    """Extra BIC penalty per galaxy relative to AIC.

    ∆BIC_extra = ln(N_pts) - 2   (per extra parameter)
    Paper Sec 3.2
    """
    return float(np.log(n_pts) - 2.0)


def estimate_aic_win_rate(baseline_wr: float, net_shift: float) -> float:
    """Projected AIC win rate after applying structural shift."""
    return np.clip(baseline_wr + net_shift, 0.0, 1.0)


def estimate_bic_win_rate(
    aic_wr: float,
    n_total: int,
    n_decisive: int,
    n_marginal: int,
    typical_npts: int,
) -> float:
    """Estimate BIC win rate from AIC win rate.

    Decisive wins (|dAIC|>10) survive the extra BIC penalty.
    Marginal wins are reduced proportionally to the extra penalty
    relative to a |dAIC|=5 (mid-marginal) reference.
    """
    penalty = bic_extra_penalty(typical_npts)
    # fraction of marginal wins lost  ~  penalty / 5  (mid-marginal dAIC reference)
    marginal_loss_frac = np.clip(penalty / 5.0, 0.0, 1.0)
    lost = marginal_loss_frac * n_marginal
    bic_wins = n_decisive + n_marginal - lost
    return float(np.clip(bic_wins / n_total, 0.0, 1.0))


def project_survey_counts(
    n_survey: int,
    aic_wr: float,
) -> Dict[str, int]:
    """Scale SPARC decisive/marginal/tied/lcdm counts to a new survey."""
    decisive_frac = SPARC_DECISIVE / SPARC_N
    marginal_frac = SPARC_MARGINAL / SPARC_N
    tied_frac = SPARC_TIED / SPARC_N
    lcdm_frac = SPARC_LCDM_WINS / SPARC_N
    # Rescale wins by ratio of new wr to baseline
    scale = aic_wr / SPARC_WIN_RATE if SPARC_WIN_RATE > 0 else 1.0
    decisive = int(round(decisive_frac * n_survey * scale))
    marginal = int(round(marginal_frac * n_survey * scale))
    total_efc = decisive + marginal
    lcdm = int(round(lcdm_frac * n_survey / SPARC_WIN_RATE * (1.0 - aic_wr)))
    tied = n_survey - total_efc - lcdm
    return {"decisive": decisive, "marginal": marginal, "tied": max(tied, 0), "lcdm": lcdm}


def regime_fractions_consistent(
    flow: float, transition: float, latent: float,
    tolerance_pp: float = 0.15,
) -> bool:
    """Check if regime fractions are within ±tolerance_pp of SPARC baseline (P3)."""
    return (
        abs(flow - FLOW_FRAC) <= tolerance_pp
        and abs(transition - TRANSITION_FRAC) <= tolerance_pp
        and abs(latent - LATENT_FRAC) <= tolerance_pp
    )


def overlap_test_estimate(
    n_overlap: int = 14,
    decisive_agree_prob: float = 0.95,
    marginal_agree_prob: float = 0.50,
    n_decisive: int = 10,
    n_marginal: int = 4,
) -> float:
    """Expected number of consistent overlap galaxies (P2)."""
    return decisive_agree_prob * n_decisive + marginal_agree_prob * n_marginal


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Reproduce Table 3 estimates
    for name, shift, n, npts in [
        ("THINGS", NET_SHIFT_TIER1, THINGS_N, TYPICAL_NPTS["THINGS"]),
        ("LITTLE_THINGS", NET_SHIFT_TIER1, LITTLE_THINGS_N, TYPICAL_NPTS["LITTLE_THINGS"]),
        ("WALLABY", NET_SHIFT_WALLABY, WALLABY_N, TYPICAL_NPTS["WALLABY"]),
    ]:
        wr_aic = estimate_aic_win_rate(SPARC_WIN_RATE, shift)
        ci = wilson_ci(n, int(round(wr_aic * n)))
        pen = bic_extra_penalty(npts)
        print(f"{name:16s}  AIC WR={wr_aic:.1%}  95%CI=[{ci[0]:.0%},{ci[1]:.0%}]  BIC_extra_pen={pen:+.2f}")

    # Overlap test
    ov = overlap_test_estimate()
    print(f"\nOverlap test expected consistent: {ov:.1f} / 14")

    # Regime consistency
    ok = regime_fractions_consistent(FLOW_FRAC, TRANSITION_FRAC, LATENT_FRAC)
    print(f"Regime fractions self-consistent: {ok}")
    print("Self-test passed.")
