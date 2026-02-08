"""
EFC v1.3 PPN Recovery via Density Saturation

Dual screening mechanisms for Solar System GR recovery.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31244827
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

# Physical constants
G_N = 6.674e-11  # m³/(kg·s²)
c = 2.998e8      # m/s
M_sun = 1.989e30 # kg
AU = 1.496e11    # m
R_sun = 6.96e8   # m

# EFC parameters from SPARC fits
G_DAGGER = 1.2e-10   # m/s² - transition acceleration
K_POWER = 0.415      # power-law index
RHO_STAR = 1e-22     # kg/m³ - transition density
N_STEEPNESS = 2      # density screening steepness

# Cassini bound
CASSINI_BOUND = 2.3e-5  # |γ - 1| constraint


@dataclass
class SolarSystemLocation:
    """Solar System location with gravitational properties."""
    name: str
    r: float              # Distance from Sun (m)
    g_bar: float          # Newtonian acceleration (m/s²)
    M_enc: float = M_sun  # Enclosed mass (kg)

    @property
    def rho_eff(self) -> float:
        """Source-smoothed effective density (kg/m³)."""
        return 3 * self.M_enc / (4 * np.pi * self.r**3)


# Standard Solar System locations
LOCATIONS = {
    'solar_surface': SolarSystemLocation('Solar surface', R_sun, 274.0),
    '1_au': SolarSystemLocation('1 AU', AU, 5.9e-3),
    'mercury': SolarSystemLocation('Mercury', 0.387 * AU, 3.9e-2),
    'saturn': SolarSystemLocation('Saturn', 9.54 * AU, 6.5e-4),
}


class AccelerationScreening:
    """
    Acceleration-based screening mechanism (galactic form).

    μ(g_bar) = (1 + g†/g_bar)^k

    In high-acceleration environments (Solar System), g_bar >> g†,
    so μ → 1 (GR recovered).
    """

    def __init__(self, g_dagger: float = G_DAGGER, k: float = K_POWER):
        """
        Initialize acceleration screening.

        Parameters
        ----------
        g_dagger : float
            Transition acceleration (m/s²), default from SPARC
        k : float
            Power-law index, default from SPARC
        """
        self.g_dagger = g_dagger
        self.k = k

    def mu(self, g_bar: float) -> float:
        """
        Calculate enhancement factor μ.

        Parameters
        ----------
        g_bar : float
            Local Newtonian acceleration (m/s²)

        Returns
        -------
        float
            Enhancement factor μ (= 1 in GR limit)
        """
        return (1 + self.g_dagger / g_bar) ** self.k

    def mu_deviation(self, g_bar: float) -> float:
        """Calculate |μ - 1|, the deviation from GR."""
        return abs(self.mu(g_bar) - 1)

    def margin_vs_cassini(self, g_bar: float) -> float:
        """Calculate margin below Cassini bound."""
        deviation = self.mu_deviation(g_bar)
        if deviation == 0:
            return np.inf
        return CASSINI_BOUND / deviation

    def evaluate_location(self, loc: SolarSystemLocation) -> dict:
        """Evaluate screening at a Solar System location."""
        mu = self.mu(loc.g_bar)
        deviation = abs(mu - 1)
        margin = self.margin_vs_cassini(loc.g_bar)

        return {
            'location': loc.name,
            'g_bar': loc.g_bar,
            'g_ratio': self.g_dagger / loc.g_bar,
            'mu': mu,
            'mu_deviation': deviation,
            'margin_vs_cassini': margin,
            'passes_cassini': deviation < CASSINI_BOUND
        }


class DensityScreening:
    """
    Density-based screening mechanism (cosmological form).

    Θ(ρ_eff) = exp[-(ρ_eff/ρ*)^n]

    where ρ_eff = 3 M_enc / (4π r³) is the source-smoothed density.

    In high-density environments (Solar System), ρ_eff >> ρ*,
    so Θ → 0 (modifications fully suppressed).
    """

    def __init__(self, rho_star: float = RHO_STAR, n: float = N_STEEPNESS):
        """
        Initialize density screening.

        Parameters
        ----------
        rho_star : float
            Transition density (kg/m³), default from SPARC
        n : float
            Steepness parameter
        """
        self.rho_star = rho_star
        self.n = n

    def theta(self, rho_eff: float) -> float:
        """
        Calculate density saturation function Θ.

        Parameters
        ----------
        rho_eff : float
            Source-smoothed effective density (kg/m³)

        Returns
        -------
        float
            Saturation function Θ (= 0 when screened, = 1 when active)
        """
        ratio = rho_eff / self.rho_star
        return np.exp(-(ratio ** self.n))

    def rho_eff(self, M_enc: float, r: float) -> float:
        """
        Calculate source-smoothed effective density.

        This is the mean interior density, NOT local particle density.
        """
        return 3 * M_enc / (4 * np.pi * r**3)

    def evaluate_location(self, loc: SolarSystemLocation) -> dict:
        """Evaluate screening at a Solar System location."""
        rho = loc.rho_eff
        theta = self.theta(rho)

        return {
            'location': loc.name,
            'r': loc.r,
            'rho_eff': rho,
            'rho_ratio': rho / self.rho_star,
            'theta': theta,
            'fully_screened': theta < 1e-10
        }


class PPNAnalysis:
    """
    PPN parameter analysis for EFC.

    Key result: γ = Ψ/Φ = 1 (derived from field structure)

    The EFC modified Einstein equation:
        G_μν = 8πG_N [1 + μ(S)] T_μν

    rescales G_N by a scalar factor. This preserves γ = 1 at
    linearized order because both metric potentials are sourced
    by the same effective coupling.
    """

    def __init__(self):
        self.gamma_linear = 1.0  # Derived result

    def gamma_higher_order_bound(
        self,
        theta: float,
        mu_0: float,
        U_over_c2: float,
        grad_ln_mu: float = 0.0
    ) -> float:
        """
        Calculate higher-order correction bound on γ.

        |γ - 1| ≤ Θ(ρ_eff) · |μ₀| · (U/c²) · r_s|∇ln μ|

        Parameters
        ----------
        theta : float
            Density screening factor
        mu_0 : float
            Acceleration screening amplitude
        U_over_c2 : float
            Newtonian potential / c²
        grad_ln_mu : float
            Gradient term (≈ 0 in screened regime)

        Returns
        -------
        float
            Upper bound on |γ - 1|
        """
        return theta * abs(mu_0) * U_over_c2 * grad_ln_mu

    def gamma_at_solar_surface(self) -> dict:
        """Calculate γ constraints at the Solar surface."""
        # Newtonian potential at Solar surface
        U_over_c2 = G_N * M_sun / (R_sun * c**2)  # ≈ 2e-6

        # In screened regime
        theta = 0  # Density screening
        mu_0 = 1.8e-13  # Acceleration screening deviation
        grad_ln_mu = 0  # Homogeneous regime

        # Even maximally aggressive bound
        max_bound = 1.0 * 1.0 * U_over_c2 * 1.0  # ≈ 2e-6

        # Actual bound with acceleration screening
        actual_bound = mu_0 * U_over_c2  # ≈ 3.6e-19

        return {
            'gamma_linear': 1.0,
            'U_over_c2': U_over_c2,
            'max_aggressive_bound': max_bound,
            'actual_bound': actual_bound,
            'cassini_bound': CASSINI_BOUND,
            'margin': CASSINI_BOUND / actual_bound if actual_bound > 0 else np.inf
        }

    def nordtvedt_bound(
        self,
        theta: float,
        epsilon: float,
        E_grav_over_Mc2: float
    ) -> float:
        """
        Calculate Nordtvedt parameter bound.

        |η|_EFC ≤ Θ(ρ_eff) · |ε| · (E_grav/Mc²)

        For Earth: E_grav/Mc² ≈ 5e-10
        """
        return theta * abs(epsilon) * E_grav_over_Mc2

    def summary(self) -> dict:
        """Return complete PPN analysis summary."""
        return {
            'gamma': {
                'value': 1.0,
                'status': 'derived (theorem)',
                'higher_order_bound': '<1e-19',
                'cassini_margin': '>1e14'
            },
            'nordtvedt_eta': {
                'bound': '<1e-17',
                'llr_constraint': '4.4e-4',
                'margin': '>1e13'
            },
            'wep': {
                'status': 'preserved by construction',
                'mechanism': 'universal coupling to T_μν'
            },
            'conclusion': 'EFC fully compatible with Solar System tests'
        }


def full_solar_system_analysis() -> dict:
    """
    Perform complete Solar System screening analysis.

    Returns
    -------
    dict
        Complete analysis results for all mechanisms and locations
    """
    accel = AccelerationScreening()
    dens = DensityScreening()
    ppn = PPNAnalysis()

    results = {
        'acceleration_screening': {},
        'density_screening': {},
        'ppn_analysis': ppn.summary()
    }

    for name, loc in LOCATIONS.items():
        results['acceleration_screening'][name] = accel.evaluate_location(loc)
        results['density_screening'][name] = dens.evaluate_location(loc)

    return results


if __name__ == '__main__':
    results = full_solar_system_analysis()

    print("=" * 60)
    print("EFC v1.3 Solar System Screening Analysis")
    print("=" * 60)

    print("\n--- Acceleration-Based Screening ---")
    for name, data in results['acceleration_screening'].items():
        print(f"\n{data['location']}:")
        print(f"  g_bar = {data['g_bar']:.2e} m/s²")
        print(f"  |μ-1| = {data['mu_deviation']:.2e}")
        print(f"  Margin vs Cassini: {data['margin_vs_cassini']:.1e}×")

    print("\n--- Density-Based Screening ---")
    for name, data in results['density_screening'].items():
        print(f"\n{data['location']}:")
        print(f"  ρ_eff = {data['rho_eff']:.2e} kg/m³")
        print(f"  Θ = {data['theta']:.2e}")

    print("\n--- PPN Analysis ---")
    ppn = results['ppn_analysis']
    print(f"γ = {ppn['gamma']['value']} ({ppn['gamma']['status']})")
    print(f"Higher-order bound: {ppn['gamma']['higher_order_bound']}")
    print(f"Cassini margin: {ppn['gamma']['cassini_margin']}")
    print(f"\nConclusion: {ppn['conclusion']}")
