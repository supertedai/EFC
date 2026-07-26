"""
Growth Rate (fσ8) Module — MVP-G1

Loads f*sigma8(z) measurements from Redshift Space Distortion (RSD)
surveys and computes likelihood against EFC growth predictions.

Data format (CSV):
    z, fs8, sigma

Data sources:
    - 6dFGS (Beutler et al. 2012)
    - BOSS DR12 (Alam et al. 2017)
    - VIPERS (Pezzotta et al. 2017)
    - Various RSD compilations

Parameters:
    Omega_m, H0, sigma8, alpha_cosmo  (4 params)
    Same alpha_cosmo as BAO/Hz/SN — not a separate alpha_growth.

Usage:
    engine = EFCGrowth()
    module = GrowthModule(engine)
    module.load_data(data_path="efc_inference/data/growth/fs8_extended.csv")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.growth import EFCGrowth

logger = logging.getLogger(__name__)


class GrowthModule(BaseModule):
    """
    f*sigma8(z) RSD growth rate module.

    Directly compares measured fσ8(z) against engine predictions.
    Uses the same alpha_cosmo parameter as background probes (BAO, Hz, SN).
    """

    def __init__(self, engine: Optional[EFCGrowth] = None):
        if engine is None:
            engine = EFCGrowth()
        super().__init__(engine)

    @property
    def name(self) -> str:
        return "growth"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load fσ8 data from CSV.

        CSV format: z, fs8, sigma
        First row is header, comma-separated.

        Parameters:
            data_path: Path to CSV file
            min_error: Floor for errors (default 0.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"fσ8 data not found: {path}")

        raw = np.loadtxt(str(path), delimiter=",", skiprows=1)

        if raw.ndim == 1:
            raw = raw.reshape(1, -1)

        if raw.shape[1] < 3:
            raise ValueError(
                f"Expected 3 columns (z, fs8, sigma), got {raw.shape[1]}"
            )

        self.coordinates = raw[:, 0]  # redshifts
        self.observed = raw[:, 1]     # fσ8
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
            "Loaded fσ8 data: %d points, z=[%.2f, %.2f]",
            len(self.coordinates), self.coordinates.min(),
            self.coordinates.max()
        )

    # predict() inherited from BaseModule — calls engine.compute(params, z)
    # log_likelihood() inherited — chi2 with diagonal errors
    # residuals() inherited
