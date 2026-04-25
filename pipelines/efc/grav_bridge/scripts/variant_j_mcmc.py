#!/usr/bin/env python3
"""
EFCVariantJ Full MCMC — Phase 2 Step 2

Quantifies the friction-channel coupling that survived the β sweep.

Morten's requirements:
    1. Posterior form: symmetric around 0, or skewed?
    2. Bayes-factor-ish indication: β ≠ 0 vs β = 0
    3. Degeneracy with Ω_m (critical — friction can mimic Ω_m shifts)

Setup:
    sample:  Ω_m, β
    fixed:   σ_8 = 0.81, H0 = 70
    prior:
        Ω_m ~ U(0.2, 0.5)
        β   ~ U(-2, 2)

Config:
    nwalkers = 32
    nsteps   = 1500
    burnin   = 300

Outputs:
    outputs/grav_bridge/variant_j_chain_<timestamp>.npz
    outputs/grav_bridge/variant_j_summary_<timestamp>.json
    outputs/grav_bridge/variant_j_plots_<timestamp>/{corner,fs8_curves,residuals,chi2_beta}.png

Usage:
    python3 scripts/grav_bridge/variant_j_mcmc.py
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
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import gaussian_kde  # noqa: E402

from efc_grav_bridge import EFCVariantJ  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402
from efc_grav_bridge import GrowthModule  # noqa: E402


# ─── Fixed physics ──────────────────────────────────────────────
SIGMA8_FIXED = 0.81
H0_FIXED = 70.0
DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

# ─── MCMC config ────────────────────────────────────────────────
NWALKERS = 32
NSTEPS = 1500
NBURN = 300
NDIM = 2              # Ω_m, β
SEED = 42

# ─── Priors ─────────────────────────────────────────────────────
OMEGA_M_LO, OMEGA_M_HI = 0.2, 0.5
BETA_LO, BETA_HI = -2.0, 2.0

PRIOR_DENSITY_BETA_AT_0 = 1.0 / (BETA_HI - BETA_LO)  # 0.25 for U(-2, 2)


def log_prior(theta: np.ndarray) -> float:
    Omega_m, beta = float(theta[0]), float(theta[1])
    if not (OMEGA_M_LO < Omega_m < OMEGA_M_HI):
        return -np.inf
    if not (BETA_LO < beta < BETA_HI):
        return -np.inf
    return 0.0


def make_log_prob(module: GrowthModule):
    def log_prob(theta: np.ndarray) -> float:
        lp = log_prior(theta)
        if not np.isfinite(lp):
            return -np.inf
        params = {
            "Omega_m": float(theta[0]),
            "H0": H0_FIXED,
            "sigma8": SIGMA8_FIXED,
            "alpha_cosmo": 0.0,
            "beta": float(theta[1]),
        }
        try:
            ll = module.log_likelihood(params)
        except Exception:
            return -np.inf
        if not np.isfinite(ll):
            return -np.inf
        return lp + ll
    return log_prob


def compute_fs8_model(module: GrowthModule, z_arr: np.ndarray,
                      Omega_m: float, beta: float) -> np.ndarray:
    params = {
        "Omega_m": float(Omega_m),
        "H0": H0_FIXED,
        "sigma8": SIGMA8_FIXED,
        "alpha_cosmo": 0.0,
        "beta": float(beta),
    }
    return module.engine.compute(params, z_arr)


def plot_corner_2d(Omega_m_samples, beta_samples, out_path):
    """Custom 2D posterior plot (corner-like)."""
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3],
                           hspace=0.05, wspace=0.05)

    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)

    # Main: 2D hist
    ax_main.hist2d(Omega_m_samples, beta_samples, bins=60, cmap="viridis")
    ax_main.axhline(0, color="white", ls="--", lw=1, alpha=0.6)
    ax_main.axvline(0.315, color="white", ls=":", lw=1, alpha=0.6, label="Planck Ω_m")
    ax_main.set_xlabel("Ω_m")
    ax_main.set_ylabel("β (friction coupling)")
    ax_main.grid(alpha=0.2)
    ax_main.legend(loc="upper right", fontsize=8)

    # Top: Ω_m marginal
    ax_top.hist(Omega_m_samples, bins=60, color="steelblue", edgecolor="white", alpha=0.8)
    ax_top.axvline(0.315, color="red", ls=":", alpha=0.5)
    ax_top.set_ylabel("N")
    ax_top.tick_params(axis="x", labelbottom=False)

    # Right: β marginal
    ax_right.hist(beta_samples, bins=60, orientation="horizontal",
                  color="coral", edgecolor="white", alpha=0.8)
    ax_right.axhline(0, color="black", ls="--", alpha=0.5, label="β=0 (LCDM)")
    ax_right.set_xlabel("N")
    ax_right.tick_params(axis="y", labelleft=False)
    ax_right.legend(fontsize=8, loc="upper right")

    # Pearson correlation
    r = float(np.corrcoef(Omega_m_samples, beta_samples)[0, 1])
    fig.suptitle(f"VariantJ posterior — Pearson r(Ω_m, β) = {r:+.3f}", y=0.98)

    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_fs8_curves(module, z_data, fs8_data, sigma_data,
                    Omega_m_med, beta_med, beta_q16, beta_q84,
                    out_path):
    """Plot data + LCDM + posterior mean + ±1σ band."""
    z_model = np.linspace(0.01, 1.2, 120)
    fs8_lcdm = compute_fs8_model(module, z_model, Omega_m_med, 0.0)
    fs8_med = compute_fs8_model(module, z_model, Omega_m_med, beta_med)
    fs8_lo = compute_fs8_model(module, z_model, Omega_m_med, beta_q16)
    fs8_hi = compute_fs8_model(module, z_model, Omega_m_med, beta_q84)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Data
    ax.errorbar(z_data, fs8_data, yerr=sigma_data, fmt="o", color="black",
                label="fσ8 data (7 points)", zorder=5, markersize=7, capsize=3)

    # Models
    ax.plot(z_model, fs8_lcdm, "-", color="#1f77b4", lw=2, label="LCDM (β=0)")
    ax.plot(z_model, fs8_med, "--", color="#d62728", lw=2,
            label=f"VariantJ posterior median (β={beta_med:+.3f})")
    ax.fill_between(z_model, fs8_lo, fs8_hi, color="#d62728", alpha=0.2,
                    label=f"β ∈ [{beta_q16:+.3f}, {beta_q84:+.3f}] (68% CI)")

    ax.set_xlabel("z")
    ax.set_ylabel("fσ8(z)")
    ax.set_title("VariantJ — fσ8 predictions at posterior median Ω_m")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_residuals(module, z_data, fs8_data, sigma_data,
                   Omega_m_med, beta_med, out_path):
    """Residuals: data − model for LCDM and posterior median."""
    fs8_lcdm = compute_fs8_model(module, z_data, Omega_m_med, 0.0)
    fs8_j = compute_fs8_model(module, z_data, Omega_m_med, beta_med)

    res_lcdm = fs8_data - fs8_lcdm
    res_j = fs8_data - fs8_j

    fig, ax = plt.subplots(figsize=(10, 5))
    # Slight horizontal offsets for readability
    w = 0.008
    ax.errorbar(z_data - w, res_lcdm, yerr=sigma_data, fmt="o", color="#1f77b4",
                label=f"LCDM residuals (Σr²/σ² = {float(np.sum((res_lcdm/sigma_data)**2)):.2f})",
                capsize=3, markersize=7)
    ax.errorbar(z_data + w, res_j, yerr=sigma_data, fmt="s", color="#d62728",
                label=f"VariantJ residuals (Σr²/σ² = {float(np.sum((res_j/sigma_data)**2)):.2f})",
                capsize=3, markersize=7)
    ax.axhline(0, color="black", ls="--", alpha=0.5)
    ax.set_xlabel("z")
    ax.set_ylabel("data − model")
    ax.set_title(f"Residuals — LCDM vs VariantJ (β={beta_med:+.3f})")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_chi2_beta(beta_samples, out_path):
    """Δχ² vs β from posterior — effective likelihood profile."""
    # Bin samples by β, compute density (not real chi2, but proxy)
    beta_bins = np.linspace(BETA_LO, BETA_HI, 101)
    kde = gaussian_kde(beta_samples)
    dens = kde(beta_bins)
    # Convert density to effective -2 ln p (up to const)
    log_dens = np.log(np.maximum(dens, 1e-50))
    chi2_eff = -2.0 * (log_dens - np.max(log_dens))  # normalized so min = 0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(beta_bins, chi2_eff, "-", color="purple", lw=2)
    ax.axhline(1.0, color="gray", ls=":", alpha=0.6, label="1σ (Δχ²=1)")
    ax.axhline(4.0, color="gray", ls="--", alpha=0.6, label="2σ (Δχ²=4)")
    ax.axhline(9.0, color="gray", ls="-.", alpha=0.6, label="3σ (Δχ²=9)")
    ax.axvline(0, color="black", ls=":", alpha=0.5, label="LCDM (β=0)")
    beta_med = float(np.median(beta_samples))
    ax.axvline(beta_med, color="red", ls="-", alpha=0.5, label=f"median β={beta_med:+.3f}")

    ax.set_xlabel("β (friction coupling)")
    ax.set_ylabel("Δχ²_eff (posterior-based)")
    ax.set_title("β profile from posterior samples")
    ax.set_ylim(0, 12)
    ax.legend(loc="upper center", ncol=2)
    ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def savage_dickey_bf(beta_samples):
    """Bayes factor estimate for β=0 via Savage-Dickey density ratio.

    BF_{model|null} = p(β=0 | data) / p(β=0 | prior)

    Larger than 1 → null (β=0) favored.
    Smaller than 1 → non-null favored.
    """
    kde = gaussian_kde(beta_samples)
    posterior_at_0 = float(kde(0.0)[0])
    return posterior_at_0 / PRIOR_DENSITY_BETA_AT_0


def verdict(beta_med, beta_std, beta_q16, beta_q84,
            bf_null, r_Om_beta):
    """Qualitative verdict."""
    lines = []
    # Posterior shape
    sign_asym = abs(beta_q84 + beta_q16) / max(abs(beta_q84 - beta_q16), 1e-9)
    if abs(beta_med) < 0.5 * beta_std:
        lines.append("β consistent with 0 within ~0.5σ")
    else:
        lines.append(f"β shifted from 0 at {abs(beta_med)/beta_std:.2f}σ")
    lines.append(f"68% CI: [{beta_q16:+.3f}, {beta_q84:+.3f}]")

    # Bayes factor
    if bf_null > 3:
        lines.append(f"BF(β=0) = {bf_null:.2f} — data favor LCDM (null preferred)")
    elif bf_null > 1:
        lines.append(f"BF(β=0) = {bf_null:.2f} — mild preference for LCDM")
    elif bf_null > 0.33:
        lines.append(f"BF(β=0) = {bf_null:.2f} — inconclusive")
    else:
        lines.append(f"BF(β=0) = {bf_null:.2f} — data disfavor β=0")

    # Degeneracy
    abs_r = abs(r_Om_beta)
    if abs_r > 0.7:
        lines.append(f"STRONG Ω_m–β degeneracy (r = {r_Om_beta:+.3f}) — joint-probe needed")
    elif abs_r > 0.4:
        lines.append(f"MODERATE Ω_m–β degeneracy (r = {r_Om_beta:+.3f})")
    else:
        lines.append(f"WEAK Ω_m–β degeneracy (r = {r_Om_beta:+.3f})")

    return lines


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    plots_dir = OUT_DIR / f"variant_j_plots_{ts}"
    plots_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" EFCVariantJ Full MCMC — Phase 2 Step 2 (quantification)")
    print("=" * 80)

    # ── Load data ───────────────────────────────────────────
    engine = EFCGrowth(cosmology=EFCVariantJ())
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    z_data = module.coordinates.copy()
    fs8_data = module.observed.copy()
    sigma_data = module.errors.copy()
    cov_status = "3x3 BOSS cov + diagonal" if module._cov_inv is not None else "diagonal"
    print(f"\nData: {module.n_data} fσ8 points — {cov_status}")

    # ── Pre-sanity: LL at anchor points ─────────────────────
    ll_0 = module.log_likelihood({"Omega_m": 0.3, "H0": H0_FIXED,
                                    "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0, "beta": 0.0})
    ll_p1 = module.log_likelihood({"Omega_m": 0.3, "H0": H0_FIXED,
                                     "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0, "beta": +0.5})
    ll_m1 = module.log_likelihood({"Omega_m": 0.3, "H0": H0_FIXED,
                                     "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0, "beta": -0.5})
    print(f"\nAnchor log-likelihoods at Ω_m=0.3, σ_8=0.81:")
    print(f"  β = 0.0   →  log L = {ll_0:+.4f}  (LCDM)")
    print(f"  β = +0.5  →  log L = {ll_p1:+.4f}")
    print(f"  β = -0.5  →  log L = {ll_m1:+.4f}")

    # ── Init walkers ────────────────────────────────────────
    rng = np.random.default_rng(SEED)
    p0 = np.column_stack([
        rng.uniform(0.25, 0.35, size=NWALKERS),
        rng.uniform(-0.2, 0.2, size=NWALKERS),
    ])
    log_prob_fn = make_log_prob(module)

    print(f"\nMCMC: nwalkers={NWALKERS}  nsteps={NSTEPS}  burnin={NBURN}  seed={SEED}")
    sampler = emcee.EnsembleSampler(NWALKERS, NDIM, log_prob_fn)

    t0 = time.time()
    print("  [burn-in]     ...", end=" ", flush=True)
    state = sampler.run_mcmc(p0, NBURN, progress=False)
    sampler.reset()
    print(f"done ({time.time() - t0:.1f}s)")

    t1 = time.time()
    print("  [production]  ...", end=" ", flush=True)
    sampler.run_mcmc(state, NSTEPS, progress=False)
    dt_prod = time.time() - t1
    dt_total = time.time() - t0
    print(f"done ({dt_prod:.1f}s)")

    # ── Diagnostics ─────────────────────────────────────────
    acc = float(np.mean(sampler.acceptance_fraction))
    try:
        tau = sampler.get_autocorr_time(tol=0, quiet=True)
    except Exception:
        tau = np.array([np.nan, np.nan])

    samples = sampler.get_chain(flat=True)
    log_probs = sampler.get_log_prob(flat=True)
    Omega_m_s = samples[:, 0]
    beta_s = samples[:, 1]

    # Posterior stats
    Om_med = float(np.median(Omega_m_s))
    Om_mean = float(np.mean(Omega_m_s))
    Om_std = float(np.std(Omega_m_s))
    Om_q16 = float(np.percentile(Omega_m_s, 16))
    Om_q84 = float(np.percentile(Omega_m_s, 84))

    beta_med = float(np.median(beta_s))
    beta_mean = float(np.mean(beta_s))
    beta_std = float(np.std(beta_s))
    beta_q16 = float(np.percentile(beta_s, 16))
    beta_q84 = float(np.percentile(beta_s, 84))
    beta_q2p5 = float(np.percentile(beta_s, 2.5))
    beta_q97p5 = float(np.percentile(beta_s, 97.5))

    # Degeneracy
    r_Om_beta = float(np.corrcoef(Omega_m_s, beta_s)[0, 1])

    # Bayes factor
    bf_null = float(savage_dickey_bf(beta_s))

    # ── Print summary ───────────────────────────────────────
    print(f"\nRuntime: {dt_total:.1f}s   Acceptance: {acc:.3f}   τ(Ω_m, β) = {tuple(tau)}")
    print(f"\nPosterior:")
    print(f"  Ω_m = {Om_med:.4f}  [{Om_q16:.4f}, {Om_q84:.4f}]  (std {Om_std:.4f})")
    print(f"  β   = {beta_med:+.4f}  [{beta_q16:+.4f}, {beta_q84:+.4f}]  (std {beta_std:.4f})")
    print(f"       95% CI β: [{beta_q2p5:+.4f}, {beta_q97p5:+.4f}]")
    print(f"\nDegeneracy:  r(Ω_m, β) = {r_Om_beta:+.4f}")
    print(f"Bayes factor BF(β=0) = {bf_null:.3f}")
    print(f"  [posterior density at β=0: {savage_dickey_bf(beta_s)*PRIOR_DENSITY_BETA_AT_0:.4f}]")
    print(f"  [prior density at β=0:     {PRIOR_DENSITY_BETA_AT_0:.4f}]")

    verdict_lines = verdict(beta_med, beta_std, beta_q16, beta_q84, bf_null, r_Om_beta)
    print(f"\n>>> VERDICT:")
    for l in verdict_lines:
        print(f"    {l}")

    # ── Generate plots ──────────────────────────────────────
    print(f"\nGenerating plots → {plots_dir}")
    plot_corner_2d(Omega_m_s, beta_s, plots_dir / "posterior_2d.png")
    plot_fs8_curves(module, z_data, fs8_data, sigma_data,
                    Om_med, beta_med, beta_q16, beta_q84,
                    plots_dir / "fs8_curves.png")
    plot_residuals(module, z_data, fs8_data, sigma_data,
                   Om_med, beta_med, plots_dir / "residuals.png")
    plot_chi2_beta(beta_s, plots_dir / "chi2_beta_profile.png")
    print(f"  4 plots saved.")

    # ── Save artifacts ──────────────────────────────────────
    summary = {
        "config": {
            "model": "EFCVariantJ",
            "coupling": "friction_channel",
            "phase": "phase_2_step_2_mcmc_quantification",
            "nwalkers": NWALKERS,
            "nsteps": NSTEPS,
            "nburn": NBURN,
            "seed": SEED,
            "sigma8_fixed": SIGMA8_FIXED,
            "H0_fixed": H0_FIXED,
            "priors": {
                "Omega_m": [OMEGA_M_LO, OMEGA_M_HI],
                "beta": [BETA_LO, BETA_HI],
            },
            "gate": {"a_t": 0.5, "delta_a": 0.1, "status": "frozen"},
        },
        "data": {
            "n_points": int(module.n_data),
            "z_range": [float(z_data.min()), float(z_data.max())],
            "covariance": cov_status,
        },
        "runtime_seconds": round(dt_total, 2),
        "diagnostics": {
            "acceptance_fraction": round(acc, 3),
            "autocorr_time": [float(t) if np.isfinite(t) else None for t in tau],
            "n_effective": [int(NWALKERS * NSTEPS / t) if np.isfinite(t) and t > 0 else None
                            for t in tau],
        },
        "anchors": {
            "ll_beta_0.0": round(ll_0, 4),
            "ll_beta_+0.5": round(ll_p1, 4),
            "ll_beta_-0.5": round(ll_m1, 4),
        },
        "Omega_m_posterior": {
            "mean": round(Om_mean, 5),
            "median": round(Om_med, 5),
            "std": round(Om_std, 5),
            "q16": round(Om_q16, 5),
            "q84": round(Om_q84, 5),
        },
        "beta_posterior": {
            "mean": round(beta_mean, 5),
            "median": round(beta_med, 5),
            "std": round(beta_std, 5),
            "q16": round(beta_q16, 5),
            "q84": round(beta_q84, 5),
            "q2.5": round(beta_q2p5, 5),
            "q97.5": round(beta_q97p5, 5),
            "sigma_from_zero": round(abs(beta_med) / beta_std, 3) if beta_std > 0 else None,
        },
        "degeneracy": {
            "pearson_r_Omega_m_beta": round(r_Om_beta, 4),
            "strength": ("strong" if abs(r_Om_beta) > 0.7 else
                         "moderate" if abs(r_Om_beta) > 0.4 else "weak"),
        },
        "bayes_factor": {
            "BF_null": round(bf_null, 3),
            "method": "savage_dickey_density_ratio",
            "prior_density_at_0": PRIOR_DENSITY_BETA_AT_0,
            "posterior_density_at_0": round(bf_null * PRIOR_DENSITY_BETA_AT_0, 5),
            "interpretation": (
                "LCDM_favored" if bf_null > 3 else
                "LCDM_mild" if bf_null > 1 else
                "inconclusive" if bf_null > 0.33 else
                "beta_nonzero_favored"
            ),
        },
        "verdict_lines": verdict_lines,
    }

    chain_path = OUT_DIR / f"variant_j_chain_{ts}.npz"
    summary_path = OUT_DIR / f"variant_j_summary_{ts}.json"
    np.savez_compressed(
        chain_path,
        samples=samples,
        log_prob=log_probs,
        acceptance_fraction=sampler.acceptance_fraction,
        Omega_m=Omega_m_s,
        beta=beta_s,
    )
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nOutputs:")
    print(f"  chain   : {chain_path}")
    print(f"  summary : {summary_path}")
    print(f"  plots   : {plots_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
