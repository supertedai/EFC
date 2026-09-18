"""Homo Fluxus engine: an EFC calculation, not established physiology.

The atlas explicitly labels this layer ``lagdeling.analogi`` as
paradigme/hypotese/minoritet.  This motor calculates the proposed EFC flow
quantity; it does not measure or establish a biological consciousness.
"""
from __future__ import annotations
import numpy as np
from .base_engine import EFCEngine


class FluxusEngine(EFCEngine):
    REQUIRED_PARAMS = ["energy_density", "entropy_production", "tau_leak", "kappa"]
    SYNLIGHET = "offentlig"

    @property
    def name(self):
        return "homo.fluxus"

    def validate_params(self, params_dict):
        if not super().validate_params(params_dict):
            return False
        return (params_dict["energy_density"] > 0 and params_dict["entropy_production"] >= 0
                and params_dict["tau_leak"] > 0 and params_dict["kappa"] >= 0)

    def compute(self, params_dict, coordinates):
        x = np.asarray(coordinates, dtype=float)
        out = np.full(x.shape, np.nan)
        try:
            valid = self.validate_params(params_dict)
        except (TypeError, ValueError):
            valid = False
        if x.ndim != 1 or not valid:
            return out
        ok = np.isfinite(x) & (x > 0)
        sigma = max(float(params_dict["entropy_production"]), 0.0)
        eps = np.finfo(float).eps
        out[ok] = float(params_dict["kappa"]) * x[ok] / ((sigma + eps) * float(params_dict["tau_leak"]))
        return out

    def regime(self, params, energy_density):
        r = self.compute(params, np.array([energy_density]))[0]
        if not np.isfinite(r):
            return "utenfor_gyldighet"
        return "flytsubjekt" if r >= 1 / np.e else "flytobjekt"

    def regime_node(self, params):
        return {"id": "homo.fluxus", "synlighet": self.SYNLIGHET,
                "perspektiv": "paradigme",
                "epistemikk": {"sannhetsstatus": "hypotese", "evidensstatus": "proxy", "konsensusstatus": "minoritet", "sosial_mekanisme": "vår egen ramme", "konsensus_er_ikke_sannhet": True},
                "stipulasjoner": {"stipulert_av_oss": True},
                "regime": {"name": "Homo Fluxus", "validity": "energy_density > 0; R < 1/e flytobjekt, R >= 1/e flytsubjekt; NaN utenfor", "law_form": "R = kappa * rho_E / ((sigma+epsilon) * tau_leak)"},
                "phase": "regime_engine", "measure": {"target": "R", "measurer": "EFC-beregning", "instrument": "FluxusEngine", "proxy_chain": ["rho_E, sigma, tau_leak, kappa -> R"], "placement": "EFC-rammeverkets hypotese", "compression": "energiflyt -> R"},
                "episenter": "R-terskelen", "buffer": {"role": "tau_leak", "note": "EFC-analogi"}, "ontology": {"assumes": ["EFC-loven som hypotese"], "source": "Homo Fluxus v1/v2"},
                "observer": {"bandwidth": "EFC-parametre", "awareness": "hypothesis_open", "er_del_av_systemet": True}, "emergence": {"loop": "energiflyt -> R", "properties": ["R"]}, "fractal": {"pattern": "flyt -> persistens", "note": "analogi"}, "coupling": {"local": "EFC-beregning", "global": "homo.fluxus"}, "maale_paradigme": {"koordinater": ["energi"], "enheter": "EFC-enheter", "status": "avledet"}, "nivaa": {"indeks": 0, "forelder": None, "tidsskala": "motortid", "lengdeskala": "system"}}
