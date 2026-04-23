#!/usr/bin/env python3
"""
Step 3: VariantK (non-local memory) + fs8 with BAO-anchored Ω_m prior.

Phase 3 test — memory coupling as minimal break from Markov growth.

Procedure:
    1. Auto-load Step 1 BAO+Hz Ω_m prior
    2. Sample (Ω_m, β) with:
         Ω_m ~ N(μ_BAO, σ_BAO)     — same informative prior as Step 2
         β   ~ U(-4, 4)             — wider range than Step 2, since memory is
                                      ~1/2 as "strong" at a=1 (G(1)≈0.5 vs gate(1)≈1)
    3. Diagnose: does β survive BAO lock (unlike VariantJ friction)?

Key question (Morten's framing):
    "If β collapses to 0 under BAO-lock (like VariantJ): non-local
     memory is ALSO just Ω_m degeneracy → problem is deeper than locality.
     If β survives: first candidate for correct coupling structure."

Output:
    outputs/grav_bridge/step3_chain_<timestamp>.npz
    outputs/grav_bridge/step3_summary_<timestamp>.json
    outputs/grav_bridge/step3_plots_<timestamp>/{posterior_2d,fs8_curves,residuals,chi2_beta}.png
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

from efc_grav_bridge import EFCVariantK  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402
from efc_grav_bridge import GrowthModule  # noqa: E402


SIGMA8_FIXED = 0.81
H0_FIXED = 70.0
DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

NWALKERS = 32
NSTEPS = 1500
NBURN = 300
NDIM = 2
SEED = 42

# β-prior wider for VariantK (memory response is ~½ as strong at a=1)
BETA_LO, BETA_HI = -4.0, 4.0
PRIOR_DENSITY_BETA_AT_0 = 1.0 / (BETA_HI - BETA_LO)  # 0.125 for U(-4, 4)

OMEGA_M_HARD_LO, OMEGA_M_HARD_HI = 0.15, 0.55


def load_step1_prior():
    candidates = sorted(OUT_DIR.glob("step1_summary_*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError("Run step1_bao_hz_lcdm_mcmc.py first.")
    with open(candidates[0]) as f:
        s1 = json.load(f)
    p = s1["use_as_prior_in_step_2"]["Omega_m_gaussian_prior"]
    return float(p["mean"]), float(p["std"]), candidates[0].name


def load_step2_beta_posterior():
    """Load Step 2 (VariantJ + BAO prior) result for comparison."""
    candidates = sorted(OUT_DIR.glob("step2_summary_*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    with open(candidates[0]) as f:
        data = json.load(f)
    b = data["beta_posterior"]
    return {
        "file": candidates[0].name,
        "median": b["median"],
        "std": b["std"],
        "q16": b["q16"],
        "q84": b["q84"],
        "r_Om_beta": data["degeneracy"]["pearson_r_Omega_m_beta"],
        "BF_null": data["bayes_factor"]["BF_null"],
    }


def log_prior(theta, Om_mu, Om_sigma):
    Om, beta = float(theta[0]), float(theta[1])
    if not (OMEGA_M_HARD_LO < Om < OMEGA_M_HARD_HI):
        return -np.inf
    if not (BETA_LO < beta < BETA_HI):
        return -np.inf
    return -0.5 * ((Om - Om_mu) / Om_sigma) ** 2


def make_log_prob(module, Om_mu, Om_sigma):
    def log_prob(theta):
        lp = log_prior(theta, Om_mu, Om_sigma)
        if not np.isfinite(lp):
            return -np.inf
        params = {
            "Omega_m": float(theta[0]), "H0": H0_FIXED,
            "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0,
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
    return module.engine.compute({
        "Omega_m": float(Om), "H0": H0_FIXED,
        "sigma8": SIGMA8_FIXED, "alpha_cosmo": 0.0,
        "beta": float(beta),
    }, z_arr)


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
    ax_main.set_xlabel("Ω_m"); ax_main.set_ylabel("β (memory coupling)")
    ax_main.grid(alpha=0.2); ax_main.legend(loc="upper right", fontsize=8)

    ax_top.hist(Om_s, bins=60, color="steelblue", edgecolor="white", alpha=0.8, density=True)
    Om_grid = np.linspace(Om_s.min(), Om_s.max(), 200)
    prior_curve = np.exp(-0.5 * ((Om_grid - Om_mu) / Om_sigma) ** 2) / (Om_sigma * np.sqrt(2*np.pi))
    ax_top.plot(Om_grid, prior_curve, "r--", lw=1.5, alpha=0.7, label="BAO prior")
    ax_top.set_ylabel("PDF"); ax_top.tick_params(axis="x", labelbottom=False)
    ax_top.legend(fontsize=8)

    ax_right.hist(beta_s, bins=60, orientation="horizontal",
                  color="mediumorchid", edgecolor="white", alpha=0.8)
    ax_right.axhline(0, color="black", ls="--", alpha=0.5, label="β=0 (LCDM)")
    ax_right.set_xlabel("N"); ax_right.tick_params(axis="y", labelleft=False)
    ax_right.legend(fontsize=8, loc="upper right")

    r = float(np.corrcoef(Om_s, beta_s)[0, 1])
    fig.suptitle(f"VariantK (memory) + BAO prior — Pearson r(Ω_m, β) = {r:+.3f}", y=0.98)
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
    ax.plot(z_model, fs8_lcdm, "-", color="#1f77b4", lw=2, label="LCDM (β=0)")
    ax.plot(z_model, fs8_med, "--", color="#9467bd", lw=2,
            label=f"VariantK (β_med={beta_med:+.3f})")
    ax.fill_between(z_model, fs8_lo, fs8_hi, color="#9467bd", alpha=0.2,
                    label=f"β ∈ [{beta_q16:+.3f}, {beta_q84:+.3f}] (68% CI)")
    ax.set_xlabel("z"); ax.set_ylabel("fσ8(z)")
    ax.set_title("Step 3 — VariantK (memory) at BAO-anchored Ω_m")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_residuals(module, z_data, fs8_data, sigma_data, Om_med, beta_med, out_path):
    fs8_lcdm = compute_fs8_model(module, z_data, Om_med, 0.0)
    fs8_k = compute_fs8_model(module, z_data, Om_med, beta_med)
    res_lcdm = fs8_data - fs8_lcdm
    res_k = fs8_data - fs8_k
    chi2_lcdm = float(np.sum((res_lcdm / sigma_data) ** 2))
    chi2_k = float(np.sum((res_k / sigma_data) ** 2))

    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.008
    ax.errorbar(z_data - w, res_lcdm, yerr=sigma_data, fmt="o", color="#1f77b4",
                label=f"LCDM (Σr²/σ² = {chi2_lcdm:.2f})", capsize=3, markersize=7)
    ax.errorbar(z_data + w, res_k, yerr=sigma_data, fmt="s", color="#9467bd",
                label=f"VariantK (Σr²/σ² = {chi2_k:.2f})", capsize=3, markersize=7)
    ax.axhline(0, color="black", ls="--", alpha=0.5)
    ax.set_xlabel("z"); ax.set_ylabel("data − model")
    ax.set_title(f"Step 3 residuals — BAO-anchored, β={beta_med:+.3f}")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_chi2_beta(beta_s, out_path):
    beta_bins = np.linspace(BETA_LO, BETA_HI, 161)
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
    ax.set_xlabel("β (memory coupling)"); ax.set_ylabel("Δχ²_eff")
    ax.set_title("Step 3 — β posterior profile (memory + BAO)")
    ax.set_ylim(0, 12); ax.legend(loc="upper center", ncol=2); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def savage_dickey_bf(beta_s):
    kde = gaussian_kde(beta_s)
    return float(kde(0.0)[0]) / PRIOR_DENSITY_BETA_AT_0


def memory_verdict(beta_med, beta_std, beta_q16, beta_q84, r_Om_beta, bf_null,
                   step2):
    """Diagnose if memory survives or collapses like VariantJ."""
    sigma_from_0 = abs(beta_med) / beta_std if beta_std > 0 else float("inf")
    lines = [
        f"VariantK β = {beta_med:+.4f} ± {beta_std:.4f}  (68% CI [{beta_q16:+.4f}, {beta_q84:+.4f}])",
        f"VariantK β from 0: {sigma_from_0:.2f}σ",
        f"VariantK r(Ω_m, β) = {r_Om_beta:+.4f}",
        f"VariantK BF(β=0)   = {bf_null:.3f}",
    ]
    if step2:
        lines.append(f"  vs Step 2 VariantJ: β={step2['median']:+.4f} ± {step2['std']:.4f}, "
                     f"r={step2['r_Om_beta']:+.3f}, BF={step2['BF_null']:.3f}")

    # Diagnosis
    if sigma_from_0 >= 2.0:
        verdict = "MEMORY_SURVIVES — β detected at >2σ even with BAO lock. First candidate coupling."
    elif sigma_from_0 >= 1.0:
        verdict = "MEMORY_HINT — β shifted from 0 at ~1σ, worth joint-fit follow-up."
    elif step2 and abs(beta_med) < 0.5 * abs(step2["median"]) and beta_std < 1.2 * step2["std"]:
        verdict = "MEMORY_COLLAPSES — β like VariantJ: non-locality did NOT save the coupling. Lesson: problem is not locality alone."
    else:
        verdict = "MEMORY_CONSISTENT_WITH_ZERO — β indistinguishable from 0."

    lines.append(f"VERDICT: {verdict}")
    return lines, verdict


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    plots_dir = OUT_DIR / f"step3_plots_{ts}"
    plots_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" Step 3: VariantK (non-local memory) + fs8 with BAO Ω_m prior")
    print("=" * 80)

    Om_mu, Om_sigma, step1_file = load_step1_prior()
    print(f"\nLoaded BAO prior from {step1_file}:")
    print(f"  Ω_m prior: N({Om_mu:.5f}, {Om_sigma:.5f})")

    step2 = load_step2_beta_posterior()
    if step2:
        print(f"\nStep 2 reference (VariantJ friction): {step2['file']}")
        print(f"  β = {step2['median']:+.4f} ± {step2['std']:.4f}  BF={step2['BF_null']:.3f}")

    engine = EFCGrowth(cosmology=EFCVariantK())
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    z_data = module.coordinates.copy()
    fs8_data = module.observed.copy()
    sigma_data = module.errors.copy()
    cov_status = "3x3 BOSS cov + diagonal" if module._cov_inv is not None else "diagonal"
    print(f"\nfσ8 data: {module.n_data} points — {cov_status}")

    rng = np.random.default_rng(SEED)
    p0 = np.column_stack([
        rng.normal(Om_mu, Om_sigma, size=NWALKERS),
        rng.uniform(-0.4, 0.4, size=NWALKERS),
    ])
    log_prob_fn = make_log_prob(module, Om_mu, Om_sigma)

    print(f"\nMCMC: nwalkers={NWALKERS} nsteps={NSTEPS} burnin={NBURN} seed={SEED}")
    print(f"Priors: Ω_m ~ N({Om_mu:.5f}, {Om_sigma:.5f}),  β ~ U({BETA_LO}, {BETA_HI})")

    sampler = emcee.EnsembleSampler(NWALKERS, NDIM, log_prob_fn)

    t0 = time.time()
    print("  [burn-in]    ...", end=" ", flush=True)
    state = sampler.run_mcmc(p0, NBURN, progress=False)
    sampler.reset()
    print(f"done ({time.time()-t0:.1f}s)")

    t1 = time.time()
    print("  [production] ...", end=" ", flush=True)
    sampler.run_mcmc(state, NSTEPS, progress=False)
    dt = time.time() - t0
    print(f"done ({time.time()-t1:.1f}s)")

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

    print(f"\nRuntime: {dt:.1f}s  Acceptance: {acc:.3f}  τ = {tuple(tau)}")
    print(f"\nPosterior:")
    print(f"  Ω_m = {Om_med:.5f}  [{Om_q16:.5f}, {Om_q84:.5f}]  (std {Om_std:.5f})")
    print(f"  β   = {beta_med:+.4f}  [{beta_q16:+.4f}, {beta_q84:+.4f}]  (std {beta_std:.4f})")
    print(f"      95% CI β: [{beta_q2p5:+.4f}, {beta_q97p5:+.4f}]")
    print(f"\nDegeneracy: r(Ω_m, β) = {r_Om_beta:+.4f}")
    print(f"Bayes factor BF(β=0) = {bf_null:.3f}")

    verdict_lines, verdict = memory_verdict(beta_med, beta_std, beta_q16, beta_q84,
                                             r_Om_beta, bf_null, step2)
    print("\n>>> MEMORY DIAGNOSIS:")
    for l in verdict_lines:
        print(f"    {l}")

    print(f"\nGenerating plots → {plots_dir}")
    plot_corner_2d(Om_s, beta_s, Om_mu, Om_sigma, plots_dir / "posterior_2d.png")
    plot_fs8_curves(module, z_data, fs8_data, sigma_data,
                    Om_med, beta_med, beta_q16, beta_q84,
                    plots_dir / "fs8_curves.png")
    plot_residuals(module, z_data, fs8_data, sigma_data, Om_med, beta_med,
                   plots_dir / "residuals.png")
    plot_chi2_beta(beta_s, plots_dir / "chi2_beta_profile.png")
    print("  4 plots saved.")

    summary = {
        "config": {
            "step": "3_variant_k_memory_with_bao_prior",
            "model": "EFCVariantK",
            "coupling": "friction_channel_non_local_memory",
            "nwalkers": NWALKERS, "nsteps": NSTEPS, "nburn": NBURN, "seed": SEED,
            "H0_fixed": H0_FIXED, "sigma8_fixed": SIGMA8_FIXED,
            "gate": {"a_t": 0.5, "delta_a": 0.1},
        },
        "step1_input": {
            "source_file": step1_file,
            "Omega_m_prior_mean": Om_mu,
            "Omega_m_prior_std": Om_sigma,
        },
        "step2_reference": step2,
        "runtime_seconds": round(dt, 2),
        "diagnostics": {
            "acceptance_fraction": round(acc, 3),
            "autocorr_time": [float(t) if np.isfinite(t) else None for t in tau],
        },
        "Omega_m_posterior": {
            "mean": round(float(np.mean(Om_s)), 6),
            "median": round(Om_med, 6),
            "std": round(Om_std, 6),
            "q16": round(Om_q16, 6), "q84": round(Om_q84, 6),
        },
        "beta_posterior": {
            "mean": round(beta_mean, 5), "median": round(beta_med, 5),
            "std": round(beta_std, 5),
            "q16": round(beta_q16, 5), "q84": round(beta_q84, 5),
            "q2.5": round(beta_q2p5, 5), "q97.5": round(beta_q97p5, 5),
            "sigma_from_zero": round(abs(beta_med) / beta_std, 3) if beta_std > 0 else None,
        },
        "degeneracy": {"pearson_r_Omega_m_beta": round(r_Om_beta, 4)},
        "bayes_factor": {"BF_null": round(bf_null, 3),
                         "method": "savage_dickey_density_ratio"},
        "verdict": verdict,
        "verdict_lines": verdict_lines,
    }

    chain_path = OUT_DIR / f"step3_chain_{ts}.npz"
    summary_path = OUT_DIR / f"step3_summary_{ts}.json"
    np.savez_compressed(chain_path, samples=samples, log_prob=log_probs,
                        acceptance_fraction=sampler.acceptance_fraction,
                        Omega_m=Om_s, beta=beta_s)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nOutputs:")
    print(f"  chain   : {chain_path}")
    print(f"  summary : {summary_path}")
    print(f"  plots   : {plots_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
