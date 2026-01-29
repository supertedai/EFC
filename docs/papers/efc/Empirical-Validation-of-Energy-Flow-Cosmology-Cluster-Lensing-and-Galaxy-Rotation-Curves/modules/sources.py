"""
EFC Sources Module
==================
Source terms Q(x) for different matter components.

In EFC, different matter types couple differently to the entropy gradient:
- Collisionless (galaxies, stars): strong coupling
- Dissipative (gas): weak coupling
"""

import numpy as np

__all__ = ['Q_gal_density', 'Q_gas_grad_div', 'Q_gas_grad_mag', 'Q_gas_laplacian_log']


def Q_gal_density(M_gal, normalize=True):
    """
    Galaxy source term: surface density.
    
    Q_gal = Σ_gal (normalized)
    
    For rotation curves: use stellar mass surface density Σ_*(r)
    For clusters: use galaxy number density or luminosity density
    """
    Q = M_gal.copy()
    if normalize:
        Q = Q / (np.max(np.abs(Q)) + 1e-12)
    return Q


def Q_gas_grad_div(S, eps=1e-3, normalize=True):
    """
    Gas source term: divergence of normalized entropy gradient.
    
    Q_gas = ∇·(∇S / (S+ε))
    
    This is structure-robust (not edge-sensitive like |∇S|).
    Captures compression/expansion of entropy field.
    
    Parameters
    ----------
    S : 2D array
        Entropy proxy (e.g., T * n_e^(-2/3) for ICM)
    eps : float
        Regularization to prevent division by zero
    normalize : bool
        If True, standardize output
    """
    Sy, Sx = np.gradient(S)
    Vx = Sx / (S + eps)
    Vy = Sy / (S + eps)
    Vy_y, _ = np.gradient(Vy)
    _, Vx_x = np.gradient(Vx)
    
    Q = Vx_x + Vy_y
    
    if normalize:
        Q = (Q - np.median(Q)) / (np.std(Q) + 1e-12)
    
    return Q


def Q_gas_grad_mag(S, normalize=True):
    """
    Gas source term: magnitude of entropy gradient.
    
    Q_gas = |∇S|
    
    Simpler but more edge-sensitive than grad_div.
    """
    Sy, Sx = np.gradient(S)
    Q = np.sqrt(Sx**2 + Sy**2)
    
    if normalize:
        Q = Q / (np.max(Q) + 1e-12)
    
    return Q


def Q_gas_laplacian_log(S, eps=1e-3, normalize=True):
    """
    Gas source term: Laplacian of log-entropy.
    
    Q_gas = ∇²(log(S+ε))
    
    Alternative that's less stripe-prone than grad_div.
    """
    logS = np.log(S + eps)
    
    # Laplacian via second derivatives
    d2y, _ = np.gradient(np.gradient(logS, axis=0), axis=0)
    _, d2x = np.gradient(np.gradient(logS, axis=1), axis=1)
    
    Q = d2x + d2y
    
    if normalize:
        Q = (Q - np.median(Q)) / (np.std(Q) + 1e-12)
    
    return Q


# =============================================================================
# 1D SOURCES (for rotation curves)
# =============================================================================

def Q_stellar_1d(Sigma_star, normalize=True):
    """
    Stellar source term for rotation curves.
    
    Q_*(r) = Σ_*(r)
    
    Parameters
    ----------
    Sigma_star : 1D array
        Stellar surface density profile [M_sun/pc²]
    """
    Q = Sigma_star.copy()
    if normalize:
        Q = Q / (np.max(np.abs(Q)) + 1e-12)
    return Q


def Q_gas_1d(Sigma_gas, normalize=True):
    """
    Gas source term for rotation curves.
    
    Q_gas(r) = Σ_gas(r)
    
    For SPARC: typically HI + He correction
    """
    Q = Sigma_gas.copy()
    if normalize:
        Q = Q / (np.max(np.abs(Q)) + 1e-12)
    return Q
