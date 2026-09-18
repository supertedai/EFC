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

    # ------------------------------------------------------------------
    # regime_node() bro (trinn 11): motoren beskriver seg selv i atlaset
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        h0 = params_dict["H0"]
        om = params_dict["Omega_m"]
        al = params_dict["alpha_cosmo"]
        validity = (
            f"H(z) for z >= 0 — EFC-deformed expansion: Omega_m={om}, "
            f"H0={h0}, alpha_cosmo={al} (alpha=0 = the LCDM baseline); the "
            "engine COMPUTES the rate via the injected background model — "
            "it classifies no regime boundary itself"
        )
        law_form = ("E²(a) = Om*a^-3 + (1-Om) + alpha*[g(a)-g(1)] — "
                    "the EFCVariantA background (default; the engine "
                    "accepts other injected models too — this law form "
                    "describes only the default)")
        return {
            "id": "efc.hubble_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the fσ8 measurements (Stage-III, 7 of them) — the data basis"],
            "motor": "hubble"},
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
            # the engine cannot know where in the ladder its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": "efc.efc_background_engine",
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {"name": "The Hubble engine — the expansion",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "H(z) — the expansion rate",
                "measurer": "EFCHubble (the EFCVariantA cosmology)",
                "instrument": "the observation side is BAO/chronometers; "
                              "the engine computes the rate",
                "proxy_chain": ["BAO/SNIa -> H(z) (observation)",
                                "H(z) -> EFC parameters (inference)"],
                "placement": "the engine computes the expansion rate along z — "
                             "the r_d calibration is the L1 anchor (the observation "
                             "side, not the engine's own classification)",
                "compression": "all of H(z) -> three EFC parameters",
            },
            "episenter": "the z frame: the H(z) curve is the backbone of "
                         "the regime — the observations are carried by it",
            "buffer": {
                "role": "the background energy is the buffer that holds "
                        "the expansion — modelled, not measured directly",
                "note": "the buffer belongs to the background, not the engine.",
            },
            "ontology": {
                "assumes": ["the background is homogeneous and isotropic",
                            "E²(a) er den riktige deformasjonen"],
                "source": "EFCVariantA; efc_inference/engine/hubble.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "the engine sees only H(z) — one channel "
                                     "of the full state of the expansion",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "density -> expansion -> redshift — "
                        "H(z) is the read-out of the loop",
                "properties": ["H0", "Omega_m", "alpha_cosmo"],
            },
            "fractal": {
                "pattern": "the regime knee of expansion — the same transition "
                           "pattern as the CC->CV knee (analogy, not "
                           "identity)",
                "note": "one pattern, two domains.",
            },
            "coupling": {
                "local": "the engine works along the z axis",
                "global": "H(z) carries the L1->L2 transition — coupled to "
                          "growth (the growth feels the expansion) and "
                          "obs.bao (COUPLED_TO/OBSERVED_IN)",
                "empathy_note": "the expansion does not itself know that it "
                                "is observed — but the engine knows what it "
                                "carries.",
            },
        }
