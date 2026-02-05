"""
EFC Sigma(k,z) Module - M2 Activation
======================================

Implements Energy-Flow Cosmology gravitational response modification
for weak lensing cosmic shear observables.

Σ(k,z) = μ_EFC(k, S(z)) × [1 + η(k,z)] / 2

For M2 initial test: Simplified form with η=1 (no slip)
Σ(k,z) = μ_EFC(k, S(z))

This module integrates with KCAP/CosmoSIS project_2d.py
"""

import numpy as np
from scipy.interpolate import interp1d


class EFCSigma:
    """
    EFC gravitational response Σ(k,z) for lensing observables.

    Modified Poisson equation:
        ∇²Ψ = 4πG a² ρ Δ × μ_EFC(k, S)

    Lensing potential:
        Φ + Ψ = 2Ψ × Σ(k,z)
        where Σ(k,z) ≡ μ_EFC(k, S) for η=1
    """

    def __init__(self, mode='phenomenological'):
        """
        Initialize EFC Sigma module.

        Parameters:
        -----------
        mode : str
            'phenomenological' : Simple parametric form for testing
            'lcdm' : Return Σ=1 everywhere (ΛCDM limit)
            'derived' : Full field-theoretic derivation (future)
        """
        self.mode = mode

        # Phenomenological parameters (M2 test values)
        self.alpha_L2 = 0.05  # L1→L2 transition strength
        self.k_transition = 0.1  # h/Mpc (transition scale)
        self.z_activation = 0.5  # Redshift where EFC activates

    def mu_EFC(self, k, z, S=None):
        """
        Compute μ_EFC(k, z, S) - EFC gravitational enhancement.

        Parameters:
        -----------
        k : float or array
            Wavenumber in h/Mpc
        z : float or array
            Redshift
        S : float or array, optional
            Structural state parameter (default: use redshift proxy)

        Returns:
        --------
        mu : float or array
            Gravitational enhancement factor μ_EFC
            μ = 1.0 for ΛCDM
            μ > 1.0 for EFC enhancement
        """
        # Ensure array format
        k = np.atleast_1d(np.asarray(k, dtype=float))
        z = np.atleast_1d(np.asarray(z, dtype=float))

        if self.mode == 'lcdm':
            # ΛCDM limit - no modification
            return np.squeeze(np.ones_like(k))

        elif self.mode == 'phenomenological':
            # Simple parametric form for M2 testing
            # Inspired by regime-transition framework

            # Scale-dependent part (k-dependence)
            # Smooth transition around k_transition
            k_factor = 1.0 + self.alpha_L2 * np.tanh((k - self.k_transition) / 0.05)

            # Redshift-dependent activation (late-time enhancement)
            # EFC effects stronger at low-z (more structure)
            if np.isscalar(z) or len(z) == 1:
                z_val = float(z) if np.isscalar(z) else z[0]
                if z_val < self.z_activation:
                    z_factor = 1.0 + self.alpha_L2 * (1.0 - z_val / self.z_activation)
                else:
                    z_factor = 1.0
            else:
                z_factor = np.where(z < self.z_activation,
                                   1.0 + self.alpha_L2 * (1.0 - z / self.z_activation),
                                   1.0)

            # Combined response
            if np.isscalar(z_factor):
                mu = k_factor * z_factor
            else:
                mu = np.outer(z_factor, np.ones_like(k)) * k_factor

            return np.squeeze(mu)

        elif self.mode == 'derived':
            # TODO: Full field-theoretic derivation
            # mu = f(k, S, Θ(ρ), regime_boundaries, ...)
            raise NotImplementedError("Derived mode requires full EFC field equations")

        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def Sigma_kz(self, k, z, S=None, eta=1.0):
        """
        Compute Σ(k,z) for lensing observables.

        Σ(k,z) = μ_EFC(k, S) × [1 + η(k,z)] / 2

        Parameters:
        -----------
        k : float or array
            Wavenumber in h/Mpc
        z : float or array
            Redshift
        S : float or array, optional
            Structural state
        eta : float or array, optional
            Gravitational slip parameter (default: 1.0 = no slip)

        Returns:
        --------
        Sigma : float or array
            Lensing modification factor
            Sigma = 1.0 for ΛCDM (μ=1, η=1)
        """
        mu = self.mu_EFC(k, z, S)
        Sigma = mu * (1.0 + eta) / 2.0

        return Sigma

    def get_modification_grid(self, k_array, z_array, S_array=None):
        """
        Get full 2D modification grid for KCAP integration.

        Parameters:
        -----------
        k_array : array (n_k,)
            Wavenumber grid in h/Mpc
        z_array : array (n_z,)
            Redshift grid
        S_array : array (n_z,), optional
            Structural state grid

        Returns:
        --------
        Sigma_grid : array (n_z, n_k)
            2D grid of Σ(k,z) values
        """
        k_array = np.atleast_1d(k_array)
        z_array = np.atleast_1d(z_array)

        n_k = len(k_array)
        n_z = len(z_array)

        Sigma_grid = np.zeros((n_z, n_k))

        for i_z, z in enumerate(z_array):
            S = S_array[i_z] if S_array is not None else None
            Sigma_grid[i_z, :] = self.Sigma_kz(k_array, z, S)

        return Sigma_grid

    def modify_power_spectrum(self, P_kz, k_array, z_array):
        """
        Apply EFC modification to matter power spectrum.

        P_EFC(k,z) = P_ΛCDM(k,z) × Σ(k,z)²

        Parameters:
        -----------
        P_kz : array (n_z, n_k)
            Matter power spectrum grid
        k_array : array (n_k,)
            Wavenumber grid in h/Mpc
        z_array : array (n_z,)
            Redshift grid

        Returns:
        --------
        P_EFC : array (n_z, n_k)
            Modified power spectrum
        """
        Sigma_grid = self.get_modification_grid(k_array, z_array)
        P_EFC = P_kz * Sigma_grid**2

        return P_EFC


# ============================================================================
# M2 Test Functions
# ============================================================================

def test_efc_sigma():
    """Quick test of EFC Sigma implementation."""
    print("="*60)
    print("EFC Sigma(k,z) Module - M2 Test")
    print("="*60)

    efc = EFCSigma(mode='phenomenological')

    # Test parameters
    k_test = np.logspace(-3, 1, 50)  # 0.001 to 10 h/Mpc
    z_test = np.array([0.0, 0.3, 0.6, 1.0, 2.0])

    print("\nTest 1: Σ(k,z) at different redshifts")
    print("-" * 60)
    for z in z_test:
        Sigma = efc.Sigma_kz(k_test, z)
        k_idx = np.argmin(np.abs(k_test - 0.1))
        print(f"z={z:.1f}: Σ(k=0.1)={Sigma[k_idx]:.4f}")

    print("\nTest 2: Scale dependence at z=0.3")
    print("-" * 60)
    k_scales = [0.01, 0.1, 1.0]
    z_fixed = 0.3
    for k in k_scales:
        Sigma = efc.Sigma_kz(k, z_fixed)
        print(f"k={k:.2f} h/Mpc: Σ={float(Sigma):.4f}")

    print("\nTest 3: ΛCDM limit check")
    print("-" * 60)
    efc_lcdm = EFCSigma(mode='lcdm')
    Sigma_lcdm = efc_lcdm.Sigma_kz(0.1, 0.5)
    print(f"mode='lcdm': Σ(k=0.1, z=0.5) = {float(Sigma_lcdm):.6f} (should be 1.0)")

    print("\nTest 4: Zero alpha limit")
    print("-" * 60)
    efc_zero = EFCSigma(mode='phenomenological')
    efc_zero.alpha_L2 = 0.0
    Sigma_zero = efc_zero.Sigma_kz(0.1, 0.5)
    print(f"α_L2=0.0: Σ(k=0.1, z=0.5) = {float(Sigma_zero):.6f} (should be 1.0)")

    print("\nTest 5: 2D grid generation")
    print("-" * 60)
    k_grid = np.array([0.01, 0.1, 1.0])
    z_grid = np.array([0.0, 0.5, 1.0])
    efc_test = EFCSigma(mode='phenomenological')
    Sigma_2d = efc_test.get_modification_grid(k_grid, z_grid)
    print(f"Grid shape: {Sigma_2d.shape}")
    print(f"Σ(z=0, k=0.1): {Sigma_2d[0,1]:.4f}")
    print(f"Σ(z=0.5, k=0.1): {Sigma_2d[1,1]:.4f}")
    print(f"Σ(z=1.0, k=0.1): {Sigma_2d[2,1]:.4f}")

    print("\n" + "="*60)
    print("M2 Test Complete - EFC Module Ready")
    print("="*60)

    return True


if __name__ == "__main__":
    test_efc_sigma()
