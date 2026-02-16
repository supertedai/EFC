#!/usr/bin/env python3
"""
KT4: Superposition Test
========================
AQUAL is nonlinear: Phi(M1+M2) != Phi(M1) + Phi(M2).
The violation must be smooth and systematic, not noisy.

Output: kt4_superposition.json
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kernel.solver import solve_aqual
from kernel.observables import superposition_violation, radial_profile


def run_kt4(N=31, G_eff=1.0, a0=2.0, M_A=30.0, M_B=30.0, d=4.0,
            output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'runs')
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("KT4: SUPERPOSITION TEST")
    print("=" * 60)

    pos_A = [-d, 0, 0]
    pos_B = [+d, 0, 0]
    print(f"  M_A={M_A} at x=-{d}, M_B={M_B} at x=+{d}, a0={a0}")

    # A alone
    print("\n  Solving A alone...")
    t0 = time.time()
    res_A = solve_aqual(N, [(pos_A, M_A)], G_eff, a0)
    print(f"    ({time.time() - t0:.1f}s)")

    # B alone
    print("  Solving B alone...")
    t0 = time.time()
    res_B = solve_aqual(N, [(pos_B, M_B)], G_eff, a0)
    print(f"    ({time.time() - t0:.1f}s)")

    # A+B together
    print("  Solving A+B together...")
    t0 = time.time()
    res_AB = solve_aqual(N, [(pos_A, M_A), (pos_B, M_B)], G_eff, a0)
    print(f"    ({time.time() - t0:.1f}s)")

    # Measure violation
    sv = superposition_violation(res_AB['Phi'], res_A['Phi'], res_B['Phi'],
                                 res_AB['boundary'])

    # Smoothness along x-axis
    pos = res_AB['pos']
    x_axis = ((np.abs(pos[:, 1]) < 0.5) & (np.abs(pos[:, 2]) < 0.5) &
              (~res_AB['boundary']))
    x_vals = pos[x_axis, 0]
    sort_idx = np.argsort(x_vals)
    delta_profile = sv['delta_Phi'][x_axis][sort_idx]

    noise_ratio = None
    if len(delta_profile) > 5:
        noise_ratio = float(np.std(np.diff(delta_profile)) /
                           (np.std(delta_profile) + 1e-30))

    print(f"\n  RMS(dPhi)/Phi_max = {sv['rms_normalized']:.4e}")
    print(f"  max|dPhi|/Phi_max = {sv['max_normalized']:.4e}")
    if noise_ratio is not None:
        print(f"  Noise ratio: {noise_ratio:.3f}")

    smooth = noise_ratio is not None and noise_ratio < 2.0
    nonzero = float(sv['rms_normalized']) > 1e-6

    verdict = {
        'rms_normalized': float(sv['rms_normalized']),
        'max_normalized': float(sv['max_normalized']),
        'noise_ratio': float(noise_ratio) if noise_ratio is not None else None,
        'smooth': bool(smooth),
        'nonzero': bool(nonzero),
        'overall': 'PASS' if (smooth and nonzero) else 'FAIL',
    }

    output = {
        'test': 'KT4',
        'description': 'Superposition violation (nonlinear coupling)',
        'params': {'N': N, 'G_eff': G_eff, 'a0': a0,
                   'M_A': M_A, 'M_B': M_B, 'd': d},
        'verdict': verdict,
    }

    outpath = os.path.join(output_dir, 'kt4_superposition.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {outpath}")
    print(f"  Verdict: {verdict}")
    return output


if __name__ == '__main__':
    run_kt4()
