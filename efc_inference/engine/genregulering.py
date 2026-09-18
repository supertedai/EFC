"""Physiological gene-regulation engine: Hill regulation with explicit regimes."""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine

class GenreguleringEngine(EFCEngine):
    REQUIRED_PARAMS = ["basal_expression", "max_expression", "activation_threshold", "repression_threshold", "hill_coefficient", "repression_coefficient"]
    SYNLIGHET = "offentlig"
    @property
    def name(self): return "genregulering"
    def validate_params(self, params_dict):
        if not super().validate_params(params_dict): return False
        return (params_dict["basal_expression"] >= 0 and params_dict["max_expression"] >= params_dict["basal_expression"] and
                0 < params_dict["activation_threshold"] < params_dict["repression_threshold"] and
                params_dict["hill_coefficient"] > 0 and params_dict["repression_coefficient"] > 0)
    def classify(self, params, tf):
        tf = float(tf)
        if tf < 0: return "utenfor"
        if tf == 0: return "av"
        if tf < params["activation_threshold"]: return "basalt"
        if tf <= params["repression_threshold"]: return "aktivert"
        return "repressivt"
    def expression(self, params, tf):
        tf = np.asarray(tf, dtype=float); out = np.full(tf.shape, np.nan)
        ok = tf >= 0
        a, h = params["activation_threshold"], params["hill_coefficient"]
        r, hr = params["repression_threshold"], params["repression_coefficient"]
        activation = np.divide(tf**h, a**h + tf**h, out=np.zeros_like(tf), where=ok)
        repression = np.divide(r**hr, r**hr + tf**hr, out=np.ones_like(tf), where=ok)
        out[ok] = params["basal_expression"] + (params["max_expression"]-params["basal_expression"])*activation[ok]*repression[ok]
        return out
    def compute(self, params_dict, coordinates):
        c = np.asarray(coordinates, dtype=float)
        try: valid = self.validate_params(params_dict)
        except (TypeError, ValueError, KeyError): valid = False
        if c.ndim != 1 or not valid: return np.full(c.shape, np.nan)
        return self.expression(params_dict, c)
    def regime_node(self, params):
        return {"id":"homo.genregulering", "synlighet":self.SYNLIGHET, "phase":"regime_engine", "regime":{"name":"Gene regulation", "regimes":["av","basalt","aktivert","repressivt"], "validity":"TF concentration >= 0; off at 0, basal below the activation threshold, activated between the thresholds, repressive above the threshold", "law_form":"Hill kinetics with negative feedback"}, "measure":{"target":"mRNA/protein expression", "measurer":"RNA-seq/ChIP-seq", "instrument":"sequencing"}, "emergence":{"loop":"signal -> TF -> expression -> protein -> feedback"}, "lagdeling":{"fysiologi":{"status":"akademia","kilde":"molecular biology (standard)"},"analogi":{"status":"paradigme","kilde":"EFC: regime shift"}}}
