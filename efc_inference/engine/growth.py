"""
EFC Growth Function Engine -- MVP-G1: Hubble Friction Channel

Computes f*sigma8(z) from EFC parameters using the standard growth ODE
with cosmology-model-modified H(a).

Physics (MVP-G1):
    The growth of linear perturbations obeys:

        D'' + [3/a + H'/H] D' - source(a) * D = 0

    where ' = d/da, E(a) = H(a)/H0, and the EFC deformation enters
    ONLY through H(a) -- Poisson equation is unmodified (mu = 1).

    This is the "Hubble friction channel": the EFC energy-flow field
    modifies expansion history, which changes the friction term H'/H
    in the growth ODE, altering structure formation rate.

    Observables:
        f(a) = d ln D / d ln a = a * D'/D
        sigma8(z) = sigma8_0 * D(z) / D(0)
        f*sigma8(z) = f(z) * sigma8(z)

    LCDM limit: alpha_cosmo = 0 -> reproduces LCDM growth exactly.

Ontology:
    The cosmological model (E^2, dE^2/da, growth source) is injected
    via CosmologyModel at construction time. Gate functions are owned
    by the model, not by this engine.

Required parameters:
    - Omega_m: matter density parameter
    - H0: Hubble constant (km/s/Mpc) -- used by EFCHubble
    - sigma8: normalization of matter power spectrum at z=0
    - alpha_cosmo: EFC flow coupling (same parameter as in EFCHubble)
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Optional

from .base_engine import EFCEngine
from ..core.cosmology_model import CosmologyModel, EFCVariantA


class EFCGrowth(EFCEngine):
    """
    Compute f*sigma8(z) using the standard growth ODE with
    cosmology-model-provided E(a), dE/da, and source term.

    Optimized: computes E(a) and dE/da analytically via the
    CosmologyModel (no spline interpolation).
    """

    REQUIRED_PARAMS = ["Omega_m", "H0", "sigma8", "alpha_cosmo"]

    # Integration settings
    _A_INI = 1e-3       # start deep in matter era
    _RTOL = 1e-8         # relative tolerance (relaxed for speed)
    _ATOL = 1e-10        # absolute tolerance

    def __init__(self, cosmology: Optional[CosmologyModel] = None):
        if cosmology is None:
            cosmology = EFCVariantA()
        self.cosmology = cosmology

    @property
    def name(self) -> str:
        return f"growth-{self.cosmology.name}"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute f*sigma8(z) at redshifts z.

        Parameters:
            params_dict:  Must contain Omega_m, H0, sigma8, alpha_cosmo
            coordinates:  (N,) array of redshifts z

        Returns:
            (N,) array of f*sigma8(z)
        """
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan, dtype=float)

        return self._compute(params_dict, coordinates)

    def _compute(self, params_dict: dict, z: np.ndarray) -> np.ndarray:
        """
        Growth via numerical ODE integration with CosmologyModel.

        Growth ODE in scale factor a:
            D'' + [3/a + (1/E) dE/da] D' - source(a) * D = 0

        where source(a) = (3/2) * Omega_m / (a^5 * E^2) for unmodified Poisson,
        delegated to self.cosmology.growth_source().

        Initial conditions (matter-dominated era, a << 1):
            D(a_ini) = a_ini    (growing mode: D ~ a)
            D'(a_ini) = 1.0     (d/da of D = a is 1)
        """
        z = np.atleast_1d(np.asarray(z, dtype=float))
        s8 = params_dict["sigma8"]

        # Scale factors corresponding to data redshifts
        a_data = 1.0 / (1.0 + z)

        # Check E^2 > 0 at a_ini (if not, unphysical parameters)
        E2_ini = self.cosmology.e_squared(np.array([self._A_INI]), params_dict)
        if E2_ini[0] <= 0:
            return np.full_like(z, np.nan, dtype=float)

        cosmology = self.cosmology  # local ref for closure

        def growth_ode(a, y):
            """RHS of the growth ODE system -- uses CosmologyModel."""
            D, Dp = y

            # E^2(a) and dE^2/da from cosmology model
            a_arr = np.array([a])
            E2 = cosmology.e_squared(a_arr, params_dict).item()

            if E2 <= 0:
                return [0.0, 0.0]

            E_a = np.sqrt(E2)

            dE2_da = cosmology.de_squared_da(a_arr, params_dict).item()
            dE_da = dE2_da / (2.0 * E_a)

            # Friction coefficient: 3/a + E'/E
            friction = 3.0 / a + dE_da / E_a

            # Source term from cosmology model
            source = cosmology.growth_source(a_arr, params_dict).item()

            return [Dp, -friction * Dp + source * D]

        # Initial conditions: matter-dominated growing mode D ~ a
        y0 = [self._A_INI, 1.0]

        # Integrate from a_ini to a=1
        sol = solve_ivp(
            growth_ode,
            t_span=(self._A_INI, 1.0),
            y0=y0,
            method='RK45',
            rtol=self._RTOL,
            atol=self._ATOL,
            dense_output=True,
        )

        if not sol.success:
            return np.full_like(z, np.nan, dtype=float)

        # Evaluate D(a) and D'(a) at data points and at a=1
        D_at_1 = float(sol.sol(1.0)[0])

        if D_at_1 <= 0:
            return np.full_like(z, np.nan, dtype=float)

        fs8 = np.zeros_like(z, dtype=float)

        for i, ai in enumerate(a_data):
            if ai < self._A_INI or ai > 1.0:
                fs8[i] = np.nan
                continue

            D_i, Dp_i = sol.sol(ai)

            if D_i <= 0:
                fs8[i] = np.nan
                continue

            # f(a) = a * D'(a) / D(a)  =  d ln D / d ln a
            f_i = ai * Dp_i / D_i

            # sigma8(z) = sigma8_0 * D(z) / D(0)
            sigma8_z = s8 * D_i / D_at_1

            fs8[i] = f_i * sigma8_z

        return fs8
