"""
Abstract base class for EFC observation modules.

A module owns:
  - Data (observed values, errors, coordinates)
  - An engine reference (for computing predictions)
  - log_likelihood computation
  - Prediction and residual methods

Module files contain ONLY data handling — never physics equations.
Physics lives in engine/ files.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Optional

from ..engine.base_engine import EFCEngine


class BaseModule(ABC):
    """
    Base class for all EFC observation modules.

    Subclasses must implement:
        - load_data() -> populate self.observed, self.errors, self.coordinates
        - name property

    The engine is injected at construction time.
    """

    def __init__(self, engine: EFCEngine):
        self.engine = engine
        self.observed: Optional[np.ndarray] = None
        self.errors: Optional[np.ndarray] = None
        self.coordinates: Optional[np.ndarray] = None
        self._loaded = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Module identifier (e.g. 'sparc', 'bao')."""
        ...

    @abstractmethod
    def load_data(self, **kwargs):
        """
        Load observational data.
        Must populate: self.observed, self.errors, self.coordinates
        """
        ...

    def predict(self, params_dict: dict) -> np.ndarray:
        """Compute model predictions at data coordinates."""
        if not self._loaded:
            raise RuntimeError(f"Module '{self.name}': call load_data() first")
        return self.engine.compute(params_dict, self.coordinates)

    def residuals(self, params_dict: dict) -> np.ndarray:
        """Normalized residuals: (obs - pred) / err."""
        pred = self.predict(params_dict)
        return (self.observed - pred) / self.errors

    def log_likelihood(self, params_dict: dict) -> float:
        """
        Chi-squared log-likelihood.
        Override for full covariance or other likelihood forms.
        """
        if not self._loaded:
            raise RuntimeError(f"Module '{self.name}': call load_data() first")

        pred = self.predict(params_dict)

        if np.any(~np.isfinite(pred)):
            return -np.inf

        from ..core.likelihoods import log_likelihood_chi2
        return log_likelihood_chi2(self.observed, pred, self.errors)

    # EFC MCMC parameter mapping: theta = [Om, H0, s8, alpha]
    # Must match the order in research_mcmc.py _log_prob_baseline_efc()
    EFC_PARAM_NAMES = ["Omega_m", "H0", "sigma8", "alpha_cosmo"]
    EFC_FIXED_PARAMS = {"r_d": 147.09}  # rd fixed in current inference

    def _params_from_array(self, arr: np.ndarray) -> dict:
        """Convert flat MCMC sample [Om, H0, s8, alpha] to params dict.

        Maps the 4-element array from the EFC posterior chain to the
        named parameter dict expected by engine.compute().
        """
        params = {name: float(arr[i])
                  for i, name in enumerate(self.EFC_PARAM_NAMES)
                  if i < len(arr)}
        params.update(self.EFC_FIXED_PARAMS)
        return params

    @property
    def n_data(self) -> int:
        if self.observed is None:
            return 0
        return len(self.observed)

    def summary(self) -> dict:
        return {
            "name": self.name,
            "engine": self.engine.name,
            "n_data": self.n_data,
            "loaded": self._loaded,
        }
