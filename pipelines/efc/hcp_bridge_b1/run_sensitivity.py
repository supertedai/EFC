#!/usr/bin/env python3
"""
Sensitivity Analysis for Paper A
==================================
Tests robustness of κ to hub/periphery threshold choice.
"""

import numpy as np
from pathlib import Path
from scipy.linalg import eigh

DATA_DIR = Path(__file__).parent / 'real_data'


def load_csv(path):
    return np.loadtxt(path, delimiter=',')


def compute_kappa(W, FC, hub_pct, periph_pct):
    n = W.shape[0]
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)
    hub_idx = sorted_idx[-max(1, int(hub_pct * n)):]
    periph_idx = sorted_idx[:max(1, int(periph_pct * n))]

    # FC-CV proxy
    fc_std = np.std(FC, axis=1)
    fc_mean = np.mean(np.abs(FC), axis=1)
    cv = fc_std / np.where(fc_mean > 0, fc_mean, 1e-10)
    s_hub = np.mean(cv[hub_idx])
    s_periph = np.mean(cv[periph_idx])
    kappa_fc = s_hub / s_periph if s_periph > 0 else np.nan

    # Structural proxy
    log_deg = np.log1p(degree)
    s_hub_s = np.mean(log_deg[hub_idx])
    s_periph_s = np.mean(log_deg[periph_idx])
    kappa_struct = s_hub_s / s_periph_s if s_periph_s > 0 else np.nan

    return kappa_fc, kappa_struct


def main():
    print("=" * 65)
    print("SENSITIVITY ANALYSIS: κ vs Hub/Periphery Thresholds")
    print("=" * 65)

    # Use Schaefer-200 as reference
    W = load_csv(DATA_DIR / 'struc_schaefer200.csv')
    FC = load_csv(DATA_DIR / 'func_schaefer200.csv')

    hub_pcts = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]
    periph_pcts = [0.20, 0.25, 0.30, 0.35, 0.40]

    print(f"\n  Atlas: Schaefer-200 (n=200)")
    print(f"\n  κ (FC-CV proxy):")
    print(f"  {'':>10s}", end='')
    for pp in periph_pcts:
        print(f"  P={pp:.0%}", end='')
    print()

    fc_values = []
    for hp in hub_pcts:
        print(f"  H={hp:.0%}   ", end='')
        for pp in periph_pcts:
            kfc, _ = compute_kappa(W, FC, hp, pp)
            fc_values.append(kfc)
            print(f"  {kfc:.3f}", end='')
        print()

    fc_arr = np.array([v for v in fc_values if not np.isnan(v)])
    print(f"\n  Range: [{fc_arr.min():.3f}, {fc_arr.max():.3f}]")
    print(f"  Mean:  {fc_arr.mean():.3f}")
    print(f"  CV:    {fc_arr.std()/fc_arr.mean()*100:.1f}%")
    print(f"  All > 1.0: {np.all(fc_arr > 1.0)}")

    print(f"\n  κ (structural proxy):")
    print(f"  {'':>10s}", end='')
    for pp in periph_pcts:
        print(f"  P={pp:.0%}", end='')
    print()

    struct_values = []
    for hp in hub_pcts:
        print(f"  H={hp:.0%}   ", end='')
        for pp in periph_pcts:
            _, ks = compute_kappa(W, FC, hp, pp)
            struct_values.append(ks)
            print(f"  {ks:.3f}", end='')
        print()

    s_arr = np.array([v for v in struct_values if not np.isnan(v)])
    print(f"\n  Range: [{s_arr.min():.3f}, {s_arr.max():.3f}]")
    print(f"  Mean:  {s_arr.mean():.3f}")
    print(f"  CV:    {s_arr.std()/s_arr.mean()*100:.1f}%")
    print(f"  All > 1.0: {np.all(s_arr > 1.0)}")

    # Cross-atlas sensitivity at fixed thresholds (10%/30%)
    print(f"\n{'━' * 65}")
    print("  CROSS-ATLAS (hub=10%, periph=30%)")
    print(f"{'━' * 65}")

    scales = [
        ('Desikan-68', 'struc_desikan.csv', 'func_desikan.csv'),
        ('Schaefer-100', 'struc_schaefer100.csv', 'func_schaefer100.csv'),
        ('Schaefer-200', 'struc_schaefer200.csv', 'func_schaefer200.csv'),
        ('Schaefer-300', 'struc_schaefer300.csv', 'func_schaefer300.csv'),
        ('Glasser-360', 'strucMatrix_glasser360.csv', 'func_glasser360.csv'),
        ('Schaefer-400', 'struc_schaefer400.csv', 'func_schaefer400.csv'),
    ]

    print(f"\n  {'Atlas':<15s} {'κ_fc':>7s} {'κ_struct':>9s}")
    print(f"  {'─'*15} {'─'*7} {'─'*9}")

    for name, sc, fc in scales:
        sc_path = DATA_DIR / sc
        fc_path = DATA_DIR / fc
        if not sc_path.exists() or not fc_path.exists():
            continue
        W = load_csv(sc_path)
        FC = load_csv(fc_path)
        kfc, ks = compute_kappa(W, FC, 0.10, 0.30)
        print(f"  {name:<15s} {kfc:>7.3f} {ks:>9.3f}")

    print(f"\n  CONCLUSION:")
    if np.all(s_arr > 1.0):
        print(f"  ✓ Structural κ > 1 for ALL threshold combinations")
    else:
        print(f"  ⚠ Structural κ < 1 for some thresholds")

    fc_above_1 = np.sum(fc_arr > 1.0) / len(fc_arr) * 100
    print(f"  FC-based κ > 1 for {fc_above_1:.0f}% of threshold combinations")


if __name__ == "__main__":
    main()
