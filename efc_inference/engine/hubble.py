"""
EFC Hubble Parameter Engine

Computes H(z) from EFC parameters for BAO / SNIa / H(z) analysis.

Physics:
    H(z) in EFC differs from LCDM because the energy flow field
    modifies the expansion dynamics. The Friedmann-like equation becomes:

        E^2(a) = Omega_m * a^{-3} + Omega_Lambda + alpha * [g(a) - g(1)]

    where g(a) is a late-time logistic gate:

        g(a) = 1 / (1 + exp(-(a - a_t) / delta_a))

    and the normalization [g(a) - g(1)] ensures:
        - At a=1 (today, z=0): the alpha term vanishes -> H0 remains "real H0"
        - At early times (a << a_t): g(a) ~ 0 -> pure LCDM
        - At intermediate z: alpha shapes H(z) without absorbing into H0 or Omega_Lambda

    LCDM limit: alpha = 0 -> E^2 = Omega_m * a^{-3} + (1 - Omega_m)
    This is exact, bit-for-bit identical to FlatLCDM cosmology.

Ontology:
    The cosmological model (E^2 formula, gate parameters, assumptions)
    is injected via CosmologyModel at construction time.
    Default: EFCVariantA (a_t=0.5, delta_a=0.1).
    Alternative: FlatLCDM (pure LCDM, alpha ignored).

Required parameters:
    - H0: Hubble constant (km/s/Mpc)
    - Omega_m: matter density parameter
    - alpha_cosmo: EFC flow coupling at cosmological scale

Morten:
    Current implementation is Variant A (minimal, testable).
    Gate parameters (a_t, delta_a) are owned by EFCVariantA.
    To make them free, create a new CosmologyModel subclass.
"""

import numpy as np
from typing import Optional

from .base_engine import EFCEngine
from ..core.cosmology_model import CosmologyModel, EFCVariantA


class EFCHubble(EFCEngine):
    """
    Compute H(z) from a CosmologyModel.

    H(z) = H0 * E(z)

    where E^2(a) is delegated to the injected CosmologyModel.
    Default cosmology: EFCVariantA (Variant A, fixed gate).
    """

    REQUIRED_PARAMS = ["H0", "Omega_m", "alpha_cosmo"]

    def __init__(self, cosmology: Optional[CosmologyModel] = None):
        if cosmology is None:
            cosmology = EFCVariantA()
        self.cosmology = cosmology

    @property
    def name(self) -> str:
        return f"hubble-{self.cosmology.name}"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute H(z) at redshifts z.

        Parameters:
            params_dict:  Must contain H0, Omega_m, alpha_cosmo
            coordinates:  (N,) array of redshifts z

        Returns:
            (N,) array of H(z) in km/s/Mpc
        """
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan, dtype=float)

        H0 = params_dict["H0"]

        # Scale factor from redshift
        a = 1.0 / (1.0 + coordinates)

        # E^2(a) from cosmology model
        E2 = self.cosmology.e_squared(a, params_dict)

        # Guard: E^2 must be positive for physical H(z)
        result = np.where(E2 > 0, H0 * np.sqrt(E2), np.nan)

        return result
