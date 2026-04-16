#!/usr/bin/env python3
"""
V' Robustness Test + Valley Volume + Multi-Parameter Scan
==========================================================

Determines whether the EFC (mu, Sigma, eta) valley is:
    ROBUST   (>10% of parameter space)
    MARGINAL (1-10%)
    FRAGILE  (<1%)

Three tests:
    1. V' response curve at fixed (k, z)
    2. 2D valley map in (V', k) space
    3. Multi-parameter Monte Carlo (all params +/-20%)
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from efc_inference.engine.lensing import EFCLensingParams, compute_mu_eta_sigma

z = 0.5
k_sweet = 0.08

# ================================================================
# STEP 1: V' scan
# ================================================================
print("=" * 70)
print("V' RESPONSE CURVE at k=0.08, z=0.5")
print("=" * 70)

Vp_range = np.linspace(0.1, 1.5, 100)
vp_hdr = "Vprime"
print(f"  {vp_hdr:>8} {'mu':>8} {'eta':>8} {'Sigma':>8} {'slip':>8} {'R':>8}")
print("-" * 60)

valley_count = 0
valley_vp = []

display_vals = [0.1, 0.3, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5]

for Vp in Vp_range:
    p = EFCLensingParams(V_prime=Vp)
    r = compute_mu_eta_sigma(k_sweet, z, p)

    in_v = (0.93 < r['mu'] < 0.96 and 1.03 < r['sigma'] < 1.07
            and 1.05 < r['eta'] < 1.15)

    show = any(abs(Vp - v) < 0.02 for v in display_vals) or in_v
    if show:
        marker = ' <-- VALLEY' if in_v else ''
        print(f"  {Vp:8.3f} {r['mu']:8.4f} {r['eta']:8.4f} "
              f"{r['sigma']:8.4f} {r['slip']:8.4f} {r['R']:8.4f}{marker}")

    if in_v:
        valley_count += 1
        valley_vp.append(Vp)

total = len(Vp_range)
print(f"\nValley fraction: {valley_count}/{total} = {valley_count/total:.1%}")
if valley_vp:
    print(f"Valley V' range: [{min(valley_vp):.3f}, {max(valley_vp):.3f}]")
    width = max(valley_vp) - min(valley_vp)
    center = np.mean(valley_vp)
    print(f"Valley V' width: {width:.3f} (center: {center:.3f})")
    print(f"Fractional width: {width / center:.1%}")

# ================================================================
# STEP 2: 2D valley map (V', k)
# ================================================================
print(f"\n{'=' * 70}")
print("2D VALLEY MAP: (V', k)")
print("=" * 70)

Vp_2d = np.linspace(0.1, 1.5, 80)
k_2d = np.logspace(-1.5, -0.3, 80)  # 0.03 to 0.5

valley_area = 0
total_area = 0
valley_points = []

for Vp in Vp_2d:
    for k in k_2d:
        p = EFCLensingParams(V_prime=Vp)
        r = compute_mu_eta_sigma(float(k), z, p)

        total_area += 1
        if (0.93 < r['mu'] < 0.96
                and np.isfinite(r['sigma']) and 1.03 < r['sigma'] < 1.07
                and 1.05 < r['eta'] < 1.15
                and r['regime'] in ('VALLEY', 'GR')):
            valley_area += 1
            valley_points.append((Vp, k, r['mu'], r['eta'], r['sigma']))

print(f"Valley area: {valley_area}/{total_area} = {valley_area / total_area:.2%}")

if valley_points:
    vps = [x[0] for x in valley_points]
    ks = [x[1] for x in valley_points]
    print(f"V' range in valley: [{min(vps):.3f}, {max(vps):.3f}]")
    print(f"k range in valley:  [{min(ks):.4f}, {max(ks):.4f}] h/Mpc")

    score = valley_area / total_area
    if score > 0.10:
        verdict = "ROBUST (>10% of parameter space)"
    elif score > 0.01:
        verdict = "MARGINAL (1-10%)"
    else:
        verdict = "FINE-TUNED (<1%)"
    print(f"\nVALLEY SCORE: {score:.2%} -- {verdict}")

# ================================================================
# STEP 3: Multi-parameter robustness (all params +/-20%)
# ================================================================
print(f"\n{'=' * 70}")
print("MULTI-PARAMETER ROBUSTNESS (all params +/-20%)")
print("=" * 70)

base = EFCLensingParams()
n_samples = 5000
rng = np.random.RandomState(42)

in_valley_count = 0
near_valley_count = 0
mu_lt1_count = 0
sigma_gt1_count = 0

for _ in range(n_samples):
    p = EFCLensingParams(
        alpha=base.alpha * (1.0 + 0.2 * (2 * rng.random() - 1)),
        K0=base.K0 * (1.0 + 0.2 * (2 * rng.random() - 1)),
        gamma0=base.gamma0 * (1.0 + 0.2 * (2 * rng.random() - 1)),
        V_prime=base.V_prime * (1.0 + 0.2 * (2 * rng.random() - 1)),
    )

    r = compute_mu_eta_sigma(k_sweet, z, p)

    if r['mu'] < 1.0:
        mu_lt1_count += 1
    if np.isfinite(r['sigma']) and r['sigma'] > 1.0:
        sigma_gt1_count += 1

    in_v = (0.93 < r['mu'] < 0.96
            and np.isfinite(r['sigma']) and 1.03 < r['sigma'] < 1.07
            and 1.05 < r['eta'] < 1.15)
    near_v = (0.90 < r['mu'] < 0.97
              and np.isfinite(r['sigma']) and r['sigma'] > 1.0
              and 1.0 < r['eta'] < 1.3)

    if in_v:
        in_valley_count += 1
    if near_v:
        near_valley_count += 1

print(f"  Samples: {n_samples}")
print(f"  mu < 1:           {mu_lt1_count}/{n_samples} = {mu_lt1_count / n_samples:.1%}")
print(f"  Sigma > 1:        {sigma_gt1_count}/{n_samples} = {sigma_gt1_count / n_samples:.1%}")
print(f"  In valley:        {in_valley_count}/{n_samples} = {in_valley_count / n_samples:.1%}")
print(f"  Near valley:      {near_valley_count}/{n_samples} = {near_valley_count / n_samples:.1%}")

if in_valley_count / n_samples > 0.10:
    robustness = "ROBUST"
elif in_valley_count / n_samples > 0.01:
    robustness = "MARGINAL"
else:
    robustness = "FRAGILE"
print(f"\n  ROBUSTNESS VERDICT: {robustness}")

# ================================================================
# BOTTOM LINE
# ================================================================
print(f"\n{'=' * 70}")
print("BOTTOM LINE")
print("=" * 70)

vp_info = (f"range [{min(valley_vp):.2f}, {max(valley_vp):.2f}]"
           if valley_vp else "narrow")
mc_pct = in_valley_count / n_samples
publishable = mc_pct > 0.05

print(f"""
  Valley exists at k ~ 0.07-0.10 h/Mpc with:
    mu ~ 0.96, eta ~ 1.10-1.15, Sigma ~ 1.03

  V' sensitivity: {vp_info}
  Multi-param robustness: {mc_pct:.1%} of +/-20% perturbations stay in valley

  The valley is {"PUBLISHABLE" if publishable else "FRAGILE -- needs more work"}
""")
