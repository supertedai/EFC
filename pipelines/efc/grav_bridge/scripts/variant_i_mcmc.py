#!/usr/bin/env python3
"""
EFCVariantI Minimal MCMC — Vei Z GRAV→cosmo bridge first chain.

Samples (Ω_m, C) against fs8_extended data (with BOSS DR12 3x3 covariance).
σ8 is FIXED at 0.81 (Planck) to avoid σ8–C degeneracy.

Config (Morten's lock):
    nwalkers = 16
    nsteps   = 500
    burnin   = 100
    priors:
        Ω_m  Uniform(0.2, 0.5)
        C    Uniform(0.5, 5.0)

Pre-sanity: prints LL at (Ω_m=0.3, C=1.0) and (Ω_m=0.3, C=2.32)
so we can confirm the likelihood function responds to C before sampling.

Outputs:
    outputs/grav_bridge/variant_i_chain_<timestamp>.npz
    outputs/grav_bridge/variant_i_summary_<timestamp>.json

Usage:
    python3 scripts/grav_bridge/variant_i_mcmc.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import emcee  # noqa: E402

from efc_grav_bridge import EFCVariantI  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402
from efc_grav_bridge import GrowthModule  # noqa: E402


# ─── Fixed physics (Morten's lock) ──────────────────────────────
SIGMA8_FIXED = 0.81   # Planck — avoid σ8–C degeneracy
H0_FIXED = 70.0       # km/s/Mpc — fσ8 is weakly H0-sensitive
DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

# ─── MCMC config (Morten's lock: minimal first) ─────────────────
NWALKERS = 16
NSTEPS = 500
NBURN = 100
NDIM = 2              # Ω_m, C
SEED = 42

# ─── Priors ─────────────────────────────────────────────────────
OMEGA_M_LO, OMEGA_M_HI = 0.2, 0.5
C_LO, C_HI = 0.5, 5.0


def log_prior(theta: np.ndarray) -> float:
    Omega_m, C = float(theta[0]), float(theta[1])
    if not (OMEGA_M_LO < Omega_m < OMEGA_M_HI):
        return -np.inf
    if not (C_LO < C < C_HI):
        return -np.inf
    return 0.0


def make_log_prob(module: GrowthModule):
    """Closure capturing the (already-loaded) data module."""
    def log_prob(theta: np.ndarray) -> float:
        lp = log_prior(theta)
        if not np.isfinite(lp):
            return -np.inf
        params = {
            "Omega_m": float(theta[0]),
            "H0": H0_FIXED,
            "sigma8": SIGMA8_FIXED,
            "alpha_cosmo": 0.0,
            "C": float(theta[1]),
        }
        try:
            ll = module.log_likelihood(params)
        except Exception:
            return -np.inf
        if not np.isfinite(ll):
            return -np.inf
        return lp + ll
    return log_prob


def verdict(c_mean: float, c_std: float) -> str:
    """Qualitative verdict on the C posterior."""
    if c_std > 1.2:
        return "FLAT_POSTERIOR  — data cannot distinguish C in [0.5, 5]"
    if abs(c_mean - 1.0) < 1.5 * c_std:
        return "GR_COMPATIBLE   — C → 1 within ~1.5σ (GRAV bridge not preferred)"
    if abs(c_mean - 2.32) < 1.5 * c_std:
        return "GRAV_CONSISTENT — C → 2.32 within ~1.5σ (bridge holds)"
    return "NON_TRIVIAL     — C away from both GR and KT2 prior"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 72)
    print(" EFCVariantI Minimal MCMC — Vei Z GRAV→cosmo bridge")
    print("=" * 72)

    # ── Load data ────────────────────────────────────────────
    engine = EFCGrowth(cosmology=EFCVariantI())
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    cov_status = "3x3 BOSS covariance + diagonal" if module._cov_inv is not None else "diagonal only"
    print(f"\nData: {module.n_data} fσ8 points — {cov_status}")

    # ── Pre-sanity: LL at anchor points ──────────────────────
    anchor_c1 = {"Omega_m": 0.3, "H0": H0_FIXED, "sigma8": SIGMA8_FIXED,
                 "alpha_cosmo": 0.0, "C": 1.0}
    anchor_c232 = {**anchor_c1, "C": 2.32}
    anchor_c5 = {**anchor_c1, "C": 5.0}
    ll_c1 = module.log_likelihood(anchor_c1)
    ll_c232 = module.log_likelihood(anchor_c232)
    ll_c5 = module.log_likelihood(anchor_c5)
    print(f"\nAnchor log-likelihoods at Ω_m=0.3, σ8=0.81:")
    print(f"  C = 1.00  →  log L = {ll_c1:+.4f}   (LCDM baseline)")
    print(f"  C = 2.32  →  log L = {ll_c232:+.4f}   (KT2 GRAV prior)")
    print(f"  C = 5.00  →  log L = {ll_c5:+.4f}   (extreme check)")
    print(f"  Δlog L (C=1 → C=2.32) = {ll_c232 - ll_c1:+.4f}")

    # ── Initialize walkers near LCDM ─────────────────────────
    rng = np.random.default_rng(SEED)
    p0 = np.column_stack([
        rng.uniform(0.27, 0.33, size=NWALKERS),
        rng.uniform(0.8, 1.6, size=NWALKERS),
    ])

    log_prob_fn = make_log_prob(module)

    # ── Run MCMC ─────────────────────────────────────────────
    print(f"\nMCMC config: nwalkers={NWALKERS}  nsteps={NSTEPS}  burnin={NBURN}  seed={SEED}")
    sampler = emcee.EnsembleSampler(NWALKERS, NDIM, log_prob_fn)

    t0 = time.time()
    print("  [burn-in]   ...", end=" ", flush=True)
    state = sampler.run_mcmc(p0, NBURN, progress=False)
    sampler.reset()
    print(f"done ({time.time() - t0:.1f}s)")

    t1 = time.time()
    print("  [production] ...", end=" ", flush=True)
    sampler.run_mcmc(state, NSTEPS, progress=False)
    dt_prod = time.time() - t1
    dt_total = time.time() - t0
    print(f"done ({dt_prod:.1f}s)")

    # ── Diagnostics ──────────────────────────────────────────
    acc = float(np.mean(sampler.acceptance_fraction))
    try:
        tau = sampler.get_autocorr_time(tol=0, quiet=True)
    except Exception:
        tau = np.array([np.nan, np.nan])

    samples = sampler.get_chain(flat=True)  # (nwalkers*nsteps, ndim)
    log_probs = sampler.get_log_prob(flat=True)
    Omega_m_samples = samples[:, 0]
    C_samples = samples[:, 1]

    c_mean = float(np.mean(C_samples))
    c_std = float(np.std(C_samples))
    c_median = float(np.median(C_samples))
    c_q16 = float(np.percentile(C_samples, 16))
    c_q84 = float(np.percentile(C_samples, 84))

    sigma_from_gr = abs(c_mean - 1.0) / c_std if c_std > 0 else float("inf")
    sigma_from_grav = abs(c_mean - 2.32) / c_std if c_std > 0 else float("inf")

    results = {
        "config": {
            "model": "EFCVariantI",
            "path": "Vei_Z (low-pass, k_L=0.05 h/Mpc, k_eff=0.1 h/Mpc)",
            "nwalkers": NWALKERS,
            "nsteps": NSTEPS,
            "nburn": NBURN,
            "seed": SEED,
            "sigma8_fixed": SIGMA8_FIXED,
            "H0_fixed": H0_FIXED,
            "prior_Omega_m": [OMEGA_M_LO, OMEGA_M_HI],
            "prior_C": [C_LO, C_HI],
        },
        "data": {
            "n_points": int(module.n_data),
            "z_range": [float(module.coordinates.min()), float(module.coordinates.max())],
            "covariance": cov_status,
        },
        "anchors": {
            "ll_C_1.00": round(float(ll_c1), 4),
            "ll_C_2.32": round(float(ll_c232), 4),
            "ll_C_5.00": round(float(ll_c5), 4),
            "dll_c1_to_c232": round(float(ll_c232 - ll_c1), 4),
        },
        "runtime_seconds": round(dt_total, 2),
        "acceptance_fraction": round(acc, 3),
        "autocorr_time": [float(t) if np.isfinite(t) else None for t in tau],
        "Omega_m_posterior": {
            "mean": round(float(np.mean(Omega_m_samples)), 5),
            "std": round(float(np.std(Omega_m_samples)), 5),
            "median": round(float(np.median(Omega_m_samples)), 5),
            "q16": round(float(np.percentile(Omega_m_samples, 16)), 5),
            "q84": round(float(np.percentile(Omega_m_samples, 84)), 5),
        },
        "C_posterior": {
            "mean": round(c_mean, 5),
            "std": round(c_std, 5),
            "median": round(c_median, 5),
            "q16": round(c_q16, 5),
            "q84": round(c_q84, 5),
            "frac_within_0.1_of_1.00": round(float(np.mean(np.abs(C_samples - 1.0) < 0.1)), 4),
            "frac_within_0.1_of_2.32": round(float(np.mean(np.abs(C_samples - 2.32) < 0.1)), 4),
            "p_C_lt_1.2": round(float(np.mean(C_samples < 1.2)), 4),
            "p_C_gt_2.0": round(float(np.mean(C_samples > 2.0)), 4),
        },
        "diagnostics": {
            "sigma_from_GR_C_eq_1": round(sigma_from_gr, 3),
            "sigma_from_KT2_C_eq_2p32": round(sigma_from_grav, 3),
            "verdict": verdict(c_mean, c_std),
        },
    }

    # ── Save ─────────────────────────────────────────────────
    chain_path = OUT_DIR / f"variant_i_chain_{ts}.npz"
    summary_path = OUT_DIR / f"variant_i_summary_{ts}.json"
    np.savez_compressed(
        chain_path,
        samples=samples,
        log_prob=log_probs,
        acceptance_fraction=sampler.acceptance_fraction,
        Omega_m=Omega_m_samples,
        C=C_samples,
    )
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    # ── Report ───────────────────────────────────────────────
    print(f"\nRuntime: {dt_total:.1f}s  Acceptance: {acc:.3f}  τ(Ω_m, C) = {tuple(tau)}")
    print(f"\nPosterior:")
    print(f"  Ω_m = {results['Omega_m_posterior']['mean']:.4f} ± {results['Omega_m_posterior']['std']:.4f}   "
          f"[{results['Omega_m_posterior']['q16']:.4f}, {results['Omega_m_posterior']['q84']:.4f}]")
    print(f"  C   = {c_mean:.4f} ± {c_std:.4f}   "
          f"[{c_q16:.4f}, {c_q84:.4f}]")
    print(f"\nConsistency:")
    print(f"  σ from GR  (C=1.00):   {sigma_from_gr:.2f}")
    print(f"  σ from KT2 (C=2.32):   {sigma_from_grav:.2f}")
    print(f"  p(C < 1.2): {results['C_posterior']['p_C_lt_1.2']:.3f}")
    print(f"  p(C > 2.0): {results['C_posterior']['p_C_gt_2.0']:.3f}")
    print(f"\n>>> VERDICT: {results['diagnostics']['verdict']} <<<")
    print(f"\nOutputs:")
    print(f"  chain   : {chain_path}")
    print(f"  summary : {summary_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
