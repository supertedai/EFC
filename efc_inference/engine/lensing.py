"""
EFC Lensing Engine — STUB

Computes convergence kappa(theta) from EFC parameters.

Physics (to be implemented by Morten):
    Gravitational lensing convergence in EFC:
        kappa(theta) = (1/2) * integral[rho_eff(r) * Sigma_cr^{-1}] dl
    where rho_eff includes the EFC energy flow contribution.
    The effective mass includes both baryonic and flow-induced components.

Required parameters (tentative):
    - Sigma_cr: critical surface mass density
    - alpha_lens: EFC lensing coupling
    - kappa_EFC: EFC convergence normalization
"""

import numpy as np
from .base_engine import EFCEngine


class EFCLensing(EFCEngine):
    """
    Compute lensing convergence kappa(theta).

    STATUS: STUB — raises NotImplementedError.
    Morten: implement compute() with EFC lensing equations.
    """

    REQUIRED_PARAMS = ["alpha_lens", "kappa_EFC"]

    @property
    def name(self) -> str:
        return "lensing"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute kappa(theta) at angular positions.

        Parameters:
            params_dict:  Must contain alpha_lens, kappa_EFC, ...
            coordinates:  (N,) array of angular positions (arcmin)

        Returns:
            (N,) array of convergence kappa
        """
        raise NotImplementedError(
            "EFCLensing.compute() is a stub.\n"
            "Morten: implement the EFC lensing convergence here.\n"
            "Input: params_dict with alpha_lens, kappa_EFC\n"
            "Input: coordinates = angular positions in arcmin\n"
            "Output: kappa(theta) array"
        )
