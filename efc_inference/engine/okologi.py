"""Ecology engine: logistic growth and Lotka-Volterra periods."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine

class OkologiEngine(EFCEngine):
    REQUIRED_PARAMS=["growth_rate","carrying_capacity","initial_population","prey_growth_rate","predation_rate","predator_growth_rate","predator_death_rate"]
    SYNLIGHET="offentlig"
    @property
    def name(self): return "okologi"
    def validate_params(self, params_dict):
        if not super().validate_params(params_dict): return False
        return params_dict["growth_rate"] >= 0 and params_dict["carrying_capacity"] > 0 and params_dict["initial_population"] >= 0 and all(params_dict[k] > 0 for k in ("prey_growth_rate","predation_rate","predator_growth_rate","predator_death_rate"))
    def logistic_population(self,p,time):
        t=np.asarray(time,dtype=float); out=np.full(t.shape,np.nan); ok=t>=0
        r,K,N0=p["growth_rate"],p["carrying_capacity"],p["initial_population"]
        out[ok]=K/(1+(K-N0)/N0*np.exp(-r*t[ok])) if N0 else 0.0
        return out
    def lotka_volterra_period(self,p): return 2*np.pi/np.sqrt(p["prey_growth_rate"]*p["predator_death_rate"])
    def classify(self,p,population,time=0.0):
        n=float(population)
        if n < 0: return "utenfor"
        K=p["carrying_capacity"]
        if n == 0: return "kollaps"
        if n < 0.8*K: return "vekst"
        if n <= 1.2*K: return "metning"
        return "oscillasjon"
    def compute(self,params_dict,coordinates):
        c=np.asarray(coordinates,dtype=float)
        try: valid=self.validate_params(params_dict)
        except (TypeError,ValueError,KeyError): valid=False
        if c.ndim != 1 or not valid: return np.full(c.shape,np.nan)
        return self.logistic_population(params_dict,c)
    def regime_node(self,params):
        return {"id":"homo.okologi","synlighet":self.SYNLIGHET,"phase":"regime_engine","regime":{"name":"Ecosystem regimes","regimes":["vekst","metning","kollaps","oscillasjon"],"validity":"time >= 0 for logistic growth; the Lotka-Volterra period holds only for positive coefficients and idealized closed systems","law_form":"logistic growth with a carrying capacity; Lotka-Volterra for predator-prey"},"measure":{"target":"population and carrying capacity","measurer":"field measurements/time series","instrument":"ecological monitoring"},"emergence":{"loop":"growth -> resource limitation -> stability or collapse"},"lagdeling":{"fysiologi":{"status":"akademia","kilde":"Scheffer, regime-shift ecology"},"analogi":{"status":"paradigme","kilde":"EFC: alternative regimes"}}}
