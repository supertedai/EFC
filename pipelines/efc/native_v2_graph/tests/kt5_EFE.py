#!/usr/bin/env python3
"""
KT5: External Field Effect (EFE)
==================================
In MOND/AQUAL, an external uniform field g_ext partially restores
Newtonian dynamics where internal g < a0.

Measurement strategy:
  - Subtract external field contribution from total g
  - Measure INTERNAL enhancement only
  - Compare: does internal MOND enhancement decrease with g_ext?

Output: kt5_efe.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import radial_profile, efe_enhancement


def _measure_internal_enhancement(res, G_eff, M, g_ext, a0,
                                  r_min=6.0, r_max=12.0):
    """
    Measure enhancement after subtracting external field component.

    The external field adds a uniform gradient g_ext in x-direction.
    Total g_measured = g_internal + g_ext_component.
    We need to isolate g_internal.

    Strategy: decompose g_vec into radial and external components,
    then measure radial part only.
    """
    pos = res['pos']
    g_vec = res['g_vec']
    r_arr = res['r_arr']
    boundary = res['boundary']

    # Subtract uniform external field
    g_internal = g_vec.copy()
    if g_ext != 0:
        g_internal[:, 0] -= g_ext  # external field is in x-direction

    g_internal_mag = np.linalg.norm(g_internal, axis=1)

    # Radial profile of internal |g|
    r_bins, g_profile, _, _ = radial_profile(
        pos, r_arr, g_internal_mag, boundary)
    g_newton = G_eff * M / r_bins ** 2

    mask = (r_bins > r_min) & (r_bins < r_max) & (g_profile > 0) & (g_newton > 0)
    if np.sum(mask) < 2:
        return np.nan, np.nan, r_bins, g_profile

    enhancement = float(np.mean(g_profile[mask] / g_newton[mask]))

    # Also measure along x-axis (with and against ext field)
    mask_px = ((pos[:, 0] > 0) & (np.abs(pos[:, 1]) < 0.5) &
               (np.abs(pos[:, 2]) < 0.5) & (~boundary))
    mask_nx = ((pos[:, 0] < 0) & (np.abs(pos[:, 1]) < 0.5) &
               (np.abs(pos[:, 2]) < 0.5) & (~boundary))
    g_px = float(np.mean(g_internal_mag[mask_px])) if np.sum(mask_px) > 0 else np.nan
    g_nx = float(np.mean(g_internal_mag[mask_nx])) if np.sum(mask_nx) > 0 else np.nan
    asymmetry = (g_px - g_nx) / (0.5 * (g_px + g_nx)) if (g_px + g_nx) > 0 else 0.0

    return enhancement, float(asymmetry), r_bins, g_profile


def run_kt5(g_ext_ratios=None, N=31, M=50.0, G_eff=1.0, a0=2.0,
            output_dir=None):
    if g_ext_ratios is None:
        g_ext_ratios = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT5: EXTERNAL FIELD EFFECT (EFE)")
    print("  Corrected: subtracts g_ext before measuring enhancement")
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

        # Raw (total) enhancement
        enh_raw, _, _, _ = efe_enhancement(
            res['pos'], res['g_mag'], res['r_arr'], res['boundary'], G_eff, M)

        # Corrected (internal) enhancement
        enh_int, asym, _, _ = _measure_internal_enhancement(
            res, G_eff, M, g_ext, a0)

        entry = {
            'g_ext_ratio': g_ext_ratio,
            'g_ext': float(g_ext),
            'enhancement_raw': float(enh_raw) if not np.isnan(enh_raw) else None,
            'enhancement_internal': float(enh_int) if not np.isnan(enh_int) else None,
            'asymmetry': float(asym) if not np.isnan(asym) else None,
            'converged': res['converged'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    Enhancement (raw):      {enh_raw:.3f}")
        print(f"    Enhancement (internal): {enh_int:.3f}")
        print(f"    Asymmetry:              {asym:.3f}")
        print(f"    ({dt:.1f}s)")

    # Verdict
    enh_0 = next((r['enhancement_internal'] for r in results
                   if r['g_ext_ratio'] == 0.0), None)
    enh_strong = [r['enhancement_internal'] for r in results
                  if r['g_ext_ratio'] >= 2.0 and r['enhancement_internal'] is not None]

    if enh_0 is not None and enh_strong:
        if min(enh_strong) < enh_0 * 0.7:
            efe_status = 'CONFIRMED'
        elif min(enh_strong) < enh_0 * 0.9:
            efe_status = 'PARTIAL'
        else:
            efe_status = 'NOT_DETECTED'
    else:
        efe_status = 'INSUFFICIENT_DATA'

    verdict = {
        'baseline_enhancement': enh_0,
        'min_strong_enhancement': min(enh_strong) if enh_strong else None,
        'efe_status': efe_status,
        'note': 'Uses internal field (g_ext subtracted) for measurement',
    }

    output = {
        'test': 'KT5',
        'description': 'External Field Effect with g_ext subtraction',
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
