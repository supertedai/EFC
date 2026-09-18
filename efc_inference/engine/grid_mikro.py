"""GridMikroEngine — grid-mikrofysikken bak μ(g) (L-031).

Bygger på Mortens publiserte DOI-er — formlene er HENTET fra
papirene, ikke diktet opp:

- DOI 10.6084/m9.figshare.31942821 (Derivation of Γ(ρ)):
  Γ(ρ) = Γ0 · ρ/(ρ + ρcrit) — lineær ved lav tetthet, mettende ved
  høy, med ρcrit fra grid-mode-skalaen a0. Γ(ρ) (dynamisk) er skilt
  fra μBE(g) (statisk) — ingen dobbelttelling.
- DOI 10.6084/m9.figshare.31942800 (Density of States Deff(ρ)):
  Deff(ρ) ∝ √(ρ/ρcrit) med ρcrit = a0/(GN·lg) — boundary-mode-
  aktivering på en endelig gitterbrønn. Dette oppgraderer broen til
  Scenario B+: Γ(ρ) = Γ0·y/(1+y) med y = √(ρ/ρcrit).

To scenarioer implementeres og deklareres eksplisitt:
  scenario A  (31942821): Γ = Γ0·ρ/(ρ+ρcrit)
  scenario B+ (31942800): Γ = Γ0·y/(1+y), y = √(ρ/ρcrit)

Regimer (begge scenarioer):
  lav tetthet : Γ ~ lineær i ρ (eller ~√ρ i B+)
  mettet      : Γ → Γ0 når ρ >> ρcrit

Ærlighet: dette er EFCs mikrofysiske hypotese (Scenario B+ er
papirets egen oppgradering), IKKE konsensus-fysikk. L-031 står åpen
til prediksjonene fra papirenes forseglede tabeller er testet.
"""
from __future__ import annotations

import math

import numpy as np

from efc_inference.engine.base_engine import EFCEngine


class GridMikroEngine(EFCEngine):
    """Entropi-produksjonen Γ(ρ) og Deff(ρ) fra grid-modene."""

    REQUIRED_PARAMS = ["rho", "rho_crit", "Gamma0"]

    DOI = {
        "gamma_derivation": "10.6084/m9.figshare.31942821",
        "density_of_states": "10.6084/m9.figshare.31942800",
    }

    @property
    def name(self) -> str:
        return "grid_mikro"

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt tetthetsverdier, returner Γ(ρ) per punkt (scenario B+)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        koord = np.asarray(coordinates, dtype=float)
        ut = []
        for rho in koord:
            p = {**params_dict, "rho": float(rho)}
            ut.append(self.gamma(p, scenario="B_plus"))
        return np.array(ut)

    def deff(self, params: dict) -> float:
        """Deff(ρ) ∝ √(ρ/ρcrit) — boundary-mode-aktivering (31942800)."""
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        if rho < 0 or rho_crit <= 0:
            return float("nan")
        return float(math.sqrt(rho / rho_crit))

    def gamma(self, params: dict, scenario: str = "B_plus") -> float:
        """Γ(ρ) i scenario A eller B+.

        A:  Γ0·ρ/(ρ+ρcrit)                    (31942821)
        B+: Γ0·y/(1+y), y = √(ρ/ρcrit)        (31942800)
        """
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        G0 = float(params["Gamma0"])
        if rho < 0 or rho_crit <= 0:
            return float("nan")
        if scenario == "A":
            return float(G0 * rho / (rho + rho_crit))
        if scenario == "B_plus":
            y = math.sqrt(rho / rho_crit)
            return float(G0 * y / (1.0 + y))
        raise ValueError(f"ukjent scenario: {scenario}")

    def regime(self, params: dict) -> str:
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        if not (math.isfinite(rho) and math.isfinite(rho_crit)) \
                or rho < 0 or rho_crit <= 0:
            return "ugyldig"
        if rho < rho_crit:
            return "lav_tetthet"
        return "mettet"

    def regime_node(self, params: dict) -> dict:
        return {
            "id": "efc.grid_mikro_engine",
            "synlighet": self.SYNLIGHET,
            "regime": {
                "name": self.regime(params),
                "validity": ("lav_tetthet: Gamma ~ lineaer (A) eller ~ "
                             "sqrt-rho (B+); mettet: Gamma -> Gamma0 for "
                             "rho >> rho_crit. Predikerer IKKE observerte "
                             "rotasjonskurver alene — dette er broen, "
                             "ikke den ferdige responsen."),
            },
            "phase": self.regime(params),
            "measure": {
                "target": "Gamma(rho) og Deff(rho)",
                "measurer": "den teoretiske avledningen (von Neumann-"
                            "entropi over grid-modenes BE-okkuperings-"
                            "statistikk)",
                "instrument": "ingen direkte — mikrofysisk avledning, "
                              "modellavhengig",
                "proxy_chain": ["tetthet -> grid-mode-okkupering -> "
                                "entropi-produksjon — ren teori-kjede"],
                "placement": "teorirom",
                "compression": "grid-mikrofysikken komprimeres til "
                               "y = sqrt(rho/rho_crit)",
            },
            "episenter": ("grid-rammen: rho_crit = a0/(GN lg) er en "
                          "lesning av tettheten i grid-modens skala — "
                          "ikke en direkte observabel"),
            "buffer": {
                "role": "grid-modene er bufferen — okkuperte moders "
                        "entropi lader opp med tettheten og metter",
                "note": "samme mettende buffer-form som batteriet og "
                        "hjemostasen — her pa gitter-skala",
            },
            "ontology": {
                "assumes": [
                    "grid-modene følger Bose-Einstein-okkuperings-"
                    "statistikk (31942821)",
                    "Deff(ρ) kommer fra boundary-mode-aktivering på en "
                    "endelig gitterbrønn (31942800)",
                    "Scenario B+ er EFCs mikrofysiske HYPOTESE — ikke "
                    "konsensus-fysikk; L-031 står åpen til papirenes "
                    "forseglede prediksjoner er testet",
                    "Gamma(rho) er DYNAMISK og skilles fra muBE(g) som "
                    "er statisk — dobbelttelling er eksplisitt "
                    "oppløst",
                ],
                "source": ("DOI 10.6084/m9.figshare.31942821 og "
                           "10.6084/m9.figshare.31942800 (Magnusson, "
                           "2026)"),
            },
            "observer": {
                "bandwidth": "ingen instrumentvindu — ren avledning; "
                             "det er et hull i seg selv at det ikke "
                             "finnes en direkte måling",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "tetthet -> mod-okkupering -> entropi-"
                        "produksjon -> effektiv gravitasjonsrespons — "
                        "loopen er papirets bro",
                "properties": ["linearitet ved lav tetthet",
                               "metning ved hoy tetthet"],
            },
            "fractal": {
                "pattern": "gitter-mode -> grid-bronn -> galakse-"
                           "respons: samme mettende form på hver skala",
                "note": "y = sqrt(rho/rho_crit) er den mikrofysiske "
                        "versjonen av buffer-metningen",
            },
            "coupling": {
                "local": "hver gitter-celle bidrar lokalt",
                "global": "Deff(ρ) aggregerer modene til den "
                          "gravitasjonelt aktive tettheten av tilstander",
                "empathy_note": "det usynligste laget bærer broen "
                                "mellom GR og QFT — og det er avledet, "
                                "ikke målt",
            },
            "perspektiv": "paradigme",
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "ingen",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vaar egen ramme — baeres av oss, "
                                     "ikke av feltet",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["masse", "rom", "energi"],
                "enheter": "rho_crit = a0/(GN lg)",
                "status": "avledet",
                "alternativer": ["konsensus-QFT uten grid-struktur"],
            },
            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": [("rho_crit = a0/(GN lg) — grensen mellom "
                              "lav og mettet er VÅR skala-definisjon")],
                "motor": "grid_mikro",
            },
            "analogi": {
                "avbildning": ("grid-moders metning -> batteriets "
                               "ladekurve / hjemostasens setpunkt"),
                "bryter_der": ("gitter-modene er en teoretisk "
                               "konstruksjon — batteriet er målt; "
                               "formen er lik, substratets status er "
                               "ikke"),
            },
            # Plataseringen eies av ATLASET (scripts/maintenance/efc_bro_konvensjon.py):
            # motoren kan ikke vite hvor i stigen dens node hoerer. Feltet maa
            # likevel staa her fordi RegimeNode krever det — testen binder dem.
            "nivaa": {
                "indeks": 3,
                "forelder": "efc.grid_mikrofysikk",
                "tidsskala": "gitter-skala",
                "lengdeskala": "lg (grid-lengden)",
            },
        }
