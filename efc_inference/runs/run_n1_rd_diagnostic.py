#!/usr/bin/env python3
"""
N1: BAO(14)+Growth(7) rd diagnostic — is the α hint real or an rd artifact?

N1a: rd FIXED at 147.09 Mpc (Planck)
     4 free params: [Omega_m, H0, sigma8, alpha_cosmo]
     LCDM baseline: 3 free params: [Omega_m, H0, sigma8]

N1b: rd with Gaussian prior N(147.1, 4.0) — mild BBN/CMB-ish regularization
     5 free params: [Omega_m, H0, rd, sigma8, alpha_cosmo]
     LCDM baseline: 4 free params: [Omega_m, H0, rd, sigma8]

Key question: Does α survive when rd can't absorb degrees of freedom?
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import emcee
from multiprocessing import Pool

from efc_inference.engine.hubble import EFCHubble
from efc_inference.engine.growth import EFCGrowth
from efc_inference.modules.bao_module import BAOModule
from efc_inference.modules.growth_module import GrowthModule


# ── Data paths ──
BAO_PATH = "efc_inference/data/bao/bao_starter.csv"
GROWTH_PATH = "efc_inference/data/growth/fs8_extended.csv"


def load_modules():
    """Load BAO + Growth modules."""
    bao_engine = EFCHubble()
    bao_mod = BAOModule(bao_engine)
    bao_mod.load_data(data_path=BAO_PATH)

    growth_engine = EFCGrowth()
    growth_mod = GrowthModule(growth_engine)
    growth_mod.load_data(data_path=GROWTH_PATH)

    return bao_mod, growth_mod


# ═══════════════════════════════════════════════════════════════
#  N1a: rd FIXED = 147.09
# ═══════════════════════════════════════════════════════════════

def log_prior_n1a_efc(theta):
    """EFC prior: [Omega_m, H0, sigma8, alpha_cosmo]. rd fixed."""
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    return 0.0


def log_prior_n1a_lcdm(theta):
    """LCDM prior: [Omega_m, H0, sigma8]. rd fixed."""
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    return 0.0


def log_prob_n1a_efc(theta, bao_mod, growth_mod):
    lp = log_prior_n1a_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": 147.09}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


def log_prob_n1a_lcdm(theta, bao_mod, growth_mod):
    lp = log_prior_n1a_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": 147.09}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


# ═══════════════════════════════════════════════════════════════
#  N1b: rd with Gaussian prior N(147.1, 4.0)
# ═══════════════════════════════════════════════════════════════

RD_PRIOR_MU = 147.1
RD_PRIOR_SIGMA = 4.0


def log_prior_n1b_efc(theta):
    """EFC prior: [Omega_m, H0, rd, sigma8, alpha_cosmo] + rd Gaussian."""
    Om, H0, rd, s8, alpha = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (100.0 < rd < 200.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    if not (-10.0 < alpha < 10.0): return -np.inf
    # Gaussian prior on rd
    lp_rd = -0.5 * ((rd - RD_PRIOR_MU) / RD_PRIOR_SIGMA)**2
    return lp_rd


def log_prior_n1b_lcdm(theta):
    """LCDM prior: [Omega_m, H0, rd, sigma8] + rd Gaussian."""
    Om, H0, rd, s8 = theta
    if not (0.1 < Om < 0.6):   return -np.inf
    if not (50.0 < H0 < 85.0): return -np.inf
    if not (100.0 < rd < 200.0): return -np.inf
    if not (0.5 < s8 < 1.2):   return -np.inf
    lp_rd = -0.5 * ((rd - RD_PRIOR_MU) / RD_PRIOR_SIGMA)**2
    return lp_rd


def log_prob_n1b_efc(theta, bao_mod, growth_mod):
    lp = log_prior_n1b_efc(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8, alpha = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": alpha, "r_d": rd}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


def log_prob_n1b_lcdm(theta, bao_mod, growth_mod):
    lp = log_prior_n1b_lcdm(theta)
    if not np.isfinite(lp):
        return -np.inf
    Om, H0, rd, s8 = theta
    params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
              "alpha_cosmo": 0.0, "r_d": rd}
    ll_bao = bao_mod.log_likelihood(params)
    ll_gr = growth_mod.log_likelihood(params)
    if not np.isfinite(ll_bao) or not np.isfinite(ll_gr):
        return -np.inf
    return lp + ll_bao + ll_gr


# ═══════════════════════════════════════════════════════════════
#  MCMC runner
# ═══════════════════════════════════════════════════════════════

def run_mcmc(label, log_prob_fn, ndim, p0, nwalkers, nsteps, burnin, args):
    """Run emcee and return flat chain + best logprob."""
    import time
    print(f"\n── {label}: {nwalkers}w × {nsteps}s ──")
    t0 = time.time()

    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob_fn, args=args)
    sampler.run_mcmc(p0, nsteps, progress=True)

    dt = time.time() - t0
    chain = sampler.get_chain(discard=burnin, flat=True)
    logprob = sampler.get_log_prob(discard=burnin, flat=True)
    print(f"Chain: {chain.shape}, time: {dt:.0f}s")

    return chain, logprob


def summarize(label, param_names, chain, logprob, n_data):
    """Print parameter summary and return best-fit logprob."""
    ndim = len(param_names)
    k = ndim  # number of free parameters
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

    # Significance of alpha if present
    if "alpha_cosmo" in param_names:
        idx_a = param_names.index("alpha_cosmo")
        a_mean = np.mean(chain[:, idx_a])
        a_std = np.std(chain[:, idx_a])
        sig = abs(a_mean) / a_std if a_std > 0 else 0
        p_neg = np.mean(chain[:, idx_a] < 0) * 100
        print(f"\n  |α|/σ = {sig:.2f}σ")
        print(f"  P(α<0) = {p_neg:.1f}%")

    # Correlations
    if ndim > 1:
        print(f"\n--- Correlations ---")
        corrmat = np.corrcoef(chain.T)
        for i in range(ndim):
            for j in range(i+1, ndim):
                r = corrmat[i, j]
                flag = " *** DEGENERACY" if abs(r) > 0.7 else ""
                print(f"  Corr({param_names[i]}, {param_names[j]}) = "
                      f"{r:+.3f}{flag}")

    # Chi2 at best fit
    chi2_total = -2.0 * ll_max
    dof = n_data - k
    chi2_red = chi2_total / dof if dof > 0 else float('inf')
    print(f"\n  LL_max: {ll_max:.2f}")
    print(f"  χ² Total: {chi2_total:.2f}, dof={dof}, χ²_red={chi2_red:.3f}")

    return ll_max, k


def compare_models(ll_efc, k_efc, ll_lcdm, k_lcdm, n_data):
    """AIC/BIC comparison."""
    aic_efc = -2 * ll_efc + 2 * k_efc
    aic_lcdm = -2 * ll_lcdm + 2 * k_lcdm
    bic_efc = -2 * ll_efc + k_efc * np.log(n_data)
    bic_lcdm = -2 * ll_lcdm + k_lcdm * np.log(n_data)

    daic = aic_efc - aic_lcdm
    dbic = bic_efc - bic_lcdm

    pref = "EFC" if daic < 0 else "LCDM"
    print(f"\n  ΔAIC = {daic:.2f} ({pref} favored)")
    pref = "EFC" if dbic < 0 else "LCDM"
    print(f"  ΔBIC = {dbic:.2f} ({pref} favored)")

    return daic, dbic


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    bao_mod, growth_mod = load_modules()
    n_bao = len(bao_mod.coordinates)
    n_gr = len(growth_mod.coordinates)
    n_total = n_bao + n_gr
    print(f"BAO: {n_bao} pts, Growth: {n_gr} pts, Total: {n_total}")

    NWALKERS = 48
    NSTEPS = 4000
    BURNIN = 1500
    args = (bao_mod, growth_mod)

    # ═══════════════════════════════════════════════════════════
    # N1a: rd FIXED = 147.09
    # ═══════════════════════════════════════════════════════════
    print("\n" + "█"*60)
    print("  N1a: rd FIXED = 147.09 Mpc (Planck)")
    print("█"*60)

    # EFC: 4 params [Omega_m, H0, sigma8, alpha_cosmo]
    p0_efc = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),   # Omega_m
        np.random.uniform(65, 72, NWALKERS),        # H0
        np.random.uniform(0.7, 0.9, NWALKERS),      # sigma8
        np.random.uniform(-3, 1, NWALKERS),          # alpha_cosmo
    ])
    chain_efc, lp_efc = run_mcmc(
        "N1a EFC (rd=147.09)", log_prob_n1a_efc,
        ndim=4, p0=p0_efc, nwalkers=NWALKERS, nsteps=NSTEPS,
        burnin=BURNIN, args=args
    )
    ll_efc, k_efc = summarize(
        "N1a EFC (rd=147.09 FIXED)",
        ["Omega_m", "H0", "sigma8", "alpha_cosmo"],
        chain_efc, lp_efc, n_total
    )

    # LCDM: 3 params [Omega_m, H0, sigma8]
    p0_lcdm = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        np.random.uniform(0.7, 0.9, NWALKERS),
    ])
    chain_lcdm, lp_lcdm = run_mcmc(
        "N1a LCDM (rd=147.09)", log_prob_n1a_lcdm,
        ndim=3, p0=p0_lcdm, nwalkers=NWALKERS, nsteps=NSTEPS,
        burnin=BURNIN, args=args
    )
    ll_lcdm, k_lcdm = summarize(
        "N1a LCDM (rd=147.09 FIXED)",
        ["Omega_m", "H0", "sigma8"],
        chain_lcdm, lp_lcdm, n_total
    )

    print(f"\n── N1a Model comparison (rd FIXED) ──")
    print(f"  LL_max(EFC):  {ll_efc:.2f}")
    print(f"  LL_max(LCDM): {ll_lcdm:.2f}")
    daic_a, dbic_a = compare_models(ll_efc, k_efc, ll_lcdm, k_lcdm, n_total)

    # Per-probe chi2 at best-fit EFC
    idx_best = np.argmax(lp_efc)
    Om_b, H0_b, s8_b, a_b = chain_efc[idx_best]
    pars_best = {"Omega_m": Om_b, "H0": H0_b, "sigma8": s8_b,
                 "alpha_cosmo": a_b, "r_d": 147.09}
    chi2_bao = -2.0 * bao_mod.log_likelihood(pars_best)
    chi2_gr = -2.0 * growth_mod.log_likelihood(pars_best)
    print(f"\n  Per-probe χ² (best EFC):")
    print(f"    BAO:    {chi2_bao:.2f} ({n_bao} pts)")
    print(f"    Growth: {chi2_gr:.2f} ({n_gr} pts)")

    # ═══════════════════════════════════════════════════════════
    # N1b: rd with Gaussian prior N(147.1, 4.0)
    # ═══════════════════════════════════════════════════════════
    print("\n\n" + "█"*60)
    print(f"  N1b: rd ~ N({RD_PRIOR_MU}, {RD_PRIOR_SIGMA})")
    print("█"*60)

    # EFC: 5 params [Omega_m, H0, rd, sigma8, alpha_cosmo]
    p0_efc = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        np.random.normal(147.1, 3.0, NWALKERS),
        np.random.uniform(0.7, 0.9, NWALKERS),
        np.random.uniform(-3, 1, NWALKERS),
    ])
    chain_efc_b, lp_efc_b = run_mcmc(
        "N1b EFC (rd prior)", log_prob_n1b_efc,
        ndim=5, p0=p0_efc, nwalkers=NWALKERS, nsteps=NSTEPS,
        burnin=BURNIN, args=args
    )
    ll_efc_b, k_efc_b = summarize(
        f"N1b EFC (rd ~ N({RD_PRIOR_MU},{RD_PRIOR_SIGMA}))",
        ["Omega_m", "H0", "r_d", "sigma8", "alpha_cosmo"],
        chain_efc_b, lp_efc_b, n_total
    )

    # LCDM: 4 params [Omega_m, H0, rd, sigma8]
    p0_lcdm = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        np.random.normal(147.1, 3.0, NWALKERS),
        np.random.uniform(0.7, 0.9, NWALKERS),
    ])
    chain_lcdm_b, lp_lcdm_b = run_mcmc(
        "N1b LCDM (rd prior)", log_prob_n1b_lcdm,
        ndim=4, p0=p0_lcdm, nwalkers=NWALKERS, nsteps=NSTEPS,
        burnin=BURNIN, args=args
    )
    ll_lcdm_b, k_lcdm_b = summarize(
        f"N1b LCDM (rd ~ N({RD_PRIOR_MU},{RD_PRIOR_SIGMA}))",
        ["Omega_m", "H0", "r_d", "sigma8"],
        chain_lcdm_b, lp_lcdm_b, n_total
    )

    print(f"\n── N1b Model comparison (rd prior) ──")
    print(f"  LL_max(EFC):  {ll_efc_b:.2f}")
    print(f"  LL_max(LCDM): {ll_lcdm_b:.2f}")
    daic_b, dbic_b = compare_models(ll_efc_b, k_efc_b, ll_lcdm_b, k_lcdm_b, n_total)

    # Per-probe chi2 at best-fit EFC (N1b)
    idx_best_b = np.argmax(lp_efc_b)
    Om_b2, H0_b2, rd_b2, s8_b2, a_b2 = chain_efc_b[idx_best_b]
    pars_best_b = {"Omega_m": Om_b2, "H0": H0_b2, "sigma8": s8_b2,
                   "alpha_cosmo": a_b2, "r_d": rd_b2}
    chi2_bao_b = -2.0 * bao_mod.log_likelihood(pars_best_b)
    chi2_gr_b = -2.0 * growth_mod.log_likelihood(pars_best_b)
    print(f"\n  Per-probe χ² (best EFC):")
    print(f"    BAO:    {chi2_bao_b:.2f} ({n_bao} pts)")
    print(f"    Growth: {chi2_gr_b:.2f} ({n_gr} pts)")

    # rd posterior width
    rd_mean = np.mean(chain_efc_b[:, 2])
    rd_std = np.std(chain_efc_b[:, 2])
    rd_lo, rd_hi = np.percentile(chain_efc_b[:, 2], [2.5, 97.5])
    print(f"\n  rd posterior: {rd_mean:.1f} ± {rd_std:.1f}  95%CI=[{rd_lo:.1f}, {rd_hi:.1f}]")
    print(f"  rd prior:     {RD_PRIOR_MU} ± {RD_PRIOR_SIGMA}")
    if rd_std < RD_PRIOR_SIGMA * 0.8:
        print(f"  → rd CONSTRAINED by data (σ_post < 0.8 × σ_prior)")
    else:
        print(f"  → rd PRIOR-DOMINATED (σ_post ≈ σ_prior)")

    # ═══════════════════════════════════════════════════════════
    # SUMMARY TABLE
    # ═══════════════════════════════════════════════════════════
    print("\n\n" + "="*60)
    print("  DIAGNOSTIC SUMMARY: rd sensitivity")
    print("="*60)

    # Extract alpha from each run
    for run_label, chain_run, lp_run, daic, dbic in [
        ("Orig (rd flat)", None, None, -1.89, -0.84),
        ("N1a (rd=147.09)", chain_efc, lp_efc, daic_a, dbic_a),
        ("N1b (rd prior)", chain_efc_b, lp_efc_b, daic_b, dbic_b),
    ]:
        if chain_run is not None:
            idx_a = -1  # alpha is always last column
            a_m = np.mean(chain_run[:, idx_a])
            a_s = np.std(chain_run[:, idx_a])
            sig = abs(a_m) / a_s if a_s > 0 else 0

            # Get key correlations
            corrmat = np.corrcoef(chain_run.T)
            # alpha vs Omega_m (col 0)
            corr_a_om = corrmat[0, idx_a]
            # alpha vs sigma8 (col before alpha)
            if chain_run.shape[1] == 4:
                corr_a_s8 = corrmat[2, 3]   # sigma8=col2, alpha=col3
            else:
                corr_a_s8 = corrmat[3, 4]   # sigma8=col3, alpha=col4

            print(f"\n  {run_label}:")
            print(f"    α = {a_m:.2f} ± {a_s:.2f}  ({sig:.2f}σ)")
            print(f"    ΔAIC={daic:.2f}  ΔBIC={dbic:.2f}")
            print(f"    corr(α,Ωm)={corr_a_om:+.3f}  corr(α,σ8)={corr_a_s8:+.3f}")
        else:
            print(f"\n  {run_label} (from previous run):")
            print(f"    α = -1.22 ± 0.62  (1.95σ)")
            print(f"    ΔAIC={daic:.2f}  ΔBIC={dbic:.2f}")
            print(f"    corr(α,Ωm)=+0.775  corr(α,σ8)=-0.719")

    # Verdict
    print("\n" + "="*60)
    a_n1a = np.mean(chain_efc[:, 3])
    s_n1a = np.std(chain_efc[:, 3])
    sig_n1a = abs(a_n1a) / s_n1a if s_n1a > 0 else 0

    a_n1b = np.mean(chain_efc_b[:, 4])
    s_n1b = np.std(chain_efc_b[:, 4])
    sig_n1b = abs(a_n1b) / s_n1b if s_n1b > 0 else 0

    if sig_n1a < 1.0 and sig_n1b < 1.0:
        print("  VERDICT: α COLLAPSED — signal was rd artifact")
    elif sig_n1a > 1.5 and sig_n1b > 1.5:
        print("  VERDICT: α ROBUST — signal survives rd control")
    elif sig_n1a > 1.5 and sig_n1b < 1.5:
        print("  VERDICT: α PARTIALLY ROBUST — survives fixed rd but weakens with prior")
    else:
        print("  VERDICT: α MARGINAL — needs further investigation")

    print(f"    N1a: {sig_n1a:.2f}σ   N1b: {sig_n1b:.2f}σ")
    print("="*60)


if __name__ == "__main__":
    main()
