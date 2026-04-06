"""
Sign Structure of an Additive Gate-Function Modification to the Friedmann Equation

Implements the sign lemma, gate function, EFC-modified Friedmann equation,
and numerical verification against CLASS results.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31333414
Series: EFCLASS Technical Note I
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class CosmologicalParameters:
    """Planck 2018 + EFC parameters used in the technical note."""
    h: float = 0.674
    omega_b: float = 0.02237
    omega_cdm: float = 0.1200
    m_nu_eV: float = 0.06
    A: float = 0.15
    z_t: float = 1.01
    n: int = 6

    @property
    def Omega_r(self) -> float:
        """Radiation density parameter (approximate)."""
        return 9.0e-5

    @property
    def Omega_m(self) -> float:
        """Total matter density parameter."""
        return (self.omega_b + self.omega_cdm) / self.h**2

    @property
    def Omega_Lambda(self) -> float:
        """Standard cosmological constant."""
        return 1.0 - self.Omega_m - self.Omega_r

    @property
    def a_t(self) -> float:
        """Transition scale factor."""
        return 1.0 / (1.0 + self.z_t)

    @property
    def g_0(self) -> float:
        """Gate function at z=0 (a=1)."""
        return self.gate(0.0)

    @property
    def Omega_Lambda_prime(self) -> float:
        """Adjusted cosmological constant for closure: E_EFC(0) = 1."""
        return self.Omega_Lambda - self.A * self.g_0

    def gate(self, z: float) -> float:
        """
        Sigmoid gate function.

        g(z) = 1 / (1 + (a_t / a)^n)
        where a = 1/(1+z), a_t = 1/(1+z_t)
        """
        a = 1.0 / (1.0 + z)
        ratio = self.a_t / a
        return 1.0 / (1.0 + ratio**self.n)

    def E2_standard(self, z: float) -> float:
        """Standard Friedmann equation: E^2(z) = Omega_r(1+z)^4 + Omega_m(1+z)^3 + Omega_Lambda."""
        zp1 = 1.0 + z
        return self.Omega_r * zp1**4 + self.Omega_m * zp1**3 + self.Omega_Lambda

    def E2_efc(self, z: float) -> float:
        """EFC-modified Friedmann equation: E^2_EFC(z) = Omega_r(1+z)^4 + Omega_m(1+z)^3 + Omega'_Lambda + A*g(z)."""
        zp1 = 1.0 + z
        return (self.Omega_r * zp1**4
                + self.Omega_m * zp1**3
                + self.Omega_Lambda_prime
                + self.A * self.gate(z))

    def delta_E2(self, z: float) -> float:
        """
        Sign lemma quantity: Delta E^2 = A * [g(z) - g(0)].

        Lemma 1: This is strictly non-positive for all z > 0.
        """
        return self.A * (self.gate(z) - self.g_0)

    def delta_H_over_H_pct(self, z: float) -> float:
        """
        Fractional change in H(z): DeltaH/H in percent.

        Since E^2 = H^2/H0^2, DeltaH/H ~ DeltaE^2 / (2 * E^2_std).
        """
        E2_std = self.E2_standard(z)
        if E2_std == 0:
            return 0.0
        dE2 = self.delta_E2(z)
        return 100.0 * dE2 / (2.0 * E2_std)


@dataclass
class SignVerificationPoint:
    """Single verification point comparing CLASS vs analytical delta-H^2."""
    z: float
    delta_H2_class: float
    delta_H2_analytical: float
    delta_H_over_H_pct: float


# Published CLASS verification data (Table 1 of the paper)
CLASS_VERIFICATION_DATA = [
    SignVerificationPoint(z=0.0, delta_H2_class=0.0, delta_H2_analytical=0.0, delta_H_over_H_pct=0.0),
    SignVerificationPoint(z=0.3, delta_H2_class=-4.049e-10, delta_H2_analytical=-4.038e-10, delta_H_over_H_pct=-0.291),
    SignVerificationPoint(z=0.5, delta_H2_class=-1.003e-9, delta_H2_analytical=-1.003e-9, delta_H_over_H_pct=-0.569),
    SignVerificationPoint(z=0.7, delta_H2_class=-1.915e-9, delta_H2_analytical=-1.918e-9, delta_H_over_H_pct=-0.853),
    SignVerificationPoint(z=1.0, delta_H2_class=-3.620e-9, delta_H2_analytical=-3.621e-9, delta_H_over_H_pct=-1.124),
    SignVerificationPoint(z=1.5, delta_H2_class=-5.856e-9, delta_H2_analytical=-5.856e-9, delta_H_over_H_pct=-1.039),
    SignVerificationPoint(z=2.0, delta_H2_class=-6.839e-9, delta_H2_analytical=-6.840e-9, delta_H_over_H_pct=-0.739),
    SignVerificationPoint(z=3.0, delta_H2_class=-7.348e-9, delta_H2_analytical=-7.348e-9, delta_H_over_H_pct=-0.349),
    SignVerificationPoint(z=5.0, delta_H2_class=-7.458e-9, delta_H2_analytical=-7.458e-9, delta_H_over_H_pct=-0.107),
]


@dataclass
class GrowthSignaturePoint:
    """Growth rate comparison at BOSS DR12 redshifts."""
    z: float
    fsigma8_LCDM: float
    fsigma8_EFC: float
    delta_pct: float


# Published growth signature data (Table 2)
GROWTH_SIGNATURE_DATA = [
    GrowthSignaturePoint(z=0.38, fsigma8_LCDM=0.4749, fsigma8_EFC=0.4773, delta_pct=0.50),
    GrowthSignaturePoint(z=0.51, fsigma8_LCDM=0.4731, fsigma8_EFC=0.4762, delta_pct=0.65),
    GrowthSignaturePoint(z=0.61, fsigma8_LCDM=0.4679, fsigma8_EFC=0.4715, delta_pct=0.76),
]


class SignStructureAnalysis:
    """
    Analysis of sign structure in the EFC gate-function modification.

    Key result (Lemma 1): Under E(0) = 1 normalisation,
    Delta E^2 = A[g(z) - g(0)] <= 0 for all z > 0.
    """

    KEY_CONCLUSIONS = [
        "Delta E^2(z) = A[g(z) - g(0)] <= 0 for all z > 0 (Lemma 1)",
        "H_EFC(z) <= H_LCDM(z): reduced Hubble friction enhances structure growth",
        "Background-level EFC cannot suppress sigma_8 under E(0) = 1 normalisation",
        "f*sigma_8 increases by +0.5-0.8% for A = 0.15",
        "S_8 tension requires perturbation-level modifications (mu < 1)",
        "Structural constraint independent of numerical values of (A, z_t, n)",
    ]

    CLASS_PATCH_INFO = {
        "files_modified": ["background.h", "background.c", "input.c"],
        "total_lines": 77,
    }

    def __init__(self, params: CosmologicalParameters = None):
        self.params = params or CosmologicalParameters()

    def verify_sign_lemma(self, z_values: List[float] = None) -> List[Dict]:
        """
        Verify Lemma 1: Delta E^2 <= 0 for all z > 0.

        Returns list of {z, delta_E2, sign_ok} dicts.
        """
        if z_values is None:
            z_values = [0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 50.0, 100.0]

        results = []
        for z in z_values:
            dE2 = self.params.delta_E2(z)
            results.append({
                "z": z,
                "delta_E2": dE2,
                "sign_ok": dE2 <= 0.0 or z == 0.0,
            })
        return results

    def verify_closure(self) -> Dict:
        """Verify the closure condition E_EFC(0) = 1."""
        E2_0 = self.params.E2_efc(0.0)
        return {
            "E2_efc_at_0": E2_0,
            "closure_satisfied": abs(E2_0 - 1.0) < 1e-10,
            "Omega_Lambda_prime": self.params.Omega_Lambda_prime,
            "g_0": self.params.g_0,
        }

    def gate_suppression_at_cmb(self) -> Dict:
        """Check gate suppression at CMB (z=1100)."""
        g_cmb = self.params.gate(1100.0)
        return {
            "g_z1100": g_cmb,
            "fully_suppressed": g_cmb < 1e-10,
            "delta_E2_z1100": self.params.delta_E2(1100.0),
        }

    def growth_enhancement(self) -> List[Dict]:
        """Return growth signature: fractional delta-H/H at key redshifts."""
        results = []
        for z in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]:
            results.append({
                "z": z,
                "delta_H_over_H_pct": round(self.params.delta_H_over_H_pct(z), 4),
                "gate_value": round(self.params.gate(z), 6),
            })
        return results

    def summary(self) -> str:
        """Human-readable summary of the sign structure analysis."""
        p = self.params
        closure = self.verify_closure()
        cmb = self.gate_suppression_at_cmb()

        lines = [
            "EFCLASS Technical Note I: Sign Structure Analysis",
            "=" * 55,
            "",
            "Parameters:",
            f"  h = {p.h}, omega_b = {p.omega_b}, omega_cdm = {p.omega_cdm}",
            f"  A = {p.A}, z_t = {p.z_t}, n = {p.n}",
            f"  g(0) = {p.g_0:.6f}",
            f"  Omega'_Lambda = {p.Omega_Lambda_prime:.4f}",
            "",
            "Closure check:",
            f"  E^2_EFC(0) = {closure['E2_efc_at_0']:.10f}  "
            f"({'OK' if closure['closure_satisfied'] else 'FAIL'})",
            "",
            "CMB safety:",
            f"  g(z=1100) = {cmb['g_z1100']:.2e}  "
            f"({'Suppressed' if cmb['fully_suppressed'] else 'NOT suppressed'})",
            "",
            "Sign verification (Delta H/H %):",
        ]

        for row in self.growth_enhancement():
            sign = "negative" if row["delta_H_over_H_pct"] < 0 else "zero/positive"
            lines.append(f"  z={row['z']:.1f}: {row['delta_H_over_H_pct']:+.4f}%  ({sign})")

        lines.append("")
        lines.append("Key conclusions:")
        for c in self.KEY_CONCLUSIONS:
            lines.append(f"  - {c}")

        return "\n".join(lines)
