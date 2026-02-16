#!/usr/bin/env python3
"""
KT3: Mass Scaling of Transition Radius
========================================
In MOND/AQUAL: r_transition ~ sqrt(GM/a0) ~ sqrt(M).
Does the graph-AQUAL reproduce beta ~ 0.5 in r_trans ~ M^beta?

Uses TWO detection methods:
  1. Ratio-based: first r where g/g_N > threshold
  2. Slope-based: r where local slope crosses -1.5

Output: kt3_mass_scaling.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import (radial_profile, find_transition_radius,
                                 find_transition_radius_slope)


def run_kt3(M_values=None, N=31, G_eff=1.0, a0=2.0, output_dir=None):
    if M_values is None:
        M_values = [10, 25, 50, 100, 200]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT3: MASS SCALING")
    print("=" * 60)

    results = []
    for M in M_values:
        r_pred = np.sqrt(G_eff * M / a0)
        r_src = max(2.0, 1.5 * (M / 50) ** 0.33)
        print(f"\n  M={M}, r_MOND(pred)={r_pred:.2f}")

        t0 = time.time()
        res = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0, r_source=r_src)
        dt = time.time() - t0

        r, g, g_std, counts = radial_profile(
            res['pos'], res['r_arr'], res['g_mag'], res['boundary'])
        g_newton = G_eff * M / r ** 2

        # Method 1: ratio threshold
        r_trans_ratio = find_transition_radius(r, g, g_newton, threshold=1.5)
        # Method 2: slope-based
        r_trans_slope = find_transition_radius_slope(r, g, slope_threshold=-1.5)

        entry = {
            'M': float(M),
            'r_pred': float(r_pred),
            'r_trans_ratio': float(r_trans_ratio) if not np.isnan(r_trans_ratio) else None,
            'r_trans_slope': float(r_trans_slope) if not np.isnan(r_trans_slope) else None,
            'converged': res['converged'],
            'time_s': round(dt, 1),
        }
        results.append(entry)
        print(f"    r_trans (ratio): {r_trans_ratio}")
        print(f"    r_trans (slope): {r_trans_slope}")
        print(f"    r_pred:          {r_pred:.2f}")
        print(f"    ({dt:.1f}s)")

    # Fit power law for each method
    def fit_beta(results, key):
        valid = [(r['M'], r[key]) for r in results if r[key] is not None]
        if len(valid) < 3:
            return None, valid
        Ms = np.array([v[0] for v in valid])
        rt = np.array([v[1] for v in valid])
        if np.all(rt == rt[0]):
            return 0.0, valid
        beta, _ = np.polyfit(np.log10(Ms), np.log10(rt), 1)
        return float(beta), valid

    beta_ratio, _ = fit_beta(results, 'r_trans_ratio')
    beta_slope, _ = fit_beta(results, 'r_trans_slope')

    def judge(beta):
        if beta is None:
            return 'insufficient_data'
        if abs(beta - 0.5) < 0.1:
            return 'PASS'
        if abs(beta - 0.5) < 0.2:
            return 'MARGINAL'
        return 'FAIL'

    verdict = {
        'beta_ratio': beta_ratio,
        'beta_slope': beta_slope,
        'verdict_ratio': judge(beta_ratio),
        'verdict_slope': judge(beta_slope),
        'expected': 0.5,
        'note': 'beta=0 means Lambda-locked transition (not mass-dependent)',
    }

    output = {
        'test': 'KT3',
        'description': 'Mass scaling of transition radius',
        'params': {'N': N, 'G_eff': G_eff, 'a0': a0},
        'results': results,
        'verdict': verdict,
    }

    outpath = os.path.join(output_dir, 'kt3_mass_scaling.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {outpath}")
    print(f"  Verdict: {verdict}")
    return output


if __name__ == '__main__':
    run_kt3()
