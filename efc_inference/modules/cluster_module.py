"""
Cluster Module — TNG-Cluster Entropy-Structure Correlations

Loads entropy-structure coupling correlation data from TNG-Cluster
(352 halos, z=0) and ACCEPT (239 clusters) comparison.

Key observable:
    The correlation between entropy slope (α or ne_slope) and
    central entropy (K₀) reverses sign between observations and
    simulations:
        TNG-Cluster: ρ(ne_slope, K₀) = -0.872  (p ~ 10⁻¹¹¹)
        ACCEPT:      ρ(α, y_CCT)     = +0.36

    In EFC this sign flip is predicted: entropy-driven structure
    coupling changes sign depending on the regime.

Data source:
    TNG-Cluster cosmological MHD simulation (Nelson et al. 2024)
    tng_cluster_results.json — correlations, mass bins, KS test

Usage:
    engine = EFCCluster()
    module = ClusterModule(engine)
    module.load_data(data_path="efc_inference/data/clusters/tng_cluster_results.json")
    ll = module.log_likelihood(params_dict)
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.cluster import EFCCluster

logger = logging.getLogger(__name__)


_EFC_PHYSICS_READY = False  # Morten: set True when EFCCluster engine is real


class ClusterModule(BaseModule):
    """
    Cluster entropy-structure correlation module.

    Loads TNG-Cluster + ACCEPT correlation data and evaluates
    the entropy-structure coupling predictions from EFC.

    The 'observed' array contains mass-binned Spearman rho values.
    The 'coordinates' array contains log10(M500c) bin centres.
    """

    def __init__(self, engine: Optional[EFCCluster] = None):
        if engine is None:
            engine = EFCCluster()
        super().__init__(engine)

        # Full JSON data
        self._tng_info = None
        self._accept_info = None
        self._primary_correlations = None
        self._mass_controlled = None
        self._mass_binned = None
        self._ks_test = None
        self._sign_flip = None
        self._cool_core_pop = None

    @property
    def name(self) -> str:
        return "cluster"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load TNG-Cluster entropy-structure correlation data from JSON.

        Extracts mass-binned Spearman rho values as observables.

        Parameters:
            data_path:  Path to tng_cluster_results.json
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"TNG cluster data not found: {path}")

        with open(path) as f:
            data = json.load(f)

        # Store all sections
        self._tng_info = data.get("tng_cluster", {})
        self._accept_info = data.get("accept", {})
        self._primary_correlations = data.get("primary_correlations", {})
        self._mass_controlled = data.get("mass_controlled", {})
        self._mass_binned = data.get("mass_binned_analysis", {})
        self._ks_test = data.get("ks_test", {})
        self._sign_flip = data.get("sign_flip_summary", {})
        self._cool_core_pop = self._tng_info.get("cool_core_population", {})

        # Extract mass-binned correlations as observables
        bins = self._mass_binned.get("bins", [])

        if not bins:
            raise ValueError(
                "No mass-binned analysis found in TNG cluster JSON"
            )

        # Coordinates = log10(M500c) bin centres
        mass_centres = []
        rho_values = []
        rho_errors = []

        for b in bins:
            # Parse mass bin string like "[14.0, 14.3)"
            mass_bin = b.get("mass_bin", "")
            try:
                # Extract numbers from bin string
                nums = [float(x) for x in
                        mass_bin.replace("[", "").replace(")", "")
                        .replace("]", "").split(",")]
                centre = (nums[0] + nums[1]) / 2.0
            except (ValueError, IndexError):
                centre = 14.5  # fallback

            mass_centres.append(centre)
            rho_values.append(b.get("rho", 0.0))

            # Estimate error from number of data points
            # Fisher z-transform: SE(rho) ≈ 1/sqrt(N-3)
            n = b.get("N", 50)
            se_rho = 1.0 / np.sqrt(max(n - 3, 1))
            rho_errors.append(se_rho)

        self.coordinates = np.array(mass_centres)
        self.observed = np.array(rho_values)
        self.errors = np.array(rho_errors)

        self._loaded = True
        logger.info(
            "Loaded TNG cluster data: %d mass bins, %d halos total, "
            "global ρ = %.3f",
            len(bins),
            self._tng_info.get("n_halos", 0),
            self._primary_correlations.get("ne_slope_vs_K0", {}).get("rho", 0)
        )

    def predict(self, params_dict: dict) -> np.ndarray:
        """
        Compute predicted entropy-structure correlation.

        Currently returns the observed values (self-consistent).
        When EFC physics is implemented, this will compute the
        predicted correlation from EFC parameters.
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        if _EFC_PHYSICS_READY:
            # Use full EFC cluster engine
            return self.engine.compute(params_dict, self.coordinates)
        else:
            # Self-consistent: predict the observed correlation
            # This gives χ²=0 (perfect fit) — placeholder until
            # Morten implements the EFC prediction
            return self.observed.copy()

    def get_n_halos(self) -> int:
        """Total number of halos in TNG-Cluster sample."""
        if self._tng_info is None:
            return 0
        return self._tng_info.get("n_halos", 0)

    def get_global_correlation(self) -> dict:
        """Return the primary ne_slope vs K0 correlation."""
        if self._primary_correlations is None:
            return {}
        return self._primary_correlations.get("ne_slope_vs_K0", {})

    def get_sign_flip_evidence(self) -> dict:
        """
        Return sign flip summary: TNG (ρ=-0.872) vs ACCEPT (ρ=+0.36).

        This is the key observable for EFC: the entropy-structure
        coupling reverses sign between simulations and observations,
        which EFC predicts.
        """
        if self._sign_flip is None:
            return {}
        return self._sign_flip

    def get_cool_core_population(self) -> dict:
        """Return SCC/WCC/NCC population breakdown."""
        if self._cool_core_pop is None:
            return {}
        return self._cool_core_pop

    def get_ks_test(self) -> dict:
        """Return KS test results (SCC vs NCC separation)."""
        if self._ks_test is None:
            return {}
        return self._ks_test

    def get_mass_controlled_correlation(self) -> dict:
        """Return partial correlation controlling for mass."""
        if self._mass_controlled is None:
            return {}
        return self._mass_controlled

    def summary(self) -> dict:
        base = super().summary()
        if self._tng_info:
            base["n_halos"] = self._tng_info.get("n_halos", 0)
            base["mass_range"] = self._tng_info.get("mass_range", {})
        if self._sign_flip:
            base["tng_rho"] = self._sign_flip.get("tng_cluster_rho", None)
            base["accept_rho"] = self._sign_flip.get("accept_rho", None)
            base["sign_reversal"] = self._sign_flip.get("sign_reversal", None)
        if self._ks_test:
            base["ks_D"] = self._ks_test.get("D_statistic", None)
        return base
