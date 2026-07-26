"""
Weak-Lensing Shear Module — KiDS-1000 Σ(k,z) Implementation

Loads the EFC lensing response function Σ(k,z) from KiDS-1000 re-analysis
and computes likelihood against engine predictions.

In EFC: the lensing signal is modified by the entropy gradient
through an effective lensing response Σ(k,z):
    P_eff(k,z) = Σ(k,z)² × P_ΛCDM(k,z)

The parametric form is:
    Σ(k,z) = 1 + α × sigmoid((k - k_trans)/δk) × max(0, 1 - z/z_activ)

where:
    α       = lensing response amplitude
    k_trans = transition wavenumber (h/Mpc)
    z_activ = activation redshift
    δk      = transition width (h/Mpc)

Data source:
    KiDS-1000 re-analysis (Asgari et al. 2021 + EFC Σ-correction)
    kids1000_results.json — Σ(k,z) 2D grid, S₈ tension analysis

Key results:
    Δχ² = -50.9 (770 data points, 3 extra parameters)
    S₈ tension: 2.6σ → 0.3σ after Σ-correction

Usage:
    engine = EFCLensing()  # or a Σ-capable engine
    module = ShearModule(engine)
    module.load_data(data_path="efc_inference/data/lensing/kids1000_results.json")
    ll = module.log_likelihood(params_dict)
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.lensing import EFCLensing

logger = logging.getLogger(__name__)


# ── LCDM Fallback: Parametric Σ(k,z) engine ──────────────────────
# Used when EFCLensing.compute() is a stub (NotImplementedError).
# Implements: Σ(k,z) = 1 + α × sigmoid((k - k_trans)/δk) × clamp(1 - z/z_activ)

_EFC_PHYSICS_READY = False  # Morten: set True when EFCLensing is real


class _LensingResponseEngine:
    """
    Parametric Σ(k,z) model as LCDM+EFC fallback.

    Parameters in params_dict:
        alpha_lens   (float): response amplitude (default 0.10)
        k_trans      (float): transition wavenumber h/Mpc (default 0.10)
        z_activ      (float): activation redshift (default 0.50)
        delta_k      (float): transition width h/Mpc (default 0.05)
    """

    DEFAULT_PARAMS = {
        "alpha_lens": 0.10,
        "k_trans": 0.10,
        "z_activ": 0.50,
        "delta_k": 0.05,
    }

    @staticmethod
    def compute_sigma(params_dict: dict,
                      k_array: np.ndarray,
                      z_array: np.ndarray) -> np.ndarray:
        """
        Compute Σ(k, z) for paired (k, z) arrays.

        Parameters:
            params_dict: EFC parameters
            k_array:  (N,) wavenumbers in h/Mpc
            z_array:  (N,) redshifts (same length as k_array)

        Returns:
            (N,) Σ values
        """
        alpha = params_dict.get("alpha_lens",
                                _LensingResponseEngine.DEFAULT_PARAMS["alpha_lens"])
        k_trans = params_dict.get("k_trans",
                                  _LensingResponseEngine.DEFAULT_PARAMS["k_trans"])
        z_activ = params_dict.get("z_activ",
                                  _LensingResponseEngine.DEFAULT_PARAMS["z_activ"])
        delta_k = params_dict.get("delta_k",
                                  _LensingResponseEngine.DEFAULT_PARAMS["delta_k"])

        # Sigmoid transition in k
        if delta_k > 0:
            sigmoid_k = 1.0 / (1.0 + np.exp(-(k_array - k_trans) / delta_k))
        else:
            sigmoid_k = np.where(k_array >= k_trans, 1.0, 0.0)

        # Redshift activation: strongest at z=0, vanishes at z >= z_activ
        if z_activ > 0:
            z_factor = np.clip(1.0 - z_array / z_activ, 0.0, 1.0)
        else:
            z_factor = np.ones_like(z_array)

        sigma = 1.0 + alpha * sigmoid_k * z_factor
        return sigma


class ShearModule(BaseModule):
    """
    Weak-lensing cosmic shear module with KiDS-1000 Σ(k,z) data.

    Loads the 2D Σ grid from kids1000_results.json and evaluates
    the EFC lensing response against predictions.
    """

    def __init__(self, engine: Optional[EFCLensing] = None):
        if engine is None:
            engine = EFCLensing()
        super().__init__(engine)

        # Additional data from JSON
        self._fit_results = None
        self._likelihood_analysis = None
        self._s8_analysis = None
        self._tomographic = None
        self._sigma_data = None

    @property
    def name(self) -> str:
        return "shear"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load KiDS-1000 Σ(k,z) data from JSON.

        Extracts the 2D Σ grid and flattens to (k,z) pairs for
        likelihood evaluation.

        Parameters:
            data_path:  Path to kids1000_results.json
            relative_error:  Systematic uncertainty on Σ (default 0.02 = 2%)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"KiDS-1000 data not found: {path}")

        with open(path) as f:
            data = json.load(f)

        # Store full results
        self._fit_results = data.get("fit_results", {})
        self._likelihood_analysis = data.get("likelihood_analysis", {})
        self._s8_analysis = data.get("s8_tension_analysis", {})
        self._tomographic = data.get("tomographic_fingerprint", {})
        self._sigma_data = data.get("sigma_values", {})

        # Extract 2D grid
        grid = self._sigma_data.get("2d_grid", {})
        k_values = grid.get("k_values_h_per_Mpc", [])
        z_values = grid.get("z_values", [])
        sigma_matrix = grid.get("sigma_matrix", [])

        if not k_values or not z_values or not sigma_matrix:
            raise ValueError(
                "Missing 2D grid data in KiDS-1000 JSON. "
                "Expected: sigma_values.2d_grid with k_values, z_values, sigma_matrix"
            )

        n_k = len(k_values)
        n_z = len(z_values)

        if len(sigma_matrix) != n_k:
            raise ValueError(
                f"sigma_matrix has {len(sigma_matrix)} rows, expected {n_k} (n_k)"
            )

        # Flatten 2D grid to paired arrays
        k_flat = []
        z_flat = []
        sigma_flat = []

        for i, k_val in enumerate(k_values):
            row = sigma_matrix[i]
            if len(row) != n_z:
                raise ValueError(
                    f"sigma_matrix row {i} has {len(row)} columns, expected {n_z}"
                )
            for j, z_val in enumerate(z_values):
                k_flat.append(k_val)
                z_flat.append(z_val)
                sigma_flat.append(row[j])

        # coordinates = (N, 2) array of (k, z) pairs
        self.coordinates = np.column_stack([
            np.array(k_flat),
            np.array(z_flat)
        ])

        # observed = Σ values from KiDS-1000
        self.observed = np.array(sigma_flat)

        # errors = relative uncertainty (systematic)
        relative_error = kwargs.get("relative_error", 0.02)
        self.errors = np.abs(self.observed) * relative_error

        # Floor: minimum error = 0.005
        self.errors = np.maximum(self.errors, 0.005)

        self._loaded = True
        logger.info(
            "Loaded KiDS-1000 Σ(k,z) data: %d grid points "
            "(k: %s, z: %s), Δχ² = %.1f",
            len(self.observed),
            k_values, z_values,
            self._likelihood_analysis.get("delta_chi2", 0)
        )

    def predict(self, params_dict: dict) -> np.ndarray:
        """
        Compute predicted Σ(k,z) at data grid points.

        Uses parametric _LensingResponseEngine as LCDM fallback
        when EFCLensing engine is a stub.
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        k_array = self.coordinates[:, 0]
        z_array = self.coordinates[:, 1]

        if _EFC_PHYSICS_READY:
            # Use full EFC lensing engine
            return self.engine.compute(params_dict, self.coordinates)
        else:
            # Parametric Σ(k,z) fallback
            return _LensingResponseEngine.compute_sigma(
                params_dict, k_array, z_array
            )

    def get_best_fit_params(self) -> dict:
        """Return best-fit parameters from KiDS-1000 analysis."""
        if self._fit_results is None:
            return {}
        bp = self._fit_results.get("best_fit_parameters", {})
        return {k: v.get("value") for k, v in bp.items() if isinstance(v, dict)}

    def get_s8_reframing(self) -> dict:
        """
        Return the S₈ tension reframing analysis.

        Shows how including Σ reduces KiDS-1000 vs Planck tension
        from 2.6σ to 0.3σ.
        """
        if self._s8_analysis is None:
            return {}
        return self._s8_analysis

    def get_tomographic_fingerprint(self) -> dict:
        """Return tomographic improvement factors (low-z vs high-z)."""
        if self._tomographic is None:
            return {}
        return self._tomographic

    def get_delta_chi2(self) -> float:
        """Return Δχ² improvement from adding Σ."""
        if self._likelihood_analysis is None:
            return 0.0
        return self._likelihood_analysis.get("delta_chi2", 0.0)

    def summary(self) -> dict:
        base = super().summary()
        if self._likelihood_analysis:
            base["delta_chi2"] = self._likelihood_analysis.get("delta_chi2", 0)
            base["delta_AIC"] = self._likelihood_analysis.get("delta_AIC", 0)
            base["n_original_data"] = self._likelihood_analysis.get("n_data_points", 0)
        if self._s8_analysis:
            reframed = self._s8_analysis.get("reframed_analysis", {})
            base["s8_tension_before"] = self._s8_analysis.get(
                "standard_comparison", {}).get("tension_sigma", None)
            base["s8_tension_after"] = reframed.get(
                "comparison_to_planck", {}).get("tension_sigma", None)
        return base
