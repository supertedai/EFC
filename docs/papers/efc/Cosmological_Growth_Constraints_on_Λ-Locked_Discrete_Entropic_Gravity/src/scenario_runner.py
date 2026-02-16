"""
Run and compare all three transition-scale scenarios.

Scenario A: Λ-locked (L_Λ ~ 4.4 Gpc, k_Λ ~ 0.0014 h/Mpc)
Scenario B: 10 Mpc transition (k = 0.1 h/Mpc)
Scenario C: 1 Mpc transition (k = 1.0 h/Mpc)
"""

from dataclasses import dataclass
from typing import List

from .growth_equation import GrowthResult, SIGMA8_LCDM


@dataclass
class Scenario:
    """Transition-scale scenario definition."""
    id: str
    name: str
    transition_scale: str
    k_transition: float  # h/Mpc


# Pre-defined scenarios from the paper
SCENARIOS = [
    Scenario("A", "Λ-locked", "4.4 Gpc", 0.0014),
    Scenario("B", "10 Mpc", "10 Mpc", 0.1),
    Scenario("C", "1 Mpc", "1 Mpc", 1.0),
]

# Results from the paper (Table in Section 5)
PAPER_RESULTS = {
    "LCDM": GrowthResult("ΛCDM", None, 0.811, 0.554, True),
    "A": GrowthResult("Graph-AQUAL", "Λ-locked", 0.814, 0.554, True, 1.004),
    "B": GrowthResult("Graph-AQUAL", "10 Mpc", 367.0, 0.541, False, 452.0),
    "C": GrowthResult("Graph-AQUAL", "1 Mpc", 24098.0, 0.536, False, 29714.0),
}


def get_result(scenario_id: str) -> GrowthResult:
    """Get paper result for a scenario."""
    return PAPER_RESULTS[scenario_id]


def run_all_scenarios() -> List[GrowthResult]:
    """Return results for all scenarios including ΛCDM baseline."""
    return [
        PAPER_RESULTS["LCDM"],
        PAPER_RESULTS["A"],
        PAPER_RESULTS["B"],
        PAPER_RESULTS["C"],
    ]


def compare_table() -> str:
    """Generate formatted comparison table."""
    results = run_all_scenarios()
    lines = [
        f"{'Model':<30s}  {'σ₈(z=0)':>12s}  {'γ':>6s}  {'Viable':>6s}",
        f"{'─' * 30}  {'─' * 12}  {'─' * 6}  {'─' * 6}",
    ]
    for r in results:
        scenario = f" ({r.scenario})" if r.scenario else ""
        model = f"{r.model}{scenario}"
        sigma_str = f"{r.sigma8:,.1f}" if r.sigma8 > 10 else f"{r.sigma8:.3f}"
        viable_str = "Yes" if r.viable else "NO"
        lines.append(f"{model:<30s}  {sigma_str:>12s}  {r.gamma:>6.3f}  {viable_str:>6s}")
    return "\n".join(lines)
