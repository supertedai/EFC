"""
EFC Rotation Velocity Engine

Wraps src/efc/core/efc_core.py to compute galaxy rotation curves.
This is the ONLY non-stub engine — it uses existing EFC physics code.

Physics:
    v(r) = sqrt(|Ef(r)| * r)
    where Ef is the EFC energy flow field.
"""

import numpy as np
import sys
from pathlib import Path

from .base_engine import EFCEngine

# Add src/ to path so we can import efc_core
_src_path = str(Path(__file__).resolve().parents[2] / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


class EFCRotation(EFCEngine):
    """
    Compute EFC rotation velocity profile v(r).

    Uses EFCParameters and EFCModel from src/efc/core/efc_core.py.

    Required parameters:
        - entropy_scale (S0): entropy normalization
        - length_scale (Ls): characteristic length scale
        - flow_constant: energy flow coupling
        - velocity_scale: velocity normalization
    """

    REQUIRED_PARAMS = ["entropy_scale", "length_scale",
                       "flow_constant", "velocity_scale"]

    @property
    def name(self) -> str:
        return "rotation"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute rotation velocity at radii r.

        Parameters:
            params_dict:  Must contain entropy_scale, length_scale,
                         flow_constant, velocity_scale
            coordinates:  (N,) array of radii in kpc

        Returns:
            (N,) array of rotation velocities in km/s
        """
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan)

        try:
            from efc.core.efc_core import EFCParameters, EFCModel

            efc_params = EFCParameters(
                entropy_scale=params_dict["entropy_scale"],
                length_scale=params_dict["length_scale"],
                flow_constant=params_dict["flow_constant"],
                velocity_scale=params_dict["velocity_scale"],
            )

            model = EFCModel(efc_params)
            v_rot = model.rotation_velocity(coordinates)

            return v_rot

        except ImportError:
            # Fallback: simple parametric rotation curve
            # v(r) = velocity_scale * sqrt(r / (r + length_scale))
            Ls = params_dict["length_scale"]
            Vs = params_dict["velocity_scale"]
            return Vs * np.sqrt(coordinates / (coordinates + Ls))

        except Exception:
            return np.full_like(coordinates, np.nan)

    # ------------------------------------------------------------------
    # regime_node() bro (trinn 11): motoren beskriver seg selv i atlaset
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        es = params_dict["entropy_scale"]
        ls = params_dict["length_scale"]
        vs = params_dict["velocity_scale"]
        validity = (
            "rotasjonskurver v(r) fra EFC-kjernen (fallback: parametrisk) — "
            f"entropiskala {es}, lengdeskala {ls}, hastighetsskala {vs}; "
            "flat rotasjon UTEN moerk-materie-antakelse — lest som L2-"
            "regimets lokale test (analogi, ikke bevist)"
        )
        law_form = ("v(r) via efc_core; fallback v = vs*sqrt(r/(r+ls)) — "
                    "numerisk kurve, ingen tabell")
        return {
            "id": "efc.rotation_engine",
            "regime": {"name": "Rotasjonsmotoren — galakserotasjon",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "v(r) — rotasjonshastighet som funksjon av radius",
                "measurer": "EFCRotation (efc_core + parametrisk fallback)",
                "instrument": "observasjonssiden er galaksespektre; motoren "
                              "regner kurven",
                "proxy_chain": ["spektrallinjer -> v(r) (observasjon)",
                                "v(r) -> EFC-parametre (inferens)"],
                "placement": "motoren klassifiserer L2-regimets lokale "
                             "struktur — galaksen som gravitasjonsrom",
                "compression": "en rotasjonskurve -> fire EFC-parametre",
            },
            "episenter": "radiusrammen: kurvens flathet er testen — "
                         "hypotese, ikke dom",
            "buffer": {
                "role": "galaksens materie-buffer holder kurven flat "
                        "gjennom koplingsfeltet — tolkning, ikke maaling",
                "note": "bufferen er modellens, ikke motorens.",
            },
            "ontology": {
                "assumes": ["rotasjonskurver er et rent gravitasjons-"
                            "maaleri", "EFC-kjernen er korrekt for "
                            "galakseskalaen"],
                "source": "efc_core; parametrisk fallback — "
                          "efc_inference/engine/rotation.py",
            },
            "observer": {"bandwidth": "motoren ser bare v(r) — én kanal "
                                     "av galaksens fulle dynamikk",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "masse -> koplingsfelt -> flat rotasjon — "
                        "kurvens flathet er loopens signatur",
                "properties": ["v_flat", "r_skala"],
            },
            "fractal": {
                "pattern": "flathet som regime — samme observasjonsmonster "
                           "som CC-plataaet og vannets faseplatåer (analogi)",
                "note": "ett monster, tre domener — ikke identitet.",
            },
            "coupling": {
                "local": "motoren arbeider på én galakse av gangen",
                "global": "rotasjonskurver er L2-regimets lokale avlesning "
                          "— koblet til vekst- og hubble-motorene via "
                          "regimet (COUPLED_TO)",
                "empathy_note": "hver galakse bærer hele regimet i sin "
                                "egen kurve.",
            },
        }
