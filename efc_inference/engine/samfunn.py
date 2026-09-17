"""EFC Samfunn Engine — SIR-epidemiologi som flytmodell (L-042).

SIR-modellen er flytmodellen i ren form: mottagelige (S) -> smittede
(I) -> friske (R), med R0 = beta/gamma som terskelen — R0 > 1 er
UTBRUDD (release: reservoaret av mottagelige tømmes), R0 < 1 er
DEMPET (holding: smitten finner ikke nok mottagelige), og R0 = 1 er
selve TERSKELEN (regimeskiftet).

Modellen er en IDEALISERT homogen SIR: ingen aldersstruktur, ingen
nettverkstopologi, ingen atferd, ingen vaksinasjonsstrategier. Den
er IKKE en epidemiologisk modell-konkurrent — epidemiologi er et
eget fag med egen litteratur; motoren koder bare formen.

Fysikken (homogen SIR):
    dS/dt = -beta S I / N
    dI/dt =  beta S I / N - gamma I
    dR/dt =  gamma I
    R0 = beta / gamma
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class SamfunnEngine(EFCEngine):
    """Homogen SIR-flytmodell med R0-terskel (idealisert)."""

    REQUIRED_PARAMS = [
        "beta",   # 1/døgn — smitterate
        "gamma",  # 1/døgn — tilfriskningsrate
        "N",      # populasjonsstørrelse
    ]

    @property
    def name(self) -> str:
        return "samfunn"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def r0(self, params: dict) -> float:
        """R0 = beta / gamma — det grunnleggende reproduksjonstallet."""
        if params["gamma"] == 0:
            return float("inf")
        return float(params["beta"] / params["gamma"])

    def utbrudds_status(self, params: dict) -> str:
        """Regimeklassifisering ved terskelen R0 = 1."""
        r0 = self.r0(params)
        if r0 > 1:
            return "utbrudd"
        if r0 < 1:
            return "dempet"
        return "terskel"

    def sir_bane(self, params: dict, t: np.ndarray,
                 s0: float = 0.999, i0: float = 0.001):
        """SIR-banen som FRAKSJONER av N (s + i + r = 1 til enhver
        tid; populasjonstallene er S = N*s, I = N*i, R = N*r).

        Integreres med Euler på et fint grid — tilstrekkelig for
        formens kvalitative bane (dette er en form-modell, ikke en
        presisjonsintegrator; det står i docstringens ærlighet)."""
        s, i = s0, i0
        s_bane, i_bane, r_bane = [s], [i], [1 - s - i]
        dt = float(np.mean(np.diff(np.asarray(t, dtype=float))))
        for _ in range(len(np.atleast_1d(t)) - 1):
            ds = -params["beta"] * s * i
            di = params["beta"] * s * i - params["gamma"] * i
            s = max(0.0, s + ds * dt)
            i = max(0.0, i + di * dt)
            r = 1.0 - s - i
            s_bane.append(s)
            i_bane.append(i)
            r_bane.append(r)
        return (np.array(s_bane), np.array(i_bane), np.array(r_bane))

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt (beta, gamma)-par (N x 2), returner R0 per punkt."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        ut = []
        for rad in koord:
            p = {**params_dict, "beta": float(rad[0]),
                 "gamma": float(rad[1])}
            ut.append(self.r0(p))
        return np.array(ut)

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        r0 = self.r0(params)
        validity = (
            "SIR-flytregime: mottagelige -> smittede -> friske med "
            f"R0 = {r0:.2f} — terskelen R0 = 1 er regimeskiftet: over "
            "den er utbruddet (release, reservoaret tømmes), under er "
            "smitten dempet (holding). IDEALISERT homogen SIR: ingen "
            "aldersstruktur, ingen nettverk, ingen atferd, ingen "
            "vaksinasjon — IKKE en epidemiologisk modell-konkurrent. "
            "Banen integreres med Euler på fint grid — form-modell, "
            "ikke presisjonsintegrator."
        )
        law_form = ("dS/dt = -beta S I/N; dI/dt = beta S I/N - gamma I; "
                    "dR/dt = gamma I; R0 = beta/gamma")
        return {
            "id": "efc.samfunn_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["R0 = 1 — terskelen mellom tre regimer — regimebryter"],
            "motor": "samfunn"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vaar egen ramme — baeres av oss, ikke av feltet",
                "konsensus_er_ikke_sannhet": True
            },
            "regime": {
                "name": "SIR-epidemiologi — flyt med terskel",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "R0, utbruddsstatus, epidemi-banen",
                "measurer": "homogen SIR-integrasjon",
                "instrument": "SamfunnEngine (efc_inference/engine/samfunn.py)",
                "proxy_chain": [
                    "beta, gamma -> R0",
                    "R0 -> utbruddsstatus (terskel 1)",
                    "SIR-banen -> kurveformen",
                ],
                "placement": "ett (beta, gamma)-punkt om gangen i det homogene regimet",
                "compression": "(beta, gamma) -> (R0, status, bane)",
            },
            "episenter": "terskelen R0 = 1: punktet der en smitte dør eller tar av — epidemiens regimeskifte",
            "buffer": {
                "role": "reservoaret av mottagelige er bufferen: utbruddet tømmer den, og når den er tom, dør epidemien av seg selv",
                "note": "ANALOGI til immunologiens terskelstyrte forsvar (homo.immunologi) — ikke identitet: SIR er befolkningsflyt, immunresponsen er kroppslig forsvar.",
            },
            "ontology": {
                "assumes": [
                    "homogen blanding (alle møter alle likt)",
                    "konstante beta og gamma i vinduet",
                ],
                "source": "Kermack-McKendrick SIR (1927); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare aggregatene S, I, R — ingen individer, ingen nettverk",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "smitte -> utbrudd -> reservoaret tømmes -> flokkimmunitet -> smitten dør — epidemiens loop",
                "properties": ["R0", "toppunkt", "sluttstørrelse"],
            },
            "fractal": {
                "pattern": "flyt gjennom et begrenset reservoar med terskel: epidemi, utladning, kollaps (analogi)",
                "note": "ett mønster, tre domener.",
            },
            "coupling": {
                "local": "ett samfunn, én epidemi",
                "global": "helse-domenet er homo.fluxus sin kollektive skala — ANALOGOUS_TO homo.immunologi",
                "empathy_note": "epidemien vet ikke at den er en flyt — den bare går til reservoaret er tomt.",
            },
        }
