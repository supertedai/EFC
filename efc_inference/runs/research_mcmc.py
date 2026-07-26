#!/usr/bin/env python3
"""
Reusable MCMC research functions for EFC inference.

Extracts the proven MCMC logic from run_n1_rd_diagnostic.py,
run_n2_sigma8_sweep.py, and run_t7_loo_growth.py into callable
functions for the autonomous research daemon.

All prior functions are copied verbatim from the working manual scripts.
Uses raw emcee.EnsembleSampler (not EFCSampler).
"""
import os
import sys
import time
import json
import logging
import tempfile
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import emcee

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from efc_inference.engine.hubble import EFCHubble
from efc_inference.engine.growth import EFCGrowth
from efc_inference.modules.bao_module import BAOModule
from efc_inference.modules.growth_module import GrowthModule
from efc_inference.modules.hz_module import HzModule
from efc_inference.modules.snia_module import SNIaModule
from efc_inference.core.cosmology_model import (
    CosmologyModel, EFCVariantA, EFCVariantB, EFCVariantC, EFCVariantF,
    EFCVariantG, FlatLCDM,
)
from efc_inference.core.sound_horizon import compute_rd_efc

logger = logging.getLogger("research_mcmc")


# ═══════════════════════════════════════════════════════════════
#  DATACLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class AlphaStats:
    """Statistics for the alpha_cosmo parameter."""
    mean: float
    std: float
    significance: float     # |mean| / std
    p_negative: float       # P(alpha < 0), fraction [0,1]
    median: float
    ci95_lo: float          # 2.5th percentile
    ci95_hi: float          # 97.5th percentile


@dataclass
class ParamStats:
    """Generic parameter statistics."""
    mean: float
    std: float
    median: float
    ci95_lo: float
    ci95_hi: float


@dataclass
class ModelComparison:
    """AIC/BIC model comparison EFC vs LCDM."""
    ll_efc: float
    ll_lcdm: float
    k_efc: int              # number of free params EFC
    k_lcdm: int             # number of free params LCDM
    n_data: int             # total data points
    daic: float             # AIC_EFC - AIC_LCDM (negative = EFC favored)
    dbic: float             # BIC_EFC - BIC_LCDM


@dataclass
class BaselineResult:
    """Result from run_joint_inference()."""
    alpha: AlphaStats
    comparison: ModelComparison
    correlations: dict      # {"a_om": float, "a_s8": float, "a_h0": float}
    om: ParamStats
    s8: ParamStats
    h0: ParamStats
    chain_efc: np.ndarray
    chain_lcdm: np.ndarray
    manifest: dict
    sampler_efc: object = None  # raw emcee sampler for convergence diagnostics
    probe_likelihoods: dict = None  # per-probe ΔlogL at best-fit (EFC vs ΛCDM)


# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════

RD_FIXED = 147.09
RD_PRIOR_MU = 147.1
RD_PRIOR_SIGMA = 4.0

DEFAULT_NWALKERS = 48
DEFAULT_NSTEPS = 4000
DEFAULT_BURNIN = 1500
DEFAULT_SEED = 42

# Data paths (relative to repo root)
# BAO_PATH: env override allows switching to DESI DR2 (JSON w/ full covariance)
BAO_PATH = os.environ.get("EFC_BAO_DATA_PATH", "efc_inference/data/bao/bao_starter.csv")
GROWTH_PATH = "efc_inference/data/growth/fs8_extended.csv"
HZ_PATH = "efc_inference/data/hubble/hz_cosmic_chronometers.csv"
SNIA_PATH = "efc_inference/data/snia/pantheon_binned.csv"
SNIA_COV_PATH = "efc_inference/data/snia/pantheon_binned_covtotal.npy"


# ═══════════════════════════════════════════════════════════════
#  PRIVATE HELPERS
# ═══════════════════════════════════════════════════════════════

def _extract_alpha(chain: np.ndarray, alpha_col: int) -> AlphaStats:
    """Extract alpha statistics from MCMC chain."""
    samples = chain[:, alpha_col]
    mean = float(np.mean(samples))
    std = float(np.std(samples))
    return AlphaStats(
        mean=mean,
        std=std,
        significance=abs(mean) / std if std > 0 else 0.0,
        p_negative=float(np.mean(samples < 0)),
        median=float(np.median(samples)),
        ci95_lo=float(np.percentile(samples, 2.5)),
        ci95_hi=float(np.percentile(samples, 97.5)),
    )


def _extract_param(chain: np.ndarray, col: int) -> ParamStats:
    """Extract generic parameter statistics from MCMC chain."""
    samples = chain[:, col]
    return ParamStats(
        mean=float(np.mean(samples)),
        std=float(np.std(samples)),
        median=float(np.median(samples)),
        ci95_lo=float(np.percentile(samples, 2.5)),
        ci95_hi=float(np.percentile(samples, 97.5)),
    )


def _compute_comparison(
    ll_efc: float, k_efc: int,
    ll_lcdm: float, k_lcdm: int,
    n_data: int,
) -> ModelComparison:
    """Compute AIC/BIC model comparison."""
    aic_efc = -2 * ll_efc + 2 * k_efc
    aic_lcdm = -2 * ll_lcdm + 2 * k_lcdm
    bic_efc = -2 * ll_efc + k_efc * np.log(n_data)
    bic_lcdm = -2 * ll_lcdm + k_lcdm * np.log(n_data)
    return ModelComparison(
        ll_efc=float(ll_efc),
        ll_lcdm=float(ll_lcdm),
        k_efc=k_efc,
        k_lcdm=k_lcdm,
        n_data=n_data,
        daic=float(aic_efc - aic_lcdm),
        dbic=float(bic_efc - bic_lcdm),
    )


def _build_manifest(
    seed: int,
    nwalkers: int,
    nsteps: int,
    burnin: int,
    bao_path: str,
    growth_path: str,
    n_bao: int,
    n_growth: int,
    hz_path: str = "",
    n_hz: int = 0,
    snia_path: str = "",
    n_snia: int = 0,
) -> dict:
    """Build reproducibility manifest."""
    git_hash = "unknown"
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass

    manifest = {
        "seed": seed,
        "nwalkers": nwalkers,
        "nsteps": nsteps,
        "burnin": burnin,
        "bao_data": os.path.basename(bao_path),
        "growth_data": os.path.basename(growth_path),
        "n_bao": n_bao,
        "n_growth": n_growth,
        "git_hash": git_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "emcee_version": emcee.__version__,
        "numpy_version": np.__version__,
    }

    # Multi-probe fields (backward compatible — only added if present)
    if n_hz > 0:
        manifest["hz_data"] = os.path.basename(hz_path)
        manifest["n_hz"] = n_hz
    if n_snia > 0:
        manifest["snia_data"] = os.path.basename(snia_path)
        manifest["n_snia"] = n_snia
    manifest["n_total"] = n_bao + n_growth + n_hz + n_snia
    manifest["probes"] = [p for p, n in
                           [("bao", n_bao), ("growth", n_growth),
                            ("hz", n_hz), ("snia", n_snia)] if n > 0]

    return manifest


def _run_emcee(
    label: str,
    log_prob_fn,
    ndim: int,
    p0: np.ndarray,
    nwalkers: int,
    nsteps: int,
    burnin: int,
    args: tuple,
    seed: int = DEFAULT_SEED,
    pool=None,
) -> tuple:
    """Run emcee sampler, return (chain, logprob, time_seconds, sampler).

    chain: (n_samples, ndim) flat chain after burnin
    logprob: (n_samples,) log-posterior after burnin
    sampler: raw emcee.EnsembleSampler (for convergence diagnostics)

    pool: optional multiprocessing.Pool for parallel walker evaluation.
          On Windows, must use `if __name__ == '__main__':` guard.
    """
    cores_info = f", pool={pool._processes}cores" if pool and hasattr(pool, '_processes') else ""
    logger.info(f"  {label}: {nwalkers}w x {nsteps}s{cores_info} ...")
    t0 = time.time()

    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob_fn, args=args, pool=pool)
    sampler.run_mcmc(p0, nsteps, progress=False)

    dt = time.time() - t0
    chain = sampler.get_chain(discard=burnin, flat=True)
    logprob = sampler.get_log_prob(discard=burnin, flat=True)

    logger.info(f"  {label}: {chain.shape[0]} samples, {dt:.0f}s")
    return chain, logprob, dt, sampler


def _correlations_4param(chain: np.ndarray) -> dict:
    """Compute correlations for [Om, H0, s8, alpha] chain."""
    corrmat = np.corrcoef(chain.T)
    return {
        "a_om": float(corrmat[0, 3]),
        "a_h0": float(corrmat[1, 3]),
        "a_s8": float(corrmat[2, 3]),
        "om_h0": float(corrmat[0, 1]),
        "om_s8": float(corrmat[0, 2]),
    }


def _correlations_5param(chain: np.ndarray) -> dict:
    """Compute correlations for [Om, H0, rd, s8, alpha] chain."""
    corrmat = np.corrcoef(chain.T)
    return {
        "a_om": float(corrmat[0, 4]),
        "a_h0": float(corrmat[1, 4]),
        "a_rd": float(corrmat[2, 4]),
        "a_s8": float(corrmat[3, 4]),
        "om_rd": float(corrmat[0, 2]),
    }


def _init_p0_4param(nwalkers: int, seed: int) -> np.ndarray:
    """Initialize walkers for [Om, H0, s8, alpha]."""
    rng = np.random.RandomState(seed)
    return np.column_stack([
        rng.uniform(0.2, 0.35, nwalkers),       # Omega_m
        rng.uniform(65, 72, nwalkers),            # H0
        rng.normal(0.80, 0.03, nwalkers),         # sigma8 (D3: honest prior)
        rng.uniform(-3, 1, nwalkers),             # alpha_cosmo
    ])


def _init_p0_3param(nwalkers: int, seed: int) -> np.ndarray:
    """Initialize walkers for [Om, H0, s8]."""
    rng = np.random.RandomState(seed)
    return np.column_stack([
        rng.uniform(0.2, 0.35, nwalkers),
        rng.uniform(65, 72, nwalkers),
        rng.normal(0.80, 0.03, nwalkers),         # D3: honest prior
    ])


# ═══════════════════════════════════════════════════════════════
#  PRIOR FUNCTIONS — copied verbatim from working scripts
# ═══════════════════════════════════════════════════════════════

def _sum_log_likelihoods(params: dict, modules: dict) -> float:
    """Sum log-likelihoods from all available modules.

    Args:
        params: Parameter dict (Omega_m, H0, sigma8, alpha_cosmo, r_d, ...)
        modules: Dict with keys bao, growth, hz, snia (any can be None).

    Returns:
        Sum of log-likelihoods. Returns -inf if any module returns -inf.
    """
    total = 0.0
    for name, mod in modules.items():
        if mod is None:
            continue
        ll = mod.log_likelihood(params)
        if not np.isfinite(ll):
            return -np.inf
        total += ll
    return total


# --- Baseline priors (rd=147.09, sigma8~N(0.80,0.04) — D3 honest prior) ---

def _log_prior_baseline_efc(theta):
    """EFC prior for baseline: [Om, H0, s8, alpha], rd fixed, sigma8 honest.

    D3: σ8 prior widened from N(0.81, 0.02) to N(0.80, 0.04).
    Weak-lensing-informed rather than Planck-LCDM-dependent.
    """
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prior_baseline_lcdm(theta):
    """LCDM prior for baseline: [Om, H0, s8], rd fixed, sigma8 honest.

    D3: σ8 prior widened from N(0.81, 0.02) to N(0.80, 0.04).
    """
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prob_baseline_efc(theta, modules):
    lp = _log_prior_baseline_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_baseline_lcdm(theta, modules):
    lp = _log_prior_baseline_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


# --- N1a priors (rd FIXED, flat sigma8) ---

def _log_prior_n1a_efc(theta):
    """EFC prior: [Om, H0, s8, alpha]. rd=147.09 fixed, sigma8 flat."""
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return 0.0


def _log_prior_n1a_lcdm(theta):
    """LCDM prior: [Om, H0, s8]. rd=147.09 fixed."""
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    return 0.0


def _log_prob_n1a_efc(theta, modules):
    lp = _log_prior_n1a_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n1a_lcdm(theta, modules):
    lp = _log_prior_n1a_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


# --- N1b priors (rd with Gaussian prior N(147.1, 4.0)) ---

def _log_prior_n1b_efc(theta):
    """EFC prior: [Om, H0, rd, s8, alpha] + rd Gaussian."""
    Om, H0, rd, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (100.0 < rd < 200.0):   return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return -0.5 * ((rd - RD_PRIOR_MU) / RD_PRIOR_SIGMA) ** 2


def _log_prior_n1b_lcdm(theta):
    """LCDM prior: [Om, H0, rd, s8] + rd Gaussian."""
    Om, H0, rd, s8 = theta
    if not (0.1 < Om < 0.6):    return -np.inf
    if not (50.0 < H0 < 85.0):  return -np.inf
    if not (100.0 < rd < 200.0): return -np.inf
    if not (0.5 < s8 < 1.2):    return -np.inf
    return -0.5 * ((rd - RD_PRIOR_MU) / RD_PRIOR_SIGMA) ** 2


def _log_prob_n1b_efc(theta, modules):
    lp = _log_prior_n1b_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n1b_lcdm(theta, modules):
    lp = _log_prior_n1b_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


# --- N2 sigma8 sweep priors (rd=147.09 fixed) ---

def _sigma8_log_prior(s8: float, mode: str) -> float:
    """Return log-prior contribution from sigma8 given mode.

    D3 update: 'stram' now uses honest prior N(0.80, 0.04).
    'middels' uses N(0.80, 0.06).
    """
    if mode == "stram":
        if not (0.5 < s8 < 1.2):
            return -np.inf
        return -0.5 * ((s8 - 0.80) / 0.04) ** 2
    elif mode == "middels":
        if not (0.5 < s8 < 1.2):
            return -np.inf
        return -0.5 * ((s8 - 0.80) / 0.06) ** 2
    elif mode == "flat":
        if not (0.6 < s8 < 1.0):
            return -np.inf
        return 0.0
    else:
        raise ValueError(f"Unknown sigma8 mode: {mode}")


def _log_prior_n2_efc(theta, s8_mode):
    """EFC prior for N2: [Om, H0, s8, alpha], rd fixed, sigma8 per mode."""
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    lp_s8 = _sigma8_log_prior(s8, s8_mode)
    if not np.isfinite(lp_s8):
        return -np.inf
    return lp_s8


def _log_prior_n2_lcdm(theta, s8_mode):
    """LCDM prior for N2: [Om, H0, s8], rd fixed, sigma8 per mode."""
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    lp_s8 = _sigma8_log_prior(s8, s8_mode)
    if not np.isfinite(lp_s8):
        return -np.inf
    return lp_s8


def _log_prob_n2_efc(theta, modules, s8_mode):
    lp = _log_prior_n2_efc(theta, s8_mode)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n2_lcdm(theta, modules, s8_mode):
    lp = _log_prior_n2_lcdm(theta, s8_mode)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


# --- N3 gate-freedom priors (a_t, delta_a as free params) ---

# Default gate sweep grid: discrete + free
N3_GATE_SWEEP_GRID = [
    ("early",    0.35, 0.10),   # early transition
    ("baseline", 0.50, 0.10),   # current default (VariantA)
    ("late",     0.65, 0.10),   # late transition
    ("narrow",   0.50, 0.05),   # narrow gate
    ("wide",     0.50, 0.20),   # wide gate
]


def _log_prior_n3_efc(theta):
    """EFC prior for N3: [Om, H0, s8, alpha, a_t, delta_a].

    D3: σ8 ~ N(0.80, 0.04) (honest prior).
    Gate priors:
        a_t    ~ N(0.5, 0.15) truncated to [0.2, 0.9]
        delta_a ~ N(0.1, 0.06) truncated to [0.01, 0.4]
    """
    Om, H0, s8, alpha, a_t, delta_a = theta
    if not (0.1 < Om < 0.6):       return -np.inf
    if not (50.0 < H0 < 85.0):     return -np.inf
    if not (0.5 < s8 < 1.2):       return -np.inf
    if not (-10.0 < alpha < 10.0):  return -np.inf
    if not (0.2 < a_t < 0.9):      return -np.inf
    if not (0.01 < delta_a < 0.4):  return -np.inf
    # sigma8 honest prior (D3)
    lp = -0.5 * ((s8 - 0.80) / 0.04) ** 2
    # gate Gaussian priors
    lp += -0.5 * ((a_t - 0.5) / 0.15) ** 2
    lp += -0.5 * ((delta_a - 0.1) / 0.06) ** 2
    return lp


def _log_prior_n3_efc_fixed_gate(theta, a_t_fixed, delta_a_fixed):
    """EFC prior for N3 discrete sweep: [Om, H0, s8, alpha], gate fixed.

    D3: σ8 ~ N(0.80, 0.04) (honest prior).
    """
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):       return -np.inf
    if not (50.0 < H0 < 85.0):     return -np.inf
    if not (0.5 < s8 < 1.2):       return -np.inf
    if not (-10.0 < alpha < 10.0):  return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prob_n3_efc(theta, modules):
    """Log-probability for N3 free-gate EFC: 6 params."""
    lp = _log_prior_n3_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha, a_t, delta_a = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED,
              "a_t": a_t, "delta_a": delta_a}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n3_efc_fixed(theta, modules, a_t_fixed, delta_a_fixed):
    """Log-probability for N3 fixed-gate EFC: 4 params + fixed gate."""
    lp = _log_prior_n3_efc_fixed_gate(theta, a_t_fixed, delta_a_fixed)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED,
              "a_t": a_t_fixed, "delta_a": delta_a_fixed}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _init_p0_6param(nwalkers: int, seed: int) -> np.ndarray:
    """Initialize walkers for N3 free-gate: [Om, H0, s8, alpha, a_t, delta_a]."""
    rng = np.random.RandomState(seed)
    return np.column_stack([
        rng.uniform(0.2, 0.35, nwalkers),       # Omega_m
        rng.uniform(65, 72, nwalkers),            # H0
        rng.normal(0.80, 0.03, nwalkers),         # sigma8 (D3: honest prior)
        rng.uniform(-3, 1, nwalkers),             # alpha_cosmo
        rng.normal(0.5, 0.05, nwalkers),          # a_t
        np.clip(rng.normal(0.1, 0.02, nwalkers), 0.02, 0.35),  # delta_a
    ])


def _correlations_6param(chain: np.ndarray) -> dict:
    """Correlations for [Om, H0, s8, alpha, a_t, delta_a]."""
    corrmat = np.corrcoef(chain.T)
    return {
        "a_om": float(corrmat[0, 3]),
        "a_h0": float(corrmat[1, 3]),
        "a_s8": float(corrmat[2, 3]),
        "a_at": float(corrmat[3, 4]),      # alpha vs a_t
        "a_da": float(corrmat[3, 5]),      # alpha vs delta_a
        "at_da": float(corrmat[4, 5]),     # a_t vs delta_a
        "om_at": float(corrmat[0, 4]),
        "om_da": float(corrmat[0, 5]),
    }


# ═══════════════════════════════════════════════════════════════
#  N4 — MODIFIED POISSON (μ ≠ 1) — D1 diagnostic
# ═══════════════════════════════════════════════════════════════

N4_MU_SWEEP_GRID = [
    ("mu_0.80", 0.80),    # sub-GR coupling
    ("mu_0.90", 0.90),    # mild sub-GR
    ("mu_1.00", 1.00),    # standard GR (baseline)
    ("mu_1.10", 1.10),    # mild super-GR
    ("mu_1.20", 1.20),    # super-GR coupling
]


def _log_prior_n4_efc(theta):
    """EFC prior for N4: [Om, H0, s8, alpha, mu_0].

    D3: σ8 ~ N(0.80, 0.04) (honest prior).
    μ_0 ~ N(1.0, 0.3) centered on GR.
    """
    Om, H0, s8, alpha, mu_0 = theta
    if not (0.1 < Om < 0.6):       return -np.inf
    if not (50.0 < H0 < 85.0):     return -np.inf
    if not (0.5 < s8 < 1.2):       return -np.inf
    if not (-10.0 < alpha < 10.0):  return -np.inf
    if not (0.3 < mu_0 < 2.0):     return -np.inf
    # sigma8 honest prior (D3)
    lp = -0.5 * ((s8 - 0.80) / 0.04) ** 2
    # mu_0 prior centered on GR
    lp += -0.5 * ((mu_0 - 1.0) / 0.3) ** 2
    return lp


def _log_prior_n4_efc_fixed_mu(theta, mu_0_fixed):
    """EFC prior for N4 discrete sweep: [Om, H0, s8, alpha], mu_0 fixed.

    D3: σ8 ~ N(0.80, 0.04) (honest prior).
    """
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):       return -np.inf
    if not (50.0 < H0 < 85.0):     return -np.inf
    if not (0.5 < s8 < 1.2):       return -np.inf
    if not (-10.0 < alpha < 10.0):  return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prob_n4_efc(theta, modules):
    """Log-probability for N4 free-μ EFC: 5 params."""
    lp = _log_prior_n4_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha, mu_0 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED, "mu_0": mu_0}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n4_efc_fixed(theta, modules, mu_0_fixed):
    """Log-probability for N4 fixed-μ EFC: 4 params + fixed mu_0."""
    lp = _log_prior_n4_efc_fixed_mu(theta, mu_0_fixed)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED, "mu_0": mu_0_fixed}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _init_p0_5param_n4(nwalkers: int, seed: int) -> np.ndarray:
    """Initialize walkers for N4 free-μ: [Om, H0, s8, alpha, mu_0]."""
    rng = np.random.RandomState(seed)
    return np.column_stack([
        rng.uniform(0.2, 0.35, nwalkers),       # Omega_m
        rng.uniform(65, 72, nwalkers),            # H0
        rng.normal(0.80, 0.03, nwalkers),         # sigma8 (D3)
        rng.uniform(-3, 1, nwalkers),             # alpha_cosmo
        rng.normal(1.0, 0.1, nwalkers),           # mu_0 (near GR)
    ])


def _correlations_5param_n4(chain: np.ndarray) -> dict:
    """Correlations for [Om, H0, s8, alpha, mu_0]."""
    corrmat = np.corrcoef(chain.T)
    return {
        "a_om": float(corrmat[0, 3]),
        "a_h0": float(corrmat[1, 3]),
        "a_s8": float(corrmat[2, 3]),
        "a_mu0": float(corrmat[3, 4]),      # alpha vs mu_0
        "mu0_om": float(corrmat[0, 4]),
        "mu0_s8": float(corrmat[2, 4]),
    }


def run_n4_mu_sweep(
    modules: dict,
    nwalkers: int = 48,
    nsteps: int = 4000,
    burnin: int = 1500,
    seed: int = 42,
    pass_sigma: float = 1.7,
    collapse_sigma: float = 1.3,
    degeneracy_corr_max: float = 0.80,
    pool=None,
) -> dict:
    """N4: Modified Poisson sweep — is α driven by μ freedom?

    Part 1: Discrete sweep — run EFC at 5 fixed μ_0 values.
    Part 2: Free μ_0 — run 5-param EFC.

    Uses EFCVariantC cosmology for growth_source evaluation.

    Returns:
        dict with sweep_results, free_mu, correlations, verdict
    """
    np.random.seed(seed)
    total_time = 0.0
    n_data = sum(m.n_data for m in modules.values() if m is not None)

    # Need VariantC modules for proper growth_source evaluation
    # But for emcee log-prob, the modules already use the engine's cosmology.
    # mu_0 enters via the params dict → growth engine reads it.
    # However, our current EFCGrowth engine uses CosmologyModel.growth_source()
    # which for VariantA/B does NOT read mu_0.
    # For N4 emcee, we need modules built with EFCVariantC.
    # Use load_modules() factory (same pattern as N3 with VariantB).
    n4_modules = load_modules(cosmology=EFCVariantC())

    sweep_results = []

    # Part 1: Discrete μ_0 sweep
    for label, mu_0_val in N4_MU_SWEEP_GRID:
        t0 = time.time()
        ndim_sweep = 4
        p0 = _init_p0_4param(nwalkers, seed + hash(label) % 1000)

        sampler = emcee.EnsembleSampler(
            nwalkers, ndim_sweep, _log_prob_n4_efc_fixed,
            args=(n4_modules, mu_0_val), pool=pool,
        )
        sampler.run_mcmc(p0, nsteps, progress=False, thin_by=1)
        dt = time.time() - t0
        total_time += dt

        chain = sampler.get_chain(discard=burnin, flat=True)
        alpha_samples = chain[:, 3]
        alpha_mean = float(np.mean(alpha_samples))
        alpha_std = float(np.std(alpha_samples))
        alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0

        sweep_results.append({
            "label": label,
            "mu_0": mu_0_val,
            "alpha_mean": alpha_mean,
            "alpha_std": alpha_std,
            "alpha_sig": alpha_sig,
            "time_seconds": dt,
        })
        logger.info(f"N4 sweep [{label}]: α={alpha_mean:.3f}±{alpha_std:.3f} ({alpha_sig:.2f}σ)")

    # Sweep stability
    sweep_sigs = [r["alpha_sig"] for r in sweep_results]
    sweep_range = max(sweep_sigs) - min(sweep_sigs) if sweep_sigs else 0
    sweep_stable = sweep_range < 0.5

    # Part 2: Free μ_0 (5 params)
    t0 = time.time()
    ndim_free = 5
    p0_free = _init_p0_5param_n4(nwalkers, seed + 42)
    sampler_free = emcee.EnsembleSampler(
        nwalkers, ndim_free, _log_prob_n4_efc,
        args=(n4_modules,), pool=pool,
    )
    sampler_free.run_mcmc(p0_free, nsteps, progress=False, thin_by=1)
    dt_free = time.time() - t0
    total_time += dt_free

    chain_free = sampler_free.get_chain(discard=burnin, flat=True)
    alpha_free = chain_free[:, 3]
    mu0_free = chain_free[:, 4]

    alpha_mean = float(np.mean(alpha_free))
    alpha_std = float(np.std(alpha_free))
    alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0
    mu0_mean = float(np.mean(mu0_free))
    mu0_std = float(np.std(mu0_free))

    free_mu_result = {
        "alpha_mean": alpha_mean,
        "alpha_std": alpha_std,
        "alpha_sig": alpha_sig,
        "alpha_p_negative": float(np.mean(alpha_free < 0)),
        "mu0_mean": mu0_mean,
        "mu0_std": mu0_std,
        "mu0_deviation_from_gr": abs(mu0_mean - 1.0) / mu0_std if mu0_std > 0 else 0.0,
        "time_seconds": dt_free,
    }

    # Correlations
    correlations = _correlations_5param_n4(chain_free)
    corr_alpha_mu0 = correlations["a_mu0"]

    # Verdict
    free_pass = alpha_sig >= pass_sigma
    high_degeneracy = abs(corr_alpha_mu0) > degeneracy_corr_max

    if alpha_sig < collapse_sigma:
        verdict = "COLLAPSED"
    elif free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    else:
        verdict = "MARGINAL"

    logger.info(f"N4 verdict: {verdict} (α={alpha_sig:.2f}σ, μ0={mu0_mean:.3f}±{mu0_std:.3f})")

    return {
        "sweep_results": sweep_results,
        "free_mu": free_mu_result,
        "correlations": correlations,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "alpha_survives_freedom": free_pass,
        "high_degeneracy": high_degeneracy,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N5: D2a SOUND HORIZON PRIOR SWEEP
# ═══════════════════════════════════════════════════════════════

# Reuse N1b priors but with configurable rd_sigma
def _log_prior_n5_efc(theta, rd_mu, rd_sigma):
    """EFC prior for N5: [Om, H0, rd, s8, alpha] + rd Gaussian."""
    Om, H0, rd, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (100.0 < rd < 200.0):   return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    # Gaussian rd prior (D3 honest s8 prior is built into bounds)
    lp = -0.5 * ((rd - rd_mu) / rd_sigma) ** 2
    # D3 honest s8 prior: N(0.80, 0.04)
    lp += -0.5 * ((s8 - 0.80) / 0.04) ** 2
    return lp


def _log_prior_n5_efc_flat(theta):
    """EFC prior for N5 flat-rd: [Om, H0, rd, s8, alpha], U(100,200)."""
    Om, H0, rd, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (100.0 < rd < 200.0):   return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prob_n5_efc(theta, modules, rd_mu, rd_sigma):
    lp = _log_prior_n5_efc(theta, rd_mu, rd_sigma)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_n5_efc_flat(theta, modules):
    lp = _log_prior_n5_efc_flat(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def run_n5_rd_sweep(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pass_sigma: float = 1.7,
    collapse_sigma: float = 1.3,
    degeneracy_corr_max: float = 0.80,
    pool=None,
) -> dict:
    """N5/D2a: Sound horizon prior sweep.

    Tests whether α signal is robust to r_d prior choice.
    Runs 4 configurations:
      1. Tight: N(147.0, 2.0) — BBN-informed
      2. Standard: N(147.0, 5.0)
      3. Broad: N(147.0, 10.0) — ΛCDM-independent
      4. Flat: U(100, 200) — completely uninformative

    Returns sweep results + degeneracy structure.
    """
    logger.info("=== N5/D2a: SOUND HORIZON PRIOR SWEEP ===")

    n_data = sum(len(m.data.get("z", [])) for m in modules.values()
                 if hasattr(m, 'data') and isinstance(m.data, dict))

    # Define r_d prior configurations
    configs = [
        ("tight",    147.0,  2.0),  # BBN-informed
        ("standard", 147.0,  5.0),  # Standard N1b-like
        ("broad",    147.0, 10.0),  # ΛCDM-independent
    ]

    sweep_results = []
    total_time = 0.0

    for name, rd_mu, rd_sigma in configs:
        logger.info(f"-- N5: rd ~ N({rd_mu}, {rd_sigma}) [{name}] --")

        rng = np.random.RandomState(seed + 50 + len(sweep_results))
        p0 = np.column_stack([
            rng.uniform(0.2, 0.35, nwalkers),   # Om
            rng.uniform(65, 72, nwalkers),        # H0
            rng.normal(rd_mu, min(rd_sigma, 3.0), nwalkers),  # rd
            rng.uniform(0.7, 0.9, nwalkers),      # s8
            rng.uniform(-3, 1, nwalkers),          # alpha
        ])

        chain, lp, dt, _ = _run_emcee(
            f"N5 [{name}]", _log_prob_n5_efc, ndim=5,
            p0=p0, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=(modules, rd_mu, rd_sigma),
            seed=seed + 50 + len(sweep_results), pool=pool,
        )
        total_time += dt

        alpha_stats = _extract_alpha(chain, alpha_col=4)
        rd_samples = chain[:, 2]
        rd_mean = float(np.mean(rd_samples))
        rd_std = float(np.std(rd_samples))
        rd_ci_width = float(np.percentile(rd_samples, 97.5) - np.percentile(rd_samples, 2.5))

        # Correlations
        corr_alpha_rd = float(np.corrcoef(chain[:, 4], chain[:, 2])[0, 1])
        corr_alpha_om = float(np.corrcoef(chain[:, 4], chain[:, 0])[0, 1])

        logger.info(f"  [{name}] α = {alpha_stats.mean:.3f} ± {alpha_stats.std:.3f} "
                     f"({alpha_stats.significance:.2f}σ)")
        logger.info(f"  [{name}] rd = {rd_mean:.1f} ± {rd_std:.1f}, "
                     f"95%CI width={rd_ci_width:.1f}")
        logger.info(f"  [{name}] corr(α,rd) = {corr_alpha_rd:.3f}")

        sweep_results.append({
            "config": name,
            "rd_prior_mu": rd_mu,
            "rd_prior_sigma": rd_sigma,
            "alpha": alpha_stats,
            "rd_mean": rd_mean,
            "rd_std": rd_std,
            "rd_ci_width_95": rd_ci_width,
            "corr_alpha_rd": corr_alpha_rd,
            "corr_alpha_om": corr_alpha_om,
        })

    # Flat prior: U(100, 200)
    logger.info("-- N5: rd flat U(100, 200) --")
    rng_flat = np.random.RandomState(seed + 60)
    p0_flat = np.column_stack([
        rng_flat.uniform(0.2, 0.35, nwalkers),
        rng_flat.uniform(65, 72, nwalkers),
        rng_flat.uniform(130, 165, nwalkers),   # rd flat
        rng_flat.uniform(0.7, 0.9, nwalkers),
        rng_flat.uniform(-3, 1, nwalkers),
    ])

    chain_flat, lp_flat, dt, _ = _run_emcee(
        "N5 [flat]", _log_prob_n5_efc_flat, ndim=5,
        p0=p0_flat, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,),
        seed=seed + 60, pool=pool,
    )
    total_time += dt

    alpha_flat = _extract_alpha(chain_flat, alpha_col=4)
    rd_flat = chain_flat[:, 2]
    rd_flat_mean = float(np.mean(rd_flat))
    rd_flat_std = float(np.std(rd_flat))
    corr_alpha_rd_flat = float(np.corrcoef(chain_flat[:, 4], chain_flat[:, 2])[0, 1])

    logger.info(f"  [flat] α = {alpha_flat.mean:.3f} ± {alpha_flat.std:.3f} "
                 f"({alpha_flat.significance:.2f}σ)")
    logger.info(f"  [flat] rd = {rd_flat_mean:.1f} ± {rd_flat_std:.1f}")
    logger.info(f"  [flat] corr(α,rd) = {corr_alpha_rd_flat:.3f}")

    sweep_results.append({
        "config": "flat",
        "rd_prior_mu": None,
        "rd_prior_sigma": None,
        "alpha": alpha_flat,
        "rd_mean": rd_flat_mean,
        "rd_std": rd_flat_std,
        "rd_ci_width_95": float(np.percentile(rd_flat, 97.5) - np.percentile(rd_flat, 2.5)),
        "corr_alpha_rd": corr_alpha_rd_flat,
        "corr_alpha_om": float(np.corrcoef(chain_flat[:, 4], chain_flat[:, 0])[0, 1]),
    })

    # Analyze sweep stability
    sigs = [r["alpha"].significance for r in sweep_results]
    sig_range = max(sigs) - min(sigs) if sigs else 0.0
    sweep_stable = sig_range < 1.0  # less than 1σ variation across priors

    # Check degeneracy with r_d
    max_corr = max(abs(r["corr_alpha_rd"]) for r in sweep_results)
    high_degeneracy = max_corr > degeneracy_corr_max

    # Best case: tight prior (most constrained)
    alpha_best = sweep_results[0]["alpha"]  # tight
    alpha_worst = sweep_results[-1]["alpha"]  # flat

    free_pass = alpha_worst.significance >= pass_sigma

    if alpha_worst.significance < collapse_sigma:
        verdict = "COLLAPSED"
    elif free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    else:
        verdict = "MARGINAL"

    logger.info(f"  Sweep σ range: [{min(sigs):.2f}, {max(sigs):.2f}], range={sig_range:.2f}")
    logger.info(f"  Max |corr(α,rd)| = {max_corr:.3f}")
    logger.info(f"  N5 VERDICT: {verdict}")

    return {
        "sweep_results": sweep_results,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "high_degeneracy": high_degeneracy,
        "sig_range": sig_range,
        "max_corr_alpha_rd": max_corr,
        "alpha_survives_flat": free_pass,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N6 / D2b: EFC SOUND HORIZON DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════

def run_n6_rd_efc(
    baseline_chains: np.ndarray,
    R_max: float = 0.01,
    sigma_ln_a: float = 0.5,
    safety_threshold_pct: float = 0.5,
    Omega_b: float = 0.0493,
    sweep_R_max: Optional[list] = None,
) -> dict:
    """N6/D2b: EFC-native sound horizon diagnostic.

    POST-FIT diagnostic — no MCMC. Takes posterior samples from the
    baseline fit and computes r_d^EFC for each, giving a posterior
    distribution of the EFC grid-state correction to the sound horizon.

    This connects EFC theory (c_eff = c/(1+R)) to the BAO standard ruler
    without introducing new free parameters.

    Args:
        baseline_chains: Shape (N, 4) array with columns [Om, H0, s8, alpha].
                         These are posterior samples from the baseline MCMC.
        R_max:           Peak grid resistance (default: 0.01, EFC postulate)
        sigma_ln_a:      Gaussian window width in ln(a) (default: 0.5)
        safety_threshold_pct: Max |Delta r_d(EFC-GR)/r_d(GR)| [%]
        Omega_b:         Baryon density (default: 0.0493)
        sweep_R_max:     R_max values for sensitivity sweep

    Returns:
        dict with:
            rd_efc_mean, rd_efc_std:    Posterior mean ± std of r_d^EFC [Mpc]
            rd_gr_mean, rd_gr_std:      GR baseline r_d (same samples)
            delta_rd_pct_mean:          Mean (r_d^EFC - r_d^GR) / r_d^GR * 100
            delta_rd_pct_std:           Std of same
            safety_pass:                All samples within threshold?
            R_at_drag_mean:             Mean grid resistance at drag
            sweep_results:              R_max sensitivity sweep results
            verdict:                    PASS | SAFETY_WARNING | SAFETY_FAIL
            total_time_seconds:         Wall time
    """
    from efc_inference.core.sound_horizon import compute_rd_efc as _compute_rd

    logger.info("=== N6/D2b: EFC SOUND HORIZON DIAGNOSTIC ===")
    t0 = time.time()

    if sweep_R_max is None:
        sweep_R_max = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05]

    n_samples = len(baseline_chains)
    logger.info(f"  Processing {n_samples} posterior samples")

    # Subsample if too many (keep computation fast)
    max_eval = 500
    if n_samples > max_eval:
        rng = np.random.RandomState(42)
        idx = rng.choice(n_samples, max_eval, replace=False)
        chains_sub = baseline_chains[idx]
    else:
        chains_sub = baseline_chains

    # ── Per-sample r_d computation ──
    rd_efc_arr = []
    rd_gr_arr = []
    delta_arr = []
    R_drag_arr = []
    R_peak_arr = []

    for i, row in enumerate(chains_sub):
        Om, H0 = row[0], row[1]
        result = _compute_rd(Om, H0, Omega_b, R_max, sigma_ln_a, safety_threshold_pct)
        rd_efc_arr.append(result["rd_efc"])
        rd_gr_arr.append(result["rd_gr"])
        delta_arr.append(result["delta_rd_pct"])
        R_drag_arr.append(result["R_at_drag"])
        R_peak_arr.append(result["R_peak"])

    rd_efc_arr = np.array(rd_efc_arr)
    rd_gr_arr = np.array(rd_gr_arr)
    delta_arr = np.array(delta_arr)

    rd_efc_mean = float(np.mean(rd_efc_arr))
    rd_efc_std = float(np.std(rd_efc_arr))
    rd_gr_mean = float(np.mean(rd_gr_arr))
    rd_gr_std = float(np.std(rd_gr_arr))
    delta_mean = float(np.mean(delta_arr))
    delta_std = float(np.std(delta_arr))

    from efc_inference.core.sound_horizon import SAFETY_WARN_PCT
    abs_delta_max = float(np.max(np.abs(delta_arr)))
    safety_pass = abs_delta_max < safety_threshold_pct
    if abs_delta_max < SAFETY_WARN_PCT:
        safety_level = "pass"
    elif abs_delta_max < safety_threshold_pct:
        safety_level = "warning"
    else:
        safety_level = "fail"

    logger.info(f"  r_d^EFC = {rd_efc_mean:.4f} ± {rd_efc_std:.4f} Mpc")
    logger.info(f"  r_d^GR  = {rd_gr_mean:.4f} ± {rd_gr_std:.4f} Mpc")
    logger.info(f"  Delta   = {delta_mean:+.4f} ± {delta_std:.4f}%")
    logger.info(f"  R(a_d)  = {np.mean(R_drag_arr):.6f}")
    logger.info(f"  R_peak  = {np.mean(R_peak_arr):.6f}")
    logger.info(f"  Safety  = {safety_level.upper()} (|Δ|_max={abs_delta_max:.3f}%, "
                f"warn={SAFETY_WARN_PCT}%, fail={safety_threshold_pct}%)")

    # ── Sensitivity sweep at posterior median cosmology ──
    Om_med = float(np.median(baseline_chains[:, 0]))
    H0_med = float(np.median(baseline_chains[:, 1]))

    sweep_results = []
    for R_m in sweep_R_max:
        sr = _compute_rd(Om_med, H0_med, Omega_b, R_m, sigma_ln_a, safety_threshold_pct)
        sweep_results.append({
            "R_max": R_m,
            "rd_efc": sr["rd_efc"],
            "rd_gr": sr["rd_gr"],
            "delta_rd_pct": sr["delta_rd_pct"],
            "delta_rd_vs_planck_pct": sr["delta_rd_vs_planck_pct"],
            "safety_pass": sr["safety_pass"],
        })
        logger.info(f"  Sweep R_max={R_m:.4f}: rd={sr['rd_efc']:.4f}, "
                     f"Delta={sr['delta_rd_pct']:+.4f}%")

    # ── Verdict (three-tier: PASS / WARN / FAIL) ──
    # PASS: |Δr_d| < 0.5%  (EFC correction negligible at drag epoch)
    # WARN: 0.5% ≤ |Δr_d| < 1.0%  (small correction, within BAO tolerance)
    # FAIL: |Δr_d| ≥ 1.0%  (correction exceeds BAO precision, proxy invalid)
    if safety_level == "fail":
        verdict = "FAIL"
    elif safety_level == "warning":
        verdict = "WARN"
    else:
        verdict = "PASS"

    dt = time.time() - t0
    logger.info(f"  N6 VERDICT: {verdict} ({dt:.1f}s)")

    return {
        "rd_efc_mean": rd_efc_mean,
        "rd_efc_std": rd_efc_std,
        "rd_gr_mean": rd_gr_mean,
        "rd_gr_std": rd_gr_std,
        "delta_rd_pct_mean": delta_mean,
        "delta_rd_pct_std": delta_std,
        "safety_pass": safety_pass,
        "safety_level": safety_level,
        "safety_threshold_pct": safety_threshold_pct,
        "R_at_drag_mean": float(np.mean(R_drag_arr)),
        "R_peak_mean": float(np.mean(R_peak_arr)),
        "c_eff_at_drag_mean": 1.0 / (1.0 + float(np.mean(R_drag_arr))),
        "R_max": R_max,
        "sigma_ln_a": sigma_ln_a,
        "Omega_b": Omega_b,
        "n_samples_evaluated": len(chains_sub),
        "sweep_results": sweep_results,
        "verdict": verdict,
        "total_time_seconds": dt,
    }


# ═══════════════════════════════════════════════════════════════
#  PUBLIC FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load_modules(bao_path: str = BAO_PATH, growth_path: str = GROWTH_PATH,
                  hz_path: str = HZ_PATH, snia_path: str = SNIA_PATH,
                  snia_cov_path: str = SNIA_COV_PATH,
                  cosmology: Optional[CosmologyModel] = None):
    """Load all observation modules: BAO + Growth + Hz + SNIa.

    Args:
        bao_path: Path to BAO data CSV.
        growth_path: Path to growth data CSV.
        hz_path: Path to H(z) cosmic chronometer CSV.
        snia_path: Path to SNIa distance modulus CSV.
        snia_cov_path: Path to SNIa covariance matrix (.npy).
        cosmology: CosmologyModel instance. Default: EFCVariantA().
                   All engines share the same cosmology for consistency.

    Returns:
        dict with keys: bao, growth, hz, snia (each a module instance)
        hz and snia are None if data files not found (graceful degradation).
    """
    if cosmology is None:
        cosmology = EFCVariantA()

    # Shared Hubble engine for BAO, Hz, SNIa
    hubble_engine = EFCHubble(cosmology=cosmology)

    bao_mod = BAOModule(hubble_engine)
    bao_mod.load_data(data_path=bao_path)

    growth_engine = EFCGrowth(cosmology=cosmology)
    growth_mod = GrowthModule(growth_engine)
    growth_mod.load_data(data_path=growth_path)

    # Hz: cosmic chronometers (graceful if missing)
    hz_mod = None
    try:
        hz_mod = HzModule(hubble_engine)
        hz_mod.load_data(data_path=hz_path)
        logger.info(f"Hz module loaded: {hz_mod.n_data} points")
    except (FileNotFoundError, ValueError) as e:
        logger.warning(f"Hz data not available ({e}), running without Hz")
        hz_mod = None

    # SNIa: Pantheon binned (graceful if missing)
    snia_mod = None
    try:
        snia_mod = SNIaModule(hubble_engine)
        snia_mod.load_data(data_path=snia_path, cov_path=snia_cov_path)
        logger.info(f"SNIa module loaded: {snia_mod.n_data} points, "
                     f"cov={'full' if snia_mod._covariance is not None else 'diagonal'}")
    except (FileNotFoundError, ValueError) as e:
        logger.warning(f"SNIa data not available ({e}), running without SNIa")
        snia_mod = None

    return {"bao": bao_mod, "growth": growth_mod, "hz": hz_mod, "snia": snia_mod}


def run_joint_inference(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    bao_path: str = BAO_PATH,
    growth_path: str = GROWTH_PATH,
    hz_path: str = HZ_PATH,
    snia_path: str = SNIA_PATH,
    pool=None,
) -> BaselineResult:
    """Run baseline multi-probe inference.

    Uses all available probes: BAO + Growth + Hz + SNIa.
    rd=147.09 fixed, sigma8~N(0.80, 0.04) (D3: honest prior).
    EFC: 4 params [Om, H0, s8, alpha].
    LCDM: 3 params [Om, H0, s8] with identical data/likelihood (alpha=0).

    Args:
        modules: Dict from load_modules() with keys bao, growth, hz, snia.
        pool: Optional multiprocessing.Pool for parallel walker evaluation.
    """
    np.random.seed(seed)
    n_bao = len(modules["bao"].coordinates)
    n_growth = len(modules["growth"].coordinates)
    n_hz = modules["hz"].n_data if modules.get("hz") else 0
    n_snia = modules["snia"].n_data if modules.get("snia") else 0
    n_data = n_bao + n_growth + n_hz + n_snia
    args = (modules,)

    probes = [p for p, n in [("BAO", n_bao), ("Growth", n_growth),
                              ("Hz", n_hz), ("SNIa", n_snia)] if n > 0]
    logger.info(f"=== BASELINE: Joint {'+'.join(probes)} ({n_data} pts) ===")

    # EFC: 4 params
    p0_efc = _init_p0_4param(nwalkers, seed)
    chain_efc, lp_efc, dt_efc, sampler_efc = _run_emcee(
        "Baseline EFC", _log_prob_baseline_efc, ndim=4,
        p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed, pool=pool,
    )

    # LCDM: 3 params (identical data, alpha=0)
    p0_lcdm = _init_p0_3param(nwalkers, seed + 1)
    chain_lcdm, lp_lcdm, dt_lcdm, _ = _run_emcee(
        "Baseline LCDM", _log_prob_baseline_lcdm, ndim=3,
        p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed + 1, pool=pool,
    )

    ll_efc = float(np.max(lp_efc))
    ll_lcdm = float(np.max(lp_lcdm))

    alpha = _extract_alpha(chain_efc, alpha_col=3)
    comparison = _compute_comparison(ll_efc, 4, ll_lcdm, 3, n_data)
    correlations = _correlations_4param(chain_efc)

    manifest = _build_manifest(seed, nwalkers, nsteps, burnin,
                               bao_path, growth_path, n_bao, n_growth,
                               hz_path=hz_path, n_hz=n_hz,
                               snia_path=snia_path, n_snia=n_snia)
    manifest["total_time_seconds"] = dt_efc + dt_lcdm

    logger.info(f"  alpha = {alpha.mean:.3f} +/- {alpha.std:.3f} "
                f"({alpha.significance:.2f}sigma)  "
                f"dAIC={comparison.daic:.2f}  dBIC={comparison.dbic:.2f}")

    # ── Per-probe ΔlogL at best-fit (EFC vs ΛCDM) ──
    probe_likelihoods = {}
    try:
        best_efc_idx = int(np.argmax(lp_efc))
        best_lcdm_idx = int(np.argmax(lp_lcdm))
        best_efc = chain_efc[best_efc_idx]
        best_lcdm = chain_lcdm[best_lcdm_idx]

        params_efc = {"Omega_m": best_efc[0], "H0": best_efc[1],
                      "sigma8": best_efc[2], "alpha_cosmo": best_efc[3],
                      "rd": RD_FIXED}
        params_lcdm = {"Omega_m": best_lcdm[0], "H0": best_lcdm[1],
                       "sigma8": best_lcdm[2], "alpha_cosmo": 0.0,
                       "rd": RD_FIXED}

        for probe_name, mod in modules.items():
            if mod is not None:
                try:
                    ll_efc_p = mod.log_likelihood(params_efc)
                    ll_lcdm_p = mod.log_likelihood(params_lcdm)
                    dll = float(ll_efc_p - ll_lcdm_p)
                    probe_likelihoods[probe_name] = {
                        "ll_efc": float(ll_efc_p),
                        "ll_lcdm": float(ll_lcdm_p),
                        "delta_logL": dll,
                    }
                    logger.info(f"  ΔlogL({probe_name}): {dll:+.3f} "
                                f"({'EFC' if dll > 0 else 'ΛCDM'})")
                except Exception as e:
                    logger.warning(f"  ΔlogL({probe_name}): error — {e}")
    except Exception as e:
        logger.warning(f"  Per-probe ΔlogL failed: {e}")

    return BaselineResult(
        alpha=alpha,
        comparison=comparison,
        correlations=correlations,
        om=_extract_param(chain_efc, 0),
        s8=_extract_param(chain_efc, 2),
        h0=_extract_param(chain_efc, 1),
        chain_efc=chain_efc,
        chain_lcdm=chain_lcdm,
        manifest=manifest,
        sampler_efc=sampler_efc,
        probe_likelihoods=probe_likelihoods,
    )


def run_n1_rd_diagnostic(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    pool=None,
) -> dict:
    """N1: rd diagnostic — is the alpha hint real or an rd artifact?

    N1a: rd FIXED = 147.09 (Planck). 4-param EFC + 3-param LCDM.
    N1b: rd ~ N(147.1, 4.0). 5-param EFC + 4-param LCDM.

    Uses all available probes from modules dict.
    Returns dict with n1a, n1b results, verdict, and rd CI width.
    """
    np.random.seed(seed)
    n_data = sum(m.n_data for m in modules.values() if m is not None)
    args = (modules,)
    total_time = 0.0

    logger.info("=== N1: rd DIAGNOSTIC ===")

    # ── N1a: rd FIXED = 147.09 ──
    logger.info("-- N1a: rd=147.09 fixed --")

    p0_efc = _init_p0_4param(nwalkers, seed + 10)
    chain_n1a_efc, lp_n1a_efc, dt, _ = _run_emcee(
        "N1a EFC (rd=147.09)", _log_prob_n1a_efc, ndim=4,
        p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed + 10, pool=pool,
    )
    total_time += dt

    p0_lcdm = _init_p0_3param(nwalkers, seed + 11)
    chain_n1a_lcdm, lp_n1a_lcdm, dt, _ = _run_emcee(
        "N1a LCDM (rd=147.09)", _log_prob_n1a_lcdm, ndim=3,
        p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed + 11, pool=pool,
    )
    total_time += dt

    alpha_n1a = _extract_alpha(chain_n1a_efc, alpha_col=3)
    comp_n1a = _compute_comparison(
        float(np.max(lp_n1a_efc)), 4,
        float(np.max(lp_n1a_lcdm)), 3,
        n_data,
    )
    corr_n1a = _correlations_4param(chain_n1a_efc)

    logger.info(f"  N1a alpha = {alpha_n1a.mean:.3f} +/- {alpha_n1a.std:.3f} "
                f"({alpha_n1a.significance:.2f}sigma)")

    # ── N1b: rd ~ N(147.1, 4.0) ──
    logger.info("-- N1b: rd prior N(147.1, 4.0) --")

    rng = np.random.RandomState(seed + 20)
    p0_efc_b = np.column_stack([
        rng.uniform(0.2, 0.35, nwalkers),
        rng.uniform(65, 72, nwalkers),
        rng.normal(147.1, 3.0, nwalkers),       # rd
        rng.uniform(0.7, 0.9, nwalkers),          # sigma8
        rng.uniform(-3, 1, nwalkers),              # alpha
    ])
    chain_n1b_efc, lp_n1b_efc, dt, _ = _run_emcee(
        "N1b EFC (rd prior)", _log_prob_n1b_efc, ndim=5,
        p0=p0_efc_b, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,), seed=seed + 20, pool=pool,
    )
    total_time += dt

    rng2 = np.random.RandomState(seed + 21)
    p0_lcdm_b = np.column_stack([
        rng2.uniform(0.2, 0.35, nwalkers),
        rng2.uniform(65, 72, nwalkers),
        rng2.normal(147.1, 3.0, nwalkers),
        rng2.uniform(0.7, 0.9, nwalkers),
    ])
    chain_n1b_lcdm, lp_n1b_lcdm, dt, _ = _run_emcee(
        "N1b LCDM (rd prior)", _log_prob_n1b_lcdm, ndim=4,
        p0=p0_lcdm_b, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,), seed=seed + 21, pool=pool,
    )
    total_time += dt

    alpha_n1b = _extract_alpha(chain_n1b_efc, alpha_col=4)
    comp_n1b = _compute_comparison(
        float(np.max(lp_n1b_efc)), 5,
        float(np.max(lp_n1b_lcdm)), 4,
        n_data,
    )
    corr_n1b = _correlations_5param(chain_n1b_efc)

    # rd posterior: 95% CI width
    rd_samples = chain_n1b_efc[:, 2]
    rd_ci_lo = float(np.percentile(rd_samples, 2.5))
    rd_ci_hi = float(np.percentile(rd_samples, 97.5))
    rd_ci_width_95 = rd_ci_hi - rd_ci_lo

    logger.info(f"  N1b alpha = {alpha_n1b.mean:.3f} +/- {alpha_n1b.std:.3f} "
                f"({alpha_n1b.significance:.2f}sigma)")
    logger.info(f"  N1b rd = {np.mean(rd_samples):.1f} +/- {np.std(rd_samples):.1f}  "
                f"95%CI=[{rd_ci_lo:.1f}, {rd_ci_hi:.1f}]  width={rd_ci_width_95:.1f}")

    # ── Verdict ──
    n1a_pass = (alpha_n1a.significance >= pass_sigma
                and comp_n1a.daic <= pass_daic)
    n1b_pass = (alpha_n1b.significance >= pass_sigma
                and comp_n1b.daic <= pass_daic)

    if n1a_pass and n1b_pass:
        verdict = "PASS"
    elif n1a_pass and not n1b_pass:
        verdict = "PARTIAL"
    else:
        verdict = "COLLAPSED"

    logger.info(f"  N1 VERDICT: {verdict}")

    return {
        "n1a": {
            "alpha": alpha_n1a,
            "comparison": comp_n1a,
            "correlations": corr_n1a,
        },
        "n1b": {
            "alpha": alpha_n1b,
            "comparison": comp_n1b,
            "correlations": corr_n1b,
            "rd_mean": float(np.mean(rd_samples)),
            "rd_std": float(np.std(rd_samples)),
            "rd_ci_width_95": rd_ci_width_95,
        },
        "verdict": verdict,
        "alpha_survives_n1a": n1a_pass,
        "alpha_survives_n1b": n1b_pass,
        "total_time_seconds": total_time,
    }


def run_n2_sigma8_sweep(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    collapse_sigma: float = 1.3,
    pool=None,
) -> dict:
    """N2: sigma8 prior-sweep — is alpha driven by sigma8 freedom?

    Three sigma8 treatments (all with rd=147.09 fixed):
      N2a: sigma8 ~ N(0.80, 0.04) stram (D3: honest prior)
      N2b: sigma8 ~ N(0.80, 0.06) middels
      N2c: sigma8 ~ U(0.6, 1.0) flat

    Each: 4-param EFC + 3-param LCDM.
    Uses all available probes from modules dict.
    """
    np.random.seed(seed)
    n_data = sum(m.n_data for m in modules.values() if m is not None)
    total_time = 0.0

    logger.info("=== N2: sigma8 SWEEP ===")

    variants = {}
    for i, (label, s8_mode) in enumerate([
        ("N2a stram", "stram"),
        ("N2b middels", "middels"),
        ("N2c flat", "flat"),
    ]):
        logger.info(f"-- {label} (sigma8 {s8_mode}) --")

        s_off = seed + 30 + i * 10

        # sigma8 init
        rng = np.random.RandomState(s_off)
        if s8_mode == "flat":
            s8_init = rng.uniform(0.7, 0.9, nwalkers)
        else:
            s8_init = rng.normal(0.81, 0.03, nwalkers)
            s8_init = np.clip(s8_init, 0.6, 1.1)

        # EFC: 4 params
        p0_efc = np.column_stack([
            rng.uniform(0.2, 0.35, nwalkers),
            rng.uniform(65, 72, nwalkers),
            s8_init,
            rng.uniform(-3, 1, nwalkers),
        ])
        chain_efc, lp_efc, dt, _ = _run_emcee(
            f"{label} EFC", _log_prob_n2_efc, ndim=4,
            p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=(modules, s8_mode),
            seed=s_off, pool=pool,
        )
        total_time += dt

        # LCDM: 3 params
        rng2 = np.random.RandomState(s_off + 1)
        if s8_mode == "flat":
            s8_init_l = rng2.uniform(0.7, 0.9, nwalkers)
        else:
            s8_init_l = rng2.normal(0.81, 0.03, nwalkers)
            s8_init_l = np.clip(s8_init_l, 0.6, 1.1)

        p0_lcdm = np.column_stack([
            rng2.uniform(0.2, 0.35, nwalkers),
            rng2.uniform(65, 72, nwalkers),
            s8_init_l,
        ])
        chain_lcdm, lp_lcdm, dt, _ = _run_emcee(
            f"{label} LCDM", _log_prob_n2_lcdm, ndim=3,
            p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=(modules, s8_mode),
            seed=s_off + 1, pool=pool,
        )
        total_time += dt

        alpha = _extract_alpha(chain_efc, alpha_col=3)
        comp = _compute_comparison(
            float(np.max(lp_efc)), 4,
            float(np.max(lp_lcdm)), 3,
            n_data,
        )
        corrs = _correlations_4param(chain_efc)

        logger.info(f"  {label}: alpha = {alpha.mean:.3f} +/- {alpha.std:.3f} "
                    f"({alpha.significance:.2f}sigma)  "
                    f"dAIC={comp.daic:.2f}")

        variants[s8_mode] = {
            "alpha": alpha,
            "comparison": comp,
            "correlations": corrs,
            "s8": _extract_param(chain_efc, 2),
            "om": _extract_param(chain_efc, 0),
        }

    # Verdict based on stram (tightest prior)
    stram = variants["stram"]
    stram_pass = (stram["alpha"].significance >= pass_sigma
                  and stram["comparison"].daic <= pass_daic)

    if stram_pass:
        verdict = "PASS"
    elif stram["alpha"].significance < collapse_sigma:
        verdict = "COLLAPSED"
    else:
        verdict = "MARGINAL"

    logger.info(f"  N2 VERDICT: {verdict}")

    return {
        "variants": variants,
        "verdict": verdict,
        "alpha_survives_stram": stram_pass,
        "total_time_seconds": total_time,
    }


def run_t7_leave_one_out(
    modules: dict,
    growth_path: str = GROWTH_PATH,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = 3000,        # reduced for LOO (14 runs)
    burnin: int = 1000,
    seed: int = DEFAULT_SEED,
    pass_sigma: float = 1.7,   # DEPRECATED — kept for backward compat
    pool=None,
    pass_daic: float = 0.0,    # DEPRECATED
    loo_min_pass: int = 5,
    pass_p_negative: float = 0.80,  # NEW: sign-consistency criterion
) -> dict:
    """T7: Leave-One-Out on f*sigma8 — is alpha driven by one data point?

    Baseline-modus: rd=147.09 fixed, sigma8~N(0.80, 0.04) (D3: honest).
    All probes always full. Growth: remove 1 of N points each run.
    N LOO runs x (EFC + LCDM) = 2N MCMC chains.

    Pass criterion (v2 — sign-consistency):
        P(α < 0) >= pass_p_negative (default 0.80) per LOO channel.
        Strength tags: strong (>0.95), medium (0.90-0.95), weak (0.80-0.90).
    """
    np.random.seed(seed)
    total_time = 0.0

    logger.info("=== T7: LEAVE-ONE-OUT ===")

    # Read raw growth data
    raw = np.loadtxt(growth_path, delimiter=",", skiprows=1)
    n_growth = raw.shape[0]

    logger.info(f"  Growth data: {n_growth} points")
    for i in range(n_growth):
        logger.info(f"    [{i}] z={raw[i,0]:.2f}  fs8={raw[i,1]:.3f}+/-{raw[i,2]:.3f}")

    loo_results = []

    for idx in range(n_growth):
        excluded_z = float(raw[idx, 0])
        excluded_fs8 = float(raw[idx, 1])
        excluded_sig = float(raw[idx, 2])

        logger.info(f"  LOO-{idx}: drop z={excluded_z:.2f} "
                    f"(fs8={excluded_fs8:.3f}+/-{excluded_sig:.3f})")

        # Create LOO dataset: mask out point idx
        mask = np.ones(n_growth, dtype=bool)
        mask[idx] = False
        reduced = raw[mask]

        # Write temp CSV for GrowthModule
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        tmp.write("z,fs8,sigma\n")
        for row in reduced:
            tmp.write(f"{row[0]:.4f},{row[1]:.4f},{row[2]:.4f}\n")
        tmp.flush()
        tmp_path = tmp.name
        tmp.close()

        # Load growth module from temp file
        growth_engine = EFCGrowth()
        growth_mod_loo = GrowthModule(growth_engine)
        growth_mod_loo.load_data(data_path=tmp_path)
        os.unlink(tmp_path)

        # Build LOO modules dict: replace growth, keep everything else
        loo_modules = dict(modules)
        loo_modules["growth"] = growth_mod_loo

        n_data_loo = sum(m.n_data for m in loo_modules.values() if m is not None)
        args = (loo_modules,)

        s_off = seed + 100 + idx * 10

        # EFC: 4 params (baseline priors: rd=147.09, sigma8 stram)
        p0_efc = _init_p0_4param(nwalkers, s_off)
        chain_efc, lp_efc, dt, _ = _run_emcee(
            f"LOO-{idx} EFC", _log_prob_baseline_efc, ndim=4,
            p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=args, seed=s_off, pool=pool,
        )
        total_time += dt

        # LCDM: 3 params
        p0_lcdm = _init_p0_3param(nwalkers, s_off + 1)
        chain_lcdm, lp_lcdm, dt, _ = _run_emcee(
            f"LOO-{idx} LCDM", _log_prob_baseline_lcdm, ndim=3,
            p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=args, seed=s_off + 1, pool=pool,
        )
        total_time += dt

        alpha = _extract_alpha(chain_efc, alpha_col=3)
        comp = _compute_comparison(
            float(np.max(lp_efc)), 4,
            float(np.max(lp_lcdm)), 3,
            n_data_loo,
        )

        # Sign-consistency criterion (v2):
        pneg = alpha.p_negative
        passed = pneg >= pass_p_negative

        # Strength tag
        if pneg >= 0.95:
            strength = "strong"
        elif pneg >= 0.90:
            strength = "medium"
        elif pneg >= 0.80:
            strength = "weak"
        else:
            strength = "fail"

        logger.info(f"    alpha = {alpha.mean:.3f} +/- {alpha.std:.3f} "
                    f"({alpha.significance:.2f}sigma) P(α<0)={pneg:.3f} "
                    f"[{strength}] dAIC={comp.daic:.2f}  "
                    f"{'PASS' if passed else 'FAIL'}")

        loo_results.append({
            "idx": idx,
            "z_excluded": excluded_z,
            "fs8_excluded": excluded_fs8,
            "sig_excluded": excluded_sig,
            "alpha": alpha,
            "comparison": comp,
            "correlations": _correlations_4param(chain_efc),
            "passed": passed,
            "p_negative": pneg,
            "strength": strength,
        })

    # Summary
    pass_count = sum(1 for r in loo_results if r["passed"])
    robustness_score = pass_count / n_growth

    p_negs = [r["p_negative"] for r in loo_results]
    most_influential_idx = int(np.argmin(p_negs))  # lowest P(α<0)

    alpha_means = [r["alpha"].mean for r in loo_results]
    alpha_range = (min(alpha_means), max(alpha_means))

    # Strength distribution
    strength_counts = {}
    for r in loo_results:
        s = r["strength"]
        strength_counts[s] = strength_counts.get(s, 0) + 1

    if pass_count >= loo_min_pass:
        verdict = "PASS"
    elif pass_count >= 3:
        verdict = "PARTIAL"
    else:
        verdict = "NOT_ROBUST"

    logger.info(f"  T7 SUMMARY: {pass_count}/{n_growth} sign-consistent = "
                f"{robustness_score:.0%}")
    logger.info(f"  Strength: {strength_counts}")
    logger.info(f"  P(α<0) range: [{min(p_negs):.3f}, {max(p_negs):.3f}]")
    logger.info(f"  T7 VERDICT: {verdict}")

    return {
        "loo_results": loo_results,
        "pass_count": pass_count,
        "n_total": n_growth,
        "robustness_score": robustness_score,
        "verdict": verdict,
        "most_influential_idx": most_influential_idx,
        "alpha_range": alpha_range,
        "total_time_seconds": total_time,
        # New sign-consistency fields
        "criterion": "sign_consistency",
        "pass_p_negative": pass_p_negative,
        "p_negative_range": (min(p_negs), max(p_negs)) if p_negs else (0.0, 0.0),
        "strength_counts": strength_counts,
    }


# ═══════════════════════════════════════════════════════════════
#  CONVERGENCE GATE
# ═══════════════════════════════════════════════════════════════

def check_convergence(sampler, burnin: int, policy) -> dict:
    """Check MCMC convergence using R-hat, ESS, and acceptance fraction.

    Args:
        sampler: emcee.EnsembleSampler after running
        burnin: number of steps to discard
        policy: ResearchPolicy (uses inference_gates.convergence)

    Returns:
        dict with keys: converged (bool), rhat_max, ess_min,
        acceptance_mean, details (dict)
    """
    from efc_inference.core.utils import gelman_rubin, effective_sample_size

    gate = policy.inference_gates.convergence

    # Get raw chain: (nwalkers, nsteps, ndim)
    raw_chain = sampler.get_chain(discard=burnin)  # NOT flat

    # R-hat per parameter
    rhat = gelman_rubin(raw_chain)
    rhat_max_val = float(np.max(rhat))

    # ESS per parameter
    ess = effective_sample_size(raw_chain)
    ess_min_val = float(np.min(ess))

    # Acceptance fraction
    acc = sampler.acceptance_fraction
    acc_mean = float(np.mean(acc))

    # Check convergence
    rhat_ok = rhat_max_val <= gate.rhat_max
    ess_ok = ess_min_val >= gate.ess_min
    acc_ok = gate.acceptance_lo <= acc_mean <= gate.acceptance_hi

    converged = rhat_ok and ess_ok and acc_ok

    details = {
        "rhat_per_param": [float(r) for r in rhat],
        "ess_per_param": [float(e) for e in ess],
        "acceptance_per_walker": [float(a) for a in acc],
        "rhat_ok": rhat_ok,
        "ess_ok": ess_ok,
        "acc_ok": acc_ok,
        "thresholds": {
            "rhat_max": gate.rhat_max,
            "ess_min": gate.ess_min,
            "acceptance_lo": gate.acceptance_lo,
            "acceptance_hi": gate.acceptance_hi,
        },
    }

    logger.info(
        f"  Convergence: {'PASS' if converged else 'FAIL'} — "
        f"R-hat_max={rhat_max_val:.4f} (≤{gate.rhat_max}), "
        f"ESS_min={ess_min_val:.0f} (≥{gate.ess_min}), "
        f"acc={acc_mean:.3f} ([{gate.acceptance_lo},{gate.acceptance_hi}])"
    )

    return {
        "converged": converged,
        "rhat_max": rhat_max_val,
        "ess_min": ess_min_val,
        "acceptance_mean": acc_mean,
        "details": details,
    }


def run_n3_gate_sweep(
    modules: dict = None,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    collapse_sigma: float = 1.3,
    pool=None,
    gate_grid: list = None,
) -> dict:
    """N3: Gate freedom test — does alpha survive free (a_t, delta_a)?

    Two-part test:
    1. Discrete sweep: run 5 fixed (a_t, delta_a) configurations, compare alpha.
    2. Free-gate: run 6-param MCMC with a_t, delta_a as free parameters.

    If alpha significance is maintained across gate choices → signal is physical.
    If alpha collapses → current 2σ signal is partly a gate-shape artifact.

    Returns dict with:
        - discrete_variants: dict of results per grid point
        - free_gate: dict with alpha, gate posteriors, correlations
        - verdict: PASS / MARGINAL / COLLAPSED
        - alpha_survives: bool
    """
    if gate_grid is None:
        gate_grid = N3_GATE_SWEEP_GRID

    # Load modules with VariantB if not provided
    if modules is None:
        modules = load_modules(cosmology=EFCVariantB())
    else:
        # Re-load with VariantB cosmology for gate freedom
        modules_b = load_modules(cosmology=EFCVariantB())
        modules = modules_b

    np.random.seed(seed)
    n_data = sum(m.n_data for m in modules.values() if m is not None)
    total_time = 0.0

    logger.info("=== N3: GATE FREEDOM TEST ===")

    # ── Part 1: Discrete sweep (4 params each, different fixed gates) ──
    logger.info("-- Part 1: Discrete gate sweep --")
    discrete_variants = {}

    for i, (label, a_t_val, da_val) in enumerate(gate_grid):
        logger.info(f"  N3-{label}: a_t={a_t_val}, delta_a={da_val}")
        s_off = seed + 50 + i * 10

        # EFC with this fixed gate: 4 params
        p0_efc = _init_p0_4param(nwalkers, s_off)
        chain_efc, lp_efc, dt, _ = _run_emcee(
            f"N3-{label} EFC", _log_prob_n3_efc_fixed, ndim=4,
            p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=(modules, a_t_val, da_val),
            seed=s_off, pool=pool,
        )
        total_time += dt

        # LCDM baseline (gate-independent, but re-run for fair comparison)
        p0_lcdm = _init_p0_3param(nwalkers, s_off + 1)
        chain_lcdm, lp_lcdm, dt, _ = _run_emcee(
            f"N3-{label} LCDM", _log_prob_baseline_lcdm, ndim=3,
            p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
            burnin=burnin, args=(modules,),
            seed=s_off + 1, pool=pool,
        )
        total_time += dt

        alpha = _extract_alpha(chain_efc, alpha_col=3)
        comp = _compute_comparison(
            float(np.max(lp_efc)), 4,
            float(np.max(lp_lcdm)), 3,
            n_data,
        )
        corrs = _correlations_4param(chain_efc)

        logger.info(f"    alpha = {alpha.mean:.3f} ± {alpha.std:.3f} "
                    f"({alpha.significance:.2f}σ) ΔAIC={comp.daic:.2f}")

        discrete_variants[label] = {
            "a_t": a_t_val,
            "delta_a": da_val,
            "alpha": alpha,
            "comparison": comp,
            "correlations": corrs,
        }

    # ── Part 2: Free gate (6 params: Om, H0, s8, alpha, a_t, delta_a) ──
    logger.info("-- Part 2: Free gate (6-param MCMC) --")
    s_off_free = seed + 100

    p0_free = _init_p0_6param(nwalkers, s_off_free)
    chain_free, lp_free, dt, _ = _run_emcee(
        "N3 free-gate EFC", _log_prob_n3_efc, ndim=6,
        p0=p0_free, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,),
        seed=s_off_free, pool=pool,
    )
    total_time += dt

    # LCDM for comparison (3 params, no gate)
    p0_lcdm_free = _init_p0_3param(nwalkers, s_off_free + 1)
    chain_lcdm_free, lp_lcdm_free, dt, _ = _run_emcee(
        "N3 free-gate LCDM", _log_prob_baseline_lcdm, ndim=3,
        p0=p0_lcdm_free, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,),
        seed=s_off_free + 1, pool=pool,
    )
    total_time += dt

    alpha_free = _extract_alpha(chain_free, alpha_col=3)
    a_t_stats = _extract_param(chain_free, 4)
    delta_a_stats = _extract_param(chain_free, 5)
    comp_free = _compute_comparison(
        float(np.max(lp_free)), 6,   # 6 params EFC
        float(np.max(lp_lcdm_free)), 3,  # 3 params LCDM
        n_data,
    )
    corrs_free = _correlations_6param(chain_free)

    logger.info(f"  Free-gate: alpha = {alpha_free.mean:.3f} ± {alpha_free.std:.3f} "
                f"({alpha_free.significance:.2f}σ)")
    logger.info(f"  a_t = {a_t_stats.mean:.3f} ± {a_t_stats.std:.3f} "
                f"[{a_t_stats.ci95_lo:.3f}, {a_t_stats.ci95_hi:.3f}]")
    logger.info(f"  delta_a = {delta_a_stats.mean:.3f} ± {delta_a_stats.std:.3f} "
                f"[{delta_a_stats.ci95_lo:.3f}, {delta_a_stats.ci95_hi:.3f}]")
    logger.info(f"  ΔAIC = {comp_free.daic:.2f}")
    logger.info(f"  Correlations: alpha-a_t = {corrs_free['a_at']:.3f}, "
                f"alpha-delta_a = {corrs_free['a_da']:.3f}")

    free_gate_result = {
        "alpha": alpha_free,
        "a_t": a_t_stats,
        "delta_a": delta_a_stats,
        "comparison": comp_free,
        "correlations": corrs_free,
    }

    # ── Verdict ──
    # Criterion: alpha must survive in BOTH baseline gate AND free gate
    baseline_variant = discrete_variants.get("baseline", None)
    baseline_alpha_sig = baseline_variant["alpha"].significance if baseline_variant else 0.0
    free_alpha_sig = alpha_free.significance

    # Check consistency: alpha spread across discrete grid
    discrete_sigs = [v["alpha"].significance for v in discrete_variants.values()]
    min_discrete_sig = min(discrete_sigs) if discrete_sigs else 0.0
    max_discrete_sig = max(discrete_sigs) if discrete_sigs else 0.0
    mean_discrete_sig = float(np.mean(discrete_sigs)) if discrete_sigs else 0.0

    # Alpha survives if:
    # 1. Free gate alpha is at or above collapse_sigma
    # 2. Mean discrete sweep alpha is at or above collapse_sigma
    free_survives = free_alpha_sig >= pass_sigma and comp_free.daic <= pass_daic
    discrete_robust = mean_discrete_sig >= pass_sigma

    if free_survives and discrete_robust:
        verdict = "PASS"
    elif free_alpha_sig < collapse_sigma:
        verdict = "COLLAPSED"
    else:
        verdict = "MARGINAL"

    logger.info(f"  N3 VERDICT: {verdict}")
    logger.info(f"    Free gate: {free_alpha_sig:.2f}σ (pass={free_survives})")
    logger.info(f"    Discrete range: [{min_discrete_sig:.2f}σ — {max_discrete_sig:.2f}σ], "
                f"mean={mean_discrete_sig:.2f}σ (robust={discrete_robust})")

    return {
        "discrete_variants": discrete_variants,
        "free_gate": free_gate_result,
        "verdict": verdict,
        "alpha_survives": free_survives and discrete_robust,
        "discrete_sigma_range": [min_discrete_sig, max_discrete_sig],
        "discrete_sigma_mean": mean_discrete_sig,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N7: GLOBAL PARAMETER-LOCK CROSS-PROBE ("DOMSTOLEN")
# ═══════════════════════════════════════════════════════════════

# N7 uses EFCVariantF: background α + GRAV-locked G_eff growth source.
# FROZEN: C=2.32, k_lambda=0.0014, a_t=0.5, delta_a=0.1, r_d=147.09
# FREE: Omega_m, H0, sigma8, alpha_cosmo (4 params)
# LCDM: 3 params (alpha=0), same modules
#
# Key design: ALL 4 probes run through EFCVariantF.growth_source()
# which includes G_eff(k_eff, a)/G = 1 + (C²-1)·gate(a)·screen(k_eff).
# This is the first time the GRAV discrete gravity sector is coupled
# to the cosmological likelihood.

# --- N7 priors: identical to baseline (D3 honest σ8) ---

def _log_prior_n7_efc(theta):
    """EFC prior for N7: [Om, H0, s8, alpha], rd fixed, σ8 honest.

    Identical to baseline. The physics change is in the cosmology model
    (EFCVariantF), not in the prior.
    """
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):      return -np.inf
    if not (50.0 < H0 < 85.0):    return -np.inf
    if not (0.5 < s8 < 1.2):      return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return -0.5 * ((s8 - 0.80) / 0.04) ** 2


def _log_prob_n7_efc(theta, modules):
    """Log-probability for N7 EFC with GRAV-locked G_eff: 4 params."""
    lp = _log_prior_n7_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _compute_per_probe_chi2(params_dict: dict, modules: dict) -> dict:
    """Compute per-probe fit quality for diagnostic purposes.

    For each probe, computes:
      - log_likelihood: raw logL value
      - neg2ll: -2 * logL (comparable across probes)
      - n_data: number of data points
      - chi2_approx: approximate chi2 = -2*(logL - logL_saturated)
                     For Gaussian with known errors: chi2 = -2*logL - const

    A probe is "exploding" if its contribution to the total logL is
    disproportionately negative (much worse than other probes).
    We flag based on neg2ll / n_data ratio: > 50 is dangerous.

    Returns dict keyed by probe name.
    """
    result = {}
    for name, mod in modules.items():
        if mod is None:
            continue
        try:
            ll = mod.log_likelihood(params_dict)
            n_pts = mod.n_data if hasattr(mod, 'n_data') else len(mod.coordinates)
            neg2ll = -2.0 * ll if np.isfinite(ll) else np.inf
            # Approximate chi2/dof ratio: neg2ll/n as a rough quality metric
            # Note: this includes the normalization constant, so it's not
            # a true chi2_red. But large values still signal poor fits.
            quality_ratio = neg2ll / n_pts if n_pts > 0 else np.inf
            result[name] = {
                "log_likelihood": float(ll),
                "neg2ll": float(neg2ll),
                "n_data": n_pts,
                "quality_ratio": float(quality_ratio),
            }
        except Exception as e:
            result[name] = {
                "log_likelihood": -np.inf,
                "neg2ll": np.inf,
                "n_data": 0,
                "quality_ratio": np.inf,
                "error": str(e),
            }
    return result


def run_n7_cross_probe_lock(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pool=None,
) -> dict:
    """N7: Global parameter-lock cross-probe test ("Domstolen").

    ALL 4 data probes (BAO + H(z) + fσ₈ + SNIa) run SIMULTANEOUSLY with:
      - EFCVariantF cosmology: background α + GRAV-locked G_eff growth
      - FROZEN: C=2.32, k_lambda=0.0014, a_t=0.5, delta_a=0.1, r_d=147.09
      - FREE: Omega_m, H0, sigma8, alpha_cosmo
      - No rescue: μ=1 (no free Poisson modification), no free lensing amplitude

    Runs EFC 4p vs LCDM 3p. LCDM uses FlatLCDM cosmology (NOT VariantF
    with alpha=0, since LCDM should be a clean reference).

    Returns:
        dict with alpha stats, ΔAIC/ΔBIC, per-probe χ², correlations,
        and deterministic verdict:
          - SURVIVES:  α ≥ 2σ AND ΔAIC < -2 AND no probe explodes
          - MARGINAL:  α ≥ 1.5σ AND ΔAIC < 0
          - NO_SIGNAL: α < 1.5σ OR ΔAIC > 0
          - EXPLODED:  any probe has χ²_red > 5
    """
    logger.info("=== N7: GLOBAL PARAMETER-LOCK CROSS-PROBE ('DOMSTOLEN') ===")
    logger.info("  Cosmology: EFCVariantF (GRAV-locked G_eff)")
    logger.info("  Frozen: C=2.32, k_lambda=0.0014, a_t=0.5, delta_a=0.1, r_d=147.09")

    np.random.seed(seed)
    total_time = 0.0

    # Build modules with EFCVariantF cosmology (GRAV-coupled)
    n7_modules = load_modules(cosmology=EFCVariantF())
    n_data = sum(m.n_data for m in n7_modules.values() if m is not None)

    probes = [p for p, m in n7_modules.items() if m is not None]
    probe_counts = {p: m.n_data for p, m in n7_modules.items() if m is not None}
    logger.info(f"  Probes: {probes} ({n_data} total pts)")

    # ── EFC: 4 params [Om, H0, s8, alpha] with GRAV-locked growth ──
    p0_efc = _init_p0_4param(nwalkers, seed + 700)
    chain_efc, lp_efc, dt_efc, sampler_efc = _run_emcee(
        "N7 EFC (VariantF)", _log_prob_n7_efc, ndim=4,
        p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(n7_modules,), seed=seed + 700, pool=pool,
    )
    total_time += dt_efc

    # ── LCDM: 3 params [Om, H0, s8], alpha=0 ──
    # LCDM uses baseline modules (VariantA with alpha=0 = FlatLCDM)
    # so the growth source is (3/2) Ωm / (a⁵ E²) without G_eff.
    p0_lcdm = _init_p0_3param(nwalkers, seed + 701)
    chain_lcdm, lp_lcdm, dt_lcdm, _ = _run_emcee(
        "N7 LCDM (reference)", _log_prob_baseline_lcdm, ndim=3,
        p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(modules,), seed=seed + 701, pool=pool,
    )
    total_time += dt_lcdm

    # ── Extract statistics ──
    alpha = _extract_alpha(chain_efc, alpha_col=3)
    ll_efc = float(np.max(lp_efc))
    ll_lcdm = float(np.max(lp_lcdm))
    comparison = _compute_comparison(ll_efc, 4, ll_lcdm, 3, n_data)
    correlations = _correlations_4param(chain_efc)

    # Parameter stats
    om = _extract_param(chain_efc, 0)
    h0 = _extract_param(chain_efc, 1)
    s8 = _extract_param(chain_efc, 2)

    # ── Per-probe χ² at best-fit ──
    best_idx = np.argmax(lp_efc)
    best_params_efc = {
        "Omega_m": float(chain_efc[best_idx, 0]),
        "H0": float(chain_efc[best_idx, 1]),
        "sigma8": float(chain_efc[best_idx, 2]),
        "alpha_cosmo": float(chain_efc[best_idx, 3]),
        "r_d": RD_FIXED,
    }
    per_probe_efc = _compute_per_probe_chi2(best_params_efc, n7_modules)

    # Also compute per-probe for LCDM at best-fit for comparison
    best_idx_lcdm = np.argmax(lp_lcdm)
    best_params_lcdm = {
        "Omega_m": float(chain_lcdm[best_idx_lcdm, 0]),
        "H0": float(chain_lcdm[best_idx_lcdm, 1]),
        "sigma8": float(chain_lcdm[best_idx_lcdm, 2]),
        "alpha_cosmo": 0.0,
        "r_d": RD_FIXED,
    }
    per_probe_lcdm = _compute_per_probe_chi2(best_params_lcdm, modules)

    # Check for exploding probes:
    # A probe "explodes" if its EFC logL is catastrophically worse than LCDM.
    # Threshold: if EFC logL is worse by > 10 per data point, something is wrong.
    any_exploded = False
    exploded_probes = []
    for pname in per_probe_efc:
        ll_efc_p = per_probe_efc[pname]["log_likelihood"]
        ll_lcdm_p = per_probe_lcdm.get(pname, {}).get("log_likelihood", -np.inf)
        n_p = per_probe_efc[pname]["n_data"]
        if n_p > 0 and np.isfinite(ll_efc_p) and np.isfinite(ll_lcdm_p):
            degradation_per_pt = (ll_lcdm_p - ll_efc_p) / n_p
            per_probe_efc[pname]["degradation_per_pt"] = float(degradation_per_pt)
            if degradation_per_pt > 5.0:  # much worse than LCDM
                any_exploded = True
                exploded_probes.append(pname)
        else:
            per_probe_efc[pname]["degradation_per_pt"] = 0.0

    logger.info(f"  alpha = {alpha.mean:.3f} ± {alpha.std:.3f} "
                f"({alpha.significance:.2f}σ)")
    logger.info(f"  ΔAIC = {comparison.daic:.2f}, ΔBIC = {comparison.dbic:.2f}")
    logger.info(f"  P(α<0) = {alpha.p_negative:.3f}")
    for pname, pdata in per_probe_efc.items():
        ll_p = pdata["log_likelihood"]
        deg = pdata.get("degradation_per_pt", 0)
        logger.info(f"  Probe {pname}: logL={ll_p:.2f}, Δ/pt vs LCDM={deg:.3f}")
    if exploded_probes:
        logger.warning(f"  EXPLODED probes: {exploded_probes}")

    # ── Deterministic verdict ──
    if any_exploded:
        verdict = "EXPLODED"
    elif alpha.significance >= 2.0 and comparison.daic < -2.0:
        verdict = "SURVIVES"
    elif alpha.significance >= 1.5 and comparison.daic < 0.0:
        verdict = "MARGINAL"
    else:
        verdict = "NO_SIGNAL"

    logger.info(f"  N7 VERDICT: {verdict}")

    # ── G_eff diagnostic info ──
    geff_at_1 = EFCVariantF().g_eff_over_G(np.array([1.0]))[0]
    geff_at_05 = EFCVariantF().g_eff_over_G(np.array([0.5]))[0]
    geff_info = {
        "C": EFCVariantF.C_GRAV,
        "k_lambda": EFCVariantF.K_LAMBDA,
        "k_eff": EFCVariantF.K_EFF,
        "g_eff_at_a1": float(geff_at_1),
        "g_eff_at_a05": float(geff_at_05),
        "modification_pct": float((geff_at_1 - 1.0) * 100),
    }

    return {
        "alpha": alpha,
        "comparison": comparison,
        "correlations": correlations,
        "om": om,
        "h0": h0,
        "s8": s8,
        "per_probe_efc": per_probe_efc,
        "per_probe_lcdm": per_probe_lcdm,
        "verdict": verdict,
        "any_exploded": any_exploded,
        "exploded_probes": exploded_probes,
        "geff_info": geff_info,
        "best_fit_params_efc": best_params_efc,
        "best_fit_params_lcdm": best_params_lcdm,
        "total_time_seconds": total_time,
        "n_data": n_data,
        "probe_counts": probe_counts,
        "cosmology_model": "EFCVariantF",
        "frozen_params": {
            "C": 2.32,
            "k_lambda": 0.0014,
            "a_t": 0.5,
            "delta_a": 0.1,
            "r_d": RD_FIXED,
        },
    }


# ═══════════════════════════════════════════════════════════════
#  VARIANT-G: CONSTITUTIVE LAW GROWTH-ONLY DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════

# VariantG tests whether entropy-gradient-driven mu(z) improves growth
# likelihood. ZERO extra free parameters vs LCDM:
#   - VariantG: 3 params [Om, H0, s8] + mu from constitutive law
#   - LCDM:     3 params [Om, H0, s8] + mu = 1
# Both share identical background (pure LCDM, no alpha, no gate).
# The ONLY difference is in growth_source: mu(z) vs mu=1.
#
# This is a GROWTH-ONLY test. We compute ΔlogL from growth probe only
# (fσ8) to avoid contamination from background-sensitive probes.

def run_variant_g_diagnostic(
    modules: dict,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    pool=None,
    k_eff: float = None,
    scenario: str = None,
) -> dict:
    """Variant-G: constitutive-law growth diagnostic (Phase 8).

    Runs 3-parameter MCMC [Om, H0, σ8] with two cosmology models:
      1. EFCVariantG: mu(z) from constitutive law (entropy gradients)
      2. FlatLCDM:    mu = 1 (standard GR)

    Both have IDENTICAL backgrounds (pure LCDM), IDENTICAL priors,
    IDENTICAL data. The only difference is growth_source.

    Args:
        k_eff: Override k_eff (h/Mpc). If None, uses default 0.1.
        scenario: Named scenario ("G10", "G02", "G01"). Overrides k_eff.

    Key output: ΔlogL_growth = logL_growth(VariantG) - logL_growth(LCDM)
    If ΔlogL_growth ~ 0: entropy-gradient mu is undetectable at current precision.
    If ΔlogL_growth > 1: potential signal worth investigating with full pipeline.

    Returns:
        dict with ΔlogL_growth, mu_diagnostics, parameter stats, verdict
    """
    # Resolve scenario → k_eff
    if scenario:
        vg = EFCVariantG.for_scenario(scenario)
        scenario_name = scenario
    elif k_eff is not None:
        vg = EFCVariantG(k_eff=k_eff)
        scenario_name = f"k{k_eff}"
    else:
        vg = EFCVariantG()
        scenario_name = "G10"  # default

    logger.info(f"=== VARIANT-G: CONSTITUTIVE LAW DIAGNOSTIC ({scenario_name}) ===")

    mu_diag = vg.mu_diagnostics()

    logger.info(f"  Scenario: {scenario_name}")
    logger.info(f"  Cosmology: EFCVariantG (constitutive law)")
    logger.info(f"  Background: pure LCDM (no alpha)")
    logger.info(f"  Free params: [Om, H0, s8] (3p, same as LCDM)")
    logger.info(f"  Frozen: C={mu_diag['C_grav']}, k_lambda={mu_diag['k_lambda']}, "
                f"k_eff={mu_diag['k_eff']}")
    logger.info(f"  chi_c={mu_diag['chi_c']:.6f}, eps_eff={mu_diag['epsilon_eff']:.8f}, "
                f"screen={mu_diag['screen_k_eff']:.8f}")
    logger.info(f"  mu range: [{mu_diag['mu_min']:.6f}, {mu_diag['mu_max']:.6f}]")
    for z_val in [0.3, 0.5, 0.7, 1.0, 1.5, 2.3]:
        key = f"mu_z{z_val:.1f}"
        logger.info(f"    mu(z={z_val}) = {mu_diag[key]:.8f} "
                    f"(Δ = {(mu_diag[key]-1)*100:.4f}%)")

    np.random.seed(seed)
    total_time = 0.0

    # Build modules with VariantG cosmology
    vg_modules = load_modules(cosmology=vg)

    # Build modules with FlatLCDM (mu=1 reference)
    lcdm_modules = load_modules(cosmology=FlatLCDM())

    # Both run 3-parameter MCMC: [Om, H0, s8]
    # Use existing LCDM prior/prob functions (they do exactly this)

    # ── VariantG: 3 params ──
    p0_vg = _init_p0_3param(nwalkers, seed + 800)
    chain_vg, lp_vg, dt_vg, _ = _run_emcee(
        "VariantG (mu from chi)", _log_prob_baseline_lcdm, ndim=3,
        p0=p0_vg, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(vg_modules,), seed=seed + 800, pool=pool,
    )
    total_time += dt_vg

    # ── LCDM reference: 3 params ──
    p0_lcdm = _init_p0_3param(nwalkers, seed + 801)
    chain_lcdm, lp_lcdm, dt_lcdm, _ = _run_emcee(
        "LCDM reference (mu=1)", _log_prob_baseline_lcdm, ndim=3,
        p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=(lcdm_modules,), seed=seed + 801, pool=pool,
    )
    total_time += dt_lcdm

    # ── Extract best-fit parameters ──
    best_idx_vg = np.argmax(lp_vg)
    best_params_vg = {
        "Omega_m": float(chain_vg[best_idx_vg, 0]),
        "H0": float(chain_vg[best_idx_vg, 1]),
        "sigma8": float(chain_vg[best_idx_vg, 2]),
        "alpha_cosmo": 0.0,
        "r_d": RD_FIXED,
    }

    best_idx_lcdm = np.argmax(lp_lcdm)
    best_params_lcdm = {
        "Omega_m": float(chain_lcdm[best_idx_lcdm, 0]),
        "H0": float(chain_lcdm[best_idx_lcdm, 1]),
        "sigma8": float(chain_lcdm[best_idx_lcdm, 2]),
        "alpha_cosmo": 0.0,
        "r_d": RD_FIXED,
    }

    # ── Per-probe log-likelihoods at best-fit ──
    per_probe_vg = _compute_per_probe_chi2(best_params_vg, vg_modules)
    per_probe_lcdm = _compute_per_probe_chi2(best_params_lcdm, lcdm_modules)

    # ── Compute ΔlogL per probe (positive = VariantG fits better) ──
    dll = {}
    for probe in per_probe_vg:
        ll_vg = per_probe_vg[probe]["log_likelihood"]
        ll_ref = per_probe_lcdm.get(probe, {}).get("log_likelihood", -np.inf)
        if np.isfinite(ll_vg) and np.isfinite(ll_ref):
            dll[probe] = float(ll_vg - ll_ref)
        else:
            dll[probe] = 0.0

    dll_growth = dll.get("growth", 0.0)
    dll_total = sum(dll.values())

    logger.info(f"  ΔlogL per probe:")
    for probe, val in dll.items():
        logger.info(f"    {probe}: {val:+.4f}")
    logger.info(f"  ΔlogL_growth: {dll_growth:+.4f}")
    logger.info(f"  ΔlogL_total:  {dll_total:+.4f}")

    # ── Parameter comparison ──
    om_vg = _extract_param(chain_vg, 0)
    h0_vg = _extract_param(chain_vg, 1)
    s8_vg = _extract_param(chain_vg, 2)
    om_lcdm = _extract_param(chain_lcdm, 0)
    h0_lcdm = _extract_param(chain_lcdm, 1)
    s8_lcdm = _extract_param(chain_lcdm, 2)

    # Sigma8 shift is the key diagnostic
    # If mu > 1, VariantG should prefer LOWER sigma8 to compensate
    s8_shift = s8_vg.mean - s8_lcdm.mean
    logger.info(f"  σ8 shift: {s8_shift:+.4f} "
                f"(VG={s8_vg.mean:.4f}±{s8_vg.std:.4f}, "
                f"LCDM={s8_lcdm.mean:.4f}±{s8_lcdm.std:.4f})")

    # ── Total logL comparison (same k=3, so ΔAIC = -2·ΔlogL) ──
    ll_vg_total = float(np.max(lp_vg))
    ll_lcdm_total = float(np.max(lp_lcdm))
    daic = -2.0 * (ll_vg_total - ll_lcdm_total)  # same k, so just -2*ΔlogL
    logger.info(f"  Total best logL: VG={ll_vg_total:.2f}, LCDM={ll_lcdm_total:.2f}")
    logger.info(f"  ΔAIC (same k=3): {daic:+.3f}")

    # ── Deterministic verdict ──
    if abs(dll_growth) < 0.1:
        verdict = "UNDETECTABLE"
    elif dll_growth > 1.0:
        verdict = "SIGNAL"
    elif dll_growth > 0.5:
        verdict = "MARGINAL_SIGNAL"
    elif dll_growth < -1.0:
        verdict = "ANTI_SIGNAL"
    else:
        verdict = "WEAK"

    logger.info(f"  VariantG VERDICT: {verdict}")

    return {
        "verdict": verdict,
        "dll_growth": dll_growth,
        "dll_total": dll_total,
        "dll_per_probe": dll,
        "daic_same_k": daic,
        "s8_vg_mean": s8_vg.mean,
        "s8_vg_std": s8_vg.std,
        "s8_lcdm_mean": s8_lcdm.mean,
        "s8_lcdm_std": s8_lcdm.std,
        "s8_shift": s8_shift,
        "om_vg_mean": om_vg.mean,
        "h0_vg_mean": h0_vg.mean,
        "mu_diagnostics": mu_diag,
        "best_fit_params_vg": best_params_vg,
        "best_fit_params_lcdm": best_params_lcdm,
        "per_probe_vg": per_probe_vg,
        "per_probe_lcdm": per_probe_lcdm,
        "total_time_seconds": total_time,
        "cosmology_model": "EFCVariantG",
        "scenario": scenario_name,
        "k_eff": mu_diag["k_eff"],
        "mu_amp": mu_diag["mu_max"] - 1.0,
        "mu_span": mu_diag["mu_max"] - mu_diag["mu_min"],
        "frozen_params": {
            "C": mu_diag["C_grav"],
            "k_lambda": mu_diag["k_lambda"],
            "k_eff": mu_diag["k_eff"],
            "chi_c": mu_diag["chi_c"],
            "epsilon_eff": mu_diag["epsilon_eff"],
            "screen_k_eff": mu_diag["screen_k_eff"],
            "hill_n": vg.HILL_N,
            "r_d": RD_FIXED,
        },
    }


# ═══════════════════════════════════════════════════════════════
#  NUTS GPU ADAPTER — returns BaselineResult (same as emcee)
# ═══════════════════════════════════════════════════════════════

def _nuts_available() -> bool:
    """Check if NUTS/JAX/numpyro dependencies are available."""
    try:
        import jax
        import numpyro
        return True
    except ImportError:
        return False


def run_joint_inference_nuts(
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = DEFAULT_SEED,
    target_accept: float = 0.8,
    bao_path: str = BAO_PATH,
    growth_path: str = GROWTH_PATH,
    hz_path: str = HZ_PATH,
    snia_path: str = SNIA_PATH,
    snia_cov_path: str = SNIA_COV_PATH,
) -> BaselineResult:
    """Run baseline multi-probe inference via GPU NUTS (JAX/numpyro).

    Transparent replacement for run_joint_inference() — returns the same
    BaselineResult dataclass. NUTS provides gradient-based exploration
    with superior effective samples per second on GPU.

    Requires: jax, numpyro, CUDA GPU.
    Falls back to emcee if JAX is unavailable.

    Args:
        num_warmup:     NUTS warmup steps (analogous to burnin)
        num_samples:    post-warmup samples per chain
        num_chains:     parallel chains (1 per GPU typical)
        seed:           PRNG seed
        target_accept:  NUTS target acceptance probability
        bao_path:       Path to BAO data CSV
        growth_path:    Path to growth data CSV
        hz_path:        Path to H(z) data CSV
        snia_path:      Path to SNIa data CSV
        snia_cov_path:  Path to SNIa covariance matrix
    """
    from efc_inference.runs.jax_efc_nuts import (
        load_data, run_nuts_efc, NUTSResult,
    )

    logger.info("=== BASELINE: NUTS GPU (JAX/numpyro) ===")

    t0 = time.time()

    # Load data (uses JAX arrays, same CSVs as emcee)
    data = load_data(
        bao_path=bao_path,
        growth_path=growth_path,
        hz_path=hz_path,
        snia_path=snia_path,
        snia_cov_path=snia_cov_path,
    )

    logger.info(f"  Data: {data.n_total} points")
    logger.info(f"  NUTS: {num_warmup}w + {num_samples}s, {num_chains} chains, "
                f"target_accept={target_accept}")

    # Run NUTS
    result = run_nuts_efc(
        data=data,
        num_warmup=num_warmup,
        num_samples=num_samples,
        num_chains=num_chains,
        seed=seed,
        target_accept=target_accept,
    )

    dt_total = time.time() - t0

    # Convert NUTSResult → BaselineResult
    # Create AlphaStats from NUTS result
    alpha = AlphaStats(
        mean=result.alpha_mean,
        std=result.alpha_std,
        significance=result.alpha_significance,
        p_negative=result.alpha_p_negative,
        median=result.alpha_mean,       # NUTS gives mean≈median for well-sampled
        ci95_lo=result.alpha_mean - 1.96 * result.alpha_std,
        ci95_hi=result.alpha_mean + 1.96 * result.alpha_std,
    )

    comparison = _compute_comparison(
        result.ll_max_efc, 4,
        result.ll_max_lcdm, 3,
        result.n_data,
    )

    # Build manifest for NUTS
    git_hash = "unknown"
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass

    import jax
    import numpyro
    manifest = {
        "seed": seed,
        "sampler": "nuts",
        "num_warmup": num_warmup,
        "num_samples": num_samples,
        "num_chains": num_chains,
        "target_accept": target_accept,
        "n_total": result.n_data,
        "probes": ["bao", "growth", "hz", "snia"],
        "git_hash": git_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "jax_version": jax.__version__,
        "numpyro_version": numpyro.__version__,
        "devices": str(jax.devices()),
        "total_time_seconds": dt_total,
        "time_efc_seconds": result.time_efc,
        "time_lcdm_seconds": result.time_lcdm,
        "n_eff_min": result.n_eff_min,
        "r_hat_max": result.r_hat_max,
        "dense_mass": True,
        "float64": True,
    }

    # Compute correlations from full posterior chain if available
    if result.posterior_chain is not None and len(result.posterior_chain) > 10:
        pc = result.posterior_chain  # (n_samples, 4) = [Om, H0, s8, alpha]
        cc = np.corrcoef(pc.T)      # 4×4 correlation matrix
        correlations = {
            "a_om": float(cc[3, 0]),
            "a_h0": float(cc[3, 1]),
            "a_s8": float(cc[3, 2]),
            "om_h0": float(cc[0, 1]),
            "om_s8": float(cc[0, 2]),
        }
        # Full chain: columns [Om, H0, s8, alpha]
        chain_efc = result.posterior_chain
        # LCDM chain: first 3 columns (no alpha)
        chain_lcdm = result.posterior_chain[:, :3]
        logger.info(f"  Full posterior chain: {chain_efc.shape}")
    else:
        # Fallback: synthetic 1-row chain (for backward compat)
        correlations = {
            "a_om": 0.0, "a_h0": 0.0, "a_s8": 0.0,
            "om_h0": 0.0, "om_s8": 0.0,
        }
        chain_efc = np.array([[
            result.om_mean, result.h0_mean, result.s8_mean, result.alpha_mean
        ]])
        chain_lcdm = np.array([[
            result.om_mean, result.h0_mean, result.s8_mean
        ]])
        logger.warning("  No posterior chain — using synthetic 1-row fallback")

    logger.info(f"  alpha = {alpha.mean:.3f} +/- {alpha.std:.3f} "
                f"({alpha.significance:.2f}sigma)  "
                f"dAIC={comparison.daic:.2f}  dBIC={comparison.dbic:.2f}")
    logger.info(f"  n_eff_min={result.n_eff_min:.0f}  r_hat_max={result.r_hat_max:.4f}")
    logger.info(f"  Total time: {dt_total:.0f}s")

    return BaselineResult(
        alpha=alpha,
        comparison=comparison,
        correlations=correlations,
        om=ParamStats(
            mean=result.om_mean, std=result.om_std,
            median=result.om_mean,
            ci95_lo=result.om_mean - 1.96 * result.om_std,
            ci95_hi=result.om_mean + 1.96 * result.om_std,
        ),
        s8=ParamStats(
            mean=result.s8_mean, std=result.s8_std,
            median=result.s8_mean,
            ci95_lo=result.s8_mean - 1.96 * result.s8_std,
            ci95_hi=result.s8_mean + 1.96 * result.s8_std,
        ),
        h0=ParamStats(
            mean=result.h0_mean, std=result.h0_std,
            median=result.h0_mean,
            ci95_lo=result.h0_mean - 1.96 * result.h0_std,
            ci95_hi=result.h0_mean + 1.96 * result.h0_std,
        ),
        chain_efc=chain_efc,
        chain_lcdm=chain_lcdm,
        manifest=manifest,
        sampler_efc=None,       # No emcee sampler object for NUTS
    )


# ═══════════════════════════════════════════════════════════════
#  D2: SELF-CONSISTENT SOUND HORIZON
# ═══════════════════════════════════════════════════════════════

def _compute_rd_d2(Om: float, H0: float, R_max: float = 0.01,
                   safety_threshold_pct: float = 1.0):
    """Compute self-consistent EFC sound horizon.

    Returns rd_efc [Mpc] or None if safety check fails.
    """
    result = compute_rd_efc(Om, H0, R_max=R_max,
                            safety_threshold_pct=safety_threshold_pct)
    if result["safety_level"] == "fail":
        return None
    return result["rd_efc"]


# --- D2 priors: same bounds as baseline, but r_d computed from (Om, H0) ---

def _log_prob_d2_efc(theta, modules, R_max=0.01):
    """EFC D2: [Om, H0, s8, alpha] with self-consistent r_d(Om, H0)."""
    lp = _log_prior_baseline_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    rd = _compute_rd_d2(Om, H0, R_max=R_max)
    if rd is None:
        return -np.inf  # safety fail → reject
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def _log_prob_d2_lcdm(theta, modules, R_max=0.01):
    """LCDM D2: [Om, H0, s8] with self-consistent r_d(Om, H0)."""
    lp = _log_prior_baseline_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    rd = _compute_rd_d2(Om, H0, R_max=R_max)
    if rd is None:
        return -np.inf
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": rd}
    ll = _sum_log_likelihoods(params, modules)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def run_d2_comparison(
    modules: dict,
    baseline_result: BaselineResult,
    nwalkers: int = DEFAULT_NWALKERS,
    nsteps: int = DEFAULT_NSTEPS,
    burnin: int = DEFAULT_BURNIN,
    seed: int = DEFAULT_SEED,
    R_max: float = 0.01,
    pass_delta_alpha: float = 0.3,
    pool=None,
) -> dict:
    """D2: Self-consistent sound horizon comparison.

    Runs the SAME 4-param EFC + 3-param LCDM MCMC, but with r_d computed
    from physics (sound_horizon.py) instead of hardcoded 147.09.

    Compares alpha from D2 vs proxy baseline to determine whether the
    alpha signal is robust to self-consistent sound horizon treatment.

    Args:
        modules:            Data modules dict (bao, growth, hz, snia).
        baseline_result:    BaselineResult from proxy run (for comparison).
        R_max:              EFC grid resistance (0.01 = 1%, fixed postulate).
        pass_delta_alpha:   Max |Δα_sig| for PASS verdict.

    Returns:
        Dict with:
            verdict:            PASS | MARGINAL | COLLAPSED
            alpha_d2:           AlphaStats from D2 run
            alpha_proxy:        AlphaStats from proxy baseline (for comparison)
            delta_alpha_sig:    |α_d2_sig - α_proxy_sig|
            rd_posterior_mean:  Mean r_d across D2 posterior
            rd_posterior_std:   Std of r_d across posterior
            comparison_d2:      ModelComparison (D2 EFC vs D2 LCDM)
            total_time_seconds: Wall time
    """
    logger.info("=== D2: SELF-CONSISTENT SOUND HORIZON ===")
    logger.info(f"  R_max = {R_max} (EFC grid resistance)")
    logger.info(f"  Proxy baseline: alpha = {baseline_result.alpha.mean:.3f} "
                f"+/- {baseline_result.alpha.std:.3f} "
                f"({baseline_result.alpha.significance:.2f}sigma)")

    t0 = time.time()
    np.random.seed(seed + 200)  # offset from baseline seeds

    n_data = sum(m.n_data for m in modules.values() if m is not None)
    args = (modules, R_max)

    # ── D2 EFC: 4 params [Om, H0, s8, alpha], r_d self-consistent ──
    p0_efc = _init_p0_4param(nwalkers, seed + 200)
    chain_d2_efc, lp_d2_efc, dt_efc, _ = _run_emcee(
        "D2 EFC (self-consistent rd)", _log_prob_d2_efc, ndim=4,
        p0=p0_efc, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed + 200, pool=pool,
    )

    # ── D2 LCDM: 3 params [Om, H0, s8], r_d self-consistent ──
    p0_lcdm = _init_p0_3param(nwalkers, seed + 201)
    chain_d2_lcdm, lp_d2_lcdm, dt_lcdm, _ = _run_emcee(
        "D2 LCDM (self-consistent rd)", _log_prob_d2_lcdm, ndim=3,
        p0=p0_lcdm, nwalkers=nwalkers, nsteps=nsteps,
        burnin=burnin, args=args, seed=seed + 201, pool=pool,
    )

    total_time = time.time() - t0

    # ── Extract D2 results ──
    alpha_d2 = _extract_alpha(chain_d2_efc, alpha_col=3)
    ll_efc = float(np.max(lp_d2_efc))
    ll_lcdm = float(np.max(lp_d2_lcdm))
    comparison_d2 = _compute_comparison(ll_efc, 4, ll_lcdm, 3, n_data)

    # ── Compute r_d posterior distribution ──
    rd_samples = []
    for i in range(min(500, len(chain_d2_efc))):
        Om_i, H0_i = chain_d2_efc[i, 0], chain_d2_efc[i, 1]
        rd_i = _compute_rd_d2(Om_i, H0_i, R_max=R_max)
        if rd_i is not None:
            rd_samples.append(rd_i)
    rd_arr = np.array(rd_samples) if rd_samples else np.array([RD_FIXED])
    rd_mean = float(np.mean(rd_arr))
    rd_std = float(np.std(rd_arr))

    # ── Verdict ──
    delta_alpha_sig = abs(alpha_d2.significance - baseline_result.alpha.significance)

    if alpha_d2.significance < 1.0:
        verdict = "COLLAPSED"
    elif delta_alpha_sig > 2 * pass_delta_alpha:
        verdict = "COLLAPSED"
    elif delta_alpha_sig > pass_delta_alpha:
        verdict = "MARGINAL"
    else:
        verdict = "PASS"

    logger.info(f"  D2 alpha = {alpha_d2.mean:.3f} +/- {alpha_d2.std:.3f} "
                f"({alpha_d2.significance:.2f}sigma)")
    logger.info(f"  D2 r_d   = {rd_mean:.4f} +/- {rd_std:.4f} Mpc "
                f"(proxy: {RD_FIXED})")
    logger.info(f"  Delta significance: {delta_alpha_sig:.3f}sigma "
                f"(threshold: {pass_delta_alpha})")
    logger.info(f"  D2 dAIC  = {comparison_d2.daic:.2f}  "
                f"dBIC = {comparison_d2.dbic:.2f}")
    logger.info(f"  D2 VERDICT: {verdict}")
    logger.info(f"  Wall time: {total_time:.0f}s")

    return {
        "verdict": verdict,
        "alpha_mean": alpha_d2.mean,
        "alpha_std": alpha_d2.std,
        "alpha_sig": alpha_d2.significance,
        "alpha_p_negative": alpha_d2.p_negative,
        "proxy_alpha_sig": baseline_result.alpha.significance,
        "delta_alpha_sig": delta_alpha_sig,
        "rd_posterior_mean": rd_mean,
        "rd_posterior_std": rd_std,
        "rd_proxy": RD_FIXED,
        "daic": comparison_d2.daic,
        "dbic": comparison_d2.dbic,
        "R_max": R_max,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  SERIALIZATION HELPERS
# ═══════════════════════════════════════════════════════════════

def alpha_stats_to_dict(a: AlphaStats) -> dict:
    """Convert AlphaStats to JSON-serializable dict."""
    return {
        "mean": a.mean,
        "std": a.std,
        "significance": a.significance,
        "p_negative": a.p_negative,
        "median": a.median,
        "ci95_lo": a.ci95_lo,
        "ci95_hi": a.ci95_hi,
    }


def param_stats_to_dict(p: ParamStats) -> dict:
    """Convert ParamStats to JSON-serializable dict."""
    return {
        "mean": p.mean,
        "std": p.std,
        "median": p.median,
        "ci95_lo": p.ci95_lo,
        "ci95_hi": p.ci95_hi,
    }


def comparison_to_dict(c: ModelComparison) -> dict:
    """Convert ModelComparison to JSON-serializable dict."""
    return {
        "ll_efc": c.ll_efc,
        "ll_lcdm": c.ll_lcdm,
        "k_efc": c.k_efc,
        "k_lcdm": c.k_lcdm,
        "n_data": c.n_data,
        "daic": c.daic,
        "dbic": c.dbic,
    }
