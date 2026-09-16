"""Forseglet fσ8-arbiter (trinn 12).

Den maskinelle dommeren mot EFCs forseglede prediksjon P2:

    fσ8(z=0.7) = 0.430 (EFC)  vs  0.449 (ΛCDM)

Forseglet 2026-04-14 under DOI 10.6084/m9.figshare.32013156
(«Sealed Blind Predictions for Growth-Rate Observables: EFC vs ΛCDM»),
og liggende som melding paa bussen (emne
kosmos.kosmologi.tilstand.efc-fs8, seq 5817, kilde efc-sealed-baseline).

Viktig skille — FORSEGLET ANKER vs MOTORPREDIKSJON:
- 0.430 er det BLINDE ankeret som ble forseglet 2026-04-14. Dommen
  felles alltid mot ankeret — kriteriet kan ikke endres etter
  forseglingen.
- I tillegg beregner arbiteren en EKSPLISITT motorprediksjon fra de
  gitte parametrene (growth-motoren). Avstanden maaling↔motorprediksjon
  rapporteres separat, slik at avviket mellom motorlaget og ankeret
  blir SYNLIG — aldri skjult.

Dommelogikken er treverdig og hver dom baerer regelen som felte den,
med kilde. Arbiteren feller ALDRI en dom på data den ikke har.

Ærlighetsklausul: den forseglede prediksjonen hviler på μ<1 (B-kanalen
i perturbasjonslaget, «linear growth with entropy damping»). Motorlagets
growth-API (efc_inference.engine.growth) har per i dag mu=1 hardkodet —
bare bakgrunnskanalen (alpha_cosmo) er med. Arbiteren rapporterer dette
åpenlyst og påstår ikke at 0.430 er maskinelt reprodusert.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from efc_inference.engine.growth import EFCGrowth

FORSEGLET_DOI = "10.6084/m9.figshare.32013156"
FORSEGLET_DATO = "2026-04-14"
ARBITER_INSTRUMENT = "DESI DR2 full-shape RSD (galakse-RSD, z~0.7)"
ANKER_EFC = 0.430
ANKER_LCDM = 0.449
# Instrumentet krever galakse-RSD-tracere (LRG/ELG); Lyα er en annen
# tracer og kan ikke felle dommen. z-vinduet er testens regime: z~0.7.
TILLATTE_TRACERE = ("LRG", "ELG")
Z_MIN, Z_MAKS = 0.5, 0.9
# Flytetallsavrunding gjør at «nøyaktig 1σ/2σ/3σ»-verdier kan lande en
# hårsbredd på feil side av grensen (2.0 blir 1.999999999999999). «~1σ»-
# formuleringen er uansett ikke eksakt, så grensene bruker en epsilon.
EPS = 1e-9


class SealedFs8Arbiter:
    """Dommer mot den forseglede fσ8(z=0.7)-prediksjonen."""

    def __init__(self, growth: Optional[EFCGrowth] = None):
        self.growth = growth or EFCGrowth()

    # ------------------------------------------------------------------
    # Kriteriet (forseglet) — norsk gjengivelse, kildehenvist
    # ------------------------------------------------------------------
    @staticmethod
    def kriterium() -> dict:
        return {
            "anker_efc": ANKER_EFC,
            "anker_lcdm": ANKER_LCDM,
            "arbiter_instrument": ARBITER_INSTRUMENT,
            "tillatte_tracere": list(TILLATTE_TRACERE),
            "z_vindu": [Z_MIN, Z_MAKS],
            "forseglet_dato": FORSEGLET_DATO,
            "forseglet_doi": FORSEGLET_DOI,
            "bekreftelse": ("DESI DR2 full-shape fsigma8(z~0.7) skal ligge "
                            "innenfor ~1σ av 0.430"),
            "falsifikasjon_a": ("Målt fσ8(z=0.7) > 0.449 ved mer enn 3σ — "
                                "konsistent med ΛCDM ved høy signifikans "
                                "(P2 damage-test)"),
            "falsifikasjon_b": ("Falsifisert hvis målingen er konsistent "
                                "med 0.449 (ΛCDM) innenfor mindre enn 1σ "
                                "eller ekskluderer 0.430 ved minst 2σ "
                                "(P1, falsifiable_by)"),
        }

    # ------------------------------------------------------------------
    # Prediksjonene — parameter-avledet fra motoren, ikke hardkodet
    # ------------------------------------------------------------------
    def nullmodell(self, params: Optional[dict] = None) -> float:
        """ΛCDM-nullmodellen: alpha_cosmo=0."""
        p = dict(params or {})
        p.setdefault("Omega_m", 0.3)
        p.setdefault("H0", 70.0)
        p.setdefault("sigma8", 0.8)
        p["alpha_cosmo"] = 0.0
        return float(self.growth.compute(p, np.array([0.7]))[0])

    def prediksjon_efc(self, params: dict) -> float:
        """EFC-motorprediksjonen fra de gitte parametrene."""
        return float(self.growth.compute(params, np.array([0.7]))[0])

    # ------------------------------------------------------------------
    # Dommen
    # ------------------------------------------------------------------
    def vurder(self, måling: Optional[dict],
               params: Optional[dict] = None) -> dict:
        """Treverdig dom: PASS / FAIL / VENTER.

        måling: dict med fsigma8, sigma, z_eff, tracer, kilde — eller
        None (arbiter-målingen finnes ikke ennå).
        params: motorparametre for den EKSPLISITTE motorprediksjonen.
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

        # --- validering av målingen -----------------------------------
        for felt in ("fsigma8", "sigma", "z_eff", "tracer", "kilde"):
            if felt not in måling or måling[felt] is None:
                return {
                    "status": "VENTER",
                    "årsak": f"Målingen mangler feltet «{felt}» — "
                             "ugyldig grunnlag, dom ikke felt.",
                    "regel": "ingen — ugyldig måling",
                    "kilde": "arbiterens egen validering",
                }
        if not np.isfinite(måling["sigma"]) or måling["sigma"] <= 0:
            return {
                "status": "VENTER",
                "årsak": (f"sigma={måling['sigma']} er ikke et positivt, "
                          "endelig tall — ugyldig grunnlag, dom ikke "
                          "felt."),
                "regel": "ingen — ugyldig måling",
                "kilde": "arbiterens egen validering",
            }
        if måling["tracer"].upper() not in TILLATTE_TRACERE:
            return {
                "status": "VENTER",
                "årsak": (f"Traceren {måling['tracer']} er ikke galakse-"
                          f"RSD ({'/'.join(TILLATTE_TRACERE)}). Lyα er en "
                          "annen tracer og kan ikke felle denne dommen."),
                "regel": "ingen — feil instrument",
                "kilde": ARBITER_INSTRUMENT,
            }
        if not (Z_MIN <= måling["z_eff"] <= Z_MAKS):
            return {
                "status": "VENTER",
                "årsak": (f"z_eff={måling['z_eff']} ligger utenfor testens "
                          f"z-vindu [{Z_MIN}, {Z_MAKS}] — målingen er "
                          "ikke kriteriets måling."),
                "regel": "ingen — feil z-vindu",
                "kilde": "kriteriet gjelder z~0.7",
            }

        m = måling["fsigma8"]
        s = måling["sigma"]
        diff_efc = abs(m - ANKER_EFC) / s
        diff_lcdm = abs(m - ANKER_LCDM) / s

        # --- eksplisitt motorprediksjon (separat fra ankeret) ----------
        motor_pred = None
        if params is not None:
            motor_pred = self.prediksjon_efc(params)

        detaljer = {
            "avstand_anker_efc_sigma": round(diff_efc, 2),
            "avstand_anker_lcdm_sigma": round(diff_lcdm, 2),
        }
        if motor_pred is not None:
            detaljer["motorprediksjon"] = motor_pred
            detaljer["avstand_motorprediksjon_sigma"] = round(
                abs(m - motor_pred) / s, 2)

        if diff_efc <= 1.0 + EPS:
            return {
                "status": "PASS",
                "årsak": (f"Målingen {m}±{s} ligger {diff_efc:.1f}σ fra "
                          f"ankeret 0.430 — innenfor ~1σ "
                          "(bekreftelseskriteriet)."),
                "regel": self.kriterium()["bekreftelse"],
                "kilde": FORSEGLET_DOI,
                **detaljer,
            }

        over_lcdm_3sigma = (m - ANKER_LCDM) / s > 3.0 + EPS
        konsistent_lcdm_1sigma = diff_lcdm < 1.0 + EPS
        ekskluderer_anker_2sigma = diff_efc >= 2.0 - EPS

        if over_lcdm_3sigma:
            return {
                "status": "FAIL",
                "årsak": (f"Målingen {m}±{s} ligger "
                          f"{(m - ANKER_LCDM) / s:.1f}σ OVER 0.449 — "
                          "konsistent med ΛCDM ved høy signifikans "
                          "(P2 damage-test)."),
                "regel": self.kriterium()["falsifikasjon_a"],
                "kilde": f"validation-ledger P2 (DAMAGE); {FORSEGLET_DOI}",
                **detaljer,
            }

        if konsistent_lcdm_1sigma or ekskluderer_anker_2sigma:
            return {
                "status": "FAIL",
                "årsak": (f"Målingen {m}±{s} er konsistent med 0.449 "
                          f"innenfor <1σ ({diff_lcdm:.1f}σ) eller "
                          f"ekskluderer ankeret 0.430 ved ≥2σ "
                          f"({diff_efc:.1f}σ) — falsifisert etter P1."),
                "regel": self.kriterium()["falsifikasjon_b"],
                "kilde": FORSEGLET_DOI,
                **detaljer,
            }

        return {
            "status": "VENTER",
            "årsak": (f"Målingen {m}±{s} skiller ikke modellene ved "
                      f"kriteriet: {diff_efc:.1f}σ fra 0.430, "
                      f"{diff_lcdm:.1f}σ fra 0.449 — verken bekreftet "
                      "eller falsifisert."),
            "regel": "ingen — mellomliggende",
            "kilde": FORSEGLET_DOI,
            **detaljer,
        }

    # ------------------------------------------------------------------
    # Rapporten — full proveniens + ærlighetsklausulen
    # ------------------------------------------------------------------
    def rapport(self, måling: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
        """Full rapport: kriterium, prediksjoner, dom og ærlighet."""
        dom = self.vurder(måling, params)
        null = self.nullmodell()
        return {
            "kriterium": self.kriterium(),
            "nullmodell_fs8_07": null,
            "dom": dom,
            "mu_kanal_i_motorlaget": False,
            "ærlighet": ("Den forseglede prediksjonen 0.430 hviler på "
                         "μ<1 (B-kanalen, «linear growth with entropy "
                         "damping»). Motorlagets growth-API har per i dag "
                         "mu=1 — bare bakgrunnskanalen (alpha_cosmo) "
                         "finnes. 0.430 er derfor IKKE maskinelt "
                         "reprodusert fra motorene; å hevde det ville "
                         "være en påstand uten grunnlag. Arbiteren "
                         "rapporterer motorprediksjonen SEPARAT fra det "
                         "forseglede ankeret — avviket skal synes, ikke "
                         "skjules."),
        }

    # ------------------------------------------------------------------
    # Busspayloaden (emne kosmos.kosmologi.utfall.efc-fs8-arbiter)
    # ------------------------------------------------------------------
    def payload(self, måling: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
        """Payload for publisering — eller for artefakt når bussen er
        read-only for oss (verden-MCP er kun konsument)."""
        return {
            "emne": "kosmos.kosmologi.utfall.efc-fs8-arbiter",
            "kriterium": self.kriterium(),
            "rapport": self.rapport(måling, params),
            "proveniens": {
                "generert_av": "SealedFs8Arbiter",
                "modul": "efc_inference/arbiter/sealed_fs8.py",
                "growth_motor": type(self.growth).__name__,
                "generert_tid": None,  # fylles av kalleren med faktisk tid
            },
        }
