#!/usr/bin/env python3
"""
T7: Leave-One-Out on fσ8(z) — is the α hint driven by one data point?

Setup: N2a-modus (rd=147.09 fixed, σ8~N(0.81,0.02) stram)
       BAO(14) always included in full.
       Growth: remove 1 of 7 fσ8 points each run.

7 LOO runs × (EFC + LCDM) = 14 MCMC chains total.

Pass/fail rule:
  - If α holds ~2σ in ≥5 of 7 LOO runs:  → ROBUST
  - If 1 point "carries" the whole effect:  → NOT ROBUST (identify which)

Robustness score = fraction of LOO runs with |α|/σ > 1.7
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

# ── Constants (N2a-modus) ──
RD_FIXED = 147.09
BAO_PATH = "efc_inference/data/bao/bao_starter.csv"
GROWTH_PATH = "efc_inference/data/growth/fs8_extended.csv"
NWALKERS = 48
NSTEPS = 3000      # Reduced from 4000 — LOO needs 14 runs
BURNIN = 1000


def load_bao():
    """Load BAO module (always full 14 pts)."""
    engine = EFCHubble()
    mod = BAOModule(engine)
    mod.load_data(data_path=BAO_PATH)
    return mod


def load_growth_loo(exclude_idx):
    """Load growth module, excluding point at index exclude_idx.

    Returns: GrowthModule with 6 of 7 points loaded, and info about excluded point.
    """
    # Read raw data
    raw = np.loadtxt(GROWTH_PATH, delimiter=",", skiprows=1)
    n_pts = raw.shape[0]

    excluded_z = raw[exclude_idx, 0]
    excluded_fs8 = raw[exclude_idx, 1]
    excluded_sig = raw[exclude_idx, 2]

    # Create mask
    mask = np.ones(n_pts, dtype=bool)
    mask[exclude_idx] = False
    reduced = raw[mask]

    # Write temporary file
    import tempfile
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    tmp.write("z,fs8,sigma\n")
    for row in reduced:
        tmp.write(f"{row[0]:.4f},{row[1]:.4f},{row[2]:.4f}\n")
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    engine = EFCGrowth()
    mod = GrowthModule(engine)
    mod.load_data(data_path=tmp_path)

    os.unlink(tmp_path)

    return mod, excluded_z, excluded_fs8, excluded_sig


# ═══════════════════════════════════════════════════════════════
#  Priors — N2a: σ8 ~ N(0.81, 0.02), rd = 147.09 fixed
# ═══════════════════════════════════════════════════════════════

def log_prior_efc(theta):
    Om, H0, s8, alpha = theta
    if not (0.1 < Om < 0.6):
        return -np.inf
    if not (50.0 < H0 < 85.0):
        return -np.inf
    if not (-10.0 < alpha < 10.0):
        return -np.inf
    if not (0.5 < s8 < 1.2):
        return -np.inf
    return -0.5 * ((s8 - 0.81) / 0.02)**2


def log_prior_lcdm(theta):
    Om, H0, s8 = theta
    if not (0.1 < Om < 0.6):
        return -np.inf
    if not (50.0 < H0 < 85.0):
        return -np.inf
    if not (0.5 < s8 < 1.2):
        return -np.inf
    return -0.5 * ((s8 - 0.81) / 0.02)**2


def log_prob_efc(theta, bao_mod, growth_mod):
    lp = log_prior_efc(theta)
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


def log_prob_lcdm(theta, bao_mod, growth_mod):
    lp = log_prior_lcdm(theta)
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
#  MCMC runner
# ═══════════════════════════════════════════════════════════════

def run_mcmc(label, log_prob_fn, ndim, p0, args):
    print(f"  {label}: {NWALKERS}w × {NSTEPS}s ... ", end="", flush=True)
    t0 = time.time()
    sampler = emcee.EnsembleSampler(NWALKERS, ndim, log_prob_fn, args=args)
    sampler.run_mcmc(p0, NSTEPS, progress=False)   # quiet for 14 runs
    dt = time.time() - t0
    chain = sampler.get_chain(discard=BURNIN, flat=True)
    logprob = sampler.get_log_prob(discard=BURNIN, flat=True)
    print(f"{dt:.0f}s, {chain.shape[0]} samples")
    return chain, logprob


def run_loo(idx, bao_mod):
    """Run one LOO iteration: exclude growth point idx, run EFC + LCDM."""
    growth_mod, ex_z, ex_fs8, ex_sig = load_growth_loo(idx)
    n_data = len(bao_mod.coordinates) + len(growth_mod.coordinates)  # 14 + 6 = 20

    label_base = f"LOO-{idx} (drop z={ex_z:.2f}, fσ8={ex_fs8:.3f}±{ex_sig:.3f})"
    print(f"\n── {label_base} ──")

    # EFC: 4 params
    p0_efc = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        np.random.normal(0.81, 0.015, NWALKERS),
        np.random.uniform(-3, 1, NWALKERS),
    ])
    chain_efc, lp_efc = run_mcmc(
        f"EFC", log_prob_efc, ndim=4, p0=p0_efc,
        args=(bao_mod, growth_mod)
    )
    ll_efc = np.max(lp_efc)

    # LCDM: 3 params
    p0_lcdm = np.column_stack([
        np.random.uniform(0.2, 0.35, NWALKERS),
        np.random.uniform(65, 72, NWALKERS),
        np.random.normal(0.81, 0.015, NWALKERS),
    ])
    chain_lcdm, lp_lcdm = run_mcmc(
        f"LCDM", log_prob_lcdm, ndim=3, p0=p0_lcdm,
        args=(bao_mod, growth_mod)
    )
    ll_lcdm = np.max(lp_lcdm)

    # Extract α stats
    a_mean = np.mean(chain_efc[:, 3])
    a_std = np.std(chain_efc[:, 3])
    sig = abs(a_mean) / a_std if a_std > 0 else 0
    p_neg = np.mean(chain_efc[:, 3] < 0) * 100

    # Ωm, σ8
    om_mean = np.mean(chain_efc[:, 0])
    om_std = np.std(chain_efc[:, 0])
    s8_mean = np.mean(chain_efc[:, 2])
    s8_std = np.std(chain_efc[:, 2])

    # Correlations
    corrmat = np.corrcoef(chain_efc.T)
    corr_a_om = corrmat[0, 3]
    corr_a_s8 = corrmat[2, 3]

    # Model comparison
    k_efc, k_lcdm = 4, 3
    aic_efc = -2 * ll_efc + 2 * k_efc
    aic_lcdm = -2 * ll_lcdm + 2 * k_lcdm
    bic_efc = -2 * ll_efc + k_efc * np.log(n_data)
    bic_lcdm = -2 * ll_lcdm + k_lcdm * np.log(n_data)
    daic = aic_efc - aic_lcdm
    dbic = bic_efc - bic_lcdm

    print(f"  α = {a_mean:.3f} ± {a_std:.3f}  ({sig:.2f}σ)  "
          f"P(α<0)={p_neg:.1f}%  ΔAIC={daic:.2f}  ΔBIC={dbic:.2f}")

    return {
        "idx": idx,
        "z_excluded": ex_z,
        "fs8_excluded": ex_fs8,
        "sig_excluded": ex_sig,
        "alpha_mean": a_mean,
        "alpha_std": a_std,
        "sig": sig,
        "p_neg": p_neg,
        "daic": daic,
        "dbic": dbic,
        "om_mean": om_mean,
        "om_std": om_std,
        "s8_mean": s8_mean,
        "s8_std": s8_std,
        "corr_a_om": corr_a_om,
        "corr_a_s8": corr_a_s8,
        "ll_efc": ll_efc,
        "ll_lcdm": ll_lcdm,
    }


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    np.random.seed(42)
    print("=" * 70)
    print("  T7: LEAVE-ONE-OUT on fσ8 (N2a-modus: rd=147.09, σ8 stram)")
    print("=" * 70)

    bao_mod = load_bao()
    print(f"BAO: {len(bao_mod.coordinates)} pts (always full)")

    # Read full growth data for reference
    raw = np.loadtxt(GROWTH_PATH, delimiter=",", skiprows=1)
    n_growth = raw.shape[0]
    print(f"Growth: {n_growth} pts total, LOO = {n_growth} runs × 2 chains")
    print(f"Priors: σ8~N(0.81,0.02), rd={RD_FIXED}")
    print(f"MCMC: {NWALKERS}w × {NSTEPS}s, burnin={BURNIN}")

    # Full data points for reference
    print(f"\nfσ8 data points:")
    for i in range(n_growth):
        print(f"  [{i}] z={raw[i,0]:.2f}  fσ8={raw[i,1]:.3f}±{raw[i,2]:.3f}")

    t_total = time.time()

    # Run all LOO iterations
    results = []
    for i in range(n_growth):
        r = run_loo(i, bao_mod)
        results.append(r)

    dt_total = time.time() - t_total

    # ═══════════════════════════════════════════════════════════
    # SUMMARY TABLE
    # ═══════════════════════════════════════════════════════════
    print("\n\n" + "=" * 80)
    print("  T7 LEAVE-ONE-OUT SUMMARY (N2a-modus: rd=147.09, σ8~N(0.81,0.02))")
    print("=" * 80)

    # N2a reference (all 7 growth pts)
    print(f"\n  N2a reference (all 7):  α = -1.00±0.46,  2.20σ,  ΔAIC=-2.91")
    print()

    hdr = (f"  {'Drop':>5s}  {'z':>5s}  {'fσ8±σ':>12s}  "
           f"{'α mean±σ':>12s}  {'|α|/σ':>6s}  {'ΔAIC':>7s}  {'ΔBIC':>7s}  "
           f"{'r(α,Ωm)':>8s}  {'r(α,σ8)':>8s}  {'pass':>5s}")
    print(hdr)
    print("  " + "-" * 76)

    n_pass = 0
    worst_idx = None
    worst_sig = 999

    for r in results:
        a_str = f"{r['alpha_mean']:.2f}±{r['alpha_std']:.2f}"
        fs8_str = f"{r['fs8_excluded']:.3f}±{r['sig_excluded']:.3f}"
        passed = r["sig"] >= 1.7 and r["daic"] <= 0
        if passed:
            n_pass += 1
        pf_str = "✓" if passed else "✗"

        if r["sig"] < worst_sig:
            worst_sig = r["sig"]
            worst_idx = r["idx"]

        print(f"  [{r['idx']:1d}]  {r['z_excluded']:5.2f}  {fs8_str:>12s}  "
              f"{a_str:>12s}  {r['sig']:6.2f}  {r['daic']:7.2f}  {r['dbic']:7.2f}  "
              f"{r['corr_a_om']:+8.3f}  {r['corr_a_s8']:+8.3f}  {pf_str:>5s}")

    robustness = n_pass / len(results)

    print("\n" + "=" * 80)
    print(f"  ROBUSTNESS SCORE: {n_pass}/{len(results)} = {robustness:.0%}")
    print(f"  (fraction of LOO runs with |α|/σ ≥ 1.7 AND ΔAIC ≤ 0)")

    # α range across LOO
    a_means = [r["alpha_mean"] for r in results]
    a_sigs = [r["sig"] for r in results]
    print(f"\n  α range:    [{min(a_means):.2f}, {max(a_means):.2f}]  "
          f"(spread = {max(a_means)-min(a_means):.2f})")
    print(f"  |α|/σ range: [{min(a_sigs):.2f}, {max(a_sigs):.2f}]")

    if worst_idx is not None:
        wr = results[worst_idx]
        print(f"\n  Most influential point: [{worst_idx}] z={wr['z_excluded']:.2f} "
              f"(dropping it gives |α|/σ = {wr['sig']:.2f})")

    # Verdict
    print()
    if robustness >= 5/7:
        print("  VERDICT: α is ROBUST to LOO — no single fσ8 point drives the signal")
        if robustness == 1.0:
            print("           Perfect score: all 7 LOO runs pass")
    elif robustness >= 3/7:
        print("  VERDICT: α is PARTIALLY ROBUST — some points have outsized influence")
        # Identify which points break it
        breakers = [r for r in results if not (r["sig"] >= 1.7 and r["daic"] <= 0)]
        for b in breakers:
            print(f"    ⚠ Dropping z={b['z_excluded']:.2f} weakens to {b['sig']:.2f}σ, ΔAIC={b['daic']:.2f}")
    else:
        print("  VERDICT: α is NOT ROBUST — signal depends on specific data points")
        # Identify breakers
        breakers = [r for r in results if not (r["sig"] >= 1.7 and r["daic"] <= 0)]
        for b in breakers:
            print(f"    ✗ z={b['z_excluded']:.2f}: {b['sig']:.2f}σ, ΔAIC={b['daic']:.2f}")

    print(f"\n  Total time: {dt_total:.0f}s ({dt_total/60:.1f} min)")
    print("=" * 80)


if __name__ == "__main__":
    main()
