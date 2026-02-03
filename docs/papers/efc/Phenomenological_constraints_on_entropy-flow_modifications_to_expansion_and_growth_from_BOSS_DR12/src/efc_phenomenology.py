"""
EFC Phenomenological Model Implementation

Single-parameter extension where α_L2 modifies both expansion and growth
with opposite signs - a distinctive EFC signature.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31243828
"""

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize

# Physical constants
C_LIGHT = 299792.458  # km/s


class EFCPhenomenology:
    """
    EFC phenomenological model with single entropy-coupling parameter.

    The model modifies ΛCDM observables:
    - D_M^EFC(z) = D_M^ΛCDM(z) × [1 + α_L2 × g_D(z)]
    - H^EFC(z) = H^ΛCDM(z) × [1 + α_L2 × g_H(z)]
    - fσ8^EFC(z) = fσ8^ΛCDM(z) × [1 + α_L2 × g_growth(z)]

    Key feature: g_D > 0 and g_growth < 0, so positive α_L2
    increases distances while suppressing growth (anti-correlation).

    Parameters
    ----------
    H0 : float
        Hubble constant in km/s/Mpc (default: 69.65, EFC best-fit)
    Omega_m : float
        Matter density parameter (default: 0.347)
    sigma8 : float
        Amplitude of matter fluctuations (default: 0.669)
    alpha_L2 : float
        Entropy-coupling parameter (default: 0.353)
    """

    def __init__(self, H0=69.65, Omega_m=0.347, sigma8=0.669, alpha_L2=0.353):
        self.H0 = H0
        self.Omega_m = Omega_m
        self.Omega_L = 1.0 - Omega_m
        self.sigma8 = sigma8
        self.alpha_L2 = alpha_L2

        # Fiducial sound horizon for BOSS DR12
        self.rs_fid = 147.78  # Mpc

    def E(self, z):
        """Dimensionless Hubble parameter E(z) = H(z)/H0 in ΛCDM."""
        return np.sqrt(self.Omega_m * (1 + z)**3 + self.Omega_L)

    def Omega_m_z(self, z):
        """Redshift-dependent matter density parameter."""
        return self.Omega_m * (1 + z)**3 / self.E(z)**2

    # ==================== Coupling Functions ====================

    def g_D(self, z):
        """
        Distance coupling function.

        g_D(z) = (1 - Ωm(z))/(1+z) × ln(1+z)

        Properties:
        - g_D(0) = 0
        - g_D → 0 at high z (matter dominated)
        - Peaks at z ~ 0.5-0.7 (dark energy dominated)
        - Always positive for z > 0
        """
        if z == 0:
            return 0.0
        Omega_m_z = self.Omega_m_z(z)
        return (1 - Omega_m_z) / (1 + z) * np.log(1 + z)

    def g_H(self, z):
        """
        Hubble coupling function.

        Related to g_D by approximate consistency with integral relation.
        """
        if z == 0:
            return 0.0
        Omega_m_z = self.Omega_m_z(z)
        E2 = self.E(z)**2

        term1 = (1 - Omega_m_z) / (1 + z)
        term2 = 1 - np.log(1 + z)
        term3 = 1 + 3 * Omega_m_z - 3 * self.Omega_m * (1 + z)**3 / E2

        return -term1 * term2 * term3

    def g_growth(self, z):
        """
        Growth coupling function.

        g_growth(z) = -[1 - Ωm(z)]^(3/2) × ln(1+z) / (1+z)^(1/2)

        Properties:
        - Always NEGATIVE for z > 0
        - Opposite sign to g_D (anti-correlation!)
        - Positive α_L2 suppresses growth
        """
        if z == 0:
            return 0.0
        Omega_m_z = self.Omega_m_z(z)
        return -(1 - Omega_m_z)**(3/2) * np.log(1 + z) / np.sqrt(1 + z)

    # ==================== ΛCDM Observables ====================

    def H_LCDM(self, z):
        """ΛCDM Hubble parameter in km/s/Mpc."""
        return self.H0 * self.E(z)

    def DM_LCDM(self, z):
        """ΛCDM comoving distance in Mpc."""
        integrand = lambda zp: 1.0 / self.E(zp)
        result, _ = quad(integrand, 0, z)
        return C_LIGHT / self.H0 * result

    def f_LCDM(self, z):
        """ΛCDM growth rate f(z) ≈ Ωm(z)^0.55."""
        return self.Omega_m_z(z)**0.55

    def sigma8_z_LCDM(self, z):
        """
        ΛCDM σ8(z) using growth factor approximation.
        """
        # Simplified: σ8(z) ≈ σ8(0) × D(z)/D(0)
        # Using approximation D(z) ∝ (1+z)^(-1) in matter era
        # More accurate: integrate growth equation
        D_ratio = self._growth_factor_ratio(z)
        return self.sigma8 * D_ratio

    def _growth_factor_ratio(self, z):
        """Growth factor D(z)/D(0) using numerical integration."""
        # Solve growth equation: D'' + (2 + E'/E)D' - 3/2 Ωm(z) D = 0
        # Simplified approximation for demonstration
        from scipy.integrate import odeint

        def growth_ode(y, a):
            D, dD = y
            z_a = 1/a - 1
            E_a = self.E(z_a)
            Omega_m_a = self.Omega_m_z(z_a)

            # d²D/da² + (3/a + E'/E)dD/da - 3Ωm/(2a²)D = 0
            # Convert to first-order system
            d2D = (3 * Omega_m_a / (2 * a**2) * D
                   - (3/a + self._dlnE_dlna(z_a)) * dD)
            return [dD, d2D]

        a_init = 1e-3
        a_final = 1.0 / (1 + z)
        a_grid = np.linspace(a_init, 1.0, 1000)

        # Initial conditions in matter era: D ∝ a
        y0 = [a_init, 1.0]

        solution = odeint(growth_ode, y0, a_grid)
        D_grid = solution[:, 0]

        # Interpolate to get D(z) and D(0)
        D_z = np.interp(a_final, a_grid, D_grid)
        D_0 = D_grid[-1]

        return D_z / D_0

    def _dlnE_dlna(self, z):
        """d ln E / d ln a for growth equation."""
        a = 1.0 / (1 + z)
        E2 = self.E(z)**2
        return -3 * self.Omega_m * (1 + z)**3 / (2 * E2)

    def fsigma8_LCDM(self, z):
        """ΛCDM fσ8(z) = f(z) × σ8(z)."""
        return self.f_LCDM(z) * self.sigma8_z_LCDM(z)

    # ==================== EFC Modified Observables ====================

    def H_EFC(self, z):
        """EFC-modified Hubble parameter."""
        return self.H_LCDM(z) * (1 + self.alpha_L2 * self.g_H(z))

    def DM_EFC(self, z):
        """EFC-modified comoving distance."""
        return self.DM_LCDM(z) * (1 + self.alpha_L2 * self.g_D(z))

    def fsigma8_EFC(self, z):
        """EFC-modified growth rate fσ8."""
        return self.fsigma8_LCDM(z) * (1 + self.alpha_L2 * self.g_growth(z))

    # ==================== BAO Observables ====================

    def DM_over_rs(self, z, rs=None):
        """D_M(z)/r_s for BAO analysis."""
        if rs is None:
            rs = self.rs_fid
        return self.DM_EFC(z) / rs

    def H_times_rs(self, z, rs=None):
        """H(z) × r_s for BAO analysis."""
        if rs is None:
            rs = self.rs_fid
        return self.H_EFC(z) * rs

    def DH_over_rs(self, z, rs=None):
        """D_H(z)/r_s = c/(H(z)×r_s) for BAO analysis."""
        if rs is None:
            rs = self.rs_fid
        return C_LIGHT / (self.H_EFC(z) * rs)

    # ==================== Predictions ====================

    def gravitational_slip(self, z):
        """
        EFC prediction for gravitational slip η = Φ/Ψ.

        EFC predicts η = 1 (no slip) at all z, distinguishing it
        from scalar-tensor and f(R) theories.
        """
        return 1.0  # EFC prediction

    def compute_observables(self, z_array):
        """
        Compute all observables at given redshifts.

        Returns dict with DM, H, fsigma8 for both ΛCDM and EFC.
        """
        results = {'z': z_array}

        for model in ['LCDM', 'EFC']:
            DM_func = self.DM_LCDM if model == 'LCDM' else self.DM_EFC
            H_func = self.H_LCDM if model == 'LCDM' else self.H_EFC
            fs8_func = self.fsigma8_LCDM if model == 'LCDM' else self.fsigma8_EFC

            results[f'DM_{model}'] = np.array([DM_func(z) for z in z_array])
            results[f'H_{model}'] = np.array([H_func(z) for z in z_array])
            results[f'fsigma8_{model}'] = np.array([fs8_func(z) for z in z_array])

        return results

    def __repr__(self):
        return (f"EFCPhenomenology(H0={self.H0}, Omega_m={self.Omega_m}, "
                f"sigma8={self.sigma8}, alpha_L2={self.alpha_L2})")


# Best-fit models for convenience
LCDM_BEST_FIT = EFCPhenomenology(H0=66.57, Omega_m=0.359, sigma8=0.667, alpha_L2=0.0)
EFC_BEST_FIT = EFCPhenomenology(H0=69.65, Omega_m=0.347, sigma8=0.669, alpha_L2=0.353)


def demonstrate_anticorrelation():
    """
    Demonstrate the key EFC signature: anti-correlated expansion and growth.
    """
    model = EFC_BEST_FIT

    print("EFC Anti-Correlation Signature")
    print("=" * 50)
    print(f"α_L2 = {model.alpha_L2}")
    print()
    print(f"{'z':>6} {'g_D(z)':>10} {'g_growth(z)':>12} {'Sign':>8}")
    print("-" * 40)

    for z in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
        g_D = model.g_D(z)
        g_growth = model.g_growth(z)
        sign = "opposite" if g_D * g_growth < 0 else "same"
        print(f"{z:>6.1f} {g_D:>10.4f} {g_growth:>12.4f} {sign:>8}")

    print()
    print("Positive α_L2 → larger D_M (farther) AND smaller fσ8 (less growth)")
    print("This anti-correlation is a distinctive EFC signature!")


if __name__ == '__main__':
    demonstrate_anticorrelation()
