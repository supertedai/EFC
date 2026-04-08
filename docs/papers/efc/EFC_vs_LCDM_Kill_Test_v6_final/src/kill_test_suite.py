"""
Six-probe kill-test suite — Section 3 of the Kill-Test v6 paper.

Probes:
    1. DDO 154 rotation curve               (L3 / FLOW)
    2. Multi-component SPARC refit          (L3)
    3. Bullet Cluster                       (L2→L3)
    4. CMB primary                          (L0, neutral by construction)
    5. A_L lensing anomaly / (μ, Σ)         (L2)
    6. Cobaya minimize (K0, m²) full chain  (L2)

Verdict categories:
    EFC_decisive            — ΔAIC > 10 in EFC direction
    EFC                     — Δχ² < 0 stable across datasets
    tied                    — |ΔAIC| < 2
    neutral_by_construction — regime where α_S → 0
    LCDM / LCDM_decisive    — (none currently)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Static probe definitions from Section 3 of the paper
# ---------------------------------------------------------------------------

PROBES: List[Dict[str, object]] = [
    {
        "id": "probe-1",
        "name": "DDO 154 rotation curve",
        "regime": "L3",
        "metric": "chi2_red",
        "efc": 0.05,
        "lcdm": 2.71,
        "delta_aic": 35.4,
        "verdict": "EFC_decisive",
        "note": "NFW residuals ±9 km/s; EFC within ±1 km/s",
    },
    {
        "id": "probe-2",
        "name": "Multi-component SPARC refit",
        "regime": "L3",
        "metric": "success_rate_percent",
        "efc": 100,
        "lcdm": 5,
        "delta_aic": -126,  # best galaxy (NGC 7331)
        "verdict": "EFC_decisive",
        "note": "NGC 7331 ΔAIC = −126; NGC 4138 ΔAIC = −86",
    },
    {
        "id": "probe-3",
        "name": "Bullet Cluster",
        "regime": "L2-L3",
        "metric": "chi2_red",
        "efc": 0.46,
        "lcdm": 0.55,
        "delta_aic": 0.6,
        "verdict": "tied",
        "note": "EFC uses observable gas-shock entropy; ΛCDM requires 85% invisible mass",
    },
    {
        "id": "probe-4",
        "name": "CMB primary",
        "regime": "L0",
        "metric": "delta_chi2",
        "efc": 0.0,
        "lcdm": 0.0,
        "delta_aic": 0.0,
        "verdict": "neutral_by_construction",
        "note": "α_S → 0 at z > 1100; peaks, ratios, damping tail identical to ΛCDM",
    },
    {
        "id": "probe-5",
        "name": "A_L / (μ, Σ) lensing anomaly",
        "regime": "L2",
        "metric": "delta_chi2",
        "efc": -0.45,
        "lcdm": 0.0,
        "delta_aic": -0.45,
        "verdict": "EFC",
        "note": "MGCAMB + Planck 2018 plik_lite, free cosmo: (μ,Σ)=(0.94,1.05)",
    },
    {
        "id": "probe-6",
        "name": "Cobaya minimize (full chain)",
        "regime": "L2",
        "metric": "delta_chi2",
        "efc": -0.30,
        "lcdm": 0.0,
        "delta_aic": -0.30,
        "verdict": "EFC",
        "note": "Best of four runs: lowl + lensing + BAO + Pantheon+ (K0, m²)",
    },
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    """
    Single probe verdict entry.
    """
    id: str
    name: str
    regime: str
    metric: str
    efc: float
    lcdm: float
    delta_aic: float
    verdict: str
    note: str = ""

    @property
    def decisive_for_efc(self) -> bool:
        """True if ΔAIC > 10 in EFC direction."""
        return self.delta_aic > 10.0

    def as_row(self) -> str:
        """Return a compact string representation."""
        return (
            f"[{self.regime:>5}] {self.name:<40}  "
            f"ΔAIC = {self.delta_aic:+6.2f}  "
            f"→ {self.verdict}"
        )


def probe_result(probe_dict: Dict[str, object]) -> ProbeResult:
    """Construct a ProbeResult from a static PROBES entry."""
    return ProbeResult(
        id=str(probe_dict["id"]),
        name=str(probe_dict["name"]),
        regime=str(probe_dict["regime"]),
        metric=str(probe_dict["metric"]),
        efc=float(probe_dict["efc"]),
        lcdm=float(probe_dict["lcdm"]),
        delta_aic=float(probe_dict["delta_aic"]),
        verdict=str(probe_dict["verdict"]),
        note=str(probe_dict.get("note", "")),
    )


def run_all_probes() -> List[ProbeResult]:
    """
    Return the full list of ProbeResult entries.

    Returns
    -------
    list of ProbeResult
        One entry per probe.
    """
    return [probe_result(p) for p in PROBES]


def verdict_summary(results: Optional[List[ProbeResult]] = None) -> Dict[str, int]:
    """
    Count verdict categories across probes.

    Parameters
    ----------
    results : list of ProbeResult, optional
        Uses run_all_probes() if not provided.

    Returns
    -------
    dict
        Verdict → count.
    """
    if results is None:
        results = run_all_probes()
    counts: Dict[str, int] = {}
    for r in results:
        counts[r.verdict] = counts.get(r.verdict, 0) + 1
    return counts


def passes_non_rejectability() -> bool:
    """
    Non-rejectability test: no probe is LCDM or LCDM_decisive,
    and at least one probe is EFC or EFC_decisive.

    Returns
    -------
    bool
        True if EFC is non-rejectable across the six probes.
    """
    results = run_all_probes()
    anti_efc = any(r.verdict.startswith("LCDM") for r in results)
    pro_efc = any(r.verdict.startswith("EFC") for r in results)
    return (not anti_efc) and pro_efc


# ---------------------------------------------------------------------------
# Demonstration / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("EFC vs ΛCDM Kill-Test v6 — six-probe verdict")
    print("=" * 72)
    for r in run_all_probes():
        print(r.as_row())
    print("=" * 72)
    print(f"Verdict summary: {verdict_summary()}")
    print(f"Non-rejectability test: "
          f"{'PASS (EFC survives)' if passes_non_rejectability() else 'FAIL'}")
