"""Okologisk motor: logistisk vekst og Lotka-Volterra-perioder."""
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
        return {"id":"homo.okologi","synlighet":self.SYNLIGHET,"phase":"regime_engine","regime":{"name":"Økosystemregimer","regimes":["vekst","metning","kollaps","oscillasjon"],"validity":"tid >= 0 for logistisk vekst; Lotka-Volterra-perioden gjelder bare positive koeffisienter og idealiserte lukkede systemer","law_form":"logistisk vekst med bæreevne; Lotka-Volterra for predator-byttedyr"},"measure":{"target":"populasjon og bæreevne","measurer":"feltmålinger/tidsrekker","instrument":"økologisk overvåking"},"emergence":{"loop":"vekst -> ressursbegrensning -> stabilitet eller kollaps"},"lagdeling":{"fysiologi":{"status":"akademia","kilde":"Scheffer, regime-shift-økologi"},"analogi":{"status":"paradigme","kilde":"EFC: alternative regimer"}}}
