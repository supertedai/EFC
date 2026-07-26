"""
Prior distributions for EFC parameters.

All priors implement: log_prob(x), sample(rng).
"""

import numpy as np
from abc import ABC, abstractmethod


class Prior(ABC):
    @abstractmethod
    def log_prob(self, x: float) -> float:
        ...

    @abstractmethod
    def sample(self, rng: np.random.Generator) -> float:
        ...


class UniformPrior(Prior):
    """Flat prior between lo and hi."""

    def __init__(self, lo: float, hi: float):
        self.lo = lo
        self.hi = hi
        self._log_norm = -np.log(hi - lo)

    def log_prob(self, x: float) -> float:
        if self.lo <= x <= self.hi:
            return self._log_norm
        return -np.inf

    def sample(self, rng: np.random.Generator) -> float:
        return rng.uniform(self.lo, self.hi)


class GaussianPrior(Prior):
    """Gaussian (normal) prior with mean mu and std sigma."""

    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma
        self._log_norm = -0.5 * np.log(2 * np.pi * sigma**2)

    def log_prob(self, x: float) -> float:
        return self._log_norm - 0.5 * ((x - self.mu) / self.sigma) ** 2

    def sample(self, rng: np.random.Generator) -> float:
        return rng.normal(self.mu, self.sigma)


class LogUniformPrior(Prior):
    """Log-uniform (Jeffreys) prior: flat in log(x) between lo and hi.
    Both lo and hi must be positive."""

    def __init__(self, lo: float, hi: float):
        if lo <= 0 or hi <= 0:
            raise ValueError("LogUniformPrior requires positive bounds")
        self.lo = lo
        self.hi = hi
        self._log_norm = -np.log(np.log(hi / lo))

    def log_prob(self, x: float) -> float:
        if self.lo <= x <= self.hi:
            return self._log_norm - np.log(x)
        return -np.inf

    def sample(self, rng: np.random.Generator) -> float:
        log_lo = np.log(self.lo)
        log_hi = np.log(self.hi)
        return np.exp(rng.uniform(log_lo, log_hi))


class TruncatedGaussianPrior(Prior):
    """Gaussian prior truncated to [lo, hi]."""

    def __init__(self, mu: float, sigma: float, lo: float, hi: float):
        self.mu = mu
        self.sigma = sigma
        self.lo = lo
        self.hi = hi
        self._gauss_log_norm = -0.5 * np.log(2 * np.pi * sigma**2)

    def log_prob(self, x: float) -> float:
        if x < self.lo or x > self.hi:
            return -np.inf
        return self._gauss_log_norm - 0.5 * ((x - self.mu) / self.sigma) ** 2

    def sample(self, rng: np.random.Generator) -> float:
        for _ in range(10000):
            x = rng.normal(self.mu, self.sigma)
            if self.lo <= x <= self.hi:
                return x
        return rng.uniform(self.lo, self.hi)
