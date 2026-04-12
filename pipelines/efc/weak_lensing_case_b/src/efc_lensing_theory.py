"""
EFC Lensing Theory — Case B: Growth-Modified Power Spectrum
============================================================

Case A (nested_sampling pipeline):
    P_eff = P_ΛCDM × Σ² (post-hoc scaling via Alens)
    → Only amplitude, no k/z structure in P(k)

Case B (this module):
    μ(k,z) injected into growth ODE → D(k,z) modified → P(k,z) changes
    → Lensing kernel sees modified P(k,z) with full (k,z) structure
    → Plus Σ(k,z) modifies the lensing convergence directly

This is NOT a proxy — it computes the actual effect of EFC parameters
on the matter power spectrum and lensing observables.

Bridge: (K0, m_sq) → R(k,a) → μ(k,z), η(k,z), Σ(k,z)
    From: tools/cobaya_bridge/bridge_theory.py

    R(k,a) = K0 × Θ(ρ_m(a)) × (Γ'φ̇)² × a⁴ / k⁴
    μ(k,z) = 1 / (1 + R(k,z))
    f(K0, m², k) = 1 - m² / (K0 × k²)
    η(k,z) = 1 + (η_ref - 1) / f_ref × f
    Σ(k,z) = μ × (1 + η) / 2

At (a=1, k=0.05 h/Mpc): (μ, Σ) = (0.94, 1.05)

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-12
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator

# Bridge constants from tools/cobaya_bridge/bridge_theory.py
GAMMA_PHI_SQ = (0.049 * 0.01) ** 2  # 2.401e-7
K_LENS_REF = 0.05  # h/Mpc
ETA_REF = 1.23
K0_REF = 1.66
MSQ_REF = 0.0035
F_REF = 1.0 - MSQ_REF / (K0_REF * K_LENS_REF ** 2)  # 0.156627
RHO_STAR = 1.0e-22  # kg/m³
RHO_M_TODAY = 8.5e-27  # kg/m³


def screening_function(a, Omega_m=0.3):
    """
    Θ(ρ_eff) = exp(-(ρ_eff / ρ_*)²)

    At cosmological densities, Θ ≈ 1 (no screening).
    At galactic/solar system densities, Θ → 0 (GR recovered).
    """
    # Cosmological matter density ρ_m(a) = ρ_m,0 × a⁻³
    rho_m = RHO_M_TODAY * a ** (-3)
    return np.exp(-(rho_m / RHO_STAR) ** 2)


def stiffness_response(K0, k, a):
    """
    R(k, a) = K0 × Θ(ρ_m(a)) × (Γ'φ̇)² × a⁴ / k⁴

    Full scale-dependent stiffness from bridge_theory.py, generalized
    to arbitrary (k, a) instead of just the reference point.
    """
    k = np.atleast_1d(np.asarray(k, dtype=np.float64))
    a = np.atleast_1d(np.asarray(a, dtype=np.float64))
    Theta = screening_function(a)
    # Broadcast: k[:, None] × a[None, :] → shape (Nk, Na)
    k2d = k[:, None] if k.ndim == 1 and a.ndim == 1 else k
    a2d = a[None, :] if k.ndim == 1 and a.ndim == 1 else a
    R = K0 * Theta * GAMMA_PHI_SQ * a2d ** 4 / np.maximum(k2d ** 4, 1e-30)
    return np.squeeze(R)


def mu_kz(K0, k, z):
    """μ(k,z) = 1 / (1 + R(k, a(z)))."""
    a = 1.0 / (1.0 + np.atleast_1d(z))
    R = stiffness_response(K0, k, a)
    return 1.0 / (1.0 + R)


def slip_factor(K0, m_sq, k):
    """f = 1 - m² / (K0 × k²) — linearised slip cancellation."""
    k = np.atleast_1d(np.asarray(k, dtype=np.float64))
    return 1.0 - m_sq / (K0 * k ** 2)


def eta_kz(K0, m_sq, k, z):
    """η(k,z) = 1 + (η_ref - 1) / f_ref × f(K0, m², k)."""
    f = slip_factor(K0, m_sq, k)
    # Cap eta to physical range [1, 2]
    eta = 1.0 + (ETA_REF - 1.0) / F_REF * f
    return np.clip(eta, 1.0, 2.0)


def sigma_kz(K0, m_sq, k, z):
    """Σ(k,z) = μ(k,z) × (1 + η(k,z)) / 2 — lensing parameter."""
    mu = mu_kz(K0, k, z)
    eta = eta_kz(K0, m_sq, k, z)
    if mu.ndim == 2 and eta.ndim == 1:
        # eta has no z-dependence via slip (only k), broadcast
        eta = eta[:, None] if eta.shape[0] == mu.shape[0] else eta
    return mu * (1.0 + eta) / 2.0


# =========================================================================
# Growth factor modification — the core of Case B
# =========================================================================

def growth_ode(a, y, k, K0, Omega_m, H0_km_s_Mpc):
    """
    Modified growth ODE with EFC μ(k,z):

        D'' + (3/a + H'/H) D' - (3/2) Ω_m(a) μ(k,a) D / a² = 0

    where prime = d/da.

    Parameters
    ----------
    a : float
        Scale factor
    y : [D, dD/da]
    k : float
        Wavenumber [h/Mpc]
    K0 : float
        EFC stiffness parameter
    Omega_m : float
        Present-day matter fraction
    H0_km_s_Mpc : float
        Hubble constant (only used for normalization)
    """
    D, dD_da = y

    # H(a)/H0 for flat ΛCDM background
    # (EFC background = ΛCDM; modification is perturbation-only)
    E2 = Omega_m * a ** (-3) + (1.0 - Omega_m)  # (H/H0)²
    E = np.sqrt(E2)

    # dE/da
    dE2_da = -3.0 * Omega_m * a ** (-4)
    dE_da = dE2_da / (2.0 * E)

    # dlnH/da = dE/da / E
    dlnH_da = dE_da / E

    # Ω_m(a) = Ω_m,0 a⁻³ / E²(a)
    Omega_m_a = Omega_m * a ** (-3) / E2

    # EFC modification
    z = 1.0 / a - 1.0
    mu_val = mu_kz(K0, np.array([k]), np.array([z]))
    mu = float(np.squeeze(mu_val))

    # Growth ODE
    d2D_da2 = -(3.0 / a + dlnH_da) * dD_da + 1.5 * Omega_m_a * mu * D / a ** 2

    return [dD_da, d2D_da2]


def compute_growth_ratio(k_array, z_array, K0, Omega_m=0.3, H0=67.36):
    """
    Compute [D_EFC(k,z) / D_GR(z)]² — the growth modification factor.

    This is the key quantity that modifies P(k,z):
        P_EFC(k,z) = P_ΛCDM(k,z) × [D_EFC(k,z) / D_GR(z)]²

    Parameters
    ----------
    k_array : array
        Wavenumbers [h/Mpc]
    z_array : array
        Redshifts (sorted ascending)
    K0 : float
        EFC stiffness
    Omega_m : float
        Matter fraction

    Returns
    -------
    growth_ratio_sq : ndarray, shape (Nk, Nz)
        [D_EFC(k,z) / D_GR(z)]² for each (k, z)
    """
    k_array = np.atleast_1d(k_array)
    z_array = np.atleast_1d(z_array)

    # Scale factors (descending from high z to today)
    a_eval = 1.0 / (1.0 + z_array)
    a_init = min(a_eval.min(), 0.01)  # Start deep in matter domination

    # GR growth (K0=0 limit, μ=1 everywhere)
    sol_gr = solve_ivp(
        lambda a, y: growth_ode(a, y, 0.0, 0.0, Omega_m, H0),
        t_span=(a_init, 1.0),
        y0=[a_init, 1.0],
        t_eval=np.sort(a_eval),
        method='RK45', rtol=1e-6
    )
    D_gr_raw = sol_gr.y[0]  # Unnormalized

    # EFC growth for each k
    growth_ratio_sq = np.ones((len(k_array), len(z_array)))

    for ik, k in enumerate(k_array):
        if K0 == 0:
            continue  # GR limit, ratio = 1

        # Bind k and K0 in closure to avoid late-binding issues
        def _ode(a, y, _k=k, _K0=K0):
            return growth_ode(a, y, _k, _K0, Omega_m, H0)

        sol_efc = solve_ivp(
            _ode,
            t_span=(a_init, 1.0),
            y0=[a_init, 1.0],
            t_eval=np.sort(a_eval),
            method='RK45', rtol=1e-6
        )
        D_efc_raw = sol_efc.y[0]  # Unnormalized

        # Growth ratio: compare unnormalized D at each epoch.
        # Both start from same initial conditions, so the ratio
        # at any a reflects accumulated modification.
        # For P(k,z) modification: we want [D_EFC(a)/D_GR(a)]²
        # normalized so that at a_init the ratio is 1.
        ratio = D_efc_raw / D_gr_raw
        growth_ratio_sq[ik, :] = ratio ** 2

    return growth_ratio_sq


def modified_power_spectrum(k_array, z_array, Pk_LCDM, K0, m_sq, Omega_m=0.3):
    """
    Compute the full Case B modified power spectrum:

        P_eff(k,z) = P_ΛCDM(k,z) × [D_EFC(k,z)/D_GR(z)]² × Σ²(k,z)

    The first factor captures GROWTH modification (μ in ODE).
    The second factor captures LENSING modification (Σ in kernel).

    Parameters
    ----------
    k_array : array, shape (Nk,)
    z_array : array, shape (Nz,)
    Pk_LCDM : array, shape (Nk, Nz) — standard ΛCDM power spectrum
    K0, m_sq : float — EFC bridge parameters
    Omega_m : float

    Returns
    -------
    Pk_eff : array, shape (Nk, Nz) — modified power spectrum
    """
    # Growth modification
    g2 = compute_growth_ratio(k_array, z_array, K0, Omega_m)

    # Lensing modification
    Sig = sigma_kz(K0, m_sq, k_array, z_array)
    if Sig.ndim == 1:
        Sig = Sig[:, None] * np.ones((1, len(z_array)))

    # Full modified P(k,z)
    return Pk_LCDM * g2 * Sig ** 2


# =========================================================================
# Limber integral for angular power spectrum C_ℓ
# =========================================================================

def limber_cl(ell, z_bins_i, z_bins_j, k_array, z_array, Pk_eff,
              chi_of_z, dchi_dz, n_z_func_i, n_z_func_j,
              Omega_m, H0):
    """
    Compute C_ℓ^{ij} via the Limber approximation:

        C_ℓ^{ij} = ∫ W_i(χ) W_j(χ) P_eff(k=ℓ/χ, z(χ)) / χ² dχ

    where W_i(χ) is the lensing efficiency for bin i.

    Parameters
    ----------
    ell : float
        Multipole
    z_bins_i, z_bins_j : tuple (z_lo, z_hi)
    k_array, z_array : arrays
    Pk_eff : array (Nk, Nz)
    chi_of_z : callable
    dchi_dz : callable
    n_z_func_i, n_z_func_j : callable — n(z) for each bin
    Omega_m, H0 : float

    Returns
    -------
    cl : float
    """
    from scipy.interpolate import RectBivariateSpline

    # Interpolate P(k,z) on log-k grid
    log_k = np.log(k_array)
    Pk_interp = RectBivariateSpline(log_k, z_array, np.log(np.clip(Pk_eff, 1e-30, None)))

    # Integration grid in z (Limber: k = (ℓ+0.5)/χ)
    z_int = np.linspace(0.01, 3.0, 200)
    chi_int = np.array([chi_of_z(z) for z in z_int])

    # Lensing efficiency kernel
    c_km_s = 299792.458  # km/s
    prefactor = 1.5 * Omega_m * (H0 / c_km_s) ** 2  # h²/Mpc²

    def W_lens(z_eval, chi_eval, nz_func, z_max=3.0):
        """Lensing efficiency: W(χ) = prefactor × (1+z) × χ × ∫_z^∞ n(z') (χ'-χ)/χ' dz'."""
        W = np.zeros_like(z_eval)
        for i, (z_l, chi_l) in enumerate(zip(z_eval, chi_eval)):
            # Source distribution above lens
            z_src = np.linspace(z_l, z_max, 100)
            nz_src = np.array([nz_func(z) for z in z_src])
            chi_src = np.array([chi_of_z(z) for z in z_src])
            integrand = nz_src * (chi_src - chi_l) / chi_src
            W[i] = prefactor * (1 + z_l) * chi_l * np.trapz(integrand, z_src)
        return W

    W_i = W_lens(z_int, chi_int, n_z_func_i)
    W_j = W_lens(z_int, chi_int, n_z_func_j)

    # Limber: k = (ℓ + 0.5) / χ
    k_limber = (ell + 0.5) / chi_int

    # Evaluate P(k, z) at Limber points
    P_at_limber = np.zeros_like(z_int)
    for i, (lk, z) in enumerate(zip(np.log(k_limber), z_int)):
        if k_array[0] <= k_limber[i] <= k_array[-1]:
            P_at_limber[i] = np.exp(float(Pk_interp(lk, z)))

    # Integrand: W_i W_j P / χ²
    integrand = W_i * W_j * P_at_limber / chi_int ** 2

    # dχ
    dchi = np.gradient(chi_int, z_int) * np.gradient(z_int)
    cl = np.trapz(integrand, chi_int)

    return cl


# =========================================================================
# Consistency check: bridge reproduces reference values
# =========================================================================

def verify_bridge():
    """Verify that at (K0=1.66, m²=0.0035, k=0.05, a=1) we get (μ,Σ)=(0.94,1.05)."""
    k = np.array([K_LENS_REF])
    z = np.array([0.0])

    mu = np.squeeze(mu_kz(K0_REF, k, z))
    sig = np.squeeze(sigma_kz(K0_REF, MSQ_REF, k, z))

    assert abs(float(mu) - 0.94) < 5e-3, f"μ={float(mu)}, expected ~0.94"
    assert abs(float(sig) - 1.05) < 5e-3, f"Σ={float(sig)}, expected ~1.05"
    return True


if __name__ == "__main__":
    print("EFC Lensing Theory — Case B")
    print("=" * 50)

    # Bridge check
    verify_bridge()
    print("Bridge verification: PASS")

    # Show scale dependence
    k = np.logspace(-3, 0, 50)
    z = np.array([0.0, 0.5, 1.0])
    for zi in z:
        mu_vals = mu_kz(K0_REF, k, np.array([zi]))
        sig_vals = sigma_kz(K0_REF, MSQ_REF, k, np.array([zi]))
        print(f"\nz={zi}:")
        print(f"  mu(k=0.001) = {mu_vals[0]:.4f},  mu(k=0.05) = {mu_vals[25]:.4f}")
        print(f"  Sig(k=0.001) = {sig_vals[0]:.4f}, Sig(k=0.05) = {sig_vals[25]:.4f}")

    # Growth modification at reference point
    k_test = np.array([0.01, 0.05, 0.1, 0.5])
    z_test = np.array([0.0, 0.5, 1.0, 2.0])
    g2 = compute_growth_ratio(k_test, z_test, K0_REF)
    print("\nGrowth ratio [D_EFC/D_GR]² at K0=1.66:")
    for ik, k in enumerate(k_test):
        for iz, z in enumerate(z_test):
            print(f"  k={k:.2f}, z={z:.1f}: {g2[ik, iz]:.6f}")
