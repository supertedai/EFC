#!/usr/bin/env python3
"""C-collision reproduction: run BOTH solvers at matched parameters and compare C.

solve_aqual      -> pipelines/efc/native_v2_graph/kernel/solver.py (modular)
solve_discrete_aqual -> src/efc/solver/grid_aqual_killtests.py (standalone)

Matched: N in {21,31}, M=50, G_eff=1, a0=2.0, volume-weighted,
window r_out_min=max(r_mond,5.0), r_out_max=N//2-3, r_mond=sqrt(G_eff*M/a0)=5.
"""
import sys, time
import numpy as np

# --- solve_aqual (modular) ---
sys.path.insert(0, '/home/morten/EFC-prov/pipelines/efc/native_v2_graph')
from kernel.solver import solve_aqual
from kernel.observables import radial_profile, measure_prefactor_C as C_mod

# --- solve_discrete_aqual (standalone killtests) ---
sys.path.insert(0, '/home/morten/EFC-prov/src/efc/solver')
from grid_aqual_killtests import solve_discrete_aqual, measure_prefactor_C as C_disc

M = 50.0; G_eff = 1.0; a0 = 2.0
r_mond = np.sqrt(G_eff * M / a0)   # = 5.0
r_out_min = max(r_mond, 5.0)

for N in [21, 31]:
    r_out_max = N // 2 - 3
    print(f"\n=== N={N} (window r in ({r_out_min}, {r_out_max})) ===")

    # --- solve_aqual ---
    t0 = time.time()
    res = solve_aqual(N, [([0, 0, 0], M)], G_eff, a0, quiet=True)
    dt_a = time.time() - t0
    r, g, g_std, counts = radial_profile(res['pos'], res['r_arr'], res['g_mag'], res['boundary'])
    g_newton = G_eff * M / r ** 2
    C_a, C_a_std = C_mod(r, g, g_newton, a0, r_out_min, r_out_max)

    # --- solve_discrete_aqual ---
    t0 = time.time()
    resd = solve_discrete_aqual(N, M, G_eff, a0, damping=0.3, max_iter=500, tol=1e-4,
                                volume_weighted=True, quiet=True)
    dt_d = time.time() - t0
    C_d, C_d_std = C_disc(resd['r'], resd['g'], resd['g_newton'], a0, r_out_min, r_out_max)

    print(f"  solve_aqual:          C = {C_a:.6f} +/- {C_a_std:.6f}   ({dt_a:.1f}s, iters={res['iterations']})")
    print(f"  solve_discrete_aqual: C = {C_d:.6f} +/- {C_d_std:.6f}   ({dt_d:.1f}s, iters={resd['iterations']})")
    if not (np.isnan(C_a) or np.isnan(C_d)):
        print(f"  delta = {abs(C_a - C_d):.6f}  ({100*abs(C_a-C_d)/C_a:.3f}%)")

    # source injection diagnostic
    # both use uniform ball r<r_source, vol=(4/3)pi r_source^3
    rhs_a_nnz = int(np.count_nonzero(res['rhs']))
    rhs_d_nnz = None
    print(f"  source nonzero nodes: modular rhs={rhs_a_nnz}")
