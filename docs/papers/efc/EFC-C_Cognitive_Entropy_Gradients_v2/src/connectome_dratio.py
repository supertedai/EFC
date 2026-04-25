"""
EFC-C v2.1 pipeline module: connectome_dratio.py

Computes hub-to-periphery degree ratio D_ratio from a structural adjacency matrix W.

PDF v2.1 §4.2: HCP MMP1.0 (360 parcels), top 10% / bottom 30% by weighted degree.
"""


def weighted_degree(W):
    """Compute weighted degree k_i = sum_j W_ij per parcel.

    Parameters
    ----------
    W : list of list of float
        Square symmetric weighted adjacency matrix.

    Returns
    -------
    list of float : weighted degrees
    """
    n = len(W)
    return [sum(W[i][j] for j in range(n)) for i in range(n)]


def compute_dratio(W, hub_pct=0.10, periph_pct=0.30):
    """Compute hub-to-periphery degree ratio D_ratio = <k_hub>/<k_periph>.

    Parameters
    ----------
    W : list of list of float
        Weighted structural adjacency (e.g. streamline density between HCP MMP1.0 parcels).
    hub_pct : float
        Fraction defining hub set by weighted degree (default 0.10 = top 10%).
    periph_pct : float
        Fraction defining periphery set by weighted degree (default 0.30 = bottom 30%).

    Returns
    -------
    dict : {D_ratio, mean_k_hub, mean_k_periph, n_hub, n_periph}
    """
    degrees = weighted_degree(W)
    sorted_deg = sorted(degrees, reverse=True)
    n = len(degrees)
    n_hub = max(1, int(n * hub_pct))
    n_periph = max(1, int(n * periph_pct))
    k_hub = sorted_deg[:n_hub]
    k_periph = sorted_deg[-n_periph:]
    mean_k_hub = sum(k_hub) / len(k_hub)
    mean_k_periph = sum(k_periph) / len(k_periph)
    return {
        "D_ratio": mean_k_hub / mean_k_periph if mean_k_periph > 0 else float("inf"),
        "mean_k_hub": mean_k_hub,
        "mean_k_periph": mean_k_periph,
        "n_hub": n_hub,
        "n_periph": n_periph,
        "hub_pct": hub_pct,
        "periph_pct": periph_pct,
    }


def hub_periph_indices(W, hub_pct=0.10, periph_pct=0.30):
    """Return parcel indices for hub and periphery sets."""
    degrees = weighted_degree(W)
    indexed = sorted(enumerate(degrees), key=lambda x: x[1], reverse=True)
    n = len(degrees)
    n_hub = max(1, int(n * hub_pct))
    n_periph = max(1, int(n * periph_pct))
    hub_idx = [i for i, _ in indexed[:n_hub]]
    periph_idx = [i for i, _ in indexed[-n_periph:]]
    return {"hub_indices": hub_idx, "periph_indices": periph_idx}
