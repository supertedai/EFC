#!/usr/bin/env python3
"""
Grid-AQUAL v0.1: Systematic Convergence & Kill-Tests
=====================================================
Three critical tests from GPT analysis:
  KILL-TEST 1: Newton recovery (deep UV)
    - Lower a0 so g/a0 >> 1 everywhere, slope must approach -2
  KILL-TEST 2: Prefactor C ~ 2.3 convergence
    - Scan N = {21, 31, 41}, volume-weighted vs unweighted binning
    - Does C approach 1 as N grows?
  KILL-TEST 3: Mass-scaling of transition radius
    - M = {10, 25, 50, 100, 200}, fixed a0
    - r_transition proportional to sqrt(M) without retuning?
Author: Morten Magnusson / Symbiose
Date:   2026-02-16
"""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LATTICE
# ============================================================

def build_cubic_lattice(N, spacing=1.0):
    n_nodes = N**3
    positions = np.zeros((n_nodes, 3))
    adjacency = [[] for _ in range(n_nodes)]

    def idx(x, y, z):
        return x * N * N + y * N + z

    for x in range(N):
        for y in range(N):
            for z in range(N):
                i = idx(x, y, z)
                positions[i] = [x * spacing, y * spacing, z * spacing]
                for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
                    nx_, ny_, nz_ = x+dx, y+dy, z+dz
                    if 0 <= nx_ < N and 0 <= ny_ < N and 0 <= nz_ < N:
                        j = idx(nx_, ny_, nz_)
                        adjacency[i].append(j)

    degree = np.array([len(adj) for adj in adjacency])
    center = (N-1) * spacing / 2
    positions -= center
    return positions, adjacency, degree


def mu_aqual(x):
    """Standard MOND interpolation: mu(x) = x / sqrt(1 + x^2)"""
    return x / np.sqrt(1.0 + x**2)


# ============================================================
# SOLVER
# ============================================================

def solve_discrete_aqual(N, M_source, G_eff, a0, r_source=2.0,
                         spacing=1.0, max_iter=400, tol=1e-5,
                         damping=0.5, boundary_margin=1.5,
                         volume_weighted=True, quiet=False):
    pos, adj, deg = build_cubic_lattice(N, spacing)
    n = N**3
    r_arr = np.linalg.norm(pos, axis=1)

    # Source
    rhs = np.zeros(n)
    for i in range(n):
        if r_arr[i] < r_source:
            vol = (4/3) * np.pi * r_source**3
            rhs[i] = 4 * np.pi * G_eff * M_source / vol

    # Boundary
    r_max = np.max(r_arr)
    boundary = r_arr > (r_max - boundary_margin * spacing)

    # Initial linear Poisson
    A_lin = lil_matrix((n, n))
    for i in range(n):
        A_lin[i, i] = float(deg[i])
        for j in adj[i]:
            A_lin[i, j] = -1.0
    A_lin_csr = A_lin.tocsr()

    rhs_bc = rhs.copy()
    for i in np.where(boundary)[0]:
        A_lin_csr[i, :] = 0
        A_lin_csr[i, i] = 1.0
        rhs_bc[i] = 0.0
    Phi = spsolve(A_lin_csr, rhs_bc)

    # Picard iteration
    converged_flag = False
    change = 1.0
    for iteration in range(max_iter):
        Phi_old = Phi.copy()

        A_mat = lil_matrix((n, n))
        for i in range(n):
            if boundary[i]:
                A_mat[i, i] = 1.0
                continue
            diag = 0.0
            for j in adj[i]:
                dPhi = abs(Phi[i] - Phi[j])
                x = dPhi / (a0 * spacing) if a0 > 0 else 1e10
                w = max(mu_aqual(x), 1e-6)
                A_mat[i, j] = -w
                diag += w
            A_mat[i, i] = diag

        A_csr = A_mat.tocsr()
        rhs_iter = rhs.copy()
        for i in np.where(boundary)[0]:
            rhs_iter[i] = 0.0

        Phi_new = spsolve(A_csr, rhs_iter)
        Phi = (1 - damping) * Phi_old + damping * Phi_new

        change = np.max(np.abs(Phi - Phi_old)) / (np.max(np.abs(Phi)) + 1e-10)
        if change < tol:
            converged_flag = True
            break

    if not quiet:
        tag = "CONVERGED" if converged_flag else f"NOT CONVERGED ({change:.2e})"
        print(f"    N={N}, a0={a0}, M={M_source}: {iteration+1} iters, {tag}")

    # Gravity
    g_mag = np.zeros(n)
    for i in range(n):
        gvec = np.zeros(3)
        for j in adj[i]:
            dr = pos[j] - pos[i]
            dist = np.linalg.norm(dr)
            dPhi = Phi[i] - Phi[j]
            if dist > 0:
                gvec += dPhi * dr / dist**2
        g_mag[i] = np.linalg.norm(gvec)

    # Radial binning
    r_bins = np.arange(2.5, N//2 - 2, 1.0)
    g_binned = np.zeros(len(r_bins))
    g_std = np.zeros(len(r_bins))
    Phi_binned = np.zeros(len(r_bins))
    counts = np.zeros(len(r_bins), dtype=int)

    for k, rb in enumerate(r_bins):
        mask = (r_arr > rb - 0.5) & (r_arr < rb + 0.5) & (~boundary)
        cnt = np.sum(mask)
        if cnt > 0:
            if volume_weighted:
                weights = 1.0 / (4 * np.pi * r_arr[mask]**2 + 1e-10)
                weights /= np.sum(weights)
                g_binned[k] = np.sum(weights * g_mag[mask])
                Phi_binned[k] = np.sum(weights * Phi[mask])
            else:
                g_binned[k] = np.mean(g_mag[mask])
                Phi_binned[k] = np.mean(Phi[mask])
            g_std[k] = np.std(g_mag[mask])
            counts[k] = cnt

    g_newton = G_eff * M_source / r_bins**2

    return {
        'r': r_bins, 'g': g_binned, 'g_std': g_std,
        'g_newton': g_newton, 'Phi': Phi_binned,
        'iterations': iteration + 1, 'converged': converged_flag,
        'counts': counts, 'N': N, 'a0': a0, 'M': M_source
    }


# ============================================================
# HELPERS
# ============================================================

def measure_slope(r, g, r_min, r_max):
    mask = (r > r_min) & (r < r_max) & (g > 0)
    n_pts = int(np.sum(mask))
    if n_pts < 3:
        return np.nan, n_pts
    coeffs = np.polyfit(np.log10(r[mask]), np.log10(g[mask]), 1)
    return coeffs[0], n_pts


def measure_prefactor_C(r, g, g_newton, a0, r_min, r_max):
    mask = (r > r_min) & (r < r_max) & (g > 0) & (g_newton > 0)
    if np.sum(mask) < 2:
        return np.nan, np.nan
    g_mond = np.sqrt(a0 * g_newton[mask])
    C_vals = g[mask] / g_mond
    return float(np.mean(C_vals)), float(np.std(C_vals))


def find_transition_radius(r, g, g_newton, threshold=1.5):
    mask = (g > 0) & (g_newton > 0) & (r > 3)
    if np.sum(mask) < 2:
        return np.nan
    ratio = g[mask] / g_newton[mask]
    r_valid = r[mask]
    idx = np.where(ratio > threshold)[0]
    if len(idx) == 0:
        return np.nan
    return float(r_valid[idx[0]])


# ============================================================
# KILL-TEST 1: Newton Recovery
# ============================================================

def kill_test_1():
    print("\n" + "=" * 70)
    print("KILL-TEST 1: NEWTON RECOVERY")
    print("  Does slope -> -2 when g/a0 >> 1?")
    print("=" * 70)

    N = 31; M = 50.0; G_eff = 1.0
    a0_values = [2.0, 0.5, 0.1, 0.01, 0.001]

    results = []
    for a0 in a0_values:
        r_mond = np.sqrt(G_eff * M / a0)
        print(f"\n  a0 = {a0}, r_MOND = {r_mond:.1f}")

        t0 = time.time()
        res = solve_discrete_aqual(N, M, G_eff, a0,
                                   damping=0.3 if a0 > 0.05 else 0.5,
                                   max_iter=500, tol=1e-4)
        dt = time.time() - t0

        slope_inner, _ = measure_slope(res['r'], res['g'], 3.0, 5.0)
        slope_mid, _ = measure_slope(res['r'], res['g'], 5.0, 8.0)
        slope_outer, _ = measure_slope(res['r'], res['g'], 8.0, 12.0)

        mask_r3 = (res['r'] > 2.5) & (res['r'] < 3.5) & (res['g'] > 0)
        g_at_3 = res['g'][mask_r3][0] if np.any(mask_r3) else 0
        g_over_a0 = g_at_3 / a0 if a0 > 0 else np.inf

        results.append({
            'a0': a0, 'r_mond': r_mond,
            'slope_inner': slope_inner, 'slope_mid': slope_mid,
            'slope_outer': slope_outer, 'g_over_a0': g_over_a0,
            'time': dt, 'res': res
        })
        print(f"    g(r=3)/a0 = {g_over_a0:.1f}")
        print(f"    Slopes: inner={slope_inner:.2f}, mid={slope_mid:.2f}, outer={slope_outer:.2f}")
        print(f"    ({dt:.1f}s)")

    print(f"\n  {'a0':<8} {'r_MOND':<8} {'g/a0':<12} {'inner':<10} {'outer':<10} {'OK?'}")
    print(f"  {'-'*56}")
    for r in results:
        ok = r['slope_inner'] < -1.7 if r['g_over_a0'] > 10 else True
        print(f"  {r['a0']:<8.3f} {r['r_mond']:<8.1f} {r['g_over_a0']:<12.1f} "
              f"{r['slope_inner']:<10.2f} {r['slope_outer']:<10.2f} "
              f"{'PASS' if ok else 'FAIL'}")

    deep = [r for r in results if r['g_over_a0'] > 30]
    if deep:
        s = [r['slope_inner'] for r in deep]
        if all(x < -1.7 for x in s):
            print(f"\n  >>> KT1 PASSED: Newton recovery (slopes {[f'{x:.2f}' for x in s]})")
        else:
            print(f"\n  >>> KT1 FAILED: slopes {[f'{x:.2f}' for x in s]} not -> -2")
    return results


# ============================================================
# KILL-TEST 2: Prefactor Convergence
# ============================================================

def kill_test_2():
    print("\n" + "=" * 70)
    print("KILL-TEST 2: PREFACTOR C CONVERGENCE")
    print("  Does C = g_AQUAL / g_MOND -> 1 as N -> inf?")
    print("=" * 70)

    M = 50.0; G_eff = 1.0; a0 = 2.0
    N_values = [21, 31, 41]
    results_vw = []; results_nw = []

    for N in N_values:
        print(f"\n  --- N = {N} ({N**3} nodes) ---")

        t0 = time.time()
        res_vw = solve_discrete_aqual(N, M, G_eff, a0,
                                       damping=0.3, max_iter=500, tol=1e-4,
                                       volume_weighted=True)
        dt = time.time() - t0

        res_nw = solve_discrete_aqual(N, M, G_eff, a0,
                                       damping=0.3, max_iter=500, tol=1e-4,
                                       volume_weighted=False, quiet=True)

        r_mond = np.sqrt(G_eff * M / a0)
        r_out_min = max(r_mond, 5.0)
        r_out_max = N // 2 - 3

        C_vw, C_std_vw = measure_prefactor_C(res_vw['r'], res_vw['g'],
                                              res_vw['g_newton'], a0,
                                              r_out_min, r_out_max)
        C_nw, C_std_nw = measure_prefactor_C(res_nw['r'], res_nw['g'],
                                              res_nw['g_newton'], a0,
                                              r_out_min, r_out_max)
        slope_vw, _ = measure_slope(res_vw['r'], res_vw['g'], r_out_min, r_out_max)

        results_vw.append({'N': N, 'C': C_vw, 'C_std': C_std_vw,
                           'slope': slope_vw, 'time': dt, 'res': res_vw})
        results_nw.append({'N': N, 'C': C_nw, 'C_std': C_std_nw, 'res': res_nw})

        print(f"    C (vol-weighted) = {C_vw:.3f} +/- {C_std_vw:.3f}")
        print(f"    C (unweighted)   = {C_nw:.3f} +/- {C_std_nw:.3f}")
        print(f"    outer slope      = {slope_vw:.2f}")
        print(f"    ({dt:.1f}s)")

    print(f"\n  {'N':<6} {'N^3':<8} {'C_vw':<10} {'C_nw':<10} {'slope':<10}")
    print(f"  {'-'*42}")
    for rvw, rnw in zip(results_vw, results_nw):
        print(f"  {rvw['N']:<6} {rvw['N']**3:<8} {rvw['C']:<10.3f} "
              f"{rnw['C']:<10.3f} {rvw['slope']:<10.2f}")

    C_vals = [r['C'] for r in results_vw if not np.isnan(r['C'])]
    if len(C_vals) >= 2:
        trend = C_vals[-1] - C_vals[0]
        if abs(C_vals[-1] - 1.0) < 0.3:
            print(f"\n  >>> KT2: C trending toward 1 (latest {C_vals[-1]:.3f})")
        elif abs(trend) < 0.05:
            print(f"\n  >>> KT2: C STABLE at {C_vals[-1]:.3f} -- may be grid prediction")
        else:
            print(f"\n  >>> KT2: C converging: {[f'{c:.3f}' for c in C_vals]}")
    return results_vw, results_nw


# ============================================================
# KILL-TEST 3: Mass Scaling
# ============================================================

def kill_test_3():
    print("\n" + "=" * 70)
    print("KILL-TEST 3: MASS SCALING")
    print("  r_transition proportional to sqrt(M)?")
    print("=" * 70)

    N = 31; G_eff = 1.0; a0 = 2.0
    M_values = [10, 25, 50, 100, 200]
    results = []

    for M in M_values:
        r_pred = np.sqrt(G_eff * M / a0)
        r_src = max(2.0, 1.5 * (M / 50) ** 0.33)
        print(f"\n  M = {M}, r_MOND(pred) = {r_pred:.2f}")

        t0 = time.time()
        res = solve_discrete_aqual(N, M, G_eff, a0,
                                   r_source=r_src, damping=0.3,
                                   max_iter=500, tol=1e-4)
        dt = time.time() - t0

        r_trans = find_transition_radius(res['r'], res['g'], res['g_newton'], 1.5)
        results.append({'M': M, 'r_pred': r_pred, 'r_trans': r_trans,
                        'time': dt, 'res': res})

        if np.isnan(r_trans):
            print(f"    r_trans = NOT FOUND")
        else:
            print(f"    r_trans = {r_trans:.2f}  (pred {r_pred:.2f}, ratio {r_trans/r_pred:.3f})")
        print(f"    ({dt:.1f}s)")

    valid = [(r['M'], r['r_pred'], r['r_trans'])
             for r in results if not np.isnan(r['r_trans'])]
    print(f"\n  {'M':<8} {'sqrtM':<8} {'r_pred':<10} {'r_meas':<10} {'ratio':<10}")
    print(f"  {'-'*44}")
    for M, rp, rm in valid:
        print(f"  {M:<8} {np.sqrt(M):<8.2f} {rp:<10.2f} {rm:<10.2f} {rm/rp:<10.3f}")

    if len(valid) >= 3:
        Ms = np.array([v[0] for v in valid])
        rt = np.array([v[2] for v in valid])
        beta, _ = np.polyfit(np.log10(Ms), np.log10(rt), 1)
        print(f"\n  Power-law fit: r_trans ~ M^{beta:.3f}")
        print(f"  Expected (MOND): 0.500")
        if abs(beta - 0.5) < 0.1:
            print(f"  >>> KT3 PASSED: beta = {beta:.3f}")
        elif abs(beta - 0.5) < 0.2:
            print(f"  >>> KT3 MARGINAL: beta = {beta:.3f}")
        else:
            print(f"  >>> KT3 FAILED: beta = {beta:.3f}")
    return results


# ============================================================
# FIGURES
# ============================================================

def make_figures(kt1, kt2_vw, kt2_nw, kt3):
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('Grid-AQUAL v0.1: Systematic Kill-Tests',
                 fontsize=15, fontweight='bold', y=0.98)

    # KT1 panel 1: g(r) for different a0
    ax = axes[0, 0]
    cols = ['red', 'orange', 'green', 'blue', 'purple']
    for i, res in enumerate(kt1):
        r, g = res['res']['r'], res['res']['g']
        m = (r > 2.5) & (g > 0) & (r < 13)
        if np.any(m):
            ax.loglog(r[m], g[m], color=cols[i], lw=2, label=f"$a_0$={res['a0']}")
    r_ref = np.linspace(3, 12, 50)
    g0 = kt1[0]['res']['g'][2] if kt1[0]['res']['g'][2] > 0 else 1
    r0 = kt1[0]['res']['r'][2]
    ax.loglog(r_ref, g0*(r_ref/r0)**(-2), 'k:', alpha=0.4, label='$r^{-2}$')
    ax.loglog(r_ref, g0*(r_ref/r0)**(-1), 'k--', alpha=0.4, label='$r^{-1}$')
    ax.set_xlabel('r'); ax.set_ylabel('|g|')
    ax.set_title('KT1: g(r) for different $a_0$')
    ax.legend(fontsize=7, loc='lower left')

    # KT1 panel 2: slopes
    ax = axes[0, 1]
    ga = [r['g_over_a0'] for r in kt1]
    si = [r['slope_inner'] for r in kt1]
    so = [r['slope_outer'] for r in kt1]
    ax.semilogx(ga, si, 'bo-', lw=2, ms=8, label='Inner (r=3-5)')
    ax.semilogx(ga, so, 'rs-', lw=2, ms=8, label='Outer (r=8-12)')
    ax.axhline(-2, color='black', ls='--', alpha=0.5, label='Newton')
    ax.axhline(-1, color='magenta', ls='--', alpha=0.5, label='MOND')
    ax.set_xlabel('g(r=3)/$a_0$'); ax.set_ylabel('slope')
    ax.set_title('KT1: Slope vs acceleration')
    ax.legend(fontsize=8); ax.set_ylim(-3, 0)

    # KT2: C vs N
    ax = axes[0, 2]
    Ns = [r['N'] for r in kt2_vw]
    Cvw = [r['C'] for r in kt2_vw]
    Cnw = [r['C'] for r in kt2_nw]
    Cstd = [r['C_std'] for r in kt2_vw]
    ax.errorbar(Ns, Cvw, yerr=Cstd, fmt='bo-', lw=2, ms=8, capsize=5, label='Vol-weighted')
    ax.plot(Ns, Cnw, 'rs--', lw=2, ms=8, label='Unweighted')
    ax.axhline(1.0, color='green', ls='--', alpha=0.5, label='C=1 (exact MOND)')
    ax.set_xlabel('N'); ax.set_ylabel('C = $g_{AQ}/g_{MOND}$')
    ax.set_title('KT2: Prefactor convergence')
    ax.legend(fontsize=8)

    # KT2: g/gN for different N
    ax = axes[1, 0]
    a0 = 2.0
    cols_n = ['blue', 'red', 'green', 'purple']
    for i, res in enumerate(kt2_vw):
        r = res['res']['r']; g = res['res']['g']; gN = res['res']['g_newton']
        m = (r > 3) & (g > 0) & (gN > 0) & (r < res['N']//2 - 3)
        if np.any(m):
            ax.plot(r[m], g[m]/gN[m], color=cols_n[i], lw=2, label=f"N={res['N']}")
    r_p = kt2_vw[-1]['res']['r']; gN_p = kt2_vw[-1]['res']['g_newton']
    mp = (r_p > 3) & (gN_p > 0) & (r_p < kt2_vw[-1]['N']//2 - 3)
    ax.plot(r_p[mp], np.sqrt(a0/gN_p[mp]), 'm:', lw=1.5, label=r'$\sqrt{a_0/g_N}$')
    ax.axhline(1, color='gray', ls='--', alpha=0.3)
    ax.set_xlabel('r'); ax.set_ylabel('$g/g_N$')
    ax.set_title('KT2: Enhancement vs N')
    ax.legend(fontsize=7); ax.set_ylim(0, 6)

    # KT3: r_trans vs sqrt(M)
    ax = axes[1, 1]
    valid = [(r['M'], r['r_pred'], r['r_trans'])
             for r in kt3 if not np.isnan(r['r_trans'])]
    if valid:
        Ms = [v[0] for v in valid]
        rp = [v[1] for v in valid]
        rm = [v[2] for v in valid]
        sqM = [np.sqrt(m) for m in Ms]
        ax.plot(sqM, rm, 'bo-', lw=2, ms=8, label='Measured')
        ax.plot(sqM, rp, 'r--', lw=2, label='Predicted $\\sqrt{GM/a_0}$')
    ax.set_xlabel('$\\sqrt{M}$'); ax.set_ylabel('$r_{transition}$')
    ax.set_title('KT3: Mass scaling')
    ax.legend(fontsize=8)

    # KT3: g(r) for different M
    ax = axes[1, 2]
    cols_m = ['blue', 'cyan', 'red', 'orange', 'purple']
    for i, res in enumerate(kt3):
        r, g = res['res']['r'], res['res']['g']
        m = (r > 2.5) & (g > 0) & (r < 13)
        if np.any(m):
            ax.loglog(r[m], g[m], color=cols_m[i], lw=2, label=f"M={res['M']}")
    ax.set_xlabel('r'); ax.set_ylabel('|g|')
    ax.set_title('KT3: g(r) for different M')
    ax.legend(fontsize=7)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = '/home/user/EFC/src/efc/solver/grid_aqual_convergence.png'
    plt.savefig(out, dpi=200, bbox_inches='tight')
    print(f"\nFigure saved: {out}")
    return out


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    t0 = time.time()

    print("=" * 70)
    print("GRID-AQUAL v0.1: SYSTEMATIC KILL-TESTS")
    print("=" * 70)

    kt1 = kill_test_1()
    kt2_vw, kt2_nw = kill_test_2()
    kt3 = kill_test_3()
    figpath = make_figures(kt1, kt2_vw, kt2_nw, kt3)

    dt = time.time() - t0
    print("\n" + "=" * 70)
    print(f"DONE in {dt:.0f}s ({dt/60:.1f} min)")
    print("=" * 70)
    print("""
Decision tree:
  KT1 PASS + KT2 C->1  : Pure AQUAL on graph, numerics confirmed
  KT1 PASS + KT2 C!=1  : Graph gives modified MOND (own prediction)
  KT1 FAIL              : Not AQUAL, different effective theory
  KT3 beta~0.5          : Correct mass-scaling (strong confirmation)
  KT3 beta!=0.5         : Scaling broken (investigate)
""")
