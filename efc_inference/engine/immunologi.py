"""Immune-response engine with an explicit exposure regime."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine

class ImmunologiEngine(EFCEngine):
    REQUIRED_PARAMS = ["antigen_threshold","exposure","peak_day","peak_titer","baseline_titer","decay_rate"]
    SYNLIGHET = "offentlig"
    @property
    def name(self): return "immunologi"
    def validate_params(self, params_dict):
        try:
            for name in self.REQUIRED_PARAMS:
                if name not in params_dict or name == "exposure": continue
                if not np.isfinite(params_dict[name]): return False
        except (TypeError, ValueError): return False
        p = params_dict
        return p.get("exposure") in ("primary","secondary") and p["peak_day"] > 0 and p["peak_titer"] >= p["baseline_titer"] >= 0 and p["decay_rate"] >= 0 and p["antigen_threshold"] >= 0
    def classify(self, p, day):
        day=float(day)
        if day < 0: return "utenfor"
        if p.get("tolerant", False): return "toleranse"
        if "antigen" in p and p["antigen"] <= p["antigen_threshold"]: return "usensibilisert"
        return "primaerrespons" if p["exposure"] == "primary" else "sekundaerrespons"
    def antibody_titer(self, p, day):
        d=np.asarray(day,dtype=float); out=np.full(d.shape,np.nan); ok=d>=0
        peak=p["peak_day"]; amp=p["peak_titer"]-p["baseline_titer"]
        out[ok]=p["baseline_titer"] + amp*np.exp(-p["decay_rate"]*(d[ok]-peak)**2)
        return out
    def compute(self, params_dict, coordinates):
        c=np.asarray(coordinates,dtype=float)
        try: valid=self.validate_params(params_dict)
        except (TypeError,ValueError,KeyError): valid=False
        if c.ndim != 1 or not valid: return np.full(c.shape,np.nan)
        return self.antibody_titer(params_dict,c)
    def regime_node(self, params):
        return {"id":"homo.immunologi","synlighet":self.SYNLIGHET,"phase":"regime_engine","regime":{"name":"The immune system","regimes":["usensibilisert","primaerrespons","sekundaerrespons","toleranse"],"validity":"days >= 0; activation requires antigen above threshold and context; the exposure type selects primary/secondary; tolerance is explicit","law_form":"clonal expansion and a time-dependent antibody titre"},"measure":{"target":"antibody titre","measurer":"ELISA","instrument":"immunological analysis"},"emergence":{"loop":"antigen -> activation -> response -> memory"},"lagdeling":{"fysiologi":{"status":"akademia","kilde":"Janeway; Matzinger"},"analogi":{"status":"paradigme","kilde":"EFC: threshold-governed buffer"}}}
