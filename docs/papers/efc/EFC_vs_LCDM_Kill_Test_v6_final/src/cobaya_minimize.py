"""
Cobaya minimize aggregator — Section 6 of the Kill-Test v6 paper.

Aggregates the four cobaya minimize runs and the per-sector decomposition
reported in Tables 5 and 6 of the paper. All four runs return Δχ² ≤ 0.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Table 5: the four cobaya minimize runs
# ---------------------------------------------------------------------------

COBAYA_RUNS: List[Dict[str, object]] = [
    {
        "run": "MGCAMB",
        "dataset": "plik_lite + lowl + lensing (free cosmo)",
        "parameters": ["mu0", "Sigma0"],
        "delta_chi2": -0.45,
        "engine": "direct_eval",
    },
    {
        "run": "A_lens proxy",
        "dataset": "plik_lite + lowl + lensing (fixed cosmo)",
        "parameters": ["A_lens"],
        "delta_chi2": -0.81,
        "engine": "cobaya_minimize",
    },
    {
        "run": "A_lens free",
        "dataset": "plik_lite + lowl + lensing (free cosmo)",
        "parameters": ["A_lens"],
        "delta_chi2": -0.70,
        "engine": "cobaya_minimize",
    },
    {
        "run": "K0 m2",
        "dataset": "lowl + lensing + BAO + Pantheon+",
        "parameters": ["K0", "m2"],
        "delta_chi2": -0.30,
        "engine": "cobaya_bobyqa",
    },
]


# ---------------------------------------------------------------------------
# Table 6: sector decomposition (K0, m² run)
# ---------------------------------------------------------------------------

SECTOR_DECOMPOSITION: List[Dict[str, float]] = [
    {"sector": "lowl TT", "gr": 20.130, "efc": 19.941, "delta": -0.189},
    {"sector": "lowl EE", "gr": 395.831, "efc": 395.761, "delta": -0.070},
    {"sector": "Lensing", "gr": 9.547, "efc": 9.218, "delta": -0.329},
    {"sector": "BAO", "gr": 13.216, "efc": 13.037, "delta": -0.179},
    {"sector": "Pantheon+", "gr": 1405.744, "efc": 1406.212, "delta": 0.468},
]

TOTAL_DELTA_CHI2 = -0.300  # Sum of above (with rounding)


# ---------------------------------------------------------------------------
# Table 7: parameters at minimum (K0, m² run)
# ---------------------------------------------------------------------------

PARAMETERS_AT_MINIMUM: List[Dict[str, Optional[float]]] = [
    {"parameter": "K0", "ref_v5": 1.66, "gr": None, "efc": 1.552, "delta_pct": -6.5},
    {"parameter": "m2", "ref_v5": 0.0035, "gr": None, "efc": 0.00318, "delta_pct": -9.1},
    {"parameter": "mu0", "ref_v5": 0.940, "gr": 1.000, "efc": 0.9437, "delta": -0.056},
    {"parameter": "Sigma0", "ref_v5": 1.050, "gr": 1.000, "efc": 1.069, "delta": 0.069},
    {"parameter": "A_lens", "ref_v5": 1.036, "gr": 1.000, "efc": 1.143, "delta": 0.143},
    {"parameter": "H0_km_s_Mpc", "ref_v5": None, "gr": 67.89, "efc": 68.79, "delta": 0.90},
    {"parameter": "sigma8", "ref_v5": None, "gr": 0.811, "efc": 0.797, "delta": -0.014},
    {"parameter": "Omega_m", "ref_v5": None, "gr": 0.302, "efc": 0.299, "delta": -0.003},
]


# ---------------------------------------------------------------------------
# Dataclass wrappers and aggregators
# ---------------------------------------------------------------------------

@dataclass
class CobayaRunResult:
    """Single cobaya minimize run."""
    run: str
    dataset: str
    parameters: List[str]
    delta_chi2: float
    engine: str

    @property
    def efc_preferred(self) -> bool:
        """True if Δχ² ≤ 0 (EFC preferred)."""
        return self.delta_chi2 <= 0.0


def aggregate_runs(runs: Optional[List[Dict[str, object]]] = None) -> Dict[str, object]:
    """
    Aggregate cobaya minimize runs.

    Parameters
    ----------
    runs : list of dict, optional
        Run entries; uses COBAYA_RUNS if not provided.

    Returns
    -------
    dict
        Aggregate statistics with keys:
        - n_runs
        - n_efc_preferred
        - delta_chi2_min
        - delta_chi2_max
        - delta_chi2_mean
        - all_efc_preferred (bool)
    """
    if runs is None:
        runs = COBAYA_RUNS
    deltas = [float(r["delta_chi2"]) for r in runs]
    n_efc = sum(1 for d in deltas if d <= 0)
    return {
        "n_runs": len(runs),
        "n_efc_preferred": n_efc,
        "delta_chi2_min": min(deltas),
        "delta_chi2_max": max(deltas),
        "delta_chi2_mean": sum(deltas) / len(deltas),
        "all_efc_preferred": n_efc == len(runs),
    }


def delta_chi2(sector_decomp: Optional[List[Dict[str, float]]] = None) -> float:
    """
    Return the total Δχ² from the sector decomposition.

    Parameters
    ----------
    sector_decomp : list of dict, optional
        Per-sector rows with 'delta' key; uses SECTOR_DECOMPOSITION if absent.

    Returns
    -------
    float
        Sum of per-sector Δχ² values.
    """
    if sector_decomp is None:
        sector_decomp = SECTOR_DECOMPOSITION
    return sum(float(row["delta"]) for row in sector_decomp)


# ---------------------------------------------------------------------------
# Demonstration / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("EFC vs ΛCDM Kill-Test v6 — Cobaya minimize aggregator")
    print("=" * 72)
    print()

    print("Table 5: Four cobaya runs")
    print(f"{'Run':<16} {'Params':<18} {'Δχ²':>8}  Dataset")
    print("-" * 72)
    for r in COBAYA_RUNS:
        params = ", ".join(r["parameters"])  # type: ignore[arg-type]
        print(f"{r['run']:<16} {params:<18} {r['delta_chi2']:>+8.2f}  {r['dataset']}")
    print()

    print("Table 6: Sector decomposition (K0, m² run)")
    print(f"{'Sector':<14} {'GR':>12} {'EFC':>12} {'Δχ²':>10}")
    print("-" * 52)
    for s in SECTOR_DECOMPOSITION:
        print(f"{s['sector']:<14} {s['gr']:>12.3f} {s['efc']:>12.3f} {s['delta']:>+10.3f}")
    total_gr = sum(s["gr"] for s in SECTOR_DECOMPOSITION)
    total_efc = sum(s["efc"] for s in SECTOR_DECOMPOSITION)
    total_delta = sum(s["delta"] for s in SECTOR_DECOMPOSITION)
    print("-" * 52)
    print(f"{'Total':<14} {total_gr:>12.3f} {total_efc:>12.3f} {total_delta:>+10.3f}")
    print()

    agg = aggregate_runs()
    print("Aggregate cobaya verdict:")
    for k, v in agg.items():
        print(f"  {k}: {v}")
    print()

    print(f"Total Δχ² from sector decomposition: {delta_chi2():+.3f}")
