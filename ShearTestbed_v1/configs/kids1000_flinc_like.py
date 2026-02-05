"""
Simple KiDS-1000 Flinc likelihood module for CosmoSIS.
Reads pre-cut xipm data in ASCII format (195 data points).
"""

import numpy as np
from cosmosis.datablock import option_section, names


def setup(options):
    """Load KiDS-1000 Flinc data and covariance."""

    data_file = options.get_string(option_section, "data_file")
    cov_file = options.get_string(option_section, "cov_file")
    like_name = options.get_string(option_section, "like_name", default="kids1000_flinc")

    # KiDS-1000 configuration
    n_bin = 5  # tomographic bins
    n_theta_plus = 7  # xi+ bins (9 - 2 large-scale cut)
    n_theta_minus = 6  # xi- bins (9 - 3 small-scale cut)

    # Angular bins: 9 log-spaced bins from 0.5' to 300'
    theta_edges = np.array([0.5, 1.01777898, 2.0717481, 4.21716333, 8.58428037,
                            17.4738002, 35.56893304, 72.40262468, 147.37973879, 300.0])
    theta_centers = np.sqrt(theta_edges[:-1] * theta_edges[1:])  # geometric mean

    # Scale cuts applied:
    # xi+: keep bins 0-6 (cut bins 7,8 - largest theta)
    # xi-: keep bins 3-8 (cut bins 0,1,2 - smallest theta)
    theta_plus = theta_centers[:n_theta_plus]  # first 7 bins
    theta_minus = theta_centers[3:]  # last 6 bins (bins 3-8)

    # Convert to radians
    theta_plus_rad = theta_plus * np.pi / 180 / 60
    theta_minus_rad = theta_minus * np.pi / 180 / 60

    # Load data vector (195 points: 105 xi+ + 90 xi-)
    data = np.loadtxt(data_file)
    n_data = len(data)

    # Load covariance matrix (195 x 195)
    cov = np.loadtxt(cov_file)

    # Invert covariance
    inv_cov = np.linalg.inv(cov)

    # Number of pairs: 5 bins -> 15 pairs (auto + cross)
    n_pairs = n_bin * (n_bin + 1) // 2

    config = {
        'data': data,
        'inv_cov': inv_cov,
        'n_bin': n_bin,
        'n_pairs': n_pairs,
        'n_theta_plus': n_theta_plus,
        'n_theta_minus': n_theta_minus,
        'theta_plus': theta_plus_rad,
        'theta_minus': theta_minus_rad,
        'like_name': like_name,
    }

    print(f"KiDS-1000 Flinc likelihood loaded:")
    print(f"  Data points: {n_data}")
    print(f"  Covariance: {cov.shape}")
    print(f"  Tomographic bins: {n_bin}")
    print(f"  xi+ theta bins: {n_theta_plus}")
    print(f"  xi- theta bins: {n_theta_minus}")

    return config


def execute(block, config):
    """Compute likelihood."""

    data = config['data']
    inv_cov = config['inv_cov']
    n_bin = config['n_bin']
    n_pairs = config['n_pairs']
    n_theta_plus = config['n_theta_plus']
    n_theta_minus = config['n_theta_minus']
    theta_plus = config['theta_plus']
    theta_minus = config['theta_minus']
    like_name = config['like_name']

    # Build theory vector from CosmoSIS datablock
    theory = []

    # Get xi+ for all pairs
    pair_idx = 0
    for i in range(1, n_bin + 1):
        for j in range(1, i + 1):
            # Read shear_xi_plus for this bin pair
            xi_plus = block['shear_xi_plus', f'bin_{i}_{j}']
            theta = block['shear_xi_plus', 'theta']

            # Interpolate to our angular bins
            from scipy.interpolate import InterpolatedUnivariateSpline
            interp = InterpolatedUnivariateSpline(np.log(theta), xi_plus)
            xi_plus_binned = interp(np.log(theta_plus))

            theory.extend(xi_plus_binned)
            pair_idx += 1

    # Get xi- for all pairs
    pair_idx = 0
    for i in range(1, n_bin + 1):
        for j in range(1, i + 1):
            # Read shear_xi_minus for this bin pair
            xi_minus = block['shear_xi_minus', f'bin_{i}_{j}']
            theta = block['shear_xi_minus', 'theta']

            # Interpolate to our angular bins
            from scipy.interpolate import InterpolatedUnivariateSpline
            interp = InterpolatedUnivariateSpline(np.log(theta), xi_minus)
            xi_minus_binned = interp(np.log(theta_minus))

            theory.extend(xi_minus_binned)
            pair_idx += 1

    theory = np.array(theory)

    # Compute chi-squared
    diff = data - theory
    chi2 = diff @ inv_cov @ diff

    # Log-likelihood
    like = -0.5 * chi2

    # Save to datablock
    block[names.likelihoods, like_name + '_like'] = like
    block[names.data_vector, like_name + '_chi2'] = chi2
    block[names.data_vector, like_name + '_theory'] = theory
    block[names.data_vector, like_name + '_data'] = data

    return 0


def cleanup(config):
    pass
