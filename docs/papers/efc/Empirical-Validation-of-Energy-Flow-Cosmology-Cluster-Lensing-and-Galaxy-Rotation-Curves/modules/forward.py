"""
EFC Forward Models
==================
Forward models for different observables:
- Lensing convergence κ (clusters)
- Rotation velocity v(r) (galaxies)
- Velocity dispersion σ (ellipticals) [future]
"""

import numpy as np
from .kernels import make_kernel_yukawa, make_kernel_1d_yukawa

__all__ = ['forward_kappa_2d', 'forward_velocity_1d', 'fft_convolve']


def fft_convolve(a, K):
    """Fast 2D convolution via FFT."""
    return np.fft.irfftn(np.fft.rfftn(a) * np.fft.rfftn(K), s=a.shape)


def forward_kappa_2d(theta, Q_gal, Q_gas, kernel_cfg):
    """
    Forward model for lensing convergence.
    
    κ_model = A · (K ⊛ Q_gal) + (A/R) · (K ⊛ Q_gas) + κ₀
    
    Parameters
    ----------
    theta : array
        [logA, logR, loglam, k0]
    Q_gal : 2D array
        Galaxy/collisionless source term
    Q_gas : 2D array
        Gas/dissipative source term
    kernel_cfg : dict
        Kernel configuration (r0_px, etc.)
    
    Returns
    -------
    kappa_model : 2D array
    """
    logA, logR, loglam, k0 = theta
    A = np.exp(logA)
    R = np.exp(logR)
    lam = np.exp(loglam)
    
    K = make_kernel_yukawa(Q_gal.shape, lam_px=lam, r0_px=kernel_cfg.get("r0_px", 2.0))
    
    k_gal = fft_convolve(Q_gal, K)
    k_gas = fft_convolve(Q_gas, K)
    
    return A * k_gal + (A / R) * k_gas + k0


def forward_kappa_gal_only(theta, Q_gal, kernel_cfg):
    """
    Simplified forward model: galaxy-only (R → ∞).
    
    κ_model = A · (K ⊛ Q_gal) + κ₀
    
    Parameters
    ----------
    theta : array
        [logA, loglam, k0]
    """
    logA, loglam, k0 = theta
    A = np.exp(logA)
    lam = np.exp(loglam)
    
    K = make_kernel_yukawa(Q_gal.shape, lam_px=lam, r0_px=kernel_cfg.get("r0_px", 2.0))
    k_gal = fft_convolve(Q_gal, K)
    
    return A * k_gal + k0


# =============================================================================
# ROTATION CURVE FORWARD MODEL
# =============================================================================

def forward_velocity_1d(theta, r_kpc, Sigma_star, Sigma_gas=None, 
                        r0_kpc=0.1, G=4.302e-6):
    """
    Forward model for rotation velocity from EFC.
    
    The key insight: use SAME λ from cluster fits.
    
    v²(r) = r · dΦ/dr
    
    where Φ is computed from Yukawa-convolved surface density.
    
    Parameters
    ----------
    theta : array
        [logA, loglam] or [logA, logR, loglam] if gas included
        λ is in kpc (same physical units as r)
    r_kpc : 1D array
        Radial distances in kpc
    Sigma_star : 1D array
        Stellar surface density [M_sun/pc²]
    Sigma_gas : 1D array, optional
        Gas surface density [M_sun/pc²]
    r0_kpc : float
        Core regularization in kpc
    G : float
        Gravitational constant [kpc/M_sun * (km/s)²]
    
    Returns
    -------
    v_model : 1D array
        Circular velocity in km/s
    """
    if Sigma_gas is None:
        logA, loglam = theta
        R = np.inf
    else:
        logA, logR, loglam = theta
        R = np.exp(logR)
    
    A = np.exp(logA)
    lam = np.exp(loglam)  # in kpc
    
    # Build effective surface density with Yukawa weighting
    # This is a simplified 1D approximation
    # Full treatment would do 2D convolution on disk
    
    # For now: compute enclosed mass with Yukawa falloff
    dr = np.gradient(r_kpc)
    
    # Yukawa weight function
    def yukawa_weight(r, r_prime, lam, r0):
        dist = np.abs(r - r_prime)
        return np.exp(-dist / lam) / (dist + r0)
    
    # Effective enclosed "mass" at each radius
    v2 = np.zeros_like(r_kpc)
    
    for i, r in enumerate(r_kpc):
        if r < 1e-3:
            continue
        
        # Integrate weighted surface density
        weights = yukawa_weight(r, r_kpc, lam, r0_kpc)
        weights /= np.sum(weights * dr)
        
        # Effective surface density
        Sigma_eff = A * Sigma_star
        if Sigma_gas is not None:
            Sigma_eff += (A / R) * Sigma_gas
        
        # Weighted sum (simplified - proper treatment needs 2D integral)
        M_eff = np.sum(Sigma_eff * weights * 2 * np.pi * r_kpc * dr)
        
        # v² = G M_eff / r (simplified)
        v2[i] = G * M_eff / r
    
    return np.sqrt(np.maximum(v2, 0))


def forward_velocity_1d_proper(theta, r_kpc, Sigma_star, Sigma_gas=None,
                                r0_kpc=0.1, G=4.302e-6):
    """
    Proper 1D rotation curve from Yukawa potential.
    
    Φ(r) = -G ∫ Σ(r') K(|r-r'|) 2πr' dr'
    
    v²(r) = r · dΦ/dr
    
    This is the correct formulation for testing EFC on SPARC.
    """
    if Sigma_gas is None:
        logA, loglam = theta
        R = np.inf
    else:
        logA, logR, loglam = theta
        R = np.exp(logR)
    
    A = np.exp(logA)
    lam = np.exp(loglam)
    
    nr = len(r_kpc)
    dr = np.gradient(r_kpc)
    
    # Effective surface density
    Sigma_eff = A * Sigma_star * 1e6  # Convert M_sun/pc² to M_sun/kpc²
    if Sigma_gas is not None:
        Sigma_eff += (A / R) * Sigma_gas * 1e6
    
    # Compute potential at each r
    Phi = np.zeros(nr)
    
    for i in range(nr):
        r = r_kpc[i]
        
        # Yukawa kernel from all r' to this r
        for j in range(nr):
            r_prime = r_kpc[j]
            if r_prime < 1e-6:
                continue
            
            # Distance (for 1D axisymmetric, use |r - r'| approximation)
            # Proper treatment: elliptic integral for disk potential
            dist = np.sqrt(r**2 + r_prime**2)  # Simplified
            
            K = np.exp(-dist / lam) / (dist + r0_kpc)
            
            Phi[i] -= G * Sigma_eff[j] * K * 2 * np.pi * r_prime * dr[j]
    
    # v² = r · dΦ/dr
    dPhi_dr = np.gradient(Phi, r_kpc)
    v2 = r_kpc * np.abs(dPhi_dr)
    
    return np.sqrt(np.maximum(v2, 0))
