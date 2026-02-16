#!/usr/bin/env python3
"""
Grid-AQUAL v0.1: Extra Kill-Tests (2 of 3)
============================================
From GPT analysis — the two remaining "ekte motor" tests:
  TEST 4: Superposition / Two Sources
    - AQUAL is nonlinear -> superposition is BROKEN in specific way
    - g(two sources) != g(source1) + g(source2)
    - But solution must still be PHYSICAL (smooth, no artifacts)
    - Compare: Phi(M1+M2) vs Phi(M1)+Phi(M2) -- the DIFFERENCE is the
      nonlinear coupling, which should be systematic, not noisy
  TEST 5: External Field Effect (EFE)
    - In MOND, an external uniform field g_ext partially restores
      Newton INSIDE a system (even where internal g < a0)
    - This is a DISTINCTIVE prediction of AQUAL vs dark matter
    - Strategy: solve with uniform tilt added to boundary conditions
    - When g_ext > a0: internal dynamics should become more Newtonian
    - This is the most distinctive observable from graph-AQUAL
Both tests use the same solver from grid_aqual_v2.py / convergence script.
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
# LATTICE + SOLVER (same as convergence script)
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
    return x / np.sqrt(1.0 + x**2)


def solve_aqual(N, sources, G_eff, a0, r_source=2.0,
                spacing=1.0, max_iter=400, tol=1e-4,
                damping=0.3, boundary_phi=None, quiet=False):
    """
    Generalised solver.

    sources: list of (position_3d, mass) tuples
    boundary_phi: if provided, function(pos) -> Phi at boundary nodes
                  (used for EFE: adds uniform tilt)
    """
    pos, adj, deg = build_cubic_lattice(N, spacing)
    n = N**3
    r_arr = np.linalg.norm(pos, axis=1)

    # Source density
    rhs = np.zeros(n)
    for src_pos, src_M in sources:
        src_pos = np.array(src_pos, dtype=float)
        for i in range(n):
            dist = np.linalg.norm(pos[i] - src_pos)
            if dist < r_source:
                vol = (4/3) * np.pi * r_source**3
                rhs[i] += 4 * np.pi * G_eff * src_M / vol

    # Boundary
    r_max = np.max(r_arr)
    boundary = r_arr > (r_max - 1.5 * spacing)

    # Boundary values
    phi_boundary = np.zeros(n)
    if boundary_phi is not None:
        for i in np.where(boundary)[0]:
            phi_boundary[i] = boundary_phi(pos[i])

    # Initial: linear Poisson
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
        rhs_bc[i] = phi_boundary[i]
    Phi = spsolve(A_lin_csr, rhs_bc)

    # Picard
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
            rhs_iter[i] = phi_boundary[i]

        Phi_new = spsolve(A_csr, rhs_iter)
        Phi = (1 - damping) * Phi_old + damping * Phi_new

        change = np.max(np.abs(Phi - Phi_old)) / (np.max(np.abs(Phi)) + 1e-10)
        if change < tol:
            converged_flag = True
            break

    if not quiet:
        tag = "OK" if converged_flag else f"NOT CONV ({change:.2e})"
        print(f"    {tag} in {iteration+1} iters")

    # Gravity
    g_vec = np.zeros((n, 3))
    g_mag = np.zeros(n)
    for i in range(n):
        gv = np.zeros(3)
        for j in adj[i]:
            dr = pos[j] - pos[i]
            dist = np.linalg.norm(dr)
            dPhi = Phi[i] - Phi[j]
            if dist > 0:
                gv += dPhi * dr / dist**2
        g_vec[i] = gv
        g_mag[i] = np.linalg.norm(gv)

    return {
        'pos': pos, 'Phi': Phi, 'g_mag': g_mag, 'g_vec': g_vec,
        'r_arr': r_arr, 'boundary': boundary,
        'converged': converged_flag, 'iterations': iteration + 1
    }


def radial_profile(pos, r_arr, field, boundary, r_max_frac=0.85,
                   center=None, volume_weighted=True):
    """Radial binning around a center point."""
    if center is None:
        center = np.array([0.0, 0.0, 0.0])
    r_from_center = np.linalg.norm(pos - center, axis=1)
    r_limit = r_max_frac * np.max(r_arr)

    r_bins = np.arange(2.5, r_limit, 1.0)
    f_binned = np.zeros(len(r_bins))

    for k, rb in enumerate(r_bins):
        mask = (r_from_center > rb-0.5) & (r_from_center < rb+0.5) & (~boundary)
        if np.sum(mask) > 0:
            if volume_weighted:
                w = 1.0 / (4*np.pi*r_from_center[mask]**2 + 1e-10)
                w /= np.sum(w)
                f_binned[k] = np.sum(w * field[mask])
            else:
                f_binned[k] = np.mean(field[mask])
    return r_bins, f_binned


# ============================================================
# TEST 4: SUPERPOSITION
# ============================================================

def test_superposition():
    """
    In nonlinear AQUAL, superposition is broken:
      Phi(M1+M2) != Phi(M1) + Phi(M2)

    Strategy:
      1. Solve with source A alone at (-d, 0, 0)
      2. Solve with source B alone at (+d, 0, 0)
      3. Solve with both A+B together
      4. Compare: Phi_AB vs Phi_A + Phi_B
      5. The difference dPhi = Phi_AB - (Phi_A + Phi_B) is the nonlinear coupling

    Expected:
      - Newton (a0->inf): dPhi ~ 0 (linear, superposition holds)
      - AQUAL (finite a0): dPhi != 0, smooth, systematic
      - Noisy/divergent dPhi: numerical artifact (BAD)
    """
    print("\n" + "=" * 70)
    print("TEST 4: SUPERPOSITION (two sources)")
    print("  Nonlinear AQUAL breaks superposition in specific way")
    print("=" * 70)

    N = 31
    G_eff = 1.0
    a0 = 2.0
    M_A = 30.0
    M_B = 30.0
    d = 4.0  # separation from center

    pos_A = np.array([-d, 0, 0])
    pos_B = np.array([+d, 0, 0])

    print(f"\n  Setup: M_A={M_A} at x=-{d}, M_B={M_B} at x=+{d}")
    print(f"  Grid: {N}^3, a0={a0}")

    # 1. Source A alone
    print("\n  Solving A alone...")
    t0 = time.time()
    res_A = solve_aqual(N, [(pos_A, M_A)], G_eff, a0)
    print(f"    ({time.time()-t0:.1f}s)")

    # 2. Source B alone
    print("  Solving B alone...")
    t0 = time.time()
    res_B = solve_aqual(N, [(pos_B, M_B)], G_eff, a0)
    print(f"    ({time.time()-t0:.1f}s)")

    # 3. Both together
    print("  Solving A+B together...")
    t0 = time.time()
    res_AB = solve_aqual(N, [(pos_A, M_A), (pos_B, M_B)], G_eff, a0)
    print(f"    ({time.time()-t0:.1f}s)")

    # 4. Newton reference (a0 -> inf)
    print("  Solving A+B Newton (a0->inf)...")
    t0 = time.time()
    res_N = solve_aqual(N, [(pos_A, M_A), (pos_B, M_B)], G_eff, a0=1e10, quiet=True)
    res_NA = solve_aqual(N, [(pos_A, M_A)], G_eff, a0=1e10, quiet=True)
    res_NB = solve_aqual(N, [(pos_B, M_B)], G_eff, a0=1e10, quiet=True)
    print(f"    ({time.time()-t0:.1f}s)")

    # 5. Analysis
    Phi_sum = res_A['Phi'] + res_B['Phi']
    Phi_AB = res_AB['Phi']
    delta_Phi = Phi_AB - Phi_sum

    Phi_sum_N = res_NA['Phi'] + res_NB['Phi']
    delta_Phi_N = res_N['Phi'] - Phi_sum_N

    # Statistics (exclude boundary)
    interior = ~res_AB['boundary']
    Phi_scale = np.max(np.abs(Phi_AB[interior]))

    delta_aqual_rms = np.sqrt(np.mean(delta_Phi[interior]**2))
    delta_newton_rms = np.sqrt(np.mean(delta_Phi_N[interior]**2))
    delta_aqual_max = np.max(np.abs(delta_Phi[interior]))
    delta_newton_max = np.max(np.abs(delta_Phi_N[interior]))

    print(f"\n  SUPERPOSITION VIOLATION:")
    print(f"    AQUAL:  RMS(dPhi)/Phi_max = {delta_aqual_rms/Phi_scale:.4e}, "
          f"max|dPhi|/Phi_max = {delta_aqual_max/Phi_scale:.4e}")
    print(f"    Newton: RMS(dPhi)/Phi_max = {delta_newton_rms/Phi_scale:.4e}, "
          f"max|dPhi|/Phi_max = {delta_newton_max/Phi_scale:.4e}")
    print(f"    Ratio AQUAL/Newton: {delta_aqual_rms/(delta_newton_rms+1e-30):.1f}x")

    if delta_aqual_rms > 5 * delta_newton_rms:
        print(f"\n  >> Superposition BROKEN in AQUAL (as expected for nonlinear theory)")
    else:
        print(f"\n  >> Superposition violation weak -- may need larger separation or lower a0")

    # Profile along x-axis
    pos = res_AB['pos']
    x_axis = (np.abs(pos[:, 1]) < 0.5) & (np.abs(pos[:, 2]) < 0.5) & (~res_AB['boundary'])
    x_vals = pos[x_axis, 0]
    sort_idx = np.argsort(x_vals)
    x_sorted = x_vals[sort_idx]
    delta_profile = delta_Phi[x_axis][sort_idx]
    delta_N_profile = delta_Phi_N[x_axis][sort_idx]

    # Check smoothness: is dPhi smooth or noisy?
    if len(delta_profile) > 5:
        noise = np.std(np.diff(delta_profile)) / (np.std(delta_profile) + 1e-30)
        noise_N = np.std(np.diff(delta_N_profile)) / (np.std(delta_N_profile) + 1e-30)
        print(f"\n  SMOOTHNESS CHECK (lower = smoother):")
        print(f"    AQUAL dPhi noise ratio:  {noise:.3f}")
        print(f"    Newton dPhi noise ratio: {noise_N:.3f}")
        if noise < 2.0:
            print(f"    >> dPhi is SMOOTH (physical nonlinear coupling)")
        else:
            print(f"    >> dPhi is NOISY (numerical artifact)")

    return {
        'res_A': res_A, 'res_B': res_B, 'res_AB': res_AB, 'res_N': res_N,
        'delta_Phi': delta_Phi, 'delta_Phi_N': delta_Phi_N,
        'x_sorted': x_sorted, 'delta_profile': delta_profile,
        'delta_N_profile': delta_N_profile,
        'Phi_scale': Phi_scale
    }


# ============================================================
# TEST 5: EXTERNAL FIELD EFFECT (EFE)
# ============================================================

def test_efe():
    """
    In MOND/AQUAL, an external uniform field g_ext partially
    restores Newtonian dynamics even where internal g < a0.

    Strategy:
      1. Solve isolated source (Dirichlet Phi=0 at boundary)
      2. Solve same source with tilted boundary: Phi_boundary = -g_ext * x
         This imposes a uniform external field in x-direction
      3. Compare: does the MOND enhancement DECREASE with g_ext?

    Expected:
      - g_ext = 0: full MOND enhancement
      - g_ext ~ a0: partial restoration of Newton
      - g_ext >> a0: fully Newtonian (mu->1 everywhere)
    """
    print("\n" + "=" * 70)
    print("TEST 5: EXTERNAL FIELD EFFECT (EFE)")
    print("  Does external field restore Newton inside?")
    print("=" * 70)

    N = 31
    G_eff = 1.0
    a0 = 2.0
    M = 50.0

    # External field strengths (in units of a0)
    g_ext_values = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]

    results = []
    for g_ext_ratio in g_ext_values:
        g_ext = g_ext_ratio * a0

        print(f"\n  g_ext/a0 = {g_ext_ratio} (g_ext = {g_ext:.1f})")

        if g_ext == 0:
            bphi = None
        else:
            # Uniform field in x-direction: Phi_ext = -g_ext * x
            bphi = lambda pos, ge=g_ext: -ge * pos[0]

        t0 = time.time()
        res = solve_aqual(N, [([0,0,0], M)], G_eff, a0,
                          boundary_phi=bphi,
                          damping=0.3, max_iter=500, tol=1e-4)
        dt = time.time() - t0

        # Measure MOND enhancement in outer region
        # Along x-axis (direction of external field)
        r, g_profile = radial_profile(res['pos'], res['r_arr'],
                                       res['g_mag'], res['boundary'])
        g_newton = G_eff * M / r**2

        # Enhancement in outer region (r = 6-12)
        mask = (r > 6) & (r < 12) & (g_profile > 0) & (g_newton > 0)
        if np.sum(mask) > 0:
            enhancement = np.mean(g_profile[mask] / g_newton[mask])
        else:
            enhancement = np.nan

        # Also measure along x specifically (with and against ext field)
        pos = res['pos']
        # Positive x direction (with ext field)
        mask_px = (pos[:, 0] > 0) & (np.abs(pos[:, 1]) < 0.5) & \
                  (np.abs(pos[:, 2]) < 0.5) & (~res['boundary'])
        # Negative x direction (against ext field)
        mask_nx = (pos[:, 0] < 0) & (np.abs(pos[:, 1]) < 0.5) & \
                  (np.abs(pos[:, 2]) < 0.5) & (~res['boundary'])

        g_px = np.mean(res['g_mag'][mask_px]) if np.sum(mask_px) > 0 else np.nan
        g_nx = np.mean(res['g_mag'][mask_nx]) if np.sum(mask_nx) > 0 else np.nan
        asymmetry = (g_px - g_nx) / (0.5 * (g_px + g_nx)) if (g_px + g_nx) > 0 else 0

        results.append({
            'g_ext_ratio': g_ext_ratio, 'g_ext': g_ext,
            'enhancement': enhancement, 'asymmetry': asymmetry,
            'g_px': g_px, 'g_nx': g_nx,
            'time': dt, 'res': res, 'r': r, 'g_profile': g_profile
        })
        print(f"    Enhancement g/g_N (r=6-12): {enhancement:.3f}")
        print(f"    Asymmetry (along vs against): {asymmetry:.3f}")
        print(f"    ({dt:.1f}s)")

    # Summary
    print(f"\n  EFE SUMMARY:")
    print(f"  {'g_ext/a0':<12} {'g/g_N':<10} {'asymmetry':<12} {'interpretation'}")
    print(f"  {'-'*52}")
    for r in results:
        if r['g_ext_ratio'] == 0:
            interp = "baseline (full MOND)"
        elif r['enhancement'] < results[0]['enhancement'] * 0.7:
            interp = "Newton RESTORED"
        elif r['enhancement'] < results[0]['enhancement'] * 0.9:
            interp = "partial restoration"
        else:
            interp = "still MOND-like"
        print(f"  {r['g_ext_ratio']:<12.1f} {r['enhancement']:<10.3f} "
              f"{r['asymmetry']:<12.3f} {interp}")

    # EFE verdict
    enh_0 = results[0]['enhancement']
    enh_strong = [r['enhancement'] for r in results if r['g_ext_ratio'] >= 2.0]
    if enh_strong and not np.isnan(enh_0):
        if min(enh_strong) < enh_0 * 0.7:
            print(f"\n  >> EFE CONFIRMED: Strong external field restores Newton")
            print(f"     Enhancement dropped from {enh_0:.2f} to {min(enh_strong):.2f}")
        elif min(enh_strong) < enh_0 * 0.9:
            print(f"\n  >> EFE PARTIAL: Some restoration but weak")
        else:
            print(f"\n  >> EFE NOT DETECTED: External field has no effect")

    return results


# ============================================================
# FIGURES
# ============================================================

def make_figures(sup_results, efe_results):
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('Grid-AQUAL v0.1: Superposition & EFE Tests',
                 fontsize=15, fontweight='bold', y=0.98)

    # == SUPERPOSITION ==

    # Panel 1: dPhi along x-axis
    ax = axes[0, 0]
    x = sup_results['x_sorted']
    ax.plot(x, sup_results['delta_profile'], 'r-', lw=2, label='AQUAL $\\delta\\Phi$')
    ax.plot(x, sup_results['delta_N_profile'], 'k--', lw=1.5, label='Newton $\\delta\\Phi$')
    ax.axhline(0, color='gray', ls=':', alpha=0.3)
    ax.axvline(-4, color='blue', ls=':', alpha=0.3, label='Source A')
    ax.axvline(+4, color='blue', ls=':', alpha=0.3, label='Source B')
    ax.set_xlabel('x'); ax.set_ylabel('$\\delta\\Phi = \\Phi_{AB} - (\\Phi_A + \\Phi_B)$')
    ax.set_title('Superposition violation along x-axis')
    ax.legend(fontsize=8)

    # Panel 2: Phi profiles comparison
    ax = axes[0, 1]
    pos = sup_results['res_AB']['pos']
    x_mask = (np.abs(pos[:, 1]) < 0.5) & (np.abs(pos[:, 2]) < 0.5) & \
             (~sup_results['res_AB']['boundary'])
    x_vals = pos[x_mask, 0]
    si = np.argsort(x_vals)
    ax.plot(x_vals[si], sup_results['res_AB']['Phi'][x_mask][si], 'r-', lw=2,
            label='$\\Phi_{AB}$ (AQUAL)')
    Phi_sum = sup_results['res_A']['Phi'] + sup_results['res_B']['Phi']
    ax.plot(x_vals[si], Phi_sum[x_mask][si], 'b--', lw=2, label='$\\Phi_A + \\Phi_B$')
    ax.plot(x_vals[si], sup_results['res_N']['Phi'][x_mask][si], 'k:', lw=1.5,
            label='Newton $\\Phi_{AB}$')
    ax.set_xlabel('x'); ax.set_ylabel('$\\Phi$')
    ax.set_title('Potentials: joint vs sum')
    ax.legend(fontsize=8)

    # Panel 3: |g| for A, B, AB
    ax = axes[0, 2]
    for label, res, color, ls in [
        ('A alone', sup_results['res_A'], 'blue', '--'),
        ('B alone', sup_results['res_B'], 'green', '--'),
        ('A+B joint', sup_results['res_AB'], 'red', '-'),
    ]:
        r, g = radial_profile(res['pos'], res['r_arr'], res['g_mag'], res['boundary'])
        mask = (r > 2) & (g > 0) & (r < 13)
        if np.any(mask):
            ax.semilogy(r[mask], g[mask], color=color, ls=ls, lw=2, label=label)
    ax.set_xlabel('r (from origin)'); ax.set_ylabel('|g|')
    ax.set_title('Gravity: individual vs joint')
    ax.legend(fontsize=8)

    # == EFE ==

    # Panel 4: g profiles for different g_ext
    ax = axes[1, 0]
    cols = ['black', 'blue', 'green', 'orange', 'red', 'purple']
    for i, res in enumerate(efe_results):
        r, g = res['r'], res['g_profile']
        mask = (r > 3) & (g > 0) & (r < 12)
        if np.any(mask):
            ax.semilogy(r[mask], g[mask], color=cols[i], lw=2,
                        label=f"$g_{{ext}}/a_0$={res['g_ext_ratio']}")
    ax.set_xlabel('r'); ax.set_ylabel('|g|')
    ax.set_title('EFE: g(r) for different external fields')
    ax.legend(fontsize=7)

    # Panel 5: Enhancement vs g_ext/a0
    ax = axes[1, 1]
    ge = [r['g_ext_ratio'] for r in efe_results]
    enh = [r['enhancement'] for r in efe_results]
    ax.plot(ge, enh, 'bo-', lw=2, ms=8)
    ax.axhline(1.0, color='gray', ls='--', alpha=0.5, label='Newton (no enhancement)')
    ax.set_xlabel('$g_{ext} / a_0$')
    ax.set_ylabel('$\\langle g/g_N \\rangle$ (r=6-12)')
    ax.set_title('EFE: Enhancement drops with external field')
    ax.legend(fontsize=8)

    # Panel 6: Asymmetry vs g_ext
    ax = axes[1, 2]
    asym = [r['asymmetry'] for r in efe_results]
    ax.plot(ge, asym, 'rs-', lw=2, ms=8)
    ax.axhline(0, color='gray', ls='--', alpha=0.5)
    ax.set_xlabel('$g_{ext} / a_0$')
    ax.set_ylabel('Asymmetry (along vs against)')
    ax.set_title('EFE: Directional asymmetry')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = '/home/user/EFC/src/efc/solver/grid_aqual_extra_tests.png'
    plt.savefig(out, dpi=200, bbox_inches='tight')
    print(f"\nFigure saved: {out}")
    return out


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    t0 = time.time()

    print("=" * 70)
    print("GRID-AQUAL v0.1: EXTRA KILL-TESTS")
    print("  Test 4: Superposition (nonlinear coupling)")
    print("  Test 5: External Field Effect (EFE)")
    print("=" * 70)

    sup = test_superposition()
    efe = test_efe()
    figpath = make_figures(sup, efe)

    dt = time.time() - t0
    print("\n" + "=" * 70)
    print(f"DONE in {dt:.0f}s ({dt/60:.1f} min)")
    print("=" * 70)
    print("""
Interpretation:
  Test 4 (Superposition):
    PASS: dPhi smooth + nonzero -> correct AQUAL nonlinearity
    FAIL: dPhi noisy/divergent  -> numerical artifact
    WARN: dPhi ~ 0 even in MOND regime -> check a0 / separation
  Test 5 (EFE):
    PASS: Enhancement drops with g_ext -> EFE works on graph
    FAIL: Enhancement unchanged -> EFE absent (problem for MOND claim)

  If both pass: graph-AQUAL has FULL MOND structure
  (Newton limit + sqrt(a0 g_N) + broken superposition + EFE)
""")
