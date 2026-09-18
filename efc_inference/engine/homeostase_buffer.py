"""Measured physiological homeostasis bands and buffer regimes."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class HomeostaseBufferEngine(EFCEngine):
    REQUIRED_PARAMS = []
    SYNLIGHET = "offentlig"
    TEMP = (36.5, 37.5); GLUCOSE = (4.0, 7.0); PH = (7.35, 7.45)

    @property
    def name(self): return "homo.homeostase_buffer"

    def validate_params(self, params_dict): return isinstance(params_dict, dict)

    def classify_state(self, temperature_c, glucose_mmol_l, ph):
        vals = np.array([temperature_c, glucose_mmol_l, ph], dtype=float)
        if not np.all(np.isfinite(vals)): return "utenfor_gyldighet"
        normal = (self.TEMP[0] <= vals[0] <= self.TEMP[1] and self.GLUCOSE[0] <= vals[1] <= self.GLUCOSE[1] and self.PH[0] <= vals[2] <= self.PH[1])
        if normal: return "normalt"
        deviations = sum([not self.TEMP[0] <= vals[0] <= self.TEMP[1], not self.GLUCOSE[0] <= vals[1] <= self.GLUCOSE[1], not self.PH[0] <= vals[2] <= self.PH[1]])
        compensated = (35.0 <= vals[0] <= 40.0 and 2.0 <= vals[1] <= 12.0 and 7.0 <= vals[2] <= 7.8)
        return "kompensert" if compensated and deviations == 1 else "dekompensert"

    def compute(self, params_dict, coordinates):
        x = np.asarray(coordinates, dtype=float); out = np.full(x.shape[:-1] if x.ndim else x.shape, np.nan)
        if x.ndim != 2 or x.shape[1] != 3: return np.full(x.shape, np.nan)
        for i, row in enumerate(x):
            in_domain = (35.0 <= row[0] <= 40.0 and 2.0 <= row[1] <= 12.0 and 7.0 <= row[2] <= 7.8)
            if in_domain and self.classify_state(*row) != "utenfor_gyldighet":
                out[i] = np.linalg.norm([(row[0]-37.0)/0.5, (row[1]-5.5)/1.5, (row[2]-7.40)/0.05])
        return out

    def regime_node(self, params):
        return {"id":"homo.homeostase_buffer","synlighet":self.SYNLIGHET,"perspektiv":"akademia","stipulasjoner":{"stipulert_av_oss":True},"epistemikk":{"sannhetsstatus":"stottet","evidensstatus":"replikert","konsensusstatus":"institusjonell","sosial_mekanisme":"fysiologisk litteratur","konsensus_er_ikke_sannhet":True},"regime":{"name":"Homeostase-bufferen","validity":"normalt: 36.5-37.5 C, 4-7 mmol/L, pH 7.35-7.45; kompensert: 35-40 C, 2-12 mmol/L, pH 7.0-7.8; ellers dekompensert; utenfor NaN","law_form":"forstyrrelse -> negativ tilbakekobling -> stabilitet"},"phase":"regime_engine","measure":{"target":"avvik fra setpunkt","measurer":"fysiologiske målinger","instrument":"HomeostaseBufferEngine","proxy_chain":["temperatur, glukose, pH -> avvik"],"placement":"kroppens reguleringssløyfer","compression":"tre målevariabler -> avviksnorm"},"episenter":"referansebåndet","buffer":{"role":"negativ tilbakekobling"},"ontology":{"assumes":["måleverdiene er fysiologiske referanser"],"source":"standard human physiology references"},"observer":{"bandwidth":"temperatur, glukose, pH","awareness":"instrument_window","er_del_av_systemet":True},"emergence":{"loop":"forstyrrelse -> kompensasjon -> stabilitet","properties":["setpunkt","kapasitet"]},"fractal":{"pattern":"dempe endring"},"coupling":{"local":"per regulert variabel","global":"homo.fluxus sin stabilitetsbasis"},"maale_paradigme":{"koordinater":["temperatur","fraksjon","ingen"],"enheter":"C, mmol/L, pH","status":"målt"},"nivaa":{"indeks":1,"forelder":"homo.fluxus","tidsskala":"min-h","lengdeskala":"kroppen"}}
