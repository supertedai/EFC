"""
EFC Cluster Mass Function Engine — STUB

Computes n(M, z) — the halo mass function from EFC parameters.

Physics (to be implemented by Morten):
    The cluster mass function in EFC is modified because the
    energy flow field affects the collapse threshold:
        n(M, z) = (rho_m / M) * |d ln sigma / d ln M| * f_EFC(sigma, z)
    where f_EFC is the EFC multiplicity function.

Required parameters (tentative):
    - Omega_m: matter density
    - sigma8: power spectrum normalization
    - alpha_cluster: EFC coupling for cluster scales
    - delta_c_EFC: EFC-modified collapse threshold
"""

import numpy as np
from .base_engine import EFCEngine


class EFCCluster(EFCEngine):
    """
    Compute halo mass function n(M, z).

    STATUS: STUB — raises NotImplementedError.
    Morten: implement compute() with EFC mass function.
    """

    REQUIRED_PARAMS = ["Omega_m", "sigma8", "alpha_cluster"]

    @property
    def name(self) -> str:
        return "cluster"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute n(M, z) at masses M.

        Parameters:
            params_dict:  Must contain Omega_m, sigma8, alpha_cluster, ...
            coordinates:  (N,) array of halo masses M (solar masses)

        Returns:
            (N,) array of dn/dM (number density per mass interval)
        """
        raise NotImplementedError(
            "EFCCluster.compute() is a stub.\n"
            "Morten: implement the EFC mass function here.\n"
            "Input: params_dict with Omega_m, sigma8, alpha_cluster\n"
            "Input: coordinates = halo masses M in solar masses\n"
            "Output: dn/dM array"
        )
