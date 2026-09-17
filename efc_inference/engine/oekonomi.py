"""EFC Oekonomi Engine — Minskys finansregimer (L-041).

Minskys finansielle ustabilitetshypotese er holding->release-formen
i finans: stabilitet avler tillit, tillit avler gjeld, og gjelden
driver systemet gjennom tre regimer — hedge (inntektene dekker gjeld
og renter), spekulativ (inntektene dekker rentene, gjelden må
rulles) og Ponzi (inntektene dekker ingen av delene — eiendeler må
selges). Krise er utløsningen: de stabile årene ER holdingen som
bygget bufferen.

Modellen er en IDEALISERT regime-klassifisering med en lineær
gjeldsgrad-drift i stabile perioder (Minsky-momentet:
«stabilitet er destabiliserende»). Den er IKKE en økonomisk
modell-konkurrent — økonomi er et eget fag med egen litteratur;
motoren koder bare formen.

Regimene (gjeldsgrad = gjeld / årlig inntekt):
    hedge:      inntektene dekker renter + avdrag
    spekulativ: inntektene dekker rentene, gjelden rulles
    ponzi:      inntektene dekker ingen av delene
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

REGIME_KODER = {"hedge": 0, "spekulativ": 1, "ponzi": 2}


class OekonomiEngine(EFCEngine):
    """Minskys finansregimer med gjeldsgrad-terskler (idealisert)."""

    REQUIRED_PARAMS = [
        "rente",              # 1/år — lånerenten
        "inntektsavkastning",  # 1/år — avkastningen på inntekten
        "gjeldsgrad_hedge",    # terskel: hedge -> spekulativ
        "gjeldsgrad_ponzi",    # terskel: spekulativ -> ponzi
    ]

    @property
    def name(self) -> str:
        return "oekonomi"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def regime(self, params: dict, gjeldsgrad: float) -> str:
        """Klassifiserer finansregimet fra gjeldsgraden."""
        if gjeldsgrad < params["gjeldsgrad_hedge"]:
            return "hedge"
        if gjeldsgrad < params["gjeldsgrad_ponzi"]:
            return "spekulativ"
        return "ponzi"

    def gjeldsgrad_drift(self, params: dict, gjeldsgrad: float,
                         stabile_aar: float) -> float:
        """Minsky-momentet: i stabile perioder vokser gjelden raskere
        enn inntekten — gjeldsgraden drifter oppover med (rente -
        inntektsavkastning + tillitsledd). Idealisert lineær drift."""
        # Idealisert: gjelden vokser med renten, inntekten med
        # avkastningen; i stabilitet løsnes kredittvilkårene og
        # driften forsterkes (tillitsleddet, fast idealisert 0.06/år
        # — større enn rente-minus-avkastningsgapet slik at
        # Minsky-momentet er positivt, slik hypotesen krever).
        tillitsledd = 0.06
        drift_rate = (params["rente"] - params["inntektsavkastning"]
                      + tillitsledd)
        if drift_rate <= 0:
            # Modellen forutsetter positiv drift; uten den er
            # Minsky-momentet udefinert — ærlig NaN, ikke stille
            # klipping til stillstand.
            return float("nan")
        return float(gjeldsgrad * (1.0 + drift_rate * stabile_aar))

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt gjeldsgrader, returner regime-koder (0=hedge,
        1=spekulativ, 2=ponzi)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        gg = np.asarray(coordinates, dtype=float)
        return np.array([REGIME_KODER[self.regime(params_dict, float(g))]
                         for g in gg])

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        validity = (
            "Minskys finansregimer: stabilitet avler tillit -> gjeld "
            "vokser -> hedge -> spekulativ -> ponzi -> krise. De "
            "stabile årene ER holdingen som bygger bufferen til "
            "utløsningen (Minsky-momentet: stabilitet er "
            "destabiliserende — her som målbar gjeldsgrad-drift). "
            "AVGRENSNING: Minsky er ÉN tradisjon blant flere i "
            "økonomifaget; modellen predikerer IKKE krisers tidspunkt "
            "eller forekomst — bare regimets kvalitative form. "
            "IDEALISERT regime-klassifisering med lineær drift — "
            "IKKE en økonomisk modell-konkurrent: ingen sektorer, "
            "ingen sentralbank, ingen politikk, ingen heterogene "
            "aktører."
        )
        law_form = ("hedge: inntekt dekker renter + avdrag; "
                    "spekulativ: inntekt dekker renter, gjeld rulles; "
                    "ponzi: inntekt dekker ingenting — eiendeler "
                    "selges. Gjeldsgrad-drift: gg(t+1) = gg(t) * "
                    "(1 + (r - g + tillit) * dt)")
        return {
            "id": "efc.oekonomi_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["drift_rate <= 0 -> NaN (ikke stille klipping) — ærlighetsgrense", "hedge/spekulativ/ponzi-grensene — Minsky-typologi — en tradisjon blant flere"],
            "motor": "oekonomi"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vaar egen ramme — baeres av oss, ikke av feltet",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["tid", "fraksjon"],
                "enheter": "motorspesifikke (SI)",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer"]
            },
            "nivaa": {
                "indeks": 2,
                "forelder": "homo.fluxus",
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Minskys finansregimer — stabilitet som holding",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "finansregime (hedge/spekulativ/ponzi), gjeldsgrad-drift",
                "measurer": "terskel-klassifisering + lineær drift",
                "instrument": "OekonomiEngine (efc_inference/engine/oekonomi.py)",
                "proxy_chain": [
                    "gjeldsgrad -> regime (to terskler)",
                    "stabile år -> gjeldsgrad-drift (Minsky-momentet)",
                ],
                "placement": "ett gjeldsgrad-punkt om gangen i det idealiserte regimet",
                "compression": "(gjeldsgrad, stabilitetsvarighet) -> (regime, drift)",
            },
            "episenter": "ponzi-terskelen: punktet der systemet ikke lenger kan rulle — finansens regimeskifte fra holding til release",
            "buffer": {
                "role": "de stabile årene er bufferen: tilliten bygges opp og gjelden akkumuleres — helt til bufferen er full og krisen utløses",
                "note": "ANALOGI til homeostase-bufferens metning (homo.homeostase_buffer) — ikke identitet: finanssystemet har ingen setpunkt-mekanisme, bare terskler.",
            },
            "ontology": {
                "assumes": [
                    "Minskys tre regimer beskriver finansens kvalitative tilstander",
                    "gjeldsgrad-driften er lineær og tillitsleddet konstant (idealisering)",
                ],
                "source": "Hyman Minsky, Financial Instability Hypothesis (1970-80-årene); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare gjeldsgrad og renter — ingen sektorbalanser, ingen valutadynamikk",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "stabilitet -> tillit -> gjeld -> spekulasjon -> ponzi -> krise -> ny stabilitet — Minsky-syklusen",
                "properties": ["regime", "gjeldsgrad", "drift"],
            },
            "fractal": {
                "pattern": "stabilitet som bygger sin egen utløsning: finans, forkastning, solens flares (analogi)",
                "note": "ett mønster, tre domener — bufferen lades av det stabile selv.",
            },
            "coupling": {
                "local": "ett system, én gjeldsgrad",
                "global": "økonomien er homo.fluxus sin kollektive skala — ANALOGOUS_TO homo.homeostase_buffer",
                "empathy_note": "markedet vet ikke at stabiliteten er midlertidig — det bare bygger videre.",
            },
        }
