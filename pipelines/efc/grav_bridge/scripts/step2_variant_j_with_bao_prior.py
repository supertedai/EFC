#!/usr/bin/env python3
"""
Step 2: VariantJ + fs8 with informative Ω_m prior from Step 1 BAO+Hz.

Morten: "Bruk Ω_m prior (fra BAO). Kjør fs8 + β. Dette bryter degenerasjonen eksplisitt."

Procedure:
    1. Auto-load latest step1 summary from outputs/grav_bridge/
    2. Extract Ω_m mean, std from BAO+Hz posterior
    3. Run MCMC on (Ω_m, β) with:
         Ω_m ~ N(μ_BAO, σ_BAO)    [informative Gaussian prior]
         β   ~ U(-2, 2)            [flat]
    4. Compare β posterior and r(Ω_m, β) against unrestricted run

Scenarios (Morten's lock):
    A) β → 0 when Ω_m locked       → friction was just Ω_m projection
    B) β ≠ 0 with locked Ω_m       → real timing signal
    C) BAO and fs8 in conflict     → deeper model issue

Output:
    outputs/grav_bridge/step2_chain_<timestamp>.npz
    outputs/grav_bridge/step2_summary_<timestamp>.json
    outputs/grav_bridge/step2_plots_<timestamp>/{posterior_2d,fs8_curves,residuals,chi2_beta}.png
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
H0_FIXED = 70.0  # fσ8 is ~H0-independent at our precision; Step 1 gives H0=68.96
DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

# ─── MCMC config ────────────────────────────────────────────────
NWALKERS = 32
NSTEPS = 1500
NBURN = 300
NDIM = 2
SEED = 42

# ─── Priors ─────────────────────────────────────────────────────
# Omega_m: informative Gaussian from Step 1 (auto-loaded below)
# beta:    same flat U(-2, 2) as before — direct comparison
BETA_LO, BETA_HI = -2.0, 2.0
PRIOR_DENSITY_BETA_AT_0 = 1.0 / (BETA_HI - BETA_LO)
# Safety bounds on Omega_m to avoid numerical issues far from prior
OMEGA_M_HARD_LO, OMEGA_M_HARD_HI = 0.15, 0.55


def load_step1_prior():
    """Load Ω_m prior parameters from latest step1_summary JSON."""
    candidates = sorted(OUT_DIR.glob("step1_summary_*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(
            "No step1_summary_*.json found. Run step1_bao_hz_lcdm_mcmc.py first."
        )
    latest = candidates[0]
    with open(latest) as f:
        s1 = json.load(f)
    prior_block = s1.get("use_as_prior_in_step_2", {}).get("Omega_m_gaussian_prior", {})
    mu = float(prior_block["mean"])
    sigma = float(prior_block["std"])
    return mu, sigma, latest.name


def log_prior(theta, Om_mu, Om_sigma):
    Om, beta = float(theta[0]), float(theta[1])
    if not (OMEGA_M_HARD_LO < Om < OMEGA_M_HARD_HI):
        return -np.inf
    if not (BETA_LO < beta < BETA_HI):
        return -np.inf
    # Gaussian on Ω_m
    lp_Om = -0.5 * ((Om - Om_mu) / Om_sigma) ** 2
    return lp_Om


def make_log_prob(module, Om_mu, Om_sigma):
    def log_prob(theta):
        lp = log_prior(theta, Om_mu, Om_sigma)
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


def compute_fs8_model(module, z_arr, Om, beta):
    params = {
        "Omega_m": float(Om), "H0": H0_FIXED,
        "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0, "beta": float(beta),
    }
    return module.engine.compute(params, z_arr)


def plot_corner_2d(Om_s, beta_s, Om_mu, Om_sigma, out_path):
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3],
                           hspace=0.05, wspace=0.05)
    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)

    ax_main.hist2d(Om_s, beta_s, bins=60, cmap="viridis")
    ax_main.axhline(0, color="white", ls="--", lw=1, alpha=0.6)
    ax_main.axvline(Om_mu, color="white", ls=":", lw=1, alpha=0.6, label=f"BAO Ω_m={Om_mu:.4f}")
    ax_main.set_xlabel("Ω_m")
    ax_main.set_ylabel("β (friction coupling)")
    ax_main.grid(alpha=0.2)
    ax_main.legend(loc="upper right", fontsize=8)

    ax_top.hist(Om_s, bins=60, color="steelblue", edgecolor="white", alpha=0.8, density=True)
    # Overlay BAO prior
    Om_grid = np.linspace(Om_s.min(), Om_s.max(), 200)
    prior_curve = np.exp(-0.5 * ((Om_grid - Om_mu) / Om_sigma) ** 2) / (Om_sigma * np.sqrt(2*np.pi))
    ax_top.plot(Om_grid, prior_curve, "r--", lw=1.5, alpha=0.7, label="BAO prior")
    ax_top.set_ylabel("PDF")
    ax_top.tick_params(axis="x", labelbottom=False)
    ax_top.legend(fontsize=8)

    ax_right.hist(beta_s, bins=60, orientation="horizontal",
                  color="coral", edgecolor="white", alpha=0.8)
    ax_right.axhline(0, color="black", ls="--", alpha=0.5, label="β=0 (LCDM)")
    ax_right.set_xlabel("N")
    ax_right.tick_params(axis="y", labelleft=False)
    ax_right.legend(fontsize=8, loc="upper right")

    r = float(np.corrcoef(Om_s, beta_s)[0, 1])
    fig.suptitle(f"VariantJ + BAO prior — Pearson r(Ω_m, β) = {r:+.3f}", y=0.98)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_fs8_curves(module, z_data, fs8_data, sigma_data,
                    Om_med, beta_med, beta_q16, beta_q84, out_path):
    z_model = np.linspace(0.01, 1.2, 120)
    fs8_lcdm = compute_fs8_model(module, z_model, Om_med, 0.0)
    fs8_med = compute_fs8_model(module, z_model, Om_med, beta_med)
    fs8_lo = compute_fs8_model(module, z_model, Om_med, beta_q16)
    fs8_hi = compute_fs8_model(module, z_model, Om_med, beta_q84)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(z_data, fs8_data, yerr=sigma_data, fmt="o", color="black",
                label="fσ8 data", zorder=5, markersize=7, capsize=3)
    ax.plot(z_model, fs8_lcdm, "-", color="#1f77b4", lw=2, label="LCDM (β=0, BAO Ω_m)")
    ax.plot(z_model, fs8_med, "--", color="#d62728", lw=2,
            label=f"VariantJ + BAO prior (β_med={beta_med:+.3f})")
    ax.fill_between(z_model, fs8_lo, fs8_hi, color="#d62728", alpha=0.2,
                    label=f"β ∈ [{beta_q16:+.3f}, {beta_q84:+.3f}] (68% CI)")
    ax.set_xlabel("z"); ax.set_ylabel("fσ8(z)")
    ax.set_title("Step 2 — fσ8 at BAO-anchored Ω_m")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_residuals(module, z_data, fs8_data, sigma_data, Om_med, beta_med, out_path):
    fs8_lcdm = compute_fs8_model(module, z_data, Om_med, 0.0)
    fs8_j = compute_fs8_model(module, z_data, Om_med, beta_med)
    res_lcdm = fs8_data - fs8_lcdm
    res_j = fs8_data - fs8_j
    chi2_lcdm = float(np.sum((res_lcdm / sigma_data) ** 2))
    chi2_j = float(np.sum((res_j / sigma_data) ** 2))

    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.008
    ax.errorbar(z_data - w, res_lcdm, yerr=sigma_data, fmt="o", color="#1f77b4",
                label=f"LCDM residuals (Σr²/σ² = {chi2_lcdm:.2f})", capsize=3, markersize=7)
    ax.errorbar(z_data + w, res_j, yerr=sigma_data, fmt="s", color="#d62728",
                label=f"VariantJ residuals (Σr²/σ² = {chi2_j:.2f})", capsize=3, markersize=7)
    ax.axhline(0, color="black", ls="--", alpha=0.5)
    ax.set_xlabel("z"); ax.set_ylabel("data − model")
    ax.set_title(f"Step 2 residuals at BAO-anchored Ω_m={Om_med:.4f}, β={beta_med:+.3f}")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_chi2_beta(beta_s, out_path):
    beta_bins = np.linspace(BETA_LO, BETA_HI, 101)
    kde = gaussian_kde(beta_s)
    dens = kde(beta_bins)
    log_dens = np.log(np.maximum(dens, 1e-50))
    chi2_eff = -2.0 * (log_dens - np.max(log_dens))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(beta_bins, chi2_eff, "-", color="purple", lw=2)
    for thr, ls, lab in [(1, ":", "1σ"), (4, "--", "2σ"), (9, "-.", "3σ")]:
        ax.axhline(thr, color="gray", ls=ls, alpha=0.6, label=lab)
    ax.axvline(0, color="black", ls=":", alpha=0.5, label="LCDM")
    bm = float(np.median(beta_s))
    ax.axvline(bm, color="red", ls="-", alpha=0.5, label=f"median β={bm:+.3f}")
    ax.set_xlabel("β"); ax.set_ylabel("Δχ²_eff")
    ax.set_title("Step 2 — β posterior profile (BAO-anchored)")
    ax.set_ylim(0, 12); ax.legend(loc="upper center", ncol=2); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def savage_dickey_bf(beta_s):
    kde = gaussian_kde(beta_s)
    return float(kde(0.0)[0]) / PRIOR_DENSITY_BETA_AT_0


def scenario_verdict(beta_med, beta_std, beta_q16, beta_q84, r_Om_beta,
                     beta_unlocked_med, beta_unlocked_std,
                     beta_unlocked_q16, beta_unlocked_q84):
    """Determine Scenario A/B/C vs unrestricted run."""
    sigma_from_0 = abs(beta_med) / beta_std if beta_std > 0 else float("inf")
    # Did β collapse? Compare width to unrestricted run.
    width_ratio = (beta_q84 - beta_q16) / max(beta_unlocked_q84 - beta_unlocked_q16, 1e-9)
    # Did β shift significantly?
    shift_sigma = abs(beta_med - beta_unlocked_med) / max(beta_unlocked_std, 1e-9)

    lines = []
    lines.append(f"β_locked    = {beta_med:+.4f} ± {beta_std:.4f} (68% CI [{beta_q16:+.4f}, {beta_q84:+.4f}])")
    lines.append(f"β_unlocked  = {beta_unlocked_med:+.4f} ± {beta_unlocked_std:.4f} (68% CI [{beta_unlocked_q16:+.4f}, {beta_unlocked_q84:+.4f}])")
    lines.append(f"CI width ratio (locked/unlocked) = {width_ratio:.3f}")
    lines.append(f"β shift from unlocked: {shift_sigma:.2f}σ")
    lines.append(f"β distance from 0 (locked): {sigma_from_0:.2f}σ")

    # Scenario diagnosis
    if sigma_from_0 < 1.0 and width_ratio < 0.7:
        scenario = "A — Friction was Ω_m projection: β collapsed and CI tightened"
    elif sigma_from_0 >= 2.0:
        scenario = "B — Real timing signal: β significant even with Ω_m locked"
    elif sigma_from_0 >= 1.0:
        scenario = "B (weak) — Hint of timing signal, not conclusive"
    elif width_ratio > 1.2:
        scenario = "C — BAO and fσ8 in conflict: constraint does not tighten β"
    else:
        scenario = "A (soft) — β compatible with 0, CI not dramatically narrower"
    lines.append(f"SCENARIO: {scenario}")
    lines.append(f"r(Ω_m, β) with BAO prior = {r_Om_beta:+.4f}")
    return lines, scenario


def load_unrestricted_beta_posterior():
    """Load most recent variant_j_summary (unrestricted MCMC) for comparison."""
    candidates = sorted(OUT_DIR.glob("variant_j_summary_*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    with open(candidates[0]) as f:
        data = json.load(f)
    b = data["beta_posterior"]
    return b["median"], b["std"], b["q16"], b["q84"], candidates[0].name


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    plots_dir = OUT_DIR / f"step2_plots_{ts}"
    plots_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" Step 2: VariantJ + fs8 with BAO-anchored Ω_m prior")
    print("=" * 80)

    # Load Step 1 prior
    Om_mu, Om_sigma, step1_file = load_step1_prior()
    print(f"\nLoaded BAO+Hz prior from {step1_file}:")
    print(f"  Ω_m prior:  N({Om_mu:.5f}, {Om_sigma:.5f})")

    # Load unrestricted VariantJ run for comparison
    unlocked = load_unrestricted_beta_posterior()
    if unlocked:
        bu_med, bu_std, bu_q16, bu_q84, unl_file = unlocked
        print(f"\nComparing vs unrestricted VariantJ run in {unl_file}:")
        print(f"  β_unlocked: {bu_med:+.4f} ± {bu_std:.4f}  [{bu_q16:+.4f}, {bu_q84:+.4f}]")
    else:
        bu_med = bu_std = bu_q16 = bu_q84 = None
        print("\n(No unrestricted VariantJ run found — scenario diagnosis will be absolute only)")

    # ── Setup ───────────────────────────────────────────────
    engine = EFCGrowth(cosmology=EFCVariantJ())
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    z_data = module.coordinates.copy()
    fs8_data = module.observed.copy()
    sigma_data = module.errors.copy()
    cov_status = "3x3 BOSS cov + diagonal" if module._cov_inv is not None else "diagonal"
    print(f"\nfσ8 data: {module.n_data} points — {cov_status}")

    # ── Init walkers ────────────────────────────────────────
    rng = np.random.default_rng(SEED)
    p0 = np.column_stack([
        rng.normal(Om_mu, Om_sigma, size=NWALKERS),  # init from prior
        rng.uniform(-0.2, 0.2, size=NWALKERS),
    ])
    log_prob_fn = make_log_prob(module, Om_mu, Om_sigma)

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
    dt_prod = time.time() - t1
    dt = time.time() - t0
    print(f"done ({dt_prod:.1f}s)")

    acc = float(np.mean(sampler.acceptance_fraction))
    try:
        tau = sampler.get_autocorr_time(tol=0, quiet=True)
    except Exception:
        tau = np.array([np.nan, np.nan])

    samples = sampler.get_chain(flat=True)
    log_probs = sampler.get_log_prob(flat=True)
    Om_s = samples[:, 0]
    beta_s = samples[:, 1]

    Om_med = float(np.median(Om_s))
    Om_std = float(np.std(Om_s))
    Om_q16 = float(np.percentile(Om_s, 16))
    Om_q84 = float(np.percentile(Om_s, 84))

    beta_med = float(np.median(beta_s))
    beta_mean = float(np.mean(beta_s))
    beta_std = float(np.std(beta_s))
    beta_q16 = float(np.percentile(beta_s, 16))
    beta_q84 = float(np.percentile(beta_s, 84))
    beta_q2p5 = float(np.percentile(beta_s, 2.5))
    beta_q97p5 = float(np.percentile(beta_s, 97.5))

    r_Om_beta = float(np.corrcoef(Om_s, beta_s)[0, 1])
    bf_null = savage_dickey_bf(beta_s)

    print(f"\nRuntime: {dt:.1f}s  Acceptance: {acc:.3f}  τ(Ω_m, β) = {tuple(tau)}")
    print(f"\nPosterior (with BAO+Hz Ω_m prior):")
    print(f"  Ω_m = {Om_med:.5f}  [{Om_q16:.5f}, {Om_q84:.5f}]  (std {Om_std:.5f})")
    print(f"  β   = {beta_med:+.4f}  [{beta_q16:+.4f}, {beta_q84:+.4f}]  (std {beta_std:.4f})")
    print(f"       95% CI β: [{beta_q2p5:+.4f}, {beta_q97p5:+.4f}]")
    print(f"\nDegeneracy: r(Ω_m, β) = {r_Om_beta:+.4f}")
    print(f"Bayes factor BF(β=0) = {bf_null:.3f}")

    # Scenario diagnosis
    if bu_med is not None:
        verdict_lines, scenario = scenario_verdict(
            beta_med, beta_std, beta_q16, beta_q84, r_Om_beta,
            bu_med, bu_std, bu_q16, bu_q84,
        )
        print(f"\n>>> SCENARIO DIAGNOSIS:")
        for l in verdict_lines:
            print(f"    {l}")
    else:
        scenario = "N/A (no unrestricted run to compare)"
        verdict_lines = [f"β = {beta_med:+.4f} ± {beta_std:.4f}"]

    # ── Generate plots ──────────────────────────────────────
    print(f"\nGenerating plots → {plots_dir}")
    plot_corner_2d(Om_s, beta_s, Om_mu, Om_sigma, plots_dir / "posterior_2d.png")
    plot_fs8_curves(module, z_data, fs8_data, sigma_data,
                    Om_med, beta_med, beta_q16, beta_q84,
                    plots_dir / "fs8_curves.png")
    plot_residuals(module, z_data, fs8_data, sigma_data,
                   Om_med, beta_med, plots_dir / "residuals.png")
    plot_chi2_beta(beta_s, plots_dir / "chi2_beta_profile.png")
    print("  4 plots saved.")

    # ── Save ────────────────────────────────────────────────
    summary = {
        "config": {
            "step": "2_variant_j_with_bao_prior",
            "model": "EFCVariantJ",
            "coupling": "friction_channel",
            "nwalkers": NWALKERS,
            "nsteps": NSTEPS,
            "nburn": NBURN,
            "seed": SEED,
            "H0_fixed": H0_FIXED,
            "sigma8_fixed": SIGMA8_FIXED,
            "gate": {"a_t": 0.5, "delta_a": 0.1},
        },
        "step1_input": {
            "source_file": step1_file,
            "Omega_m_prior_mean": Om_mu,
            "Omega_m_prior_std": Om_sigma,
        },
        "runtime_seconds": round(dt, 2),
        "diagnostics": {
            "acceptance_fraction": round(acc, 3),
            "autocorr_time": [float(t) if np.isfinite(t) else None for t in tau],
        },
        "Omega_m_posterior": {
            "mean": round(float(np.mean(Om_s)), 6),
            "median": round(Om_med, 6),
            "std": round(Om_std, 6),
            "q16": round(Om_q16, 6),
            "q84": round(Om_q84, 6),
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
        },
        "bayes_factor": {
            "BF_null": round(bf_null, 3),
            "method": "savage_dickey_density_ratio",
        },
        "comparison_to_unrestricted": {
            "beta_unlocked_median": bu_med,
            "beta_unlocked_std": bu_std,
            "beta_unlocked_q16": bu_q16,
            "beta_unlocked_q84": bu_q84,
        } if bu_med is not None else None,
        "scenario": scenario,
        "verdict_lines": verdict_lines,
    }

    chain_path = OUT_DIR / f"step2_chain_{ts}.npz"
    summary_path = OUT_DIR / f"step2_summary_{ts}.json"
    np.savez_compressed(
        chain_path,
        samples=samples,
        log_prob=log_probs,
        acceptance_fraction=sampler.acceptance_fraction,
        Omega_m=Om_s,
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
