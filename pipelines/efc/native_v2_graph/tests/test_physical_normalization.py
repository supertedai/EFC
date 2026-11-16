"""Numerical regression tests for the continuum-calibrated graph operators."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kernel.graph import build_cubic_lattice, radial_distances
from kernel.fields import multi_source_density, point_source_density
from kernel.operators import (
    discrete_gradient,
    gauss_flux_through_shell,
    graph_laplacian,
    weighted_laplacian,
)
from kernel.aqual import make_conductivity, mu_standard
from kernel.observables import measure_slope, radial_g_profile_vector, radial_profile
from tests.kt2_C_convergence import fixed_h_convergence_status
from tests.kt6_physical_normalization import experiment_metadata
from kernel.solver import solve_aqual, solve_linear_poisson


def _node_index(positions, target):
    return int(np.argmin(np.linalg.norm(positions - np.asarray(target), axis=1)))


def test_kt6_metadata_records_code_units_and_dirichlet_boundary():
    metadata = experiment_metadata(
        N=21, M=50.0, G_eff=1.0, a0=2.0, box_side=20.0,
        r_source=2.0, boundary_margin=1.5,
    )
    assert metadata["unit_system"] == "dimensionless code units; no SI mapping asserted"
    assert metadata["boundary_condition"].startswith("Dirichlet Phi=0")
    assert "boundary_mask" in metadata["boundary_condition"]
    assert "spherical margin shell" in metadata["boundary_condition"]
    assert "graph-truncated" in metadata["boundary_treatment"]
    assert "not Dirichlet-pinned" in metadata["boundary_treatment"]
    assert "pre-existing solver behaviour" in metadata["boundary_treatment"]
    assert metadata["boundary_margin"] == 1.5
    assert metadata["spacing"] == 1.0
    assert metadata["box_side"] == 20.0
    assert metadata["source_mask_rule"] == "distance < r_source"


def test_legacy_kt2_labels_fixed_h_sweep_as_domain_trend_only():
    assert fixed_h_convergence_status([2.44, 2.35, 2.32], spacing=1.0) == \
        "fixed_h_domain_size_trend_only"


def test_constant_potential_has_zero_gradient_at_interior_and_boundary():
    positions, adjacency, _ = build_cubic_lattice(5, spacing=0.5)
    phi = np.full(len(positions), 7.0)
    gradient, magnitude = discrete_gradient(positions, adjacency, phi)

    assert np.allclose(gradient, 0.0, atol=1e-12)
    assert np.allclose(magnitude, 0.0, atol=1e-12)


def test_axis_linear_potential_returns_signed_physical_gradient():
    positions, adjacency, _ = build_cubic_lattice(5, spacing=0.5)
    phi = positions[:, 0]
    gradient, magnitude = discrete_gradient(positions, adjacency, phi)

    interior = _node_index(positions, (0.0, 0.0, 0.0))
    boundary = _node_index(positions, (-1.0, 0.0, 0.0))
    expected = np.array([1.0, 0.0, 0.0])

    assert np.allclose(gradient[interior], expected, atol=1e-12)
    assert np.isclose(magnitude[interior], 1.0, atol=1e-12)
    assert np.allclose(gradient[boundary], expected, atol=1e-12)


def test_diagonal_linear_potential_returns_full_gradient_norm():
    positions, adjacency, _ = build_cubic_lattice(5, spacing=0.5)
    expected = np.array([1.0, 2.0, -3.0])
    phi = positions @ expected
    gradient, magnitude = discrete_gradient(positions, adjacency, phi)

    interior = _node_index(positions, (0.0, 0.0, 0.0))
    assert np.allclose(gradient[interior], expected, atol=1e-12)
    assert np.isclose(magnitude[interior], np.sqrt(14.0), atol=1e-12)


@pytest.mark.parametrize(("spacing", "n_grid"), [(1.0, 9), (0.5, 17), (0.25, 33)])
def test_point_source_rhs_integrates_to_declared_mass(spacing, n_grid):
    positions, _, _ = build_cubic_lattice(n_grid, spacing=spacing)
    radii = radial_distances(positions)
    mass = 8.0
    gravitational_constant = 1.7
    rho = point_source_density(
        positions, radii, mass, r_source=2.0, spacing=spacing
    )

    # The sampled density, not the field RHS, must integrate to the target mass.
    represented_mass = np.sum(rho) * spacing ** 3
    assert np.isclose(represented_mass, mass, rtol=1e-12, atol=1e-12)


def test_graph_laplacian_quadratic_scaling_is_minus_six_h_squared():
    for spacing in (0.5, 1.0, 2.0):
        positions, adjacency, degree = build_cubic_lattice(5, spacing=spacing)
        phi = np.sum(positions ** 2, axis=1)
        laplacian = graph_laplacian(adjacency, degree, len(positions)).tocsr()
        center = _node_index(positions, (0.0, 0.0, 0.0))

        assert np.isclose((laplacian @ phi)[center], -6.0 * spacing ** 2)


def test_linear_solver_applies_physical_h_to_source_rhs():
    spacing = 0.5
    mass = 8.0
    gravitational_constant = 1.7
    result = solve_linear_poisson(
        N=17,
        M=mass,
        G_eff=gravitational_constant,
        spacing=spacing,
        r_source=2.0,
    )

    assert np.isclose(
        np.sum(result["rho"]) * spacing ** 3, mass, rtol=1e-12, atol=1e-12
    )
    assert np.allclose(
        result["rhs"],
        -4.0 * np.pi * gravitational_constant * result["rho"] * spacing ** 2,
        rtol=1e-12,
        atol=1e-12,
    )


def test_aqual_face_mu_uses_full_diagonal_gradient_norm():
    spacing = 0.5
    a0 = 2.0
    positions, adjacency, _ = build_cubic_lattice(5, spacing=spacing)
    gradient = np.array([1.0, 2.0, -3.0])
    phi = positions @ gradient
    boundary = np.zeros(len(positions), dtype=bool)
    conductivity = make_conductivity(a0, spacing)
    gradients, _ = discrete_gradient(positions, adjacency, phi, spacing=spacing)
    operator = weighted_laplacian(
        adjacency,
        conductivity,
        phi,
        len(positions),
        boundary,
        gradient_vectors=gradients,
    ).tocsr()

    center = _node_index(positions, (0.0, 0.0, 0.0))
    x_neighbor = _node_index(positions, (spacing, 0.0, 0.0))
    y_neighbor = _node_index(positions, (0.0, spacing, 0.0))
    z_neighbor = _node_index(positions, (0.0, 0.0, spacing))
    expected_face_weight = mu_standard(np.linalg.norm(gradient) / a0)

    for neighbor in (x_neighbor, y_neighbor, z_neighbor):
        assert np.isclose(-operator[center, neighbor], expected_face_weight, rtol=1e-12)
        assert np.isclose(-operator[neighbor, center], expected_face_weight, rtol=1e-12)


def test_aqual_face_mu_uses_axis_gradient_norm_for_transverse_faces():
    spacing = 0.5
    a0 = 2.0
    positions, adjacency, _ = build_cubic_lattice(5, spacing=spacing)
    phi = positions[:, 0]
    boundary = np.zeros(len(positions), dtype=bool)
    gradients, _ = discrete_gradient(positions, adjacency, phi, spacing=spacing)
    operator = weighted_laplacian(
        adjacency,
        make_conductivity(a0, spacing),
        phi,
        len(positions),
        boundary,
        gradient_vectors=gradients,
    ).tocsr()

    center = _node_index(positions, (0.0, 0.0, 0.0))
    neighbors = [
        _node_index(positions, (spacing, 0.0, 0.0)),
        _node_index(positions, (0.0, spacing, 0.0)),
        _node_index(positions, (0.0, 0.0, spacing)),
    ]
    expected_weight = mu_standard(1.0 / a0)
    for neighbor in neighbors:
        assert np.isclose(-operator[center, neighbor], expected_weight, rtol=1e-12)



def test_multi_source_rhs_integrates_to_sum_of_masses():
    spacing = 0.5
    positions, _, _ = build_cubic_lattice(17, spacing=spacing)
    sources = [([-1.0, 0.0, 0.0], 3.0), ([1.0, 0.0, 0.0], 5.0)]
    rho = multi_source_density(
        positions, sources, r_source=1.0, spacing=spacing
    )

    assert np.isclose(np.sum(rho) * spacing ** 3, 8.0, rtol=1e-12, atol=1e-12)


def _outward_flux_through_node_shell(result, radius, a0, spacing):
    grad_phi, _ = discrete_gradient(
        result["pos"], result["adj"], result["Phi"], spacing=spacing
    )
    conductivity = make_conductivity(a0, spacing)
    return gauss_flux_through_shell(
        result["pos"],
        result["adj"],
        result["Phi"],
        grad_phi,
        radius,
        spacing,
        conductivity,
    )


def test_aqual_gauss_flux_matches_enclosed_source_on_multiple_shells():
    gravitational_constant = 1.0
    mass = 1.0
    a0 = 0.1
    spacing = 1.0
    result = solve_aqual(
        N=11,
        sources=[([0.0, 0.0, 0.0], mass)],
        G_eff=gravitational_constant,
        a0=a0,
        r_source=1.0,
        spacing=spacing,
        max_iter=500,
        tol=1e-6,
        quiet=True,
    )
    assert result["converged"]

    expected_flux = 4.0 * np.pi * gravitational_constant * mass
    for radius in (2.0, 3.0, 4.0):
        measured_flux = _outward_flux_through_node_shell(
            result, radius, a0, spacing
        )
        assert np.isclose(measured_flux, expected_flux, rtol=2e-3, atol=2e-3)


def test_linear_solver_vector_acceleration_points_toward_source():
    result = solve_linear_poisson(
        N=9, M=1.0, G_eff=1.0, spacing=1.0, r_source=1.0
    )
    node = _node_index(result["pos"], (3.0, 0.0, 0.0))
    assert result["g_vec"][node, 0] < 0.0
    assert np.isclose(
        np.linalg.norm(result["g_vec"][node]), result["g_mag"][node], rtol=1e-12
    )

    radii, radial_field, _, _ = radial_g_profile_vector(
        result["pos"], result["g_vec"], result["r_arr"], result["boundary"]
    )
    bin_index = int(np.argmin(np.abs(radii - 3.5)))
    assert radial_field[bin_index] > 0.0


def test_newton_point_source_has_correct_amplitude_and_slope_at_fixed_box():
    target_mass = 50.0
    gravitational_constant = 1.0
    box_side = 20.0
    expected_bins = np.array([4.5, 5.5, 6.5, 7.5, 8.5])

    for n_grid in (21, 31, 41):
        spacing = box_side / (n_grid - 1)
        result = solve_linear_poisson(
            N=n_grid,
            M=target_mass,
            G_eff=gravitational_constant,
            spacing=spacing,
            r_source=2.0,
        )
        radii, g_profile, _, counts = radial_profile(
            result["pos"], result["r_arr"], result["g_mag"], result["boundary"]
        )
        mask = np.isin(radii, expected_bins) & (counts > 0)
        assert np.array_equal(radii[mask], expected_bins)

        amplitude = g_profile[mask] / (
            gravitational_constant * target_mass / expected_bins ** 2
        )
        assert np.all(np.abs(amplitude - 1.0) < 0.12)
        slope, n_points = measure_slope(radii, g_profile, 4.0, 9.0)
        assert n_points == len(expected_bins)
        assert abs(slope + 2.0) < 0.15


def test_aqual_rejects_source_support_overlapping_boundary_mask():
    # N=9, h=1: the Dirichlet pin is the spherical shell r > r_max - 1.5h
    # (r_max = 6.928, so the shell is r > 5.428). A source centred at the
    # corner [4,4,4] (r = 6.928) has support overlapping the pinned shell;
    # its mass would be dropped from the solved equation, so the solver must
    # reject it rather than silently under-report the solved mass.
    with pytest.raises(ValueError, match="boundary mask"):
        solve_aqual(
            N=9,
            sources=[([4.0, 4.0, 4.0], 1.0)],
            G_eff=1.0,
            a0=2.0,
            r_source=2.0,
            spacing=1.0,
            max_iter=2,
            tol=1e-3,
            quiet=True,
        )


def test_aqual_accepts_central_source_and_reports_full_active_mass():
    spacing = 1.0
    mass = 1.0
    result = solve_aqual(
        N=9,
        sources=[([0.0, 0.0, 0.0], mass)],
        G_eff=1.0,
        a0=2.0,
        r_source=1.0,
        spacing=spacing,
        max_iter=2,
        tol=1e-3,
        quiet=True,
    )
    # The central source does not touch the boundary shell, so the mass that
    # enters the solved equation equals the declared discrete mass.
    assert np.isclose(result["active_source_mass"], mass, rtol=1e-12, atol=1e-12)
    assert np.isclose(
        np.sum(result["rho"]) * spacing ** 3, mass, rtol=1e-12, atol=1e-12
    )


def test_linear_solver_reports_active_source_mass_equal_to_total():
    spacing = 1.0
    mass = 1.0
    result = solve_linear_poisson(
        N=9, M=mass, G_eff=1.0, spacing=spacing, r_source=1.0
    )
    assert np.isclose(result["active_source_mass"], mass, rtol=1e-12, atol=1e-12)
