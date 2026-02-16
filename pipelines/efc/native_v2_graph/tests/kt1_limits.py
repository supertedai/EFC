#!/usr/bin/env python3
"""
KT1: Newton/MOND Limit Recovery
================================
Does slope -> -2 when g/a0 >> 1 (Newton)?
Does slope -> -1 when g << a0 (MOND)?

Output: kt1_limits.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import radial_profile, measure_slope


def run_kt1(a0_values=None, N=31, M=50.0, G_eff=1.0, output_dir=None):
    if a0_values is None:
        a0_values = [2.0, 0.5, 0.1, 0.01, 0.001]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT1: NEWTON/MOND LIMIT RECOVERY")
    print("=" * 60)

    results = []
    for a0 in a0_values:
        r_mond = np.sqrt(G_eff * M / a0)
        print(f"\n  a0={a0}, r_MOND={r_mond:.1f}")

        t0 = time.time()
        damping = 0.3 if a0 > 0.05 else 0.5
        res = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0, damping=damping)
        dt = time.time() - t0

        r, g, g_std, counts = radial_profile(
            res['pos'], res['r_arr'], res['g_mag'], res['boundary'])

        slope_inner, n_inner = measure_slope(r, g, 3.0, 5.0)
        slope_mid, n_mid = measure_slope(r, g, 5.0, 8.0)
        slope_outer, n_outer = measure_slope(r, g, 8.0, 12.0)

        entry = {
            'a0': a0,
            'r_mond': float(r_mond),
            'slope_inner': float(slope_inner) if not np.isnan(slope_inner) else None,
            'slope_mid': float(slope_mid) if not np.isnan(slope_mid) else None,
            'slope_outer': float(slope_outer) if not np.isnan(slope_outer) else None,
            'converged': res['converged'],
            'iterations': res['iterations'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    slopes: inner={slope_inner:.2f}, mid={slope_mid:.2f}, outer={slope_outer:.2f}")
        print(f"    ({dt:.1f}s)")

    # Verdict
    deep_newton = [r for r in results if r['a0'] <= 0.01]
    newton_ok = all(
        r['slope_mid'] is not None and r['slope_mid'] < -1.9
        for r in deep_newton
    )
    mond_result = next((r for r in results if r['a0'] == max(a0_values)), None)
    mond_ok = (mond_result and mond_result['slope_outer'] is not None and
               mond_result['slope_outer'] > -1.2)

    verdict = {
        'newton_recovery': 'PASS' if newton_ok else 'FAIL',
        'mond_limit': 'PASS' if mond_ok else 'FAIL',
        'overall': 'PASS' if (newton_ok and mond_ok) else 'FAIL',
    }

    output = {
        'test': 'KT1',
        'description': 'Newton/MOND limit recovery',
        'params': {'N': N, 'M': M, 'G_eff': G_eff},
        'results': results,
        'verdict': verdict,
    }

    outpath = os.path.join(output_dir, 'kt1_limits.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {outpath}")
    print(f"  Verdict: {verdict}")
    return output


if __name__ == '__main__':
    run_kt1()
