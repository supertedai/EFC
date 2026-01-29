"""
EFC Weak Lensing Module — μ(k,z) and Σ_lens(k,z) for DES Y6 Testing
====================================================================

Implementation of Energy-Flow Cosmology modified gravity parameters
for cosmological pipeline integration (CosmoSIS/Cobaya).

Based on:
- Magnusson (2025), "Energy-Flow Cosmology: Field Equations for Entropy-Driven Spacetime"
  doi:10.6084/m9.figshare.30421807
- DES Y6 Results: arXiv:2601.14559

Theoretical basis:
    μ(k,z) = 1 + A_μ × Θ(z_t - z) × 1/(1 + k²/k_*²)
    
    With Postulat A: δΣ ∝ ρ_m δ_m (linear matter coupling)
    Baseline: η = Φ/Ψ ≈ 1, so Σ_lens ≈ μ

Author: EFC Initiative
Version: 1.0
Date: 2026-01-29
"""

import numpy as np
from typing import Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.interpolate import interp1d


# =============================================================================
# EFC Parameters
# =============================================================================

@dataclass
class EFCParams:
    """EFC weak lensing parameters."""
    
    # Free parameter (to be constrained by data)
    A_mu: float = 0.0  # EFC amplitude, prior: [-0.5, +0.5]
    
    # Fixed parameters (from protocol)
    z_t: float = 2.0           # Regime transition redshift
    k_star: float = 0.1        # Scale filter [h/Mpc]
    
    # Slip parameter (minimal model: no slip)
    eta: float = 1.0           # Φ/Ψ ratio
    
    # Optional: soft transition width
    delta_z: float = 0.0       # If > 0, use tanh instead of Heaviside
    
    def __post_init__(self):
        """Validate parameters."""
        if not -1.0 <= self.A_mu <= 1.0:
            raise ValueError(f"A_mu={self.A_mu} outside physical range [-1, 1]")
        if self.z_t <= 0:
            raise ValueError(f"z_t={self.z_t} must be positive")
        if self.k_star <= 0:
            raise ValueError(f"k_star={self.k_star} must be positive")


# =============================================================================
# Core Functions: μ(k,z) and Σ_lens(k,z)
# =============================================================================

def mu_efc(k: np.ndarray, z: np.ndarray, params: EFCParams) -> np.ndarray:
    """
    Compute EFC modified gravity parameter μ(k,z).
    
    μ(k,z) = 1 + A_μ × g(z) × h(k)
    
    where:
        g(z) = Θ(z_t - z)  [regime gating]
        h(k) = 1/(1 + k²/k_*²)  [scale filter]
    
    Parameters
    ----------
    k : array_like
        Wavenumber [h/Mpc]
    z : array_like
        Redshift
    params : EFCParams
        EFC parameters
        
    Returns
    -------
    mu : ndarray
        Shape (len(k), len(z)) or broadcast-compatible
    """
    k = np.atleast_1d(k)
    z = np.atleast_1d(z)
    
    # Scale filter h(k)
    h_k = 1.0 / (1.0 + (k / params.k_star)**2)
    
    # Regime gating g(z)
    if params.delta_z > 0:
        # Smooth transition
        g_z = 0.5 * (1.0 - np.tanh((z - params.z_t) / params.delta_z))
    else:
        # Sharp Heaviside
        g_z = np.where(z < params.z_t, 1.0, 0.0)
    
    # Broadcast to (k, z) grid
    h_k = h_k[:, np.newaxis] if k.ndim == 1 else h_k
    g_z = g_z[np.newaxis, :] if z.ndim == 1 else g_z
    
    # μ(k,z)
    mu = 1.0 + params.A_mu * h_k * g_z
    
    return np.squeeze(mu)


def sigma_lens_efc(k: np.ndarray, z: np.ndarray, params: EFCParams) -> np.ndarray:
    """
    Compute EFC lensing parameter Σ_lens(k,z).
    
    Σ_lens = (μ/2)(1 + η)
    
    In minimal model (η=1): Σ_lens = μ
    
    Parameters
    ----------
    k : array_like
        Wavenumber [h/Mpc]
    z : array_like
        Redshift
    params : EFCParams
        EFC parameters
        
    Returns
    -------
    sigma_lens : ndarray
    """
    mu = mu_efc(k, z, params)
    sigma_lens = 0.5 * mu * (1.0 + params.eta)
    return sigma_lens


def eta_efc(k: np.ndarray, z: np.ndarray, params: EFCParams) -> np.ndarray:
    """
    Compute gravitational slip η = Φ/Ψ.
    
    In minimal EFC model: η = 1 (no slip).
    
    Future extension: η(k,z) from anisotropic stress in T^(S,J)_ij.
    """
    k = np.atleast_1d(k)
    z = np.atleast_1d(z)
    return np.full((len(k), len(z)), params.eta)


# =============================================================================
# Growth Factor Modification
# =============================================================================

def growth_ode_efc(a: float, y: np.ndarray, 
                   H_func: Callable, Omega_m_func: Callable,
                   k: float, params: EFCParams) -> np.ndarray:
    """
    ODE for scale-dependent growth factor with EFC μ(k,z).
    
    d²D/da² + (3/a + dlnH/da) dD/da - (3/2) Ω_m(a) μ(k,a) D / a² = 0
    
    Rewritten as first-order system:
        y[0] = D(a)
        y[1] = dD/da
    
    Parameters
    ----------
    a : float
        Scale factor
    y : array
        [D, dD/da]
    H_func : callable
        H(a) in units where H0=1
    Omega_m_func : callable
        Ω_m(a)
    k : float
        Wavenumber [h/Mpc]
    params : EFCParams
        EFC parameters
        
    Returns
    -------
    dyda : array
        [dD/da, d²D/da²]
    """
    z = 1.0/a - 1.0
    D, dD_da = y
    
    H = H_func(a)
    Omega_m = Omega_m_func(a)
    
    # Numerical derivative of ln(H)
    da = 1e-5
    dln_H_da = (np.log(H_func(a + da)) - np.log(H_func(a - da))) / (2 * da)
    
    # EFC modification
    mu = float(mu_efc(np.array([k]), np.array([z]), params))
    
    # Growth ODE
    d2D_da2 = -(3.0/a + dln_H_da) * dD_da + 1.5 * Omega_m * mu * D / a**2
    
    return np.array([dD_da, d2D_da2])


def compute_growth_factor_efc(k: float, z_array: np.ndarray,
                               H_func: Callable, Omega_m_func: Callable,
                               params: EFCParams) -> np.ndarray:
    """
    Compute scale-dependent growth factor D(k,z) with EFC.
    
    Parameters
    ----------
    k : float
        Wavenumber [h/Mpc]
    z_array : array
        Redshifts (must be sorted descending, i.e., high z first)
    H_func : callable
        H(a)
    Omega_m_func : callable
        Ω_m(a)
    params : EFCParams
        EFC parameters
        
    Returns
    -------
    D : array
        Growth factor normalized to D(z=0) = 1
    """
    from scipy.integrate import solve_ivp
    
    # Initial conditions at high z (matter domination)
    a_init = 1.0 / (1.0 + z_array[0])
    y0 = [a_init, 1.0]  # D ∝ a in matter domination
    
    # Scale factors to evaluate
    a_array = 1.0 / (1.0 + z_array)
    
    # Solve ODE
    sol = solve_ivp(
        lambda a, y: growth_ode_efc(a, y, H_func, Omega_m_func, k, params),
        t_span=(a_init, 1.0),
        y0=y0,
        t_eval=a_array,
        method='RK45',
        rtol=1e-8
    )
    
    D = sol.y[0]
    
    # Normalize to D(z=0) = 1
    D = D / D[-1]
    
    return D


# =============================================================================
# Lensing Kernel Modification
# =============================================================================

def modified_lensing_kernel(chi: np.ndarray, chi_s: float,
                            k: np.ndarray, z: np.ndarray,
                            params: EFCParams,
                            chi_of_z: Callable) -> np.ndarray:
    """
    Compute EFC-modified lensing kernel.
    
    W(χ) = (3/2) Ω_m H₀² (1+z) χ (χ_s - χ)/χ_s × Σ_lens(k, z(χ))
    
    Parameters
    ----------
    chi : array
        Comoving distance [Mpc/h]
    chi_s : float
        Source comoving distance
    k : array
        Wavenumbers for Σ_lens evaluation
    z : array
        Redshifts corresponding to chi
    params : EFCParams
        EFC parameters
    chi_of_z : callable
        χ(z) relation
        
    Returns
    -------
    W_modified : array
        Modified lensing kernel
    """
    # Standard geometric kernel (without prefactors)
    W_geo = chi * (chi_s - chi) / chi_s
    W_geo = np.where(chi < chi_s, W_geo, 0.0)
    
    # EFC modification
    sigma = sigma_lens_efc(k, z, params)
    
    # If sigma is 2D (k, z), need to handle properly
    if sigma.ndim == 2:
        # Return modified kernel for each k
        W_modified = W_geo[np.newaxis, :] * sigma
    else:
        W_modified = W_geo * sigma
    
    return W_modified


# =============================================================================
# CosmoSIS Interface
# =============================================================================

def setup_cosmosis(options):
    """
    CosmoSIS setup function.
    
    Read EFC parameters from ini file.
    """
    from cosmosis.datablock import option_section
    
    # Read parameters
    A_mu = options.get_double(option_section, "A_mu", default=0.0)
    z_t = options.get_double(option_section, "z_t", default=2.0)
    k_star = options.get_double(option_section, "k_star", default=0.1)
    eta = options.get_double(option_section, "eta", default=1.0)
    
    params = EFCParams(A_mu=A_mu, z_t=z_t, k_star=k_star, eta=eta)
    
    return params


def execute_cosmosis(block, params):
    """
    CosmoSIS execute function.
    
    Modify matter power spectrum or lensing signals.
    """
    from cosmosis.datablock import names
    
    # Get k and z arrays from datablock
    k = block[names.matter_power_nl, "k_h"]
    z = block[names.matter_power_nl, "z"]
    P_k_z = block[names.matter_power_nl, "P_k"]
    
    # Compute μ(k,z)
    mu = mu_efc(k, z, params)
    
    # Option 1: Modify P(k) directly (approximate)
    # P_modified = P_k_z * mu**2  # If μ affects growth
    
    # Option 2: Store μ and Σ for later use in shear calculation
    block["efc", "mu_k_z"] = mu
    block["efc", "sigma_lens_k_z"] = sigma_lens_efc(k, z, params)
    block["efc", "k"] = k
    block["efc", "z"] = z
    
    return 0


# =============================================================================
# Cobaya Interface
# =============================================================================

class EFCLensing:
    """
    Cobaya theory class for EFC modified lensing.
    
    Usage in Cobaya yaml:
    
    theory:
      camb:
        ...
      efc_lensing:
        python_path: /path/to/efc_weak_lensing.py
        class: EFCLensing
        
    params:
      A_mu:
        prior:
          min: -0.5
          max: 0.5
        latex: A_\\mu
    """
    
    def initialize(self):
        """Initialize EFC theory."""
        self.z_t = self.provider.get_param("z_t") if hasattr(self, 'provider') else 2.0
        self.k_star = self.provider.get_param("k_star") if hasattr(self, 'provider') else 0.1
    
    def get_requirements(self):
        """Specify requirements from CAMB/CLASS."""
        return {
            "Pk_grid": {"k_max": 10.0, "z": [0, 0.5, 1.0, 1.5, 2.0]},
            "comoving_radial_distance": {"z": [0, 0.5, 1.0, 1.5, 2.0]},
        }
    
    def calculate(self, state, want_derived=True, **params_values):
        """
        Calculate EFC modifications.
        
        Parameters
        ----------
        state : dict
            Output state dictionary
        params_values : dict
            Sampled parameters including A_mu
        """
        A_mu = params_values.get("A_mu", 0.0)
        
        params = EFCParams(
            A_mu=A_mu,
            z_t=self.z_t,
            k_star=self.k_star
        )
        
        # Get P(k,z) from provider
        k, z, Pk = self.provider.get_Pk_grid()
        
        # Compute μ(k,z) and Σ_lens(k,z)
        mu = mu_efc(k, z, params)
        sigma_lens = sigma_lens_efc(k, z, params)
        
        # Store for likelihood
        state["mu_k_z"] = mu
        state["sigma_lens_k_z"] = sigma_lens
        state["k_efc"] = k
        state["z_efc"] = z
    
    def get_mu(self, k, z):
        """Get μ(k,z) for external use."""
        return self._current_state.get("mu_k_z")
    
    def get_sigma_lens(self, k, z):
        """Get Σ_lens(k,z) for external use."""
        return self._current_state.get("sigma_lens_k_z")


# =============================================================================
# Testing and Validation
# =============================================================================

def test_mu_limits():
    """Test that μ → 1 in GR limit and at high z."""
    params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
    
    k = np.logspace(-3, 1, 100)  # 0.001 to 10 h/Mpc
    
    # At z > z_t: should be μ = 1
    z_high = np.array([3.0])
    mu_high = mu_efc(k, z_high, params)
    assert np.allclose(mu_high, 1.0), f"μ should be 1 at z > z_t, got {mu_high}"
    
    # At z < z_t, k >> k_*: should approach 1 (scale filter)
    z_low = np.array([0.5])
    mu_low = mu_efc(k[-1:], z_low, params)  # k = 10 >> k_* = 0.1
    assert np.abs(mu_low - 1.0) < 0.01, f"μ should → 1 at k >> k_*, got {mu_low}"
    
    # At z < z_t, k << k_*: should be 1 + A_μ
    mu_low_k = mu_efc(k[:1], z_low, params)  # k = 0.001 << k_* = 0.1
    expected = 1.0 + params.A_mu
    assert np.abs(mu_low_k - expected) < 0.01, f"μ should be {expected} at k << k_*, got {mu_low_k}"
    
    print("✓ All limit tests passed")


def test_s8_scaling():
    """
    Estimate S8 scaling from EFC.
    
    Rough approximation: S8_EFC / S8_ΛCDM ≈ √(Σ_lens_eff)
    """
    # Target: explain DES Y6 S8 = 0.789 vs Planck S8 ≈ 0.83
    ratio_target = 0.789 / 0.83  # ≈ 0.95
    
    # At DES effective scales/redshifts
    k_eff = 0.1  # h/Mpc
    z_eff = 0.5
    
    # What A_μ gives this?
    # Σ_lens ≈ μ = 1 + A_μ × g(z) × h(k)
    # At k = k_*, h(k) = 0.5
    # At z = 0.5 < z_t = 2, g(z) = 1
    # So μ = 1 + 0.5 × A_μ
    # Want √μ ≈ 0.95, so μ ≈ 0.90
    # 1 + 0.5 × A_μ = 0.90 → A_μ = -0.20
    
    A_mu_needed = -0.20
    
    params = EFCParams(A_mu=A_mu_needed, z_t=2.0, k_star=0.1)
    mu = mu_efc(np.array([k_eff]), np.array([z_eff]), params)
    
    s8_ratio = np.sqrt(float(mu))
    
    print(f"For A_μ = {A_mu_needed}:")
    print(f"  μ(k={k_eff}, z={z_eff}) = {float(mu):.3f}")
    print(f"  S8 ratio ≈ √μ = {s8_ratio:.3f}")
    print(f"  Target ratio = {ratio_target:.3f}")
    print(f"  Match: {'✓' if np.abs(s8_ratio - ratio_target) < 0.02 else '✗'}")


def plot_mu_k_z(params: Optional[EFCParams] = None, save_path: Optional[str] = None):
    """
    Plot μ(k,z) as function of k for different z.
    
    Parameters
    ----------
    params : EFCParams, optional
        If None, use default with A_μ = -0.1
    save_path : str, optional
        Path to save figure
    """
    import matplotlib.pyplot as plt
    
    if params is None:
        params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
    
    k = np.logspace(-3, 1, 200)
    z_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for z in z_values:
        mu = mu_efc(k, np.array([z]), params)
        label = f"z = {z}" + (" (GR)" if z >= params.z_t else "")
        ax.semilogx(k, mu, label=label)
    
    ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5, label='GR')
    ax.axvline(params.k_star, color='red', linestyle=':', alpha=0.5, label=f'k_* = {params.k_star}')
    
    ax.set_xlabel(r'$k$ [h/Mpc]')
    ax.set_ylabel(r'$\mu(k,z)$')
    ax.set_title(f'EFC Modified Gravity: $A_\\mu = {params.A_mu}$, $z_t = {params.z_t}$')
    ax.legend()
    ax.set_xlim(1e-3, 10)
    ax.set_ylim(0.85, 1.05)
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to {save_path}")
    
    plt.show()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("EFC Weak Lensing Module v1.0")
    print("=" * 50)
    
    # Run tests
    print("\nRunning tests...")
    test_mu_limits()
    
    print("\nS8 scaling estimate:")
    test_s8_scaling()
    
    # Example usage
    print("\n" + "=" * 50)
    print("Example: μ(k,z) for A_μ = -0.1")
    
    params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
    
    k = np.array([0.01, 0.1, 1.0])
    z = np.array([0.0, 1.0, 2.0, 3.0])
    
    print(f"\nk [h/Mpc]: {k}")
    print(f"z: {z}")
    print(f"\nμ(k,z):")
    mu = mu_efc(k, z, params)
    print(mu)
    
    # Plot if matplotlib available
    try:
        plot_mu_k_z(params)
    except ImportError:
        print("\nMatplotlib not available, skipping plot")
