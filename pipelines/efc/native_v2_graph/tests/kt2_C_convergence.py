#!/usr/bin/env python3
"""
KT2: Prefactor C Convergence
==============================
Does C = g_AQUAL / g_MOND -> 1 as N -> inf?
Or does C stabilize at a grid-specific value?

v2: Tests TWO boundary conditions:
  1. Cubic Dirichlet (original) — may have geometry bias
  2. Spherical mask — only measure within inscribed sphere

If C differs between cubic and spherical, it's a geometry artefact.
If C is the same, it's a real discrete-theory prediction.

Output: kt2_C_convergence.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import radial_profile, measure_slope, measure_prefactor_C


def run_kt2(N_values=None, M=50.0, G_eff=1.0, a0=2.0, output_dir=None):
    if N_values is None:
        N_values = [21, 31, 41]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT2: PREFACTOR C CONVERGENCE")
    print("  v2: compares cubic vs spherical measurement domain")
    print("=" * 60)

    r_mond = np.sqrt(G_eff * M / a0)
    results = []

    for N in N_values:
        print(f"\n  N={N} ({N**3} nodes)")
        t0 = time.time()

        res = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0)
        dt = time.time() - t0

        # --- Full cubic domain (original) ---
        r, g, g_std, counts = radial_profile(
            res['pos'], res['r_arr'], res['g_mag'], res['boundary'])
        g_newton = G_eff * M / r ** 2

        r_out_min = max(r_mond, 5.0)
        r_out_max = N // 2 - 3

        C_cubic, C_std_cubic = measure_prefactor_C(
            r, g, g_newton, a0, r_out_min, r_out_max)
        slope_cubic, _ = measure_slope(r, g, r_out_min, r_out_max)

        # --- Spherical mask: only nodes within inscribed sphere ---
        R_sphere = (N - 1) * 0.5 * 0.8  # 80% of half-width
        sphere_mask = res['r_arr'] > R_sphere
        boundary_sphere = res['boundary'] | sphere_mask

        r_s, g_s, g_std_s, counts_s = radial_profile(
            res['pos'], res['r_arr'], res['g_mag'], boundary_sphere)
        g_newton_s = G_eff * M / r_s ** 2

        r_out_max_s = R_sphere * 0.85
        C_sphere, C_std_sphere = measure_prefactor_C(
            r_s, g_s, g_newton_s, a0, r_out_min, r_out_max_s)
        slope_sphere, _ = measure_slope(r_s, g_s, r_out_min, r_out_max_s)

        entry = {
            'N': N,
            'n_nodes': N ** 3,
            'C_cubic': float(C_cubic) if not np.isnan(C_cubic) else None,
            'C_std_cubic': float(C_std_cubic) if not np.isnan(C_std_cubic) else None,
            'slope_cubic': float(slope_cubic) if not np.isnan(slope_cubic) else None,
            'C_sphere': float(C_sphere) if not np.isnan(C_sphere) else None,
            'C_std_sphere': float(C_std_sphere) if not np.isnan(C_std_sphere) else None,
            'slope_sphere': float(slope_sphere) if not np.isnan(slope_sphere) else None,
            'R_sphere': float(R_sphere),
            'converged': res['converged'],
            'iterations': res['iterations'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    Cubic:   C = {C_cubic:.3f} +/- {C_std_cubic:.3f}, slope = {slope_cubic:.2f}")
        print(f"    Sphere:  C = {C_sphere:.3f} +/- {C_std_sphere:.3f}, slope = {slope_sphere:.2f}")
        print(f"    ({dt:.1f}s)")

    # Verdict
    C_cubic_vals = [r['C_cubic'] for r in results if r['C_cubic'] is not None]
    C_sphere_vals = [r['C_sphere'] for r in results if r['C_sphere'] is not None]

    def interpret_series(vals, label):
        if len(vals) < 2:
            return 'insufficient_data'
        trend = vals[-1] - vals[0]
        if abs(vals[-1] - 1.0) < 0.3:
            return 'converging_to_1'
        elif abs(trend) < 0.05:
            return 'stable_prediction'
        else:
            return 'converging_slowly'

    # Geometry diagnostic: if C_cubic != C_sphere, it's a boundary effect
    geometry_diagnostic = None
    if C_cubic_vals and C_sphere_vals:
        delta_C = abs(C_cubic_vals[-1] - C_sphere_vals[-1])
        if delta_C < 0.05:
            geometry_diagnostic = 'consistent (not geometry artefact)'
        elif delta_C < 0.2:
            geometry_diagnostic = 'minor_geometry_effect'
        else:
            geometry_diagnostic = 'significant_geometry_artefact'

    verdict = {
        'C_cubic_latest': C_cubic_vals[-1] if C_cubic_vals else None,
        'C_sphere_latest': C_sphere_vals[-1] if C_sphere_vals else None,
        'trend_cubic': float(C_cubic_vals[-1] - C_cubic_vals[0]) if len(C_cubic_vals) >= 2 else None,
        'trend_sphere': float(C_sphere_vals[-1] - C_sphere_vals[0]) if len(C_sphere_vals) >= 2 else None,
        'interpretation_cubic': interpret_series(C_cubic_vals, 'cubic'),
        'interpretation_sphere': interpret_series(C_sphere_vals, 'sphere'),
        'geometry_diagnostic': geometry_diagnostic,
    }

    output = {
        'test': 'KT2',
        'description': 'Prefactor C — v2 cubic vs spherical domain',
        'params': {'M': M, 'G_eff': G_eff, 'a0': a0},
        'results': results,
        'verdict': verdict,
    }

    outpath = os.path.join(output_dir, 'kt2_C_convergence.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {outpath}")
    print(f"  Verdict: {verdict}")
    return output


if __name__ == '__main__':
    run_kt2()
