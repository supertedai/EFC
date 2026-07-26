"""
EFC Parameter Vector

Manages a named set of parameters with bounds, priors, and array conversion.
Each parameter has: name, value, bounds (lo, hi), prior specification.

Usage:
    pv = EFCParameterVector()
    pv.add("S0", 1e-24, bounds=(1e-26, 1e-22), prior=LogUniformPrior(1e-26, 1e-22))
    pv.add("Ls", 8.0, bounds=(1.0, 50.0), prior=GaussianPrior(8.0, 3.0))

    arr = pv.to_array()          # np.array for emcee
    pv2 = pv.from_array(arr)     # reconstruct from sampler output
    lp = pv.log_prior()          # sum of log-priors
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from .priors import Prior, UniformPrior


@dataclass
class Parameter:
    name: str
    value: float
    bounds: tuple  # (lo, hi)
    prior: Prior
    fixed: bool = False


class EFCParameterVector:
    """Ordered collection of named parameters with prior support."""

    def __init__(self):
        self._params: list[Parameter] = []
        self._index: dict[str, int] = {}

    def add(self, name: str, value: float, bounds: tuple,
            prior: Optional[Prior] = None, fixed: bool = False):
        if name in self._index:
            raise ValueError(f"Parameter '{name}' already exists")
        if prior is None:
            prior = UniformPrior(bounds[0], bounds[1])
        p = Parameter(name=name, value=value, bounds=bounds,
                      prior=prior, fixed=fixed)
        self._index[name] = len(self._params)
        self._params.append(p)

    @property
    def free_params(self) -> list[Parameter]:
        return [p for p in self._params if not p.fixed]

    @property
    def all_params(self) -> list[Parameter]:
        return list(self._params)

    @property
    def names(self) -> list[str]:
        return [p.name for p in self._params]

    @property
    def free_names(self) -> list[str]:
        return [p.name for p in self.free_params]

    @property
    def ndim(self) -> int:
        return len(self.free_params)

    @property
    def bounds_array(self) -> np.ndarray:
        return np.array([p.bounds for p in self.free_params])

    def __getitem__(self, name: str) -> float:
        return self._params[self._index[name]].value

    def __setitem__(self, name: str, value: float):
        self._params[self._index[name]].value = value

    def to_array(self) -> np.ndarray:
        return np.array([p.value for p in self.free_params])

    def from_array(self, arr: np.ndarray) -> "EFCParameterVector":
        """Return a copy with free parameters set from array."""
        pv = EFCParameterVector()
        free_idx = 0
        for p in self._params:
            if p.fixed:
                pv.add(p.name, p.value, p.bounds, p.prior, fixed=True)
            else:
                pv.add(p.name, float(arr[free_idx]), p.bounds, p.prior, fixed=False)
                free_idx += 1
        return pv

    def update_from_array(self, arr: np.ndarray):
        """Update free parameter values in-place from array."""
        free_idx = 0
        for p in self._params:
            if not p.fixed:
                p.value = float(arr[free_idx])
                free_idx += 1

    def log_prior(self) -> float:
        """Sum of log-priors for all free parameters."""
        lp = 0.0
        for p in self.free_params:
            val = p.prior.log_prob(p.value)
            if not np.isfinite(val):
                return -np.inf
            lp += val
        return lp

    def sample_prior(self, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """Draw one sample from the joint prior (free params only)."""
        if rng is None:
            rng = np.random.default_rng()
        return np.array([p.prior.sample(rng) for p in self.free_params])

    def in_bounds(self, arr: Optional[np.ndarray] = None) -> bool:
        """Check if all free parameters are within bounds."""
        if arr is not None:
            self.update_from_array(arr)
        for p in self.free_params:
            lo, hi = p.bounds
            if p.value < lo or p.value > hi:
                return False
        return True

    def to_dict(self) -> dict:
        """All parameters as {name: value} dict."""
        return {p.name: p.value for p in self._params}

    def __repr__(self) -> str:
        lines = [f"EFCParameterVector(ndim={self.ndim}):"]
        for p in self._params:
            flag = " [FIXED]" if p.fixed else ""
            lines.append(f"  {p.name} = {p.value:.6g}  {p.bounds}{flag}")
        return "\n".join(lines)
