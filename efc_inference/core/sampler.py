"""
EFC MCMC Sampler

Wraps emcee EnsembleSampler with:
- EFCParameterVector for parameter management
- MetaController integration (L0-L3, EBE, RBC penalties)
- Module-based likelihood summation
- Convergence diagnostics
"""

import numpy as np
import logging
from typing import Optional

try:
    import emcee
except ImportError:
    emcee = None

from .parameters import EFCParameterVector
from .utils import gelman_rubin, effective_sample_size, summary_statistics

logger = logging.getLogger(__name__)


class MetaController:
    """
    Aggregates meta-layer penalties (L0-L3, EBE, RBC).
    Each meta-layer is a callable: meta_layer(params_dict) -> float (log penalty).
    """

    def __init__(self):
        self._layers: list[tuple[str, callable]] = []

    def add_layer(self, name: str, layer_fn: callable):
        self._layers.append((name, layer_fn))

    def log_penalty(self, params_dict: dict) -> float:
        total = 0.0
        for name, fn in self._layers:
            penalty = fn(params_dict)
            if not np.isfinite(penalty):
                return -np.inf
            total += penalty
        return total

    @property
    def layer_names(self) -> list[str]:
        return [name for name, _ in self._layers]


class EFCSampler:
    """
    Main inference sampler.

    Usage:
        sampler = EFCSampler(params, modules=[sparc_module], meta=meta_ctrl)
        sampler.run(n_walkers=32, n_steps=5000, burn_in=1000)
        results = sampler.results()
    """

    def __init__(self, params: EFCParameterVector,
                 modules: list,
                 meta: Optional[MetaController] = None,
                 n_walkers: int = 32):
        if emcee is None:
            raise ImportError("emcee is required: pip install emcee")

        self.params = params
        self.modules = modules
        self.meta = meta or MetaController()
        self.n_walkers = n_walkers
        self._sampler = None
        self._chain = None
        self._log_prob = None
        self._burn_in = 0

    def log_probability(self, theta: np.ndarray) -> float:
        """
        Full log-posterior:
          log P = log_prior + meta_penalty + sum(log_likelihood per module)
        """
        pv = self.params.from_array(theta)

        # Prior
        lp = pv.log_prior()
        if not np.isfinite(lp):
            return -np.inf

        # Bounds check
        if not pv.in_bounds():
            return -np.inf

        params_dict = pv.to_dict()

        # Meta penalties (L0-L3, EBE, RBC)
        meta_penalty = self.meta.log_penalty(params_dict)
        if not np.isfinite(meta_penalty):
            return -np.inf

        # Sum log-likelihoods from all modules
        total_ll = 0.0
        for module in self.modules:
            ll = module.log_likelihood(params_dict)
            if not np.isfinite(ll):
                return -np.inf
            total_ll += ll

        return lp + meta_penalty + total_ll

    def run(self, n_steps: int = 5000, burn_in: int = 1000,
            progress: bool = True, thin: int = 1):
        """Run MCMC sampling."""
        ndim = self.params.ndim
        if ndim == 0:
            raise ValueError("No free parameters to sample")

        logger.info(f"Starting MCMC: {self.n_walkers} walkers, "
                    f"{n_steps} steps, {ndim} parameters")

        # Initialize walkers around prior samples
        rng = np.random.default_rng(42)
        p0 = np.array([self.params.sample_prior(rng)
                        for _ in range(self.n_walkers)])

        # Create emcee sampler
        self._sampler = emcee.EnsembleSampler(
            self.n_walkers, ndim, self.log_probability
        )

        # Run
        self._sampler.run_mcmc(p0, n_steps, progress=progress, thin_by=thin)

        self._chain = self._sampler.get_chain()  # (n_steps, n_walkers, ndim)
        self._log_prob = self._sampler.get_log_prob()  # (n_steps, n_walkers)
        self._burn_in = burn_in

        logger.info(f"MCMC complete. Acceptance: "
                    f"{np.mean(self._sampler.acceptance_fraction):.3f}")

    @property
    def flat_chain(self) -> np.ndarray:
        """Flattened chain after burn-in: (n_samples, ndim)."""
        if self._chain is None:
            raise RuntimeError("Run sampler first")
        return self._chain[self._burn_in:].reshape(-1, self.params.ndim)

    @property
    def flat_log_prob(self) -> np.ndarray:
        """Flattened log-prob after burn-in."""
        if self._log_prob is None:
            raise RuntimeError("Run sampler first")
        return self._log_prob[self._burn_in:].flatten()

    @property
    def best_fit(self) -> dict:
        """Parameter values at maximum log-posterior."""
        flat_lp = self.flat_log_prob
        best_idx = np.argmax(flat_lp)
        best_theta = self.flat_chain[best_idx]
        pv = self.params.from_array(best_theta)
        result = pv.to_dict()
        result["_log_posterior"] = float(flat_lp[best_idx])
        return result

    def convergence(self) -> dict:
        """Convergence diagnostics."""
        if self._chain is None:
            raise RuntimeError("Run sampler first")

        # Reshape to (n_walkers, n_steps_post_burnin, ndim)
        post_burn = self._chain[self._burn_in:]  # (n_steps, n_walkers, ndim)
        chains_by_walker = post_burn.transpose(1, 0, 2)  # (n_walkers, n_steps, ndim)

        r_hat = gelman_rubin(chains_by_walker)
        ess = effective_sample_size(chains_by_walker)

        return {
            "r_hat": {name: float(r) for name, r in
                      zip(self.params.free_names, r_hat)},
            "ess": {name: float(e) for name, e in
                    zip(self.params.free_names, ess)},
            "acceptance_fraction": float(np.mean(
                self._sampler.acceptance_fraction)),
            "converged": bool(np.all(r_hat < 1.1)),
        }

    def results(self) -> dict:
        """Full results summary."""
        stats = summary_statistics(self.flat_chain, self.params.free_names)
        conv = self.convergence()

        return {
            "best_fit": self.best_fit,
            "posterior_summary": stats,
            "convergence": conv,
            "n_walkers": self.n_walkers,
            "n_samples": len(self.flat_chain),
            "modules": [m.name for m in self.modules],
            "meta_layers": self.meta.layer_names,
        }
