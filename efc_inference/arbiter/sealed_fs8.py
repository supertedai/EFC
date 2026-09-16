"""Forseglet fσ8-arbiter (trinn 12).

Den maskinelle dommeren mot EFCs forseglede prediksjon P2:

    fσ8(z=0.7) = 0.430 (EFC)  vs  0.449 (ΛCDM)

Forseglet 2026-04-14 under DOI 10.6084/m9.figshare.32013156
(«Sealed Blind Predictions for Growth-Rate Observables: EFC vs ΛCDM»),
og liggende som melding paa bussen (emne
kosmos.kosmologi.tilstand.efc-fs8, seq 5817, kilde efc-sealed-baseline).

Dommelogikken er treverdig og hver dom baerer regelen som felte den,
med kilde. Arbiteren feller ALDRI en dom på data den ikke har — uten
arbiter-målingen (DESI DR2 full-shape galakse-RSD fσ8(z~0.7)) sier
den VENTER og forteller hva som mangler.

Ærlighetsklausul: den forseglede prediksjonen hviler på μ<1 (B-kanalen
i perturbasjonslaget, «linear growth with entropy damping»). Motorlagets
growth-API (efc_inference.engine.growth) har per i dag mu=1 hardkodet —
bare bakgrunnskanalen (alpha_cosmo) er med. Arbiteren rapporterer dette
åpenlyst og påstår ikke at 0.430 er maskinelt reprodusert.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from efc_inference.engine.growth import EFCGrowth

FORSEGLET_DOI = "10.6084/m9.figshare.32013156"
FORSEGLET_DATO = "2026-04-14"
ARBITER_INSTRUMENT = "DESI DR2 full-shape RSD (galakse-RSD, z~0.7)"
PREDIKSJON_EFC = 0.430
PREDIKSJON_LCDM = 0.449


@dataclass(frozen=True)
class Maaling:
    fsigma8: float
    sigma: float
    z_eff: float
    kilde: str


class SealedFs8Arbiter:
    """Dommer mot den forseglede fσ8(z=0.7)-prediksjonen."""

    def __init__(self, growth: Optional[EFCGrowth] = None):
        self.growth = growth or EFCGrowth()

    # ------------------------------------------------------------------
    # Kriteriet (forseglet)
    # ------------------------------------------------------------------
    @staticmethod
    def kriterium() -> dict:
        return {
            "prediksjon_efc": PREDIKSJON_EFC,
            "prediksjon_lcdm": PREDIKSJON_LCDM,
            "arbiter_instrument": ARBITER_INSTRUMENT,
            "forseglet_dato": FORSEGLET_DATO,
            "forseglet_doi": FORSEGLET_DOI,
            "bekreftelse": ("DESI DR2 full-shape fsigma8(z~0.7) must fall "
                            "within ~1sigma of 0.430"),
            "falsifikasjon_a": ("Measured fσ8(z=0.7) > 0.449 at > 3σ — "
                                "consistent with ΛCDM at high significance "
                                "(P2 damage test)"),
            "falsifikasjon_b": ("falsified if result is consistent with "
                                "0.449 (ΛCDM) within <1σ or excludes 0.430 "
                                "at ≥2σ (P1, falsifiable_by)"),
        }

    # ------------------------------------------------------------------
    # Prediksjonene — parameter-avledet fra motoren, ikke hardkodet
    # ------------------------------------------------------------------
    def nullmodell(self,
                   params: Optional[dict] = None) -> float:
        """ΛCDM-nullmodellen: alpha_cosmo=0."""
        p = dict(params or {})
        p.setdefault("Omega_m", 0.3)
        p.setdefault("H0", 70.0)
        p.setdefault("sigma8", 0.8)
        p["alpha_cosmo"] = 0.0
        return float(self.growth.compute(p, np.array([0.7]))[0])

    def prediksjon_efc(self, params: dict) -> float:
        """EFC-prediksjonen fra motoren med de gitte parametrene."""
        return float(self.growth.compute(params, np.array([0.7]))[0])

    # ------------------------------------------------------------------
    # Dommen
    # ------------------------------------------------------------------
    def vurder(self, måling: Optional[dict]) -> dict:
        """Treverdig dom: PASS / FAIL / VENTER.

        måling: dict med fsigma8, sigma, z_eff, kilde — eller None.
        """
        if måling is None:
            return {
                "status": "VENTER",
                "årsak": ("Arbiter-målingen mangler: DESI DR2 full-shape "
                          "galakse-RSD fσ8(z~0.7) er ikke tilgjengelig. "
                          "Den publiserte DR2 Lyα full-shape-målingen "
                          "(2026-07-30) er en annen tracer og kan ikke "
                          "felle denne dommen."),
                "regel": "ingen — intet grunnlag",
                "kilde": "buss-emne kosmos.kosmologi.tilstand.efc-fs8 "
                         "(arbiter: nei, venter_på: DESI DR2 full-shape)",
            }
        m = måling["fsigma8"]
        s = måling["sigma"]
        diff_efc = abs(m - PREDIKSJON_EFC) / s
        diff_lcdm = abs(m - PREDIKSJON_LCDM) / s

        if diff_efc <= 1.0:
            return {
                "status": "PASS",
                "årsak": (f"Målingen {m}±{s} ligger {diff_efc:.1f}σ fra "
                          f"0.430 — innen ~1σ (bekreftelseskriteriet)."),
                "regel": self.kriterium()["bekreftelse"],
                "kilde": FORSEGLET_DOI,
                "avstand_efc_sigma": round(diff_efc, 2),
                "avstand_lcdm_sigma": round(diff_lcdm, 2),
            }

        over_lcdm_3sigma = (m - PREDIKSJON_LCDM) / s > 3.0
        konsistent_lcdm_1sigma = diff_lcdm < 1.0
        ekskluderer_efc_2sigma = (m - PREDIKSJON_EFC) / s >= 2.0

        if over_lcdm_3sigma:
            return {
                "status": "FAIL",
                "årsak": (f"Målingen {m}±{s} ligger "
                          f"{(m - PREDIKSJON_LCDM) / s:.1f}σ OVER 0.449 — "
                          "konsistent med ΛCDM ved høy signifikans "
                          "(P2 damage test)."),
                "regel": self.kriterium()["falsifikasjon_a"],
                "kilde": ("validation-ledger P2 (DAMAGE); "
                          f"{FORSEGLET_DOI}"),
                "avstand_efc_sigma": round(diff_efc, 2),
                "avstand_lcdm_sigma": round(diff_lcdm, 2),
            }

        if konsistent_lcdm_1sigma or ekskluderer_efc_2sigma:
            return {
                "status": "FAIL",
                "årsak": (f"Målingen {m}±{s} er konsistent med 0.449 "
                          f"innen <1σ ({diff_lcdm:.1f}σ) eller ekskluderer "
                          f"0.430 ved ≥2σ ({diff_efc:.1f}σ) — falsifisert "
                          "etter P1."),
                "regel": self.kriterium()["falsifikasjon_b"],
                "kilde": FORSEGLET_DOI,
                "avstand_efc_sigma": round(diff_efc, 2),
                "avstand_lcdm_sigma": round(diff_lcdm, 2),
            }

        return {
            "status": "VENTER",
            "årsak": (f"Målingen {m}±{s} skiller ikke modellene ved "
                      f"kriteriet: {diff_efc:.1f}σ fra 0.430, "
                      f"{diff_lcdm:.1f}σ fra 0.449 — verken bekreftet "
                      "eller falsifisert."),
            "regel": "ingen — mellomliggende",
            "kilde": FORSEGLET_DOI,
            "avstand_efc_sigma": round(diff_efc, 2),
            "avstand_lcdm_sigma": round(diff_lcdm, 2),
        }

    # ------------------------------------------------------------------
    # Rapporten — full proveniens + ærlighetsklausulen
    # ------------------------------------------------------------------
    def rapport(self, måling: Optional[dict] = None) -> dict:
        """Full rapport: kriterium, prediksjoner, dom og ærlighet."""
        dom = self.vurder(måling)
        null = self.nullmodell()
        return {
            "kriterium": self.kriterium(),
            "nullmodell_fs8_07": null,
            "dom": dom,
            "mu_kanal_i_motorlaget": False,
            "ærlighet": ("Den forseglede prediksjonen 0.430 hviler på "
                         "μ<1 (B-kanalen, 'linear growth with entropy "
                         "damping'). Motorlagets growth-API har per i dag "
                         "mu=1 — bare bakgrunnskanalen (alpha_cosmo) "
                         "finnes. 0.430 er derfor IKKE maskinelt "
                         "reprodusert fra motorene; å hevde det ville "
                         "være en påstand uten grunnlag."),
        }

    # ------------------------------------------------------------------
    # Busspayloaden (emne kosmos.kosmologi.utfall.efc-fs8-arbiter)
    # ------------------------------------------------------------------
    def payload(self, måling: Optional[dict] = None) -> dict:
        """Payload for publisering — eller for artefakt når bussen er
        read-only for oss (verden-MCP er kun konsument)."""
        return {
            "emne": "kosmos.kosmologi.utfall.efc-fs8-arbiter",
            "kriterium": self.kriterium(),
            "rapport": self.rapport(måling),
            "proveniens": {
                "generert_av": "SealedFs8Arbiter",
                "modul": "efc_inference/arbiter/sealed_fs8.py",
                "growth_motor": type(self.growth).__name__,
                "generert_tid": None,  # fylles av kalleren med faktisk tid
            },
        }
