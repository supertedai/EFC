"""
Observables: g(r), slopes, C-factor, EFE curves, mass scaling beta.

All measurements from the solved field, ready for comparison with
LCDM pipeline or data (SPARC etc).
"""
import numpy as np


def radial_profile(pos, r_arr, field, boundary, r_max_frac=0.85,
                   center=None, volume_weighted=True):
    """
    Radial binning of a scalar field.

    Returns (r_bins, f_binned) arrays.
    """
    if center is None:
        center = np.array([0.0, 0.0, 0.0])
    r_from_center = np.linalg.norm(pos - center, axis=1)
    r_limit = r_max_frac * np.max(r_arr)

    r_bins = np.arange(2.5, r_limit, 1.0)
    f_binned = np.zeros(len(r_bins))
    f_std = np.zeros(len(r_bins))
    counts = np.zeros(len(r_bins), dtype=int)

    for k, rb in enumerate(r_bins):
        mask = (r_from_center > rb - 0.5) & (r_from_center < rb + 0.5) & (~boundary)
        cnt = np.sum(mask)
        if cnt > 0:
            if volume_weighted:
                w = 1.0 / (4.0 * np.pi * r_from_center[mask] ** 2 + 1e-10)
                w /= np.sum(w)
                f_binned[k] = np.sum(w * field[mask])
            else:
                f_binned[k] = np.mean(field[mask])
            f_std[k] = np.std(field[mask])
            counts[k] = cnt

    return r_bins, f_binned, f_std, counts


def measure_slope(r, g, r_min, r_max):
    """
    Power-law slope d(log g)/d(log r) in a radial window.

    Returns (slope, n_points).
    """
    mask = (r > r_min) & (r < r_max) & (g > 0)
    n_pts = int(np.sum(mask))
    if n_pts < 3:
        return np.nan, n_pts
    coeffs = np.polyfit(np.log10(r[mask]), np.log10(g[mask]), 1)
    return float(coeffs[0]), n_pts


def measure_prefactor_C(r, g, g_newton, a0, r_min, r_max):
    """
    C = g_AQUAL / g_MOND where g_MOND = sqrt(a0 * g_N).

    Measured in a radial window. Returns (C_mean, C_std).
    """
    mask = (r > r_min) & (r < r_max) & (g > 0) & (g_newton > 0)
    if np.sum(mask) < 2:
        return np.nan, np.nan
    g_mond = np.sqrt(a0 * g_newton[mask])
    C_vals = g[mask] / g_mond
    return float(np.mean(C_vals)), float(np.std(C_vals))


def find_transition_radius(r, g, g_newton, threshold=1.5, r_min=3.0):
    """
    Find radius where g/g_N first exceeds threshold.

    Returns r_transition or NaN.
    """
    mask = (g > 0) & (g_newton > 0) & (r > r_min)
    if np.sum(mask) < 2:
        return np.nan
    ratio = g[mask] / g_newton[mask]
    r_valid = r[mask]
    idx = np.where(ratio > threshold)[0]
    if len(idx) == 0:
        return np.nan
    return float(r_valid[idx[0]])


def find_transition_radius_slope(r, g, window=3.0, slope_threshold=-1.5):
    """
    Alternative: find radius where local slope crosses threshold.

    More robust than ratio-based detection for mass-scaling test.
    """
    mask = (g > 0)
    r_valid = r[mask]
    g_valid = g[mask]

    if len(r_valid) < 5:
        return np.nan

    for i in range(2, len(r_valid) - 2):
        r_lo, r_hi = r_valid[i - 1], r_valid[i + 1]
        g_lo, g_hi = g_valid[i - 1], g_valid[i + 1]
        if g_lo > 0 and g_hi > 0 and r_lo > 0 and r_hi > 0:
            local_slope = (np.log10(g_hi) - np.log10(g_lo)) / \
                          (np.log10(r_hi) - np.log10(r_lo))
            if local_slope > slope_threshold:
                return float(r_valid[i])

    return np.nan


def rolling_log_slope(r, g, half_window=2):
    """
    Compute continuous d(log g)/d(log r) with a rolling linear fit.

    Returns (r_centers, slopes) arrays, trimmed to valid interior.
    """
    mask = (g > 0) & (r > 0)
    r_v = r[mask]
    g_v = g[mask]
    n = len(r_v)

    if n < 2 * half_window + 1:
        return np.array([]), np.array([])

    lr = np.log10(r_v)
    lg = np.log10(g_v)
    r_centers = []
    slopes = []

    for i in range(half_window, n - half_window):
        lo, hi = i - half_window, i + half_window + 1
        if hi - lo >= 3:
            coeffs = np.polyfit(lr[lo:hi], lg[lo:hi], 1)
            slopes.append(coeffs[0])
            r_centers.append(r_v[i])

    return np.array(r_centers), np.array(slopes)


def find_transition_gN_crossing(r, g, G_eff, M, a0, slope_threshold=-1.5,
                                half_window=2):
    """
    Find transition radius where g_N(r) ~ a0 and slope changes.

    Strategy:
      1. Compute r_MOND = sqrt(GM/a0) — the theoretical crossing point
      2. Compute rolling log-slope
      3. Find where slope crosses threshold NEAR r_MOND
         (within factor 3 of r_MOND, to avoid grid-edge artefacts)
      4. Also interpolate actual crossing of slope = threshold

    Returns dict with r_trans, r_mond_pred, slope_at_crossing.
    """
    r_mond = np.sqrt(G_eff * M / a0)
    r_centers, slopes = rolling_log_slope(r, g, half_window)

    if len(r_centers) == 0:
        return {'r_trans': np.nan, 'r_mond_pred': r_mond,
                'slope_at_crossing': np.nan, 'method': 'rolling_slope'}

    # Search window: r_MOND/3 to 3*r_MOND (but clamp to available range)
    r_lo = max(r_mond / 3.0, r_centers[0])
    r_hi = min(r_mond * 3.0, r_centers[-1])
    window = (r_centers >= r_lo) & (r_centers <= r_hi)

    if np.sum(window) < 2:
        # Fallback: use full range
        window = np.ones(len(r_centers), dtype=bool)

    rc_w = r_centers[window]
    sl_w = slopes[window]

    # Find interpolated crossing of slope_threshold
    for i in range(len(sl_w) - 1):
        if sl_w[i] < slope_threshold <= sl_w[i + 1]:
            # Linear interpolation
            frac = (slope_threshold - sl_w[i]) / (sl_w[i + 1] - sl_w[i])
            r_cross = rc_w[i] + frac * (rc_w[i + 1] - rc_w[i])
            return {'r_trans': float(r_cross), 'r_mond_pred': float(r_mond),
                    'slope_at_crossing': float(slope_threshold),
                    'method': 'rolling_slope_interp'}
        if sl_w[i] >= slope_threshold and i == 0:
            # Already past threshold at start of window
            return {'r_trans': float(rc_w[0]), 'r_mond_pred': float(r_mond),
                    'slope_at_crossing': float(sl_w[0]),
                    'method': 'rolling_slope_start'}

    # No crossing found — slope never reaches threshold in window
    # Return radius of flattest slope as best estimate
    i_flat = np.argmax(sl_w)
    return {'r_trans': float(rc_w[i_flat]), 'r_mond_pred': float(r_mond),
            'slope_at_crossing': float(sl_w[i_flat]),
            'method': 'rolling_slope_flattest'}


def radial_g_profile_vector(pos, g_vec, r_arr, boundary, r_max_frac=0.85):
    """
    Radial profile of g_radial = g_vec dot r_hat.

    This measures the radial component of acceleration, not |g|.
    Correct for EFE measurement where external field must be subtracted
    vectorially before projecting onto radial direction.
    """
    r_limit = r_max_frac * np.max(r_arr)
    r_bins = np.arange(2.5, r_limit, 1.0)
    g_radial_binned = np.zeros(len(r_bins))
    g_radial_std = np.zeros(len(r_bins))
    counts = np.zeros(len(r_bins), dtype=int)

    # r_hat for each node
    r_hat = np.zeros_like(pos)
    nonzero = r_arr > 1e-10
    r_hat[nonzero] = pos[nonzero] / r_arr[nonzero, np.newaxis]

    # g_vec from discrete_gradient = grad(Phi), points OUTWARD (toward
    # increasing Phi). The radial gravitational acceleration magnitude is
    # |g_radial| = g_vec . r_hat (both point outward, so dot product > 0).
    g_dot_rhat = np.sum(g_vec * r_hat, axis=1)

    for k, rb in enumerate(r_bins):
        mask = ((r_arr > rb - 0.5) & (r_arr < rb + 0.5) & (~boundary))
        cnt = np.sum(mask)
        if cnt > 0:
            # Volume-weighted
            w = 1.0 / (4.0 * np.pi * r_arr[mask] ** 2 + 1e-10)
            w /= np.sum(w)
            g_radial_binned[k] = np.sum(w * g_dot_rhat[mask])
            g_radial_std[k] = np.std(g_dot_rhat[mask])
            counts[k] = cnt

    return r_bins, g_radial_binned, g_radial_std, counts


def superposition_violation(Phi_AB, Phi_A, Phi_B, boundary):
    """
    Measure superposition violation: delta_Phi = Phi_AB - (Phi_A + Phi_B).

    Returns dict with RMS, max, and normalized values.
    """
    interior = ~boundary
    delta = Phi_AB - (Phi_A + Phi_B)
    Phi_scale = np.max(np.abs(Phi_AB[interior]))

    rms = float(np.sqrt(np.mean(delta[interior] ** 2)))
    max_abs = float(np.max(np.abs(delta[interior])))

    return {
        'delta_Phi': delta,
        'rms': rms,
        'max_abs': max_abs,
        'rms_normalized': rms / (Phi_scale + 1e-30),
        'max_normalized': max_abs / (Phi_scale + 1e-30),
    }


def efe_enhancement(pos, g_mag, r_arr, boundary, G_eff, M,
                    r_min=6.0, r_max=12.0):
    """
    Measure MOND enhancement g/g_N in a radial window.

    For EFE test: compare enhancement with and without external field.
    """
    r_bins, g_profile, _, _ = radial_profile(pos, r_arr, g_mag, boundary)
    g_newton = G_eff * M / r_bins ** 2

    mask = (r_bins > r_min) & (r_bins < r_max) & (g_profile > 0) & (g_newton > 0)
    if np.sum(mask) < 2:
        return np.nan, r_bins, g_profile, g_newton

    enhancement = float(np.mean(g_profile[mask] / g_newton[mask]))
    return enhancement, r_bins, g_profile, g_newton
