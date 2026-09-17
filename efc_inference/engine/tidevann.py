"""EFC Tidevann Engine — periodisk gravitasjonskopling (L-039).

Tidevann er den periodiske flyt-formen i gravitasjonskopling: månen
løfter og senker jordas hav i en uendelig lade/tøm-syklus, og
tidevannsbremsingen fase-låser systemet (månen viser alltid samme
side — holding i resonans).

Modellen er en IDEALISERT likevektsmodell: ingen hav-basseng-
dynamikk, ingen kystresonansforsterkning (Bay of Fundy osv.), ingen
energidissipasjonshistorikk. Tidevannshøyden er åpen-hav-skalaen.

Fysikken:
    Tidevannsakselerasjon: a_t ~ 2 G M_obj R / r^3
    Tidevannshøyde (åpent hav): h ~ a_t * R / g
    Roche-grensen (flytende): d = 2.44 R (rho_sentral/rho_objekt)^(1/3)
    Fase-låsing: rotasjonsperiode == omløpsperiode
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class TidevannEngine(EFCEngine):
    """Tidevannskopling med lade/tøm-syklus og fase-låsing (idealisert)."""

    REQUIRED_PARAMS = [
        "G",               # m^3/(kg s^2)
        "M_sentral",       # kg
        "m_objekt",        # kg
        "avstand",         # m — avstanden mellom legemene
        "radius_sentral",  # m — sentralkroppens radius
        "rho_sentral",     # kg/m^3 — sentralkroppens tetthet
        "rho_objekt",      # kg/m^3 — objektets tetthet
    ]

    @property
    def name(self) -> str:
        return "tidevann"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def tidevannsakselerasjon(self, params: dict) -> float:
        """a_t = 2 G m_obj R / r^3 — den differensielle gravitasjonen
        over sentralkroppens radius."""
        return float(2 * params["G"] * params["m_objekt"]
                     * params["radius_sentral"]
                     / params["avstand"] ** 3)

    def tidevannshoyde(self, params: dict) -> float:
        """Åpent-hav-skalaen: h ~ a_t * R / g med g = G M/R^2."""
        a_t = self.tidevannsakselerasjon(params)
        g = params["G"] * params["M_sentral"] / params["radius_sentral"] ** 2
        return float(a_t * params["radius_sentral"] / g)

    def roche_grense(self, params: dict) -> float:
        """d = 2.44 R (rho_sentral/rho_objekt)^(1/3) — terskelen der
        tidevannet bryter sammenhengen (idealisert flytende legeme)."""
        forhold = params["rho_sentral"] / params["rho_objekt"]
        return float(2.44 * params["radius_sentral"] * forhold ** (1 / 3))

    def er_faselaast(self, params: dict, rotasjonsperiode: float,
                     omlopsperiode: float) -> bool:
        """Fase-låsing: rotasjon synkronisert med omløp (1 % toleranse)."""
        return bool(abs(rotasjonsperiode - omlopsperiode)
                    / max(omlopsperiode, 1e-12) < 0.01)

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt avstander (m), returner tidevannsakselerasjonen (m/s^2)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        avstander = np.asarray(coordinates, dtype=float)
        ut = []
        for r in avstander:
            p = {**params_dict, "avstand": float(r)}
            if float(r) <= 0:
                ut.append(np.nan)
            else:
                ut.append(self.tidevannsakselerasjon(p))
        return np.array(ut)

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        h = self.tidevannshoyde(params)
        r_roche = self.roche_grense(params)
        validity = (
            "Tidevannsregime: periodisk lade/tøm-syklus — månen løfter "
            "og senker sentralkroppens hav hvert omløp; fase-låsing er "
            "tidevannsbremsingens holding (rotasjon synkronisert med "
            "omløp). IDEALISERT likevektsmodell: ingen hav-basseng-"
            "dynamikk, ingen kystresonansforsterkning, ingen "
            "dissipasjonshistorikk. Roche-grensen ("
            + f"{r_roche:.3e}" + " m) er terskelen der tidevannet "
            "bryter sammenhengen."
        )
        law_form = ("a_t = 2 G m_obj R / r^3; h ~ a_t R / g; "
                    "d_roche = 2.44 R (rho_s/rho_o)^(1/3); "
                    "fase-låsing: P_rot = P_omløp")
        return {
            "id": "efc.tidevann_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["Roche-grensen ~ 2.44 R — brytningsgrense — idealisert"],
            "motor": "tidevann"},
            "regime": {
                "name": "Tidevann — periodisk gravitasjonskopling",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "tidevannsakselerasjon, tidevannshøyde, Roche-grense, fase-låsingsstatus",
                "measurer": "analytisk tidevannsmodell",
                "instrument": "TidevannEngine (efc_inference/engine/tidevann.py)",
                "proxy_chain": [
                    "m_obj, r -> a_t (differensiell gravitasjon)",
                    "a_t -> h (åpent-hav-proxy)",
                    "perioder -> fase-låsingsstatus",
                ],
                "placement": "ett avstands-punkt om gangen i tolegeme-tidevannet",
                "compression": "(r, perioder) -> (a_t, h, Roche, låst?)",
            },
            "episenter": "Roche-grensen: punktet der den periodiske koplingen blir for sterk og sammenhengen brytes — tidevannets regimeskifte",
            "buffer": {
                "role": "havet er bufferen: det løftes og senkes i den periodiske syklusen uten å bryte — helt til Roche-grensen",
                "note": "ANALOGI til hjertets fyll-press-syklus og banens periodiske holding — ikke identitet: tidevannet er tvunget av en ytre periode, hjertet setter sin egen.",
            },
            "ontology": {
                "assumes": [
                    "likevekts-tidevann (ingen basseng-resonans)",
                    "Roche-grensen for flytende legeme (2.44-faktoren) med forenklet tetthetsforhold",
                ],
                "source": "standard tidevannsteori (differensiell gravitasjon, Roche); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare avstand og perioder — ingen bassenggeometri, ingen dissipasjonsmåling",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "omløp -> løft -> omløp -> senk — tidevannets uendelige loop",
                "properties": ["a_t", "h", "Roche-avstand", "låsingsstatus"],
            },
            "fractal": {
                "pattern": "periodisk lade/tøm-syklus: tidevann, hjertesyklus, ladesyklus (analogi)",
                "note": "ett mønster, tre domener.",
            },
            "coupling": {
                "local": "ett legemepar, én tidevannssyklus",
                "global": "tidevannet kobler månen og jorden — ANALOGOUS_TO homo.hjerte_syklus og efc.orbital_engine",
                "empathy_note": "havet spør ikke hvorfor det løftes — det bare følger, to ganger om dagen, for alltid.",
            },
        }
