"""EFC Transient Engine — stjernedodens holding->release-motor (L-036).

Koder formen som ble funnet i recon-en av kosmos.transienter
(ALeRCE/ZTF-hendelseslaget): den kompakte kjernen er en buffer som HOLDER
saa lenge gravitasjonsbindingen baerer den, og som SLIPPER naar massen
krysser stabilitetsgrensen — kollaps, transient (supernova/GRB), rest.

Modellen er IDEALISERT (kollaps-buffer): bindingsenergien E = G*M^2/R
bygges med kjernemassen, og ved stabilitetsgrensen frigjores
bindingsenergien ved den LOKALE massen. Den PASTAAR ikke prediksjonskraft
for enkelthendelser — den regner formens observabler: holdetid, utlost
energi og lettkurvens form (rask stigning, eksponensiell hale).

Den fjerde instansen av formen som allerede er bygget for solens flares
(SolarFlareEngine), jordas skjelv (JordskjelvEngine) og nevronet
(homo.aksjonspotensial).

ATLAS-KOBLINGEN ER LANDET: noden efc.transient_engine staar i
schema/regime_nodes.jsonld med de tre ANALOGOUS_TO-endepunktene
(homo.aksjonspotensial, efc.solar_flare_engine, efc.jordskjelv_engine) —
samme monster som sol/jord/nevron. Vakten som ventet paa
kollisjonsrekkefolgen er byttet mot bro-testen
tests/test_holding_release_motorer.py::test_transient_atlas_node_bro_test,
som holder atlas-nodens regime (validity + law_form) IDENTISK med
regime_node() her — maskinelt, ikke prosa-likt.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class TransientEngine(EFCEngine):
    """Holding->release-motor for kollaps-bufferen i en kompakt kjerne (idealisert)."""

    REQUIRED_PARAMS = [
        "G",                  # m^3 kg^-1 s^-2 — gravitasjonskonstanten (inngang)
        "terskelmasse",       # kg — stabilitetsgrensen (Chandrasekhar-stil modellparameter)
        "radius",             # m — kjerneradius der bindingsenergien regnes
        "vekstrate",          # kg/s — massetilvekst (oppladningen)
        "stigningstid_dager",  # dager — rask stigning i lettkurven
        "haletid_dager",      # dager — eksponensiell hale
        "stigningseksponent",  # — formparameter for stigningen (alpha)
    ]

    @property
    def name(self) -> str:
        return "transient"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def bindingsenergi(self, params: dict, masse: np.ndarray) -> np.ndarray:
        """Gravitasjonsbindingen E = G * M^2 / R (J) — bufferens energi."""
        m = np.asarray(masse, dtype=float)
        return params["G"] * m ** 2 / params["radius"]

    def holdetid(self, params: dict) -> float:
        """Tid fra M=0 til stabilitetsgrensen ved konstant vekstrate (s)."""
        return float(params["terskelmasse"] / params["vekstrate"])

    def utlost_energi(self, params: dict) -> float:
        """Energien som frigjores VED stabilitetsgrensen (J).

        Dette er energien ved terskelen — ikke en enkelthendelses malte
        energi. compute() bruker den LOKALE massen (se docstringen der).
        """
        return float(self.bindingsenergi(
            params, np.array([params["terskelmasse"]]))[0])

    def lettkurve(self, params: dict, tider_dager: np.ndarray) -> np.ndarray:
        """Normalisert lettkurve-form (maks 1.0 ved stigningstid_dager).

        Formen er PARAMETRISERT, ikke avledet: en rask stigning
        (t/t_stig)^alpha fram til kneet, deretter en eksponensiell hale
        exp(-(t-t_stig)/t_hale). Kneet er SATT av stigningstid_dager —
        det er ikke detektert fra en serie, og formen hevder ingen
        regimeendring ut over den parametriserte maksimumsverdien.

        Tider i DAGER (parameterne heter _dager); negative eller ikke-
        endelige tider er utenfor vinduet og gir NaN.
        """
        t = np.asarray(tider_dager, dtype=float)
        t_stig = float(params["stigningstid_dager"])
        t_hale = float(params["haletid_dager"])
        alpha = float(params["stigningseksponent"])
        ut = np.full(t.shape, np.nan)
        gyldig = np.isfinite(t) & (t >= 0.0)
        stigning = gyldig & (t < t_stig)
        hale = gyldig & (t >= t_stig)
        ut[stigning] = (t[stigning] / t_stig) ** alpha
        ut[hale] = np.exp(-(t[hale] - t_stig) / t_hale)
        return ut

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Gitt kjernemasse (kg), returner frigjort energi (J).

        Holding: masse < terskelmasse -> kjernen holdes oppe, utlosning = 0.
        Release: masse >= terskelmasse -> bindingsenergien ved den LOKALE
        massen frigjores (idealisert: hele bufferen slippes). Konvensjonen
        er den samme som SolarFlareEngine.compute(): energien folger det
        lokale punktet, ikke den deklarerte terskelverdien.

        Ugyldig inngang (negativ eller ikke-endelig masse) er utenfor
        vinduet og gir NaN — aldri en gjetning.
        """
        masse = np.asarray(coordinates, dtype=float)
        ut = np.full(masse.shape, np.nan)
        ut[np.isfinite(masse) & (masse < 0.0)] = np.nan
        gyldig = np.isfinite(masse) & (masse >= 0.0)
        ut[gyldig] = 0.0
        kritisk = gyldig & (masse >= params_dict["terskelmasse"])
        ut[kritisk] = self.bindingsenergi(params_dict, masse[kritisk])
        return ut

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        terskelmasse = params["terskelmasse"]
        radius = params["radius"]
        vekstrate = params["vekstrate"]
        t_hold = self.holdetid(params)
        e_ut = self.utlost_energi(params)
        t_stig = params["stigningstid_dager"]
        t_hale = params["haletid_dager"]
        alpha = params["stigningseksponent"]
        validity = (
            "holding: masse < " + str(terskelmasse) + " kg — kjernen holdes "
            "oppe, ingen utlosning; release: masse >= " + str(terskelmasse)
            + " kg — bindingsenergien ved den LOKALE massen frigjores "
            "(energien ved terskelen er " + str(e_ut) + " J). IDEALISERT "
            "regime-modell (kollaps-buffer): hele bindingsenergien "
            "G*M^2/R slippes ved stabilitetsgrensen, med radius "
            + str(radius) + " m og vekstrate " + str(vekstrate) + " kg/s "
            "(holdetid " + str(t_hold) + " s). Ekte supernovaer fordeler "
            "energien mellom noeytrinoer, kinetisk energi og straaling, og "
            "bare en brakdel blir lys. Stabilitetsgrensen er en "
            "MODELLPARAMETER (Chandrasekhar-stil): den virkelige grensen "
            "avhenger av sammensetning, rotasjon og omgivelsene. "
            "Lettkurven er en PARAMETRISERT form — stigning over "
            + str(t_stig) + " dager med eksponent " + str(alpha)
            + ", deretter eksponensiell hale med tidsskala " + str(t_hale)
            + " dager; kneet er SATT av formen, ikke detektert fra en "
            "serie. Predikerer IKKE enkelthendelser."
        )
        law_form = (
            "E_bind = G*M^2/R; holdetid = terskelmasse / vekstrate; "
            "utlosning ved masse = terskelmasse; lettkurve: (t/t_stig)^alpha "
            "fram til kneet, exp(-(t-t_stig)/t_hale) etter"
        )
        return {
            "id": "efc.transient_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["E_bind = G*M^2/R — kollapsbufferen — terskelstyrt holding->release"],
            "motor": "transient"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vaar egen ramme — baeres av oss, ikke av feltet",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["masse", "rom", "tid", "energi"],
                "enheter": "motorspesifikke (SI)",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer"]
            },
            "nivaa": {
                "indeks": 2,
                "forelder": "efc.selv.paradigme_tid",
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Stjernedodens holding->release (kollaps-buffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "holdetid, utlost energi, lettkurvens form",
                "measurer": "analytisk kollaps-buffer-modell (G*M^2/R) + parametrisert lettkurve",
                "instrument": "TransientEngine (efc_inference/engine/transient.py)",
                "proxy_chain": [
                    "kjernemasse -> bindingsenergi (E = G*M^2/R)",
                    "bindingsenergi -> utlost energi ved stabilitetsgrensen",
                    "utlost energi + stignings-/haletid -> lettkurvens normaliserte form",
                ],
                "placement": "kollaps-bufferen i den kompakte kjernen — motoren regner ett masse-punkt om gangen",
                "compression": "masse + stabilitetsgrense + vekstrate + lettkurve-tider -> (t_hold, E_ut, form)",
            },
            "episenter": "stabilitetsgrensen: punktet der kjernen slipper det den har holdt — analogien til nevronets V_th, solens b_crit og forkastningens terskel er formens egen",
            "buffer": {
                "role": "kjernen er bufferen: massen bygges og holdes oppe til stabilitetsgrensen krysses",
                "note": "ANALOGI til homo.aksjonspotensial, solens magnetiske buffer og forkastningens spenningsoppbygging — holding->release, fire domener, ikke identitet.",
            },
            "ontology": {
                "assumes": [
                    "bindingsenergien skalerer som G*M^2/R",
                    "utlosning skjer naar massen krysser en stabilitetsgrense (idealisering: grensen er en modellparameter, og ekte kollaps avhenger ogsa av rotasjon og sammensetning)",
                    "lettkurvens form er parametrisert, ikke avledet av en stralingstransportmodell",
                ],
                "source": "kollaps-buffer-bildet (supernova/GRB som frigjoring av gravitasjonsbinding); Chandrasekhar-stil masse-grense som modellparameter; lettkurvens stigning/hale som formvalg; idealiseringene er motorens egne",
            },
            "observer": {
                "bandwidth": "motoren ser bare kjernemasse og en massetilvekst — ingen rotasjon, ingen metallisitet, ingen forloperstruktur; lettkurven ser den normaliserte formen, ikke spekteret eller en lysstyrkeskala",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "masse bygges -> stabilitetsgrensen krysses -> kollaps -> transient -> resten star igjen — stjernedodens syklus",
                "properties": ["t_hold", "E_ut", "lettkurve-form"],
            },
            "fractal": {
                "pattern": "holding->release: stjernedodens transient, solens flares, nevronets spike, forkastningens skjelv — samme form, fire domener (analogi)",
                "note": "ett monster, fire domener.",
            },
            "coupling": {
                "local": "en kjerne, en buffer",
                "global": "kosmos.transienter er et HENDELSESLAG — ALeRCE/ZTF-avlesninger av mange transientklassers overganger; denne motoren koder KOLLAPS-grenen (stjernedod: supernova/GRB), ikke hendelsesstrommen som helhet. RAMMEVERKETS PLASSERING: ANALOGOUS_TO homo.aksjonspotensial, efc.solar_flare_engine og efc.jordskjelv_engine — formens fjerde domene, ikke identitet.",
                "empathy_note": "stjernen holder og holder — til den ikke kan holde mer. Som alle buffere.",
            },
        }
