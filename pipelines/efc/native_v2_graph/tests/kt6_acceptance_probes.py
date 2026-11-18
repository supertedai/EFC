#!/usr/bin/env python3
"""Bounded KT6 acceptance probes for boundary and far-radius behavior."""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kernel.observables import measure_prefactor_C, measure_slope, radial_profile
from kernel.solver import solve_aqual
from tests.kt6_physical_normalization import _profile_summary


def run(output_dir, N=21, M=50.0, G_eff=1.0, a0=2.0, box_side=20.0,
        r_source=2.0, max_iter=100, tol=1e-3):
    os.makedirs(output_dir, exist_ok=True)
    h = box_side / (N - 1)
    margin_runs = []
    for margin in (1.0, 1.5, 2.0):
        started = time.time()
        field = solve_aqual(
            N=N, sources=[([0.0, 0.0, 0.0], M)], G_eff=G_eff,
            a0=a0, r_source=r_source, spacing=h, max_iter=max_iter,
            tol=tol, quiet=True, boundary_margin=margin,
        )
        elapsed = time.time() - started
        profile = _profile_summary(field, field["g_mag"], M, G_eff, a0, (5.0, 9.0))
        margin_runs.append({
            "boundary_margin": margin,
            "converged": bool(field["converged"]),
            "iterations": int(field["iterations"]),
            "wall_time_s": elapsed,
            "C_r": profile["C_by_bin"],
            "r_bins": profile["r_bins"],
            "radial_slope": profile["log_slope"],
            "mean_C": profile["C_mean"],
            "C_bin_spread_not_uncertainty": profile["C_radial_bin_spread_not_uncertainty"],
        })

    started = time.time()
    field = solve_aqual(
        N=N, sources=[([0.0, 0.0, 0.0], M)], G_eff=G_eff, a0=a0,
        r_source=r_source, spacing=h, max_iter=max_iter, tol=tol,
        quiet=True, boundary_margin=1.5,
    )
    far_profile = _profile_summary(field, field["g_mag"], M, G_eff, a0, (9.0, 13.0))
    output = {
        "test": "KT6 acceptance probes",
        "scope": "generic standard AQUAL numerical calibration only",
        "params": {"N": N, "box_side": box_side, "spacing": h, "M": M,
                   "G_eff": G_eff, "a0": a0, "r_source": r_source,
                   "max_iter": max_iter, "tol": tol},
        "boundary_margin_sensitivity": margin_runs,
        "boundary_symmetry": {
            "status": "Pass",
            "method": "boundary_mask invariance under axis permutations and sign flips",
            "scope": "N=9, h=1, margin=1.5; regression test",
        },
        "far_radius_probe": {
            "window": [9.0, 13.0],
            "C_r": far_profile["C_by_bin"],
            "r_bins": far_profile["r_bins"],
            "acceleration_log_slope": far_profile["log_slope"],
            "slope_bin_count": far_profile["slope_bin_count"],
            "mean_C": far_profile["C_mean"],
            "C_bin_spread_not_uncertainty": far_profile["C_radial_bin_spread_not_uncertainty"],
            "converged": bool(field["converged"]),
            "iterations": int(field["iterations"]),
            "wall_time_s": time.time() - started,
            "deep_mond_asymptotic_status": "Unresolved: finite box and bounded radial window do not establish asymptotic behavior",
        },
    }
    path = os.path.join(output_dir, "kt6_acceptance_probes.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    print(json.dumps(output, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    run(sys.argv[1])
