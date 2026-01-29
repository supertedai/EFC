"""
EFC Kernels Module
==================
Non-local coupling kernels for Energy-Flow Cosmology.

The kernel K(r) defines how entropy gradients couple to gravitational response.
"""

import numpy as np

__all__ = ['make_kernel_yukawa', 'make_kernel_power', 'make_kernel_gaussian']


def make_kernel_yukawa(shape, lam_px, r0_px=2.0):
    """
    Yukawa (screened) kernel: K(r) ∝ exp(-r/λ) / (r + r₀)
    
    Physical interpretation:
        - λ: non-local coupling range
        - r₀: core regularization (prevents singularity)
    
    Parameters
    ----------
    shape : tuple
        (ny, nx) grid dimensions
    lam_px : float
        Non-local range in pixels
    r0_px : float
        Core regularization in pixels
    
    Returns
    -------
    K : 2D array, FFT-shifted for convolution
    """
    ny, nx = shape
    y = np.arange(ny) - ny // 2
    x = np.arange(nx) - nx // 2
    yy, xx = np.meshgrid(y, x, indexing="ij")
    r = np.sqrt(xx**2 + yy**2)
    
    K = np.exp(-r / lam_px) / (r + r0_px)
    K /= K.sum()
    
    return np.fft.ifftshift(K)


def make_kernel_power(shape, p, r0_px=2.0, rcut_px=None):
    """
    Power-law kernel: K(r) ∝ 1 / (r² + r₀²)^(p/2)
    
    Optional exponential cutoff for finite range.
    
    Parameters
    ----------
    shape : tuple
        (ny, nx) grid dimensions
    p : float
        Power-law index (1-2 typical)
    r0_px : float
        Core regularization
    rcut_px : float, optional
        Exponential cutoff scale
    """
    ny, nx = shape
    y = np.arange(ny) - ny // 2
    x = np.arange(nx) - nx // 2
    yy, xx = np.meshgrid(y, x, indexing="ij")
    r = np.sqrt(xx**2 + yy**2)
    
    K = 1.0 / ((r**2 + r0_px**2)**(p/2))
    
    if rcut_px is not None:
        K *= np.exp(-r / rcut_px)
    
    K /= K.sum()
    return np.fft.ifftshift(K)


def make_kernel_gaussian(shape, sigma_px):
    """
    Gaussian kernel: K(r) ∝ exp(-r²/2σ²)
    
    Simple smoothing kernel for comparison.
    """
    ny, nx = shape
    y = np.arange(ny) - ny // 2
    x = np.arange(nx) - nx // 2
    yy, xx = np.meshgrid(y, x, indexing="ij")
    r2 = xx**2 + yy**2
    
    K = np.exp(-r2 / (2 * sigma_px**2))
    K /= K.sum()
    
    return np.fft.ifftshift(K)


def make_kernel_1d_yukawa(r_array, lam, r0=0.1):
    """
    1D Yukawa kernel for radial profiles (e.g., rotation curves).
    
    K(r) = exp(-r/λ) / (r + r₀)
    
    Parameters
    ----------
    r_array : 1D array
        Radial distances (same units as λ)
    lam : float
        Non-local range
    r0 : float
        Core regularization
    
    Returns
    -------
    K : 1D array, normalized
    """
    K = np.exp(-r_array / lam) / (r_array + r0)
    K /= np.trapz(K * r_array, r_array) * 2 * np.pi  # 2D normalization
    return K
