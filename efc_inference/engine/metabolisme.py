"""Bounded cellular-energy metabolism observable.

Computes ATP yield per glucose for the declared oxygen/intensity regime.
It does not invent a flux where the substrate or oxygen regime is outside
this simple measurement domain.
"""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class MetabolismEngine(EFCEngine):
    REQUIRED_PARAMS = ["aerobic_atp_per_glucose", "anaerobic_atp_per_glucose",
                       "carbohydrate_rq", "oxygen_fraction", "anaerobic_intensity_threshold"]
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "homo.metabolisme"

    def validate_params(self, params_dict: dict) -> bool:
        if not super().validate_params(params_dict):
            return False
        return (0 < params_dict["aerobic_atp_per_glucose"] and
                0 < params_dict["anaerobic_atp_per_glucose"] <= 2 and
                0 < params_dict["carbohydrate_rq"] <= 2 and
                0 <= params_dict["oxygen_fraction"] <= 1 and
                0 < params_dict["anaerobic_intensity_threshold"] <= 1)

    def classify(self, p: dict, intensity: float) -> str:
        if intensity < 0 or intensity > 1:
            return "utenfor"
        if p["oxygen_fraction"] < 0.1 or intensity >= p["anaerobic_intensity_threshold"]:
            return "anaerob"
        return "hvile" if intensity < 0.1 else "active"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        x = np.asarray(coordinates, dtype=float)
        out = np.full(x.shape, np.nan)
        try:
            if x.ndim != 1 or not self.validate_params(params_dict):
                return out
            ok = (x >= 0) & (x <= 1)
            anaerob = ok & ((x >= params_dict["anaerobic_intensity_threshold"]) |
                            (params_dict["oxygen_fraction"] < 0.1))
            out[ok] = params_dict["aerobic_atp_per_glucose"]
            out[anaerob] = params_dict["anaerobic_atp_per_glucose"]
            return out
        except (TypeError, ValueError, KeyError):
            return out

    def regime_node(self, p: dict) -> dict:
        th = p["anaerobic_intensity_threshold"]
        return {"id": "homo.metabolisme", "synlighet": self.SYNLIGHET,
                "phase": "regime_engine", "regime": {"name": "metabolisme",
                "validity": f"intensitet i [0, 1]; aerob hvile/aktiv under {th}, anaerob fra {th}; utenfor NaN",
                "law_form": "glykolyse -> Krebs -> elektrontransport/oksidativ fosforylering; anaerob glykolyse ved begrenset O2"},
                "measure": {"target": "ATP per glukose", "instrument": "respirometri/metabolomikk"},
                "emergence": {"loop": "substrat -> ATP -> arbeid -> ADP -> substrat", "properties": ["ATP", "RQ", "O2"]}}
