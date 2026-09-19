"""Sleep/wake engine: two-process homeostatic pressure and stage."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine

class SovnVaakenEngine(EFCEngine):
    REQUIRED_PARAMS=["circadian_period","sleep_pressure_max","sleep_pressure_decay","wake_pressure_gain","sleep_threshold","rem_fraction","nrem_fraction"]
    SYNLIGHET="offentlig"
    @property
    def name(self): return "sovn_vaaken"
    def validate_params(self, params_dict):
        if not super().validate_params(params_dict): return False
        return params_dict["circadian_period"] > 0 and 0 <= params_dict["sleep_pressure_decay"] <= 1 and params_dict["wake_pressure_gain"] >= 0 and 0 < params_dict["sleep_threshold"] <= params_dict["sleep_pressure_max"] and 0 <= params_dict["rem_fraction"] < 1 and 0 < params_dict["nrem_fraction"] < 1
    def cycle_period_minutes(self, params): return 90.0
    def classify(self, params, hour):
        h=float(hour)
        if h < 0: return "utenfor"
        phase=h%params["circadian_period"]
        if phase < 8: return "NREM" if (phase%1.5) < 1.2 else "REM"
        return "vaaken"
    def homeostatic_pressure(self, params, hours):
        t=np.asarray(hours,dtype=float); out=np.full(t.shape,np.nan); ok=t>=0
        out[ok]=params["sleep_pressure_max"]*(1-np.exp(-params["wake_pressure_gain"]*t[ok]))
        return out
    def compute(self, params_dict, coordinates):
        c=np.asarray(coordinates,dtype=float)
        try: valid=self.validate_params(params_dict)
        except (TypeError,ValueError,KeyError): valid=False
        if c.ndim != 1 or not valid: return np.full(c.shape,np.nan)
        return self.homeostatic_pressure(params_dict,c)
    def regime_node(self, params):
        return {"id":"homo.sovn_vaaken","synlighet":self.SYNLIGHET,"phase":"regime_engine","regime":{"name":"Sleep/wake","regimes":["vaaken","NREM","REM"],"validity":"time >= 0; stage classification requires EEG/PSG in reality; the engine uses an explicit two-process proxy","law_form":"homeostatic pressure accumulates while awake and is drained in sleep; the SCN sets the timing"},"measure":{"target":"sleep stage and homeostatic pressure","measurer":"EEG/polysomnography","instrument":"clinical measurement"},"emergence":{"loop":"awake -> pressure -> sleep -> drainage"},"lagdeling":{"fysiologi":{"status":"akademia","kilde":"Borbely; Steriade"},"analogi":{"status":"paradigme","kilde":"EFC: regime shift"}}}
