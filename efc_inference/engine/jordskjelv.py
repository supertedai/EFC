"""EFC Jordskjelv Engine — jordas holding->release-motor (L-028).

Koder formen som ble funnet i recon-en av kosmos.jord (USGS-katalog):
forkastningen er en buffer som LADES langsomt (platene beveger seg) og
UTLOSES plutselig naar spenningen overstiger friksjonsterskelen —
elastic rebound.

Modellen er IDEALISERT (Burridge-Knopoff-stil lading): spenningen
akkumuleres med en lade-rate, og slippes ved terskelen med et
spenningsfall. Observablene er gjentakelsestid, seismisk moment og
moment-magnitude (Gutenberg-Richter-rammeverket). Den PASTAAR ikke
prediksjonskraft for enkeltskjelv — den regner formens observabler.

Moment-magnitude: Mw = (2/3)(log10 M0 - 9.1), M0 = mu * A * D med
slippet D = spenningsfall / mu (Kanamori).
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class JordskjelvEngine(EFCEngine):
    """Holding->release-motor for forkastningens spenningsbuffer (idealisert)."""

    REQUIRED_PARAMS = [
        "skjaermodul",   # Pa — mu, jordskorpens skjaermodul
        "lade_rate",     # Pa/aar — spenningsakkumulering
        "terskel",       # Pa — spenningsfall ved utlosning
        "areal",         # m^2 — bruddflate
    ]

    @property
    def name(self) -> str:
        return "jordskjelv"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def _gyldig_spenning(self, spenning: np.ndarray) -> np.ndarray:
        """Motorens fail-closed-kontrakt for spenning — EEN kilde.

        Gyldig spenning er ENDELIG og IKKE-NEGATIV: bufferen lades fra
        spenning = 0 og oppover, saa negativ spenning er utenfor
        modellens tilstandsrom. Skilt ut fordi kontrakten skal ha ett
        sted, ikke ett per kall. Samme form som
        TransientEngine._gyldig_masse() (L-036).
        """
        return np.isfinite(spenning) & (spenning >= 0.0)

    def gjentakelsestid(self, params: dict) -> float:
        """Tid mellom utlosninger ved konstant lade-rate (idealisert)."""
        return float(params["terskel"] / params["lade_rate"])

    def seismisk_moment(self, params: dict) -> float:
        """M0 = mu * A * D, med slippet D = terskel / mu (Kanamori)."""
        d = params["terskel"] / params["skjaermodul"]
        return float(params["skjaermodul"] * params["areal"] * d)

    def magnitude(self, params: dict) -> float:
        """Moment-magnitude Mw = (2/3)(log10 M0 - 9.1)."""
        m0 = self.seismisk_moment(params)
        if m0 <= 0:
            return float("nan")
        return float((2 / 3) * (np.log10(m0) - 9.1))

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Gitt spenning (Pa), returner sluppet moment (N*m).

        Holding: spenning < terskel -> bufferen holder, utlosning = 0.
        Release: spenning >= terskel -> momentet slippes (idealisert:
        M0 beregnes med det DEKLARERTE spenningsfallet, ikke det lokale).

        Ugyldig inngang (negativ eller ikke-endelig spenning) er utenfor
        vinduet og gir NaN — aldri en gjetning. For ble NaN, -1 og -inf
        rapportert som «holding» (0.0) og +inf som en utlosning.
        """
        spenning = np.asarray(coordinates, dtype=float)
        ut = np.full(spenning.shape, np.nan)
        gyldig = self._gyldig_spenning(spenning)
        ut[gyldig] = 0.0
        kritisk = gyldig & (spenning >= params_dict["terskel"])
        ut[kritisk] = self.seismisk_moment(params_dict)
        return ut

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        terskel = params["terskel"]
        t_rep = self.gjentakelsestid(params)
        mw = self.magnitude(params)
        validity = (
            "holding: spenning < " + str(terskel) + " Pa — forkastningen "
            "lades, ingen utlosning; release: spenning >= " + str(terskel)
            + " Pa — bufferen slippes. IDEALISERT regime-modell "
            "(Burridge-Knopoff-stil lading): utlosningen skjer ved en "
            "fast terskel og hele spenningsfallet slippes. Ugyldig "
            "inngang (negativ eller ikke-endelig spenning) er utenfor "
            "vinduet og gir NaN — aldri en gjetning: bufferen lades fra "
            "spenning = 0. Predikerer IKKE enkeltskjelv."
        )
        law_form = ("gjentakelsestid = terskel / lade_rate; "
                    "M0 = mu * A * (terskel/mu); "
                    "Mw = (2/3)(log10 M0 - 9.1)")
        return {
            "id": "efc.jordskjelv_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["elastic-rebound-antakelsen — idealisert modell — modellgrense, ikke prediktor"],
            "motor": "jordskjelv"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "Seismology carries the physics (Reid, Burridge-Knopoff) and has learned not to promise timing; our threshold model is our own — a false «prediction» would damage the field more than us.",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["energi", "rom", "tid"],
                "enheter": "motorspesifikke (SI)",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer"]
            },
            # Plataseringen eies av ATLASET (scripts/maintenance/efc_bro_konvensjon.py):
            # motoren kan ikke vite hvor i stigen dens node hoerer. Feltet maa
            # likevel staa her fordi RegimeNode krever det — testen binder dem.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Jordas holding->release (forkastningsbuffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "gjentakelsestid, seismisk moment, moment-magnitude",
                "measurer": "analytisk elastic-rebound-modell",
                "instrument": "JordskjelvEngine (efc_inference/engine/jordskjelv.py)",
                "proxy_chain": [
                    "lade-rate -> gjentakelsestid",
                    "spenningsfall -> slipp -> M0 -> Mw (Kanamori)",
                ],
                "placement": "forkastningens spenningsbuffer — motoren regner ett spennings-punkt om gangen",
                "compression": "lade-rate + terskel + areal -> (t_rep, M0, Mw)",
            },
            "episenter": "terskelen: punktet der forkastningen slipper det den har holdt — analogien til nevronets V_th og solens b_crit er formens egen",
            "buffer": {
                "role": "forkastningen er bufferen: spenningen lades og holdes til terskelen krysses",
                "note": "ANALOGI til homo.aksjonspotensial og solens magnetiske buffer — holding->release, tre domener, ikke identitet.",
            },
            "ontology": {
                "assumes": [
                    "elastic rebound gjelder: spenningen akkumuleres elastisk og slippes bratt",
                    "utlosning skjer ved en fast terskel (idealisering: ekte friksjon er hastighets- og tilstandsavhengig)",
                ],
                "source": "elastic rebound (Reid), Burridge-Knopoff-tradisjonen, Kanamoris Mw; idealiseringene er motorens egne",
            },
            "observer": {
                "bandwidth": "motoren ser bare spenning og lade-rate — ingen friksjonslov, ingen poretrykk",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "platedrift -> spenning bygges -> terskel -> utlosning -> spenning bygges pa nytt — skjelvsyklusen",
                "properties": ["t_rep", "M0", "Mw"],
            },
            "fractal": {
                "pattern": "holding->release: forkastningens skjelv, solens flares, nevronets spike — samme form, tre domener (analogi)",
                "note": "ett monster, tre domener.",
            },
            "coupling": {
                "local": "en forkastning, en buffer",
                "global": "skjelv er kosmos.jord sitt regimeskifte — ANALOGOUS_TO homo.aksjonspotensial og efc.solar_flare_engine",
                "empathy_note": "jorda holder og holder — til den slipper. Som alle buffere.",
            },
        }
