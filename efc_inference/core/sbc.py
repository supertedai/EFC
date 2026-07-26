"""
Simulation-Based Calibration (SBC) for EFC inference.

SBC validates that the sampler is well-calibrated by:
1. Drawing true parameters from the prior
2. Simulating synthetic data from those parameters
3. Running inference on synthetic data
4. Checking that true parameters fall within posterior at expected rates

Reference: Talts et al. (2018) "Validating Bayesian Inference Algorithms
with Simulation-Based Calibration"
"""

import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SBCResult:
    """Result from an SBC run."""
    n_simulations: int
    rank_statistics: np.ndarray    # (n_simulations, n_params)
    param_names: list              # ['Om', 'H0', 's8', 'alpha']
    ks_p_values: np.ndarray        # (n_params,) KS test p-values
    coverage_68: np.ndarray        # (n_params,) fraction where true falls in 68% CI
    coverage_95: np.ndarray        # (n_params,) fraction where true falls in 95% CI
    passed: bool
    verdict: str                   # "PASS" | "MARGINAL" | "FAIL"
    details: dict


def compute_rank(true_value: float, posterior_samples: np.ndarray) -> int:
    """Compute rank statistic: how many posterior samples < true value."""
    return int(np.sum(posterior_samples < true_value))


def ks_uniformity_test(ranks: np.ndarray, n_posterior: int) -> float:
    """Kolmogorov-Smirnov test for uniformity of rank statistics.

    Under correct calibration, rank / (n_posterior + 1) should be Uniform(0, 1).
    Returns p-value (>0.05 = plausible uniformity).
    """
    from scipy import stats
    # Normalize ranks to [0, 1]
    normalized = ranks / (n_posterior + 1)
    ks_stat, p_value = stats.kstest(normalized, 'uniform')
    return float(p_value)


def run_sbc(
    simulate_fn: Callable,
    infer_fn: Callable,
    prior_sampler: Callable,
    n_simulations: int = 100,
    param_names: Optional[list] = None,
    seed: int = 42,
) -> SBCResult:
    """Run Simulation-Based Calibration.

    Args:
        simulate_fn: (theta) -> synthetic_data
            Given true parameters, generate synthetic observed data.
        infer_fn: (synthetic_data) -> posterior_samples
            Given data, run sampler and return posterior chain (n_samples, n_params).
        prior_sampler: (rng) -> theta_true
            Sample one parameter vector from the prior.
        n_simulations: Number of SBC iterations.
        param_names: Names of parameters.
        seed: Random seed.

    Returns:
        SBCResult with rank statistics and calibration diagnostics.
    """
    if param_names is None:
        param_names = ["Om", "H0", "s8", "alpha"]

    n_params = len(param_names)
    rng = np.random.RandomState(seed)

    all_ranks = np.zeros((n_simulations, n_params), dtype=int)
    coverage_68 = np.zeros(n_params)
    coverage_95 = np.zeros(n_params)
    n_posterior = 0

    for i in range(n_simulations):
        if (i + 1) % 10 == 0 or i == 0:
            logger.info(f"  SBC simulation {i + 1}/{n_simulations}")

        # 1. Draw true parameters from prior
        theta_true = prior_sampler(rng)

        # 2. Simulate data
        try:
            synthetic_data = simulate_fn(theta_true)
        except Exception as e:
            logger.warning(f"  SBC sim {i}: simulate failed: {e}")
            continue

        # 3. Run inference
        try:
            posterior = infer_fn(synthetic_data)  # (n_samples, n_params)
        except Exception as e:
            logger.warning(f"  SBC sim {i}: inference failed: {e}")
            continue

        if posterior is None or len(posterior) == 0:
            logger.warning(f"  SBC sim {i}: empty posterior")
            continue

        n_posterior = posterior.shape[0]

        # 4. Compute rank statistics
        for j in range(n_params):
            all_ranks[i, j] = compute_rank(theta_true[j], posterior[:, j])

            # Coverage check
            lo_68 = np.percentile(posterior[:, j], 16)
            hi_68 = np.percentile(posterior[:, j], 84)
            lo_95 = np.percentile(posterior[:, j], 2.5)
            hi_95 = np.percentile(posterior[:, j], 97.5)

            if lo_68 <= theta_true[j] <= hi_68:
                coverage_68[j] += 1
            if lo_95 <= theta_true[j] <= hi_95:
                coverage_95[j] += 1

    coverage_68 /= n_simulations
    coverage_95 /= n_simulations

    # KS test for uniformity per parameter
    ks_p_values = np.zeros(n_params)
    for j in range(n_params):
        ks_p_values[j] = ks_uniformity_test(all_ranks[:, j], n_posterior)

    # Verdict
    ks_pass = np.all(ks_p_values > 0.05)
    cov_68_ok = np.all(np.abs(coverage_68 - 0.6827) < 0.15)
    cov_95_ok = np.all(np.abs(coverage_95 - 0.9545) < 0.10)

    if ks_pass and cov_68_ok and cov_95_ok:
        verdict = "PASS"
        passed = True
    elif ks_pass or (cov_68_ok and cov_95_ok):
        verdict = "MARGINAL"
        passed = False
    else:
        verdict = "FAIL"
        passed = False

    logger.info(f"  SBC verdict: {verdict}")
    for j, name in enumerate(param_names):
        logger.info(f"    {name}: KS p={ks_p_values[j]:.3f}, "
                    f"cov68={coverage_68[j]:.2f}, cov95={coverage_95[j]:.2f}")

    return SBCResult(
        n_simulations=n_simulations,
        rank_statistics=all_ranks,
        param_names=param_names,
        ks_p_values=ks_p_values,
        coverage_68=coverage_68,
        coverage_95=coverage_95,
        passed=passed,
        verdict=verdict,
        details={
            "ks_pass": bool(ks_pass),
            "cov_68_ok": bool(cov_68_ok),
            "cov_95_ok": bool(cov_95_ok),
            "n_posterior_per_sim": n_posterior,
        },
    )


def sbc_for_emcee(
    modules: dict,
    log_prob_fn: Callable,
    n_simulations: int = 50,
    nwalkers: int = 24,
    nsteps: int = 1500,
    burnin: int = 500,
    seed: int = 42,
) -> SBCResult:
    """Run SBC using emcee sampler on the EFC module system.

    This is the concrete implementation for the emcee-based research daemon.
    Generates synthetic data from modules, then runs emcee to check calibration.

    Args:
        modules: dict of loaded observation modules (bao, growth, hz, snia)
        log_prob_fn: emcee log_prob function for 4-param EFC
        n_simulations: number of SBC iterations (reduced for speed)
        nwalkers: emcee walkers (reduced for SBC)
        nsteps: emcee steps per simulation (reduced for SBC)
        burnin: burnin steps
        seed: random seed
    """
    import emcee

    param_names = ["Om", "H0", "s8", "alpha"]
    rd_fixed = 147.09

    def prior_sampler(rng):
        """Sample from EFC prior: Om~U(0.1,0.6), H0~U(50,85), s8~N(0.81,0.02), alpha~N(0,3)."""
        return np.array([
            rng.uniform(0.2, 0.4),      # Om (narrower for SBC)
            rng.uniform(60, 75),         # H0
            rng.normal(0.81, 0.02),      # s8
            rng.normal(0.0, 2.0),        # alpha (narrower for SBC)
        ])

    def simulate(theta):
        """Generate synthetic data from true parameters."""
        Om, H0, s8, alpha = theta
        params = {"Omega_m": Om, "H0": H0, "sigma8": s8,
                  "alpha_cosmo": alpha, "r_d": rd_fixed}

        # For each module, compute predictions + add noise
        synthetic = {}
        for name, mod in modules.items():
            if mod is None:
                continue
            pred = mod.predict(params)
            errors = mod.errors
            cov = getattr(mod, "_covariance", None)

            if cov is not None:
                # Draw from multivariate normal
                L = np.linalg.cholesky(cov)
                noise = L @ np.random.randn(len(pred))
            else:
                noise = errors * np.random.randn(len(pred))

            synthetic[name] = pred + noise
        return synthetic

    def infer(synthetic_data):
        """Run emcee on synthetic data and return posterior chain."""
        # Temporarily replace observed data in modules
        original_obs = {}
        for name, mod in modules.items():
            if mod is None or name not in synthetic_data:
                continue
            original_obs[name] = mod.observed.copy()
            mod._observed = synthetic_data[name]

        try:
            rng_init = np.random.RandomState(seed)
            p0 = np.column_stack([
                rng_init.uniform(0.2, 0.35, nwalkers),
                rng_init.uniform(65, 72, nwalkers),
                rng_init.normal(0.81, 0.03, nwalkers),
                rng_init.uniform(-3, 1, nwalkers),
            ])

            sampler = emcee.EnsembleSampler(
                nwalkers, 4, log_prob_fn, args=(modules,))
            sampler.run_mcmc(p0, nsteps, progress=False)
            chain = sampler.get_chain(discard=burnin, flat=True)
            return chain  # (n_samples, 4)
        finally:
            # Restore original observed data
            for name, obs in original_obs.items():
                if modules.get(name) is not None:
                    modules[name]._observed = obs

    return run_sbc(
        simulate_fn=simulate,
        infer_fn=infer,
        prior_sampler=prior_sampler,
        n_simulations=n_simulations,
        param_names=param_names,
        seed=seed,
    )


def sbc_verdict_to_dict(result: SBCResult) -> dict:
    """Convert SBCResult to JSON-serializable dict for Neo4j storage."""
    return {
        "sbc_verdict": result.verdict,
        "sbc_passed": result.passed,
        "sbc_n_simulations": result.n_simulations,
        "sbc_ks_p_values": {
            name: float(p) for name, p in zip(result.param_names, result.ks_p_values)
        },
        "sbc_coverage_68": {
            name: float(c) for name, c in zip(result.param_names, result.coverage_68)
        },
        "sbc_coverage_95": {
            name: float(c) for name, c in zip(result.param_names, result.coverage_95)
        },
        "sbc_details": result.details,
    }
