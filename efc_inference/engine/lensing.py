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
    # regime_node() bro (trinn 11): motoren beskriver seg selv i atlaset.
    # Ærlig om stubben: fysikken er ikke implementert, og selvbeskrivelsen
    # sier det — den beskriver kontrakten, ikke en beregning.
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        al = params_dict["alpha_lens"]
        kk = params_dict["kappa_EFC"]
        validity = (
            f"STUB: konvergensen kappa(theta) — fysikken er IKKE "
            f"implementert (alpha_lens={al}, kappa_EFC={kk}); motoren "
            "beskriver kontrakten, ikke beregningen — ingen maaling er "
            "påstått"
        )
        law_form = ("(kontrakt: kappa(theta) fra alpha_lens/kappa_EFC — "
                    "venter på implementering)")
        return {
            "id": "efc.lensing_engine",
            "regime": {"name": "Linsemotoren — kappa(theta) [stub]",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "kappa(theta) — konvergens som funksjon av "
                          "vinkelposisjon",
                "measurer": "EFCLensing (stub — compute() hever "
                            "NotImplementedError)",
                "instrument": "observasjonssiden er svak linsing; "
                              "motoren regner ingenting ennå",
                "proxy_chain": ["shear -> kappa (observasjon)",
                                "kappa -> EFC-parametre (venter på "
                                "fysikken)"],
                "placement": "motorens plass i L2 er reservert, ikke "
                             "inntatt",
                "compression": "ingen kompresjon ennå — kontrakten er "
                               "definert, verdien ikke",
            },
            "episenter": "vinkelrammen: linsingen er L2-strukturens "
                         "avbildning — kontrakten står, fysikken venter",
            "buffer": {
                "role": "strukturens masse-buffer bøyer lyset — "
                        "mekanismen er observert, motoren modellerer "
                        "den ikke ennå",
                "note": "bufferen er virkelighetens, ikke motorens.",
            },
            "ontology": {
                "assumes": ["svak linsing er et gyldig avbildnings-"
                            "instrument", "EFC-deformasjonen lar seg "
                            "oversette til kappa — uverifisert"],
                "source": "stub-kontrakt; efc_inference/engine/"
                          "lensing.py",
            },
            "observer": {"bandwidth": "ingen — motoren observerer ikke "
                                     "ennå",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "masse -> krumning -> kappa — loopen er "
                        "observert, ikke modellert her",
                "properties": [],
            },
            "fractal": {
                "pattern": "avbildning som regime — samme mønster som "
                           "observasjonskjedene i atlaset (analogi)",
                "note": "stubben bærer mønsteret uten beregningen.",
            },
            "coupling": {
                "local": "kontrakten er lokal per synslinje",
                "global": "kappa er L2-avbildningen — koblet til "
                          "obs.cmb_lensing (OBSERVED_IN, når fysikken "
                          "finnes)",
                "empathy_note": "stubben vet hva den ikke kan — og sier "
                                "det.",
            },
        }
