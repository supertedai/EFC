#!/usr/bin/env python3
"""
Step 1: BAO + H(z) with pure LCDM (no β) — anchor Ω_m for Step 2.

Morten: "Lås Ω_m med BAO først (uten β)."

Rationale:
    BAO and H(z) constrain geometry/background — they do NOT depend on
    growth of structure. A clean Ω_m posterior from these alone gives us
    an informative prior for Step 2 (VariantJ + fs8).

Setup:
    model:     FlatLCDM (pure, no gate, no β)
    sample:    Ω_m, H0
    fixed:     r_d = 147.09 Mpc (Planck-calibrated sound horizon)
    data:
        BAO:   DESI DR2 (13 points, full 13x13 covariance)
        H(z):  cosmic chronometers (~15 points, diagonal)

Config:
    nwalkers = 32
    nsteps   = 1500
    burnin   = 300

Outputs:
    outputs/grav_bridge/step1_chain_<timestamp>.npz
    outputs/grav_bridge/step1_summary_<timestamp>.json
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

from efc_grav_bridge import FlatLCDM  # noqa: E402
from efc_grav_bridge import EFCHubble  # noqa: E402
from efc_grav_bridge import BAOModule  # noqa: E402
from efc_grav_bridge import HzModule  # noqa: E402


# ─── Fixed physics ─────────────────────────────────────────────
R_D_FIXED = 147.09   # Mpc — Planck 2018 sound horizon
BAO_PATH = REPO_ROOT / "data" / "bao_desi_dr2.json"
HZ_PATH = REPO_ROOT / "data" / "hz_cosmic_chronometers.csv"
OUT_DIR = REPO_ROOT / "outputs"

# ─── MCMC config ───────────────────────────────────────────────
NWALKERS = 32
NSTEPS = 1500
NBURN = 300
NDIM = 2
SEED = 42

# ─── Priors (wide) ─────────────────────────────────────────────
OMEGA_M_LO, OMEGA_M_HI = 0.15, 0.55
H0_LO, H0_HI = 55.0, 85.0


def log_prior(theta):
    Om, H0 = float(theta[0]), float(theta[1])
    if not (OMEGA_M_LO < Om < OMEGA_M_HI):
        return -np.inf
    if not (H0_LO < H0 < H0_HI):
        return -np.inf
    return 0.0


def make_log_prob(bao_mod, hz_mod):
    def log_prob(theta):
        lp = log_prior(theta)
        if not np.isfinite(lp):
            return -np.inf
        params = {
            "Omega_m": float(theta[0]),
            "H0": float(theta[1]),
            "alpha_cosmo": 0.0,
            "r_d": R_D_FIXED,
        }
        try:
            ll_bao = bao_mod.log_likelihood(params)
            ll_hz = hz_mod.log_likelihood(params)
        except Exception:
            return -np.inf
        total = ll_bao + ll_hz
        if not np.isfinite(total):
            return -np.inf
        return lp + total
    return log_prob


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print(" Step 1: BAO + H(z) LCDM MCMC — anchor Ω_m for VariantJ constraint")
    print("=" * 80)

    # ── Setup ────────────────────────────────────────────────
    cosmo = FlatLCDM()
    engine = EFCHubble(cosmology=cosmo)
    bao = BAOModule(engine=engine)
    bao.load_data(data_path=str(BAO_PATH))
    hz = HzModule(engine=engine)
    hz.load_data(data_path=str(HZ_PATH))
    print(f"\nBAO data : {bao.n_data} points (DESI DR2)")
    print(f"H(z) data: {hz.n_data} points (cosmic chronometers)")

    # ── Anchor LL ────────────────────────────────────────────
    anchor = {"Omega_m": 0.315, "H0": 67.4, "alpha_cosmo": 0.0, "r_d": R_D_FIXED}
    ll_bao_anchor = bao.log_likelihood(anchor)
    ll_hz_anchor = hz.log_likelihood(anchor)
    print(f"\nAnchor log L at (Ω_m=0.315, H0=67.4, r_d=147.09):")
    print(f"  BAO  : {ll_bao_anchor:+.3f}")
    print(f"  H(z) : {ll_hz_anchor:+.3f}")
    print(f"  total: {ll_bao_anchor + ll_hz_anchor:+.3f}")

    # ── Init walkers around Planck ───────────────────────────
    rng = np.random.default_rng(SEED)
    p0 = np.column_stack([
        rng.uniform(0.28, 0.35, size=NWALKERS),
        rng.uniform(65.0, 72.0, size=NWALKERS),
    ])

    log_prob_fn = make_log_prob(bao, hz)
    print(f"\nMCMC: nwalkers={NWALKERS} nsteps={NSTEPS} burnin={NBURN} seed={SEED}")

    sampler = emcee.EnsembleSampler(NWALKERS, NDIM, log_prob_fn)

    t0 = time.time()
    print("  [burn-in]    ...", end=" ", flush=True)
    state = sampler.run_mcmc(p0, NBURN, progress=False)
    sampler.reset()
    print(f"done ({time.time()-t0:.1f}s)")

    t1 = time.time()
    print("  [production] ...", end=" ", flush=True)
    sampler.run_mcmc(state, NSTEPS, progress=False)
    print(f"done ({time.time()-t1:.1f}s)")

    dt = time.time() - t0
    acc = float(np.mean(sampler.acceptance_fraction))
    try:
        tau = sampler.get_autocorr_time(tol=0, quiet=True)
    except Exception:
        tau = np.array([np.nan, np.nan])

    samples = sampler.get_chain(flat=True)
    log_probs = sampler.get_log_prob(flat=True)
    Om_s = samples[:, 0]
    H0_s = samples[:, 1]

    Om_mean = float(np.mean(Om_s))
    Om_std = float(np.std(Om_s))
    Om_med = float(np.median(Om_s))
    Om_q16 = float(np.percentile(Om_s, 16))
    Om_q84 = float(np.percentile(Om_s, 84))

    H0_mean = float(np.mean(H0_s))
    H0_std = float(np.std(H0_s))
    H0_med = float(np.median(H0_s))
    H0_q16 = float(np.percentile(H0_s, 16))
    H0_q84 = float(np.percentile(H0_s, 84))

    r_Om_H0 = float(np.corrcoef(Om_s, H0_s)[0, 1])

    print(f"\nRuntime: {dt:.1f}s  Acceptance: {acc:.3f}  τ: {tuple(tau)}")
    print(f"\nPosterior (informative prior for Step 2):")
    print(f"  Ω_m = {Om_med:.5f} ± {Om_std:.5f}   [{Om_q16:.5f}, {Om_q84:.5f}]")
    print(f"  H0  = {H0_med:.3f} ± {H0_std:.3f}   [{H0_q16:.3f}, {H0_q84:.3f}]")
    print(f"  r(Ω_m, H0) = {r_Om_H0:+.4f}")

    # ── Save ────────────────────────────────────────────────
    summary = {
        "config": {
            "step": "1_bao_hz_lcdm_anchor",
            "model": "FlatLCDM",
            "nwalkers": NWALKERS,
            "nsteps": NSTEPS,
            "nburn": NBURN,
            "seed": SEED,
            "r_d_fixed_Mpc": R_D_FIXED,
            "priors": {
                "Omega_m": [OMEGA_M_LO, OMEGA_M_HI],
                "H0": [H0_LO, H0_HI],
            },
        },
        "data": {
            "bao": {"path": str(BAO_PATH.relative_to(REPO_ROOT)), "n_points": int(bao.n_data)},
            "hz": {"path": str(HZ_PATH.relative_to(REPO_ROOT)), "n_points": int(hz.n_data)},
        },
        "anchors": {
            "ll_bao_at_planck": round(float(ll_bao_anchor), 4),
            "ll_hz_at_planck": round(float(ll_hz_anchor), 4),
        },
        "runtime_seconds": round(dt, 2),
        "diagnostics": {
            "acceptance_fraction": round(acc, 3),
            "autocorr_time": [float(t) if np.isfinite(t) else None for t in tau],
        },
        "Omega_m_posterior": {
            "mean": round(Om_mean, 6),
            "median": round(Om_med, 6),
            "std": round(Om_std, 6),
            "q16": round(Om_q16, 6),
            "q84": round(Om_q84, 6),
        },
        "H0_posterior": {
            "mean": round(H0_mean, 4),
            "median": round(H0_med, 4),
            "std": round(H0_std, 4),
            "q16": round(H0_q16, 4),
            "q84": round(H0_q84, 4),
        },
        "pearson_r_Om_H0": round(r_Om_H0, 4),
        "use_as_prior_in_step_2": {
            "Omega_m_gaussian_prior": {
                "mean": round(Om_mean, 5),
                "std": round(Om_std, 5),
            },
        },
    }

    chain_path = OUT_DIR / f"step1_chain_{ts}.npz"
    summary_path = OUT_DIR / f"step1_summary_{ts}.json"
    np.savez_compressed(
        chain_path,
        samples=samples,
        log_prob=log_probs,
        acceptance_fraction=sampler.acceptance_fraction,
        Omega_m=Om_s,
        H0=H0_s,
    )
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nOutputs:")
    print(f"  chain   : {chain_path}")
    print(f"  summary : {summary_path}")
    print("\nSummary file also contains `use_as_prior_in_step_2` block for Step 2 to consume.")
    print("=" * 80)


if __name__ == "__main__":
    main()
