"""EFC Orbital Engine — Kepler og baneregimer (L-037).

Banemekanikk som EFC-former: en bundet bane er HOLDING (negativ
spesifikk energi — objektet holdes i et regime), unbundet fly er
RELEASE (bindingen brytes), resonans er periodelåsing (fase-holding),
og Hill-sfæren er potensialbufferen som holder en måne mot sin
sentralkropp.

Modellen er IDEALISERT tolegeme-mekanikk (Kepler + vis-viva + Hill).
Den er IKKE en N-kroppsimulator og predikerer ikke perturbasjoner —
det står i selvbeskrivelsen. Formlene er de testbareste i hele
motorlaget: prediksjoner på kjente objekter med kjente tall.

EFC-rolle: baneregimene er den periodiske flyt-formen — ANALOGI til
hjertets fyll-press-syklus (periodisk holding->release) og
ladeprosessen, ikke identitet: banemekanikken er konservativ og
reversibel, hjertet er dissipativt.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class OrbitalEngine(EFCEngine):
    """Tolegeme banemekanikk med EFC-regime-klassifisering (idealisert)."""

    REQUIRED_PARAMS = [
        "G",          # m^3/(kg s^2) — gravitasjonskonstanten
        "M_sentral",  # kg — sentralkroppens masse
        "a",          # m — store halvakse
        "e",          # 1 — eksentrisitet
        "m_objekt",   # kg — objektets masse
    ]

    @property
    def name(self) -> str:
        return "orbital"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def _m_tot(self, params: dict) -> float:
        return params["M_sentral"] + params["m_objekt"]

    def periode(self, params: dict) -> float:
        """Keplers tredje lov: T = 2π sqrt(a^3 / (G M_tot))."""
        return float(2 * np.pi
                     * np.sqrt(params["a"] ** 3
                               / (params["G"] * self._m_tot(params))))

    def hastighet(self, params: dict, r: float) -> float:
        """Vis-viva: v = sqrt(GM(2/r - 1/a))."""
        return float(np.sqrt(params["G"] * self._m_tot(params)
                             * (2.0 / r - 1.0 / params["a"])))

    def spesifikk_energi(self, params: dict, r: float) -> float:
        """eps = v^2/2 - GM/r = -GM/(2a) (konstant i banen)."""
        return float(-params["G"] * self._m_tot(params)
                     / (2.0 * params["a"]))

    def hill_sfaere(self, params: dict) -> float:
        """r_H = a (m/(3M))^(1/3) — den TILNÆRMEDE innflytelses-/
        stabilitetsgrensen mot sentralkroppen (ikke en garanti om
        brutt binding — å krysse grensen gjør banen ustabil, ikke
        nødvendigvis ubundet)."""
        return float(params["a"] * (params["m_objekt"]
                                    / (3 * params["M_sentral"])) ** (1 / 3))

    def resonans_forhold(self, periode_1: float, periode_2: float) -> float:
        """Forholdet mellom to perioder (3:2-resonans gir 1.5)."""
        return float(periode_1 / periode_2)

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt (a, e)-par (N x 2), returner spesifikk energi (J/kg).

        a > 0: elliptisk bane — negativ eps = bundet = HOLDING.
        a < 0: hyperbolsk bane — positiv eps = ubundet = RELEASE
        (konvensjonen for hyperbel er negativ store halvakse; eps =
        -GM/(2a) gir da positiv verdi automatisk).
        a == 0 eller ugyldige parametre: NaN.
        """
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        m_tot = params_dict["M_sentral"] + params_dict["m_objekt"]
        ut = []
        for rad in koord:
            a = float(rad[0])
            if a == 0:
                ut.append(np.nan)
            else:
                ut.append(-params_dict["G"] * m_tot / (2.0 * a))
        return np.array(ut)

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        r_h = self.hill_sfaere(params)
        validity = (
            "Tolegeme Kepler-regime: bundet bane (eps < 0) er HOLDING — "
            "objektet holdes i regimet; ubundet fly (eps >= 0) er "
            "RELEASE — bindingen er brutt (hyperbolske baner: negativ "
            "a gir eps > 0). IDEALISERT: ingen perturbasjoner, ingen "
            "N-kropp, ingen atmosfærisk brems. Hill-sfæren ("
            + f"{r_h:.3e}" + " m) er den TILNÆRMEDE innflytelses-/"
            "stabilitetsgrensen mot sentralkroppen — å krysse den gjør "
            "banen ustabil, ikke nødvendigvis ubundet. Predikerer "
            "enkeltbaner, IKKE N-kroppsdynamikk."
        )
        law_form = ("Kepler: T = 2π sqrt(a^3/(GM)); vis-viva: "
                    "v^2 = GM(2/r - 1/a); eps = -GM/(2a); "
                    "r_H = a (m/(3M))^(1/3)")
        return {
            "id": "efc.orbital_engine",
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["epsilon = -GM/(2a): a<0 (hyperbolsk) gir release — energigrense", "Hill-sfaeren — tilnaermet stabilitetsgrense — grense"],
            "motor": "orbital"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vaar egen ramme — baeres av oss, ikke av feltet",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "masse", "tid"],
                "enheter": "motorspesifikke (SI)",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer"]
            },
            "regime": {
                "name": "Baneregimer — Kepler og bindingsterskler",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "periode, hastighet, spesifikk energi, Hill-sfære",
                "measurer": "analytisk tolegeme-mekanikk",
                "instrument": "OrbitalEngine (efc_inference/engine/orbital.py)",
                "proxy_chain": [
                    "a, e -> T (Kepler)",
                    "a, r -> v (vis-viva)",
                    "eps = -GM/(2a) -> holding/release",
                ],
                "placement": "ett (a, e)-punkt om gangen i tolegeme-regimet",
                "compression": "baneelementer -> (T, v, eps, r_H)",
            },
            "episenter": "bindingsterskelen eps = 0: punktet der en bane går fra holdt til sluppet — fangst og unnslipning møtes der",
            "buffer": {
                "role": "Hill-sfæren er banens TILNÆRMEDE stabilitetsbuffer: innenfor er sentralkroppens grep dominerende; utenfor blir banen ustabil (uten at bindingen nødvendigvis brytes)",
                "note": "ANALOGI til hjertets fyll-press-syklus (periodisk holding->release) — ikke identitet: banemekanikken er konservativ og reversibel, hjertet er dissipativt.",
            },
            "ontology": {
                "assumes": [
                    "tolegeme-approksimasjonen gjelder (sentral masse dominerer)",
                    "banene er Kepler-ellipser (ingen perturbasjoner)",
                ],
                "source": "Keplers lover, vis-viva, Hill-sfæren (standard himmelmekanikk); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare (a, e) — ingen resonans-kart, ingen perturbasjonshistorikk",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "bane -> periode -> fase -> neste omløp — banens uendelige loop",
                "properties": ["T", "v", "eps", "r_H"],
            },
            "fractal": {
                "pattern": "periodisk flyt med bindingsterskel: bane, hjertesyklus, ladesyklus (analogi)",
                "note": "ett mønster, tre domener.",
            },
            "coupling": {
                "local": "ett objekt, én bane",
                "global": "banene er planetsystemets og satellittenes regimer — ANALOGOUS_TO homo.hjerte_syklus",
                "empathy_note": "banen spør ikke — den bare går, holdt av ingenting annet enn energien.",
            },
        }
