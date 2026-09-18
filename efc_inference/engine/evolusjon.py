"""Calculable population-genetic regimes, with explicit limits.

This is not a complete evolution simulator. It does NOT model speciation,
macroevolution, mutation, migration, linkage, epistasis, changing fitness,
or ecological/population structure. Those claims would not be calculable from
this small parameter set and are deliberately left out.
"""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class EvolusjonEngine(EFCEngine):
    """Calculable population genetics; does not model speciation or macroevolution."""
    REQUIRED_PARAMS = ["selection_coefficient", "population_size"]
    SYNLIGHET = "offentlig"
    @property
    def name(self): return "homo.evolusjon"
    def validate_params(self, params_dict):
        try: return (super().validate_params(params_dict) and params_dict["population_size"] > 0 and abs(params_dict["selection_coefficient"]) <= 1)
        except (TypeError, ValueError): return False
    def hardy_weinberg(self, p):
        p=float(p); return np.array([p*p, 2*p*(1-p), (1-p)*(1-p)]) if 0 <= p <= 1 else np.full(3,np.nan)
    def selection_coefficient(self, baseline_fitness, selected_fitness):
        a,b=float(baseline_fitness),float(selected_fitness)
        return np.nan if not np.isfinite(a+b) or a <= 0 or b < 0 else b/a-1.0
    def next_frequency(self, p, s):
        p=float(p); s=float(s); w=1+s
        if not (0 <= p <= 1 and w >= 0): return np.nan
        return p*w/(p*w + (1-p)) if p*w+(1-p)>0 else np.nan
    def fixation_time(self, p, population_size, s):
        p,n,s=float(p),float(population_size),float(s)
        if not (0 < p < 1 and n > 0 and np.isfinite(p+n+s)): return np.nan
        target=1.0-1.0/(2*n)
        if s == 0: return 4*n  # neutral diploid expectation, generations
        if s < 0: return np.nan
        return np.log((target/(1-target))/(p/(1-p)))/s
    def regime(self, p, s, drift_threshold=None):
        p,s=float(p),float(s)
        if not (0 <= p <= 1): return "utenfor_gyldighet"
        if p in (0.0,1.0): return "fiksert"
        if drift_threshold is not None and abs(s) < float(drift_threshold): return "drift"
        return "likevekt" if s == 0 else "seleksjon"
    def compute(self, params_dict, coordinates):
        x=np.asarray(coordinates,dtype=float); out=np.full(x.shape,np.nan)
        try: valid=self.validate_params(params_dict)
        except (TypeError,ValueError): valid=False
        if x.ndim != 1 or not valid: return out
        for i,p in enumerate(x):
            if 0 <= p <= 1: out[i]=self.next_frequency(p,params_dict["selection_coefficient"])
        return out
    def regime_node(self, params):
        return {"id":"homo.evolusjon","synlighet":self.SYNLIGHET,"perspektiv":"akademia","stipulasjoner":{"stipulert_av_oss":True},"epistemikk":{"sannhetsstatus":"stottet","evidensstatus":"replikert","konsensusstatus":"institusjonell","sosial_mekanisme":"population genetics","konsensus_er_ikke_sannhet":True},"regime":{"name":"Evolution","validity":"allele frequency p in [0,1]; equilibrium s=0, selection s!=0, drift when |s| is negligible against the population size, fixed p=0/1; NaN outside","law_form":"Hardy-Weinberg; p' = p(1+s)/(p(1+s)+(1-p)); t_fix via logistic selection or the 4N neutral expectation"},"phase":"regime_engine","measure":{"target":"allele frequency and genotype frequency","measurer":"population-genetic calculation","instrument":"EvolusjonEngine","proxy_chain":["p -> Hardy-Weinberg","fitness -> s -> p'","p,s,N -> fixation time"],"placement":"generations","compression":"population -> p"},"episenter":"the allele frequency","buffer":{"role":"population size and drift"},"ontology":{"assumes":["diploid Hardy-Weinberg population","constant selection within one generation"],"source":"standard population genetics (Hardy-Weinberg; Wright-Fisher)"},"observer":{"bandwidth":"p, s, N","awareness":"instrument_window","er_del_av_systemet":True},"emergence":{"loop":"reproduction -> frequency change -> the next generation","properties":["likevekt","seleksjon","drift","fiksasjon"]},"fractal":{"pattern":"frequency change across generations"},"coupling":{"local":"one allele","global":"homo.fluxus as the emergent framework hypothesis"},"maale_paradigme":{"koordinater":["fraksjon","tid"],"enheter":"fraction, generations","status":"avledet"},"nivaa":{"indeks":0,"forelder":None,"tidsskala":"generasjoner","lengdeskala":"populasjon"}}
