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

    # ------------------------------------------------------------------
    # regime_node() bridge (step 11): the engine describes itself in the atlas.
    # Honest about the stub: the physics is not implemented, and the
    # self-description says so — it describes the contract, not a computation.
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        al = params_dict["alpha_lens"]
        kk = params_dict["kappa_EFC"]
        validity = (
            f"STUB: the convergence kappa(theta) — the physics is NOT "
            f"implemented (alpha_lens={al}, kappa_EFC={kk}); the engine "
            "describes the contract, not the computation — no measurement "
            "is claimed"
        )
        law_form = ("(contract: kappa(theta) from alpha_lens/kappa_EFC — "
                    "awaiting implementation)")
        return {
            "id": "efc.lensing_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the kappa map — observed, not modelled — stub boundary"],
            "motor": "lensing"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "Lensing is measured by Planck/ACT/SPT and carried by them; this node is our CONTRACT (a stub) — it claims no measurement, and nobody in the field gains from reading it as one.",
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
                "indeks": 0,
                "forelder": None,
                "tidsskala": "—",
                "lengdeskala": "—"
            },            "regime": {"name": "The lensing engine — kappa(theta) [stub]",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "kappa(theta) — convergence as a function of "
                          "angular position",
                "measurer": "EFCLensing (stub — compute() raises "
                            "NotImplementedError)",
                "instrument": "the observation side is weak lensing; "
                              "the engine computes nothing yet",
                "proxy_chain": ["shear -> kappa (observation)",
                                "kappa -> EFC parameters (awaiting "
                                "the physics)"],
                "placement": "the place of the engine in L2 is reserved, "
                             "not taken",
                "compression": "no compression yet — the contract is "
                               "defined, the value is not",
            },
            "episenter": "the angular frame: the lensing is the L2 "
                         "structure's mapping — the contract stands, "
                         "the physics waits",
            "buffer": {
                "role": "the structure's mass buffer bends light — "
                        "the mechanism is observed, the engine does not "
                        "model it yet",
                "note": "the buffer belongs to reality, not to the engine.",
            },
            "ontology": {
                "assumes": ["weak lensing is a valid imaging instrument", "The EFC deformation can be "
                            "translated into kappa — unverified"],
                "source": "stub contract; efc_inference/engine/"
                          "lensing.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "none — the engine does not observe "
                                     "yet",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "mass -> curvature -> kappa — the loop is "
                        "observed, not modelled here",
                "properties": [],
            },
            "fractal": {
                "pattern": "mapping as regime — the same pattern as "
                           "the observation chains in the atlas (analogy)",
                "note": "the stub carries the pattern without the computation.",
            },
            "coupling": {
                "local": "the contract is local per line of sight",
                "global": "kappa is the L2 mapping — coupled to "
                          "obs.cmb_lensing (OBSERVED_IN, when the physics "
                          "exists)",
                "empathy_note": "the stub knows what it cannot do — and says "
                                "so.",
            },
        }
