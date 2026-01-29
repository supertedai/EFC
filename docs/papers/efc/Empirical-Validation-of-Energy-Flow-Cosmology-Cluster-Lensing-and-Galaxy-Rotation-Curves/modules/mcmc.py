"""
EFC MCMC Inference Module
=========================
Bayesian parameter estimation for EFC models.
"""

import numpy as np
import time

try:
    import emcee
    HAS_EMCEE = True
except ImportError:
    HAS_EMCEE = False

from .kernels import make_kernel_yukawa
from .sources import Q_gal_density, Q_gas_grad_div
from .forward import fft_convolve

__all__ = ['PARAMS_CLUSTER', 'PARAMS_GALAXY', 'run_mcmc_cluster', 'run_mcmc_galaxy']


# =============================================================================
# DEFAULT PARAMETER CONFIGURATIONS
# =============================================================================

PARAMS_CLUSTER = {
    "names": ["logA", "logR", "loglam", "k0"],
    "ndim": 4,
    "kernel": {
        "kind": "yukawa",
        "r0_px": 2.0,
    },
    "Q_gas": {
        "kind": "grad_div",
        "eps": 1e-3,
    },
    "noise": {
        "sigma_kappa": 0.004,
    },
    "priors": {
        "logA":   (np.log(1e-6), np.log(50.0)),
        "logR":   (np.log(1.2),  np.log(1e6)),
        "loglam": (np.log(3.0),  np.log(300.0)),
        "k0":     (-0.10, 0.10),
    }
}

PARAMS_GALAXY = {
    "names": ["logA", "loglam"],
    "ndim": 2,
    "kernel": {
        "kind": "yukawa",
        "r0_kpc": 0.1,
    },
    "noise": {
        "sigma_v": 5.0,  # km/s typical uncertainty
    },
    "priors": {
        "logA":   (np.log(0.1), np.log(10.0)),
        "loglam": (np.log(0.5), np.log(50.0)),  # kpc
    }
}


# =============================================================================
# LIKELIHOOD FUNCTIONS
# =============================================================================

def log_prior_cluster(theta, priors):
    """Flat priors for cluster model."""
    logA, logR, loglam, k0 = theta
    if not (priors["logA"][0]   < logA   < priors["logA"][1]):   return -np.inf
    if not (priors["logR"][0]   < logR   < priors["logR"][1]):   return -np.inf
    if not (priors["loglam"][0] < loglam < priors["loglam"][1]): return -np.inf
    if not (priors["k0"][0]     < k0     < priors["k0"][1]):     return -np.inf
    return 0.0


def log_prior_galaxy(theta, priors):
    """Flat priors for galaxy model."""
    logA, loglam = theta
    if not (priors["logA"][0]   < logA   < priors["logA"][1]):   return -np.inf
    if not (priors["loglam"][0] < loglam < priors["loglam"][1]): return -np.inf
    return 0.0


def log_likelihood_cluster(theta, kappa_obs, Q_gal, Q_gas, sigma, kernel_cfg, mask=None):
    """Gaussian likelihood for κ field."""
    logA, logR, loglam, k0 = theta
    A = np.exp(logA)
    R = np.exp(logR)
    lam = np.exp(loglam)
    
    K = make_kernel_yukawa(Q_gal.shape, lam_px=lam, r0_px=kernel_cfg.get("r0_px", 2.0))
    
    k_model = A * fft_convolve(Q_gal, K) + (A / R) * fft_convolve(Q_gas, K) + k0
    
    resid = kappa_obs - k_model
    if mask is not None:
        resid = resid[mask]
    
    chi2 = np.sum(resid**2 / sigma**2)
    return -0.5 * chi2


def log_likelihood_galaxy(theta, v_obs, v_err, r_kpc, Sigma_star, Sigma_gas, 
                          forward_func, r0_kpc=0.1):
    """Gaussian likelihood for rotation curve."""
    try:
        v_model = forward_func(theta, r_kpc, Sigma_star, Sigma_gas, r0_kpc=r0_kpc)
        resid = v_obs - v_model
        chi2 = np.sum((resid / v_err)**2)
        return -0.5 * chi2
    except:
        return -np.inf


def log_posterior_cluster(theta, kappa_obs, Q_gal, Q_gas, cfg, mask=None):
    """Full posterior for cluster model."""
    lp = log_prior_cluster(theta, cfg["priors"])
    if not np.isfinite(lp):
        return -np.inf
    ll = log_likelihood_cluster(
        theta, kappa_obs, Q_gal, Q_gas,
        sigma=cfg["noise"]["sigma_kappa"],
        kernel_cfg=cfg["kernel"],
        mask=mask
    )
    return lp + ll


def log_posterior_galaxy(theta, v_obs, v_err, r_kpc, Sigma_star, Sigma_gas, 
                         forward_func, cfg):
    """Full posterior for galaxy model."""
    lp = log_prior_galaxy(theta, cfg["priors"])
    if not np.isfinite(lp):
        return -np.inf
    ll = log_likelihood_galaxy(
        theta, v_obs, v_err, r_kpc, Sigma_star, Sigma_gas,
        forward_func, r0_kpc=cfg["kernel"].get("r0_kpc", 0.1)
    )
    return lp + ll


# =============================================================================
# MCMC RUNNERS
# =============================================================================

def run_mcmc_cluster(kappa_obs, M_gal, S_proxy, cfg=None, mask=None,
                     nwalkers=64, nsteps=4000, burnin=1000, thin=10, seed=42):
    """
    Run MCMC for cluster lensing.
    
    Parameters
    ----------
    kappa_obs : 2D array
        Observed convergence map
    M_gal : 2D array
        Galaxy density map
    S_proxy : 2D array
        Entropy proxy (for Q_gas)
    cfg : dict, optional
        Configuration (uses PARAMS_CLUSTER if None)
    mask : 2D bool array, optional
        Pixel mask
    
    Returns
    -------
    dict with chain, best_theta, etc.
    """
    if not HAS_EMCEE:
        raise ImportError("emcee required: pip install emcee")
    
    if cfg is None:
        cfg = PARAMS_CLUSTER
    
    rng = np.random.default_rng(seed)
    
    # Prepare source terms
    Q_gal = Q_gal_density(M_gal)
    Q_gas = Q_gas_grad_div(S_proxy, eps=cfg["Q_gas"]["eps"])
    
    # Initial point
    theta0 = np.array([
        np.log(0.5),
        np.log(100.0),
        np.log(60.0),
        0.0
    ])
    
    ndim = cfg["ndim"]
    p0 = theta0 + 0.02 * rng.standard_normal(size=(nwalkers, ndim))
    
    # Ensure walkers in prior
    for i in range(nwalkers):
        tries = 0
        while not np.isfinite(log_prior_cluster(p0[i], cfg["priors"])):
            p0[i] = theta0 + 0.02 * rng.standard_normal(ndim)
            tries += 1
            if tries > 10000:
                raise RuntimeError("Cannot initialize walkers")
    
    # Run sampler
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, log_posterior_cluster,
        args=(kappa_obs, Q_gal, Q_gas, cfg, mask)
    )
    
    t0 = time.time()
    sampler.run_mcmc(p0, nsteps, progress=True)
    elapsed = time.time() - t0
    
    # Extract results
    chain = sampler.get_chain(discard=burnin, thin=thin, flat=True)
    logp = sampler.get_log_prob(discard=burnin, thin=thin, flat=True)
    best = chain[np.argmax(logp)]
    
    return {
        "chain": chain,
        "logp": logp,
        "best_theta": best,
        "param_names": cfg["names"],
        "acceptance": np.mean(sampler.acceptance_fraction),
        "elapsed_s": elapsed,
        "Q_gal": Q_gal,
        "Q_gas": Q_gas,
    }


def run_mcmc_galaxy(v_obs, v_err, r_kpc, Sigma_star, Sigma_gas, forward_func,
                    cfg=None, nwalkers=32, nsteps=2000, burnin=500, thin=5, seed=42):
    """
    Run MCMC for galaxy rotation curve.
    
    Parameters
    ----------
    v_obs : 1D array
        Observed rotation velocities [km/s]
    v_err : 1D array
        Velocity uncertainties [km/s]
    r_kpc : 1D array
        Radial distances [kpc]
    Sigma_star : 1D array
        Stellar surface density [M_sun/pc²]
    Sigma_gas : 1D array
        Gas surface density [M_sun/pc²]
    forward_func : callable
        Forward model function
    cfg : dict, optional
        Configuration (uses PARAMS_GALAXY if None)
    
    Returns
    -------
    dict with chain, best_theta, etc.
    """
    if not HAS_EMCEE:
        raise ImportError("emcee required: pip install emcee")
    
    if cfg is None:
        cfg = PARAMS_GALAXY
    
    rng = np.random.default_rng(seed)
    
    # Initial point
    theta0 = np.array([np.log(1.0), np.log(5.0)])  # A=1, λ=5 kpc
    
    ndim = cfg["ndim"]
    p0 = theta0 + 0.1 * rng.standard_normal(size=(nwalkers, ndim))
    
    # Ensure walkers in prior
    for i in range(nwalkers):
        tries = 0
        while not np.isfinite(log_prior_galaxy(p0[i], cfg["priors"])):
            p0[i] = theta0 + 0.1 * rng.standard_normal(ndim)
            tries += 1
            if tries > 10000:
                raise RuntimeError("Cannot initialize walkers")
    
    # Run sampler
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, log_posterior_galaxy,
        args=(v_obs, v_err, r_kpc, Sigma_star, Sigma_gas, forward_func, cfg)
    )
    
    t0 = time.time()
    sampler.run_mcmc(p0, nsteps, progress=True)
    elapsed = time.time() - t0
    
    chain = sampler.get_chain(discard=burnin, thin=thin, flat=True)
    logp = sampler.get_log_prob(discard=burnin, thin=thin, flat=True)
    best = chain[np.argmax(logp)]
    
    return {
        "chain": chain,
        "logp": logp,
        "best_theta": best,
        "param_names": cfg["names"],
        "acceptance": np.mean(sampler.acceptance_fraction),
        "elapsed_s": elapsed,
    }
