#!/usr/bin/env python3
"""
N2: σ8 prior-sweep — is the α hint driven by σ8 freedom?

All runs use rd FIXED = 147.09 (N1a-modus, rd is clean).
Three σ8 treatments:

  N2a: σ8 ~ N(0.81, 0.02)  — stram (Planck-ish)
  N2b: σ8 ~ N(0.81, 0.06)  — middels
  N2c: σ8 ~ U(0.6, 1.0)    — flat bred (= original)

Free params (EFC):  [Omega_m, H0, sigma8, alpha_cosmo]  (4 params, rd=147.09)
Free params (LCDM): [Omega_m, H0, sigma8]               (3 params, rd=147.09)

Key question: Does α survive when σ8 can't absorb the signal?
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import emcee
import time

from efc_inference.engine.hubble import EFCHubble
from efc_inference.engine.growth import EFCGrowth
from efc_inference.modules.bao_module import BAOModule
from efc_inference.modules.growth_module import GrowthModule

# ── Constants ──
RD_FIXED = 147.09
BAO_PATH = "efc_inference/data/bao/bao_starter.csv"
GROWTH_PATH = "efc_inference/data/growth/fs8_extended.csv"
NWALKERS = 48
NSTEPS = 4000
BURNIN = 1500


def load_modules():
    bao_engine = EFCHubble()
    bao_mod = BAOModule(bao_engine)
    bao_mod.load_data(data_path=BAO_PATH)
    growth_engine = EFCGrowth()
    growth_mod = GrowthModule(growth_engine)
    growth_mod.load_data(data_path=GROWTH_PATH)
    return bao_mod, growth_mod


# ═══════════════════════════════════════════════════════════════
#  Prior functions — parameterized by σ8 treatment
# ═══════════════════════════════════════════════════════════════

def _sigma8_log_prior(s8, mode):
    """Return log-prior contribution from σ8 given mode."""
    if mode == "stram":
        # N(0.81, 0.02)
        if not (0.5 < s8 < 1.2):
            return -np.inf
        return -0.5 * ((s8 - 0.81) / 0.02)**2
    elif mode == "middels":
        # N(0.81, 0.06)
        if not (0.5 < s8 < 1.2):
            return -np.inf
        return -0.5 * ((s8 - 0.81) / 0.06)**2
    elif mode == "flat":
        # U(0.6, 1.0)
        if not (0.6 < s8 < 1.0):
            return -np.inf
        return 0.0
    else:
        raise ValueError(f"Unknown σ8 mode: {mode}")


def log_prior_efc(theta, s8_mode):
    """EFC prior: [Omega_m, H0, sigma8, alpha_cosmo]. rd fixed."""
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):
        return -np.inf
    if not (50.0 < H0 < 85.0):
        return -np.inf
    if not (-10.0 < alpha < 10.0):
        return -np.inf
    lp_s8 = _sigma8_log_prior(s8, s8_mode)
    if not np.isfinite(lp_s8):
        return -np.inf
    return lp_s8


def log_prior_lcdm(theta, s8_mode):
    """LCDM prior: [Omega_m, H0, sigma8]. rd fixed."""
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):
        return -np.inf
    if not (50.0 < H0 < 85.0):
        return -np.inf
    lp_s8 = _sigma8_log_prior(s8, s8_mode)
    if not np.isfinite(lp_s8):
        return -np.inf
    return lp_s8


def log_prob_efc(theta, bao_mod, growth_mod, s8_mode):
    lp = log_prior_efc(theta, s8_mode)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": RD_FIXED}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


def log_prob_lcdm(theta, bao_mod, growth_mod, s8_mode):
    lp = log_prior_lcdm(theta, s8_mode)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": RD_FIXED}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


# ═══════════════════════════════════════════════════════════════
#  MCMC + Analysis
# ═══════════════════════════════════════════════════════════════

def run_mcmc(label, log_prob_fn, ndim, p0, args):
    print(f"\n── {label}: {NWALKERS}w × {NSTEPS}s ──")
    t0 = time.time()
    sampler = emcee.EnsembleSampler(NWALKERS, ndim, log_prob_fn, args=args)
    sampler.run_mcmc(p0, NSTEPS, progress=True)
    dt = time.time() - t0
    chain = sampler.get_chain(discard=BURNIN, flat=True)
    logprob = sampler.get_log_prob(discard=BURNIN, flat=True)
    print(f"Chain: {chain.shape}, time: {dt:.0f}s")
    return chain, logprob


def summarize(label, param_names, chain, logprob, n_data):
    ndim = len(param_names)
    ll_max = np.max(logprob)

    print(f"\n{'='*60}")
    print(f"{label} — {ndim} params")
    print(f"{'='*60}")

    for i, name in enumerate(param_names):
        med = np.median(chain[:, i])
        mean = np.mean(chain[:, i])
        std = np.std(chain[:, i])
        lo, hi = np.percentile(chain[:, i], [2.5, 97.5])
        print(f"  {name:18s}: {mean:.4f} ± {std:.4f}  "
              f"median={med:.4f}  95%CI=[{lo:.4f}, {hi:.4f}]")

    if "alpha_cosmo" in param_names:
        idx_a = param_names.index("alpha_cosmo")
        a_mean = np.mean(chain[:, idx_a])
        a_std = np.std(chain[:, idx_a])
        sig = abs(a_mean) / a_std if a_std > 0 else 0
        p_neg = np.mean(chain[:, idx_a] < 0) * 100
        print(f"\n  |α|/σ = {sig:.2f}σ")
        print(f"  P(α<0) = {p_neg:.1f}%")

    if ndim > 1:
        print(f"\n--- Correlations ---")
        corrmat = np.corrcoef(chain.T)
        for i in range(ndim):
            for j in range(i+1, ndim):
                r = corrmat[i, j]
                flag = " *** DEGENERACY" if abs(r) > 0.7 else ""
                print(f"  Corr({param_names[i]}, {param_names[j]}) = "
                      f"{r:+.3f}{flag}")

    chi2_total = -2.0 * ll_max
    dof = n_data - ndim
    chi2_red = chi2_total / dof if dof > 0 else float('inf')
    print(f"\n  LL_max: {ll_max:.2f}")

    return ll_max, ndim


def compare_models(ll_efc, k_efc, ll_lcdm, k_lcdm, n_data):
    aic_efc = -2 * ll_efc + 2 * k_efc
    aic_lcdm = -2 * ll_lcdm + 2 * k_lcdm
    bic_efc = -2 * ll_efc + k_efc * np.log(n_data)
    bic_lcdm = -2 * ll_lcdm + k_lcdm * np.log(n_data)
    daic = aic_efc - aic_lcdm
    dbic = bic_efc - bic_lcdm
    pref = "EFC" if daic < 0 else "LCDM"
    print(f"  ΔAIC = {daic:.2f} ({pref} favored)")
    pref = "EFC" if dbic < 0 else "LCDM"
    print(f"  ΔBIC = {dbic:.2f} ({pref} favored)")
    return daic, dbic


def run_variant(label, s8_mode, bao_mod, growth_mod, n_total):
    """Run one σ8 variant (EFC + LCDM)."""
    print(f"\n\n{'█'*60}")
    print(f"  {label}")
    print(f"{'█'*60}")

    # σ8 init center
    s8_center = 0.81
    if s8_mode == "flat":
        s8_init = np.random.uniform(0.7, 0.9, NWALKERS)
    else:
        s8_init = np.random.normal(0.81, 0.03, NWALKERS)
        s8_init = np.clip(s8_init, 0.6, 1.1)

    # EFC: 4 params
    p0_efc = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        s8_init,
        np.random.uniform(-3, 1, NWALKERS),
    ])
    chain_efc, lp_efc = run_mcmc(
        f"{label} EFC", log_prob_efc, ndim=4, p0=p0_efc,
        args=(bao_mod, growth_mod, s8_mode)
    )
    ll_efc, k_efc = summarize(
        f"{label} EFC",
        ["Omega_m", "H0", "sigma8", "alpha_cosmo"],
        chain_efc, lp_efc, n_total
    )

    # LCDM: 3 params
    if s8_mode == "flat":
        s8_init_l = np.random.uniform(0.7, 0.9, NWALKERS)
    else:
        s8_init_l = np.random.normal(0.81, 0.03, NWALKERS)
        s8_init_l = np.clip(s8_init_l, 0.6, 1.1)

    p0_lcdm = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        s8_init_l,
    ])
    chain_lcdm, lp_lcdm = run_mcmc(
        f"{label} LCDM", log_prob_lcdm, ndim=3, p0=p0_lcdm,
        args=(bao_mod, growth_mod, s8_mode)
    )
    ll_lcdm, k_lcdm = summarize(
        f"{label} LCDM",
        ["Omega_m", "H0", "sigma8"],
        chain_lcdm, lp_lcdm, n_total
    )

    print(f"\n── {label} Model comparison ──")
    print(f"  LL_max(EFC):  {ll_efc:.2f}")
    print(f"  LL_max(LCDM): {ll_lcdm:.2f}")
    daic, dbic = compare_models(ll_efc, k_efc, ll_lcdm, k_lcdm, n_total)

    return chain_efc, lp_efc, daic, dbic


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    bao_mod, growth_mod = load_modules()
    n_bao = len(bao_mod.coordinates)
    n_gr = len(growth_mod.coordinates)
    n_total = n_bao + n_gr
    print(f"BAO: {n_bao} pts, Growth: {n_gr} pts, Total: {n_total}")
    print(f"rd FIXED = {RD_FIXED}")

    results = {}

    for label, s8_mode in [
        ("N2a: σ8~N(0.81,0.02) stram", "stram"),
        ("N2b: σ8~N(0.81,0.06) middels", "middels"),
        ("N2c: σ8~U(0.6,1.0) flat", "flat"),
    ]:
        chain, lp, daic, dbic = run_variant(
            label, s8_mode, bao_mod, growth_mod, n_total
        )
        # Extract key numbers
        a_mean = np.mean(chain[:, 3])
        a_std = np.std(chain[:, 3])
        sig = abs(a_mean) / a_std if a_std > 0 else 0

        om_mean = np.mean(chain[:, 0])
        om_std = np.std(chain[:, 0])
        s8_mean = np.mean(chain[:, 2])
        s8_std = np.std(chain[:, 2])

        corrmat = np.corrcoef(chain.T)
        corr_a_om = corrmat[0, 3]
        corr_a_s8 = corrmat[2, 3]

        results[s8_mode] = {
            "label": label,
            "alpha_mean": a_mean, "alpha_std": a_std, "sig": sig,
            "om_mean": om_mean, "om_std": om_std,
            "s8_mean": s8_mean, "s8_std": s8_std,
            "daic": daic, "dbic": dbic,
            "corr_a_om": corr_a_om, "corr_a_s8": corr_a_s8,
        }

    # ═══════════════════════════════════════════════════════════
    # SUMMARY TABLE
    # ═══════════════════════════════════════════════════════════
    print("\n\n" + "="*70)
    print("  N2 DIAGNOSTIC SUMMARY: σ8 sensitivity (rd=147.09 fixed)")
    print("="*70)

    # Reference from N1a
    print(f"\n  {'Run':<32s} {'α mean±σ':>14s} {'sig':>6s} {'ΔAIC':>7s} {'ΔBIC':>7s} {'r(α,Ωm)':>8s} {'r(α,σ8)':>8s} {'Ωm':>12s} {'σ8':>12s}")
    print(f"  {'-'*30}  {'-'*12}  {'-'*4}  {'-'*5}  {'-'*5}  {'-'*6}  {'-'*6}  {'-'*10}  {'-'*10}")

    # N1a reference
    print(f"  {'N1a ref (rd=147.09, σ8 flat)':<32s} {'-1.22±0.62':>14s} {'1.97':>6s} {'-1.90':>7s} {'-0.85':>7s} {'+0.782':>8s} {'-0.714':>8s} {'0.254±0.031':>12s} {'0.848±0.068':>12s}")

    for mode in ["stram", "middels", "flat"]:
        r = results[mode]
        a_str = f"{r['alpha_mean']:.2f}±{r['alpha_std']:.2f}"
        sig_str = f"{r['sig']:.2f}"
        daic_str = f"{r['daic']:.2f}"
        dbic_str = f"{r['dbic']:.2f}"
        corr_om_str = f"{r['corr_a_om']:+.3f}"
        corr_s8_str = f"{r['corr_a_s8']:+.3f}"
        om_str = f"{r['om_mean']:.3f}±{r['om_std']:.3f}"
        s8_str = f"{r['s8_mean']:.3f}±{r['s8_std']:.3f}"
        print(f"  {r['label']:<32s} {a_str:>14s} {sig_str:>6s} {daic_str:>7s} {dbic_str:>7s} {corr_om_str:>8s} {corr_s8_str:>8s} {om_str:>12s} {s8_str:>12s}")

    # Verdict
    print("\n" + "="*70)
    r_stram = results["stram"]
    r_flat = results["flat"]

    if r_stram["sig"] >= 1.7 and r_stram["daic"] <= 0:
        print("  VERDICT: α SURVIVES σ8 control — signal is genuine")
        print(f"    σ8 stram: {r_stram['sig']:.2f}σ, ΔAIC={r_stram['daic']:.2f}")
        print(f"    σ8 flat:  {r_flat['sig']:.2f}σ, ΔAIC={r_flat['daic']:.2f}")
    elif r_stram["sig"] < 1.3:
        print("  VERDICT: α COLLAPSED — signal was σ8-freedom artifact")
        print(f"    σ8 stram: {r_stram['sig']:.2f}σ (collapsed)")
        print(f"    σ8 flat:  {r_flat['sig']:.2f}σ")
    else:
        print("  VERDICT: α PARTIALLY DEPENDENT on σ8 — marginal signal")
        print(f"    σ8 stram: {r_stram['sig']:.2f}σ")
        print(f"    σ8 flat:  {r_flat['sig']:.2f}σ")

    # Degeneracy evolution
    print(f"\n  Degeneracy evolution across σ8 priors:")
    print(f"    {'Prior':<20s} {'corr(α,σ8)':>12s} {'corr(α,Ωm)':>12s}")
    for mode in ["stram", "middels", "flat"]:
        r = results[mode]
        short = {"stram": "N(0.81,0.02)", "middels": "N(0.81,0.06)", "flat": "U(0.6,1.0)"}[mode]
        print(f"    {short:<20s} {r['corr_a_s8']:>+12.3f} {r['corr_a_om']:>+12.3f}")

    print("="*70)


if __name__ == "__main__":
    main()
