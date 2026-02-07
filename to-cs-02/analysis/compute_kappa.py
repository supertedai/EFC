"""
TO-CS-02: Kappa (Integration/Causal Closure) Computation
Computes Transfer Entropy (TE) between all 56 directed ROI pairs.

Locked parameters (Appendix B):
- pyinform TE, k=3 (history length), 6 bins
- 8 ROIs x 7 targets = 56 directed pairs
"""

import numpy as np
from pyinform import transfer_entropy


def discretize_signal(x, n_bins=6):
    """
    Discretize a continuous signal into n_bins equal-width bins.

    Parameters
    ----------
    x : np.ndarray, 1D continuous signal
    n_bins : int, number of bins (locked: 6)

    Returns
    -------
    x_disc : np.ndarray of int, discretized signal
    """
    x_min, x_max = x.min(), x.max()
    if x_max == x_min:
        return np.zeros(len(x), dtype=int)
    # Equal-width binning
    x_norm = (x - x_min) / (x_max - x_min)
    x_disc = np.clip((x_norm * n_bins).astype(int), 0, n_bins - 1)
    return x_disc


def compute_te_pair(source, target, k=3, n_bins=6):
    """
    Compute transfer entropy from source to target.

    Parameters
    ----------
    source : np.ndarray, 1D continuous signal
    target : np.ndarray, 1D continuous signal
    k : int, history length (locked: 3)
    n_bins : int, discretization bins (locked: 6)

    Returns
    -------
    te : float, transfer entropy value (bits)
    """
    src_disc = discretize_signal(source, n_bins)
    tgt_disc = discretize_signal(target, n_bins)
    te = transfer_entropy(src_disc, tgt_disc, k=k)
    return te


def compute_kappa_for_condition(roi_signals, k=3, n_bins=6):
    """
    Compute kappa (TE) for all 56 directed pairs in one condition.

    Parameters
    ----------
    roi_signals : dict, {roi_name: np.ndarray (n_epochs, n_samples)}
    k : int, TE history length (locked: 3)
    n_bins : int, discretization bins (locked: 6)

    Returns
    -------
    kappa : dict with keys:
        'te_matrix': dict of dicts, te_matrix[source][target] = mean TE across epochs
        'te_epoch': dict of dicts, te_epoch[source][target] = np.ndarray (n_epochs,)
        'kappa_global': float, mean of all 56 directed pairs
        'kappa_in': {roi: float}, mean TE from all other ROIs -> this ROI
        'kappa_out': {roi: float}, mean TE from this ROI -> all other ROIs
        'kappa_hub': {roi: float}, mean(kappa_in, kappa_out)
        'A_FP': float, TE(F->P) - TE(P->F) asymmetry (frontal-parietal)
        'A_CP': float, TE(C->P) - TE(P->C) asymmetry (central-parietal)
    """
    roi_names = sorted(roi_signals.keys())
    n_rois = len(roi_names)
    n_epochs = roi_signals[roi_names[0]].shape[0]

    # Compute TE for all directed pairs
    te_matrix = {src: {} for src in roi_names}
    te_epoch = {src: {} for src in roi_names}

    for src in roi_names:
        for tgt in roi_names:
            if src == tgt:
                continue
            epoch_tes = []
            for e in range(n_epochs):
                te = compute_te_pair(
                    roi_signals[src][e],
                    roi_signals[tgt][e],
                    k=k, n_bins=n_bins
                )
                epoch_tes.append(te)
            te_epoch[src][tgt] = np.array(epoch_tes)
            te_matrix[src][tgt] = np.mean(epoch_tes)

    # Global kappa: mean of all 56 directed pairs
    all_tes = [te_matrix[s][t] for s in roi_names for t in roi_names if s != t]
    kappa_global = np.mean(all_tes)

    # Hub measures per ROI
    kappa_in = {}
    kappa_out = {}
    kappa_hub = {}
    for roi in roi_names:
        # Incoming: all others -> this ROI
        incoming = [te_matrix[s][roi] for s in roi_names if s != roi]
        kappa_in[roi] = np.mean(incoming)
        # Outgoing: this ROI -> all others
        outgoing = [te_matrix[roi][t] for t in roi_names if t != roi]
        kappa_out[roi] = np.mean(outgoing)
        # Hub: mean of in and out
        kappa_hub[roi] = np.mean([kappa_in[roi], kappa_out[roi]])

    # Directional asymmetries
    # A_FP: frontal -> parietal minus parietal -> frontal
    frontal_rois = [r for r in roi_names if r.startswith('F_')]
    parietal_rois = [r for r in roi_names if r.startswith('P_')]

    fp_forward = []  # F -> P
    fp_backward = []  # P -> F
    for f in frontal_rois:
        for p in parietal_rois:
            if f in te_matrix and p in te_matrix[f]:
                fp_forward.append(te_matrix[f][p])
            if p in te_matrix and f in te_matrix[p]:
                fp_backward.append(te_matrix[p][f])

    A_FP = np.mean(fp_forward) - np.mean(fp_backward) if fp_forward and fp_backward else 0.0

    # A_CP: central -> parietal minus parietal -> central
    central_rois = [r for r in roi_names if r.startswith('C_')]
    cp_forward = []
    cp_backward = []
    for c in central_rois:
        for p in parietal_rois:
            if c in te_matrix and p in te_matrix[c]:
                cp_forward.append(te_matrix[c][p])
            if p in te_matrix and c in te_matrix[p]:
                cp_backward.append(te_matrix[p][c])

    A_CP = np.mean(cp_forward) - np.mean(cp_backward) if cp_forward and cp_backward else 0.0

    kappa = {
        'te_matrix': te_matrix,
        'te_epoch': te_epoch,
        'kappa_global': kappa_global,
        'kappa_in': kappa_in,
        'kappa_out': kappa_out,
        'kappa_hub': kappa_hub,
        'A_FP': A_FP,
        'A_CP': A_CP,
    }

    return kappa


def compute_kappa_all_conditions(subject_data, band='full', k=3, n_bins=6):
    """
    Compute kappa for all conditions of a subject.

    Parameters
    ----------
    subject_data : dict from load_subject_all_conditions
    band : str, 'full' or 'deltafree'

    Returns
    -------
    kappa_results : dict, {condition_name: kappa_dict}
    """
    kappa_results = {}
    for cond_name, roi_signals in subject_data[band].items():
        print(f"    Computing kappa for {cond_name}...")
        kappa_results[cond_name] = compute_kappa_for_condition(roi_signals, k=k, n_bins=n_bins)
    return kappa_results
