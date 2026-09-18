"""Bounded cell-cycle phase observable.

Values are categorical codes: G1=0, S=1, G2=2, M=3, G0=4.
Checkpoint failure is represented as G0/blocked, never silently advanced.
"""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class CellCycleEngine(EFCEngine):
    REQUIRED_PARAMS = ["g1_hours", "s_hours", "g2_hours", "m_hours",
                       "g1_checkpoint_passed", "g2_checkpoint_passed", "spindle_checkpoint_passed"]
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "homo.cellesyklus"

    def validate_params(self, params_dict: dict) -> bool:
        if not super().validate_params(params_dict):
            return False
        return all(params_dict[k] > 0 for k in ("g1_hours", "s_hours", "g2_hours", "m_hours")) and all(
            isinstance(params_dict[k], (bool, np.bool_)) for k in self.REQUIRED_PARAMS[4:])

    def classify(self, p: dict, t_hours: float) -> str:
        y = self.compute(p, np.array([t_hours]))[0]
        return ("G1", "S", "G2", "M", "G0")[int(y)] if np.isfinite(y) else "utenfor"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        t = np.asarray(coordinates, dtype=float)
        out = np.full(t.shape, np.nan)
        try:
            if t.ndim != 1 or not self.validate_params(params_dict):
                return out
            g1, s, g2, m = (params_dict[k] for k in ("g1_hours", "s_hours", "g2_hours", "m_hours"))
            total = g1 + s + g2 + m
            ok = (t >= 0) & (t <= total)
            out[ok] = 4.0
            if params_dict["g1_checkpoint_passed"]:
                out[ok & (t < g1)] = 0.0
                out[ok & (t >= g1) & (t < g1 + s)] = 1.0
            if params_dict["g2_checkpoint_passed"]:
                out[ok & (t >= g1 + s) & (t < g1 + s + g2)] = 2.0
            if params_dict["spindle_checkpoint_passed"]:
                out[ok & (t >= g1 + s + g2)] = 3.0
            return out
        except (TypeError, ValueError, KeyError):
            return out

    def regime_node(self, p: dict) -> dict:
        total = sum(p[k] for k in ("g1_hours", "s_hours", "g2_hours", "m_hours"))
        return {"id": "homo.cellesyklus", "synlighet": self.SYNLIGHET,
                "phase": "regime_engine", "regime": {"name": "The cell cycle",
                "validity": f"t in [0, {total}] hours; NaN outside; G0 at checkpoint stop",
                "law_form": "G1 -> S -> G2 -> M -> G1 with the G1/S, G2/M and spindle checkpoints"},
                "measure": {"target": "cell phase", "instrument": "flow cytometry/FUCCI"},
                "emergence": {"loop": "growth -> replication -> checkpoint -> division", "properties": ["G0", "checkpoint"]}}
