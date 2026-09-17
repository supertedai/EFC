"""EFC Klima Engine — strålingsbalanse og regimebrytere (L-040).

Klimaets 0D-energibalanse er EFC-formen i ren form på jorden: energi
inn (sol), buffer (havets varmekapasitet), terskeloverganger
(is-albedo-bryteren med hysterese mot snøballjord).

Modellen er en IDEALISERT 0D-energibalansemodell — den er IKKE en
klimamodell-konkurrent: ingen sirkulasjon, ingen skyer, ingen
romlig struktur. Det står i selvbeskrivelsen. Klimamodellering er
et eget fag med egen litteratur; motoren koder bare formen.

Fysikken:
    C dT/dt = (S/4)(1 - alpha) - eps sigma T^4
Likevekt: T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4).
Is-albedo-bryteren: albedo vokser når T faller under frysepunktet —
over en terskel finnes ingen varm likevekt (snøballjord, hysterese).
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class KlimaEngine(EFCEngine):
    """0D-energibalansemotor med buffer og regimebryter (idealisert)."""

    REQUIRED_PARAMS = [
        "solarkonstant",       # W/m^2 — S
        "albedo",              # 1 — alpha
        "emissivitet",         # 1 — eps (drivhuseffekt inkludert)
        "stefan_boltzmann",    # W/(m^2 K^4) — sigma
        "hav_varmekapasitet",  # J/(m^2 K) — C (blandingslaget)
    ]

    @property
    def name(self) -> str:
        return "klima"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def likevektstemperatur(self, params: dict) -> float:
        """T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4)."""
        s = params["solarkonstant"]
        inn = (s / 4.0) * (1.0 - params["albedo"])
        return float((inn / (params["emissivitet"]
                            * params["stefan_boltzmann"])) ** 0.25)

    def tidskonstant(self, params: dict) -> float:
        """Tau = C / (4 eps sigma T_eq^3) — bufferens treghet."""
        t_eq = self.likevektstemperatur(params)
        return float(params["hav_varmekapasitet"]
                     / (4 * params["emissivitet"]
                        * params["stefan_boltzmann"] * t_eq ** 3))

    def albedo_tilbakekobling(self, params: dict, delta_t: float) -> float:
        """Is-albedo-tilbakekoblingen: kaldere -> mer is -> høyere
        albedo. Forsterkningsfaktoren for en temperaturforstyrrelse
        (positiv tilbakekobling > 1)."""
        # Idealisert: albedo stiger lineært med fall under 0 °C med
        # stigningskoeffisient 0.005 K^-1 (størrelsesorden fra
        # is-utbredelse).
        stigning = 0.005
        d_alpha = stigning * (-delta_t) if delta_t < 0 else 0.0
        if d_alpha <= 0:
            return 1.0
        # T_eq-følsomhet for albedo: dT_eq/d_alpha = -T_eq/(4(1-alpha))
        t_eq = self.likevektstemperatur(params)
        følsomhet = t_eq / (4 * (1 - params["albedo"]))
        forsterkning = 1.0 / (1.0 - følsomhet * stigning)
        return float(forsterkning)

    def har_varm_likevekt(self, params: dict, tilstand: str = "varm") -> bool:
        """Varm likevekt finnes når T_eq > 273.15 K — med TILSTANDS-
        avhengige terskler (hysterese): fra «varm» faller systemet
        først når albedoen krysser alpha_fall (der T_eq = 273.15 K);
        fra «snøball» returnerer det først når albedoen krysser
        alpha_retur (< alpha_fall — snøballjordens reflektans
        stabiliserer den, idealisert hysteresebredde)."""
        alpha_fall = self._alpha_ved_frysepunkt(params)
        alpha_retur = params.get("alpha_retur", 0.35)
        if tilstand == "snøball":
            return bool(params["albedo"] < alpha_retur)
        return bool(params["albedo"] <= alpha_fall)

    def _alpha_ved_frysepunkt(self, params: dict) -> float:
        """Albedoen der T_eq krysser 273.15 K:
        alpha = 1 - 4 eps sigma T^4 / S."""
        t = 273.15
        utstraaling = 4 * params["emissivitet"] * params["stefan_boltzmann"] * t ** 4
        return float(1.0 - utstraaling / params["solarkonstant"])

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt albedo-verdier, returner T_eq (K) av den
        STRÅLINGSmessige likevekten — NaN der likevekten ligger under
        frysepunktet (ingen VARM likevekt finnes der)."""
        alb = np.asarray(coordinates, dtype=float)
        ut = []
        for a in alb:
            p = {**params_dict, "albedo": float(a)}
            t_eq = self.likevektstemperatur(p)
            ut.append(t_eq if t_eq > 273.15 else np.nan)
        return np.array(ut)

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        t_eq = self.likevektstemperatur(params)
        tau_aar = self.tidskonstant(params) / (365.25 * 86400)
        validity = (
            "0D-energibalanseregime: energi inn (sol) -> buffer (hav, "
            f"tau ~ {tau_aar:.0f} år) -> ut (emisjon). Is-albedo-bryteren "
            "er regimeovergangen MED TILSTANDSAVHENGIGE terskler "
            "(hysterese): fra «varm» faller systemet ved alpha_fall, "
            "fra «snøball» returnerer det først ved alpha_retur "
            "(< alpha_fall — snøballens reflektans stabiliserer den, "
            "idealisert bredde). IDEALISERT 0D-modell — IKKE en "
            "klimamodell-konkurrent: ingen sirkulasjon, ingen skyer, "
            "ingen romlig struktur."
        )
        law_form = ("C dT/dt = (S/4)(1-alpha) - eps sigma T^4; "
                    "T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4); "
                    "tau = C/(4 eps sigma T_eq^3)")
        return {
            "id": "efc.klima_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["alpha_fall ~ 0.4341 vs alpha_retur = 0.35 — hysterese-terskler — tilstandsavhengige albedoer", "straalingslikevekt under frysepunktet -> NaN — modellgrense"],
            "motor": "klima"},
            "regime": {
                "name": "Klimaets strålingsbalanse og regimebrytere",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "likevektstemperatur, tidskonstant, regimebryter",
                "measurer": "analytisk 0D-energibalanse",
                "instrument": "KlimaEngine (efc_inference/engine/klima.py)",
                "proxy_chain": [
                    "solarkonstant + albedo -> innstråling",
                    "eps sigma T^4 -> utstråling",
                    "C -> bufferens treghet",
                ],
                "placement": "jordas energibalanse — ett globalt punkt om gangen",
                "compression": "strålingsforstyrrelser -> (T_eq, tau, bryterstatus)",
            },
            "episenter": "is-albedo-terskelen: der den varme likevekten forsvinner — klimaets regimeskifte",
            "buffer": {
                "role": "havets varmekapasitet er bufferen: den demper og forsinker alle forstyrrelser — den brede bufferlogikken i global skala",
                "note": "ANALOGI til homeostase-bufferens setpunkt-holding — ikke identitet: klimaet har ingen setpunkt-mekanisme, bare tiltrekningsbassenger (som økologien).",
            },
            "ontology": {
                "assumes": [
                    "0D-approksimasjonen gjelder (globalt gjennomsnitt)",
                    "is-albedo-bryteren er idealisert (lineær stigning under 0 °C)",
                ],
                "source": "standard 0D-energibalansemodell (Budyko-Sellers-tradisjonen); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare globale gjennomsnitt — ingen regional dynamikk",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "forstyrrelse -> buffer demper -> ny likevekt -> (eller) bryter -> nytt regime — klimaets loop",
                "properties": ["T_eq", "tau", "bryterstatus"],
            },
            "fractal": {
                "pattern": "buffer + terskelbryter: klima, homeostase, økologi (analogi)",
                "note": "ett mønster, tre domener.",
            },
            "coupling": {
                "local": "ett globalt punkt",
                "global": "klimaet er homo.fluxus sin ytre tilstandsbærer — ANALOGOUS_TO homo.okologi og homo.homeostase_buffer",
                "empathy_note": "klimaet holder — til terskelen er krysset. Som alle buffere.",
            },
        }
