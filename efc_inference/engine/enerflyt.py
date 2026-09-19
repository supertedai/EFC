"""EnerFlytEngine — samfunnet som energiflyt (L-052).

Mortens prinsipp (f): hele samfunnet er et energiflyt-diagram i alle
akser. SIR-motoren modellerer epidemiologiens fraksjonsfluks; denne
modellerer ENERGI-fluksen:

    dS/dt = P - C - L

der P = produksjon, C = forbruk, L = tap, S = bufferen (lageret).

Regimene er bufferterskelens tre tilstander:
    overflod : P > C + L — bufferen fylles
    balanse  : P ~ C + L — bufferen står stille
    knapphet : C + L > P — bufferen tømmes; under terskelen er
               release-regimet (rasjonering/omfordeling)

ÆRLIGHETSKLAUSULER (review-disippel fra økonomi-/samfunns-motorene):
- Dette er ÉN akse av samfunnet. Penger, oppmerksomhet og tillit er
  andre valutaer med eksplisitt IKKE-konservering — de er ikke i
  denne modellen, og det sies eksplisitt.
- Motoren predikerer IKKE når kriser inntreffer — den sier når
  bufferen krysser terskelen i modellen. Samfunnets faktiske kriser
  har aktører, politikk og normer som ikke er i flytligningen.
- Produksjon og forbruk er idealiserte skalarer — virkelige samfunn
  har sektorer, nettverk og makt som fordeler fluksene.

Fraksjonsinvariant: regimet er invariant under per-kapita-skala —
samme flyt per person gir samme regime (skalaen er et valg, ikke en
fysikk-endring).
"""
from __future__ import annotations

import numpy as np

from efc_inference.engine.base_engine import EFCEngine


class EnerFlytEngine(EFCEngine):
    """Samfunnets energiflyt — buffer-balanse med tre regimer."""

    REQUIRED_PARAMS = [
        "produksjon",  # P — energi/tid
        "forbruk",     # C — energi/tid
        "buffer",      # S0 — startbeholdningen
    ]

    @property
    def name(self) -> str:
        return "enerflyt"

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt (produksjon, forbruk)-par, returner dS/dt per punkt."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        ut = []
        for rad in koord:
            p = {**params_dict, "produksjon": float(rad[0]),
                 "forbruk": float(rad[1])}
            ut.append(self.vurder(p)["dS_dt"])
        return np.array(ut)

    def vurder(self, params: dict) -> dict:
        """Returnerer flyt-vurderingen for gitte parametre.

        Buffer under terskelen med negativ drift gir buffer_etter =
        NaN (ikke stille klipping — mønsteret fra OekonomiEngine).
        """
        p = float(params["produksjon"])
        c = float(params["forbruk"])
        tap = float(params.get("tap", 0.0))
        s = float(params["buffer"])
        terskel = float(params.get("terskel", 0.0))

        drift = p - c - tap
        if drift == 0.0:
            regime = "balanse"
        elif drift > 0.0:
            regime = "overflod"
        else:
            regime = "knapphet"

        buffer_etter = s + drift
        if s == 0.0 and drift < 0.0:
            buffer_etter = float("nan")

        return {
            "regime": regime,
            "dS_dt": drift,
            "buffer_etter": buffer_etter,
            "under_terskel": buffer_etter < terskel,
        }

    def regime_node(self, params: dict) -> dict:
        u = self.vurder(params)
        return {
            "id": "efc.enerflyt_engine",
            "synlighet": self.SYNLIGHET,
            "regime": {
                "name": u["regime"],
                "validity": ("overflod: P > C + L — bufferen fylles; "
                             "balanse: P ~ C + L; knapphet: C + L > P — "
                             "bufferen toemmes og release-regimet er "
                             "rasjonering/omfordeling. Predikerer IKKE "
                             "naar krisen inntreffer — bare naer "
                             "bufferen krysser terskelen i modellen."),
            },
            "phase": u["regime"],
            "measure": {
                "target": "bufferen S og driften dS/dt = P - C - L",
                "measurer": "energistatistikk — produksjon, forbruk, "
                            "lager (samfunnsregnskap)",
                "instrument": "statistikkbyraaer og nettoperatoerer",
                "proxy_chain": ["registrert produksjon -> forbruk -> "
                                "bufferanslag — alle er regnskaps-"
                                "proxyer, ikke direkte maalinger"],
                "placement": "samfunnets eget regnskap",
                "compression": "hele samfunnet komprimeres til tre "
                               "tall per tidsenhet",
            },
            "episenter": ("energiregnskapets ramme: knapphet er en "
                          "lesning i P-C-L-rammen, ikke en egenskap "
                          "ved samfunnet i seg selv"),
            "buffer": {
                "role": "S er samfunnets energibuffer — holdingen som "
                        "absorberer ubalansen mellom produksjon og "
                        "forbruk",
                "note": "samme bufferlogikk som batteriet og "
                        "hjemostasen — pa samfunnsskala",
            },
            "ontology": {
                "assumes": [
                    "energi er EN akse av samfunnet — penger, "
                    "oppmerksomhet og tillit er andre valutaer med "
                    "eksplisitt IKKE-konservering og er ikke i modellen",
                    "produksjon og forbruk er idealiserte skalarer — "
                    "virkelige samfunn har sektorer, nettverk og makt",
                    "dS/dt = P - C - L er en idealisert "
                    "flytligning, ikke en sosial lov",
                ],
                "source": "energiregnskapets konservering; EFC "
                          "bufferlogikk (analogi til batteri og "
                          "hjemostase — ikke identitet)",
            },
            "observer": {
                "bandwidth": "samfunnets eget regnskap — bare det som "
                             "registreres og rapporteres; svart "
                             "økonomi og uregistrerte flukser er "
                             "usynlige for dette instrumentet",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "produksjon -> buffer -> forbruk -> "
                        "produksjonsinsentiver — loopen holder "
                        "samfunnets energisystem gaende",
                "properties": ["overflod", "balanse", "knapphet"],
            },
            "fractal": {
                "pattern": "celle -> kropp -> husholdning -> samfunn: "
                           "samme bufferbalanse pa hver skala",
                "note": "homeostase er den biologiske versjonen av "
                        "samme flytlogikk",
            },
            "coupling": {
                "local": "hver husholdning balanserer lokalt",
                "global": "samfunnets energibuffer er kollektivet — "
                          "knapphet kopler alle",
                "empathy_note": "knappheten rammer ikke likt — "
                                "modellen har ingen fordeling, og "
                                "det er et bevisst hull",
            },
            "perspektiv": "paradigme",
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "Conservation in the energy accounts is physics, carried by the statistics; the coupling to society's buffers is OUR analogy — budget and distribution questions have their own carriers and their own interests in politics.",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["energi", "tid", "fraksjon"],
                "enheter": "energi/tid, per-kapita-fraksjoner",
                "status": "proxy",
                "alternativer": ["penger, oppmerksomhet, tillit — "
                                 "ikke-konserverte valutaer utenfor "
                                 "modellen"],
            },
            # Plataseringen eies av ATLASET (scripts/maintenance/efc_bro_konvensjon.py):
            # motoren kan ikke vite hvor i stigen dens node hoerer. Feltet maa
            # likevel staa her fordi RegimeNode krever det — testen binder dem.
            "nivaa": {
                "indeks": 1,
                "forelder": "homo.fluxus",
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": [("terskelen er buffergrensen VI setter — "
                              "knapphet er vaar definisjon, ikke "
                              "naturens linje")],
                "motor": "enerflyt",
            },
            "analogi": {
                "avbildning": ("buffer -> batterilager/hjemostase, "
                               "knapphet -> utladning/feber, "
                               "produksjon -> lading/inntak"),
                "bryter_der": ("samfunnet er ikke en organisme: "
                               "ingen sentral regulator, fordelingen "
                               "er politisk, og aktorene har "
                               "intensjoner — flytligningen har "
                               "ingen av dem"),
            },
        }
