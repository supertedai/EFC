#!/usr/bin/env python3
"""
KT2: Legacy Fixed-h Domain-Size Trend
=====================================
This legacy test compares two measurement masks on the same cubic graph.
N increases while h=1 stays fixed, so the physical box grows; the radial
window also changes with N. This is not a continuum-limit or C-convergence
test. Use KT6 for matched-box physical normalization and common-bin C(r).

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


def fixed_h_convergence_status(values, spacing=1.0):
    """Label an N-sweep that holds h fixed without implying a continuum limit."""
    if len(values) < 2:
        return "insufficient_data"
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    return "fixed_h_domain_size_trend_only"


def run_kt2(N_values=None, M=50.0, G_eff=1.0, a0=2.0, output_dir=None):
    if N_values is None:
        N_values = [21, 31, 41]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT2: LEGACY FIXED-H DOMAIN-SIZE TREND")
    print("  compares two radial measurement masks on one cubic graph")
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
            'spacing': 1.0,
            'physical_box_side': float(N - 1),
            'C_window_cubic': [float(r_out_min), float(r_out_max)],
            'C_window_spherical': [float(r_out_min), float(r_out_max_s)],
            'C_cubic': float(C_cubic) if not np.isnan(C_cubic) else None,
            'C_std_cubic': float(C_std_cubic) if not np.isnan(C_std_cubic) else None,
            'slope_cubic': float(slope_cubic) if not np.isnan(slope_cubic) else None,
            'C_sphere': float(C_sphere) if not np.isnan(C_sphere) else None,
            'C_std_sphere': float(C_std_sphere) if not np.isnan(C_std_sphere) else None,
            'C_spread_semantics': 'radial-bin spread, not uncertainty on C_infinity',
            'slope_sphere': float(slope_sphere) if not np.isnan(slope_sphere) else None,
            'R_sphere': float(R_sphere),
            'converged': res['converged'],
            'iterations': res['iterations'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    Cubic:   C = {C_cubic:.3f} (radial-bin spread {C_std_cubic:.3f}), slope = {slope_cubic:.2f}")
        print(f"    Sphere:  C = {C_sphere:.3f} (radial-bin spread {C_std_sphere:.3f}), slope = {slope_sphere:.2f}")
        print(f"    ({dt:.1f}s)")

    # Verdict
    C_cubic_vals = [r['C_cubic'] for r in results if r['C_cubic'] is not None]
    C_sphere_vals = [r['C_sphere'] for r in results if r['C_sphere'] is not None]

    # N grows at fixed h=1, so this can only describe domain-size behavior.
    interpretation_cubic = fixed_h_convergence_status(C_cubic_vals, spacing=1.0)
    interpretation_sphere = fixed_h_convergence_status(C_sphere_vals, spacing=1.0)

    # Both profiles use the same cubic graph; the sphere changes only the
    # measurement mask and cannot diagnose graph topology or a boundary law.
    measurement_mask_comparison = (
        'same_cubic_graph_different_measurement_masks_only'
        if C_cubic_vals and C_sphere_vals else 'insufficient_data'
    )
    delta_C_masks = (
        abs(C_cubic_vals[-1] - C_sphere_vals[-1])
        if C_cubic_vals and C_sphere_vals else None
    )

    verdict = {
        'C_cubic_latest': C_cubic_vals[-1] if C_cubic_vals else None,
        'C_sphere_latest': C_sphere_vals[-1] if C_sphere_vals else None,
        'trend_cubic': float(C_cubic_vals[-1] - C_cubic_vals[0]) if len(C_cubic_vals) >= 2 else None,
        'trend_sphere': float(C_sphere_vals[-1] - C_sphere_vals[0]) if len(C_sphere_vals) >= 2 else None,
        'interpretation_cubic': interpretation_cubic,
        'interpretation_sphere': interpretation_sphere,
        'continuum_limit_established': False,
        'measurement_mask_comparison': measurement_mask_comparison,
        'delta_C_masks': delta_C_masks,
        'reason': 'spacing is fixed at 1 and physical box/radial windows vary with N',
    }

    output = {
        'test': 'KT2',
        'description': 'Fixed-h domain-size trend; two measurement masks on the same cubic graph',
        'params': {'M': M, 'G_eff': G_eff, 'a0': a0, 'spacing': 1.0},
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
