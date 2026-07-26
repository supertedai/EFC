"""
BAO (Baryon Acoustic Oscillation) Module

Loads BAO distance measurements and computes likelihood
against EFC Hubble parameter predictions.

Data sources:
    - BOSS DR12: D_M(z)/r_d and D_H(z)/r_d at z = 0.38, 0.51, 0.61
    - DESI 2024: D_H(z)/r_d and D_M(z)/r_d
    - 6dFGS, WiggleZ: D_V(z)/r_d

Supported formats:
    CSV (recommended):  z, observable, value, sigma
    JSON (legacy):      {"measurements": [...], "covariance": [...]}

Observable types:
    DH_over_rd  = c / (H(z) * r_d)
    DM_over_rd  = D_M(z) / r_d  (comoving distance integral)
    DV_over_rd  = [z * D_H(z) * D_M(z)^2]^(1/3) / r_d

Usage:
    engine = EFCHubble()
    module = BAOModule(engine)
    module.load_data(data_path="efc_inference/data/bao/bao_starter.csv")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
import json
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.hubble import EFCHubble

logger = logging.getLogger(__name__)

# Speed of light in km/s
C_KM_S = 299792.458

# Default sound horizon at drag epoch (Planck 2018)
DEFAULT_RD = 147.09  # Mpc


class BAOModule(BaseModule):
    """
    BAO distance measurement module.

    Supports both CSV and JSON data formats (auto-detected by extension).
    Computes D_H, D_M, and D_V distance measures from H(z).
    """

    def __init__(self, engine: Optional[EFCHubble] = None):
        if engine is None:
            engine = EFCHubble()
        super().__init__(engine)
        self._measurements = None
        self._covariance = None
        self._observables = None

    @property
    def name(self) -> str:
        return "bao"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load BAO measurements from CSV or JSON.

        Auto-detects format from file extension.

        CSV format: z, observable, value, sigma
        JSON format: {"measurements": [...], "covariance": [...]}

        Parameters:
            data_path:  Path to data file
            min_error:  Floor for errors (default 0.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"BAO data not found: {path}")

        if path.suffix == ".csv":
            self._load_csv(path, **kwargs)
        else:
            self._load_json(path, **kwargs)

        self._loaded = True
        logger.info(
            "Loaded BAO data: %d measurements, types=%s",
            len(self.coordinates), sorted(set(self._observables))
        )

    def _load_csv(self, path: Path, **kwargs):
        """Load BAO data from CSV with string observable column."""
        z_list = []
        obs_list = []
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
                obs_list.append(parts[1].strip())
                val_list.append(float(parts[2]))
                sig_list.append(float(parts[3]))

        if len(z_list) == 0:
            raise ValueError(f"No data rows found in {path}")

        self.coordinates = np.array(z_list)
        self.observed = np.array(val_list)
        self.errors = np.array(sig_list)
        self._observables = obs_list

        # Error floor
        min_error = kwargs.get("min_error", 0.0)
        if min_error > 0:
            self.errors = np.maximum(self.errors, min_error)

    def _load_json(self, path: Path, **kwargs):
        """Load BAO data from JSON (legacy format)."""
        with open(path) as f:
            data = json.load(f)

        measurements = data["measurements"]
        self._measurements = measurements
        self._observables = [m["observable"] for m in measurements]

        self.coordinates = np.array([m["z_eff"] for m in measurements])
        self.observed = np.array([m["value"] for m in measurements])
        self.errors = np.array([m["error"] for m in measurements])

        if "covariance" in data:
            self._covariance = np.array(data["covariance"])

        # Error floor
        min_error = kwargs.get("min_error", 0.0)
        if min_error > 0:
            self.errors = np.maximum(self.errors, min_error)

    def predict(self, params_dict: dict) -> np.ndarray:
        """
        Compute BAO distance predictions from H(z).

        Handles three observable types:
            DH_over_rd  = c / (H(z) * r_d)
            DM_over_rd  = comoving_distance(z) / r_d
            DV_over_rd  = [z * DH * DM^2]^(1/3) / r_d

        Uses np.trapezoid with 201-point grid for comoving distance.
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        r_d = params_dict.get("r_d", DEFAULT_RD)
        predictions = np.zeros(len(self.coordinates))

        for i, obs_type in enumerate(self._observables):
            z_i = self.coordinates[i]

            if obs_type == "DH_over_rd":
                Hz_i = self.engine.compute(params_dict,
                                           np.array([z_i]))[0]
                predictions[i] = C_KM_S / (Hz_i * r_d)

            elif obs_type == "DM_over_rd":
                DM_i = self._comoving_distance(params_dict, z_i)
                predictions[i] = DM_i / r_d

            elif obs_type == "DV_over_rd":
                Hz_i = self.engine.compute(params_dict,
                                           np.array([z_i]))[0]
                DH_i = C_KM_S / Hz_i
                DM_i = self._comoving_distance(params_dict, z_i)
                DV_i = (z_i * DH_i * DM_i**2) ** (1.0 / 3.0)
                predictions[i] = DV_i / r_d

            else:
                raise ValueError(f"Unknown BAO observable: {obs_type}")

        return predictions

    def _comoving_distance(self, params_dict: dict, z: float) -> float:
        """
        Compute comoving distance D_M(z) = int_0^z c/H(z') dz'.

        Uses trapezoidal integration with 201-point grid.
        Accuracy: ~0.01% for smooth H(z).

        Returns:
            D_M in Mpc
        """
        n_grid = 201
        z_grid = np.linspace(0.0, z, n_grid)
        Hz_grid = self.engine.compute(params_dict, z_grid)

        # c / H(z') integrand
        integrand = C_KM_S / Hz_grid

        # np.trapezoid (numpy >=2.0) / np.trapz (numpy <2.0)
        _trapz = getattr(np, 'trapezoid', None) or np.trapz
        return _trapz(integrand, z_grid)

    def log_likelihood(self, params_dict: dict) -> float:
        """Use covariance matrix if available, else chi2."""
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        pred = self.predict(params_dict)

        if np.any(~np.isfinite(pred)):
            return -np.inf

        if self._covariance is not None:
            from ..core.likelihoods import log_likelihood_covariance
            return log_likelihood_covariance(self.observed, pred,
                                             self._covariance)
        else:
            from ..core.likelihoods import log_likelihood_chi2
            return log_likelihood_chi2(self.observed, pred, self.errors)
