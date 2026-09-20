"""Measured ventricular pressure-volume cycle observable (volume in mL)."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class CardiacCycleEngine(EFCEngine):
    REQUIRED_PARAMS = ["heart_rate_bpm", "stroke_volume_ml", "ejection_fraction",
                       "end_diastolic_volume_ml", "end_systolic_volume_ml", "systole_fraction"]
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "homo.hjerte_syklus"

    def validate_params(self, p: dict) -> bool:
        if not super().validate_params(p):
            return False
        return (0 < p["heart_rate_bpm"] <= 300 and 0 < p["stroke_volume_ml"] <= p["end_diastolic_volume_ml"] and
                0 < p["ejection_fraction"] <= 1 and 0 < p["systole_fraction"] < 1 and
                0 <= p["end_systolic_volume_ml"] < p["end_diastolic_volume_ml"])

    def classify(self, p: dict, t_s: float) -> str:
        cycle = 60.0 / p["heart_rate_bpm"]
        if t_s < 0 or t_s > cycle:
            return "utenfor"
        s = p["systole_fraction"] * cycle
        if t_s < 0.05 * s:
            return "isovolumetrisk_kontraksjon"
        if t_s <= s:
            return "ejeksjon"
        if t_s < s + 0.05 * (cycle - s):
            return "isovolumetrisk_relaksasjon"
        return "fylling"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        t = np.asarray(coordinates, dtype=float)
        out = np.full(t.shape, np.nan)
        try:
            if t.ndim != 1 or not self.validate_params(params_dict):
                return out
            cycle = 60.0 / params_dict["heart_rate_bpm"]
            s = params_dict["systole_fraction"] * cycle
            ok = (t >= 0) & (t <= cycle)
            out[ok] = params_dict["end_diastolic_volume_ml"]
            ej = ok & (t > 0) & (t <= s)
            out[ej] = params_dict["end_diastolic_volume_ml"] - params_dict["stroke_volume_ml"] * t[ej] / s
            fill = ok & (t > s)
            out[fill] = params_dict["end_systolic_volume_ml"] + params_dict["stroke_volume_ml"] * (t[fill] - s) / (cycle - s)
            return out
        except (TypeError, ValueError, KeyError):
            return out

    def regime_node(self, p: dict) -> dict:
        cycle = 60.0 / p["heart_rate_bpm"]
        return {"id": "homo.hjerte_syklus", "synlighet": self.SYNLIGHET,
                "phase": "regime_engine", "regime": {"name": "cardiac cycle",
                "validity": f"t in [0, {cycle}] s; NaN outside",
                "law_form": "filling -> isovolumetric contraction -> ejection -> isovolumetric relaxation"},
                "measure": {"target": "ventricular volume [mL]", "instrument": "echocardiography"},
                "emergence": {"loop": "fill -> press -> fill", "properties": ["SV", "EF", "HR"]}}
