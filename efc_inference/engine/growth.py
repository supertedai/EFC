"""
EFC Growth Function Engine -- MVP-G1: Hubble Friction Channel

Computes f*sigma8(z) from EFC parameters using the standard growth ODE
with cosmology-model-modified H(a).

Physics (MVP-G1):
    The growth of linear perturbations obeys:

        D'' + [3/a + H'/H] D' - source(a) * D = 0

    where ' = d/da, E(a) = H(a)/H0, and the EFC deformation enters
    through the cosmology model. TWO channels exist:
      - Hubble friction: H(a) changes (all variants; EFCVariantA/B
        have mu = 1 — the Poisson term unchanged there).
      - The μ channel (step 13): EFCVariantC+ scales the source by
        μ(a) = 1 + (mu_0 - 1)·g(a); mu_0 < 1 damps the growth.
        (mu_0 is optional, default 1.0, valid [0, 2].)

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

    # Optional perturbation channel: μ(a) = 1 + (mu_0 - 1)·g(a) in the
    # variants that support it (EFCVariantC+). mu_0=1.0 = ΛCDM source.
    # Validity interval [0, 2]: μ must stay positive over g(a)∈[0,1].
    MU0_MIN, MU0_MAX, MU0_DEFAULT = 0.0, 2.0, 1.0

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

    def validate_params(self, params_dict: dict) -> bool:
        """The required fields (inherited check) + mu_0 if given: must be
        a finite number in [0, 2]. Invalid types (strings, None, bool)
        are rejected without exception."""
        if not super().validate_params(params_dict):
            return False
        if "mu_0" in params_dict:
            mu0 = params_dict["mu_0"]
            # No strings — not even numeric ones: the type is part of the
            # contract, and silent conversion hides errors at the caller.
            if isinstance(mu0, (bool, str)) or mu0 is None:
                return False
            try:
                mu0 = float(mu0)
            except (TypeError, ValueError):
                return False
            if not np.isfinite(mu0):
                return False
            if not (self.MU0_MIN <= mu0 <= self.MU0_MAX):
                return False
        return True

    def stotter_mu(self) -> bool:
        """Does the injected cosmology have a perturbation-μ channel?
        (EFCVariantA/B have μ=1 hardcoded — mu_0 then has no effect.)"""
        return hasattr(self.cosmology, "mu_of_a")

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

    # ------------------------------------------------------------------
    # The regime_node() bridge (step 11): the engine describes itself in the atlas
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        om = params_dict["Omega_m"]
        h0 = params_dict["H0"]
        s8 = params_dict["sigma8"]
        al = params_dict["alpha_cosmo"]
        mu0 = params_dict.get("mu_0", self.MU0_DEFAULT)
        if self.stotter_mu():
            mu_description = (
                f"mu_0={mu0} (μ = 1 + (mu_0−1)·g(a) — "
                f"{self.cosmology.name} has the channel; mu_0<1 damps the growth)"
            )
        else:
            mu_description = (
                f"{self.cosmology.name} has no μ channel (μ=1 hardcoded; "
                "a given mu_0 has no effect — the channel exists in "
                "EFCVariantC+)"
            )
        validity = (
            f"fσ8(z) via the growth ODE with EFC-deformed H(a): Omega_m={om}, "
            f"H0={h0}, sigma8={s8}, alpha_cosmo={al}, {mu_description} — "
            "the L2 regime's growth of structure (perturbation level)"
        )
        law_form = ("D'' + [3/a + H'/H] D' - source(a)*D = 0 — numerical "
                    "integration, f = d ln D / d ln a; the source scales "
                    "with μ(a) when the variant has the channel")
        return {
            "id": "efc.growth_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["mu=0.5 (EFCVariantC) reproduces fsigma8 ~ 0.430 — parameter choice — sealed criterion", "mu=1.0 gives 0.4534 — contrast point"],
            "motor": "growth"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "tid"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the staircase its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {"name": "The growth engine — fσ8",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "fσ8(z) — growth rate times amplitude",
                "measurer": "EFCGrowth (growth ODE with EFC-H)",
                "instrument": "the observation side is RSD/ELG/QSO; the engine "
                              "computes the growth",
                "proxy_chain": ["RSD measurements -> fσ8 (observation)",
                                "fσ8 -> EFC parameters (inference)"],
                "placement": "the engine is the L2 regime's own yardstick — "
                             "the arbiter against the sealed fσ8 baseline "
                             "is the actual EFC test",
                "compression": "the whole growth history -> four parameters",
            },
            "episenter": "the growth frame: the fσ8 curve is where EFC meets "
                         "the observation — the judgement, not the judgement decided",
            "buffer": {
                "role": "the structure's matter buffer grows through "
                        "the coupling field — modelled, not measured directly",
                "note": "the buffer belongs to the model, not to the engine.",
            },
            "ontology": {
                "assumes": ["linear perturbation theory holds at the fσ8 scales", "the growth ODE with EFC-H(a) "
                            "is the right deformation"],
                "source": "MVP-G1 hubble friction channel; "
                          "efc_inference/engine/growth.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "the engine sees only fσ8(z) — one channel "
                                     "of the growth's full state",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "density -> growth -> structure — fσ8 is the loop's "
                        "accelerometer",
                "properties": ["sigma8", "gamma_vekst"],
            },
            "fractal": {
                "pattern": "the growth regime knee — the same transition pattern "
                           "as CC->CV and L1->L2 (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "the engine works along z inside L2",
                "global": "fσ8 is the prediction side of the arbiter — coupled to "
                          "the kosmos.kosmologi-emnene topics (prediction) and "
                          "obs.fsigma8 (OBSERVED_IN)",
                "empathy_note": "the engine knows that the baseline judges it — "
                                "it nevertheless only describes itself, it "
                                "does not judge itself.",
            },
        }
