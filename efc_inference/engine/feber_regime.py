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
        return {"id":"homo.feber_regime","synlighet":self.SYNLIGHET,"perspektiv":"akademia","stipulasjoner":{"stipulert_av_oss":True},"epistemikk":{"sannhetsstatus":"stottet","evidensstatus":"replikert","konsensusstatus":"institusjonell","sosial_mekanisme":"fysiologi","konsensus_er_ikke_sannhet":True},"regime":{"name":"Feber","validity":"30-45 C; normoterm <= setpunkt+1 C; febril ved pyrogenisk setpunktsskifte; hyperterm >40 C eller ikke-pyrogen høy temperatur; NaN utenfor","law_form":"pyrogen -> hypothalamisk setpunktsskifte -> temperatur"},"phase":"regime_engine","measure":{"target":"temperatur mot setpunkt","measurer":"termometer og pyrogenstatus","instrument":"FeberRegimeEngine","proxy_chain":["pyrogen -> setpunkt","temperatur -> avvik"],"placement":"hypothalamisk regulering","compression":"temperatur + pyrogenstatus -> regime"},"episenter":"setpunktsskiftet","buffer":{"role":"regulering mot nytt setpunkt"},"ontology":{"assumes":["feber er pyrogen-drevet","hypertermi er ikke pyrogen-drevet og er ikke feber"],"source":"standard human thermoregulation references"},"observer":{"bandwidth":"temperatur og pyrogenisk status","awareness":"instrument_window","er_del_av_systemet":True},"emergence":{"loop":"pyrogen -> setpunkt -> varmeproduksjon","properties":["setpunkt_høy","temperatur"]},"fractal":{"pattern":"kontrollert regimeskifte"},"coupling":{"local":"temperaturregulering","global":"homeostase-bufferens regimeskifte"},"maale_paradigme":{"koordinater":["temperatur","temperatur"],"enheter":"C","status":"målt"},"nivaa":{"indeks":2,"forelder":"homo.homeostase_buffer","tidsskala":"timer","lengdeskala":"kroppen"}}
