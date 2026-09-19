"""Hodgkin-Huxley-inspired, piecewise action-potential observable.

The output is membrane voltage in mV.  It is deliberately a bounded
physiological waveform, not an EFC analogy.  Reference values are the
textbook measured values: approximately -70 mV at rest, -55 mV threshold,
and +30 mV at the peak (OpenStax, *Anatomy and Physiology 2e*, ch. 12).
"""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class ActionPotentialEngine(EFCEngine):
    REQUIRED_PARAMS = ["resting_potential_mv", "threshold_mv", "peak_potential_mv",
                       "depolarization_ms", "repolarization_ms", "refractory_ms"]
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "homo.aksjonspotensial"

    def validate_params(self, params_dict: dict) -> bool:
        if not super().validate_params(params_dict):
            return False
        return (params_dict["depolarization_ms"] > 0 and
                params_dict["repolarization_ms"] > 0 and
                params_dict["refractory_ms"] >= 0 and
                params_dict["resting_potential_mv"] < params_dict["threshold_mv"] < params_dict["peak_potential_mv"])

    def classify(self, params: dict, t_ms: float) -> str:
        d, r = params["depolarization_ms"], params["repolarization_ms"]
        if t_ms < 0 or t_ms > d + r + params["refractory_ms"]:
            return "utenfor"
        if t_ms == 0 or t_ms > d + r:
            return "hvile"
        if t_ms <= d:
            return "depolarisering"
        return "repolarisering"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        t = np.asarray(coordinates, dtype=float)
        out = np.full(t.shape, np.nan)
        try:
            if t.ndim != 1 or not self.validate_params(params_dict):
                return out
            rest, peak = params_dict["resting_potential_mv"], params_dict["peak_potential_mv"]
            d, r = params_dict["depolarization_ms"], params_dict["repolarization_ms"]
            ok = (t >= 0) & (t <= d + r + params_dict["refractory_ms"])
            out[ok] = rest
            dep = ok & (t > 0) & (t <= d)
            out[dep] = rest + (peak - rest) * t[dep] / d
            rep = ok & (t > d) & (t <= d + r)
            out[rep] = peak - (peak - rest) * (t[rep] - d) / r
            return out
        except (TypeError, ValueError, KeyError):
            return out

    def regime_node(self, params: dict) -> dict:
        d, r, q = (params[k] for k in ("depolarization_ms", "repolarization_ms", "refractory_ms"))
        return {"id": "homo.aksjonspotensial", "synlighet": self.SYNLIGHET,
                "phase": "regime_engine", "regime": {"name": "action potential",
                "validity": f"t in [0, {d+r+q}] ms; NaN outside",
                "law_form": "Na+ depolarisation, K+ repolarisation, refractory recovery"},
                "measure": {"target": "membrane potential V(t) [mV]", "instrument": "patch-clamp"},
                "emergence": {"loop": "rest -> depolarisation -> repolarisation -> refractory -> rest",
                              "properties": ["threshold", "spike", "refractory time"]}}
