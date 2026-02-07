"""
TO-CS-02: Omega (Differentiation) Computation
Computes Permutation Entropy (PE) and Spectral Entropy (SE) per ROI.

Locked parameters (Appendix B):
- SE: Welch PSD, normalised
- PE: order=3
- Bands: full (0.5-45 Hz), delta-free (4-40 Hz)
"""

import numpy as np
from scipy import signal
from itertools import permutations


def permutation_entropy(x, order=3, delay=1, normalize=True):
    """
    Compute permutation entropy of a time series.

    Parameters
    ----------
    x : np.ndarray, 1D time series
    order : int, embedding dimension (default 3, locked)
    delay : int, time delay (default 1)
    normalize : bool, normalise by log(order!)

    Returns
    -------
    pe : float, permutation entropy value
    """
    n = len(x)
    n_perms = np.math.factorial(order)

    # Create embedded vectors
    embedded = np.array([x[i * delay:i * delay + order] for i in range((n - (order - 1) * delay))])

    # Get ordinal patterns
    patterns = np.array([tuple(np.argsort(vec)) for vec in embedded])

    # Count unique patterns
    unique, counts = np.unique(patterns, axis=0, return_counts=True)
    probs = counts / counts.sum()

    # Shannon entropy
    pe = -np.sum(probs * np.log2(probs))

    if normalize:
        pe /= np.log2(n_perms)

    return pe


def spectral_entropy(x, sfreq, method='welch', nperseg=None, normalize=True):
    """
    Compute spectral entropy of a time series.

    Parameters
    ----------
    x : np.ndarray, 1D time series
    sfreq : float, sampling frequency
    method : str, PSD method (locked: 'welch')
    nperseg : int, segment length for Welch (default: sfreq*2)
    normalize : bool, normalise to [0, 1]

    Returns
    -------
    se : float, spectral entropy value
    """
    if nperseg is None:
        nperseg = min(int(sfreq * 2), len(x))

    freqs, psd = signal.welch(x, fs=sfreq, nperseg=nperseg)

    # Normalise PSD to probability distribution
    psd_norm = psd / psd.sum()

    # Remove zeros
    psd_norm = psd_norm[psd_norm > 0]

    # Shannon entropy of the normalised PSD
    se = -np.sum(psd_norm * np.log2(psd_norm))

    if normalize:
        se /= np.log2(len(psd_norm))

    return se


def compute_omega_for_condition(roi_signals, sfreq, pe_order=3):
    """
    Compute Omega (PE and SE) for all ROIs in one condition.

    Parameters
    ----------
    roi_signals : dict, {roi_name: np.ndarray (n_epochs, n_samples)}
    sfreq : float, sampling frequency
    pe_order : int, PE embedding order (locked: 3)

    Returns
    -------
    omega : dict with keys:
        'PE': {roi_name: np.ndarray (n_epochs,)}
        'SE': {roi_name: np.ndarray (n_epochs,)}
        'PE_mean': {roi_name: float}
        'SE_mean': {roi_name: float}
        'PE_global': float (mean across ROIs)
        'SE_global': float (mean across ROIs)
    """
    roi_names = list(roi_signals.keys())
    omega = {'PE': {}, 'SE': {}, 'PE_mean': {}, 'SE_mean': {}}

    for roi_name in roi_names:
        data = roi_signals[roi_name]  # (n_epochs, n_samples)
        n_epochs = data.shape[0]

        pe_values = np.array([permutation_entropy(data[e], order=pe_order) for e in range(n_epochs)])
        se_values = np.array([spectral_entropy(data[e], sfreq) for e in range(n_epochs)])

        omega['PE'][roi_name] = pe_values
        omega['SE'][roi_name] = se_values
        omega['PE_mean'][roi_name] = np.mean(pe_values)
        omega['SE_mean'][roi_name] = np.mean(se_values)

    # Global means
    omega['PE_global'] = np.mean([omega['PE_mean'][r] for r in roi_names])
    omega['SE_global'] = np.mean([omega['SE_mean'][r] for r in roi_names])

    return omega


def compute_omega_all_conditions(subject_data, band='full'):
    """
    Compute Omega for all conditions of a subject.

    Parameters
    ----------
    subject_data : dict from load_subject_all_conditions
    band : str, 'full' or 'deltafree'

    Returns
    -------
    omega_results : dict, {condition_name: omega_dict}
    """
    sfreq = subject_data['sfreq']
    omega_results = {}

    for cond_name, roi_signals in subject_data[band].items():
        omega_results[cond_name] = compute_omega_for_condition(roi_signals, sfreq)

    return omega_results
