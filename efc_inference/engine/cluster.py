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

    # ------------------------------------------------------------------
    # regime_node() bridge (step 11): the engine describes itself in the atlas.
    # Honest about the stub: the physics is not implemented — the contract
    # is described, not a computation.
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        om = params_dict["Omega_m"]
        s8 = params_dict["sigma8"]
        ac = params_dict["alpha_cluster"]
        validity = (
            f"STUB: the mass function n(M,z) — the physics is NOT "
            f"implemented (Omega_m={om}, sigma8={s8}, "
            f"alpha_cluster={ac}); the engine describes the contract, not "
            "the computation — no measurement is claimed"
        )
        law_form = ("(contract: n(M,z) from Omega_m/sigma8/alpha_cluster "
                    "— awaiting implementation)")
        return {
            "id": "efc.cluster_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["counting as regime — observed, not modelled — stub limit"],
            "motor": "cluster"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "masse", "tid"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {"name": "The cluster engine — n(M,z) [stub]",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "n(M,z) — the halo mass function",
                "measurer": "EFCCluster (stub — compute() raises "
                            "NotImplementedError)",
                "instrument": "the observation side is halo counts; "
                              "the engine computes nothing yet",
                "proxy_chain": ["halo counts -> n(M,z) (observation)",
                                "n(M,z) -> EFC parameters (awaiting "
                                "the physics)"],
                "placement": "the place of the engine in L2 is reserved, "
                             "not taken",
                "compression": "no compression yet — the contract is "
                               "defined, the value is not",
            },
            "episenter": "the mass space: the halo mass function is the "
                         "count of the L2 structure — the contract "
                         "stands, the physics waits",
            "buffer": {
                "role": "the halos are the structure's densest buffers — "
                        "observed, not modelled here yet",
                "note": "the buffer belongs to reality, not to the engine.",
            },
            "ontology": {
                "assumes": ["the halo mass function is a valid structure instrument", "The EFC deformation "
                            "can be translated into n(M,z) — unverified"],
                "source": "stub contract; efc_inference/engine/"
                          "cluster.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "none — the engine does not observe "
                                     "yet",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "density -> collapse -> clusters — the loop is "
                        "observed, not modelled here",
                "properties": [],
            },
            "fractal": {
                "pattern": "counting as regime — the same pattern as "
                           "the observation chains in the atlas (analogy)",
                "note": "the stub carries the pattern without the computation.",
            },
            "coupling": {
                "local": "the contract is local per mass bin",
                "global": "n(M,z) is the count of the L2 structure — "
                          "coupled to obs.klynger (OBSERVED_IN, when the "
                          "physics exists)",
                "empathy_note": "the stub knows what it cannot do — and says "
                                "so.",
            },
        }
