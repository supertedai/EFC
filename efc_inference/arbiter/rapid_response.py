"""Rapid-response-vakten (trinn 14).

Det siste leddet i den forseglede kjeden: når DESI DR2 full-shape
galakse-RSD fσ8(z~0.7) publiseres, skal dommen felles automatisk —
ikke vente på manuell kjøring.

Vakten er REN — den prosesserer den siste buss-meldingen og kjører
SealedFs8Arbiter (trinn 12, med trinn 13s μ-bevisste motorprediksjon).
Henting fra bussen er kallens ansvar (injiserbar); publisering skjer
bare hvis kalleren gir skrivetilgang — ellers er artefakten leveransen
og gapet deklareres.

Gjenkjenning: målingen må vaere galakse-RSD (tracer LRG/ELG — Lyα og
QSO avvises), z_eff i [0.5, 0.9], med fsigma8 OG sigma. Den forseglede
baselinen (efc-sealed-baseline, arbiter: nei) er referanseverdier og
feller ingen dom.
"""
from __future__ import annotations

import datetime
import json
from typing import Optional

from efc_inference.arbiter.sealed_fs8 import (
    SealedFs8Arbiter,
    TILLATTE_TRACERE,
    Z_MIN,
    Z_MAKS,
)


class RapidResponseVakt:
    """Prosesserer buss-meldinger og feller dommen når den kan."""

    def __init__(self, arbiter: Optional[SealedFs8Arbiter] = None,
                 artefakt_sti: str = "arbiter-efc-fs8-dom.json"):
        self.arbiter = arbiter or SealedFs8Arbiter()
        self.artefakt_sti = artefakt_sti

    # ------------------------------------------------------------------
    # Gjenkjenning
    # ------------------------------------------------------------------
    def gjenkjenn(self, melding: dict) -> Optional[dict]:
        """Trekker ut en arbiter-måling fra en buss-melding — eller None.

        Krever: hoder med tracer LRG/ELG, maalt med fsigma8, sigma og
        z_eff i vinduet. Alt annet (baseline, Lyα, QSO, feil form)
        returnerer None — vakten feller aldri dom på feil grunnlag.
        """
        if not isinstance(melding, dict):
            return None
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return None

        tracer = hoder.get("tracer")
        if tracer is None or str(tracer).upper() not in TILLATTE_TRACERE:
            return None

        for felt in ("fsigma8", "fsigma8_sigma", "z_eff"):
            if felt not in maalt or maalt[felt] is None:
                return None

        try:
            fs8 = float(maalt["fsigma8"])
            sigma = float(maalt["fsigma8_sigma"])
            z_eff = float(maalt["z_eff"])
        except (TypeError, ValueError):
            return None

        if not (Z_MIN <= z_eff <= Z_MAKS):
            return None

        return {
            "fsigma8": fs8,
            "sigma": sigma,
            "z_eff": z_eff,
            "tracer": str(tracer).upper(),
            "kilde": str(hoder.get("kilde", "ukjent")),
        }

    # ------------------------------------------------------------------
    # Dommen
    # ------------------------------------------------------------------
    def sjekk(self, melding: dict,
              params: Optional[dict] = None) -> dict:
        """Kjører vakten: gjenkjenner, dommer, skriver artefakt.

        Returnerer payloaden (samme format som SealedFs8Arbiter.payload
        pluss vaktens proveniens). Artefakten skrives alltid — den er
        vakten leveranse når bussen er read-only for oss.
        """
        måling = self.gjenkjenn(melding)
        if måling is None:
            # Ærlig VENTER-diagnose: si HVORFOR meldingen ikke ble dømt.
            årsak = self._hvorfor_ikke(melding)
            dom = {
                "status": "VENTER",
                "årsak": årsak,
                "regel": "ingen — meldingen er ikke arbiter-målingen",
                "kilde": "RapidResponseVakt.gjenkjenn",
            }
        else:
            dom = self.arbiter.vurder(måling, params)

        payload = {
            "emne": "kosmos.kosmologi.utfall.efc-fs8-arbiter",
            "kriterium": self.arbiter.kriterium(),
            "rapport": {
                "dom": dom,
                "mu_kanal_i_injisert_motor": bool(
                    getattr(self.arbiter.growth, "stotter_mu",
                            lambda: False)()),
                "ærlighet": self.arbiter.rapport().get("ærlighet", ""),
            },
            "proveniens": {
                "generert_av": "RapidResponseVakt",
                "modul": "efc_inference/arbiter/rapid_response.py",
                "arbiter": "SealedFs8Arbiter",
                "generert_tid": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(),
            },
        }
        self._skriv_artefakt(payload)
        return payload

    def _hvorfor_ikke(self, melding: dict) -> str:
        """Forklarer ærlig hvorfor en melding ikke ble dømt."""
        if not isinstance(melding, dict):
            return "Meldingen er ikke en dict — ugyldig form."
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return "Meldingen mangler hoder/maalt — ugyldig form."
        tracer = str(hoder.get("tracer", "ukjent"))
        if tracer.upper() not in TILLATTE_TRACERE:
            return (f"Traceren er {tracer} — ikke galakse-RSD "
                    f"({'/'.join(TILLATTE_TRACERE)}).")
        z = maalt.get("z_eff")
        if z is None or not (Z_MIN <= float(z) <= Z_MAKS):
            return (f"z_eff={z} ligger utenfor testens z-vindu "
                    f"[{Z_MIN}, {Z_MAKS}].")
        for felt in ("fsigma8", "fsigma8_sigma"):
            if felt not in maalt or maalt[felt] is None:
                return f"Målingen mangler feltet «{felt}»."
        return "Meldingen ble ikke gjenkjent som arbiter-måling."

    # ------------------------------------------------------------------
    # Artefakt
    # ------------------------------------------------------------------
    def _skriv_artefakt(self, payload: dict) -> None:
        with open(self.artefakt_sti, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
