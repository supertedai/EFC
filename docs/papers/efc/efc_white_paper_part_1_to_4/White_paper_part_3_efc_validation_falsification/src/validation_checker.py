"""
EFC White Paper Part 3 — Validation Checker.

Implements ledger status classification, kill-criterion checks,
and confirmation-level evaluation.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970904
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationTest:
    """A single test in the EFC Validation Ledger."""
    name: str
    status: str  # Pass, Partial, Collapsed, Failed, Falsified
    result: str
    tier: Optional[str] = None  # T1, T2, T3, T4


@dataclass
class KillCriterion:
    """A kill criterion for Stage-IV surveys."""
    id: str
    name: str
    threshold: float
    observed: Optional[float] = None
    triggered: bool = False


TIER_LABELS = {
    "T1": "Multi-channel consistency",
    "T2": "Data-likelihood comparison",
    "T3": "Structural/analytical proof",
    "T4": "Meta-model evaluation",
}


def classify_status(tests: list[ValidationTest]) -> dict:
    """Classify validation tests by status."""
    counts = {"Pass": 0, "Partial": 0, "Collapsed": 0, "Failed": 0, "Falsified": 0}
    for t in tests:
        counts[t.status] = counts.get(t.status, 0) + 1
    return counts


def check_kill_criterion_1(alpha_L2: float, alpha_L2_err: float) -> KillCriterion:
    """KC1: Growth suppression absent.

    |alpha_L2| < 0.1 at 3 sigma => EFC falsified (growth sector).
    """
    significance = abs(alpha_L2) / alpha_L2_err
    triggered = abs(alpha_L2) < 0.1 and significance < 3.0
    return KillCriterion("KC1", "Growth suppression absent", 0.1,
                         observed=alpha_L2, triggered=triggered)


def check_kill_criterion_2(z_cross_obs: float, z_cross_err: float) -> KillCriterion:
    """KC2: Wrong f*sigma_8 trajectory.

    |z_cross_obs - 2.042| > 3 sigma => crossover prediction falsified.
    """
    z_cross_pred = 2.042
    deviation = abs(z_cross_obs - z_cross_pred) / z_cross_err
    triggered = deviation > 3.0
    return KillCriterion("KC2", "Wrong f*sigma_8 trajectory", z_cross_pred,
                         observed=z_cross_obs, triggered=triggered)


def check_kill_criterion_3(S8_obs: float, S8_lcdm: float, S8_err: float) -> KillCriterion:
    """KC3: S_8 converges to LCDM.

    S_8 = S_{8,LCDM} +/- 0.005 at Stage-IV precision => S_8 channel falsified.
    """
    triggered = abs(S8_obs - S8_lcdm) < 0.005 and S8_err < 0.005
    return KillCriterion("KC3", "S_8 converges to LCDM", S8_lcdm,
                         observed=S8_obs, triggered=triggered)


def check_kill_criterion_4(eta_obs: float, eta_err: float) -> KillCriterion:
    """KC4: Gravitational slip absent.

    |eta - 1| < 0.01 at Euclid precision => slip prediction falsified.
    """
    triggered = abs(eta_obs - 1.0) < 0.01 and eta_err < 0.01
    return KillCriterion("KC4", "Gravitational slip absent", 1.0,
                         observed=eta_obs, triggered=triggered)


def check_kill_criterion_5(w0_obs: float, w0_err: float) -> KillCriterion:
    """KC5: Dynamical dark energy absent.

    |w_0 + 1| < 0.02 at Euclid precision => dynamical DE falsified.
    """
    triggered = abs(w0_obs + 1.0) < 0.02 and w0_err < 0.02
    return KillCriterion("KC5", "Dynamical dark energy absent", -1.0,
                         observed=w0_obs, triggered=triggered)


def confirmation_level(sigma: float) -> str:
    """Determine confirmation level from combined significance."""
    if sigma >= 5.0:
        return "Detection"
    elif sigma >= 3.5:
        return "Evidence"
    elif sigma >= 3.0:
        return "Suggestive"
    elif sigma >= 2.0:
        return "Hint"
    else:
        return "Not significant"
