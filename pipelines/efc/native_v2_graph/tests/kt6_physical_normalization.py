#!/usr/bin/env python3
"""KT6: physical normalization of the Native v2 Graph-AQUAL chain.

Runs Newton and nonlinear AQUAL source/observable controls at a fixed physical
box size. Output records raw radial profiles and Gauss flux; it does not promote
C to a physical EFC prefactor.
"""
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kernel.graph import build_cubic_lattice, radial_distances
from kernel.observables import measure_prefactor_C, measure_slope, radial_profile
from kernel.operators import discrete_gradient, gauss_flux_through_shell
from kernel.solver import solve_aqual, solve_linear_poisson


def _mass_fraction(pos, r_arr, r_source, spacing):
    count = int(np.count_nonzero(r_arr < r_source))
    sphere_volume = (4.0 / 3.0) * np.pi * r_source ** 3
    fraction = count * spacing ** 3 / sphere_volume
    return count, float(fraction)


def experiment_metadata(N, M, G_eff, a0, box_side, r_source,
                        boundary_margin=1.5):
    """Describe the explicit code units, grid, source and boundary convention."""
    if (N < 2 or M <= 0 or G_eff <= 0 or a0 <= 0 or box_side <= 0
            or r_source <= 0 or boundary_margin <= 0):
        raise ValueError(
            "N, M, G_eff, a0, box_side, r_source, and boundary_margin "
            "must be positive"
        )
    spacing = box_side / (N - 1)
    r_mond = math.sqrt(G_eff * M / a0)
    return {
        "N": int(N),
        "n_nodes": int(N ** 3),
        "box_side": float(box_side),
        "spacing": float(spacing),
        "unit_system": "dimensionless code units; no SI mapping asserted",
        "target_mass": float(M),
        "G_eff": float(G_eff),
        "a0": float(a0),
        "r_mond": float(r_mond),
        "r_source": float(r_source),
        "source_center": [0.0, 0.0, 0.0],
        "source_mask_rule": "distance < r_source",
        "boundary_condition": (
            "Dirichlet Phi=0 pinned on the spherical margin shell "
            "(boundary_mask: r > r_max - boundary_margin*h)"
        ),
        "boundary_treatment": (
            "Dirichlet pin applies to the spherical margin shell only; outer "
            "cube faces are graph-truncated (fewer neighbours) and are not "
            "Dirichlet-pinned; pre-existing solver behaviour"
        ),
        "boundary_margin": float(boundary_margin),
        "field_equation": "div(mu(|grad Phi|/a0) grad Phi)=4*pi*G_eff*rho",
        "gradient_flux_convention": (
            "centered physical node gradient; symmetric full-gradient face norm "
            "for mu; directional edge derivative DeltaPhi/h"
        ),
        "acceleration_definition": "g=-grad(Phi)",
    }


def _profile_summary(result, observed_g, target_mass, G_eff, a0,
                     radial_window):
    r, g, g_spread, counts = radial_profile(
        result["pos"], result["r_arr"], observed_g, result["boundary"]
    )
    g_newton = G_eff * target_mass / r ** 2
    r_min, r_max = radial_window
    mask = (r > r_min) & (r < r_max) & (counts > 0)
    slope, n_slope = measure_slope(r, g, r_min, r_max)
    summary = {
        "r_bins": r[mask].astype(float).tolist(),
        "g_bins": g[mask].astype(float).tolist(),
        "g_bin_spread": g_spread[mask].astype(float).tolist(),
        "counts": counts[mask].astype(int).tolist(),
        "g_newton_bins": g_newton[mask].astype(float).tolist(),
        "g_over_g_newton": (g[mask] / g_newton[mask]).astype(float).tolist(),
        "log_slope": float(slope) if np.isfinite(slope) else None,
        "slope_bin_count": int(n_slope),
    }
    if a0 is not None:
        c_mean, c_bin_spread = measure_prefactor_C(
            r, g, g_newton, a0, r_min, r_max
        )
        summary.update({
            "C_by_bin": (g[mask] / np.sqrt(a0 * g_newton[mask])).astype(float).tolist(),
            "C_mean": float(c_mean),
            "C_radial_bin_spread_not_uncertainty": float(c_bin_spread),
        })
    return summary


def _aqual_fluxes(result, a0, spacing, shell_radii):
    from kernel.aqual import make_conductivity

    grad_phi, _ = discrete_gradient(
        result["pos"], result["adj"], result["Phi"], spacing=spacing
    )
    conductivity = make_conductivity(a0, spacing)
    return {
        str(float(radius)): float(
            gauss_flux_through_shell(
                result["pos"], result["adj"], result["Phi"], grad_phi,
                radius, spacing, conductivity,
            )
        )
        for radius in shell_radii
    }


def run_kt6(N_values=None, M=50.0, G_eff=1.0, a0=2.0, box_side=20.0,
            r_source=2.0, output_dir=None, max_iter=500, tol=1e-4,
            run_source_radius_sensitivity=True, boundary_margin=1.5):
    """Run one-factor/combined source and observable controls.

    A/C use the old continuous-sphere node density (under-sampled mass) but
    the corrected AQUAL flux; B/D use a source normalized to target M. A/B
    emulate the old doubled vector-observable magnitude; C/D use the corrected
    observable. Each distinct source mass is solved once per N, then both
    observables are measured from that same solved field.
    """
    if N_values is None:
        N_values = [21, 31, 41]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "outputs", "runs", f"kt6_{run_id}"
        )
    os.makedirs(output_dir, exist_ok=True)

    r_mond = math.sqrt(G_eff * M / a0)
    radial_window = (max(5.0, r_mond), 9.0)
    shell_radii = [4.0, 6.0, 8.0, 10.0]
    results = []

    for N in N_values:
        metadata = experiment_metadata(
            N, M, G_eff, a0, box_side, r_source, boundary_margin
        )
        spacing = metadata["spacing"]
        positions, _, _ = build_cubic_lattice(N, spacing=spacing)
        r_arr = radial_distances(positions)
        measured_box_side = float(np.ptp(positions[:, 0]))
        if not np.isclose(measured_box_side, box_side, rtol=1e-12, atol=1e-12):
            raise ValueError(
                f"N={N}, h={spacing} gives box side {measured_box_side}, "
                f"expected {box_side}"
            )
        source_nodes, f_h = _mass_fraction(
            positions, r_arr, r_source, spacing
        )
        source_cases = [("unsampled_continuum_density", M * f_h),
                        ("node_volume_normalized", M)]
        run = {
            **metadata,
            "source_nodes": source_nodes,
            "continuous_sphere_volume": float((4.0 / 3.0) * np.pi * r_source ** 3),
            "unsampled_node_mass_fraction": float(f_h),
            "radial_window": [float(x) for x in radial_window],
            "shell_radii": [float(x) for x in shell_radii],
            "sources": {},
            "newton_linear": {},
        }

        for source_name, M_field in source_cases:
            start = time.time()
            field = solve_aqual(
                N=N,
                sources=[([0.0, 0.0, 0.0], M_field)],
                G_eff=G_eff,
                a0=a0,
                r_source=r_source,
                spacing=spacing,
                max_iter=max_iter,
                tol=tol,
                quiet=True,
                boundary_margin=boundary_margin,
            )
            elapsed = time.time() - start
            raw_observable = 2.0 * field["g_mag"]
            corrected_observable = field["g_mag"]
            is_under_sampled = source_name == "unsampled_continuum_density"
            labels = ("A_legacy_source_legacy_observable", "C_legacy_source_corrected_observable") if is_under_sampled else ("B_normalized_source_legacy_observable", "D_normalized_source_corrected_observable")
            run["sources"][source_name] = {
                "input_mass": float(M_field),
                "represented_mass": float(field["active_source_mass"]),
                "converged": bool(field["converged"]),
                "iterations": int(field["iterations"]),
                "final_change": float(field["final_change"]),
                "wall_time_s": float(elapsed),
                "aqual_gauss_flux": _aqual_fluxes(
                    field, a0, spacing, shell_radii
                ),
                "variants": {
                    labels[0]: _profile_summary(
                        field, raw_observable, M, G_eff, a0, radial_window,
                    ),
                    labels[1]: _profile_summary(
                        field, corrected_observable, M, G_eff, a0, radial_window,
                    ),
                },
            }

        start = time.time()
        newton = solve_linear_poisson(
            N=N, M=M, G_eff=G_eff, spacing=spacing, r_source=r_source,
            boundary_margin=boundary_margin,
        )
        elapsed = time.time() - start
        newton_profile = _profile_summary(
            newton, newton["g_mag"], M, G_eff, None, radial_window
        )
        grad_newton, _ = discrete_gradient(
            newton["pos"], newton["adj"], newton["Phi"], spacing=spacing
        )
        newton_profile["gauss_flux_by_shell"] = {
            str(float(radius)): float(
                gauss_flux_through_shell(
                    newton["pos"], newton["adj"], newton["Phi"],
                    grad_newton, radius, spacing, lambda _grad: 1.0,
                )
            )
            for radius in shell_radii
        }
        run["newton_linear"] = {
            "converged": True,
            "wall_time_s": float(elapsed),
            "profile": newton_profile,
        }
        results.append(run)
        print(
            f"KT6 N={N} h={spacing:.8f} f_h={f_h:.6f} "
            f"source_solves={len(source_cases)} complete; "
            f"D_C={run['sources']['node_volume_normalized']['variants']['D_normalized_source_corrected_observable']['C_mean']:.6f}",
            flush=True,
        )

    source_radius_sensitivity = []
    if run_source_radius_sensitivity:
        sensitivity_n = int(N_values[0])
        for sensitivity_radius in (0.75 * r_source, 1.25 * r_source):
            sensitivity_metadata = experiment_metadata(
                sensitivity_n, M, G_eff, a0, box_side,
                sensitivity_radius, boundary_margin,
            )
            sensitivity_h = sensitivity_metadata["spacing"]
            positions, _, _ = build_cubic_lattice(sensitivity_n, spacing=sensitivity_h)
            r_arr = radial_distances(positions)
            count, fraction = _mass_fraction(
                positions, r_arr, sensitivity_radius, sensitivity_h
            )
            start = time.time()
            field = solve_aqual(
                N=sensitivity_n,
                sources=[([0.0, 0.0, 0.0], M)],
                G_eff=G_eff,
                a0=a0,
                r_source=sensitivity_radius,
                spacing=sensitivity_h,
                max_iter=max_iter,
                tol=tol,
                quiet=True,
                boundary_margin=boundary_margin,
            )
            elapsed = time.time() - start
            source_radius_sensitivity.append({
                **sensitivity_metadata,
                "source_nodes": count,
                "unsampled_node_mass_fraction": fraction,
                "normalized_source_mass": float(M),
                "converged": bool(field["converged"]),
                "iterations": int(field["iterations"]),
                "wall_time_s": float(elapsed),
                "profile": _profile_summary(
                    field, field["g_mag"], M, G_eff, a0, radial_window
                ),
                "aqual_gauss_flux": _aqual_fluxes(
                    field, a0, sensitivity_h, shell_radii
                ),
            })
            print(
                f"KT6 source-radius sensitivity r_source={sensitivity_radius:.4f} "
                f"C={source_radius_sensitivity[-1]['profile']['C_mean']:.6f}",
                flush=True,
            )

    output = {
        "test": "KT6",
        "run_id": run_id,
        "description": "Physical normalization controls for continuum-calibrated Native v2 AQUAL",
        "scope": "generic standard AQUAL; not Lambda-locked EFC validation",
        "epistemic_status": "numerical calibration only; no physical C claim",
        "params": {
            "M": float(M), "G_eff": float(G_eff), "a0": float(a0),
            "box_side": float(box_side), "r_source": float(r_source),
            "unit_system": "dimensionless code units; no SI mapping asserted",
            "boundary_condition": (
                "Dirichlet Phi=0 pinned on the spherical margin shell "
                "(boundary_mask: r > r_max - boundary_margin*h); outer cube "
                "faces are graph-truncated and not Dirichlet-pinned"
            ),
            "boundary_margin": float(boundary_margin),
            "max_iter": int(max_iter), "tol": float(tol),
        },
        "results": results,
        "source_radius_sensitivity": source_radius_sensitivity,
    }
    outpath = os.path.join(output_dir, "kt6_physical_normalization.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"KT6 output: {outpath}", flush=True)
    return output


if __name__ == "__main__":
    run_kt6()
