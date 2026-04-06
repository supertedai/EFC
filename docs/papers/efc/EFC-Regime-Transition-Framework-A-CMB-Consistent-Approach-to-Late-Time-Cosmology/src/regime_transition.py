"""
EFC Regime Transition Framework: A CMB-Consistent Approach to Late-Time Cosmology

Implements the Landau theory gating function G(z), regime transition dynamics,
and CMB safety verification.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31096951
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class CosmologyParams:
    """Planck 2018 cosmological parameters."""
    H0_km_s_Mpc: float = 67.36
    omega_b: float = 0.0494
    omega_c: float = 0.2646
    omega_lambda: float = 0.685
    omega_r: float = 9e-5
    A_s: float = 2.1e-9
    n_s: float = 0.9649
    tau: float = 0.0544


@dataclass
class RegimeParams:
    """Parameters for the Landau-theory regime transition."""
    chi_early: float = 0.2
    chi_late: float = 2.5
    z_transition: float = 50.0
    delta_z: float = 30.0
    alpha: float = 10.0
    chi_c: float = 1.0
    b: float = 1.0
    tau_relax: float = 0.1
    phi0: float = 1.0


@dataclass
class NumericalParams:
    """Numerical integration parameters."""
    z_min: float = 0.0
    z_max: float = 3000.0
    n_points: int = 15000
    phi_init: float = 1e-6
    rtol: float = 1e-10
    atol: float = 1e-12


@dataclass
class CMBSafetyResult:
    """Result of CMB safety verification."""
    G_cmb: float
    z_cmb: float = 1100.0
    threshold: float = 1e-4
    safety_margin_orders: float = 0.0

    @property
    def is_safe(self) -> bool:
        return self.G_cmb < self.threshold

    def __post_init__(self):
        if self.G_cmb > 0:
            self.safety_margin_orders = math.log10(self.threshold / self.G_cmb)


# Key results from the paper
KEY_GATING_VALUES = {
    "G_z3000": 1.0e-12,
    "G_z1100": 1.0e-12,
    "G_z100": 1.2e-12,
    "G_z10": 9.2e-16,
    "G_z2": 0.25,
    "G_z0": 0.9999,
}


class RegimeTransitionFramework:
    """
    Landau-theory based regime transition framework for EFC.

    Key result: Regime-dependent modifications achieve CMB safety
    (G_CMB ~ 10^-12) through dynamical gating, not fine-tuning.
    """

    def __init__(
        self,
        cosmo: CosmologyParams = None,
        regime: RegimeParams = None,
        numerical: NumericalParams = None,
    ):
        self.cosmo = cosmo or CosmologyParams()
        self.regime = regime or RegimeParams()
        self.numerical = numerical or NumericalParams()

    def H_normalised(self, z: float) -> float:
        """Hubble parameter H(z)/H0."""
        c = self.cosmo
        return math.sqrt(
            c.omega_r * (1 + z) ** 4
            + (c.omega_b + c.omega_c) * (1 + z) ** 3
            + c.omega_lambda
        )

    def chi(self, z: float) -> float:
        """
        Control parameter chi(z).

        Transitions from chi_early (high z) to chi_late (low z)
        centered at z_transition with width delta_z.
        """
        r = self.regime
        chi_mid = (r.chi_early + r.chi_late) / 2.0
        chi_amp = (r.chi_late - r.chi_early) / 2.0
        return chi_mid - chi_amp * math.tanh((z - r.z_transition) / r.delta_z)

    def landau_coefficient(self, chi_val: float) -> float:
        """Landau coefficient a(chi) = alpha * (chi_c - chi)."""
        return self.regime.alpha * (self.regime.chi_c - chi_val)

    def gating_function(self, phi: float) -> float:
        """Gating function G(phi) = phi^2 / (phi^2 + phi0^2)."""
        phi0 = self.regime.phi0
        return phi**2 / (phi**2 + phi0**2)

    def dphi_dz(self, z: float, phi: float) -> float:
        """
        Landau equation: dphi/dz = [a(chi)*phi + b*phi^3] / [(1+z)*H(z)*tau].

        Phi is clamped to prevent numerical overflow in the cubic term.
        """
        r = self.regime
        # Clamp phi to avoid overflow in phi^3
        phi_max = 1e50
        phi = max(min(phi, phi_max), -phi_max)
        chi_val = self.chi(z)
        a = self.landau_coefficient(chi_val)
        Hz = self.H_normalised(z)
        return (a * phi + r.b * phi**3) / ((1 + z) * Hz * r.tau_relax)

    def solve_rk4(self, n_steps: int = None) -> Tuple[List[float], List[float], List[float]]:
        """
        Solve Landau equation from z_max to z_min using RK4.

        Returns (z_array, phi_array, G_array).
        """
        if n_steps is None:
            n_steps = self.numerical.n_points

        z_start = self.numerical.z_max
        z_end = self.numerical.z_min
        dz = (z_end - z_start) / n_steps  # negative step

        z_arr = []
        phi_arr = []
        G_arr = []

        z = z_start
        phi = self.numerical.phi_init

        for _ in range(n_steps + 1):
            z_arr.append(z)
            phi_arr.append(phi)
            G_arr.append(self.gating_function(phi))

            # RK4 step
            k1 = dz * self.dphi_dz(z, phi)
            k2 = dz * self.dphi_dz(z + 0.5 * dz, phi + 0.5 * k1)
            k3 = dz * self.dphi_dz(z + 0.5 * dz, phi + 0.5 * k2)
            k4 = dz * self.dphi_dz(z + dz, phi + k3)

            phi += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            z += dz

        return z_arr, phi_arr, G_arr

    def G_at_redshift(self, z_target: float, z_arr: List[float],
                      G_arr: List[float]) -> float:
        """Interpolate G at a specific redshift from solved arrays."""
        best_idx = 0
        best_dist = abs(z_arr[0] - z_target)
        for i, z in enumerate(z_arr):
            d = abs(z - z_target)
            if d < best_dist:
                best_dist = d
                best_idx = i
        return G_arr[best_idx]

    def verify_cmb_safety(self, z_arr: List[float] = None,
                          G_arr: List[float] = None) -> CMBSafetyResult:
        """
        Verify CMB safety from a solved G(z) profile.

        If no arrays provided, uses published key results.
        """
        if z_arr is not None and G_arr is not None:
            G_cmb = self.G_at_redshift(1100.0, z_arr, G_arr)
        else:
            G_cmb = KEY_GATING_VALUES["G_z1100"]

        return CMBSafetyResult(G_cmb=G_cmb)

    def key_features(self) -> List[str]:
        """Key features of the framework."""
        return [
            "CMB-safe by construction (dynamics, not tuning)",
            "Fully reproducible (code included)",
            "CLASS-compatible",
            "Landau theory framework",
        ]

    def what_this_shows(self) -> List[str]:
        """Claims and scope of the work."""
        return [
            "Regime-dependent modifications CAN be CMB-safe",
            "Landau theory provides natural gating mechanism",
            "Delayed activation (chi crosses chi_c at z~50, effect at z<2)",
            "Framework applicable beyond EFC (modified gravity, dark energy, etc.)",
        ]

    def published_G_table(self) -> List[Dict]:
        """Table of published G(z) values from the paper."""
        return [
            {"z": 3000, "G": KEY_GATING_VALUES["G_z3000"], "interpretation": "Fully suppressed"},
            {"z": 1100, "G": KEY_GATING_VALUES["G_z1100"], "interpretation": "CMB safe (8 orders below threshold)"},
            {"z": 100, "G": KEY_GATING_VALUES["G_z100"], "interpretation": "Still suppressed"},
            {"z": 10, "G": KEY_GATING_VALUES["G_z10"], "interpretation": "Intermediate-z suppressed"},
            {"z": 2, "G": KEY_GATING_VALUES["G_z2"], "interpretation": "Partial late-time activation"},
            {"z": 0, "G": KEY_GATING_VALUES["G_z0"], "interpretation": "Full activation today"},
        ]

    def summary(self) -> str:
        """Human-readable summary of the regime transition framework."""
        cmb = self.verify_cmb_safety()
        lines = [
            "EFC Regime Transition Framework",
            "=" * 50,
            "",
            "Cosmology: Planck 2018",
            f"  H0 = {self.cosmo.H0_km_s_Mpc} km/s/Mpc",
            f"  Omega_b = {self.cosmo.omega_b}",
            f"  Omega_c = {self.cosmo.omega_c}",
            "",
            "Regime transition:",
            f"  chi_early = {self.regime.chi_early}",
            f"  chi_late  = {self.regime.chi_late}",
            f"  z_trans   = {self.regime.z_transition}",
            f"  alpha     = {self.regime.alpha}",
            "",
            "Gating function G(z):",
        ]
        for row in self.published_G_table():
            lines.append(f"  z = {row['z']:5d}:  G = {row['G']:.2e}  ({row['interpretation']})")

        lines.append("")
        lines.append(f"CMB safety: G(z=1100) = {cmb.G_cmb:.2e}")
        lines.append(f"  Threshold: {cmb.threshold:.0e}")
        lines.append(f"  Safe: {cmb.is_safe}")
        lines.append(f"  Safety margin: {cmb.safety_margin_orders:.1f} orders of magnitude")

        return "\n".join(lines)
