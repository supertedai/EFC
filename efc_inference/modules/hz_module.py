"""
H(z) Cosmic Chronometer Module

Loads direct H(z) measurements from cosmic chronometers
and computes likelihood against EFC Hubble predictions.

Data format (CSV):
    z, Hz_km_s_Mpc, sigma

Data sources:
    - Moresco et al. (2016): differential age method
    - Various CC compilations (e.g. Farooq & Ratra 2017)

Usage:
    engine = EFCHubble()
    module = HzModule(engine)
    module.load_data(data_path="efc_inference/data/hubble/hz_starter.csv")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.hubble import EFCHubble

logger = logging.getLogger(__name__)


class HzModule(BaseModule):
    """
    H(z) cosmic chronometer module.

    Directly compares measured H(z) values against engine predictions.
    No distance integration needed — the simplest cosmological probe.
    """

    def __init__(self, engine: Optional[EFCHubble] = None):
        if engine is None:
            engine = EFCHubble()
        super().__init__(engine)

    @property
    def name(self) -> str:
        return "hz"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load H(z) data from CSV.

        CSV format: z, Hz_km_s_Mpc, sigma
        First row is header, comma-separated.

        Parameters:
            data_path: Path to CSV file
            min_error: Floor for errors (default 0.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"H(z) data not found: {path}")

        # Load numeric CSV: z, Hz, sigma
        raw = np.loadtxt(str(path), delimiter=",", skiprows=1)

        if raw.ndim == 1:
            raw = raw.reshape(1, -1)

        if raw.shape[1] < 3:
            raise ValueError(
                f"Expected 3 columns (z, Hz, sigma), got {raw.shape[1]}"
            )

        self.coordinates = raw[:, 0]  # redshifts
        self.observed = raw[:, 1]     # H(z) in km/s/Mpc
        self.errors = raw[:, 2]       # sigma

        # Validate
        if np.any(self.coordinates < 0):
            raise ValueError("Redshifts must be non-negative")
        if np.any(self.errors <= 0):
            raise ValueError("Errors must be positive")

        # Error floor
        min_error = kwargs.get("min_error", 0.0)
        if min_error > 0:
            self.errors = np.maximum(self.errors, min_error)

        self._loaded = True
        logger.info(
            "Loaded H(z) data: %d points, z=[%.2f, %.2f]",
            len(self.coordinates), self.coordinates.min(),
            self.coordinates.max()
        )

    # predict() inherited from BaseModule — calls engine.compute(params, z)
    # log_likelihood() inherited — chi2 with diagonal errors
    # residuals() inherited
