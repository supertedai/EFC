"""Pyrogenic fever regimes; hyperthermia is explicitly different."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class FeberRegimeEngine(EFCEngine):
    REQUIRED_PARAMS = ["setpoint_c"]
    SYNLIGHET = "offentlig"
    @property
    def name(self): return "homo.feber_regime"
    def validate_params(self, params_dict):
        try: return super().validate_params(params_dict) and 35.0 <= params_dict["setpoint_c"] <= 39.0
        except (TypeError, ValueError): return False
    def classify(self, temperature_c, pyrogenic=False, setpoint_c=37.0):
        t=float(temperature_c)
        if not np.isfinite(t) or t < 30 or t > 45: return "utenfor_gyldighet"
        if t > 40.0 or (t > 38.0 and not pyrogenic): return "hyperterm"
        if pyrogenic and t > setpoint_c + 1.0: return "febril"
        return "normoterm"
    def compute(self, params_dict, coordinates):
        x=np.asarray(coordinates,dtype=float); out=np.full(x.shape,np.nan)
        try: valid=self.validate_params(params_dict)
        except (TypeError,ValueError): valid=False
        if x.ndim != 1 or not valid: return out
        ok=np.isfinite(x)&(x>=30)&(x<=45); out[ok]=x[ok]-float(params_dict["setpoint_c"]); return out
    def regime_node(self, params):
        return {"id":"homo.feber_regime","synlighet":self.SYNLIGHET,"perspektiv":"akademia","stipulasjoner":{"stipulert_av_oss":True},"epistemikk":{"sannhetsstatus":"stottet","evidensstatus":"replikert","konsensusstatus":"institusjonell","sosial_mekanisme":"physiology","konsensus_er_ikke_sannhet":True},"regime":{"name":"Fever","validity":"30-45 C; normothermia <= setpoint+1 C; febrile at a pyrogenic setpoint shift; hyperthermia >40 C or non-pyrogenic high temperature; NaN outside","law_form":"pyrogen -> hypothalamic setpoint shift -> temperature"},"phase":"regime_engine","measure":{"target":"temperature against setpoint","measurer":"thermometer and pyrogen status","instrument":"FeberRegimeEngine","proxy_chain":["pyrogen -> setpoint","temperature -> deviation"],"placement":"hypothalamic regulation","compression":"temperature + pyrogen status -> regime"},"episenter":"the setpoint shift","buffer":{"role":"regulation towards a new setpoint"},"ontology":{"assumes":["fever is pyrogen-driven","hyperthermia is not pyrogen-driven and is not fever"],"source":"standard human thermoregulation references"},"observer":{"bandwidth":"temperature and pyrogenic status","awareness":"instrument_window","er_del_av_systemet":True},"emergence":{"loop":"pyrogen -> setpoint -> heat production","properties":["setpoint_high","temperature"]},"fractal":{"pattern":"controlled regime shift"},"coupling":{"local":"temperature regulation","global":"the regime shift of the homeostasis buffer"},"maale_paradigme":{"koordinater":["temperatur","temperatur"],"enheter":"C","status":"measured"},"nivaa":{"indeks":2,"forelder":"homo.homeostase_buffer","tidsskala":"timer","lengdeskala":"kroppen"}}
