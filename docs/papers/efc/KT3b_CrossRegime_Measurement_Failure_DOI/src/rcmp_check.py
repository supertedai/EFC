"""
RCMP check — a tiny structural linter for EFC test architectures.

Implements the Regime-Consistent Measurement Principle (DOI 31222900) as
a set of rule checks. Given a description of a test (theory regime,
driver regime, observable regime, data regime, mass-model assumption,
and whether the coupling operator between regimes is derived), the
checker reports which of the three KT3b-style violations a test design
would trigger:

    V1  Driver-response mismatch (undefined cross-regime coupling)
    V2  Boundary observation (observable at an L1/L2 transition point)
    V3  Implicit regime mixing in the mass model

A test is "RCMP-consistent" if it triggers no violations. This is a
structural / pre-measurement linter, not a statistical test.

Reference:
    Magnusson (2026), "Cross-Regime Measurement Failure in the KT3b
    Environmental Test", DOI 10.6084/m9.figshare.31963821.
    Magnusson (2026), "The Regime-Consistent Measurement Principle
    (RCMP)", DOI 10.6084/m9.figshare.31222900.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set


# Canonical regime labels used by the checker
L1 = "L1"                       # linear cosmological regime
L2 = "L2"                       # non-linear galactic regime
BOUNDARY = "L1/L2 boundary"     # transition region g ~ a_0
DERIVED = "derived"             # regime entered through a derived mapping


@dataclass
class TestArchitecture:
    """
    Structural description of a single test architecture.

    Attributes
    ----------
    name : str
        Human-readable label.
    theory_regime : str
        Regime of the theoretical prediction (L1 / L2 / derived).
    driver_regime : str
        Regime of the physical driver (L1 / L2).
    observable_regime : str
        Regime where the observable is measured. If this is the
        boundary, V2 is triggered.
    data_regime : str
        Regime of the measured data.
    mass_model_regime_assumption : str
        Regime assumption embedded in the mass model (e.g. Upsilon_star
        assumes L1 stellar physics).
    coupling_operator_derived : bool
        Whether the cross-regime coupling is derived from the action
        (True → no V1) or is a free/effective parameter (False → V1 if
        driver and theory live in different regimes).
    """

    name: str
    theory_regime: str
    driver_regime: str
    observable_regime: str
    data_regime: str
    mass_model_regime_assumption: str
    coupling_operator_derived: bool


@dataclass
class RCMPResult:
    architecture: str
    violations: Set[str] = field(default_factory=set)
    rcmp_consistent: bool = True
    notes: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag = "OK" if self.rcmp_consistent else "FAIL"
        vs = ", ".join(sorted(self.violations)) if self.violations else "none"
        return f"[{tag}] {self.architecture}: {vs}"


def check_rcmp(arch: TestArchitecture) -> RCMPResult:
    """
    Return the RCMPResult for a single test architecture.

    Rules:

    V1  Fires when the theory regime and the driver regime differ AND
        the coupling operator between them is not derived from the
        action.
    V2  Fires when the observable lives on the L1/L2 boundary.
    V3  Fires when the mass-model regime assumption differs from the
        data regime (implicit regime mixing).
    """
    result = RCMPResult(architecture=arch.name)

    # V1 — driver/response mismatch
    cross_regime = arch.theory_regime != arch.driver_regime
    if cross_regime and not arch.coupling_operator_derived:
        result.violations.add("V1")
        result.notes.append(
            f"V1: {arch.driver_regime} driver → {arch.theory_regime} theory "
            f"through an undefined coupling operator"
        )

    # V2 — boundary observation
    if arch.observable_regime == BOUNDARY:
        result.violations.add("V2")
        result.notes.append(
            "V2: observable lives on the L1/L2 boundary (g ~ a_0) where "
            "both regimes contribute and neither dominates"
        )

    # V3 — mass-model regime mixing
    if (
        arch.mass_model_regime_assumption
        and arch.mass_model_regime_assumption != arch.data_regime
    ):
        result.violations.add("V3")
        result.notes.append(
            f"V3: mass model assumes {arch.mass_model_regime_assumption} "
            f"physics applied to {arch.data_regime}-regime dynamics"
        )

    result.rcmp_consistent = len(result.violations) == 0
    return result


def check_all(architectures: List[TestArchitecture]) -> List[RCMPResult]:
    return [check_rcmp(a) for a in architectures]


# ---------------------------------------------------------------------------
#   Canonical architectures from the paper
# ---------------------------------------------------------------------------

def kt3b_original() -> TestArchitecture:
    """The original KT3b architecture — violates V1, V2, V3."""
    return TestArchitecture(
        name="KT3b original",
        theory_regime=L2,                                # D_eff(rho)
        driver_regime=L1,                                # rho_env
        observable_regime=BOUNDARY,                      # R at a_0
        data_regime=L2,                                  # rotation curves
        mass_model_regime_assumption=L1,                 # Upsilon_star = 0.5
        coupling_operator_derived=False,                 # alpha free, no kernel
    )


def architecture_A() -> TestArchitecture:
    """Pure L2: RAR slope in deep-MOND regime."""
    return TestArchitecture(
        name="A — pure L2 (RAR slope deep MOND)",
        theory_regime=L2,
        driver_regime=L2,              # restricted to L2 observable
        observable_regime=L2,          # deep MOND, far from boundary
        data_regime=L2,
        mass_model_regime_assumption=L2,
        coupling_operator_derived=True,
    )


def architecture_B() -> TestArchitecture:
    """Pure L1: fsigma8 growth rate."""
    return TestArchitecture(
        name="B — pure L1 (fsigma8 growth)",
        theory_regime=L1,
        driver_regime=L1,
        observable_regime=L1,
        data_regime=L1,
        mass_model_regime_assumption=L1,
        coupling_operator_derived=True,
    )


def architecture_C() -> TestArchitecture:
    """Derived L1→L2 mapping."""
    return TestArchitecture(
        name="C — derived L1->L2 mapping",
        theory_regime=DERIVED,
        driver_regime=L1,
        observable_regime=L2,
        data_regime=L2,
        mass_model_regime_assumption=L2,
        coupling_operator_derived=True,     # derived from action
    )


def default_architectures() -> List[TestArchitecture]:
    return [kt3b_original(), architecture_A(), architecture_B(), architecture_C()]


if __name__ == "__main__":
    for r in check_all(default_architectures()):
        print(r)
        for note in r.notes:
            print(f"    - {note}")
