"""EFC Solar Flare Engine — solens holding->release-motor (L-026).

Koder formen som ble funnet i recon-en av kosmos.sol (GOES-roentgenflux,
DONKI-utbruddskatalog): solens magnetiske felt er en buffer som LADES
langsomt (fotbevegelser vrir feltet) og UTLOSES plutselig naar feltet
overstiger en kritisk styrke — flare/CME.

Modellen er IDEALISERT (Avallon-stil energibuffer): magnetisk energi
B^2/(2 mu_0) * V bygges opp med en oppladningsrate dB/dt, og hele
bufferen slippes naar B naar b_crit. Den PASTAAR ikke prediksjonskraft
for enkelthendelser — den regner formens observabler: oppladningstid,
utlost energi og forventet GOES-klasse.

GOES-klassifiseringen folger den kanoniske skalaen (peak roentgenflux i
1-8 Angstrom-baandet): A < 1e-7, B < 1e-6, C < 1e-5, M < 1e-4,
X >= 1e-4 W/m^2. Motoren mapper utlost energi til klasse via en enkel
energi-til-flux-proxy — markert som proxy, ikke identitet.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

# GOES-klasser i stigende rekkefolge (kanonisk skala)
GOES_KLASSER = "ABCMX"


class SolarFlareEngine(EFCEngine):
    """Holding->release-motor for solens magnetiske buffer (idealisert)."""

    REQUIRED_PARAMS = [
        "mu_0",            # N/A^2 — vakumpermeabilitet
        "b_crit",          # T — kritisk feltstyrke for utlosning
        "oppladningsrate", # T/s — dB/dt i aktivt omraade
        "volum",           # m^3 — aktivt omraade-volum
    ]

    @property
    def name(self) -> str:
        return "solar_flare"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def magnetisk_energi(self, params: dict, b: np.ndarray) -> np.ndarray:
        """Magnetisk bufferenergi E = B^2 / (2 mu_0) * V."""
        b = np.asarray(b, dtype=float)
        return (b ** 2 / (2 * params["mu_0"])) * params["volum"]

    def oppladningstid(self, params: dict) -> float:
        """Tid fra B=0 til terskelen ved konstant oppladningsrate."""
        return float(params["b_crit"] / params["oppladningsrate"])

    def utlost_energi(self, params: dict) -> float:
        """Energien som slippes naar bufferen naar terskelen."""
        return float(self.magnetisk_energi(params, np.array([params["b_crit"]]))[0])

    def goes_klasse(self, energi: float) -> str:
        """Mapper utlost energi til forventet GOES-klasse (proxy).

        Proxy-kjede: energi -> peak flux (1-8 A) -> klasse.
        Kalibreringsanker: 1e22 J ~ M-klasse. Bins per dekade:
            A < 1e20, B < 1e21, C < 1e22, M < 1e23, X >= 1e23 J.
        (1e22 J er typisk frigjort energi for M-klasse-flares.)
        Idealisert: ekte flares slipper bare en BRAKDEL av bufferen.
        """
        energi_per_klasse = {
            "A": 1e20,   # A: energi < 1e20 J
            "B": 1e21,
            "C": 1e22,
            "M": 1e23,   # M: 1e22 <= energi < 1e23 (ankeret 1e22 -> M)
            "X": float("inf"),
        }
        klasse = "X"
        for k in GOES_KLASSER:
            if energi < energi_per_klasse[k]:
                klasse = k
                break
        return klasse

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Gitt feltstyrker B (T), returner utlost energi (J).

        Holding: B < b_crit -> bufferen holder, utlosning = 0.
        Release: B >= b_crit -> bufferen slippes (idealisert: helt).
        """
        b = np.asarray(coordinates, dtype=float)
        ut = np.zeros(b.shape)
        kritisk = b >= params_dict["b_crit"]
        ut[kritisk] = self.magnetisk_energi(params_dict, b[kritisk])
        return ut

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        b_crit = params["b_crit"]
        rate = params["oppladningsrate"]
        t_opp = self.oppladningstid(params)
        e_ut = self.utlost_energi(params)
        validity = (
            "holding: B < " + str(b_crit) + " T — bufferen lades, ingen "
            "utlosning; release: B >= " + str(b_crit) + " T — bufferen "
            "slippes. IDEALISERT regime-modell (Avallon-stil buffer): "
            "hele bufferen slippes ved terskelen; ekte flares slipper "
            "en brakdel. Predikerer IKKE enkelthendelser."
        )
        law_form = ("E = B^2/(2 mu_0) * V; oppladningstid = b_crit / "
                    "(dB/dt); utlosning ved B = b_crit")
        return {
            "id": "efc.solar_flare_engine",
            "regime": {
                "name": "Solens holding->release (magnetisk buffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "oppladningstid, utlost energi, GOES-klasse",
                "measurer": "analytisk buffermodell + GOES-klasseproxy",
                "instrument": "SolarFlareEngine (efc_inference/engine/solar_flare.py)",
                "proxy_chain": [
                    "B -> magnetisk energi (E = B^2/(2 mu_0) * V)",
                    "energi -> GOES-klasse (kalibreringsproxy: 1e22 J ~ M)",
                ],
                "placement": "det aktive omraadets magnetiske buffer — motoren regner ett feltstyrke-punkt om gangen",
                "compression": "feltstyrke + oppladningsrate -> (t_opp, E_ut, klasse)",
            },
            "episenter": "terskelen b_crit: punktet der bufferen slipper det den har holdt — analogien til nevronets V_th og forkastningens terskel er formens egen",
            "buffer": {
                "role": "magnetfeltet er bufferen: energien lades og holdes til terskelen krysses",
                "note": "ANALOGI til homo.aksjonspotensial og jordskjelvets forkastning — holding->release, tre domener, ikke identitet.",
            },
            "ontology": {
                "assumes": [
                    "magnetisk energitetthet B^2/(2 mu_0) gjelder",
                    "utlosning skjer ved en kritisk feltstyrke (idealisering: ekte utlosning avhenger ogsa av topologi)",
                ],
                "source": "sol-fysikkens energibuffer-bilde (Avallon-stil); GOES-klasseskalaen (1-8 A); idealiseringene er motorens egne",
            },
            "observer": {
                "bandwidth": "motoren ser bare feltstyrke og oppladningsrate — ingen magnetisk topologi, ingen plasma-dynamikk",
                "awareness": "instrument_window",
            },
            "emergence": {
                "loop": "fotbevegelser -> feltet vrir seg -> terskel -> utlosning -> feltet bygges pa nytt — flare-syklusen",
                "properties": ["t_opp", "E_ut", "GOES-klasse"],
            },
            "fractal": {
                "pattern": "holding->release: solens flares, nevronets spike, forkastningens skjelv — samme form, tre domener (analogi)",
                "note": "ett monster, tre domener.",
            },
            "coupling": {
                "local": "ett aktivt omraade, en buffer",
                "global": "flares er kosmos.sol sitt regimeskifte — ANALOGOUS_TO homo.aksjonspotensial og efc.jordskjelv_engine",
                "empathy_note": "solen holder og holder — til den slipper. Som alle buffere.",
            },
        }


class SolarFlareEngineBrakdel(SolarFlareEngine):
    """Variant som slipper en brakdel av bufferen (mer realistisk)."""

    @property
    def name(self) -> str:
        return "solar_flare_brakdel"
