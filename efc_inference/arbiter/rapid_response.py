"""Rapid-response-vakten (trinn 14).

Det siste leddet i den forseglede kjeden: når DESI DR2 full-shape
galakse-RSD fσ8(z~0.7) publiseres, skal dommen felles automatisk —
ikke vente på manuell kjøring.

Vakten er REN — den prosesserer den siste buss-meldingen og kjører
SealedFs8Arbiter (trinn 12, med trinn 13s μ-bevisste motorprediksjon).
Henting fra bussen er kallens ansvar (injiserbar); publisering skjer
bare hvis kalleren gir skrivetilgang — ellers er artefakten leveransen
og gapet deklareres.

Gjenkjenning er KONSERVATIV: vakten dømmer bare en melding som er
dokumentert som DESI DR2 full-shape galakse-RSD fσ8 — tracer LRG/ELG,
observabel fsigma8, survey/kilde som peker på DR2 full-shape, IKKE
merket som baseline (efc-sealed-baseline / arbiter: nei), z_eff i
[0.5, 0.9], med fsigma8 OG sigma. Alt annet feller ingen dom — vakten
venter heller enn å dømme feil.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
from typing import Optional

from efc_inference.arbiter.sealed_fs8 import (
    SealedFs8Arbiter,
    TILLATTE_TRACERE,
    Z_MIN,
    Z_MAKS,
)

BASELINE_KILDE = "efc-sealed-baseline"


def _endelig(v) -> bool:
    """Endelig-sjekk som aldri krasjer på ugyldige typer."""
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


class RapidResponseVakt:
    """Prosesserer buss-meldinger og feller dommen når den kan."""

    def __init__(self, arbiter: Optional[SealedFs8Arbiter] = None,
                 artefakt_sti: str = "arbiter-efc-fs8-dom.json"):
        self.arbiter = arbiter or SealedFs8Arbiter()
        self.artefakt_sti = artefakt_sti

    # ------------------------------------------------------------------
    # Gjenkjenning (konservativ)
    # ------------------------------------------------------------------
    def gjenkjenn(self, melding: dict) -> Optional[dict]:
        """Trekker ut en arbiter-måling fra en buss-melding — eller None.

        Krever HELE dokumentasjonen: galakse-RSD-tracer (LRG/ELG),
        observabel fsigma8, survey/kilde som peker på DESI DR2
        full-shape, IKKE baseline, z_eff i vinduet, fsigma8 + sigma.
        """
        if not isinstance(melding, dict):
            return None
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return None

        # Ikke baselinen — den er arbiterens grunnlag, ikke målingen.
        kilde = str(hoder.get("kilde", "")).lower()
        if hoder.get("arbiter") == "nei" or BASELINE_KILDE in kilde:
            return None

        # Observabelen må være fsigma8 — vakten dømmer ikke andre.
        if str(hoder.get("observabel", "")).lower() != "fsigma8":
            return None

        # Surveyet må være DESI DR2 (full-shape-søsken) — kilden kan
        # ikke redde et feil survey. En vilkårlig LRG-melding fra et
        # annet survey er ikke kriteriets måling.
        survey = str(hoder.get("survey", "")).lower()
        if "dr2" not in survey:
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

        if not (_endelig(fs8) and _endelig(sigma) and _endelig(z_eff)):
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

        Artefakten bærer FULL input-proveniens: meldings-ID, kilde,
        meldingens sha256-hash, den gjenkjente målingen og parametrene
        — slik at dommen alltid kan knyttes tilbake til konkret
        bussmelding.
        """
        måling = self.gjenkjenn(melding)
        if måling is None:
            dom = {
                "status": "VENTER",
                "årsak": self._hvorfor_ikke(melding),
                "regel": "ingen — meldingen er ikke arbiter-målingen",
                "kilde": "RapidResponseVakt.gjenkjenn",
            }
        else:
            dom = self.arbiter.vurder(måling, params)

        payload = {
            "emne": "kosmos.kosmologi.utfall.efc-fs8-arbiter",
            "kriterium": self.arbiter.kriterium(),
            "input": self._input_proveniens(melding, måling, params),
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

    def _input_proveniens(self, melding: dict,
                          måling: Optional[dict],
                          params: Optional[dict]) -> dict:
        """Verifiserbar kobling mellom bussmeldingen og dommen."""
        serialisert = json.dumps(melding, sort_keys=True,
                                 ensure_ascii=False)
        meldings_id = None
        hoder = melding.get("hoder") if isinstance(melding, dict) else None
        if isinstance(hoder, dict):
            meldings_id = hoder.get("Nats-Msg-Id") or hoder.get("kilde")
        return {
            "meldings_id": meldings_id,
            "meldings_hash_sha256": hashlib.sha256(
                serialisert.encode("utf-8")).hexdigest(),
            "gjenkjent_maaling": måling,
            "params": params,
        }

    def _hvorfor_ikke(self, melding: dict) -> str:
        """Forklarer ærlig hvorfor en melding ikke ble dømt — uten å
        krasje på ugyldige typer/former."""
        if not isinstance(melding, dict):
            return "Meldingen er ikke en dict — ugyldig form."
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return "Meldingen mangler hoder/maalt — ugyldig form."

        kilde = str(hoder.get("kilde", "")).lower()
        if hoder.get("arbiter") == "nei" or BASELINE_KILDE in kilde:
            return ("Meldingen er den forseglede baselinen — "
                    "referanseverdier, ikke arbiter-målingen.")
        if str(hoder.get("observabel", "")).lower() != "fsigma8":
            return (f"Observabelen er {hoder.get('observabel', 'ukjent')} "
                    "— vakten dømmer bare fsigma8.")
        survey = str(hoder.get("survey", "")).lower()
        if "dr2" not in survey:
            return ("Surveyet er ikke DESI DR2 full-shape "
                    f"(survey={hoder.get('survey', 'ukjent')}, "
                    f"kilde={hoder.get('kilde', 'ukjent')}).")

        tracer = str(hoder.get("tracer", "ukjent"))
        if tracer.upper() not in TILLATTE_TRACERE:
            return (f"Traceren er {tracer} — ikke galakse-RSD "
                    f"({'/'.join(TILLATTE_TRACERE)}).")

        for felt in ("fsigma8", "fsigma8_sigma", "z_eff"):
            if felt not in maalt or maalt[felt] is None:
                return f"Målingen mangler feltet «{felt}»."

        z_verdi = maalt["z_eff"]
        if not _endelig(z_verdi):
            return f"z_eff={z_verdi!r} er ikke et endelig tall."
        z = float(z_verdi)
        if not (Z_MIN <= z <= Z_MAKS):
            return (f"z_eff={z} ligger utenfor testens z-vindu "
                    f"[{Z_MIN}, {Z_MAKS}].")
        return "Meldingen ble ikke gjenkjent som arbiter-måling."

    # ------------------------------------------------------------------
    # Artefakt
    # ------------------------------------------------------------------
    def _skriv_artefakt(self, payload: dict) -> None:
        with open(self.artefakt_sti, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
