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
    # regime_node() bro (trinn 11): motoren beskriver seg selv i atlaset.
    # Ærlig om stubben: fysikken er ikke implementert — kontrakten
    # beskrives, ikke en beregning.
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        om = params_dict["Omega_m"]
        s8 = params_dict["sigma8"]
        ac = params_dict["alpha_cluster"]
        validity = (
            f"STUB: mass funksjonen n(M,z) — fysikken er IKKE "
            f"implementert (Omega_m={om}, sigma8={s8}, "
            f"alpha_cluster={ac}); motoren beskriver kontrakten, ikke "
            "beregningen — ingen maaling er påstått"
        )
        law_form = ("(kontrakt: n(M,z) fra Omega_m/sigma8/alpha_cluster "
                    "— venter på implementering)")
        return {
            "id": "efc.cluster_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
                             "terskler": [], "motor": ""},
            "regime": {"name": "Hopemotoren — n(M,z) [stub]",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "n(M,z) — halomassefunksjonen",
                "measurer": "EFCCluster (stub — compute() hever "
                            "NotImplementedError)",
                "instrument": "observasjonssiden er hopetellinger; "
                              "motoren regner ingenting ennå",
                "proxy_chain": ["hopetelling -> n(M,z) (observasjon)",
                                "n(M,z) -> EFC-parametre (venter på "
                                "fysikken)"],
                "placement": "motorens plass i L2 er reservert, ikke "
                             "inntatt",
                "compression": "ingen kompresjon ennå — kontrakten er "
                               "definert, verdien ikke",
            },
            "episenter": "masse-rommet: halomassefunksjonen er L2-"
                         "strukturens telling — kontrakten står, "
                         "fysikken venter",
            "buffer": {
                "role": "hopene er strukturens tetteste buffere — "
                        "observert, ikke modellert her ennå",
                "note": "bufferen er virkelighetens, ikke motorens.",
            },
            "ontology": {
                "assumes": ["halomassefunksjonen er et gyldig "
                            "strukturinstrument", "EFC-deformasjonen "
                            "lar seg oversette til n(M,z) — uverifisert"],
                "source": "stub-kontrakt; efc_inference/engine/"
                          "cluster.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "ingen — motoren observerer ikke "
                                     "ennå",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "tetthet -> kollaps -> hoper — loopen er "
                        "observert, ikke modellert her",
                "properties": [],
            },
            "fractal": {
                "pattern": "telling som regime — samme mønster som "
                           "observasjonskjedene i atlaset (analogi)",
                "note": "stubben bærer mønsteret uten beregningen.",
            },
            "coupling": {
                "local": "kontrakten er lokal per massebin",
                "global": "n(M,z) er L2-strukturens telling — koblet til "
                          "obs.klynger (OBSERVED_IN, når fysikken "
                          "finnes)",
                "empathy_note": "stubben vet hva den ikke kan — og sier "
                                "det.",
            },
        }
