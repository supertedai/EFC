#!/usr/bin/env python3
"""
KT5: External Field Effect (EFE)
==================================
In MOND/AQUAL, an external uniform field g_ext partially restores
Newtonian dynamics where internal g < a0.

v2 measurement strategy:
  - Subtract g_ext as a VECTOR from g_vec at each node
  - Project internal field onto radial direction: g_int_radial = g_int . r_hat
  - Radial-bin the radial component (not |g|)
  - Compare enhancement: should DECREASE with g_ext

Output: kt5_efe.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import (radial_profile, efe_enhancement,
                                 radial_g_profile_vector)


def _measure_efe_vectorial(res, G_eff, M, g_ext, a0,
                           r_min=6.0, r_max=12.0):
    """
    Vectorial EFE measurement.

    1. Subtract g_ext vector from g_vec at each node
    2. Project onto radial direction: g_radial = -g_int . r_hat
    3. Radial bin
    4. Compare to g_N = GM/r^2
    """
    pos = res['pos']
    g_vec = res['g_vec']
    r_arr = res['r_arr']
    boundary = res['boundary']

    # Step 1: subtract external field vector
    g_int_vec = g_vec.copy()
    if g_ext != 0:
        g_int_vec[:, 0] -= g_ext  # external field in x-direction

    # Step 2+3: radial projection and binning
    r_bins, g_radial, g_std, counts = radial_g_profile_vector(
        pos, g_int_vec, r_arr, boundary)
    g_newton = G_eff * M / r_bins ** 2

    # Step 4: enhancement in measurement window
    mask = ((r_bins > r_min) & (r_bins < r_max) &
            (g_radial > 0) & (g_newton > 0))
    if np.sum(mask) < 2:
        return np.nan, np.nan, r_bins, g_radial, g_newton

    enhancement = float(np.mean(g_radial[mask] / g_newton[mask]))

    # Also: |g_int| profile for comparison (old method)
    g_int_mag = np.linalg.norm(g_int_vec, axis=1)
    r_bins_mag, g_mag_profile, _, _ = radial_profile(
        pos, r_arr, g_int_mag, boundary)
    mask_mag = ((r_bins_mag > r_min) & (r_bins_mag < r_max) &
                (g_mag_profile > 0))
    g_newton_mag = G_eff * M / r_bins_mag ** 2
    enh_mag = float(np.mean(g_mag_profile[mask_mag] / g_newton_mag[mask_mag])) \
        if np.sum(mask_mag) > 1 else np.nan

    return enhancement, enh_mag, r_bins, g_radial, g_newton


def run_kt5(g_ext_ratios=None, N=31, M=50.0, G_eff=1.0, a0=2.0,
            output_dir=None):
    if g_ext_ratios is None:
        g_ext_ratios = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT5: EXTERNAL FIELD EFFECT (EFE)")
    print("  v2: vectorial g_int.r_hat measurement")
    print("=" * 60)

    results = []
    for g_ext_ratio in g_ext_ratios:
        g_ext = g_ext_ratio * a0
        print(f"\n  g_ext/a0 = {g_ext_ratio}")

        if g_ext == 0:
            bphi = None
        else:
            bphi = lambda pos, ge=g_ext: -ge * pos[0]

        t0 = time.time()
        res = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0,
                          boundary_phi=bphi, max_iter=500)
        dt = time.time() - t0

        # Raw (total, no subtraction)
        enh_raw, _, _, _ = efe_enhancement(
            res['pos'], res['g_mag'], res['r_arr'], res['boundary'], G_eff, M)

        # v2: vectorial radial projection
        enh_radial, enh_mag, _, _, _ = _measure_efe_vectorial(
            res, G_eff, M, g_ext, a0)

        entry = {
            'g_ext_ratio': g_ext_ratio,
            'g_ext': float(g_ext),
            'enhancement_raw': float(enh_raw) if not np.isnan(enh_raw) else None,
            'enhancement_radial': float(enh_radial) if not np.isnan(enh_radial) else None,
            'enhancement_mag': float(enh_mag) if not np.isnan(enh_mag) else None,
            'converged': res['converged'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    Enhancement (raw |g|):         {enh_raw:.3f}")
        print(f"    Enhancement (g_int . r_hat):   {enh_radial:.3f}")
        print(f"    Enhancement (|g_int| scalar):  {enh_mag:.3f}")
        print(f"    ({dt:.1f}s)")

    # Verdict — use the radial projection method
    enh_0 = next((r['enhancement_radial'] for r in results
                   if r['g_ext_ratio'] == 0.0 and r['enhancement_radial'] is not None),
                  None)
    enh_strong = [r['enhancement_radial'] for r in results
                  if r['g_ext_ratio'] >= 2.0 and r['enhancement_radial'] is not None]

    if enh_0 is not None and enh_strong:
        ratio = min(enh_strong) / enh_0
        if ratio < 0.7:
            efe_status = 'CONFIRMED'
        elif ratio < 0.9:
            efe_status = 'PARTIAL'
        elif ratio > 1.1:
            efe_status = 'ANTI_EFE'
        else:
            efe_status = 'NOT_DETECTED'
    else:
        efe_status = 'INSUFFICIENT_DATA'

    # Also check monotonicity
    radial_vals = [r['enhancement_radial'] for r in results
                   if r['enhancement_radial'] is not None]
    monotone_decreasing = all(radial_vals[i] >= radial_vals[i + 1]
                              for i in range(len(radial_vals) - 1)) \
        if len(radial_vals) >= 2 else None

    verdict = {
        'baseline_enhancement': enh_0,
        'min_strong_enhancement': min(enh_strong) if enh_strong else None,
        'strong_to_baseline_ratio': ratio if (enh_0 and enh_strong) else None,
        'efe_status': efe_status,
        'monotone_decreasing': monotone_decreasing,
        'method': 'vectorial g_int.r_hat projection',
    }

    output = {
        'test': 'KT5',
        'description': 'External Field Effect — v2 vectorial radial projection',
        'params': {'N': N, 'M': M, 'G_eff': G_eff, 'a0': a0},
        'results': results,
        'verdict': verdict,
    }

    outpath = os.path.join(output_dir, 'kt5_efe.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {outpath}")
    print(f"  Verdict: {verdict}")
    return output


if __name__ == '__main__':
    run_kt5()
