#!/usr/bin/env python3
"""
Bridge B1* Multi-Scale Test on Real HCP Data
==============================================
Instead of individual subjects, we exploit the fact that λ₂ changes
systematically across parcellation scales (68, 100, 200, 300, 360, 400 regions).

This gives us 6 "data points" on the κ vs λ₂ curve — enough to test:
  1. Whether κ scales with 1/(1 + λ₂·τ_c)  [EFC form]
  2. Or just with 1/λ₂                      [generic power-law]
  3. Or linearly                             [trivial]

The key insight: if B1* is correct, the SAME C and τ_c should fit
all scales simultaneously.
"""

import numpy as np
from pathlib import Path
from scipy.linalg import eigh
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

DATA_DIR = Path(__file__).parent / 'real_data'
C_FIXED = 4.4
TAU_C_LIT = 3.5


def load_csv(path):
    return np.loadtxt(path, delimiter=',')


def compute_lambda2(W):
    d = np.sum(W, axis=1)
    d_inv_sqrt = np.zeros_like(d, dtype=float)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    L = 0.5 * (L + L.T)
    eigenvals = eigh(L, eigvals_only=True)
    return np.sort(eigenvals)[1]


def compute_kappa_fc(W_struct, FC):
    """Compute κ using FC coefficient-of-variation as entropy proxy."""
    n = W_struct.shape[0]
    degree = np.sum(W_struct, axis=1)
    sorted_idx = np.argsort(degree)

    hub_idx = sorted_idx[-int(0.10 * n):]
    periph_idx = sorted_idx[:int(0.30 * n)]

    # CV of functional connectivity as entropy proxy
    fc_std = np.std(FC, axis=1)
    fc_mean = np.mean(np.abs(FC), axis=1)
    entropy = fc_std / np.where(fc_mean > 0, fc_mean, 1e-10)

    s_hub = np.mean(entropy[hub_idx])
    s_periph = np.mean(entropy[periph_idx])

    return s_hub / s_periph if s_periph > 0 else np.nan


def compute_kappa_struct(W):
    """Compute κ using log-degree as structural entropy proxy."""
    n = W.shape[0]
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)

    hub_idx = sorted_idx[-int(0.10 * n):]
    periph_idx = sorted_idx[:int(0.30 * n)]

    entropy = np.log1p(degree)
    s_hub = np.mean(entropy[hub_idx])
    s_periph = np.mean(entropy[periph_idx])

    return s_hub / s_periph if s_periph > 0 else np.nan


# ── Models ──
def efc_model(lambda2, tau_c):
    return C_FIXED / (1.0 + lambda2 * tau_c)

def power_model(inv_l2, A, alpha, B):
    return A * np.power(inv_l2, alpha) + B

def linear_model(inv_l2, a, b):
    return a + b * inv_l2


def aic(y, y_pred, k):
    n = len(y)
    sse = np.sum((y - y_pred) ** 2)
    if sse <= 0:
        return -np.inf
    return n * np.log(sse / n) + 2 * k


def bic(y, y_pred, k):
    n = len(y)
    sse = np.sum((y - y_pred) ** 2)
    if sse <= 0:
        return -np.inf
    return n * np.log(sse / n) + k * np.log(n)


def main():
    print("=" * 65)
    print("BRIDGE B1* MULTI-SCALE TEST ON REAL HCP DATA")
    print("6 parcellation scales × 2 entropy proxies")
    print("=" * 65)

    # ── Load all scales ─���
    scales = [
        ('Desikan-68', 'struc_desikan.csv', 'func_desikan.csv'),
        ('Schaefer-100', 'struc_schaefer100.csv', 'func_schaefer100.csv'),
        ('Schaefer-200', 'struc_schaefer200.csv', 'func_schaefer200.csv'),
        ('Schaefer-300', 'struc_schaefer300.csv', 'func_schaefer300.csv'),
        ('Glasser-360', 'strucMatrix_glasser360.csv', 'func_glasser360.csv'),
        ('Schaefer-400', 'struc_schaefer400.csv', 'func_schaefer400.csv'),
    ]

    data = []
    print(f"\n  {'Atlas':<15s} {'N':>4s} {'λ₂':>7s} {'κ_fc':>7s} {'κ_struct':>9s} {'κ_pred':>7s}")
    print(f"  {'─' * 15} {'─' * 4} {'─' * 7} {'─' * 7} {'─' * 9} {'─' * 7}")

    for name, sc_file, fc_file in scales:
        sc_path = DATA_DIR / sc_file
        fc_path = DATA_DIR / fc_file

        if not sc_path.exists():
            # Try alternate names
            alt_sc = DATA_DIR / f'strucMatrix_schaefer{name.split("-")[1]}.csv' if 'Schaefer' in name else None
            if alt_sc and alt_sc.exists():
                sc_path = alt_sc

        if not sc_path.exists():
            print(f"  {name:<15s}  SKIP (no data)")
            continue

        W = load_csv(sc_path)
        n = W.shape[0]
        lambda2 = compute_lambda2(W)

        kappa_struct = compute_kappa_struct(W)

        kappa_fc = np.nan
        if fc_path.exists():
            FC = load_csv(fc_path)
            if FC.shape[0] == n:
                kappa_fc = compute_kappa_fc(W, FC)

        kappa_pred = C_FIXED / (1.0 + lambda2 * TAU_C_LIT)

        data.append({
            'name': name,
            'n': n,
            'lambda2': lambda2,
            'kappa_fc': kappa_fc,
            'kappa_struct': kappa_struct,
            'kappa_pred': kappa_pred,
        })

        fc_str = f"{kappa_fc:.3f}" if not np.isnan(kappa_fc) else "  —"
        print(f"  {name:<15s} {n:>4d} {lambda2:>7.4f} {fc_str:>7s} {kappa_struct:>9.3f} {kappa_pred:>7.3f}")

    if len(data) < 3:
        print("\n  Not enough scales loaded. Aborting.")
        return

    # ── Extract arrays ──
    lambda2_arr = np.array([d['lambda2'] for d in data])
    kappa_struct_arr = np.array([d['kappa_struct'] for d in data])
    kappa_fc_arr = np.array([d['kappa_fc'] for d in data])
    inv_lambda2 = 1.0 / lambda2_arr

    # ── Run model comparison for each proxy ──
    for proxy_name, kappa_arr in [('structural', kappa_struct_arr),
                                   ('FC-based', kappa_fc_arr)]:
        valid = ~np.isnan(kappa_arr)
        if np.sum(valid) < 3:
            continue

        l2 = lambda2_arr[valid]
        kap = kappa_arr[valid]
        inv_l2 = 1.0 / l2
        n_pts = len(kap)

        print(f"\n{'━' * 65}")
        print(f"  MODEL COMPARISON — {proxy_name} proxy (n={n_pts} scales)")
        print(f"{'━' * 65}")

        # Correlation
        r_val, p_val = pearsonr(kap, inv_l2)
        print(f"\n  Pearson r(κ, 1/λ₂) = {r_val:.3f}  (p = {p_val:.4f})")

        # EFC fixed (0 params)
        kap_efc_fixed = C_FIXED / (1.0 + l2 * TAU_C_LIT)
        aic_efc0 = aic(kap, kap_efc_fixed, 0)
        bic_efc0 = bic(kap, kap_efc_fixed, 0)
        rmse_efc0 = np.sqrt(np.mean((kap - kap_efc_fixed) ** 2))
        r2_efc0 = 1 - np.sum((kap - kap_efc_fixed)**2) / np.sum((kap - np.mean(kap))**2)

        print(f"\n  {'Model':<40s} {'k':>2s} {'AIC':>8s} {'BIC':>8s} {'R²':>7s} {'RMSE':>7s}")
        print(f"  {'─' * 40} {'─' * 2} {'─' * 8} {'─' * 8} {'─' * 7} {'─' * 7}")
        print(f"  {'EFC fixed (C=4.4, τ_c=3.5)':<40s} {0:>2d} {aic_efc0:>8.2f} {bic_efc0:>8.2f} {r2_efc0:>7.3f} {rmse_efc0:>7.4f}")

        # EFC fit τ_c (1 param)
        try:
            popt, pcov = curve_fit(efc_model, l2, kap, p0=[3.5], bounds=(0.01, 100))
            tau_fit = popt[0]
            tau_err = np.sqrt(pcov[0, 0])
            kap_efc_fit = efc_model(l2, tau_fit)
            aic_efc1 = aic(kap, kap_efc_fit, 1)
            bic_efc1 = bic(kap, kap_efc_fit, 1)
            rmse_efc1 = np.sqrt(np.mean((kap - kap_efc_fit) ** 2))
            r2_efc1 = 1 - np.sum((kap - kap_efc_fit)**2) / np.sum((kap - np.mean(kap))**2)
            print(f"  {'EFC fit (C=4.4, τ_c=' + f'{tau_fit:.1f}±{tau_err:.1f})':<40s} {1:>2d} {aic_efc1:>8.2f} {bic_efc1:>8.2f} {r2_efc1:>7.3f} {rmse_efc1:>7.4f}")
        except RuntimeError:
            print(f"  EFC fit: FAILED")

        # Linear (2 params)
        try:
            popt_lin, _ = curve_fit(linear_model, inv_l2, kap, p0=[1, 0.01])
            kap_lin = linear_model(inv_l2, *popt_lin)
            aic_lin = aic(kap, kap_lin, 2)
            bic_lin = bic(kap, kap_lin, 2)
            rmse_lin = np.sqrt(np.mean((kap - kap_lin) ** 2))
            r2_lin = 1 - np.sum((kap - kap_lin)**2) / np.sum((kap - np.mean(kap))**2)
            print(f"  {'Linear (a=' + f'{popt_lin[0]:.3f}, b={popt_lin[1]:.4f})':<40s} {2:>2d} {aic_lin:>8.2f} {bic_lin:>8.2f} {r2_lin:>7.3f} {rmse_lin:>7.4f}")
        except RuntimeError:
            print(f"  Linear: FAILED")

        # Power-law (3 params)
        try:
            popt_pow, _ = curve_fit(power_model, inv_l2, kap, p0=[0.1, 0.5, 1.0], maxfev=10000)
            kap_pow = power_model(inv_l2, *popt_pow)
            aic_pow = aic(kap, kap_pow, 3)
            bic_pow = bic(kap, kap_pow, 3)
            rmse_pow = np.sqrt(np.mean((kap - kap_pow) ** 2))
            r2_pow = 1 - np.sum((kap - kap_pow)**2) / np.sum((kap - np.mean(kap))**2)
            print(f"  {'Power-law (3 params)':<40s} {3:>2d} {aic_pow:>8.2f} {bic_pow:>8.2f} {r2_pow:>7.3f} {rmse_pow:>7.4f}")
        except RuntimeError:
            print(f"  Power-law: FAILED")

    # ── Final verdict ──
    print(f"\n{'═' * 65}")
    print("  VERDICT")
    print(f"{'═' * 65}")
    print()
    print("  Key questions answered by this test:")
    print("  1. Is κ > 1 across all scales? (centrifugal gradient exists?)")
    print("  2. Does κ scale with λ₂? (network connectivity matters?)")
    print("  3. Does the EFC form fit better than generic alternatives?")
    print("  4. Is τ_c from fit consistent with literature (3.5s)?")

    # Save
    output_path = DATA_DIR / 'results_multiscale.json'
    with open(output_path, 'w') as f:
        json.dump([{k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                    for k, v in d.items()} for d in data], f, indent=2)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
