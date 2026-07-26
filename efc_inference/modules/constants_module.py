"""
Varying Constants Module — Null Hypothesis

Tests whether fundamental constants (mu, alpha_em) vary with redshift.
The null hypothesis: delta_X / X = 0 at all redshifts.

Data format (CSV):
    z, quantity, delta_over, sigma

Where:
    quantity:   "mu" (proton-to-electron mass ratio) or
                "alpha_em" (fine structure constant)
    delta_over: measured fractional change (delta_X / X)
    sigma:      measurement uncertainty

This module uses an internal NullEngine that always returns zeros.
Any non-zero measurement is evidence for varying constants.
In EFC, the alpha parameter could induce scale-dependent shifts.

Usage:
    module = ConstantsModule()
    module.load_data(data_path="efc_inference/data/constants/constraints_smoketest.csv")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.base_engine import EFCEngine

logger = logging.getLogger(__name__)


class _NullEngine(EFCEngine):
    """
    Null-hypothesis engine: returns zeros.

    The prediction for the null hypothesis is that fundamental
    constants do not vary (delta_X / X = 0).
    """

    REQUIRED_PARAMS = []

    @property
    def name(self) -> str:
        return "null_constants"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Return zeros — null hypothesis of no variation."""
        return np.zeros_like(coordinates, dtype=float)


class ConstantsModule(BaseModule):
    """
    Varying fundamental constants module (null hypothesis).

    Tests delta_mu/mu and delta_alpha_em/alpha_em against zero.
    Uses internal _NullEngine — no external engine needed.

    Attributes:
        quantities: list of quantity names per data point
    """

    def __init__(self, engine: Optional[EFCEngine] = None):
        if engine is None:
            engine = _NullEngine()
        super().__init__(engine)
        self.quantities = []

    @property
    def name(self) -> str:
        return "constants"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load varying constants constraints from CSV.

        CSV format: z, quantity, delta_over, sigma
        First row is header, comma-separated.
        quantity is a string column ("mu" or "alpha_em").

        Parameters:
            data_path:  Path to CSV file
            quantity:   Filter to specific quantity (optional)
            min_error:  Floor for errors (default 0.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"Constants data not found: {path}")

        # Manual parsing because of string column
        z_list = []
        qty_list = []
        val_list = []
        sig_list = []

        with open(path) as f:
            header = f.readline()  # skip header
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) < 4:
                    continue
                z_list.append(float(parts[0]))
                qty_list.append(parts[1].strip())
                val_list.append(float(parts[2]))
                sig_list.append(float(parts[3]))

        if len(z_list) == 0:
            raise ValueError(f"No data rows found in {path}")

        # Optional filter by quantity
        filter_qty = kwargs.get("quantity", None)
        if filter_qty is not None:
            mask = [q == filter_qty for q in qty_list]
            z_list = [z for z, m in zip(z_list, mask) if m]
            qty_list = [q for q, m in zip(qty_list, mask) if m]
            val_list = [v for v, m in zip(val_list, mask) if m]
            sig_list = [s for s, m in zip(sig_list, mask) if m]

            if len(z_list) == 0:
                raise ValueError(
                    f"No data for quantity='{filter_qty}' in {path}"
                )

        self.coordinates = np.array(z_list)
        self.observed = np.array(val_list)
        self.errors = np.array(sig_list)
        self.quantities = qty_list

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

        unique_qty = sorted(set(self.quantities))
        logger.info(
            "Loaded constants data: %d points, quantities=%s, z=[%.2f, %.2f]",
            len(self.coordinates), unique_qty,
            self.coordinates.min(), self.coordinates.max()
        )

    @staticmethod
    def available_quantities(data_path: str) -> list:
        """List unique quantities in a data file."""
        quantities = set()
        with open(data_path) as f:
            f.readline()  # skip header
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    quantities.add(parts[1].strip())
        return sorted(quantities)
