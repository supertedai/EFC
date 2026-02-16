#!/usr/bin/env python3
"""
KT2: Prefactor C Convergence
==============================
Does C = g_AQUAL / g_MOND -> 1 as N -> inf?
Or does C stabilize at a grid-specific value?

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
    print("=" * 60)

    r_mond = np.sqrt(G_eff * M / a0)
    results = []

    for N in N_values:
        print(f"\n  N={N} ({N**3} nodes)")
        t0 = time.time()

        res_vw = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0)
        dt = time.time() - t0

        r, g, g_std, counts = radial_profile(
            res_vw['pos'], res_vw['r_arr'], res_vw['g_mag'], res_vw['boundary'])
        g_newton = G_eff * M / r ** 2

        r_out_min = max(r_mond, 5.0)
        r_out_max = N // 2 - 3

        C, C_std = measure_prefactor_C(r, g, g_newton, a0, r_out_min, r_out_max)
        slope, _ = measure_slope(r, g, r_out_min, r_out_max)

        entry = {
            'N': N,
            'n_nodes': N ** 3,
            'C': float(C) if not np.isnan(C) else None,
            'C_std': float(C_std) if not np.isnan(C_std) else None,
            'slope_outer': float(slope) if not np.isnan(slope) else None,
            'converged': res_vw['converged'],
            'iterations': res_vw['iterations'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    C = {C:.3f} +/- {C_std:.3f}, slope = {slope:.2f}")
        print(f"    ({dt:.1f}s)")

    # Verdict
    C_vals = [r['C'] for r in results if r['C'] is not None]
    if len(C_vals) >= 2:
        trend = C_vals[-1] - C_vals[0]
        if abs(C_vals[-1] - 1.0) < 0.3:
            interpretation = 'converging_to_1'
        elif abs(trend) < 0.05:
            interpretation = 'stable_grid_prediction'
        else:
            interpretation = 'converging_slowly'
    else:
        interpretation = 'insufficient_data'

    verdict = {
        'C_latest': C_vals[-1] if C_vals else None,
        'trend': float(C_vals[-1] - C_vals[0]) if len(C_vals) >= 2 else None,
        'interpretation': interpretation,
    }

    output = {
        'test': 'KT2',
        'description': 'Prefactor C convergence with grid size',
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
