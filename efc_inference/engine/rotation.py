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
    # regime_node() bridge (step 11): the engine describes itself in the atlas
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        es = params_dict["entropy_scale"]
        ls = params_dict["length_scale"]
        vs = params_dict["velocity_scale"]
        validity = (
            "rotation curves v(r) from the EFC kernel (fallback: parametric) — "
            f"entropy scale {es}, length scale {ls}, velocity scale {vs}; "
            "flat rotation WITHOUT a dark-matter assumption — read as the L2 "
            "regime's local test (analogy, not proven)"
        )
        law_form = ("v(r) via efc_core; fallback v = vs*sqrt(r/(r+ls)) — "
                    "numerical curve, no table")
        return {
            "id": "efc.rotation_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["PPN gamma=1 — leading order — validity boundary"],
            "motor": "rotation"},
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
            },            "regime": {"name": "The rotation engine — galaxy rotation",
                       "validity": validity, "law_form": law_form},
            "phase": "regime_engine",
            "measure": {
                "target": "v(r) — rotation velocity as a function of radius",
                "measurer": "EFCRotation (efc_core + parametric fallback)",
                "instrument": "the observation side is galaxy spectra; the "
                              "engine computes the curve",
                "proxy_chain": ["spectral lines -> v(r) (observation)",
                                "v(r) -> EFC parameters (inference)"],
                "placement": "the engine classifies the local "
                             "structure of the L2 regime — the galaxy as "
                             "gravitational space",
                "compression": "one rotation curve -> four EFC parameters",
            },
            "episenter": "the radius framework: the flatness of the curve "
                         "is the test — hypothesis, not a verdict",
            "buffer": {
                "role": "the matter buffer of the galaxy keeps the curve "
                        "flat through the coupling field — interpretation, "
                        "not measurement",
                "note": "the buffer belongs to the model, not to the engine.",
            },
            "ontology": {
                "assumes": ["rotation curves are a pure gravitational measurement",
                            "the EFC core is correct for the "
                            "galaxy scale"],
                "source": "efc_core; parametric fallback — "
                          "efc_inference/engine/rotation.py",
            },
            "observer": {
                "er_del_av_systemet": True,"bandwidth": "the engine sees only v(r) — one channel "
                                     "of the galaxy's full dynamics",
                         "awareness": "instrument_window"},
            "emergence": {
                "loop": "mass -> coupling field -> flat rotation — "
                        "the flatness of the curve is the signature of the loop",
                "properties": ["v_flat", "r_skala"],
            },
            "fractal": {
                "pattern": "flatness as regime — the same observation pattern "
                           "as the CC plateau and water's phase plateaus (analogy)",
                "note": "one pattern, three domains — not identity.",
            },
            "coupling": {
                "local": "the engine works on one galaxy at a time",
                "global": "rotation curves are the L2 regime's local read-out "
                          "— coupled to the growth and hubble engines via "
                          "the regime (COUPLED_TO)",
                "empathy_note": "every galaxy carries the whole regime in its "
                                "own curve.",
            },
        }
