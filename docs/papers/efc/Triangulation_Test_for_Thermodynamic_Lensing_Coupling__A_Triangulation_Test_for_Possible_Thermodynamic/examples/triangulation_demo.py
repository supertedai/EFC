"""
Example: Triangulation Test Analysis

Demonstrates the triangulation methodology on simulated cluster data.
"""

import numpy as np
import sys
sys.path.insert(0, '..')

from src.triangulation_test import (
    TriangulationAnalysis,
    ClusterData,
    stacked_detection_threshold
)


def create_mock_merging_cluster():
    """Create mock data for a merging cluster (Bullet-like)."""
    # Radial bins from 50 to 1500 kpc
    r = np.linspace(50, 1500, 57)  # kpc

    # Mock lensing mass profile (NFW-like)
    M_200 = 1.5e15  # M_sun
    c = 4.0  # concentration
    r_s = 375  # scale radius kpc
    x = r / r_s
    M_lens = M_200 * (np.log(1 + x) - x/(1 + x)) / (np.log(1 + c) - c/(1 + c))

    # Mock temperature profile with shock
    T_base = 10.0  # keV
    T = T_base * (1 + 0.5 * np.exp(-(r - 500)**2 / 100**2))  # Shock at 500 kpc

    # Mock density profile
    n_0 = 0.01  # cm^-3
    r_c = 200  # core radius kpc
    beta = 0.67
    n_e = n_0 * (1 + (r/r_c)**2)**(-1.5*beta)

    return ClusterData(
        name="Mock Bullet-like Cluster",
        cluster_type="merging",
        r_bins=r,
        M_lens=M_lens,
        M_lens_err=M_lens * 0.1,
        T_profile=T,
        n_e_profile=n_e
    )


def create_mock_relaxed_cluster():
    """Create mock data for a relaxed cluster (Abell 1835-like)."""
    r = np.linspace(50, 1500, 50)

    # Smooth NFW profile
    M_200 = 1.2e15
    c = 5.0
    r_s = 240
    x = r / r_s
    M_lens = M_200 * (np.log(1 + x) - x/(1 + x)) / (np.log(1 + c) - c/(1 + c))

    # Smooth temperature profile (cool core)
    T = 8.0 * (r / (r + 100))  # keV, rising from cool core

    # Smooth density profile
    n_0 = 0.05
    r_c = 50
    beta = 0.6
    n_e = n_0 * (1 + (r/r_c)**2)**(-1.5*beta)

    return ClusterData(
        name="Mock Relaxed Cluster",
        cluster_type="relaxed",
        r_bins=r,
        M_lens=M_lens,
        M_lens_err=M_lens * 0.08,
        T_profile=T,
        n_e_profile=n_e
    )


def main():
    print("=" * 60)
    print("Triangulation Test for Thermodynamic-Lensing Coupling")
    print("=" * 60)
    print()

    # Analyze mock merging cluster
    print("1. MERGING CLUSTER ANALYSIS")
    print("-" * 40)

    merging_data = create_mock_merging_cluster()
    merging_analysis = TriangulationAnalysis(merging_data)

    # Compute quantities
    K = merging_analysis.compute_entropy()
    grad_K = merging_analysis.compute_entropy_gradient()
    M_HSE = merging_analysis.compute_hydrostatic_mass()
    R = merging_analysis.compute_mass_residual()

    print(f"Cluster: {merging_data.name}")
    print(f"Entropy range: {K.min():.1f} - {K.max():.1f} keV cm²")
    print(f"Max entropy gradient: {grad_K.max():.2e} keV cm² / kpc")
    print(f"Mean M_lens/M_HSE ratio: {np.mean(merging_data.M_lens / M_HSE):.2f}")
    print()

    # Run correlation test
    results = merging_analysis.correlation_test()
    print("Correlation Test Results:")
    print(f"  Pearson ρ  = {results['pearson_rho']:.3f} (p = {results['pearson_p']:.3f})")
    print(f"  Spearman ρ = {results['spearman_rho']:.3f} (p = {results['spearman_p']:.3f})")
    print(f"  Required |ρ| for 2σ: {results['rho_required_2sigma']:.3f}")
    print(f"  Significant: {results['significant_2sigma']}")
    print(f"  Interpretation: {results['interpretation']}")
    print()

    # Analyze mock relaxed cluster
    print("2. RELAXED CLUSTER ANALYSIS (Control)")
    print("-" * 40)

    relaxed_data = create_mock_relaxed_cluster()
    relaxed_analysis = TriangulationAnalysis(relaxed_data)

    print(relaxed_analysis.summary())

    # Detection thresholds for stacked samples
    print("3. DETECTION THRESHOLDS FOR STACKED SAMPLES")
    print("-" * 40)
    print()
    print("| N_clusters | N_eff | Detectable ρ (3σ) |")
    print("|------------|-------|-------------------|")

    for n_clusters in [10, 20, 50, 100]:
        rho_min = stacked_detection_threshold(n_clusters, bins_per_cluster=57, sigma=3.0)
        n_eff = n_clusters * 57
        print(f"| {n_clusters:10d} | {n_eff:5d} | {rho_min:17.3f} |")

    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print("""
The triangulation test compares:
  1. M_lens(r) - Lensing mass (geometric)
  2. M_HSE(r)  - Hydrostatic mass (dynamic)
  3. |∇K(r)|  - Entropy gradient (thermodynamic)

Expected behavior:
  - ΛCDM (null): ρ ≈ 0, R from non-thermal pressure
  - Thermodynamic coupling: ρ > 0 if κ ∝ ∇²K

Current pilot results (Bullet Cluster):
  - ρ = -0.129, p = 0.21 (not significant)
  - Consistent with sensitivity limits for %-level effects
  - Larger samples (20-50 clusters) needed for decisive test
""")


if __name__ == "__main__":
    main()
